"""Collect older-speaker clips from the public Hugging Face copy of Common Voice 17 English
(saeedzou/common-voice-17-en-age-gender-accent, CC0), without keeping the whole 23 GB.

Downloads one ~450 MB parquet shard at a time, keeps rows whose age is sixties or older,
writes their MP3s to data/cv17_older/clips plus a validated.tsv that prepare_cv.py reads,
deletes the shard, and stops once --target clips are collected.

Usage:  python -I fetch_cv17_older.py <data folder> [--target 12000]
"""
import argparse
import csv
import json
import time
import urllib.request
from pathlib import Path

import pyarrow.parquet as pq

REPO = "saeedzou/common-voice-17-en-age-gender-accent"
OLDER = {"sixties", "seventies", "eighties", "nineties"}


def shard_list():
    with urllib.request.urlopen(f"https://huggingface.co/api/datasets/{REPO}/tree/main/data") as r:
        files = json.load(r)
    return sorted(f["path"] for f in files if f["path"].startswith("data/train-") and f["path"].endswith(".parquet"))


def download(path, dest):
    """Downloads with resume: a dropped connection continues from the bytes already
    saved (the CDN once cut one shard at the same byte on every retry)."""
    url = f"https://huggingface.co/datasets/{REPO}/resolve/main/{path}"
    dest = Path(dest)
    dest.unlink(missing_ok=True)
    for attempt in range(8):
        have = dest.stat().st_size if dest.exists() else 0
        req = urllib.request.Request(url, headers={"Range": f"bytes={have}-"} if have else {})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                total = have + int(r.headers.get("Content-Length", 0))
                if have and r.status != 206:  # server ignored the range: start over
                    have, total = 0, int(r.headers.get("Content-Length", 0))
                    dest.unlink(missing_ok=True)
                with dest.open("ab") as f:
                    while chunk := r.read(1 << 20):
                        f.write(chunk)
            if dest.stat().st_size >= total:
                return
            raise IOError(f"got {dest.stat().st_size} of {total} bytes")
        except Exception as e:  # network hiccup: back off, then resume
            print(f"  retry {attempt + 1} for {path} (have {dest.stat().st_size if dest.exists() else 0} bytes): {e}",
                  flush=True)
            time.sleep(min(60, 2 ** (attempt + 1)))
    raise RuntimeError(f"could not download {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir", type=Path)
    ap.add_argument("--target", type=int, default=12000)
    args = ap.parse_args()

    out = args.data_dir / "cv17_older"
    clips = out / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    tsv = out / "validated.tsv"
    done_file = out / "shards_done.txt"
    done = set(done_file.read_text().split()) if done_file.exists() else set()
    have = sum(1 for _ in tsv.open(encoding="utf-8")) - 1 if tsv.exists() else 0

    new_file = not tsv.exists()
    with tsv.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="\\")
        if new_file:
            w.writerow(["client_id", "path", "sentence", "age", "gender", "accents"])
        for shard in shard_list():
            if have >= args.target:
                break
            if shard in done:
                continue
            tmp = out / "shard.tmp.parquet"
            t = time.time()
            download(shard, tmp)
            table = pq.read_table(tmp, columns=["client_id", "path", "sentence", "age", "gender", "accent", "audio"])
            kept = 0
            for row in table.to_pylist():
                if row["age"] not in OLDER or not row["audio"] or not row["audio"].get("bytes"):
                    continue
                name = Path(row["path"]).name or f"{row['client_id'][:8]}_{kept}.mp3"
                (clips / name).write_bytes(row["audio"]["bytes"])
                sentence = row["sentence"].replace("\t", " ").replace("\n", " ")
                w.writerow([row["client_id"], name, sentence, row["age"], row["gender"] or "", row["accent"] or ""])
                kept += 1
            f.flush()
            tmp.unlink()
            have += kept
            done.add(shard)
            done_file.write_text("\n".join(sorted(done)))
            print(f"{shard}: kept {kept} older clips ({have} total) in {time.time() - t:.0f}s", flush=True)
    print(f"done: {have} older-speaker clips in {out}")


if __name__ == "__main__":
    main()
