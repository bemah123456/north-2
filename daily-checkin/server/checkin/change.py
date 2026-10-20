"""One change score per check-in, against the person's own normal.

Answers, answer timing, the voice and drowsiness used to raise their own
alarms. Each is now turned into "evidence" from 0 (as usual) to 3 (far
from usual), and the evidence is added up:

- answers:   more orientation or 4AT attention mistakes than they usually make
- digits:    fewer digits said back than usual
- speed:     slower at the backwards task than usual (same task only)
- voice:     the voice model's change probability (hesitation, pauses, ...)
- drowsy:    signs of reduced alertness (see `drowsiness_signs`)
- evening:   the evening check-in was worse than the morning

A total of 2.5 or more is "some change" (keep an eye on it, even when no
answer was wrong). 4.5 or more, with at least two kinds of evidence of 1
or more, is "a big change", which scores the 4AT's acute change item.

Why add them up: the cloud research (PR #6) found the voice alone alarms
on about 3% of healthy days even with one-off "um"s capped, and that a 20%
slowdown can't be told from a normal day by timing alone. So no single
measure can reach "a big change" by itself, while several moderate changes
together can, which catches changes too small for any one alarm.

The weights and cut-offs are set by hand on simulated days, not learned
from real delirium, and need checking on real check-ins.
"""

from __future__ import annotations

from statistics import mean, median, pstdev

SOME_CHANGE = 2.5
BIG_CHANGE = 4.5
MAX_EVIDENCE = 3.0
# Voice and timing are less trustworthy with a TV on, and digits get misheard.
NOISY_WEIGHT = 0.5
NOISY_PARTS = ("digits", "speed", "voice")

# Before a person has a normal of their own, assume a well older adult:
# no mistakes, and three of four digits said back. Each assumption counts
# as this many days, so a few real days soon take over.
PRIOR_DAYS = 2
PRIOR_DIGITS = 3.0
SPEED_FLOOR = 0.3  # seconds per item; smallest spread we trust
LATE_DAY_SLOW_S = 6.0  # an answer this slow to start is a long silence
DURATION_FLOOR_S = 30.0

LEVELS = {"usual": "As usual", "some": "Some change from their usual", "big": "A big change from their usual"}


def _clip(x: float) -> float:
    return max(0.0, min(MAX_EVIDENCE, x))


def _shrunk_mean(values: list[float], prior: float) -> float:
    return (sum(values) + prior * PRIOR_DAYS) / (len(values) + PRIOR_DAYS)


def personal_normal(past: list[dict]) -> dict:
    """past: the `measures` of earlier usual check-ins, oldest first."""
    past = [m for m in past if m][-14:]
    orient = [m["orientation_mistakes"] for m in past if m.get("orientation_mistakes") is not None]
    att = [m["attention_score"] for m in past if m.get("attention_score") is not None]
    digits = [m["digits_correct"] for m in past if m.get("digits_correct") is not None]
    speed: dict[str, list[float]] = {}
    for m in past:
        if m.get("attention_s_per_item"):
            speed.setdefault(m["attention_kind"], []).append(m["attention_s_per_item"])
    return {
        "n_days": len(past),
        "orientation_mistakes": _shrunk_mean(orient, 0.0),
        "attention_score": _shrunk_mean(att, 0.0),
        "digits_correct": _shrunk_mean(digits, PRIOR_DIGITS),
        "speed": {k: {"mean": mean(v), "std": max(pstdev(v), SPEED_FLOOR, 0.15 * mean(v))}
                  for k, v in speed.items() if len(v) >= 2},
    }


def drowsiness_signs(today: dict, z: dict | None, routine: dict) -> list[str]:
    """Signs of reduced alertness, the 4AT's first item, beyond the answers
    themselves. Each is weak alone (a busy morning, a late night), so they
    count toward the change score and only score the 4AT's alertness item
    when three or more come together."""
    signs = []
    if z is not None and z.get("latency_s", 0) >= 2:
        signs.append("slower to answer than usual")
    elif z is None and (today.get("latency_s") or 0) > LATE_DAY_SLOW_S:
        signs.append("slow to start answering")
    if today.get("slow_answers", 0) + today.get("unanswered", 0) >= 2:
        signs.append("long silences before answering, or no answer")
    if z is not None and z.get("greeting_words", 0) >= 2:
        signs.append("saying much less than usual")
    if routine.get("duration_z") is not None and routine["duration_z"] >= 2:
        signs.append("the check-in took much longer than usual")
    if routine.get("late"):
        signs.append("checked in much later in the day than usual")
    if routine.get("missed_yesterday"):
        signs.append("missed yesterday's check-in")
    return signs


def duration_z(durations: list[float], today: float | None) -> float | None:
    durations = [d for d in durations if d][-14:]
    if today is None or len(durations) < 3:
        return None
    return (today - mean(durations)) / max(pstdev(durations), DURATION_FLOOR_S)


def evidence(today: dict, normal: dict, voice_probability: float | None, signs: list[str]) -> dict[str, float]:
    e = {
        "answers": _clip(max(0.0, today["orientation_mistakes"] - normal["orientation_mistakes"])
                         + max(0.0, (today["attention_score"] or 0) - normal["attention_score"])),
        "digits": 0.0,
        "speed": 0.0,
        "voice": 0.0,
        "drowsy": _clip(0.75 * len(signs)),
        "evening": 0.0,
    }
    if today.get("digits_correct") is not None:
        # Half a digit of slack: one slip from a perfect usual is nothing.
        e["digits"] = _clip(normal["digits_correct"] - today["digits_correct"] - 0.5)
    usual = normal["speed"].get(today.get("attention_kind"))
    if usual and today.get("attention_s_per_item"):
        z = (today["attention_s_per_item"] - usual["mean"]) / usual["std"]
        e["speed"] = _clip(z - 1)
    if voice_probability is not None:
        # 0.4 was "worth mentioning" and 0.7 used to score 4 points alone;
        # now 0.9 or more gives the most evidence one part can give.
        e["voice"] = _clip(MAX_EVIDENCE * (voice_probability - 0.4) / 0.5)
    return {k: round(v, 2) for k, v in e.items()}


def combine(e: dict[str, float], noisy: bool = False) -> dict:
    weighted = {k: v * (NOISY_WEIGHT if noisy and k in NOISY_PARTS else 1.0) for k, v in e.items()}
    total = sum(weighted.values())
    strong = sum(1 for v in weighted.values() if v >= 1)
    level = "big" if total >= BIG_CHANGE and strong >= 2 else "some" if total >= SOME_CHANGE else "usual"
    return {
        "score": round(100 * min(total, 2 * MAX_EVIDENCE) / (2 * MAX_EVIDENCE)),
        "total": round(total, 2),
        "level": level,
        "label": LEVELS[level],
        "evidence": e,
        "noisy": noisy,
    }


# The evening check-in against the same morning.
EVENING_SLOWER = 0.5  # evening/morning answer delay this much above their usual ratio
EVENING_SLOWER_S = 1.5  # and at least this many seconds slower
USUAL_EVENING_RATIO = 1.2  # until they have evenings of their own, allow 20% slower


def compare_evening(morning: dict, evening: dict, past_ratios: list[float]) -> dict:
    """morning and evening: `measures` of the two check-ins on one day.
    Delirium comes and goes within a day; a day that's clearly worse in the
    evening is the 4AT's "fluctuating course". Most people are a little
    slower in the evening, so slowness is judged against their own usual
    evening, and only mistakes can score on their own."""
    reasons = []
    drop = 0.0
    m_orient = sum(1 for k in ("year", "age") if k in morning.get("wrong", []))
    e_orient = evening["orientation_mistakes"]
    if e_orient > m_orient:
        drop += e_orient - m_orient
        reasons.append("got more questions wrong in the evening than the morning")
    if (evening["attention_score"] or 0) > (morning["attention_score"] or 0):
        drop += (evening["attention_score"] or 0) - (morning["attention_score"] or 0)
        reasons.append("did worse at the backwards task in the evening")
    if evening.get("digits_correct") is not None and morning.get("digits_correct") is not None \
            and morning["digits_correct"] - evening["digits_correct"] >= 2:
        drop += 1
        reasons.append(f"remembered {evening['digits_correct']} of 4 numbers in the evening, "
                       f"{morning['digits_correct']} in the morning")
    if evening.get("drowsy"):
        drop += 2
        reasons.append("seemed drowsy in the evening")

    slow = False
    ratio = None
    if morning.get("latency_s") and evening.get("latency_s"):
        ratio = evening["latency_s"] / max(morning["latency_s"], 0.3)
        usual = median(past_ratios[-14:]) if len(past_ratios) >= 2 else USUAL_EVENING_RATIO
        slow = ratio - usual >= EVENING_SLOWER and evening["latency_s"] - morning["latency_s"] >= EVENING_SLOWER_S
        if slow:
            reasons.append("much slower to answer in the evening than the morning")

    if drop >= 2 or (drop >= 1 and slow):
        fluctuation = "scored"
    elif drop >= 1 or slow:
        fluctuation = "watch"
    else:
        fluctuation = "none"
    return {
        "fluctuation": fluctuation,
        "evidence": {"scored": MAX_EVIDENCE, "watch": 1.5, "none": 0.0}[fluctuation],
        "reasons": reasons,
        "latency_ratio": round(ratio, 2) if ratio else None,
    }
