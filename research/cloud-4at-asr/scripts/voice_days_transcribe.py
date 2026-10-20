"""Word timestamps for real older speakers' "days", as recorded and changed.

Input: the PC's speaker_days set (20 Common Voice speakers aged 60+, 10
clips each, one clip standing for one normal day). Each clip is also
changed two ways, standing for a day when the person is not themselves:

  slow_tremor  20% slower with a 6 Hz voice tremor (the "older" effect
               from the main study)
  hesitant     1 s longer to start, a 0.7 s pause after every third word,
               and 10% slower

Every version goes through Parakeet for word timestamps, and the app's own
checkin_features turns them into the day's features.

Usage: voice_days_transcribe.py MODELS_DIR SPEAKER_DAYS_DIR OUT_JSONL
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/mnt/project-files/daily-checkin/server")
from checkin.features import checkin_features  # noqa: E402

import voice_change  # noqa: E402  (words_of)
import sherpa_onnx  # noqa: E402

SR = 16000


def ffmpeg(args_in, x=None, filters=None):
    cmd = ["ffmpeg", "-v", "error"] + args_in
    if filters:
        cmd += ["-af", filters]
    cmd += ["-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
    out = subprocess.run(cmd, input=None if x is None else x.astype(np.float32).tobytes(),
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()


def raw_in():
    return ["-f", "f32le", "-ac", "1", "-ar", str(SR), "-i", "-"]


def hesitant(x, words):
    cuts = [int(w.end * SR) for i, w in enumerate(words[:-1]) if i % 3 == 2]
    parts, prev = [np.zeros(SR, dtype=np.float32)], 0
    for c in cuts:
        parts += [x[prev:c], np.zeros(int(0.7 * SR), dtype=np.float32)]
        prev = c
    parts.append(x[prev:])
    return ffmpeg(raw_in(), np.concatenate(parts), "atempo=0.9")


def main():
    models, src, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    d = models / "sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8"
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(d / "encoder.int8.onnx"), decoder=str(d / "decoder.int8.onnx"),
        joiner=str(d / "joiner.int8.onnx"), tokens=str(d / "tokens.txt"),
        model_type="nemo_transducer", num_threads=4)
    rows = list(csv.DictReader((src / "speakers.csv").open(encoding="utf-8")))
    with out.open("w") as f:
        for r in rows:
            x = ffmpeg(["-i", str(src / r["file"])])
            words = voice_change.words_of(rec, x, SR)
            versions = {"normal": (x, words)}
            y = ffmpeg(raw_in(), x, "atempo=0.8,vibrato=f=6:d=0.25")
            versions["slow_tremor"] = (y, voice_change.words_of(rec, y, SR))
            if words:
                y = hesitant(x, words)
                versions["hesitant"] = (y, voice_change.words_of(rec, y, SR))
            for cond, (_, w) in versions.items():
                feats = checkin_features({"answer": w})
                f.write(json.dumps({"speaker": r["speaker"], "day": int(r["day"]), "condition": cond,
                                    "text": " ".join(t.text for t in w), "features": feats}) + "\n")
            f.flush()
            print(r["file"], flush=True)


if __name__ == "__main__":
    main()
