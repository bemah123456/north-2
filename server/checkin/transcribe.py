"""Speech-to-text with word timestamps.

Set STT_PROVIDER to "deepgram" (DEEPGRAM_API_KEY) or "openai"
(OPENAI_API_KEY, Whisper). Day 3 of the plan is to try both on older
voices and keep the better one. Without either, the API still accepts
answers that arrive already transcribed (the typed demo mode).
"""

from __future__ import annotations

import os

import httpx

from .features import Word


class TranscriptionUnavailable(RuntimeError):
    pass


def provider() -> str | None:
    p = os.environ.get("STT_PROVIDER")
    if p == "deepgram" and os.environ.get("DEEPGRAM_API_KEY"):
        return p
    if p == "openai" and os.environ.get("OPENAI_API_KEY"):
        return p
    return None


def transcribe(audio: bytes, content_type: str) -> tuple[str, list[Word]]:
    p = provider()
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
