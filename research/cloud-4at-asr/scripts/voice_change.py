"""Does the room alone trip the app's voice-change alarm?

The app's 4AT part 4 ("acute change") can come from the voice: features
from word timestamps (answer delay, speaking rate, pauses, fillers,
repeats) are compared with the person's own normal days, and a change
probability of 0.7 or more scores 4 points, enough for "call their doctor
today" on its own.

Here each voice gets 5 "days": day d uses the d-th healthy wording of each
orientation answer plus the d-th months-backwards answer. For each test day
the other 4 days are the baseline (all recorded in a quiet room), and the
test day is recorded quiet, slower with a tremor (a real change in how the
person talks), or with a TV in the background (a change in the room, not
the person). Word timestamps come from Parakeet.

Usage: voice_change.py MODELS_DIR AUDIO_DIR OUT_JSON
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, "/mnt/project-files/daily-checkin/server")
from checkin.baseline import build_baseline, change_probability, change_scores, top_reasons  # noqa: E402
from checkin.features import Word, checkin_features  # noqa: E402

import noise_check  # noqa: E402
import sherpa_onnx  # noqa: E402

ITEMS = ["age", "dob", "place", "year", "months_backwards"]
DAYS = 5
CONDITIONS = ["clean", "older", "tv20", "tv"]
VOICES = "libritts-3,libritts-112,libritts-260,libritts-401,libritts-560,libritts-721,vctk-2,vctk-40,vctk-80,kokoro-0,kokoro-5,kokoro-8".split(",")
ALERT = 0.7


def words_of(rec, x, sr):
    s = rec.create_stream()
    s.accept_waveform(sr, x)
    rec.decode_stream(s)
    r = s.result
    words = []
    durs = list(getattr(r, "durations", []) or [0.0] * len(r.tokens))
    for tok, start, dur in zip(r.tokens, r.timestamps, durs):
        end = start + max(dur, 0.0)
        if tok.startswith(" ") or not words:
            if tok.strip():
                words.append(Word(tok.strip(), float(start), float(end)))
        else:
            words[-1].text += tok
            words[-1].end = max(words[-1].end, float(end))
    return words


def main():
    models, audio, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    d = models / "sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8"
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(d / "encoder.int8.onnx"), decoder=str(d / "decoder.int8.onnx"),
        joiner=str(d / "joiner.int8.onnx"), tokens=str(d / "tokens.txt"),
        model_type="nemo_transducer", num_threads=4)
    path = {}
    for f in ("manifest.jsonl", "manifest_levels.jsonl"):
        for l in (audio / f).read_text().splitlines():
            r = json.loads(l)
            path[(r["condition"], r["voice"], r["id"])] = r["path"]

    feats = {}  # (cond, voice, day) -> features
    noisy = {}
    for cond in CONDITIONS:
        for v in VOICES:
            for d in range(DAYS):
                clips, flags = {}, 0
                for item in ITEMS:
                    p = path[(cond, v, f"healthy-{item}-{d}")]
                    x, sr = sf.read(audio / p, dtype="float32")
                    clips[item] = words_of(rec, x, sr)
                    flags += noise_check.background_flicker(x, sr) > 4.4
                feats[(cond, v, d)] = checkin_features(clips)
                noisy[(cond, v, d)] = flags >= 3
        print(cond, "done", flush=True)

    results = defaultdict(Counter)
    reasons = defaultdict(Counter)
    for cond in CONDITIONS:
        for v in VOICES:
            for d in range(DAYS):
                base = build_baseline([feats[("clean", v, o)] for o in range(DAYS) if o != d])
                z = change_scores(feats[(cond, v, d)], base)
                p = change_probability(z)
                c = results[cond]
                c["tests"] += 1
                c["alert"] += p >= ALERT
                c["watch"] += 0.4 <= p < ALERT
                c["alert_after_room_check"] += p >= ALERT and not noisy[(cond, v, d)]
                c["asked_to_turn_tv_off"] += noisy[(cond, v, d)]
                if p >= ALERT:
                    for t in top_reasons(z):
                        reasons[cond][t] += 1
                c["_p_sum"] += p
    summary = {cond: {**{k: v for k, v in c.items() if not k.startswith("_")},
                      "mean_probability": round(c["_p_sum"] / c["tests"], 3),
                      "alert_reasons": dict(reasons[cond])}
               for cond, c in results.items()}
    out.write_text(json.dumps({"summary": summary,
                               "features": {f"{c}|{v}|{d}": f for (c, v, d), f in feats.items()}}, indent=1))
    for cond, s in summary.items():
        n = s["tests"]
        print(f"{cond:6} alarm (4 points) {s['alert'] / n:5.1%}  watch {s['watch'] / n:5.1%}  "
              f"mean p {s['mean_probability']:.2f}  after room check {s['alert_after_room_check'] / n:5.1%}  "
              f"reasons {s['alert_reasons']}")


if __name__ == "__main__":
    main()
