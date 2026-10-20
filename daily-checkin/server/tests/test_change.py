"""Attention tests and timing, drowsiness, the evening check-in and the
combined change score."""

import json
import sqlite3
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from checkin import answers as A
from checkin import api, store
from checkin.change import combine, compare_evening, evidence, personal_normal
from checkin.exercises import build_checkin, build_evening, digit_span
from checkin.scoring import retry_reason, score_checkin

from test_scoring import DAY, PERSON, answers, history, said_back


def plan():
    return build_checkin("p1", DAY)


def usual_past(days=5):
    """Measures of ordinary days, as the server keeps them."""
    out = []
    for i in range(days):
        d = DAY - timedelta(days=days - i)
        r = score_checkin(PERSON, d, build_checkin("p1", d), answers(d, pause_every=8), [])
        out.append(r["measures"])
    return out


# 1. Attention: digit span and timing

def test_digit_span_is_four_different_digits_and_hidden_on_screen():
    for seed in range(200):
        ex = digit_span(seed * 7919)
        assert len(set(ex.expect)) == 4 and "0" not in ex.expect
        assert all(abs(int(a) - int(b)) != 1 for a, b in zip(ex.expect, ex.expect[1:]))
        assert ex.expect[::-1][0] in {str(i) for i in range(1, 10)}
        assert not any(ch.isdigit() for ch in ex.caption)


@pytest.mark.parametrize("said,expect", [
    ("six two nine four", 4),
    ("6 2 9 4", 4),
    ("6294", 4),
    ("six two nine for", 4),  # "four" heard as "for"
    ("sixty two, ninety four", 4),
    ("six nine two four", 2),  # counted in order, like the backwards tasks
    ("four nine two six", 0),  # said forwards
    ("I don't know", 0),
])
def test_digit_span_scoring(said, expect):
    assert A.score_digit_span(said, "6294")["correct_items"] == expect


def test_digit_span_with_no_numbers_is_asked_again():
    ex = digit_span(1)
    assert retry_reason(ex, {"transcript": "sorry what was that", "heard_speech": True}) == "misheard"
    assert retry_reason(ex, {"transcript": "I don't know", "heard_speech": True}) is None


def test_each_answer_is_timed():
    r = score_checkin(PERSON, DAY, plan(), answers(DAY, latency=1.5), [])
    assert all(i["latency_s"] == 1.5 and i["answer_s"] > 0 for i in r["items"])
    assert r["measures"]["attention_s_per_item"] > 0
    assert r["measures"]["digits_correct"] == 4


def test_fewer_digits_than_usual_is_a_reason():
    r = score_checkin(PERSON, DAY, plan(), answers(DAY, {"digit_span": "nine um"}), history(), past=usual_past())
    assert r["change"]["evidence"]["digits"] >= 1
    assert any("fewer numbers than usual" in x for x in r["reasons"])
    assert r["parts"]["attention"] == 0  # the 4AT's own attention item is unchanged


def test_slower_at_the_backwards_task_than_usual():
    att = next(ex for ex in plan() if ex.id == "attention")
    past = []
    for i in range(1, 9):  # earlier days with the same task
        d = DAY - timedelta(days=2 * i)
        assert next(ex for ex in build_checkin("p1", d) if ex.id == "attention").kind == att.kind
        past.append(score_checkin(PERSON, d, build_checkin("p1", d), answers(d, words_per_min=130), [])["measures"])
    slow = answers(DAY)
    slow["attention"] = answers(DAY, words_per_min=55)["attention"]
    r = score_checkin(PERSON, DAY, plan(), slow, [], past=past)
    assert r["change"]["evidence"]["speed"] >= 1
    assert "slower than usual at the backwards task" in r["reasons"]


# 3. Drowsiness

def test_one_drowsy_sign_is_not_enough_but_three_are():
    one = score_checkin(PERSON, DAY, plan(), answers(DAY, pause_every=8), history(),
                        routine={"late": True})
    assert one["parts"]["alertness"] == 0 and one["drowsiness_signs"] == ["checked in much later in the day than usual"]
    three = score_checkin(PERSON, DAY, plan(), answers(DAY, pause_every=8), history(),
                          routine={"late": True, "missed_yesterday": True, "duration_z": 3.0})
    assert three["parts"]["alertness"] == 4
    assert "missed yesterday's check-in" in three["reasons"]


def test_long_silences_count_as_a_drowsy_sign():
    given = answers(DAY, pause_every=8)
    for k in ("age", "year"):
        given[k] = answers(DAY, latency=7.0)[k]
    r = score_checkin(PERSON, DAY, plan(), given, [])
    assert r["measures"]["slow_answers"] == 2
    assert "long silences before answering, or no answer" in r["drowsiness_signs"]


# 4. The combined score

def test_voice_alone_cannot_reach_a_big_change():
    normal = personal_normal([])
    today = {"orientation_mistakes": 0, "attention_score": 0, "digits_correct": 4}
    c = combine(evidence(today, normal, 0.99, []))
    assert c["level"] == "some"  # keep an eye on it, not call the doctor


def test_one_wrong_answer_alone_is_usual():
    normal = personal_normal([])
    c = combine(evidence({"orientation_mistakes": 1, "attention_score": 0, "digits_correct": 4}, normal, 0.2, []))
    assert c["level"] == "usual"


def test_several_moderate_changes_add_up_to_a_big_one():
    normal = personal_normal(usual_past())
    today = {"orientation_mistakes": 0, "attention_score": 0, "digits_correct": 2}
    e = evidence(today, normal, 0.75, ["slower to answer than usual", "saying much less than usual"])
    assert all(v < 3 for v in e.values())  # no single part is at its limit
    assert combine(e)["level"] == "big"


def test_noise_halves_voice_evidence():
    e = {"answers": 0, "digits": 0, "speed": 0, "voice": 3.0, "drowsy": 0, "evening": 0}
    assert combine(e)["level"] == "some"
    assert combine(e, noisy=True)["level"] == "usual"


def test_small_changes_without_a_wrong_answer_say_keep_an_eye():
    two_of_four = " ".join(said_back(next(e for e in plan() if e.id == "digits")).split()[:2])
    r = score_checkin(PERSON, DAY, plan(), answers(DAY, {"digit_span": two_of_four}, pause_every=8), history(),
                      past=usual_past(), routine={"late": True, "missed_yesterday": True})
    assert r["parts"] == {"alertness": 0, "amt4": 0, "attention": 0, "acute_change": 0}
    assert r["change"]["level"] == "some"
    assert r["band"] == "possible_impairment"
    assert "small changes from their usual in more than one place" in r["reasons"]


def test_usual_day_scores_low():
    r = score_checkin(PERSON, DAY, plan(), answers(DAY, pause_every=8), history(), past=usual_past())
    assert r["change"]["level"] == "usual" and r["change"]["score"] < 20
    assert r["band"] == "unlikely"


# 2. The evening check-in, scored against the morning

def test_evening_plan_is_short_and_comparable():
    ev = build_evening("p1", DAY)
    assert [e.id for e in ev] == ["greeting", "year", "age", "attention", "digits"]
    assert ev[3].kind == "days_backwards"
    assert ev[4].expect != next(e for e in plan() if e.id == "digits").expect
    assert sum(e.listen_seconds for e in ev) <= sum(e.listen_seconds for e in plan()) * 2 / 3


def test_compare_evening():
    morning = {"wrong": [], "attention_score": 0, "digits_correct": 4, "latency_s": 1.0}
    same = {"orientation_mistakes": 0, "attention_score": 0, "digits_correct": 4, "latency_s": 1.2}
    assert compare_evening(morning, same, [])["fluctuation"] == "none"
    one_wrong = same | {"orientation_mistakes": 1}
    assert compare_evening(morning, one_wrong, [])["fluctuation"] == "watch"
    worse = same | {"orientation_mistakes": 1, "attention_score": 1}
    assert compare_evening(morning, worse, [])["fluctuation"] == "scored"
    slow = same | {"latency_s": 3.5}
    assert compare_evening(morning, slow, [])["fluctuation"] == "watch"
    assert compare_evening(morning, slow, [3.0, 3.5, 3.2])["fluctuation"] == "none"  # always slower at night
    assert compare_evening(morning, one_wrong | {"latency_s": 3.5}, [])["fluctuation"] == "scored"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(store, "AUDIO_DIR", tmp_path / "audio")
    monkeypatch.setattr(api, "DEMO_MODE", True)
    monkeypatch.delenv("API_TOKEN", raising=False)
    return TestClient(api.app)


def typed(exercises, overrides=None):
    right = {"greeting": "fine thanks, a quiet day", "age": "eighty two", "dob": "March 14 1944", "place": "home",
             "year": "2026", "months_backwards": "December November October September August July June May",
             "days_backwards": "Sunday Saturday Friday Thursday Wednesday Tuesday Monday",
             "countdown_20": "20 19 18 17 16 15 14 13 12 11 10 9 8 7"}
    out = []
    for ex in exercises:
        key = ex["id"] if ex["part"] != "attention" else ex["kind"]
        text = ex["expect"] if ex["kind"] == "digit_span" else right[key]
        out.append({"exercise_id": ex["id"], "transcript": (overrides or {}).get(key, text)})
    return json.dumps(out)


def test_evening_checkin_flow(client):
    d = "2026-10-19"
    p = client.post("/people", json={"name": "Mom", "birth_date": "1944-03-14", "place_keywords": ["home"]}).json()
    assert p["evening_checkin"] is False  # off unless the family turns it on
    pid = p["id"]
    morning = client.get(f"/people/{pid}/today", params={"date_override": d}).json()
    assert morning["session"] == "morning" and morning["evening_at"] is None
    assert client.post(f"/people/{pid}/checkins", data={"answers": typed(morning["exercises"]),
                                                        "date_override": d}).status_code == 200
    off = client.post(f"/people/{pid}/checkins", data={"answers": "[]", "date_override": d, "session": "evening"})
    assert off.status_code == 409

    client.patch(f"/people/{pid}", json={"evening_checkin": True, "evening_time": "19:00"})
    plan = client.get(f"/people/{pid}/today", params={"date_override": d, "session": "evening"}).json()
    assert plan["session"] == "evening" and not plan["already_done"] and len(plan["exercises"]) == 5
    worse = typed(plan["exercises"], {"year": "1990", "days_backwards": "Sunday Saturday"})
    ev = client.post(f"/people/{pid}/checkins", data={"answers": worse, "date_override": d, "session": "evening"})
    assert ev.status_code == 200, ev.text
    assert ev.json()["comparison"]["fluctuation"] == "scored"

    day = next(r for r in client.get(f"/people/{pid}/days").json()["days"] if r["date"] == d)
    assert day["headline"] == "Call their doctor today"
    assert any(r.startswith("in the evening: ") for r in day["reasons"])
    result = client.get(f"/checkins/{day['checkin_id']}").json()
    assert result["parts"]["acute_change"] == 4 and result["evening"]["fluctuation"] == "scored"

    # The family saying "no change" doesn't undo what the evening showed.
    fam = client.post(f"/checkins/{day['checkin_id']}/family-report", json={"different": False}).json()
    assert fam["parts"]["acute_change"] == 4
    assert client.get(f"/people/{pid}/today", params={"date_override": d, "session": "evening"}).json()["already_done"]


def test_old_database_gets_the_evening_columns(tmp_path, monkeypatch):
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.executescript("""
      create table people (id text primary key, name text not null, birth_date text not null,
        timezone text not null, checkin_time text not null, place_keywords text not null default '[]',
        family_name text, family_phone text, senior_push_token text, family_push_token text,
        created_date text not null);
      create table checkins (id text primary key, person_id text not null references people(id) on delete cascade,
        local_date text not null, completed_at text not null, local_hour real not null, result text not null,
        features text, family_says_different integer, unique (person_id, local_date));
      create table hand_scores (checkin_id text not null references checkins(id) on delete cascade,
        exercise_id text not null, value text not null, primary key (checkin_id, exercise_id));
      insert into people values ('p', 'Mom', '1944-03-14', 'UTC', '09:00', '[]', null, null, null, null, '2026-10-01');
      insert into checkins values ('c', 'p', '2026-10-02', 'x', 9.0, '{"band": "unlikely"}', null, null);
      insert into hand_scores values ('c', 'year', 'right');
    """)
    conn.commit()
    conn.close()
    monkeypatch.setattr(store, "DB_PATH", path)
    assert store.get_person("p")["evening_checkin"] is False
    assert [c["session"] for c in store.checkins("p")] == ["morning"]
    store.add_checkin("p", date(2026, 10, 2), "y", 19.0, {"band": "unlikely"}, None, None, session="evening")
    assert len(store.checkins("p", None)) == 2
    assert store.hand_scores() == {"c": {"year": "right"}}
