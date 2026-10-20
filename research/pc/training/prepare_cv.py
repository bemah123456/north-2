"""Build train/test lists of older speakers from a Mozilla Common Voice download.

Usage:
    python -I prepare_cv.py <folder containing the extracted Common Voice files> [--hours 10]

Finds every validated.tsv under the folder, keeps clips whose self-declared age is
sixties or older, splits by speaker (no speaker in both sets), and writes
training/manifests/{train,test}.csv with columns: path, sentence, age, client_id.
"""
import argparse
import csv
import random
import sys
from pathlib import Path

OLDER = {"sixties", "seventies", "eighties", "nineties"}
AVG_CLIP_SEC = 5.0  # Common Voice clips are typically 4-6 s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cv_root", type=Path)
    ap.add_argument("--hours", type=float, default=10.0, help="cap on training audio")
    ap.add_argument("--test-frac", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    csv.field_size_limit(sys.maxsize if sys.maxsize < 2**31 else 2**31 - 1)
    rows = []
    for tsv in args.cv_root.rglob("validated.tsv"):
        clips = tsv.parent / "clips"
        with tsv.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                if r.get("age") in OLDER and (clips / r["path"]).exists():
                    rows.append({"path": str(clips / r["path"]), "sentence": r["sentence"],
                                 "age": r["age"], "client_id": r["client_id"]})
    if not rows:
        sys.exit(f"No older-speaker clips found under {args.cv_root}. Is validated.tsv there?")

    speakers = sorted({r["client_id"] for r in rows})
    random.Random(args.seed).shuffle(speakers)
    n_test = max(1, int(len(speakers) * args.test_frac))
    test_spk = set(speakers[:n_test])

    train = [r for r in rows if r["client_id"] not in test_spk]
    test = [r for r in rows if r["client_id"] in test_spk]
    random.Random(args.seed).shuffle(train)
    train = train[: int(args.hours * 3600 / AVG_CLIP_SEC)]
    test = test[:2000]

    out = Path(__file__).parent / "manifests"
    out.mkdir(exist_ok=True)
    for name, part in (("train", train), ("test", test)):
        with (out / f"{name}.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["path", "sentence", "age", "client_id"])
            w.writeheader()
            w.writerows(part)

    ages = {}
    for r in rows:
        ages[r["age"]] = ages.get(r["age"], 0) + 1
    print(f"older-speaker clips found: {len(rows)} from {len(speakers)} speakers; by age: {ages}")
    print(f"train: {len(train)} clips (~{len(train) * AVG_CLIP_SEC / 3600:.1f} h); "
          f"test: {len(test)} clips from {n_test} held-out speakers")


if __name__ == "__main__":
    main()
