"""A quiet-room check the app can run on each recording before scoring it.

background_flicker() looks at the quietest 40% of 30 ms frames, the gaps
between and around the person's words, and measures how much their
loudness jumps from frame to frame. A TV or radio fills the gaps with
speech, which flickers (about 5 to 9 dB); a fan, hiss or a quiet room is
steady (under about 4 dB). Above 4.4 dB the gaps probably hold someone
else talking.

estimate_snr() is the plainer speech-to-background ratio. It drops with
any noise, steady or not, so it can't tell a TV from a fan.

Usage: noise_check.py AUDIO_DIR OUT_JSON   (measures every clip in both manifests)
"""

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

FRAME_S = 0.03


def estimate_snr(x: np.ndarray, sr: int = 16000) -> float:
    """Speech-to-background ratio in dB: 90th against 15th percentile of
    30 ms frame loudness. Digital silence is floored at -80 dBFS so a
    perfectly clean clip reads high but finite."""
    frame = int(FRAME_S * sr)
    n = len(x) // frame
    if n < 10:
        return float("nan")
    rms = np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1))
    db = 20 * np.log10(np.maximum(rms, 1e-4))
    return float(np.percentile(db, 90) - np.percentile(db, 15))


def background_flicker(x: np.ndarray, sr: int = 16000) -> float:
    """Mean frame-to-frame loudness change (dB) across the quietest 40% of
    30 ms frames."""
    frame = int(FRAME_S * sr)
    n = len(x) // frame
    if n < 10:
        return 0.0
    rms = np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1))
    db = 20 * np.log10(np.maximum(rms, 1e-4))
    quiet = db[db <= np.percentile(db, 40)]
    return float(np.abs(np.diff(quiet)).mean()) if len(quiet) > 2 else 0.0


def main():
    audio, out = Path(sys.argv[1]), Path(sys.argv[2])
    snr = {}
    for name in ("manifest.jsonl", "manifest_levels.jsonl"):
        f = audio / name
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            r = json.loads(line)
            x, sr = sf.read(audio / r["path"], dtype="float32")
            snr[r["path"]] = round(estimate_snr(x, sr), 2)
    out.write_text(json.dumps(snr))
    print(len(snr), "clips measured")


if __name__ == "__main__":
    main()
