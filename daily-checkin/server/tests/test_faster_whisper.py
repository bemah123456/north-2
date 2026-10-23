import sys
import types

import numpy as np

from checkin import transcribe


class FakeWord:
    def __init__(self, word, start, end, probability=0.95):
        self.word, self.start, self.end, self.probability = word, start, end, probability


class FakeModel:
    calls = []
    prob, logprob = 0.95, -0.2

    def __init__(self, name, device, compute_type):
        self.name = name

    def transcribe(self, samples, **kw):
        FakeModel.calls.append(kw)
        seg = types.SimpleNamespace(text=" It's 2026.", avg_logprob=FakeModel.logprob,
                                    words=[FakeWord(" It's", 0.2, 0.5, FakeModel.prob), FakeWord(" 2026.", 0.5, 1.4, FakeModel.prob)])
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


def test_model_doubt_is_reported(monkeypatch):
    monkeypatch.setenv("STT_PROVIDER", "local")
    monkeypatch.setenv("LOCAL_WHISPER_ENGINE", "faster-whisper")
    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=FakeModel))
    monkeypatch.setattr(transcribe, "_faster_model", None)
    monkeypatch.setattr(transcribe, "_decode_16k", lambda audio: np.zeros(16000, dtype=np.float32))
    monkeypatch.setattr(FakeModel, "prob", 0.95)
    sure = transcribe.transcribe_detail(b"clip", "audio/m4a")
    assert sure["unsure"] is False and sure["transcript"] == "It's 2026."
    monkeypatch.setattr(FakeModel, "prob", 0.5)
    assert transcribe.transcribe_detail(b"clip", "audio/m4a")["unsure"] is True
    monkeypatch.setattr(FakeModel, "prob", 0.95)
    monkeypatch.setattr(FakeModel, "logprob", -0.9)
    assert transcribe.transcribe_detail(b"clip", "audio/m4a")["unsure"] is True


def test_other_engines_never_say_unsure(monkeypatch):
    monkeypatch.setenv("STT_PROVIDER", "local")
    monkeypatch.delenv("LOCAL_WHISPER_ENGINE", raising=False)
    monkeypatch.setattr(transcribe, "transcribe", lambda a, c, e=None: ("2026", []))
    assert "unsure" not in transcribe.transcribe_detail(b"clip", "audio/m4a")
