"""Rule-based checks of what the senior said.

Each orientation check returns True (correct), False (wrong) or None (the
rules can't tell, e.g. an unusual way of naming a place). None answers can
be sent to the Claude judge in `judge.py`; without it they are marked for
human review and never counted as a mistake.
"""

from __future__ import annotations

import re
from datetime import date

MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]
MONTH_ABBR = {m[:3]: i for i, m in enumerate(MONTHS)} | {"sept": 8}
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

_UNITS = {
    "zero": 0, "oh": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,
}
_ORDINALS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
    "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11,
    "twelfth": 12, "thirteenth": 13, "fourteenth": 14, "fifteenth": 15,
    "sixteenth": 16, "seventeenth": 17, "eighteenth": 18, "nineteenth": 19,
    "twentieth": 20, "thirtieth": 30,
}


def tokens(text: str) -> list[str]:
    text = text.lower().replace("-", " ")
    return re.findall(r"[a-z]+|\d+", text)


def _small_number(toks: list[str], i: int) -> tuple[int, int] | None:
    """Parse 0-99 (digits, words or ordinals) at toks[i]. Returns (value, tokens used)."""
    t = toks[i]
    if t.isdigit():
        return int(t), 1
    if t in _ORDINALS:
        return _ORDINALS[t], 1
    if t in _UNITS:
        return _UNITS[t], 1
    if t in _TENS:
        base = _TENS[t]
        if i + 1 < len(toks):
            nxt = toks[i + 1]
            if nxt in _UNITS and 0 < _UNITS[nxt] < 10:
                return base + _UNITS[nxt], 2
            if nxt in _ORDINALS and _ORDINALS[nxt] < 10:
                return base + _ORDINALS[nxt], 2
        return base, 1
    return None


def numbers(text: str, years: bool = True) -> list[int]:
    """All numbers in an answer. With years=True, spoken years like
    "twenty twenty six", "nineteen oh five" and "two thousand and five" are
    read as one number. Commas and full stops separate numbers."""
    out: list[int] = []
    for chunk in re.split(r"[,.;!?/]", text):
        out.extend(_chunk_numbers(chunk, years))
    return out


def _chunk_numbers(text: str, years: bool) -> list[int]:
    toks = [t for t in tokens(text) if t not in ("and", "a")]
    out: list[int] = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t.isdigit():
            out.append(int(t))
            i += 1
            continue
        if t == "thousand" and out:
            out[-1] *= 1000
            i += 1
            if i < len(toks):
                more = _small_number(toks, i)
                if more and toks[i] not in ("thousand", "hundred"):
                    out[-1] += more[0]
                    i += more[1]
            continue
        if t == "hundred" and out:
            out[-1] *= 100
            i += 1
            continue
        parsed = _small_number(toks, i)
        if not parsed:
            i += 1
            continue
        value, used = parsed
        j = i + used
        # "nineteen fifty two" / "twenty twenty six": a century, then the rest.
        if years and value in (19, 20) and t not in _ORDINALS and j < len(toks):
            nxt = _small_number(toks, j)
            if nxt and toks[j] not in ("thousand", "hundred") and (
                nxt[0] >= 10 or toks[j] in ("oh", "zero")
            ):
                second, used2 = nxt
                if toks[j] in ("oh", "zero") and j + 1 < len(toks):
                    unit = _small_number(toks, j + 1)
                    if unit and unit[0] < 10:
                        second, used2 = unit[0], 2
                out.append(value * 100 + second)
                i = j + used2
                continue
        out.append(value)
        i = j
    return out


def months_in(text: str) -> list[int]:
    found = []
    for t in tokens(text):
        if t in MONTHS:
            found.append(MONTHS.index(t))
        elif t in MONTH_ABBR:
            found.append(MONTH_ABBR[t])
    return found


def days_in(text: str) -> list[int]:
    return [DAYS.index(t) for t in tokens(text) if t in DAYS]


def age_on(birth: date, today: date) -> int:
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def check_year(answer: str, today: date) -> bool | None:
    nums = [n for n in numbers(answer) if n >= 1900]
    if not nums:
        return False
    return today.year in nums


def check_age(answer: str, birth: date, today: date) -> bool | None:
    nums = [n for n in numbers(answer) if 40 <= n <= 120]
    if not nums:
        return False
    # The AMT4 wants the exact age; we allow the one-year slip around a
    # birthday that a well person often makes.
    actual = age_on(birth, today)
    return any(abs(n - actual) <= 1 for n in nums) if len(nums) == 1 else actual in nums


def check_dob(answer: str, birth: date) -> bool | None:
    if not answer.strip():
        return False
    months = months_in(answer)
    nums = numbers(answer)
    years = [n for n in nums if 1900 <= n <= 2020]
    days = [n for n in nums if 1 <= n <= 31]
    if not months:
        # Numeric dates like 3/14/1945 are read as month/day/year.
        if len(nums) >= 3 and 1 <= nums[0] <= 12:
            return nums[0] == birth.month and nums[1] == birth.day and birth.year in years
        return None
    month_ok = birth.month - 1 in months
    day_ok = birth.day in days
    year_ok = birth.year in years if years else None
    if month_ok and day_ok and year_ok:
        return True
    if not month_ok or (days and not day_ok) or year_ok is False:
        return False
    return None


def check_place(answer: str, place_keywords: list[str]) -> bool | None:
    words = set(tokens(answer))
    if not words:
        return False
    for kw in place_keywords:
        kw_toks = tokens(kw)
        if kw_toks and all(t in words for t in kw_toks):
            return True
    if {"home", "house", "apartment", "flat"} & words and any(
        tokens(k) and tokens(k)[0] in ("home", "house") for k in place_keywords
    ):
        return True
    if {"know", "sure"} & words and ("don" in words or "not" in words or "dont" in words):
        return False
    return None


def _sequence_score(said: list[int], expected: list[int]) -> int:
    """How many items were said in the right backwards order. Walks the
    expected list; an item said out of turn is skipped and not counted."""
    correct = 0
    pos = 0
    for item in said:
        if pos >= len(expected):
            break
        if item == expected[pos]:
            correct += 1
            pos += 1
        elif item in expected[pos + 1:]:
            pos = expected.index(item, pos) + 1
    return correct


def score_attention(kind: str, answer: str) -> dict:
    """4AT attention scoring: 0 if enough items right, 1 if they start but
    fall short, 2 if they can't start. The 4AT's own task is months
    backwards (7 of 12 needed). The day and countdown tasks are adaptations
    using the same 7/12 share."""
    if kind == "months_backwards":
        said, expected, needed = months_in(answer), list(range(11, -1, -1)), 7
    elif kind == "days_backwards":
        said, expected, needed = days_in(answer), [6, 5, 4, 3, 2, 1, 0], 5
    elif kind == "countdown_20":
        said = [n for n in numbers(answer, years=False) if 1 <= n <= 20]
        expected, needed = list(range(20, 0, -1)), 12
    else:
        raise ValueError(f"unknown attention task {kind}")
    correct = _sequence_score(said, expected)
    if correct >= needed:
        score = 0
    elif said:
        score = 1
    else:
        score = 2
    return {"correct_items": correct, "needed": needed, "out_of": len(expected), "score": score}
