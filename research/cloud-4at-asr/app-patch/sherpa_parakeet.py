"""Proposed extra speech-to-text option for checkin/transcribe.py:
STT_PROVIDER=parakeet runs NVIDIA Parakeet TDT 0.6B v2 (int8 ONNX) on the
server's CPU with sherpa-onnx, free, with word timestamps.

Setup:
  pip install sherpa-onnx
  download and unpack
  https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.tar.bz2
  and set PARAKEET_DIR to that folder.

To wire it in, add to transcribe.provider():   if p == "parakeet": return p
and to transcribe.transcribe():                if p == "parakeet": return parakeet(audio)
"""

from __future__ import annotations

import os
import subprocess
import tempfile

import numpy as np

try:  # inside the app
    from .features import Word
except ImportError:  # run on its own
    from dataclasses import dataclass

    @dataclass
    class Word:
        text: str
        start: float
        end: float

SR = 16000
_recognizer = None


def _load():
    global _recognizer
    if _recognizer is None:
        import sherpa_onnx

        d = os.environ["PARAKEET_DIR"]
        _recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=os.path.join(d, "encoder.int8.onnx"),
            decoder=os.path.join(d, "decoder.int8.onnx"),
            joiner=os.path.join(d, "joiner.int8.onnx"),
            tokens=os.path.join(d, "tokens.txt"),
            model_type="nemo_transducer",
            num_threads=int(os.environ.get("PARAKEET_THREADS", "4")),
        )
    return _recognizer


def decode_audio(audio: bytes) -> np.ndarray:
    """Any format ffmpeg reads (phone m4a, browser webm, wav) to 16 kHz mono.
    Goes through a temporary file because an m4a with its index at the end
    can't be read from a pipe (ffmpeg returns no audio and no error)."""
    with tempfile.NamedTemporaryFile(suffix=".audio") as f:
        f.write(audio)
        f.flush()
        p = subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-i", f.name, "-f", "f32le", "-ac", "1", "-ar", str(SR), "pipe:1"],
            capture_output=True, check=True,
        )
    return np.frombuffer(p.stdout, dtype=np.float32)


def words_from_tokens(tokens: list[str], starts: list[float], durations: list[float]) -> list[Word]:
    """Join sub-word tokens into words. A token starting with a space
    begins a new word; punctuation stays attached to the word before it."""
    words: list[Word] = []
    for tok, start, dur in zip(tokens, starts, durations):
        end = start + max(dur, 0.0)
        if tok.startswith(" ") or not words:
            text = tok.strip()
            if text:
                words.append(Word(text, float(start), float(end)))
        else:
            words[-1].text += tok
            words[-1].end = float(max(words[-1].end, end))
    return words


def parakeet(audio: bytes) -> tuple[str, list[Word]]:
    x = decode_audio(audio)
    if len(x) < SR // 10:
        return "", []
    rec = _load()
    s = rec.create_stream()
    s.accept_waveform(SR, x)
    rec.decode_stream(s)
    r = s.result
    durations = list(getattr(r, "durations", []) or [0.0] * len(r.tokens))
    return r.text.strip(), words_from_tokens(list(r.tokens), list(r.timestamps), durations)
