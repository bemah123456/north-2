from checkin import transcribe


def test_local_whisper_word_chunks(monkeypatch):
    calls = {}

    def fake_pipeline(audio, **kwargs):
        calls["kwargs"] = kwargs
        return {"text": " I'm at home.", "chunks": [
            {"text": " I'm", "timestamp": (1.2, 1.4)},
            {"text": " at", "timestamp": (1.5, 1.6)},
            {"text": " home.", "timestamp": (1.7, None)},
        ]}

    monkeypatch.setenv("STT_PROVIDER", "local")
    monkeypatch.setattr(transcribe, "_local_pipeline", fake_pipeline)
    text, words = transcribe.transcribe(b"audio", "audio/m4a")
    assert text == "I'm at home."
    assert [w.text for w in words] == ["I'm", "at", "home."]
    assert words[0].start == 1.2 and words[2].end == 1.7
    assert calls["kwargs"]["return_timestamps"] == "word"


def test_no_provider(monkeypatch):
    monkeypatch.delenv("STT_PROVIDER", raising=False)
    assert transcribe.provider() is None
