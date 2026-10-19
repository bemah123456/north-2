"""Speech-to-text with word timestamps.

Set STT_PROVIDER to one of:
  "local"     free: Whisper running on this server (pip install -r
              requirements-local.txt). LOCAL_WHISPER_MODEL picks the
              weights: a Hugging Face id (default openai/whisper-small) or a
              folder, such as the model fine-tuned on older voices.
  "deepgram"  paid: DEEPGRAM_API_KEY
  "openai"    paid: OPENAI_API_KEY (Whisper API)
Without any of them, the API still accepts answers that arrive already
transcribed (the typed demo mode).
"""

from __future__ import annotations

import os

import httpx

from .features import Word


class TranscriptionUnavailable(RuntimeError):
    pass


def provider() -> str | None:
    p = os.environ.get("STT_PROVIDER")
    if p == "local":
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
    if p == "deepgram":
        return _deepgram(audio, content_type)
    if p == "openai":
        return _whisper(audio, content_type)
    raise TranscriptionUnavailable("No speech-to-text provider configured")


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
            model=os.environ.get("LOCAL_WHISPER_MODEL", "openai/whisper-small"),
            device=os.environ.get("LOCAL_WHISPER_DEVICE", "cpu"),
        )
    return _local_pipeline


def _local_whisper(audio: bytes) -> tuple[str, list[Word]]:
    # Bytes are decoded with ffmpeg, so phone m4a and browser webm both work.
    model = os.environ.get("LOCAL_WHISPER_MODEL", "openai/whisper-small")
    # English-only checkpoints (".en") reject a language setting.
    extra = {} if model.endswith(".en") else {"generate_kwargs": {"language": "english", "task": "transcribe"}}
    out = _load_local()(audio, return_timestamps="word", **extra)
    words = []
    for chunk in out.get("chunks", []):
        start, end = chunk["timestamp"]
        text = chunk["text"].strip()
        if text and start is not None:
            words.append(Word(text, float(start), float(end if end is not None else start)))
    return out.get("text", "").strip(), words
