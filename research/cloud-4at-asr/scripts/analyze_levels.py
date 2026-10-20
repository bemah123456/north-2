"""How loud can the TV be, and how much does a "please turn off the TV"
prompt help?

For each model and TV level, scores healthy check-ins with the fixed
rules, then again with the quiet-room check: when most of a check-in's
answers have speech in the background, the app asks for the TV to be
turned off and records again (modelled with the same answers' quiet
"older" recordings).

Usage: analyze_levels.py AUDIO_DIR OUT_DIR HYP_DIR [HYP_DIR ...]
"""

import json
import sys
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

import numpy as np
import soundfile as sf

import analyze as AN
import noise_check

AUDIO, OUT = Path(sys.argv[1]), Path(sys.argv[2])
HYP_DIRS = [Path(p) for p in sys.argv[3:]]
LEVELS = ["older", "tv20", "tv15", "tv", "tv5"]  # "tv" is 10 dB
FLICKER = 4.4  # dB; see noise_check.background_speech
MODELS = ["sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8", "sherpa-onnx-whisper-small", "sherpa-onnx-whisper-small.en"]


def main():
    rows = [json.loads(l) for f in ("manifest.jsonl", "manifest_levels.jsonl")
            for l in (AUDIO / f).read_text().splitlines()]
    meta = {r["path"]: r for r in rows}
    hyps = defaultdict(dict)
    for d in HYP_DIRS:
        for m in MODELS:
            f = d / f"{m}.jsonl"
            if f.exists():
                for l in f.read_text().splitlines():
                    h = json.loads(l)
                    hyps[m][h["path"]] = h["hyp"]
    key = lambda p: (meta[p]["condition"], meta[p]["voice"], meta[p]["id"])  # noqa: E731
    paths = {}
    for m in MODELS:
        for p in hyps[m]:
            if meta[p]["condition"] in LEVELS:
                paths[key(p)] = p
    voices = sorted({v for (c, v, i) in paths if c == "tv5"})

    speech_f = OUT / "speech.json"
    speech = json.loads(speech_f.read_text()) if speech_f.exists() else {}
    flicker = {}
    for p in paths.values():
        x, sr = sf.read(AUDIO / p, dtype="float32")
        if p not in speech:
            import robust
            speech[p] = robust.has_speech(x, sr)
        flicker[p] = noise_check.background_flicker(x, sr)
    speech_f.write_text(json.dumps(speech))

    out = []
    attn_ids = [f"healthy-{k}-{i}" for k in AN.ATTN for i in range(len(AN.HEALTHY[k]))]
    orient_ids = [[f"healthy-{k}-{i}" for i in range(len(AN.HEALTHY[k]))] for k in AN.ORIENT]
    for m in MODELS:
        part = {}
        for k, p in paths.items():
            if p in hyps[m]:
                part[k] = AN.part_score(AN.fixed_verdict(meta[p]["kind"], hyps[m][p], speech[p]))
        for cond in LEVELS:
            c = Counter()
            for v in voices:
                if not all((cond, v, i) in part and ("older", v, i) in part for i in AN.TEXT):
                    continue
                for combo in product(*orient_ids, attn_ids):
                    noisy = sum(flicker[paths[(cond, v, i)]] > FLICKER for i in combo) >= 3
                    take = "older" if noisy else cond

                    def total(level):
                        s = [part[(level, v, i)] or 0 for i in combo]
                        return min(sum(s[:4]), 2) + s[4]
                    c["checkins"] += 1
                    c["flagged"] += total(cond) >= 1
                    c["prompted"] += noisy
                    c["flagged_with_check"] += total(take) >= 1
            if c["checkins"]:
                out.append({"model": m, "condition": cond, **c})
    (OUT / "levels.json").write_text(json.dumps(out, indent=1))
    names = {"older": "quiet", "tv20": "TV -20 dB", "tv15": "TV -15 dB", "tv": "TV -10 dB", "tv5": "TV -5 dB"}
    for s in out:
        n = s["checkins"]
        print(f"{s['model'][12:]:<32}{names[s['condition']]:<11} false alarms {s['flagged'] / n:6.1%}"
              f"  asked to turn TV off {s['prompted'] / n:6.1%}  false alarms with check {s['flagged_with_check'] / n:6.1%}")


if __name__ == "__main__":
    main()
