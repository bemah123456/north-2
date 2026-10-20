"""Fixes for speech-to-text slips that make a healthy answer look wrong.

Each fix targets a pattern seen in the model comparison, and none of them
turns a wrong answer into a right one in the test set (checked by
analyze.py, which scores impaired answers with and without these fixes).

1. Sound-alike digits after a tens word: "eighty too" -> 82,
   "seventy for" -> 74. Whisper and Parakeet both write these.
2. Years split or glued by punctuation: "20/26", "20-26" -> 2026.
3. A bare two-digit year that matches this year ("twenty six, I think")
   when no full year was said.
4. Countdown numbers glued into a year: "20, 1918, 17" -> 20, 19, 18, 17.
5. An empty transcript while the clip has speech in it means the model
   heard nothing, not that the person was wrong: mark it unsure (ask
   again) instead of a mistake.
6. An age, year or birthday answer with no number (or month) in it, and
   no "don't know", is usually a mishearing ("I made it too" for "I'm
   eighty two"): ask again instead of counting a mistake.
"""

from __future__ import annotations

import re
import sys

import numpy as np

sys.path.insert(0, "/mnt/project-files/daily-checkin/server")
from checkin import answers as A  # noqa: E402

_TENS = r"(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|[2-9]0)"
DONT_KNOW = re.compile(r"\b(don'?t|do not|not sure|no idea|can'?t|cannot|forget|forgot)\b", re.I)
_SOUND_ALIKE = {"to": "two", "too": "two", "for": "four", "won": "one", "ate": "eight", "tree": "three"}


def normalize(text: str) -> str:
    def tens_unit(m):
        unit = _SOUND_ALIKE[m.group(2).lower()]
        if m.group(1).isdigit():  # "80 too" -> "82"
            return str(int(m.group(1)) + A._UNITS[unit])
        return f"{m.group(1)} {unit}"
    text = re.sub(rf"\b{_TENS}[\s,-]+(to|too|for|won|ate|tree)\b", tens_unit, text, flags=re.I)
    text = re.sub(r"\b(19|20)\s*[/-]\s*(\d\d)\b", r"\1\2", text)
    return text


def split_glued(nums: list[int]) -> list[int]:
    """1918 -> 19, 18 when the two halves are a countdown step."""
    out = []
    for n in nums:
        a, b = divmod(n, 100)
        if 1000 <= n <= 2019 and 1 <= b <= 20 and a == b + 1:
            out.extend([a, b])
        else:
            out.append(n)
    return out


def has_speech(x: np.ndarray, sr: int = 16000) -> bool:
    """Any 30 ms frame well above the quietest frames."""
    frame = int(0.03 * sr)
    n = len(x) // frame
    if n < 3:
        return False
    e = np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1)) + 1e-6
    return bool(e.max() > 0.01 and e.max() / np.percentile(e, 10) > 10)


def verdict(kind: str, text: str, birth, today, place_keywords, speech: bool):
    """Like the app's checks, with the fixes above. Returns True, False or
    None for orientation, and the 4AT attention dict for attention tasks."""
    if not text.strip() and speech:
        return None if kind in ("age", "dob", "place", "year") else {"score": None, "correct_items": 0}
    t = normalize(text)
    if kind in ("age", "year", "dob") and speech and not A.numbers(t) and not (kind == "dob" and A.months_in(t)):
        if not DONT_KNOW.search(t):
            return None
    if kind == "age":
        return A.check_age(t, birth, today)
    if kind == "dob":
        return A.check_dob(t, birth)
    if kind == "place":
        return A.check_place(t, place_keywords)
    if kind == "year":
        ok = A.check_year(t, today)
        if ok is False and not [n for n in A.numbers(t) if n >= 1900]:
            two = [n for n in A.numbers(t) if n < 100]
            if two == [today.year % 100]:
                return True
        return ok
    if kind == "countdown_20":
        said = [n for n in split_glued(A.numbers(t, years=False)) if 1 <= n <= 20]
        correct = A._sequence_score(said, list(range(20, 0, -1)))
        score = 0 if correct >= 12 else 1 if said else 2
        return {"correct_items": correct, "needed": 12, "out_of": 20, "score": score}
    return A.score_attention(kind, t)
