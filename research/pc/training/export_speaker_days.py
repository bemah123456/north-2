"""Export a small per-speaker set of older-speaker clips ("normal days") for the cloud thread's
voice-change study. Common Voice is CC0; speaker ids are replaced by spk01, spk02, ...

Picks the speakers aged 60+ with the most clips, takes N clips each (one clip = one "day"),
copies the MP3s and writes speakers.csv. Output: research-pc/speaker_days/ (+ zip).
Usage: python -I export_speaker_days.py [--speakers 20] [--clips 10]
"""
import argparse
import csv
import random
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "cv17_older"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--speakers", type=int, default=20)
    ap.add_argument("--clips", type=int, default=10)
    args = ap.parse_args()

    by_spk = defaultdict(list)
    with (SRC / "validated.tsv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            by_spk[r["client_id"]].append(r)
    top = sorted(by_spk, key=lambda s: -len(by_spk[s]))[: args.speakers]

    out = ROOT / "research-pc" / "speaker_days"
    shutil.rmtree(out, ignore_errors=True)
    (out / "clips").mkdir(parents=True)
    rng = random.Random(5)
    rows = []
    for n, spk in enumerate(top, 1):
        clips = rng.sample(by_spk[spk], min(args.clips, len(by_spk[spk])))
        for d, r in enumerate(clips, 1):
            name = f"spk{n:02d}_day{d:02d}.mp3"
            shutil.copy(SRC / "clips" / r["path"], out / "clips" / name)
            rows.append({"file": f"clips/{name}", "speaker": f"spk{n:02d}", "day": d,
                         "age": r["age"], "gender": r.get("gender", ""), "sentence": r["sentence"]})
    with (out / "speakers.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / "README.md").write_text(
        "Older-speaker clips from Mozilla Common Voice 17 English (CC0), speakers aged 60+.\n"
        "Each clip is treated as one 'normal day' for that speaker (read sentences by healthy volunteers;\n"
        "no delirium). Speaker ids are replaced; do not try to identify speakers (Common Voice terms).\n",
        encoding="utf-8")
    zip_path = shutil.make_archive(str(ROOT / "research-pc" / "speaker_days"), "zip", out)
    print(f"{len(rows)} clips from {len(top)} speakers -> {zip_path}")


if __name__ == "__main__":
    main()
