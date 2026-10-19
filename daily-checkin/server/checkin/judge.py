"""Claude as a second opinion on answers the rules can't settle.

Only called for answers `answers.py` marks as unsure (None), such as an
unusual way of naming where someone is. Off unless ANTHROPIC_API_KEY (or
another Anthropic credential) is configured and JUDGE_ENABLED=1.
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


def judge_answer(question: str, answer: str, facts: str) -> dict | None:
    """Returns {"correct": bool, "reason": str}, or None if unavailable."""
    if not enabled():
        return None
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
