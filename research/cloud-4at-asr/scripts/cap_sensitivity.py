"""How sensitive the "capped" voice-change scoring is to its two settings.

For the cap on "um" and repeated-word scores (in spreads) and the floor on
the speaking-rate spread (words a minute), every pair is scored on both
day sets with 5 normal days, as in voice_baseline_study.py. Then the pair
is chosen on half the voices and checked on the other half, both ways
round, to see whether the gain holds on voices it was not chosen on.

Usage: cap_sensitivity.py REAL_DAYS_JSONL SYNTH_DAYS_JSONL OUT_JSON
"""

import json
import random
import sys
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, "/mnt/project-files/daily-checkin/server")
from checkin.baseline import build_baseline, change_probability, change_scores, load_model  # noqa: E402

CAPS = [1.0, 1.5, 2.0, 3.0, None]
FLOORS = [12.0, 16.0, 20.0, 25.0]
N = 5
DRAWS = 20
ALERT = 0.7
MODEL = load_model()


def load(path):
    feats = defaultdict(dict)
    for l in open(path):
        r = json.loads(l)
        if r["features"]:
            feats[r["speaker"]][(r["condition"], r["day"])] = r["features"]
    return feats


def draws(feats, rng):
    out = []
    for s, f in sorted(feats.items()):
        days = sorted(d for c, d in f if c == "normal")
        for t in days:
            combos = list(combinations([d for d in days if d != t], N))
            for c in rng.sample(combos, min(DRAWS, len(combos))):
                out.append((s, t, c))
    return out


def rates(feats, dr, cap, floor, speakers):
    hit = defaultdict(list)
    for s, t, c in dr:
        if s not in speakers:
            continue
        b = build_baseline([feats[s][("normal", d)] for d in c])
        b["features"]["words_per_min"]["std"] = max(b["features"]["words_per_min"]["std"], floor)
        for (cond, day), f in feats[s].items():
            if day != t or cond == "tv20":
                continue
            z = change_scores(f, b)
            if cap is not None:
                z = {k: min(v, cap) if k in ("filler_rate", "repeat_rate") else v for k, v in z.items()}
            hit[cond].append(change_probability(z, MODEL) >= ALERT)
    return {k: sum(v) / len(v) for k, v in hit.items()}


def main():
    rng = random.Random(7)
    real, synth = load(sys.argv[1]), load(sys.argv[2])
    dr_real, dr_synth = draws(real, rng), draws(synth, rng)
    grid = []
    for cap in CAPS:
        for floor in FLOORS:
            r = rates(real, dr_real, cap, floor, set(real))
            s = rates(synth, dr_synth, cap, floor, set(synth))
            grid.append({"cap": cap, "wpm_floor": floor, "synth_normal": s["normal"], "synth_slow": s["slow_tremor"],
                         "real_normal": r["normal"], "real_slow": r["slow_tremor"], "real_hesitant": r["hesitant"]})
            print(f"cap {str(cap):5} floor {floor:4.0f}  synth healthy {s['normal']:6.1%} slowed {s['slow_tremor']:6.1%}  "
                  f"real healthy {r['normal']:6.1%} slowed {r['slow_tremor']:6.1%} hesitant {r['hesitant']:6.1%}")

    # Choose on half the synthetic voices (lowest healthy alarms while real
    # hesitant catches stay at 85% or more), check on the other half.
    voices = sorted(synth)
    halves = [set(voices[::2]), set(voices[1::2])]
    split = []
    for pick, check in (halves, halves[::-1]):
        best = None
        for g in grid:
            if g["real_hesitant"] < 0.85:
                continue
            fa = rates(synth, dr_synth, g["cap"], g["wpm_floor"], pick)["normal"]
            if best is None or fa < best[0]:
                best = (fa, g["cap"], g["wpm_floor"])
        app = rates(synth, dr_synth, None, 12.0, check)["normal"]
        held = rates(synth, dr_synth, best[1], best[2], check)["normal"]
        split.append({"chosen_cap": best[1], "chosen_floor": best[2], "healthy_alarms_chosen_half": best[0],
                      "healthy_alarms_other_half_app": app, "healthy_alarms_other_half_capped": held})
        print(f"chosen cap {best[1]} floor {best[2]} on half A ({best[0]:.1%}); other half: app {app:.1%} -> capped {held:.1%}")
    json.dump({"baseline_days": N, "grid": grid, "split_check": split}, open(sys.argv[3], "w"), indent=1)


if __name__ == "__main__":
    main()
