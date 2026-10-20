"""Read every test answer in many synthetic voices, in three conditions.

clean:  the voice as generated
older:  20% slower, with a voice tremor (6 Hz vibrato), like many 80-year-olds
tv:     older, through a phone band (300-3400 Hz), with a TV talking in the
        background at 10 dB below the speaker. The TV mentions dates and
        numbers on purpose, the worst case for false positives.

Usage: make_audio.py MODELS_DIR OUT_DIR
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import sherpa_onnx
import soundfile as sf

from answers_set import all_items

MODELS, OUT = Path(sys.argv[1]), Path(sys.argv[2])
SR = 16000
TV_LINES = [
    "And in tonight's news, the city council met on Tuesday to discuss the budget for twenty twenty two.",
    "Temperatures will reach seventy five degrees by Friday, with rain expected in June.",
    "The game ends with a score of thirty one to fourteen, the best result since nineteen ninety eight.",
    "Coming up after the break, our special report from April and a look ahead to next year.",
]


def piper(name):
    d = MODELS / name
    onnx = next(d.glob("*.onnx"))
    return sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=str(onnx), tokens=str(d / "tokens.txt"),
                                                   data_dir=str(d / "espeak-ng-data")),
        num_threads=4)))


def kokoro(name):
    d = MODELS / name
    return sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(d / "model.onnx"), voices=str(d / "voices.bin"),
                                                       tokens=str(d / "tokens.txt"),
                                                       data_dir=str(d / "espeak-ng-data")),
        num_threads=4)))


def say(tts, text, sid, speed):
    a = tts.generate(text, sid=sid, speed=speed)
    x = np.asarray(a.samples, dtype=np.float32)
    if a.sample_rate != SR:
        x = ffmpeg(x, a.sample_rate, f"aresample={SR}")
    return x


def ffmpeg(x, sr, af):
    p = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "pipe:0",
         "-af", af, "-f", "f32le", "-ar", str(SR), "-ac", "1", "pipe:1"],
        input=x.tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32)


def pad(x, before=0.6, after=0.6):
    return np.concatenate([np.zeros(int(before * SR), np.float32), x, np.zeros(int(after * SR), np.float32)])


def rms(x):
    return float(np.sqrt(np.mean(x ** 2)) + 1e-9)


def main():
    voices = []  # (voice id, tts, sid)
    libri = piper("vits-piper-en_US-libritts_r-medium")
    for sid in [3, 47, 112, 190, 260, 333, 401, 488, 560, 640, 721, 850]:
        voices.append((f"libritts-{sid}", libri, sid))
    vctk = piper("vits-piper-en_GB-vctk-medium")
    for sid in [2, 20, 40, 60, 80]:
        voices.append((f"vctk-{sid}", vctk, sid))
    kok = kokoro("kokoro-en-v0_19")
    for sid in [0, 3, 5, 6, 8, 10]:
        voices.append((f"kokoro-{sid}", kok, sid))

    # Background TV from voices not used as speakers.
    tv = np.concatenate([say(libri, line, 900 - 7 * i, 1.0) for i, line in enumerate(TV_LINES)])
    rng = np.random.default_rng(0)

    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    items = all_items()
    for vid, tts, sid in voices:
        for it in items:
            clean = pad(say(tts, it["text"], sid, 1.0))
            older = pad(ffmpeg(say(tts, it["text"], sid, 0.8), SR, "vibrato=f=6:d=0.25"))
            phone = ffmpeg(older, SR, "highpass=f=300,lowpass=f=3400")
            start = rng.integers(0, len(tv) - len(phone)) if len(tv) > len(phone) else 0
            bg = np.resize(tv[start:], len(phone))
            bg = bg * (rms(phone) / rms(bg)) * 10 ** (-10 / 20)
            noisy = phone + ffmpeg(bg.astype(np.float32), SR, "highpass=f=300,lowpass=f=3400")[: len(phone)]
            noisy = noisy / max(1.0, float(np.abs(noisy).max()))
            for cond, x in (("clean", clean), ("older", older), ("tv", noisy)):
                path = OUT / cond / vid / f"{it['id']}.wav"
                path.parent.mkdir(parents=True, exist_ok=True)
                sf.write(path, x, SR)
                rows.append({**it, "voice": vid, "condition": cond, "path": str(path.relative_to(OUT)),
                             "seconds": round(len(x) / SR, 2)})
        print(vid, flush=True)
    (OUT / "manifest.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(len(rows), "clips")


if __name__ == "__main__":
    main()
