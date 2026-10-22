from test_api import client, person  # noqa: F401  (client is a fixture)


def test_family_can_fix_their_birth_date(client):
    p = person(client)
    r = client.patch(f"/people/{p['id']}", json={"birth_date": "1944-03-15", "place_keywords": ["home", "Rochester"]})
    assert r.status_code == 200, r.text
    assert r.json()["birth_date"] == "1944-03-15" and r.json()["place_keywords"] == ["home", "Rochester"]


def test_birth_date_must_be_real_and_past(client):
    for bad in ("2099-01-01", "1850-05-05", "1944-02-30"):
        r = client.post("/people", json={"name": "Mom", "birth_date": bad})
        assert r.status_code == 422, bad
    p = person(client)
    assert client.patch(f"/people/{p['id']}", json={"birth_date": "2099-01-01"}).status_code == 422
    assert client.patch(f"/people/{p['id']}", json={"name": ""}).status_code == 422
