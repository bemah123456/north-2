"""Missed and late check-ins.

Skipping routines and withdrawing is how the quiet (hypoactive) kind of
delirium often shows, so a missing check-in is a signal too. One missed day
is usually just a busy day, so it asks the family to check on them; two in
a row is marked as a pattern worth raising with a doctor.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from statistics import median
from zoneinfo import ZoneInfo

REMINDER_AGAIN_MIN = 60
FAMILY_ALERT_MIN = 180
LATE_HOURS = 3.0


def local_now(now_utc: datetime, tz: str) -> datetime:
    return now_utc.astimezone(ZoneInfo(tz))


def _missed(day: date, checked_in: set[date], days_off: set[date], since: date) -> bool:
    return day >= since and day not in checked_in and day not in days_off


def _plan(name: str, day: date, checked_in: set[date], days_off: set[date], since: date) -> list:
    """(minutes after the check-in time, kind, to, message) for one day."""
    plan = [(0, "reminder", "senior", "Time for your daily check-in. It only takes 2 minutes.")]
    plan.append((REMINDER_AGAIN_MIN, "reminder_again", "senior",
                 "Friendly reminder: your daily check-in is waiting for you."))
    if _missed(day - timedelta(days=1), checked_in, days_off, since):
        plan.append((FAMILY_ALERT_MIN, "missed_pattern", "family",
                     f"{name} has missed their check-in two days in a row. Please check on "
                     f"them, and consider calling their doctor if they seem unwell or confused."))
    else:
        plan.append((FAMILY_ALERT_MIN, "missed", "family",
                     f"{name} hasn't done today's check-in. Give them a call."))
    return plan


def due_actions(
    person: dict,
    now_utc: datetime,
    checked_in: set[date],
    days_off: set[date],
    already_sent: set[tuple[str, str]],
) -> list[dict]:
    """What to send right now for one person. already_sent holds
    (date iso, kind) pairs so a job that runs every few minutes sends each
    message once. With a late check-in time, yesterday's family alert can
    fall after midnight; it is still sent, under yesterday's date."""
    now = local_now(now_utc, person["timezone"])
    today = now.date()
    since = date.fromisoformat(person["created_date"])
    at = time.fromisoformat(person["checkin_time"])
    midnight = datetime.combine(today, time(0), now.tzinfo)

    actions = []
    for day in (today - timedelta(days=1), today):
        if day in days_off or day in checked_in or day < since:
            continue
        due = datetime.combine(day, at, now.tzinfo)
        for after, kind, to, message in _plan(person["name"], day, checked_in, days_off, since):
            when = due + timedelta(minutes=after)
            # Yesterday's plan only adds family alerts that fell after midnight.
            if day < today and (to != "family" or when < midnight):
                continue
            if now >= when and (day.isoformat(), kind) not in already_sent:
                actions.append({"person_id": person["id"], "date": day.isoformat(),
                                "kind": kind, "to": to, "message": message})
    # Only the most recent senior reminder is worth sending if the job was down.
    senior = [a for a in actions if a["to"] == "senior"]
    if len(senior) > 1:
        actions = [a for a in actions if a["to"] != "senior" or a is senior[-1]]
        actions += [dict(a, skipped=True) for a in senior[:-1]]
    return actions


def is_late(previous_hours: list[float], this_hour: float) -> bool:
    """Is this check-in much later in the day than their usual? Needs at
    least three earlier check-ins to know what usual is."""
    if len(previous_hours) < 3:
        return False
    return this_hour - median(previous_hours[-14:]) >= LATE_HOURS


def day_statuses(
    since: date, today: date, results: dict[date, dict], days_off: set[date], now_local: datetime,
    checkin_time: str,
) -> list[dict]:
    """One row per day for the family view, newest first."""
    rows = []
    d = today
    while d >= since:
        if d in results:
            r = results[d]
            rows.append({"date": d.isoformat(), "status": r["band"], "headline": r["headline"],
                         "reasons": r["reasons"], "checkin_id": r.get("checkin_id"),
                         # For the calendar: the day's 4AT total, and whether
                         # anything was uncertain (answers left for a person
                         # to check, answers that were hard to hear, a noisy room).
                         "score": r.get("total"),
                         "unsure": bool(r.get("needs_review")) or bool(r.get("noisy"))
                         or any(i.get("hard_to_hear") for i in r.get("items", []))})
        elif d in days_off:
            rows.append({"date": d.isoformat(), "status": "day_off", "headline": "Day off", "reasons": []})
        elif d == today and now_local < datetime.combine(
            d, time.fromisoformat(checkin_time), now_local.tzinfo
        ) + timedelta(minutes=FAMILY_ALERT_MIN):
            rows.append({"date": d.isoformat(), "status": "pending", "headline": "Not done yet", "reasons": []})
        else:
            rows.append({"date": d.isoformat(), "status": "missed", "headline": "Check on them",
                         "reasons": ["no check-in this day"]})
        d -= timedelta(days=1)
    return rows
