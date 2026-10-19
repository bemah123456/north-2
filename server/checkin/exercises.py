"""The daily check-in: which exercises to ask, in what order and wording.

The check-in follows the 4AT's four parts. Parts 1 to 3 are asked of the
senior; part 4 (acute change) comes from the voice baseline and the family.
Wording, question order and the attention task rotate by date so the
senior can't learn the answers by rote.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict
from datetime import date


@dataclass(frozen=True)
class Exercise:
    id: str  # stable within one check-in, e.g. "greeting", "year"
    part: str  # "alertness" | "orientation" | "attention"
    kind: str  # what the scorer checks
    prompt: str  # what the app says out loud and shows as a caption
    listen_seconds: int  # how long the app records before moving on

    def to_dict(self) -> dict:
        return asdict(self)


GREETINGS = [
    "Good morning! Tell me how you slept and what you have planned today.",
    "Hello! How are you feeling today, and what did you have for breakfast?",
    "Hi there! Tell me a little about how your day is going so far.",
    "Good day! What's the weather like where you are, and how are you feeling?",
]

# The four AMT4 items the 4AT uses, each with a few wordings.
ORIENTATION = {
    "age": ["How old are you?", "Can you tell me your age?"],
    "dob": ["What is your date of birth?", "When is your birthday, including the year?"],
    "place": ["Where are you right now?", "What place are you in at the moment?"],
    "year": ["What year is it?", "Can you tell me what year it is now?"],
}

ATTENTION = [
    (
        "months_backwards",
        "Please say the months of the year backwards, starting with December.",
        45,
    ),
    (
        "days_backwards",
        "Please say the days of the week backwards, starting with Sunday.",
        30,
    ),
    ("countdown_20", "Please count backwards from twenty down to one.", 45),
]


def _seed(person_id: str, day: date) -> int:
    digest = hashlib.sha256(f"{person_id}:{day.isoformat()}".encode()).hexdigest()
    return int(digest[:12], 16)


def build_checkin(person_id: str, day: date) -> list[Exercise]:
    """Return today's exercises for one person. Same inputs, same plan."""
    seed = _seed(person_id, day)
    exercises = [
        Exercise("greeting", "alertness", "free_speech", GREETINGS[seed % len(GREETINGS)], 30)
    ]

    # All four AMT4 items every day, in a rotating order and wording.
    kinds = list(ORIENTATION)
    order_seed = seed // 7
    for i in range(len(kinds) - 1, 0, -1):
        j = order_seed % (i + 1)
        order_seed //= i + 1
        kinds[i], kinds[j] = kinds[j], kinds[i]
    for k in kinds:
        wordings = ORIENTATION[k]
        exercises.append(
            Exercise(k, "orientation", k, wordings[(seed >> 3) % len(wordings)], 15)
        )

    # The 4AT's own task (months backwards) every other day; the two
    # adaptations share the remaining days.
    if day.toordinal() % 2 == 0:
        kind, prompt, secs = ATTENTION[0]
    else:
        kind, prompt, secs = ATTENTION[1 + (day.toordinal() // 2) % 2]
    exercises.append(Exercise("attention", "attention", kind, prompt, secs))
    return exercises
