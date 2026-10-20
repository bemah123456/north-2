"""Transcribe the test clips with a Hugging Face Whisper folder, the same
way the app does (transformers pipeline, word timestamps).

Usage: run_hf.py MODEL_DIR AUDIO_DIR NAME OUT_JSONL
VOICES=... limits it to some voices, like run_asr.py.
"""

import json
import os
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from transformers import pipeline

MODEL, AUDIO, NAME, OUT = sys.argv[1], Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
VOICES = set(filter(None, os.environ.get("VOICES", "").split(",")))
torch.set_num_threads(int(os.environ.get("THREADS", "4")))


def main():
    asr = pipeline("automatic-speech-recognition", model=MODEL, device="cpu")
    rows = [json.loads(l) for l in (AUDIO / "manifest.jsonl").read_text().splitlines()]
    done = {json.loads(l)["path"] for l in OUT.read_text().splitlines()} if OUT.exists() else set()
    todo = [r for r in rows if r["path"] not in done and (not VOICES or r["voice"] in VOICES)]
    t0, no_words = time.time(), 0
    with OUT.open("a") as f:
        for r in todo:
            x, sr = sf.read(AUDIO / r["path"], dtype="float32")
            out = asr({"raw": x, "sampling_rate": sr}, return_timestamps="word",
                      generate_kwargs={"language": "english", "task": "transcribe"})
            words = [c for c in out.get("chunks", []) if c["text"].strip()]
            no_words += bool(out["text"].strip()) and not words
            f.write(json.dumps({"path": r["path"], "model": NAME, "hyp": out["text"].strip(),
                                "n_words_timed": len(words)}) + "\n")
            f.flush()
    print(f"{NAME}: {len(todo)} clips, {time.time() - t0:.0f}s, {no_words} with text but no word timestamps")


if __name__ == "__main__":
    main()
