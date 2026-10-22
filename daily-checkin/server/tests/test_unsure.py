import json

from test_api import client, person, typed  # noqa: F401  (client is a fixture)

from checkin import api


def fake_hearing(monkeypatch, text, unsure):
    monkeypatch.setattr(api.transcribe, "transcribe_detail",
                        lambda data, ctype, expect=None: {"transcript": text, "words": [], "unsure": unsure})
    monkeypatch.setattr(api.transcribe, "clip_check", lambda data: {"heard_speech": True, "noisy": False})
    monkeypatch.setattr(api, "_heard", {})


def check(client, p, ex_id, clip=b"clip"):
    return client.post(f"/people/{p['id']}/answers/check", data={"exercise_id": ex_id, "date_override": "2026-10-19"},
                       files={"audio": ("a.m4a", clip, "audio/m4a")}).json()


def test_model_doubt_asks_again(client, monkeypatch):
    p = person(client)
    fake_hearing(monkeypatch, "2026", unsure=True)
    assert check(client, p, "year") == {"ask_again": True, "reason": "unsure", "noisy": False}
    fake_hearing(monkeypatch, "2026", unsure=False)
    assert check(client, p, "year") == {"ask_again": False, "reason": None, "noisy": False}


def test_doubtful_answers_are_still_scored(client, monkeypatch):
    # A wrong answer the model was unsure about still counts as wrong, so a
    # hesitant, confused answer can't slip past; the family sees it was hard to hear.
    p = person(client)
    fake_hearing(monkeypatch, "1990", unsure=True)
    plan = client.get(f"/people/{p['id']}/today", params={"date_override": "2026-10-19"}).json()
    answers = [a for a in json.loads(typed(plan)) if a["exercise_id"] != "year"]
    r = client.post(f"/people/{p['id']}/checkins", data={"answers": json.dumps(answers), "date_override": "2026-10-19"},
                    files={"audio_year": ("a.m4a", b"year", "audio/m4a")})
    year = next(i for i in r.json()["items"] if i["exercise_id"] == "year")
    assert year["correct"] is False and year["hard_to_hear"] is True
