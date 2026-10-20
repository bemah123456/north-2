"""How the senior spoke, measured from word timestamps.

Every clip starts recording the moment the app finishes speaking the
prompt, so a word's start time is also the delay since the question.
"""

from __future__ import annotations

from dataclasses import dataclass

FILLERS = {"um", "uh", "er", "erm", "hmm", "uhm", "ah", "mm"}
PAUSE_SECONDS = 0.5

# Features the baseline and model use, and the direction that means
# "worse than usual" (+1: higher is worse, -1: lower is worse).
FEATURE_DIRECTIONS = {
    "latency_s": +1,
    "words_per_min": -1,
    "pauses_per_min": +1,
    "mean_pause_s": +1,
    "filler_rate": +1,
    "repeat_rate": +1,
    "greeting_words": -1,
}


@dataclass
class Word:
    text: str
    start: float
    end: float


def clip_features(words: list[Word]) -> dict | None:
    """Features of one answer. None if nothing was said."""
    if not words:
        return None
    texts = [w.text.lower().strip(".,!?") for w in words]
    speaking = max(words[-1].end - words[0].start, 0.5)
    gaps = [b.start - a.end for a, b in zip(words, words[1:])]
    pauses = [g for g in gaps if g >= PAUSE_SECONDS]
    content = [t for t in texts if t not in FILLERS]
    repeats = sum(1 for a, b in zip(texts, texts[1:]) if a == b and a not in FILLERS)
    return {
        "latency_s": max(words[0].start, 0.0),
        "speaking_s": speaking,
        "n_words": len(content),
        "n_fillers": len(texts) - len(content),
        "n_pauses": len(pauses),
        "pause_total_s": sum(pauses),
        "n_repeats": repeats,
    }


def checkin_features(clips: dict[str, list[Word]]) -> dict | None:
    """Combine every answered clip of one check-in into the model features."""
    per = {k: clip_features(v) for k, v in clips.items()}
    answered = {k: f for k, f in per.items() if f}
    if not answered:
        return None
    speaking = sum(f["speaking_s"] for f in answered.values())
    words = sum(f["n_words"] for f in answered.values())
    all_tokens = words + sum(f["n_fillers"] for f in answered.values())
    pauses = sum(f["n_pauses"] for f in answered.values())
    pause_total = sum(f["pause_total_s"] for f in answered.values())
    latencies = sorted(f["latency_s"] for f in answered.values())
    greeting = answered.get("greeting")
    return {
        # Median, so one slow answer doesn't swamp the day.
        "latency_s": latencies[len(latencies) // 2],
        "words_per_min": 60.0 * words / speaking,
        "pauses_per_min": 60.0 * pauses / speaking,
        "mean_pause_s": pause_total / pauses if pauses else 0.0,
        "filler_rate": (all_tokens - words) / all_tokens if all_tokens else 0.0,
        "repeat_rate": sum(f["n_repeats"] for f in answered.values()) / max(words, 1),
        "greeting_words": float(greeting["n_words"]) if greeting else 0.0,
        "answered_clips": len(answered),
        "total_clips": len(clips),
    }
