"""Write manifests/train_v2.csv from every older-speaker clip downloaded so far, keeping the
existing test speakers (manifests/test.csv) out, so results stay comparable with round 1.
Usage: python -I extend_train_manifest.py <data folder> [--max 40000]
"""
import argparse
import csv
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLDER = {"sixties", "seventies", "eighties", "nineties"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", type=Path)
    ap.add_argument("--max", type=int, default=40000)
    args = ap.parse_args()

    with (HERE / "manifests" / "test.csv").open(encoding="utf-8-sig", newline="") as f:
        test_spk = {r["client_id"] for r in csv.DictReader(f)}
    rows = []
    for tsv in args.data.rglob("validated.tsv"):
        clips = tsv.parent / "clips"
        with tsv.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                if r.get("age") in OLDER and r["client_id"] not in test_spk and (clips / r["path"]).exists():
                    rows.append({"path": str(clips / r["path"]), "sentence": r["sentence"],
                                 "age": r["age"], "client_id": r["client_id"]})
    random.Random(13).shuffle(rows)
    rows = rows[: args.max]
    with (HERE / "manifests" / "train_v2.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["path", "sentence", "age", "client_id"])
        w.writeheader()
        w.writerows(rows)
    ages = {}
    for r in rows:
        ages[r["age"]] = ages.get(r["age"], 0) + 1
    print(f"train_v2: {len(rows)} clips (~{len(rows) * 5 / 3600:.0f} h) from "
          f"{len({r['client_id'] for r in rows})} speakers; excluded {len(test_spk)} test speakers; {ages}")


if __name__ == "__main__":
    main()
