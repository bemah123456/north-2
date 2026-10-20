"""What asking again really costs.

The fixed scorer asks a question again instead of scoring an empty or
number-less answer, and the main tables counted that answer as right for a
healthy person. Here the second answer is modelled: the same voice answers
the same question in one of its other wordings, and a second answer that
is wrong or again unusable counts as a mistake (as the README recommends).

Usage: reask.py AUDIO_DIR HYP_DIR SPEECH_JSON OUT_JSON
"""

import json
import sys
from collections import defaultdict
from itertools import product
from pathlib import Path

AUDIO, HYPS, SPEECH, OUT = (Path(p) for p in sys.argv[1:5])
sys.argv = sys.argv[:1] + [str(AUDIO), str(HYPS), "/tmp"]
import analyze as AN  # noqa: E402

MODELS = {"sherpa-onnx-whisper-small": "Whisper small", "sherpa-onnx-whisper-small.en": "Whisper small.en",
          "sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8": "Parakeet TDT 0.6B", "sherpa-onnx-whisper-base.en": "Whisper base.en"}


def main():
    meta = {r["path"]: r for r in map(json.loads, (AUDIO / "manifest.jsonl").read_text().splitlines())}
    speech = json.loads(SPEECH.read_text())
    out = []
    for m, name in MODELS.items():
        hyp = {json.loads(l)["path"]: json.loads(l)["hyp"] for l in (HYPS / f"{m}.jsonl").read_text().splitlines()}
        for cond in ("clean", "older", "tv"):
            s = defaultdict(dict)  # voice -> id -> part score or None
            for p, h in hyp.items():
                r = meta[p]
                if r["condition"] == cond and r["label"] == "healthy" and p in speech:
                    s[r["voice"]][r["id"]] = AN.part_score(AN.fixed_verdict(r["kind"], h, speech[p]))
            tot = n = asked = 0.0
            first_only = 0.0
            for v, got in s.items():
                if len(got) < sum(len(x) for x in AN.HEALTHY.values()):
                    continue

                def p_wrong(i):
                    if got[i] is None:
                        kind = i.split("-")[1]
                        others = [got[f"healthy-{kind}-{j}"] for j in range(len(AN.HEALTHY[kind])) if f"healthy-{kind}-{j}" != i]
                        return sum(o != 0 for o in others) / len(others)
                    return float(got[i] > 0)
                pw = {i: p_wrong(i) for i in got}
                attn = [f"healthy-{k}-{i}" for k in AN.ATTN for i in range(len(AN.HEALTHY[k]))]
                orient = [[f"healthy-{k}-{i}" for i in range(len(AN.HEALTHY[k]))] for k in AN.ORIENT]
                for combo in product(*orient, attn):
                    ok = 1.0
                    for i in combo:
                        ok *= 1 - pw[i]
                    tot += 1 - ok
                    first_only += any((got[i] or 0) > 0 for i in combo)
                    asked += any(got[i] is None for i in combo)
                    n += 1
            if n:
                out.append({"model": name, "condition": cond, "checkins": int(n),
                            "concern_reask_counted_right": round(first_only / n, 4),
                            "concern_second_answer_scored": round(tot / n, 4),
                            "checkins_with_a_reask": round(asked / n, 4)})
                print(f"{name:20}{cond:6} concern {first_only / n:6.1%} -> {tot / n:6.1%} with the second answer scored; "
                      f"check-ins with a re-ask {asked / n:6.1%}")
    OUT.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
