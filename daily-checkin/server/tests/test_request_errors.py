from datetime import datetime, timezone

import pytest

from checkin import report
from test_api import client, person, typed  # noqa: F401  (fixture and helpers)


@pytest.mark.parametrize("data", [
    {"answers": "not json"},
    {"answers": '{"exercise_id": "age"}'},
    {"answers": '[{"transcript": "eighty"}]'},
    {"answers": '[{"exercise_id": "age", "words": [{"text": "eighty"}]}]'},
    {"answers": "[]", "duration_s": "abc"},
    {"answers": "[]", "date_override": "yesterday"},
])
def test_malformed_check_ins_get_a_400(client, data):
    p = person(client)
    data = {"date_override": "2026-10-19", **data}
    r = client.post(f"/people/{p['id']}/checkins", data=data)
    assert r.status_code == 400, r.text


def test_evening_ratings_count(client):
    p = person(client)
    client.patch(f"/people/{p['id']}", json={"evening_checkin": True})
    ids = []
    for session in ("morning", "evening"):
        plan = client.get(f"/people/{p['id']}/today",
                          params={"date_override": "2026-10-19", "session": session}).json()
        r = client.post(f"/people/{p['id']}/checkins",
                        data={"answers": typed(plan), "date_override": "2026-10-19", "session": session})
        assert r.status_code == 200, r.text
        ids.append(r.json()["checkin_id"])
    client.post(f"/checkins/{ids[0]}/ease", json={"rating": 5})
    client.post(f"/checkins/{ids[1]}/ease", json={"rating": 1})
    r = report.testing_report(datetime(2026, 10, 19, 16, tzinfo=timezone.utc))
    assert r["ease_ratings"] == 2 and r["avg_ease"] == 3
    assert r["evening_checkins"] == 1 and r["checkins"] == 1
