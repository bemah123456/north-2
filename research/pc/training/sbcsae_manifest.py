"""Segment list of unscripted speech by older speakers in the Santa Barbara Corpus of Spoken
American English (SBCSAE), for the voice-change ("normal days") study. Approved by the user
2026-10-20. Speakers are replaced by spk01, spk02, ...; no names go in the output.

The corpus is CC BY-ND 3.0 US, so cut clips are not redistributed: the output is a manifest of
(conversation, start, end) plus fetch_sbcsae.py, which downloads the original WAVs from UCSB's
public links and cuts the segments locally for analysis.

Ages come from the corpus's own conversation descriptions. Each speaker appears in one
conversation, so "days" are turns spread across that conversation, not separate days.
Usage: python -I sbcsae_manifest.py <chat folder> <out folder>
"""
import csv
import re
import sys
from pathlib import Path

# conversation -> [(CHAT speaker code prefix, age, gender)]
OLDER = {
    "SBC011": [("SAM", "72", "f"), ("DORI", "83", "f"), ("ANGE", "90", "f")],
    "SBC060": [("JON", "72", "m"), ("ALAN", "66", "m")],
    "SBC049": [("ALLE", "76", "m")],
    "SBC032": [("TOM1", "60+", "m"), ("TOM2", "60+", "m"), ("TOM3", "60+", "m")],
}
BULLET = re.compile(r"\x15(\d+)_(\d+)\x15")
MIN_S, MAX_S, PER_SPEAKER = 2.5, 20.0, 10


def turns(cha: Path):
    """Consecutive utterances by one speaker merged into turns: (code, start_s, end_s, text)."""
    text = cha.read_text(encoding="utf-8", errors="replace")
    out = []
    for ln in re.sub(r"\n\t", " ", text).splitlines():
        m = re.match(r"\*([A-Z0-9_]+):\s*(.*)", ln)
        b = BULLET.search(m.group(2)) if m else None
        if not b:
            continue
        code, start, end = m.group(1), int(b.group(1)) / 1000, int(b.group(2)) / 1000
        words = BULLET.sub("", m.group(2)).strip()
        if out and out[-1][0] == code and start - out[-1][2] < 1.0 and end - out[-1][1] <= MAX_S:
            out[-1] = (code, out[-1][1], end, out[-1][3] + " " + words)
        else:
            out.append((code, start, end, words))
    return out


def main():
    chat, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    rows, n = [], 0
    for conv, speakers in OLDER.items():
        files = [p for p in chat.rglob(f"{conv}.cha") if "MACOSX" not in str(p)]
        if not files:
            print(f"missing {conv}")
            continue
        all_turns = turns(files[0])
        codes = sorted({t[0] for t in all_turns})
        for prefix, age, gender in speakers:
            mine = [t for t in all_turns if t[0].startswith(prefix) and MIN_S <= t[2] - t[1] <= MAX_S]
            if len(mine) < 8:
                print(f"{conv} speaker {prefix[:2]}..: {len(mine)} usable turns, skipped (codes: {len(codes)})")
                continue
            n += 1
            step = len(mine) / PER_SPEAKER
            pick = [mine[int(i * step)] for i in range(min(PER_SPEAKER, len(mine)))]
            for d, (_, s, e, words) in enumerate(pick, 1):
                rows.append({"file": f"clips/spk{n:02d}_day{d:02d}.wav", "speaker": f"spk{n:02d}", "day": d,
                             "age": age, "gender": gender, "conversation": conv,
                             "start_s": f"{s:.2f}", "end_s": f"{e:.2f}", "transcript": words})
            print(f"{conv} -> spk{n:02d} (age {age}): {len(mine)} usable turns, kept {len(pick)}")
    with (out / "segments.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} segments from {n} speakers -> {out / 'segments.csv'}")


if __name__ == "__main__":
    main()


