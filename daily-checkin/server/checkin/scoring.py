"""Turn one day's answers into a 4AT-style result the family can read."""

from __future__ import annotations

from datetime import date

from . import answers as A
from . import change as C
from . import judge
from .baseline import build_baseline, change_probability, change_scores, top_reasons
from .exercises import Exercise
from .features import Word, checkin_features

CHANGE_ALERT = 0.7  # voice probability that scored acute change, before the combined score
CHANGE_WATCH = 0.4  # shown as a reason, not scored

HEADLINES = {
    "possible_delirium": "Call their doctor today",
    "possible_impairment": "Keep an eye on it",
    "unlikely": "Looks like their usual self",
}

FAMILY_REASON = "family says they seem different today"
CHANGE_REASONS = {
    "some": "some change from their usual, taking everything together",
    "big": "several changes from their usual at once",
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


def _timing(words: list[Word] | None) -> dict:
    """How long they took to start, and to say the answer, in seconds."""
    if not words:
        return {}
    return {"latency_s": round(max(words[0].start, 0.0), 2),
            "answer_s": round(max(words[-1].end - words[0].start, 0.0), 2)}


def score_checkin(
    person: dict,
    day: date,
    exercises: list[Exercise],
    given: dict[str, dict],
    history: list[dict],
    family_says_different: bool | None = None,
    past: list[dict] | None = None,
    routine: dict | None = None,
) -> dict:
    """given: exercise id -> {"transcript": str, "words": list[Word] | None,
    "heard_speech": bool?, "noisy": bool?}. The last two are set for
    recorded answers. When a clip has speech but the transcript can't be an
    answer, the item is left for a person to check instead of counted as a
    mistake. Three or more noisy clips mark the check-in noisy.
    history: feature dicts from this person's earlier normal check-ins.
    past: the `measures` of the same check-ins, for the combined score.
    routine: {"late", "missed_yesterday", "duration_z"} from the server."""
    routine = routine or {}
    items = []
    mistakes = 0
    unsure = 0
    attention = None
    attention_kind = None
    attention_speed = None
    digits = None
    reasons: list[str] = []

    for ex in exercises:
        g = given.get(ex.id, {})
        text = g.get("transcript", "") or ""
        item = {"exercise_id": ex.id, "part": ex.part, "kind": ex.kind,
                "prompt": ex.prompt, "transcript": text} | _timing(g.get("words"))
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
        elif ex.kind == "digit_span":
            if misheard:
                unsure += 1
                item.update(correct_items=0, needed=None, out_of=None)
            else:
                span = A.score_digit_span(text, ex.expect)
                digits = span["correct_items"]
                item.update(span)
        elif ex.part == "attention":
            attention_kind = ex.kind
            if misheard:
                attention = {"correct_items": 0, "needed": None, "out_of": None, "score": None}
                unsure += 1
            else:
                attention = A.score_attention(ex.kind, text)
                # Seconds per item said in order: how hard the task was today.
                if attention["correct_items"] >= 3 and item.get("answer_s"):
                    attention_speed = round(item["answer_s"] / attention["correct_items"], 3)
            item.update(attention)
        items.append(item)

    # AMT4: 0 mistakes 0, 1 mistake 1, 2+ mistakes 2.
    amt4_score = min(mistakes, 2)
    wrong = [i["kind"] for i in items if i.get("correct") is False]
    if mistakes:
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

    answered = sum(1 for e in exercises
                   if (given.get(e.id, {}).get("transcript") or "").strip() or given.get(e.id, {}).get("heard_speech"))
    measures = {
        "orientation_mistakes": mistakes,
        "wrong": wrong,
        "attention_kind": attention_kind,
        "attention_score": attention["score"] if attention else None,
        "attention_s_per_item": attention_speed,
        "digits_correct": digits,
        "latency_s": feats["latency_s"] if feats else None,
        "slow_answers": sum(1 for i in items if i.get("latency_s", 0) >= C.LATE_DAY_SLOW_S),
        "unanswered": len(exercises) - answered,
    }

    # 1. Alertness. The 4AT scores this by watching; here we use clear
    # signs only: no reply to most questions, very slow and very brief
    # against their own normal, or three of the weaker signs together.
    signs = C.drowsiness_signs(measures, z, routine)
    drowsy = answered < len(exercises) / 2
    if not drowsy and z is not None:
        drowsy = z["latency_s"] >= 3 and z["greeting_words"] >= 2
    elif not drowsy and feats and baseline is None:
        drowsy = feats["latency_s"] > 8
    drowsy = drowsy or len(signs) >= 3
    measures["drowsy"] = drowsy
    alertness_score = 4 if drowsy else 0
    if drowsy:
        reasons.insert(0, "seemed drowsy or slow to respond")
    if len(signs) >= 2:
        reasons.extend(s for s in signs if s not in reasons)

    if prob is not None and z is not None and prob >= CHANGE_WATCH:
        reasons.extend(r for r in top_reasons(z) or ["voice differs from their usual"] if r not in reasons)

    # Background noise (a TV, mostly) makes healthy answers look wrong. It
    # doesn't change the 4AT score; the family is told so they can weigh it.
    # Like the research's per-check-in rule: 3 or more noisy answers.
    noisy = sum(1 for g in given.values() if g.get("noisy")) >= 3

    # 4. Acute change: the family's word, an evening worse than the morning
    # (added later), or the combined change score.
    normal = C.personal_normal(past or [])
    e = C.evidence(measures, normal, prob, signs)
    if e["digits"] >= 1:
        reasons.append(f"remembered fewer numbers than usual ({digits} of 4)")
    if e["speed"] >= 1:
        reasons.append("slower than usual at the backwards task")
    if family_says_different:
        reasons.insert(0, FAMILY_REASON)

    # Attention we couldn't hear counts 0 and waits for a person to check.
    attention_score = (attention["score"] or 0) if attention else 2
    result = {
        "date": day.isoformat(),
        "reasons": reasons,
        "parts": {
            "alertness": alertness_score,
            "amt4": amt4_score,
            "attention": attention_score,
            "acute_change": 0,
        },
        "family_says_different": bool(family_says_different),
        "change": C.combine(e, noisy) | {"baseline_days": normal["n_days"]},
        "drowsiness_signs": signs,
        "measures": measures,
        "needs_review": unsure,
        "noisy": noisy,
        "voice": {
            "measured": feats is not None,
            "baseline_days": baseline["n_days"] if baseline else 0,
            "change_probability": prob,
            "change_scores": z,
        },
        "features": feats,
        "items": items,
        "disclaimer": "Screening only, not a diagnosis. If you are worried, call their doctor.",
    }
    finalize(result)
    if noisy and result["total"]:
        result["reasons"].append("lots of background noise, so some answers may have been misheard")
    return result


def finalize(result: dict) -> dict:
    """Score the acute change item and the total from what's known now.
    Called again when the family answers or the evening check-in arrives."""
    change = result.get("change")
    if change is None:  # saved before the combined score: the voice alone decided
        big = (result["voice"]["change_probability"] or 0) >= CHANGE_ALERT
        some = False
    else:
        big, some = change["level"] == "big", change["level"] == "some"
    family = bool(result.get("family_says_different"))
    fluctuating = result.get("evening", {}).get("fluctuation") == "scored"
    result["parts"]["acute_change"] = 4 if (family or big or fluctuating) else 0
    total = sum(result["parts"].values())
    band = "possible_delirium" if total >= 4 else "possible_impairment" if (total >= 1 or some) else "unlikely"

    reasons = [r for r in result["reasons"] if r not in CHANGE_REASONS.values() and r != FAMILY_REASON]
    if family:
        reasons.insert(0, FAMILY_REASON)
    if change is not None and change["level"] != "usual":
        reasons.append(CHANGE_REASONS[change["level"]])
    result.update(total=total, band=band, headline=HEADLINES[band], reasons=reasons)
    return result


def score_evening(person: dict, day: date, exercises: list[Exercise], given: dict[str, dict],
                  morning: dict, past_ratios: list[float]) -> dict:
    """The evening check-in, and how it compares with this morning's.
    past_ratios: evening/morning answer delay on their earlier days."""
    result = score_checkin(person, day, exercises, given, history=[])
    comparison = C.compare_evening(morning.get("measures") or {}, result["measures"], past_ratios)
    result["comparison"] = comparison
    result["reasons"] = comparison["reasons"] or ["about the same as this morning"]
    return result


def apply_evening(morning: dict, evening_id: str, evening: dict) -> dict:
    """Add the evening's comparison to the day's result (the morning's)."""
    comparison = evening["comparison"]
    morning["evening"] = {"checkin_id": evening_id, "fluctuation": comparison["fluctuation"],
                          "reasons": comparison["reasons"]}
    if "change" in morning:
        e = dict(morning["change"]["evidence"], evening=comparison["evidence"])
        morning["change"] = C.combine(e, morning["change"]["noisy"]) | {
            "baseline_days": morning["change"].get("baseline_days", 0)}
    morning["reasons"] = [r for r in morning["reasons"] if not r.startswith("in the evening: ")]
    morning["reasons"].extend(f"in the evening: {r}" for r in comparison["reasons"])
    return finalize(morning)


def words_from_json(raw: list[dict] | None) -> list[Word] | None:
    if raw is None:
        return None
    return [Word(w["text"], float(w["start"]), float(w["end"])) for w in raw]
