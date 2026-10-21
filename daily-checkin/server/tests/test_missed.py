from datetime import date, datetime, timezone

from checkin.missed import due_actions, is_late

PERSON = {"id": "p1", "name": "Mom", "timezone": "America/New_York", "checkin_time": "09:00",
          "created_date": "2026-10-10"}


def at(hh, mm=0, day=19):
    # New York is UTC-4 in October.
    return datetime(2026, 10, day, hh + 4, mm, tzinfo=timezone.utc)


def kinds(actions):
    return [a["kind"] for a in actions if not a.get("skipped")]


def test_timeline_for_a_missed_day():
    done = {date(2026, 10, 18)}
    assert due_actions(PERSON, at(8, 59), done, set(), set()) == []
    assert kinds(due_actions(PERSON, at(9, 5), done, set(), set())) == ["reminder"]
    sent = {("2026-10-19", "reminder")}
    assert kinds(due_actions(PERSON, at(10, 1), done, set(), sent)) == ["reminder_again"]
    sent.add(("2026-10-19", "reminder_again"))
    family = due_actions(PERSON, at(12, 0), done, set(), sent)
    assert kinds(family) == ["missed"]
    assert family[0]["to"] == "family"
    assert family[0]["message"] == "Mom hasn't done today's check-in. Give them a call."
    sent.add(("2026-10-19", "missed"))
    assert due_actions(PERSON, at(15, 0), done, set(), sent) == []


def test_two_missed_days_is_a_pattern():
    out = due_actions(PERSON, at(12, 30), {date(2026, 10, 17)}, set(), set())
    assert "missed_pattern" in kinds(out)
    # A late job sends only the latest reminder, not a burst of them.
    assert [a["kind"] for a in out if a["to"] == "senior" and not a.get("skipped")] == ["reminder_again"]


def test_done_or_day_off_sends_nothing():
    assert due_actions(PERSON, at(13), {date(2026, 10, 19)}, set(), set()) == []
    assert due_actions(PERSON, at(13), set(), {date(2026, 10, 19)}, set()) == []


def test_day_off_yesterday_is_not_a_pattern():
    out = due_actions(PERSON, at(12, 30), set(), {date(2026, 10, 18)}, set())
    assert "missed" in kinds(out) and "missed_pattern" not in kinds(out)


def test_late_checkin():
    assert not is_late([9.0, 9.2], 14.0)
    assert is_late([9.0, 9.2, 8.9, 9.1], 13.0)
    assert not is_late([9.0, 9.2, 8.9, 9.1], 10.5)


def test_late_check_in_time_still_alerts_the_family_after_midnight():
    late = dict(PERSON, checkin_time="22:00")
    done = {date(2026, 10, 18)}
    sent = {("2026-10-19", "reminder"), ("2026-10-19", "reminder_again")}
    # 01:00 on the 20th: the 22:00 check-in on the 19th was never done.
    actions = due_actions(late, datetime(2026, 10, 20, 5, 0, tzinfo=timezone.utc), done, set(), sent)
    assert [(a["date"], a["kind"], a["to"]) for a in actions] == [("2026-10-19", "missed", "family")]
    # No senior reminders for yesterday, and nothing once it's sent or they checked in.
    sent.add(("2026-10-19", "missed"))
    assert due_actions(late, datetime(2026, 10, 20, 5, 30, tzinfo=timezone.utc), done, set(), sent) == []
    assert due_actions(late, datetime(2026, 10, 20, 5, 0, tzinfo=timezone.utc),
                       done | {date(2026, 10, 19)}, set(), set()) == []
