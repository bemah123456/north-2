"""Remix the "older" clips with the TV at several loudness levels, to find
where speech recognition breaks and whether a simple check on the
recording can spot it first.

Usage: make_tv_levels.py MODELS_DIR AUDIO_DIR
Writes AUDIO_DIR/tv{N}/... and AUDIO_DIR/manifest_levels.jsonl.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

import make_audio as M

LEVELS = [5, 15, 20]  # dB the TV sits below the speaker (10 is the main study)
VOICES = set(os.environ.get("VOICES", "").split(","))


def main():
    models, audio = Path(sys.argv[1]), Path(sys.argv[2])
    M.MODELS = models
    libri = M.piper("vits-piper-en_US-libritts_r-medium")
    tv = np.concatenate([M.say(libri, line, 900 - 7 * i, 1.0) for i, line in enumerate(M.TV_LINES)])
    rng = np.random.default_rng(1)
    rows = [json.loads(l) for l in (audio / "manifest.jsonl").read_text().splitlines()]
    out = []
    for r in rows:
        if r["condition"] != "older" or r["voice"] not in VOICES:
            continue
        older, _ = sf.read(audio / r["path"], dtype="float32")
        phone = M.ffmpeg(older, M.SR, "highpass=f=300,lowpass=f=3400")
        start = rng.integers(0, len(tv) - len(phone)) if len(tv) > len(phone) else 0
        bg = np.resize(tv[start:], len(phone)).astype(np.float32)
        bg = M.ffmpeg(bg, M.SR, "highpass=f=300,lowpass=f=3400")[: len(phone)]
        for db in LEVELS:
            x = phone + bg * (M.rms(phone) / M.rms(bg)) * 10 ** (-db / 20)
            x = (x / max(1.0, float(np.abs(x).max()))).astype(np.float32)
            cond = f"tv{db}"
            path = audio / cond / r["voice"] / Path(r["path"]).name
            path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(path, x, M.SR)
            out.append({**r, "condition": cond, "path": str(path.relative_to(audio))})
    (audio / "manifest_levels.jsonl").write_text("".join(json.dumps(r) + "\n" for r in out))
    print(len(out), "clips")


if __name__ == "__main__":
    main()
