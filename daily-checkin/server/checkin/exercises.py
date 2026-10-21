"""The daily check-in: which exercises to ask, in what order and wording.

The check-in follows the 4AT's four parts. Parts 1 to 3 are asked of the
senior; part 4 (acute change) comes from the family, an evening check-in
that's worse than the morning, and the combined change score. Wording,
question order and the attention task rotate by date so the senior can't
learn the answers by rote.

Every check-in ends with a short digit span (four numbers, said back
backwards): inattention is the core sign of delirium, and a task that is
the same kind every day gives a clean personal baseline. The optional
evening check-in is a shorter version, scored against the same morning.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, asdict
from datetime import date


@dataclass(frozen=True)
class Exercise:
    id: str  # stable within one check-in, e.g. "greeting", "year"
    part: str  # "alertness" | "orientation" | "attention"
    kind: str  # what the scorer checks
    prompt: str  # what the app says out loud and shows as a caption
    listen_seconds: int  # how long the app records before moving on
    caption: str = ""  # shown instead of the prompt when the prompt gives the answer away
    expect: str = ""  # the right answer, when it changes day to day (digit span)

    def to_dict(self) -> dict:
        return asdict(self)


GREETINGS = [
    "Hello! Tell me how you slept and what you have planned today.",
    "Hello! How are you feeling today, and what did you have for breakfast?",
    "Hi there! Tell me a little about how your day is going so far.",
    "Good day! What's the weather like where you are, and how are you feeling?",
]

EVENING_GREETINGS = [
    "Good evening! How has your day been?",
    "Hello again! What did you do this afternoon?",
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

DIGIT_SPAN_LENGTH = 4
NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def _seed(person_id: str, day: date, session: str = "morning") -> int:
    key = f"{person_id}:{day.isoformat()}" + ("" if session == "morning" else f":{session}")
    digest = hashlib.sha256(key.encode()).hexdigest()
    return int(digest[:12], 16)


def digit_span(seed: int) -> Exercise:
    """Four different digits from 1 to 9 (no zero, which is said "oh" or
    "zero"), no two neighbours in counting order, said back backwards."""
    rng = random.Random(seed)
    digits: list[int] = []
    while len(digits) < DIGIT_SPAN_LENGTH:
        d = rng.randint(1, 9)
        if d not in digits and not (digits and abs(d - digits[-1]) == 1):
            digits.append(d)
    spoken = ", ".join(NUMBER_WORDS[d] for d in digits)
    return Exercise(
        "digits", "attention", "digit_span",
        f"I'll say four numbers. Say them back to me backwards, starting with the last one. {spoken}.",
        15,
        # On screen the numbers would turn it into a reading task.
        caption="Say the four numbers backwards, starting with the last one.",
        expect="".join(str(d) for d in reversed(digits)),
    )


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
    exercises.append(digit_span(seed // 13))
    return exercises


def build_evening(person_id: str, day: date) -> list[Exercise]:
    """The optional evening check-in, about a minute long: the morning's
    rule-scored questions that can be asked twice a day, so the two can be
    compared. Days backwards every evening, so evenings compare with each
    other too."""
    seed = _seed(person_id, day, "evening")
    return [
        Exercise("greeting", "alertness", "free_speech", EVENING_GREETINGS[seed % len(EVENING_GREETINGS)], 20),
        Exercise("year", "orientation", "year", ORIENTATION["year"][(seed >> 3) % 2], 15),
        Exercise("age", "orientation", "age", ORIENTATION["age"][(seed >> 4) % 2], 15),
        Exercise("attention", "attention", *ATTENTION[1]),
        digit_span(seed // 13),
    ]


def build_session(person_id: str, day: date, session: str = "morning") -> list[Exercise]:
    return build_evening(person_id, day) if session == "evening" else build_checkin(person_id, day)
