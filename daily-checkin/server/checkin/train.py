"""Train the baseline-change model.

Two sources of training rows:

  python -m checkin.train --csv recordings.csv   # your labeled check-ins
  python -m checkin.train --synthetic            # simulated people, demo only

The CSV needs columns person_id, label ("normal" or "off") and the seven
features in features.FEATURE_DIRECTIONS (export them with
`GET /export/features`). Record some check-ins normally and some while
deliberately tired, distracted or after a bad night's sleep, as the plan
describes.

Each row is turned into change scores against that person's other normal
rows (never including itself), so the model learns "how far from their own
normal", not "how this voice sounds". Evaluation holds out whole people.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from datetime import date

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

from .baseline import MODEL_PATH, build_baseline, change_scores
from .features import FEATURE_DIRECTIONS

NAMES = list(FEATURE_DIRECTIONS)


def synthetic_rows(n_people: int = 60, days: int = 12, seed: int = 7) -> list[dict]:
    """Simulated check-ins. Each person has their own normal; "off" days
    move some features the way the delirium literature describes (slower,
    more pauses, less said). Useful only to exercise the pipeline."""
    rng = random.Random(seed)
    rows = []
    for p in range(n_people):
        norm = {
            "latency_s": rng.uniform(0.8, 2.5),
            "words_per_min": rng.uniform(95, 165),
            "pauses_per_min": rng.uniform(4, 14),
            "mean_pause_s": rng.uniform(0.6, 1.3),
            "filler_rate": rng.uniform(0.01, 0.08),
            "repeat_rate": rng.uniform(0.0, 0.03),
            "greeting_words": rng.uniform(12, 45),
        }
        for d in range(days):
            off = d >= 3 and rng.random() < 0.35
            row = {"person_id": f"sim{p}", "label": "off" if off else "normal"}
            for k, v in norm.items():
                row[k] = max(v * rng.gauss(1.0, 0.12), 0.0)
            if off:
                effects = {
                    "latency_s": lambda x: x * rng.uniform(1.4, 2.6),
                    "words_per_min": lambda x: x * rng.uniform(0.6, 0.88),
                    "pauses_per_min": lambda x: x * rng.uniform(1.3, 2.2),
                    "mean_pause_s": lambda x: x * rng.uniform(1.2, 1.9),
                    "filler_rate": lambda x: x + rng.uniform(0.02, 0.08),
                    "repeat_rate": lambda x: x + rng.uniform(0.01, 0.05),
                    "greeting_words": lambda x: x * rng.uniform(0.35, 0.8),
                }
                for k, f in effects.items():
                    if rng.random() < 0.6:
                        row[k] = f(row[k])
            rows.append(row)
    return rows


def read_csv(path: str) -> list[dict]:
    with open(path, newline="") as f:
        rows = []
        for r in csv.DictReader(f):
            row = {"person_id": r["person_id"], "label": r["label"].strip().lower()}
            for k in NAMES:
                row[k] = float(r[k])
            rows.append(row)
    return rows


def to_matrix(rows: list[dict]):
    by_person = defaultdict(list)
    for i, r in enumerate(rows):
        by_person[r["person_id"]].append(i)
    X, y, groups = [], [], []
    for pid, idxs in by_person.items():
        for i in idxs:
            others = [rows[j] for j in idxs if j != i and rows[j]["label"] == "normal"]
            base = build_baseline(others)
            if base is None:
                continue
            z = change_scores(rows[i], base)
            X.append([z[k] for k in NAMES])
            y.append(1 if rows[i]["label"] == "off" else 0)
            groups.append(pid)
    return np.clip(np.array(X), -6, 6), np.array(y), np.array(groups)


def train(rows: list[dict], source: str) -> dict:
    X, y, groups = to_matrix(rows)
    if len(set(y)) < 2:
        raise SystemExit("Need both normal and off rows to train.")
    n_people = len(set(groups))
    cv_auc = None
    if n_people >= 3:
        preds = np.zeros(len(y))
        for tr, te in GroupKFold(n_splits=min(5, n_people)).split(X, y, groups):
            m = LogisticRegression(class_weight="balanced", C=0.5, max_iter=1000)
            m.fit(X[tr], y[tr])
            preds[te] = m.predict_proba(X[te])[:, 1]
        if len(set(y)) == 2:
            cv_auc = float(roc_auc_score(y, preds))
    model = LogisticRegression(class_weight="balanced", C=0.5, max_iter=1000).fit(X, y)
    return {
        "intercept": float(model.intercept_[0]),
        "weights": {k: float(w) for k, w in zip(NAMES, model.coef_[0])},
        "trained_on": source,
        "synthetic": source == "synthetic",
        "n_rows": int(len(y)),
        "n_people": n_people,
        "n_off": int(y.sum()),
        "held_out_people_auc": cv_auc,
        "trained_date": date.today().isoformat(),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv")
    src.add_argument("--synthetic", action="store_true")
    ap.add_argument("--out", default=str(MODEL_PATH))
    args = ap.parse_args()
    rows = synthetic_rows() if args.synthetic else read_csv(args.csv)
    model = train(rows, "synthetic" if args.synthetic else args.csv)
    with open(args.out, "w") as f:
        json.dump(model, f, indent=2)
    print(json.dumps({k: v for k, v in model.items() if k != "weights"}, indent=2))
    print("weights:", json.dumps({k: round(v, 3) for k, v in model["weights"].items()}))


if __name__ == "__main__":
    main()
