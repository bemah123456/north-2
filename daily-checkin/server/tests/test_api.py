import csv
import io
import json
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from checkin import api, store

GOOD = {
    "greeting": "Slept fine thanks, going for a walk with my neighbor later today",
    "age": "eighty two", "dob": "March 14 1944", "place": "home", "year": "2026",
    "months_backwards": "December November October September August July June May",
    "days_backwards": "Sunday Saturday Friday Thursday Wednesday Tuesday Monday",
    "countdown_20": "20 19 18 17 16 15 14 13 12 11 10 9 8 7",
}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(store, "AUDIO_DIR", tmp_path / "audio")
    monkeypatch.setattr(api, "DEMO_MODE", True)
    monkeypatch.delenv("API_TOKEN", raising=False)
    monkeypatch.delenv("NOTIFY_LIVE", raising=False)
    return TestClient(api.app)


def person(client):
    r = client.post("/people", json={"name": "Mom", "birth_date": "1944-03-14",
                                     "place_keywords": ["home"], "family_phone": "+15555550100"})
    assert r.status_code == 200, r.text
    return r.json()


def typed(plan, overrides=None):
    overrides = overrides or {}
    out = []
    for ex in plan["exercises"]:
        key = ex["id"] if ex["part"] != "attention" else ex["kind"]
        right = ex["expect"] if ex["kind"] == "digit_span" else GOOD[key]
        out.append({"exercise_id": ex["id"], "transcript": overrides.get(key, right)})
    return json.dumps(out)


def test_full_day(client):
    p = person(client)
    plan = client.get(f"/people/{p['id']}/today", params={"date_override": "2026-10-19"}).json()
    assert len(plan["exercises"]) == 7 and not plan["already_done"]

    r = client.post(f"/people/{p['id']}/checkins",
                    data={"answers": typed(plan, {"year": "1990"}), "date_override": "2026-10-19"})
    assert r.status_code == 200, r.text
    result = r.json()
    assert result["headline"] == "Keep an eye on it"

    again = client.post(f"/people/{p['id']}/checkins",
                        data={"answers": typed(plan), "date_override": "2026-10-19"})
    assert again.status_code == 409

    fam = client.post(f"/checkins/{result['checkin_id']}/family-report", json={"different": True}).json()
    assert fam["headline"] == "Call their doctor today"
    assert fam["reasons"][0] == "family says they seem different today"
    undo = client.post(f"/checkins/{result['checkin_id']}/family-report", json={"different": False}).json()
    assert undo["headline"] == "Keep an eye on it"

    days = client.get(f"/people/{p['id']}/days").json()["days"]
    row = next(d for d in days if d["date"] == "2026-10-19")
    assert row["status"] == "possible_impairment"


def test_audio_needs_speech_to_text(client, monkeypatch):
    monkeypatch.delenv("STT_PROVIDER", raising=False)
    p = person(client)
    r = client.post(f"/people/{p['id']}/checkins",
                    data={"answers": "[]", "date_override": "2026-10-19"},
                    files={"audio_greeting": ("a.m4a", b"fake", "audio/m4a")})
    assert r.status_code == 503


def test_missed_job_sends_each_alert_once(client):
    p = person(client)
    with store.db() as c:
        c.execute("update people set created_date = '2026-10-18' where id = ?", (p["id"],))
    first = client.post("/jobs/missed-checkins", params={"now": "2026-10-19T16:30:00+00:00"}).json()
    kinds = [a["kind"] for a in first["actions"] if not a.get("skipped")]
    # Missed yesterday (they joined then) and today.
    assert "missed_pattern" in kinds
    assert all(a["delivered"] is False for a in first["actions"])  # not live
    second = client.post("/jobs/missed-checkins", params={"now": "2026-10-19T16:45:00+00:00"}).json()
    assert second["actions"] == []
    alerts = client.get(f"/people/{p['id']}/days").json()["alerts"]
    assert {a["kind"] for a in alerts} >= {"missed_pattern"}


def test_date_override_needs_demo_mode(client, monkeypatch):
    monkeypatch.setattr(api, "DEMO_MODE", False)
    p = person(client)
    r = client.get(f"/people/{p['id']}/today", params={"date_override": "2026-10-19"})
    assert r.status_code == 400


def test_token(client, monkeypatch):
    monkeypatch.setenv("API_TOKEN", "s3cret")
    assert client.post("/people", json={"name": "x", "birth_date": "1940-01-01"}).status_code == 401
    ok = client.post("/people", json={"name": "x", "birth_date": "1940-01-01"},
                     headers={"Authorization": "Bearer s3cret"})
    assert ok.status_code == 200


def test_health(client):
    h = client.get("/health").json()
    assert h["model"]["synthetic"] is True


def test_check_answer_asks_again_once_and_reuses_the_transcript(client, monkeypatch):
    heard = {"age": "I made it too", "year": "twenty twenty six"}
    calls = []

    def fake_transcribe(data, content_type, expect=None):
        calls.append(data)
        return heard[data.decode()], []

    monkeypatch.setattr(api.transcribe, "transcribe", fake_transcribe)
    monkeypatch.setattr(api.transcribe, "clip_check", lambda data: {"heard_speech": True, "noisy": False})
    monkeypatch.setattr(api, "_heard", {})
    p = person(client)
    plan = client.get(f"/people/{p['id']}/today", params={"date_override": "2026-10-19"}).json()
    ids = {ex["id"]: ex["id"] for ex in plan["exercises"]}

    def check(ex_id, clip):
        return client.post(f"/people/{p['id']}/answers/check",
                           data={"exercise_id": ex_id, "date_override": "2026-10-19"},
                           files={"audio": ("a.m4a", clip, "audio/m4a")}).json()

    assert check(ids["age"], b"age") == {"ask_again": True, "reason": "misheard", "noisy": False}
    assert check(ids["year"], b"year") == {"ask_again": False, "reason": None, "noisy": False}

    answers = typed(plan)
    r = client.post(f"/people/{p['id']}/checkins",
                    data={"answers": json.dumps([a for a in json.loads(answers) if a["exercise_id"] != "year"]),
                          "date_override": "2026-10-19"},
                    files={"audio_year": ("a.m4a", b"year", "audio/m4a")})
    assert r.status_code == 200, r.text
    assert calls.count(b"year") == 1  # transcribed once, during the check

    sheet = list(csv.DictReader(io.StringIO(client.get("/export/hand-scoring.csv").text)))
    year = next(row for row in sheet if row["exercise_id"] == "year")
    assert year["recording"].endswith("/audio/year") and open(year["file"], "rb").read() == b"year"
    assert next(row for row in sheet if row["exercise_id"] == "age")["file"] == ""  # typed


def test_check_answer_needs_speech_to_text(client, monkeypatch):
    monkeypatch.delenv("STT_PROVIDER", raising=False)
    monkeypatch.setattr(api, "_heard", {})
    p = person(client)
    r = client.post(f"/people/{p['id']}/answers/check",
                    data={"exercise_id": "age", "date_override": "2026-10-19"},
                    files={"audio": ("a.m4a", b"x", "audio/m4a")})
    assert r.status_code == 503


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
