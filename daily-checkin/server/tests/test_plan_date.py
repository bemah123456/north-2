from datetime import datetime, timezone

from checkin import api
from test_api import client, person, typed  # noqa: F401  (fixture and helpers)


def test_check_in_that_runs_past_midnight_keeps_its_questions(client, monkeypatch):
    monkeypatch.setattr(api, "utcnow", lambda: datetime(2026, 11, 2, 14, 0, tzinfo=timezone.utc))
    p = person(client)
    monkeypatch.setattr(api, "utcnow", lambda: datetime(2026, 11, 3, 4, 50, tzinfo=timezone.utc))  # 23:50 Nov 2
    plan = client.get(f"/people/{p['id']}/today").json()
    assert plan["date"] == "2026-11-02"
    monkeypatch.setattr(api, "utcnow", lambda: datetime(2026, 11, 3, 5, 5, tzinfo=timezone.utc))  # 00:05 Nov 3
    r = client.post(f"/people/{p['id']}/checkins", data={"answers": typed(plan), "plan_date": plan["date"]})
    assert r.status_code == 200, r.text
    assert r.json()["headline"] == "Looks like their usual self"
    days = client.get(f"/people/{p['id']}/days").json()["days"]
    assert next(d for d in days if d["date"] == "2026-11-02")["status"] != "missed"

    # Only yesterday's plan is accepted; an older one is today's check-in.
    old = client.get(f"/people/{p['id']}/today").json()
    assert old["date"] == "2026-11-03"
    stale = client.post(f"/people/{p['id']}/checkins", data={"answers": typed(old), "plan_date": "2026-10-30"})
    assert stale.status_code == 200
    bad = client.post(f"/people/{p['id']}/checkins", data={"answers": "[]", "plan_date": "soon"})
    assert bad.status_code == 400
