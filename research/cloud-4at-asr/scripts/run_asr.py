"""Transcribe every test clip with one speech model.

Usage: run_asr.py MODELS_DIR AUDIO_DIR MODEL_NAME OUT_JSONL
"""

import json
import os
import sys
import time
from pathlib import Path

import soundfile as sf
import sherpa_onnx

MODELS, AUDIO, NAME, OUT = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
THREADS = int(os.environ.get("THREADS", "4"))
INT8 = os.environ.get("INT8") == "1"
# Optional subset of voices, comma separated, for the slower models.
VOICES = set(filter(None, os.environ.get("VOICES", "").split(",")))


def one(d, pattern):
    hits = sorted(d.glob(pattern))
    # Full-precision files unless INT8=1 asks for the quantized ones.
    full = [h for h in hits if "int8" not in h.name]
    q = [h for h in hits if "int8" in h.name]
    return str(((q if INT8 else full) or hits)[0])


def recognizer(name):
    d = MODELS / name
    if "whisper" in name:
        kw = {} if name.endswith(".en") else {"language": "en", "task": "transcribe"}
        return sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=one(d, "*encoder*.onnx"), decoder=one(d, "*decoder*.onnx"),
            tokens=one(d, "*tokens.txt"), num_threads=THREADS, **kw)
    if "parakeet" in name:
        return sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=one(d, "encoder*.onnx"), decoder=one(d, "decoder*.onnx"), joiner=one(d, "joiner*.onnx"),
            tokens=one(d, "tokens.txt"), model_type="nemo_transducer", num_threads=THREADS)
    if "moonshine" in name:
        return sherpa_onnx.OfflineRecognizer.from_moonshine(
            preprocessor=one(d, "preprocess*.onnx"), encoder=one(d, "encode*.onnx"),
            uncached_decoder=one(d, "uncached_decode*.onnx"), cached_decoder=one(d, "cached_decode*.onnx"),
            tokens=one(d, "tokens.txt"), num_threads=THREADS)
    raise ValueError(name)


def main():
    rec = recognizer(NAME)
    rows = [json.loads(l) for l in (AUDIO / "manifest.jsonl").read_text().splitlines()]
    done = set()
    if OUT.exists():
        done = {json.loads(l)["path"] for l in OUT.read_text().splitlines()}
    t0 = time.time()
    audio_s = 0.0
    with OUT.open("a") as f:
        todo = [r for r in rows if r["path"] not in done and (not VOICES or r["voice"] in VOICES)]
        for i in range(0, len(todo), 16):
            batch = todo[i:i + 16]
            streams = []
            for r in batch:
                x, sr = sf.read(AUDIO / r["path"], dtype="float32")
                s = rec.create_stream()
                s.accept_waveform(sr, x)
                streams.append(s)
                audio_s += len(x) / sr
            # One at a time: batched Whisper decoding in sherpa-onnx can
            # stall for many minutes on a batch that decodes fine clip by clip.
            for s in streams:
                rec.decode_stream(s)
            for r, s in zip(batch, streams):
                f.write(json.dumps({"path": r["path"], "model": NAME + ("-int8" if INT8 else ""), "hyp": s.result.text.strip()}) + "\n")
            f.flush()
    took = time.time() - t0
    print(f"{NAME}: {len(todo)} clips, {took:.0f}s, real-time factor {took / max(audio_s, 1):.3f}")


if __name__ == "__main__":
    main()
