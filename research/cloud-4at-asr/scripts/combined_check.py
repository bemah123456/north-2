"""PR #12's combined change score on the research day sets.

PR #12 replaces "the voice alone scores 4 points" with evidence from
several parts added up (daily-checkin/server/checkin/change.py): a total
of 2.5 or more is "some change", and 4.5 or more with two parts of 1 or
more is "a big change", which scores the 4AT's acute change item.

Synthetic days (12 voices, 16 days, voice_days_synth.py): the answers are
scored from Whisper small's transcripts of the same clips with the
transcript fixes, the voice from Parakeet word timestamps, and a day is
noisy when 3 or more answers have background speech (flicker and gap).
Real days (20 speakers, 10 days, voice_days_transcribe.py): read
sentences, so only the voice and its timing can count.

Each test day gets up to 20 random sets of 5 other normal days as its
normal. Digit span, greeting, evening and routine signs are not in either
set, so they count nothing here.

Usage: combined_check.py PR12_SERVER_DIR AUDIO_DIR HYP_DIR HYP_LEVELS_DIR SPEECH_JSON SYNTH_DAYS REAL_DAYS OUT_JSON
"""

import json
import random
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import soundfile as sf

ARGS = sys.argv[1:]
sys.path.insert(0, ARGS[0])
from checkin import change as C  # noqa: E402
from checkin.baseline import build_baseline, change_probability, change_scores  # noqa: E402

AUDIO, HYPS, HYPS_LV, SPEECH = (Path(p) for p in ARGS[1:5])
SYNTH, REAL, OUT = Path(ARGS[5]), Path(ARGS[6]), Path(ARGS[7])
sys.argv = sys.argv[:1] + [str(AUDIO), str(HYPS), "/tmp"]
import analyze as AN  # noqa: E402
import noise_check as NC  # noqa: E402
import robust  # noqa: E402

N, DRAWS = 5, 20
AUDIO_COND = {"normal": "clean", "slow_tremor": "older", "tv20": "tv20"}


def load_days(path):
    days = defaultdict(dict)
    for l in open(path):
        r = json.loads(l)
        if r["features"]:
            days[r["speaker"]][(r["condition"], r["day"])] = r
    return days


def main():
    meta = {}
    for f in ("manifest.jsonl", "manifest_levels.jsonl"):
        for l in (AUDIO / f).read_text().splitlines():
            r = json.loads(l)
            meta[(r["condition"], r["voice"], r["id"])] = r
    hyp = {}
    for f in (HYPS / "sherpa-onnx-whisper-small.jsonl", HYPS_LV / "sherpa-onnx-whisper-small.jsonl"):
        for l in f.read_text().splitlines():
            h = json.loads(l)
            hyp[h["path"]] = h["hyp"]
    speech = json.loads(SPEECH.read_text())
    noisy_clip = {}

    def answer_measures(voice, cond, ids):
        ac = AUDIO_COND[cond]
        mistakes, att, noisy = 0, None, 0
        for i in ids:
            m = meta[(ac, voice, i)]
            p = m["path"]
            if p not in hyp:
                return None
            if p not in speech or p not in noisy_clip:
                x, sr = sf.read(AUDIO / p, dtype="float32")
                speech.setdefault(p, robust.has_speech(x, sr))
                noisy_clip[p] = NC.background_speech(x, sr)
            noisy += noisy_clip[p]
            s = AN.part_score(AN.fixed_verdict(m["kind"], hyp[p], speech[p]))
            if m["kind"] in AN.ORIENT:
                mistakes += (s or 0) > 0
            else:
                att = s
        return {"orientation_mistakes": mistakes, "attention_score": att, "noisy": noisy >= 3}

    rng = random.Random(7)
    results = defaultdict(Counter)
    parts = defaultdict(Counter)
    for label, path in (("Synthetic", SYNTH), ("Real", REAL)):
        days = load_days(path)
        for s, d in sorted(days.items()):
            normal_days = sorted(day for c, day in d if c == "normal")
            am = {}
            if label == "Synthetic":
                for (c, day), r in d.items():
                    am[(c, day)] = answer_measures(s, c, r["ids"])
            for t in normal_days:
                combos = list(combinations([x for x in normal_days if x != t], N))
                for combo in rng.sample(combos, min(DRAWS, len(combos))):
                    base = build_baseline([d[("normal", x)]["features"] for x in combo])
                    past = []
                    for x in combo:
                        a = am.get(("normal", x)) or {}
                        past.append({"orientation_mistakes": a.get("orientation_mistakes", 0),
                                     "attention_score": a.get("attention_score", 0),
                                     "latency_s": d[("normal", x)]["features"]["latency_s"]})
                    normal = C.personal_normal(past)
                    for (c, day), r in d.items():
                        if day != t:
                            continue
                        a = am.get((c, day), {"orientation_mistakes": 0, "attention_score": 0, "noisy": False})
                        if a is None:
                            continue
                        f = r["features"]
                        z = change_scores(f, base)
                        prob = change_probability(z)
                        measures = {"orientation_mistakes": a["orientation_mistakes"],
                                    "attention_score": a["attention_score"], "latency_s": f["latency_s"],
                                    "slow_answers": 0, "unanswered": 0, "digits_correct": None}
                        signs = C.drowsiness_signs(measures, z, {})
                        e = C.evidence(measures, normal, prob, signs)
                        res = C.combine(e, a["noisy"])
                        key = f"{label}|{c}"
                        results[key]["tests"] += 1
                        results[key][res["level"]] += 1
                        results[key]["voice_alone_old_rule"] += prob >= 0.7
                        results[key]["noisy"] += a["noisy"]
                        if res["level"] != "usual":
                            for k, v in e.items():
                                if v >= 1:
                                    parts[f"{key}|{res['level']}"][k] += 1
    out = []
    for key, c in sorted(results.items()):
        n = c["tests"]
        row = {"days": key.split("|")[0], "condition": key.split("|")[1], "tests": n,
               "some_change": round(c["some"] / n, 4), "big_change": round(c["big"] / n, 4),
               "old_voice_alarm": round(c["voice_alone_old_rule"] / n, 4), "noisy": round(c["noisy"] / n, 4),
               "parts_when_some": dict(parts[f"{key}|some"]), "parts_when_big": dict(parts[f"{key}|big"])}
        out.append(row)
        print(f"{key:24} some {row['some_change']:6.1%}  big {row['big_change']:6.1%}  "
              f"(voice alone, old rule {row['old_voice_alarm']:6.1%})  noisy {row['noisy']:5.1%}  "
              f"big from {row['parts_when_big']}  some from {row['parts_when_some']}")
    OUT.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
