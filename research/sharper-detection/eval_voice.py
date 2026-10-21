"""Healthy alarms and catches of the old voice-only rule vs the combined
score, on the cloud research's voice days (5 normal days as baseline)."""
import json, random, sys
from pathlib import Path
from collections import defaultdict
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "daily-checkin/server"))
from checkin.baseline import build_baseline, change_probability, change_scores
from checkin import change as C

def run(path):
    days = defaultdict(dict)
    for line in open(path):
        r = json.loads(line)
        days[r["speaker"]].setdefault(r["day"], {})[r["condition"]] = r["features"]
    rng = random.Random(0)
    stats = defaultdict(lambda: [0, 0, 0, 0])  # tests, old alarm, some+, big
    for spk, by_day in days.items():
        normal_days = [d for d in by_day if "normal" in by_day[d]]
        for test in normal_days:
            others = [d for d in normal_days if d != test]
            for _ in range(10):
                base = build_baseline([by_day[d]["normal"] for d in rng.sample(others, min(5, len(others)))])
                for cond, feats in by_day[test].items():
                    z = change_scores(feats, base)
                    p = change_probability(z)
                    signs = C.drowsiness_signs({"latency_s": feats["latency_s"]}, z, {})
                    e = C.evidence({"orientation_mistakes": 0, "attention_score": 0, "digits_correct": None},
                                   C.personal_normal([]), p, signs)
                    lvl = C.combine(e)["level"]
                    s = stats[cond]
                    s[0] += 1; s[1] += p >= 0.7; s[2] += lvl != "usual"; s[3] += lvl == "big"
    for cond, (n, old, some, big) in sorted(stats.items()):
        print(f"  {cond:12s} n={n:5d}  old voice rule 4 pts {old/n:6.1%}   keep an eye or more {some/n:6.1%}   big change {big/n:6.1%}")

for name in ("voice_days.jsonl", "voice_days_synth.jsonl"):
    print(name)
    run(REPO / "research/cloud-4at-asr/results" / name)
