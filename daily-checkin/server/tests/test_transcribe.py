import shutil
import subprocess

import numpy as np
import pytest

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
    monkeypatch.setattr(transcribe, "_decode_16k", lambda audio: np.zeros(16000, dtype=np.float32))
    text, words = transcribe.transcribe(b"audio", "audio/m4a")
    assert text == "I'm at home."
    assert [w.text for w in words] == ["I'm", "at", "home."]
    assert words[0].start == 1.2 and words[2].end == 1.7
    assert calls["kwargs"]["return_timestamps"] == "word"


def test_no_provider(monkeypatch):
    monkeypatch.delenv("STT_PROVIDER", raising=False)
    assert transcribe.provider() is None


def _make_clip(tmp_path, source: str, codec_args: list[str], name: str) -> bytes:
    out = tmp_path / name
    subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", source, "-ar", "16000",
                    *codec_args, str(out)], check=True)
    return out.read_bytes()


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")
def test_decodes_m4a_with_index_at_end(tmp_path):
    # Android and iOS recorders write the m4a index after the audio, which
    # ffmpeg can't read from a pipe.
    m4a = _make_clip(tmp_path, "sine=frequency=440:duration=1", ["-c:a", "aac"], "a.m4a")
    assert abs(len(transcribe._decode_16k(m4a)) - 16000) < 2000


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")
def test_has_speech(tmp_path):
    silence = _make_clip(tmp_path, "anullsrc=r=16000:cl=mono:d=2", [], "quiet.wav")
    tone = _make_clip(tmp_path, "sine=frequency=300:duration=0.5,apad=pad_dur=1.5", [], "tone.wav")
    assert transcribe.has_speech(silence) is False
    assert transcribe.has_speech(tone) is True


def test_parakeet_tokens_join_into_words():
    words = transcribe._words_from_tokens([" I", "'m", " at", " ho", "me", "."],
                                          [0.5, 0.6, 0.9, 1.1, 1.2, 1.3], [0.1, 0.1, 0.1, 0.1, 0.1, 0.05])
    assert [w.text for w in words] == ["I'm", "at", "home."]
    assert words[2].start == 1.1 and words[2].end == pytest.approx(1.35)


def _wav(x: np.ndarray) -> bytes:
    import io
    import wave

    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    return buf.getvalue()


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")
@pytest.mark.parametrize("background, level_db, noisy",
                         [(None, None, False), ("tv", -20, True), ("tv", -10, True), ("fan", -10, False)])
def test_clip_check_spots_a_tv_but_not_a_fan(background, level_db, noisy):
    # Syllable-like bursts with gaps, plus a second talker (bursty, like a
    # TV) or steady fan-like noise at level_db below the speaker.
    rng = np.random.default_rng(0)
    t = np.arange(16000 * 4) / 16000
    on = (np.sin(2 * np.pi * 3 * t) > 0.2) & (t % 1.2 < 0.8)
    x = 0.3 * on * np.sin(2 * np.pi * 180 * t)
    if background == "tv":
        syllables = np.repeat(rng.random(19) > 0.35, 16000 // 4.5 + 1)[: len(t)]
        bg = syllables * np.sin(2 * np.pi * 230 * t) * (0.5 + 0.5 * rng.random(len(t)))
    elif background == "fan":
        bg = rng.normal(size=len(t))
    if background:
        x = x + bg / bg.std() * x[on].std() * 10 ** (level_db / 20)
    check = transcribe.clip_check(_wav(x + rng.normal(size=len(t)) * 1e-4))
    assert check == {"heard_speech": True, "noisy": noisy}
