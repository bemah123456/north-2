"""Turn one day's answers into a 4AT-style result the family can read."""

from __future__ import annotations

from datetime import date

from . import answers as A
from . import judge
from .baseline import build_baseline, change_probability, change_scores, top_reasons
from .exercises import Exercise
from .features import Word, checkin_features

CHANGE_ALERT = 0.7  # model probability that scores the 4AT "acute change" item
# On its own the voice only scores the change item once we know their normal
# well. With 4 baseline days, ordinary healthy days hit the alert about 1 in 10.
VOICE_ALERT_MIN_DAYS = 5
CHANGE_WATCH = 0.4  # shown as a reason, not scored

HEADLINES = {
    "possible_delirium": "Call their doctor today",
    "possible_impairment": "Keep an eye on it",
    "unlikely": "Looks like their usual self",
}


def _check_orientation(ex: Exercise, text: str, person: dict, day: date) -> tuple[bool | None, str]:
    birth = date.fromisoformat(person["birth_date"])
    if ex.kind == "year":
        return A.check_year(text, day), "rules"
    if ex.kind == "age":
        return A.check_age(text, birth, day), "rules"
    if ex.kind == "dob":
        return A.check_dob(text, birth), "rules"
    if ex.kind == "place":
        return A.check_place(text, person.get("place_keywords", [])), "rules"
    raise ValueError(ex.kind)


def _facts(ex: Exercise, person: dict, day: date) -> str:
    birth = date.fromisoformat(person["birth_date"])
    return {
        "year": f"The current year is {day.year}.",
        "age": f"The person is {A.age_on(birth, day)} years old.",
        "dob": f"The person was born on {birth:%B} {birth.day}, {birth.year}.",
        "place": "The person is at a place described as: "
        + "; ".join(person.get("place_keywords", []) or ["unknown"]),
    }[ex.kind]


def retry_reason(ex: Exercise, g: dict) -> str | None:
    """Why a recorded answer can't be scored as heard, or None. "misheard":
    speech was heard but the transcript can't be an answer. "one_month_dropped":
    months backwards that would pass with exactly one month missing, the
    usual speech-to-text slip. The app asks the question again once; if it
    still happens, the item goes to a person instead of counting as wrong."""
    if not g.get("heard_speech"):
        return None
    text = g.get("transcript", "") or ""
    if A.misheard(ex.kind, text):
        return "misheard"
    if ex.kind == "months_backwards" and A.score_attention(ex.kind, text)["score"] and A.one_month_dropped(text):
        return "one_month_dropped"
    return None


def score_checkin(
    person: dict,
    day: date,
    exercises: list[Exercise],
    given: dict[str, dict],
    history: list[dict],
    family_says_different: bool | None = None,
) -> dict:
    """given: exercise id -> {"transcript": str, "words": list[Word] | None,
    "heard_speech": bool?, "noisy": bool?}. The last two are set for
    recorded answers. When a clip has speech but the transcript can't be an
    answer, the item is left for a person to check instead of counted as a
    mistake. Three or more noisy clips mark the check-in noisy.
    history: feature dicts from this person's earlier normal check-ins."""
    items = []
    mistakes = 0
    unsure = 0
    attention = None
    reasons: list[str] = []

    for ex in exercises:
        g = given.get(ex.id, {})
        text = g.get("transcript", "") or ""
        item = {"exercise_id": ex.id, "part": ex.part, "kind": ex.kind,
                "prompt": ex.prompt, "transcript": text}
        retry = retry_reason(ex, g)
        misheard = retry is not None
        if misheard:
            item["misheard"] = True
        if retry == "one_month_dropped":
            item["one_month_dropped"] = True
        if ex.part == "orientation":
            ok, by = (None, "rules") if misheard else _check_orientation(ex, text, person, day)
            if ok is None:
                verdict = judge.judge_answer(ex.prompt, text, _facts(ex, person, day))
                if verdict:
                    ok, by = verdict["correct"], "claude"
                    item["judge_reason"] = verdict["reason"]
            item.update(correct=ok, checked_by=by)
            if ok is False:
                mistakes += 1
            elif ok is None:
                unsure += 1
        elif ex.part == "attention":
            if misheard:
                attention = {"correct_items": 0, "needed": None, "out_of": None, "score": None}
                unsure += 1
            else:
                attention = A.score_attention(ex.kind, text)
            item.update(attention)
        items.append(item)

    # AMT4: 0 mistakes 0, 1 mistake 1, 2+ mistakes 2.
    amt4_score = min(mistakes, 2)
    if mistakes:
        wrong = [i["kind"] for i in items if i.get("correct") is False]
        names = {"year": "the year", "age": "their age", "dob": "their birthday", "place": "where they are"}
        reasons.append("got " + ", ".join(names[w] for w in wrong) + " wrong")
    if attention and attention["score"]:
        reasons.append(
            f"got {attention['correct_items']} of {attention['out_of']} in the backwards task "
            f"(needs {attention['needed']})"
        )

    # How they spoke, against their own normal.
    clips = {k: v["words"] for k, v in given.items() if v.get("words") is not None}
    feats = checkin_features(clips) if clips else None
    baseline = build_baseline(history)
    z = prob = None
    if feats and baseline:
        z = change_scores(feats, baseline)
        prob = change_probability(z)

    # 1. Alertness. The 4AT scores this by watching; here we use clear
    # signs only: no reply to most questions, or very slow and very brief
    # against their own normal.
    answered = sum(1 for e in exercises
                   if (given.get(e.id, {}).get("transcript") or "").strip() or given.get(e.id, {}).get("heard_speech"))
    drowsy = answered < len(exercises) / 2
    if not drowsy and z is not None:
        drowsy = z["latency_s"] >= 3 and z["greeting_words"] >= 2
    elif not drowsy and feats and baseline is None:
        drowsy = feats["latency_s"] > 8
    alertness_score = 4 if drowsy else 0
    if drowsy:
        reasons.insert(0, "seemed drowsy or slow to respond")

    # 4. Acute change: the family's word, or the voice model.
    change_score = 0
    if family_says_different:
        change_score = 4
        reasons.insert(0, "family says they seem different today")
    # A TV or chatter stretches the pauses the voice model measures, so on a
    # noisy check-in the voice is shown but doesn't score.
    noisy = sum(1 for g in given.values() if g.get("noisy")) >= 3
    voice_counts = not noisy and baseline is not None and baseline["n_days"] >= VOICE_ALERT_MIN_DAYS
    if prob is not None and z is not None:
        voice_reasons = top_reasons(z)
        if prob >= CHANGE_ALERT and voice_counts:
            change_score = 4
            reasons.extend(voice_reasons or ["voice differs from their usual"])
        elif prob >= CHANGE_WATCH:
            reasons.extend(voice_reasons)

    # Attention we couldn't hear counts 0 and waits for a person to check.
    attention_score = (attention["score"] or 0) if attention else 2
    total = alertness_score + amt4_score + attention_score + change_score
    band = "possible_delirium" if total >= 4 else "possible_impairment" if total >= 1 else "unlikely"
    # Background noise (a TV, mostly) makes healthy answers look wrong. It
    # doesn't change the score; the family is told so they can weigh it.
    # Like the research's per-check-in rule: 3 or more noisy answers.
    if noisy and total:
        reasons.append("lots of background noise, so some answers may have been misheard")

    return {
        "date": day.isoformat(),
        "total": total,
        "band": band,
        "headline": HEADLINES[band],
        "reasons": reasons,
        "parts": {
            "alertness": alertness_score,
            "amt4": amt4_score,
            "attention": attention_score,
            "acute_change": change_score,
        },
        "needs_review": unsure,
        "noisy": noisy,
        "voice": {
            "measured": feats is not None,
            "baseline_days": baseline["n_days"] if baseline else 0,
            "change_probability": prob,
            "change_scores": z,
            "counts": voice_counts,
        },
        "features": feats,
        "items": items,
        "disclaimer": "Screening only, not a diagnosis. If you are worried, call their doctor.",
    }


def words_from_json(raw: list[dict] | None) -> list[Word] | None:
    if raw is None:
        return None
    return [Word(w["text"], float(w["start"]), float(w["end"])) for w in raw]
