"""Each person's normal, and how far today moved from it.

Delirium is an acute change, so the useful question is not "is this voice
unusual?" but "is this voice unusual for them?". The baseline is built from
the person's first check-ins and then from recent days that looked normal.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean, pstdev

from .features import FEATURE_DIRECTIONS

MIN_BASELINE_DAYS = 2  # the doc's "first 2 to 3 check-ins"
BASELINE_WINDOW = 14

# Smallest spread we trust, so two near-identical baseline days don't make
# every tiny wobble look dramatic.
STD_FLOOR = {
    "latency_s": 0.6,
    "words_per_min": 12.0,
    "pauses_per_min": 3.0,
    "mean_pause_s": 0.25,
    "filler_rate": 0.03,
    "repeat_rate": 0.02,
    "greeting_words": 5.0,
}

MODEL_PATH = Path(__file__).with_name("model.json")


def build_baseline(history: list[dict]) -> dict | None:
    """history: feature dicts from earlier normal check-ins, oldest first."""
    days = [h for h in history if h][-BASELINE_WINDOW:]
    if len(days) < MIN_BASELINE_DAYS:
        return None
    out = {"n_days": len(days), "features": {}}
    for name in FEATURE_DIRECTIONS:
        vals = [d[name] for d in days if name in d]
        out["features"][name] = {
            "mean": mean(vals),
            "std": max(pstdev(vals), STD_FLOOR[name]),
        }
    return out


def change_scores(today: dict, baseline: dict) -> dict[str, float]:
    """Signed z-scores, flipped so positive always means "worse than usual"."""
    z = {}
    for name, direction in FEATURE_DIRECTIONS.items():
        b = baseline["features"][name]
        z[name] = direction * (today[name] - b["mean"]) / b["std"]
    return z


def load_model(path: Path = MODEL_PATH) -> dict:
    return json.loads(path.read_text())


def change_probability(z: dict[str, float], model: dict | None = None) -> float:
    """Logistic model over the change scores (weights from train.py)."""
    model = model or load_model()
    s = model["intercept"]
    for name, w in model["weights"].items():
        s += w * max(min(z.get(name, 0.0), 6.0), -6.0)
    return 1.0 / (1.0 + math.exp(-s))


REASON_TEXT = {
    "latency_s": "slower to answer than usual",
    "words_per_min": "speaking more slowly than usual",
    "pauses_per_min": "pausing more than usual",
    "mean_pause_s": "longer pauses than usual",
    "filler_rate": "more \"um\" and \"uh\" than usual",
    "repeat_rate": "repeating words more than usual",
    "greeting_words": "saying much less than usual",
}


def top_reasons(z: dict[str, float], threshold: float = 2.0, limit: int = 3) -> list[str]:
    worst = sorted(((v, k) for k, v in z.items() if v >= threshold), reverse=True)
    return [REASON_TEXT[k] for _, k in worst[:limit]]
