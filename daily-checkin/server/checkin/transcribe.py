"""Speech-to-text with word timestamps.

Set STT_PROVIDER to one of:
  "local"     free: Whisper running on this server (pip install -r
              requirements-local.txt). LOCAL_WHISPER_MODEL picks the
              weights: a Hugging Face id (default openai/whisper-small;
              small.en is more accurate in a quiet room but much worse with
              a TV on) or a folder, such as the model fine-tuned on older
              voices.
  "parakeet"  free: NVIDIA Parakeet TDT 0.6B v2 on the CPU (pip install
              sherpa-onnx; unpack sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8
              from the sherpa-onnx releases and set PARAKEET_DIR to it)
  "deepgram"  paid: DEEPGRAM_API_KEY
  "openai"    paid: OPENAI_API_KEY (Whisper API)
Without any of them, the API still accepts answers that arrive already
transcribed (the typed demo mode).
"""

from __future__ import annotations

import os
import subprocess
import tempfile

import httpx

from .features import Word


class TranscriptionUnavailable(RuntimeError):
    pass


def provider() -> str | None:
    p = os.environ.get("STT_PROVIDER")
    if p in ("local", "parakeet"):
        return p
    if p == "deepgram" and os.environ.get("DEEPGRAM_API_KEY"):
        return p
    if p == "openai" and os.environ.get("OPENAI_API_KEY"):
        return p
    return None


def transcribe(audio: bytes, content_type: str) -> tuple[str, list[Word]]:
    p = provider()
    if p == "local":
        return _local_whisper(audio)
    if p == "parakeet":
        return _parakeet(audio)
    if p == "deepgram":
        return _deepgram(audio, content_type)
    if p == "openai":
        return _whisper(audio, content_type)
    raise TranscriptionUnavailable("No speech-to-text provider configured")


SR = 16000


def _decode_16k(audio: bytes):
    """Any format ffmpeg reads (phone m4a, browser webm, wav) to 16 kHz mono.
    Goes through a temporary file: Android, and often iOS, write the m4a
    index after the audio, which ffmpeg can't read from a pipe."""
    import numpy as np

    with tempfile.NamedTemporaryFile(suffix=".audio") as f:
        f.write(audio)
        f.flush()
        p = subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-i", f.name, "-f", "f32le", "-ac", "1", "-ar", str(SR), "pipe:1"],
            capture_output=True,
        )
    if p.returncode != 0:
        raise TranscriptionUnavailable("Could not decode the recording: " + p.stderr.decode(errors="replace")[-200:])
    return np.frombuffer(p.stdout, dtype=np.float32)


def has_speech(audio: bytes) -> bool | None:
    """Whether a clip has speech in it. None when it can't be decoded here."""
    check = clip_check(audio)
    return check["heard_speech"] if check else None


def clip_check(audio: bytes) -> dict | None:
    """noisy: the quiet stretches between words sit within about 26 dB of
    the loudest speech, as with a TV on in the room, where every speech
    model we tested mishears healthy answers far more often.
    heard_speech: some 30 ms frame stands well above the quietest ones (by
    a smaller margin when the room is noisy). None when the clip can't be
    decoded here."""
    import numpy as np

    try:
        x = _decode_16k(audio)
    except (TranscriptionUnavailable, FileNotFoundError):
        return None
    frame = int(0.03 * SR)
    n = len(x) // frame
    if n < 3:
        return {"heard_speech": False, "noisy": False}
    e = np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1)) + 1e-6
    quiet = np.percentile(e, 20)
    noisy = bool(quiet > 0.003 and np.percentile(e, 95) / quiet < 20)
    heard = bool(e.max() > 0.01 and e.max() / np.percentile(e, 10) > (3 if noisy else 10))
    return {"heard_speech": heard, "noisy": noisy}


def _deepgram(audio: bytes, content_type: str) -> tuple[str, list[Word]]:
    r = httpx.post(
        "https://api.deepgram.com/v1/listen",
        params={"model": "nova-3", "filler_words": "true", "smart_format": "false"},
        headers={
            "Authorization": f"Token {os.environ['DEEPGRAM_API_KEY']}",
            "Content-Type": content_type or "audio/m4a",
        },
        content=audio,
        timeout=60,
    )
    r.raise_for_status()
    alt = r.json()["results"]["channels"][0]["alternatives"][0]
    words = [Word(w["word"], float(w["start"]), float(w["end"])) for w in alt.get("words", [])]
    return alt.get("transcript", ""), words


def _whisper(audio: bytes, content_type: str) -> tuple[str, list[Word]]:
    ext = {"audio/webm": "webm", "audio/wav": "wav", "audio/mpeg": "mp3"}.get(content_type, "m4a")
    r = httpx.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        data={
            "model": "whisper-1",
            "response_format": "verbose_json",
            "timestamp_granularities[]": "word",
            # Whisper drops "um" and "uh" unless the prompt shows them.
            "prompt": "Umm, let me think, uh, hmm.",
        },
        files={"file": (f"answer.{ext}", audio, content_type or "audio/m4a")},
        timeout=60,
    )
    r.raise_for_status()
    body = r.json()
    words = [Word(w["word"], float(w["start"]), float(w["end"])) for w in body.get("words", [])]
    return body.get("text", ""), words


DEFAULT_LOCAL_MODEL = "openai/whisper-small"
_local_pipeline = None


def _load_local():
    global _local_pipeline
    if _local_pipeline is None:
        try:
            from transformers import pipeline
        except ImportError as e:
            raise TranscriptionUnavailable("Install requirements-local.txt to use local Whisper") from e
        _local_pipeline = pipeline(
            "automatic-speech-recognition",
            model=os.environ.get("LOCAL_WHISPER_MODEL", DEFAULT_LOCAL_MODEL),
            device=os.environ.get("LOCAL_WHISPER_DEVICE", "cpu"),
        )
    return _local_pipeline


def _local_whisper(audio: bytes) -> tuple[str, list[Word]]:
    model = os.environ.get("LOCAL_WHISPER_MODEL", DEFAULT_LOCAL_MODEL)
    # English-only checkpoints (".en") reject a language setting.
    extra = {} if model.endswith(".en") else {"generate_kwargs": {"language": "english", "task": "transcribe"}}
    samples = _decode_16k(audio)
    if len(samples) < SR // 10:  # under 0.1 s: nothing to transcribe
        return "", []
    out = _load_local()({"raw": samples, "sampling_rate": SR}, return_timestamps="word", **extra)
    words = []
    for chunk in out.get("chunks", []):
        start, end = chunk["timestamp"]
        text = chunk["text"].strip()
        if text and start is not None:
            words.append(Word(text, float(start), float(end if end is not None else start)))
    return out.get("text", "").strip(), words


_parakeet_recognizer = None


def _parakeet(audio: bytes) -> tuple[str, list[Word]]:
    global _parakeet_recognizer
    x = _decode_16k(audio)
    if len(x) < SR // 10:
        return "", []
    if _parakeet_recognizer is None:
        try:
            import sherpa_onnx
        except ImportError as e:
            raise TranscriptionUnavailable("pip install sherpa-onnx to use Parakeet") from e
        d = os.environ.get("PARAKEET_DIR")
        if not d:
            raise TranscriptionUnavailable("Set PARAKEET_DIR to the unpacked Parakeet model")
        _parakeet_recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=os.path.join(d, "encoder.int8.onnx"),
            decoder=os.path.join(d, "decoder.int8.onnx"),
            joiner=os.path.join(d, "joiner.int8.onnx"),
            tokens=os.path.join(d, "tokens.txt"),
            model_type="nemo_transducer",
            num_threads=int(os.environ.get("PARAKEET_THREADS", "4")),
        )
    s = _parakeet_recognizer.create_stream()
    s.accept_waveform(SR, x)
    _parakeet_recognizer.decode_stream(s)
    r = s.result
    durations = list(getattr(r, "durations", []) or [0.0] * len(r.tokens))
    return r.text.strip(), _words_from_tokens(list(r.tokens), list(r.timestamps), durations)


def _words_from_tokens(tokens: list[str], starts: list[float], durations: list[float]) -> list[Word]:
    """Join sub-word tokens into words. A token starting with a space
    begins a new word; punctuation stays with the word before it."""
    words: list[Word] = []
    for tok, start, dur in zip(tokens, starts, durations):
        end = float(start) + max(float(dur), 0.0)
        if tok.startswith(" ") or not words:
            if tok.strip():
                words.append(Word(tok.strip(), float(start), end))
        else:
            last = words[-1]
            words[-1] = Word(last.text + tok, last.start, max(last.end, end))
    return words
