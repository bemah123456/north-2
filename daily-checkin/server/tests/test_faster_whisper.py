import sys
import types

import numpy as np

from checkin import transcribe


class FakeWord:
    def __init__(self, word, start, end):
        self.word, self.start, self.end = word, start, end


class FakeModel:
    calls = []

    def __init__(self, name, device, compute_type):
        self.name = name

    def transcribe(self, samples, **kw):
        FakeModel.calls.append(kw)
        seg = types.SimpleNamespace(text=" It's 2026.", words=[FakeWord(" It's", 0.2, 0.5), FakeWord(" 2026.", 0.5, 1.4)])
        return iter([seg]), None


def test_faster_whisper_engine(monkeypatch):
    monkeypatch.setenv("STT_PROVIDER", "local")
    monkeypatch.setenv("LOCAL_WHISPER_ENGINE", "faster-whisper")
    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=FakeModel))
    monkeypatch.setattr(transcribe, "_faster_model", None)
    monkeypatch.setattr(transcribe, "_decode_16k", lambda audio: np.zeros(16000, dtype=np.float32))

    text, words = transcribe.transcribe(b"clip", "audio/m4a", transcribe.MONTHS_BACKWARDS)
    assert text == "It's 2026."
    assert [(w.text, w.start, w.end) for w in words] == [("It's", 0.2, 0.5), ("2026.", 0.5, 1.4)]
    assert FakeModel.calls[-1]["initial_prompt"] == transcribe.MONTHS_BACKWARDS  # months list still primes it
    assert FakeModel.calls[-1]["language"] == "en" and FakeModel.calls[-1]["word_timestamps"]


def test_faster_whisper_skips_tiny_clips(monkeypatch):
    monkeypatch.setenv("STT_PROVIDER", "local")
    monkeypatch.setenv("LOCAL_WHISPER_ENGINE", "faster-whisper")
    monkeypatch.setattr(transcribe, "_decode_16k", lambda audio: np.zeros(100, dtype=np.float32))
    assert transcribe.transcribe(b"x", "audio/m4a") == ("", [])
