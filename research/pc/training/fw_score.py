"""Transcribe the saved test audio with faster-whisper exactly as the server does
(daily-checkin/server/checkin/transcribe.py: int8 weights, beam 5, word timestamps,
temperature fallback left at its defaults), and time it on the CPU.

    python -I fw_score.py <ct2 model folder> <audio folder> <out.json> [cuda|cpu]

The audio folder holds <condition>.npy (all clips joined) and <condition>_offsets.npy, written by
kaggle_round5.py. Run in its own process so CTranslate2 and PyTorch don't share GPU memory.
"""
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel


def clips(folder, cond):
    audio = np.load(folder / f"{cond}.npy")
    off = np.load(folder / f"{cond}_offsets.npy")
    return [audio[off[i]:off[i + 1]] for i in range(len(off) - 1)]


def run(model, audios):
    out = []
    for a in audios:
        segs, _ = model.transcribe(a, language="en", beam_size=5, word_timestamps=True)
        out.append("".join(s.text for s in segs).strip())
    return out


def main():
    ct2, folder, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    device = sys.argv[4] if len(sys.argv) > 4 else "cuda"
    conds = json.loads((folder / "conditions.json").read_text())
    # int8_float32 on the GPU is the CPU's int8 (8-bit weights, 32-bit activations), only faster.
    model = WhisperModel(str(ct2), device=device, compute_type="int8_float32" if device == "cuda" else "int8")
    res = {"hyps": {}, "device": device}
    for cond in conds:
        t = time.time()
        res["hyps"][cond] = run(model, clips(folder, cond))
        print(f"{cond}: {len(res['hyps'][cond])} clips in {time.time() - t:.0f}s", flush=True)
    del model
    # CPU time per answer as the server runs it (2 threads like the test laptop, then 4).
    quiet = clips(folder, conds[0])[:8]
    res["cpu_sec"] = {}
    for threads in (2, 4):
        cpu = WhisperModel(str(ct2), device="cpu", compute_type="int8", cpu_threads=threads)
        run(cpu, quiet[:1])  # warm-up
        times = []
        for a in quiet:
            t = time.time()
            run(cpu, [a])
            times.append(time.time() - t)
        res["cpu_sec"][threads] = statistics.median(times)
        print(f"CPU, {threads} threads: {res['cpu_sec'][threads]:.2f} s per clip", flush=True)
        del cpu
    out.write_text(json.dumps(res))


if __name__ == "__main__":
    main()
