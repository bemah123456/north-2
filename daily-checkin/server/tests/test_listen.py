import json

from test_api import client, person, typed  # noqa: F401  (client is a fixture)

from checkin import api, notify, store


def recorded_checkin(client, monkeypatch, p, day="2026-10-19"):
    """A check-in where the year was spoken and recorded, the rest typed."""
    monkeypatch.setattr(api.transcribe, "transcribe", lambda data, ctype, expect=None: ("2026", []))
    monkeypatch.setattr(api.transcribe, "clip_check", lambda data: {"heard_speech": True, "noisy": False})
    monkeypatch.setattr(api, "_heard", {})
    plan = client.get(f"/people/{p['id']}/today", params={"date_override": day}).json()
    answers = [a for a in json.loads(typed(plan)) if a["exercise_id"] != "year"]
    r = client.post(f"/people/{p['id']}/checkins",
                    data={"answers": json.dumps(answers), "date_override": day},
                    files={"audio_year": ("a.m4a", b"year-clip", "audio/m4a")})
    assert r.status_code == 200, r.text
    return r.json()


def test_family_hears_the_checkin(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://example.trycloudflare.com/")
    p = person(client)
    assert p["share_recordings"] is True
    result = recorded_checkin(client, monkeypatch, p)

    alert = next(a for a in client.get(f"/people/{p['id']}/days").json()["alerts"] if a["kind"] == "recording")
    assert alert["message"].startswith(f"Mom just finished today's check-in: {result['headline']}.")
    link = alert["message"].split("Listen to it here: ")[1]
    assert link.startswith(f"https://example.trycloudflare.com/listen/{result['checkin_id']}/")
    path = link.removeprefix("https://example.trycloudflare.com")

    # The private link plays without the API token.
    monkeypatch.setenv("API_TOKEN", "secret")
    page = client.get(path)
    assert page.status_code == 200 and "Play the whole check-in" in page.text
    assert client.get(f"{path}/year").content == b"year-clip"
    assert client.get(f"{path[:-3]}xyz").status_code == 404  # wrong key
    assert client.get(f"/checkins/{result['checkin_id']}/recording").status_code == 401

    # The app's view lists every question in order, with the recorded one playable.
    rec = client.get(f"/checkins/{result['checkin_id']}/recording",
                     headers={"Authorization": "Bearer secret"}).json()
    assert [x["exercise_id"] for x in rec["parts"]] == [i["exercise_id"] for i in result["items"]]
    year = next(x for x in rec["parts"] if x["exercise_id"] == "year")
    assert year["audio"] == f"/checkins/{result['checkin_id']}/audio/year" and year["transcript"] == "2026"
    assert all(x["audio"] is None for x in rec["parts"] if x["exercise_id"] != "year")


def test_without_public_url_the_message_points_to_the_app(client, monkeypatch):
    monkeypatch.delenv("PUBLIC_URL", raising=False)
    p = person(client)
    recorded_checkin(client, monkeypatch, p)
    alert = next(a for a in store.alerts(p["id"]) if a["kind"] == "recording")
    assert alert["message"].endswith("Open the app to listen to it.") and not alert["delivered"]


def test_sharing_off_sends_nothing_and_closes_links(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://example.test")
    p = person(client)
    first = recorded_checkin(client, monkeypatch, p, "2026-10-19")
    key = store.get_checkin(first["checkin_id"])["listen_key"]
    assert client.get(f"/listen/{first['checkin_id']}/{key}").status_code == 200

    assert client.patch(f"/people/{p['id']}", json={"share_recordings": False}).json()["share_recordings"] is False
    assert client.get(f"/listen/{first['checkin_id']}/{key}").status_code == 404
    rec = client.get(f"/checkins/{first['checkin_id']}/recording").json()
    assert rec["shared"] is False and all(x["audio"] is None for x in rec["parts"])

    recorded_checkin(client, monkeypatch, p, "2026-10-20")
    assert [a["date"] for a in store.alerts(p["id"]) if a["kind"] == "recording"] == ["2026-10-19"]


def test_typed_checkins_send_no_recording(client):
    p = person(client)
    plan = client.get(f"/people/{p['id']}/today", params={"date_override": "2026-10-19"}).json()
    r = client.post(f"/people/{p['id']}/checkins", data={"answers": typed(plan), "date_override": "2026-10-19"})
    assert r.status_code == 200
    assert not [a for a in store.alerts(p["id"]) if a["kind"] == "recording"]


def test_live_message_goes_out_by_text(client, monkeypatch):
    monkeypatch.setenv("NOTIFY_LIVE", "1")
    sent = []
    monkeypatch.setattr(notify, "_sms", lambda phone, body: sent.append((phone, body)) or True)
    monkeypatch.setattr(notify, "_push", lambda token, title, body: False)
    p = person(client)
    recorded_checkin(client, monkeypatch, p)
    assert sent and sent[0][0] == "+15555550100" and "just finished today's check-in" in sent[0][1]
    assert next(a for a in store.alerts(p["id"]) if a["kind"] == "recording")["delivered"] == 1
