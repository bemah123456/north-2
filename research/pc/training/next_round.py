"""Pick the best tuned model so far from comparison tables and print its folder.

Score = word error rate in quiet + word error rate with background talk (both on the same 44
held-out older speakers). Reads every out/comparison*.md; only out/... models count.
Usage: python -I next_round.py  -> prints e.g. out/whisper-small-v2
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROW = re.compile(r"^\| (out/[\w.-]+)@prompt \| \d+M \| ([\d.]+)% \([^)]*\) \| ([\d.]+)% ")


def main():
    best = {}
    for md in (HERE / "out").glob("comparison*.md"):
        for line in md.read_text(encoding="utf-8").splitlines():
            m = ROW.match(line)
            if m:
                best[m.group(1)] = float(m.group(2)) + float(m.group(3))
    if not best:
        print("out/whisper-small")
        return
    print(min(best, key=best.get))


if __name__ == "__main__":
    main()
