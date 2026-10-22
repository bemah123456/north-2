from test_api import client, person, typed  # noqa: F401  (client is a fixture)


def checkin(client, p, day, overrides=None):
    plan = client.get(f"/people/{p['id']}/today", params={"date_override": day}).json()
    r = client.post(f"/people/{p['id']}/checkins", data={"answers": typed(plan, overrides), "date_override": day})
    assert r.status_code == 200, r.text
    return r.json()


def test_days_carry_score_and_notes(client):
    p = person(client)
    checkin(client, p, "2026-10-19")
    bad = checkin(client, p, "2026-10-20", {"year": "1990", "age": "fifty"})
    assert client.put(f"/people/{p['id']}/notes/2026-10-20", json={"text": "  Started antibiotics  "}).json()["note"] \
        == "Started antibiotics"
    rows = {r["date"]: r for r in client.get(f"/people/{p['id']}/days").json()["days"]}
    assert rows["2026-10-19"]["score"] == 0 and rows["2026-10-19"]["unsure"] is False
    assert rows["2026-10-20"]["score"] == bad["total"] > 0
    assert rows["2026-10-20"]["note"] == "Started antibiotics" and rows["2026-10-19"]["note"] == ""
    client.put(f"/people/{p['id']}/notes/2026-10-20", json={"text": ""})
    rows = {r["date"]: r for r in client.get(f"/people/{p['id']}/days").json()["days"]}
    assert rows["2026-10-20"]["note"] == ""


def test_note_needs_a_real_date(client):
    p = person(client)
    assert client.put(f"/people/{p['id']}/notes/2026-02-30", json={"text": "x"}).status_code == 422
    assert client.put("/people/nobody/notes/2026-02-01", json={"text": "x"}).status_code == 404
