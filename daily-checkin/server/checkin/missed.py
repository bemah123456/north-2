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


def due_actions(
    person: dict,
    now_utc: datetime,
    checked_in: set[date],
    days_off: set[date],
    already_sent: set[tuple[str, str]],
) -> list[dict]:
    """What to send right now for one person. already_sent holds
    (date iso, kind) pairs so a job that runs every few minutes sends each
    message once."""
    now = local_now(now_utc, person["timezone"])
    today = now.date()
    since = date.fromisoformat(person["created_date"])
    if today in days_off or today in checked_in or today < since:
        return []
    due = datetime.combine(today, time.fromisoformat(person["checkin_time"]), now.tzinfo)
    minutes_late = (now - due).total_seconds() / 60
    if minutes_late < 0:
        return []

    name = person["name"]
    plan = [(0, "reminder", "senior", "Time for your daily check-in. It only takes 2 minutes.")]
    plan.append((REMINDER_AGAIN_MIN, "reminder_again", "senior",
                 "Friendly reminder: your daily check-in is waiting for you."))
    yesterday = today - timedelta(days=1)
    if _missed(yesterday, checked_in, days_off, since):
        plan.append((FAMILY_ALERT_MIN, "missed_pattern", "family",
                     f"{name} has missed their check-in two days in a row. Please check on "
                     f"them, and consider calling their doctor if they seem unwell or confused."))
    else:
        plan.append((FAMILY_ALERT_MIN, "missed", "family",
                     f"{name} hasn't done today's check-in. Give them a call."))

    actions = []
    for after, kind, to, message in plan:
        if minutes_late >= after and (today.isoformat(), kind) not in already_sent:
            actions.append({"person_id": person["id"], "date": today.isoformat(),
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
                         "reasons": r["reasons"], "checkin_id": r.get("checkin_id")})
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
