"""Synthetic "days" with conversational answers, to go with the real
speakers' read sentences.

Each of 12 synthetic voices answers the four orientation questions and one
attention task in one of 5 wordings each, so a day is one pick of wordings
(6,250 possible days per voice). 16 random days per voice are its normal
days. Each day is also scored as recorded slower with a tremor ("older"),
and with a TV 20 dB below the voice ("tv20"), from the main study's clips.

Usage: voice_days_synth.py MODELS_DIR AUDIO_DIR OUT_JSONL
"""

import json
import random
import sys
from pathlib import Path

import soundfile as sf

sys.path.insert(0, "/mnt/project-files/daily-checkin/server")
from checkin.features import checkin_features  # noqa: E402

import voice_change as VC  # noqa: E402
import sherpa_onnx  # noqa: E402

DAYS = 16
CONDS = {"clean": "normal", "older": "slow_tremor", "tv20": "tv20"}
ORIENT = ["age", "dob", "place", "year"]
ATTN = [("months_backwards", 5), ("days_backwards", 3), ("countdown_20", 2)]


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
    attn_ids = [f"healthy-{k}-{i}" for k, n in ATTN for i in range(n)]
    rng = random.Random(11)
    with out.open("w") as f:
        for v in VC.VOICES:
            words = {}
            days = [[f"healthy-{k}-{rng.randrange(5)}" for k in ORIENT] + [rng.choice(attn_ids)] for _ in range(DAYS)]
            for cond, label in CONDS.items():
                for day, ids in enumerate(days, 1):
                    clips = {}
                    for i in ids:
                        if (cond, i) not in words:
                            x, sr = sf.read(audio / path[(cond, v, i)], dtype="float32")
                            words[(cond, i)] = VC.words_of(rec, x, sr)
                        clips[i.split("-")[1]] = words[(cond, i)]
                    f.write(json.dumps({"speaker": v, "day": day, "condition": label, "ids": ids,
                                        "features": checkin_features(clips)}) + "\n")
            f.flush()
            print(v, flush=True)


if __name__ == "__main__":
    main()
