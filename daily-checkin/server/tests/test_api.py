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
    assert fam["checkin_id"] == result["checkin_id"]  # the app reports again with it
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


def test_setup_after_the_family_alert_starts_tomorrow(client, monkeypatch):
    # 9am check-in, so the family alert is at noon New York time.
    monkeypatch.setattr(api, "utcnow", lambda: datetime(2026, 10, 19, 15, 30, tzinfo=timezone.utc))  # 11:30
    assert person(client)["created_date"] == "2026-10-19"
    monkeypatch.setattr(api, "utcnow", lambda: datetime(2026, 10, 19, 22, 0, tzinfo=timezone.utc))  # 18:00
    late = person(client)
    assert late["created_date"] == "2026-10-20"
    actions = client.post("/jobs/missed-checkins", params={"now": "2026-10-20T02:30:00+00:00"}).json()["actions"]
    assert not [a for a in actions if a["person_id"] == late["id"]]


def test_bad_times_and_time_zones_are_refused(client):
    p = person(client)
    assert client.patch(f"/people/{p['id']}", json={"timezone": "Mars/Base"}).status_code == 422
    assert client.patch(f"/people/{p['id']}", json={"checkin_time": "25:00"}).status_code == 422
    assert client.patch(f"/people/{p['id']}", json={"evening_time": "19:60"}).status_code == 422
    assert client.patch(f"/people/{p['id']}", json={"checkin_time": "23:59"}).status_code == 200
    r = client.post("/people", json={"name": "Dad", "birth_date": "1940-01-01", "checkin_time": "24:30"})
    assert r.status_code == 422


def test_one_broken_person_doesnt_stop_the_missed_job(client):
    bad, good = person(client), person(client)
    with store.db() as c:
        c.execute("update people set created_date = '2026-10-18'")
        c.execute("update people set timezone = 'Mars/Base' where id = ?", (bad["id"],))
    r = client.post("/jobs/missed-checkins", params={"now": "2026-10-19T16:30:00+00:00"})
    assert r.status_code == 200
    body = r.json()
    assert [e["person_id"] for e in body["errors"]] == [bad["id"]]
    assert {a["person_id"] for a in body["actions"]} == {good["id"]}


def test_empty_or_broken_recording_counts_as_unheard(client, monkeypatch):
    def broken(data, content_type, expect=None):
        raise api.transcribe.UnreadableRecording("Could not decode the recording")

    monkeypatch.setattr(api.transcribe, "transcribe", broken)
    monkeypatch.setattr(api, "_heard", {})
    p = person(client)
    plan = client.get(f"/people/{p['id']}/today", params={"date_override": "2026-10-19"}).json()
    digits = next(ex["id"] for ex in plan["exercises"] if ex["kind"] == "digit_span")
    answers = [a for a in json.loads(typed(plan)) if a["exercise_id"] not in (digits, "year")]
    r = client.post(f"/people/{p['id']}/checkins",
                    data={"answers": json.dumps(answers), "date_override": "2026-10-19"},
                    files={f"audio_{digits}": ("a.m4a", b"", "audio/m4a"),
                           "audio_year": ("a.m4a", b"garbled", "audio/m4a")})
    assert r.status_code == 200, r.text
    check = client.post(f"/people/{p['id']}/answers/check",
                        data={"exercise_id": "year", "date_override": "2026-10-19"},
                        files={"audio": ("a.m4a", b"garbled", "audio/m4a")})
    assert check.json() == {"ask_again": False, "reason": None, "noisy": False}
