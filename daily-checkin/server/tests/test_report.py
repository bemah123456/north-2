import csv
import io
import sqlite3
from datetime import datetime, timezone

from checkin import report, store
from test_api import client, person, typed  # noqa: F401  (fixture and helpers)


def test_testing_numbers(client):
    p = person(client)
    with store.db() as c:
        c.execute("update people set created_date = '2026-10-15' where id = ?", (p["id"],))
    cids = []
    for day, overrides in [("2026-10-15", {}), ("2026-10-16", {"year": "1990"}), ("2026-10-18", {})]:
        plan = client.get(f"/people/{p['id']}/today", params={"date_override": day}).json()
        r = client.post(f"/people/{p['id']}/checkins",
                        data={"answers": typed(plan, overrides), "date_override": day, "duration_s": "150"}).json()
        cids.append(r["checkin_id"])
    client.post(f"/checkins/{cids[0]}/ease", json={"rating": 5})
    client.post(f"/checkins/{cids[1]}/ease", json={"rating": 3})
    assert client.post(f"/checkins/{cids[1]}/ease", json={"rating": 9}).status_code == 422

    # The missed day (Oct 17) raises a family alert, and the family says it was nothing.
    client.post("/jobs/missed-checkins", params={"now": "2026-10-17T17:00:00+00:00"})
    fb = client.post(f"/people/{p['id']}/alerts/feedback",
                     json={"date": "2026-10-17", "kind": "missed", "was_real": False, "note": "At the dentist"})
    assert fb.status_code == 200

    # Hand-score round trip: agree with everything except one year answer.
    sheet = list(csv.DictReader(io.StringIO(client.get("/export/hand-scoring.csv").text)))
    assert sheet and "hand_score" in sheet[0]
    assert {row["noisy_room"] for row in sheet} == {"no"}
    for row in sheet:
        if row["kind"] == "year" and row["checkin_id"] == cids[1]:
            row["hand_score"] = "right"  # the team disagrees with the app here
        elif row["app_says"] in ("right", "wrong"):
            row["hand_score"] = row["app_says"]
        elif "in order" in row["app_says"]:
            row["hand_score"] = row["app_says"].split()[0]
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=sheet[0].keys())
    w.writeheader()
    w.writerows(sheet)
    imported = client.post("/import/hand-scoring", content=out.getvalue()).json()
    assert imported["checkins"] == 3

    r = report.testing_report(datetime(2026, 10, 19, 16, tzinfo=timezone.utc))
    (who,) = r["people"]
    assert (who["days_due"], who["days_done"], who["days_missed"]) == (4, 3, 1)  # Oct 15-18; today not due yet
    assert r["completion_rate"] == 0.75
    by_room = r["hand_agreement_by_room"]
    assert by_room["quiet"]["answers_compared"] == r["hand_agreement"]["answers_compared"]
    assert by_room["noisy"]["answers_compared"] == 0
    assert r["avg_duration_s"] == 150 and r["avg_ease"] == 4
    h = r["hand_agreement"]
    assert h["answers_compared"] == 18 and h["agree"] == 17  # 6 answers a day, digit span included
    assert r["missed_alerts"]["family_answered"] == 1 and r["missed_alerts"]["were_real"] == 0
    md = report.to_markdown(r)
    assert "| Days checked in | 75% | 80%+ | missed |" in md
    assert "At the dentist" in md


def test_old_database_gets_new_columns(tmp_path, monkeypatch):
    path = tmp_path / "old.db"
    old = sqlite3.connect(path)
    old.executescript("""
      create table checkins (id text primary key, person_id text, local_date text, completed_at text,
        local_hour real, result text, features text, family_says_different integer);
      create table alerts (person_id text, date text, kind text, sent_at text, delivered integer, message text,
        primary key (person_id, date, kind));
    """)
    old.close()
    monkeypatch.setattr(store, "DB_PATH", path)
    with store.db() as c:
        cols = {r[1] for r in c.execute("pragma table_info(checkins)")}
        assert {"duration_s", "ease"} <= cols
