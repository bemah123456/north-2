"""How many normal days does the voice-change score need, and can it be
made to tell a changed voice from a normal one?

Uses voice_days_transcribe.py's output: 20 real older speakers, 10 normal
days each, plus each day slowed with a tremor ("slow_tremor") and made
hesitant ("hesitant"). For every speaker, test day and baseline size N, up
to 20 random sets of N other normal days form the baseline. A test is a
false alarm when a normal day scores 4 points (change probability 0.7 or
more), and a catch when a changed day does.

Three ways to score, each judged on speakers it never learned from:

  app      the app as it is (baseline.py and model.json)
  shrink   each person's spread is pulled toward the spread seen across
           other people's normal days, so a short baseline can't look
           unrealistically steady
  capped   the app's model, but one-off words can't trigger it alone: the
           "um" and repeated-word scores count at most 1.5 spreads, and
           speaking rate is judged against a spread of at least 20 words
           a minute (what real older speakers vary by day to day)
  refit    shrink, plus model weights and an alarm threshold learned from
           the other 19 speakers' real normal and changed days, with the
           threshold set so their normal days alarm at most 2% of the time

Usage: voice_baseline_study.py VOICE_DAYS_JSONL OUT_JSON
"""

import json
import math
import os
import random
import sys
from collections import defaultdict
from itertools import combinations

import numpy as np
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, "/mnt/project-files/daily-checkin/server")
from checkin.baseline import STD_FLOOR, build_baseline, change_probability, change_scores, load_model  # noqa: E402
from checkin.features import FEATURE_DIRECTIONS  # noqa: E402

ALERT = 0.7
NS = list(range(2, int(os.environ.get("MAX_N", "9")) + 1))
DRAWS = 20
K = 4  # how many "days" of other people's spread a baseline starts with
NAMES = [n for n in FEATURE_DIRECTIONS if n != "greeting_words"]  # no greeting in read speech
CHANGES = []  # every condition in the input besides "normal"
MAX_FALSE_ALARM = 0.02


def pooled_spread(days_by_spk, speakers):
    """Typical day-to-day spread of each feature within one person."""
    out = {}
    for n in NAMES:
        devs = []
        for s in speakers:
            v = [d[n] for d in days_by_spk[s].values()]
            m = sum(v) / len(v)
            devs += [(x - m) ** 2 for x in v]
            # n - 1 per speaker
        dof = sum(len(days_by_spk[s]) - 1 for s in speakers)
        out[n] = math.sqrt(sum(devs) / dof)
    return out


def shrunk_baseline(days, pop):
    b = build_baseline(days)
    n = len(days)
    for name in NAMES:
        vals = [d[name] for d in days]
        m = sum(vals) / n
        s2 = sum((x - m) ** 2 for x in vals) / n
        b["features"][name]["std"] = max(math.sqrt((n * s2 + K * pop[name] ** 2) / (n + K)), STD_FLOOR[name])
    return b


CAP = {"filler_rate": 1.5, "repeat_rate": 1.5}
WPM_FLOOR = 20.0


def capped_z(today, days):
    b = build_baseline(days)
    b["features"]["words_per_min"]["std"] = max(b["features"]["words_per_min"]["std"], WPM_FLOOR)
    z = change_scores(today, b)
    return {k: min(v, CAP.get(k, v)) for k, v in z.items()}


def zvec(today, base):
    z = change_scores(today, base)
    return [max(min(z[n], 6.0), -6.0) for n in NAMES]


def main():
    rows = [json.loads(l) for l in open(sys.argv[1])]
    CHANGES[:] = sorted({r["condition"] for r in rows} - {"normal"})
    feats = defaultdict(dict)  # speaker -> (cond, day) -> features
    for r in rows:
        if r["features"]:
            feats[r["speaker"]][(r["condition"], r["day"])] = r["features"]
    speakers = sorted(s for s in feats if sum(c == "normal" for c, _ in feats[s]) > max(NS))
    normal = {s: {d: f for (c, d), f in feats[s].items() if c == "normal"} for s in speakers}
    app_model = load_model()
    rng = random.Random(7)

    # Baseline draws, fixed up front so every method sees the same ones.
    draws = []  # (speaker, test_day, N, baseline_days)
    for s in speakers:
        days = sorted(normal[s])
        for t in days:
            others = [d for d in days if d != t]
            for N in NS:
                combos = list(combinations(others, N))
                for c in rng.sample(combos, min(DRAWS, len(combos))):
                    draws.append((s, t, N, c))

    def tests(s, t):
        yield "normal", normal[s][t]
        for ch in CHANGES:
            if (ch, t) in feats[s]:
                yield ch, feats[s][(ch, t)]

    results = {m: defaultdict(lambda: defaultdict(list)) for m in ("app", "shrink", "capped", "refit")}
    reasons = defaultdict(int)
    for s in speakers:
        rest = [o for o in speakers if o != s]
        pop = pooled_spread(normal, rest)

        # refit: learn weights from the other speakers (their own baselines
        # from all their other normal days, shrunk the same way).
        X, y = [], []
        for o in rest:
            od = sorted(normal[o])
            for t in od:
                base = shrunk_baseline([normal[o][d] for d in od if d != t], pop)
                for cond, f in tests(o, t):
                    if cond == "tv20":  # background TV is the room check's job, not a change in the person
                        continue
                    X.append(zvec(f, base))
                    y.append(cond != "normal")
        clf = LogisticRegression(class_weight="balanced", C=0.5, max_iter=2000).fit(np.array(X), np.array(y))
        p_tr = clf.predict_proba(np.array(X))[:, 1]
        thr = float(np.quantile(p_tr[~np.array(y)], 1 - MAX_FALSE_ALARM))

        for (ss, t, N, c) in draws:
            if ss != s:
                continue
            days = [normal[s][d] for d in c]
            b_app = build_baseline(days)
            b_sh = shrunk_baseline(days, pop)
            for cond, f in tests(s, t):
                z = change_scores(f, b_app)
                p = change_probability(z, app_model)
                results["app"][cond][N].append(p >= ALERT)
                if cond == "normal" and p >= ALERT:
                    reasons[max(NAMES, key=lambda n: z[n])] += 1
                results["capped"][cond][N].append(change_probability(capped_z(f, days), app_model) >= ALERT)
                results["shrink"][cond][N].append(change_probability(change_scores(f, b_sh), app_model) >= ALERT)
                results["refit"][cond][N].append(clf.predict_proba(np.array([zvec(f, b_sh)]))[0, 1] >= thr)

    out = []
    for m, byc in results.items():
        for cond, byn in byc.items():
            for N, v in sorted(byn.items()):
                out.append({"method": m, "condition": cond, "baseline_days": N, "tests": len(v),
                            "alarm_rate": round(sum(v) / len(v), 4)})
    final = clf.fit(np.array(X), np.array(y))
    summary = {"speakers": len(speakers), "draws_per_test": DRAWS, "rows": out,
               "app_false_alarm_top_feature": dict(reasons),
               "pooled_spread_all": pooled_spread(normal, speakers),
               "app_std_floor": {n: STD_FLOOR[n] for n in NAMES},
               "refit_weights_last_fold": dict(zip(NAMES, [round(w, 3) for w in final.coef_[0]]))}
    json.dump(summary, open(sys.argv[2], "w"), indent=1)
    print(f"{'method':8}{'cond':12}" + "".join(f"N={n:<5}" for n in NS))
    for m in results:
        for cond in ["normal"] + CHANGES:
            r = {x["baseline_days"]: x["alarm_rate"] for x in out if x["method"] == m and x["condition"] == cond}
            print(f"{m:8}{cond:12}" + "".join(f"{r[n]:<7.1%}" for n in NS))
    print("app false alarms by top feature", dict(reasons))
    print("pooled spread", {k: round(v, 3) for k, v in summary["pooled_spread_all"].items()})


if __name__ == "__main__":
    main()
