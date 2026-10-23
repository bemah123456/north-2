"""A second opinion on answers the rules can't settle.

Only called for answers `answers.py` marks as unsure (None), such as an
unusual way of naming where someone is. Off unless JUDGE_ENABLED=1.

JUDGE_ENGINE picks who judges:
  "claude" (default)  Claude reads the transcript (needs ANTHROPIC_API_KEY or
                      another Anthropic credential).
  "gemini"            Gemini listens to the recorded answer itself, so a
                      misheard transcript can't mislead it (needs a Gemini
                      backend, see gemini.py). Typed answers have no audio
                      and are judged from their text.
Either way, a failed call leaves the answer for a person to check.
"""

from __future__ import annotations

import json
import os

MODEL = os.environ.get("JUDGE_MODEL", "claude-opus-5-5")

SYSTEM = (
    "You check answers in a memory and orientation screening test for older "
    "adults. Judge only whether the spoken answer is correct given the facts. "
    "Transcripts come from speech-to-text, so allow for misheard words, "
    "filler words and natural phrasing. If the person says they don't know, "
    "the answer is not correct."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "correct": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["correct", "reason"],
    "additionalProperties": False,
}


def enabled() -> bool:
    return os.environ.get("JUDGE_ENABLED") == "1"


def engine() -> str:
    return "gemini" if os.environ.get("JUDGE_ENGINE") == "gemini" else "claude"


def judge_answer(question: str, answer: str, facts: str, audio: bytes | None = None) -> dict | None:
    """Returns {"correct": bool, "reason": str, "by": "claude" | "gemini"},
    or None if unavailable. audio: the recorded answer, for Gemini."""
    if not enabled():
        return None
    if engine() == "gemini":
        verdict = _gemini(question, answer, facts, audio)
    else:
        verdict = _claude(question, answer, facts)
    return verdict | {"by": engine()} if verdict else None


GEMINI_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "heard": {"type": "STRING"},
        "correct": {"type": "BOOLEAN"},
        "reason": {"type": "STRING"},
    },
    "required": ["heard", "correct", "reason"],
}


def _gemini(question: str, answer: str, facts: str, audio: bytes | None) -> dict | None:
    from . import gemini
    from .transcribe import TranscriptionUnavailable, _decode_16k

    if not gemini.configured():
        return None
    parts = []
    if audio:
        try:
            parts.append(gemini.audio_part(gemini.wav_16k(_decode_16k(audio))))
        except (TranscriptionUnavailable, FileNotFoundError):
            pass
    if parts:
        # The recording, not the transcript: the transcript is what the rules
        # already couldn't settle, and may be the misheard part.
        ask = (f"Facts: {facts}\nQuestion: {question}\nThe recording is the person's spoken answer. "
               "In \"heard\", write what the main speaker says (ignore background voices and TV).")
    else:
        ask = f"Facts: {facts}\nQuestion: {question}\nSpoken answer: {answer!r}\nCopy the answer into \"heard\"."
    parts.append({"text": SYSTEM + "\n\n" + ask})
    try:
        out = gemini.generate(parts, GEMINI_SCHEMA)
    except gemini.GeminiUnavailable:
        return None
    if not isinstance(out.get("correct"), bool):
        return None
    return {"correct": out["correct"], "reason": str(out.get("reason", ""))[:300],
            "heard": str(out.get("heard", ""))[:300]}


def _claude(question: str, answer: str, facts: str) -> dict | None:
    import anthropic

    client = anthropic.Anthropic()
    try:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=2000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
            system=SYSTEM,
            messages=[{
                "role": "user",
                "content": f"Facts: {facts}\nQuestion: {question}\nSpoken answer: {answer!r}",
            }],
        )
    except (anthropic.APIConnectionError, anthropic.APIStatusError):
        # The rules already marked this answer for human review; a failed
        # second opinion leaves it that way.
        return None
    if response.stop_reason in ("refusal", "max_tokens"):
        return None
    text = next((b.text for b in response.content if b.type == "text"), None)
    return json.loads(text) if text else None
