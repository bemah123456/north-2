import json
import sys
import types

from test_api import client, person, typed  # noqa: F401  (client is a fixture)

from checkin import assistant


def ask(client, p, message, history=None):
    r = client.post(f"/people/{p['id']}/ask", json={"message": message, "history": history or []})
    assert r.status_code == 200, r.text
    return r.json()


def test_built_in_answers_without_claude(client, monkeypatch):
    monkeypatch.delenv("ASSISTANT_ENABLED", raising=False)
    p = person(client)
    a = ask(client, p, "What is the 4AT?")
    assert a["source"] == "guide" and "4AT" in a["reply"] and "4 or more" in a["reply"]
    assert "Red means 4 or more" in ask(client, p, "what do the colours mean")["reply"]
    evening = ask(client, p, "What does the evening check-in do?")
    assert evening["suggestions"] == [{"setting": "evening_checkin", "value": "on", "label": "Turn on the evening check-in"}]
    assert "911" in ask(client, p, "She fell and is bleeding")["reply"]
    assert "I can explain" in ask(client, p, "hello")["reply"]


def test_red_day_says_call_the_doctor(client, monkeypatch):
    monkeypatch.delenv("ASSISTANT_ENABLED", raising=False)
    p = person(client)
    today = p["created_date"]  # their first day (tomorrow if set up late in the day)
    plan = client.get(f"/people/{p['id']}/today", params={"date_override": today}).json()
    # Wrong year, wrong age, no months: a red day.
    answers = typed(plan, {"year": "1990", "age": "fifty", "months_backwards": "I don't know",
                           "days_backwards": "I don't know", "countdown_20": "I don't know", "place": "the station"})
    client.post(f"/people/{p['id']}/checkins", data={"answers": answers, "date_override": today})
    client.post(f"/checkins/{client.get(f'/people/{p['id']}/days').json()['days'][0]['checkin_id']}/family-report",
                json={"different": True})
    reply = ask(client, p, "Should I be worried today?")["reply"]
    assert "call their doctor today" in reply


def test_claude_answer_and_only_safe_suggestions(client, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLED", "1")
    seen = {}

    class FakeMessages:
        def create(self, **kw):
            seen.update(kw)
            payload = {"reply": "Turn on the evening check-in.", "suggestions": [
                {"setting": "evening_checkin", "value": "on", "label": "Turn it on"},
                {"setting": "evening_time", "value": "23:30", "label": "Too late"},
                {"setting": "checkin_time", "value": "10:00", "label": "Remind at 10"},
            ]}
            return types.SimpleNamespace(stop_reason="end_turn",
                                         content=[types.SimpleNamespace(type="text", text=json.dumps(payload))])

    fake = types.SimpleNamespace(Anthropic=lambda: types.SimpleNamespace(beta=types.SimpleNamespace(messages=FakeMessages())),
                                 APIConnectionError=Exception, APIStatusError=Exception)
    monkeypatch.setitem(sys.modules, "anthropic", fake)
    p = person(client)
    a = ask(client, p, "She gets muddled in the evenings", [{"role": "assistant", "text": "Hi!"}, {"role": "user", "text": "hi"},
                                                            {"role": "assistant", "text": "Hello"}])
    assert a["source"] == "claude"
    assert [s["setting"] for s in a["suggestions"]] == ["evening_checkin", "checkin_time"]  # 23:30 dropped
    assert seen["model"] == "claude-opus-5-5" and seen["messages"][0]["role"] == "user"
    assert "Mom" in seen["system"][1]["text"] and "4AT" in seen["system"][0]["text"]


def test_claude_failure_falls_back_to_guide(client, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLED", "1")
    monkeypatch.setattr(assistant, "_ask_claude", lambda *a: None)
    p = person(client)
    assert ask(client, p, "What is the 4AT?")["source"] == "guide"


def test_ask_limits(client):
    p = person(client)
    assert client.post(f"/people/{p['id']}/ask", json={"message": ""}).status_code == 422
    assert client.post(f"/people/{p['id']}/ask", json={"message": "x" * 1001}).status_code == 422
    assert client.post("/people/nobody/ask", json={"message": "hi"}).status_code == 404


def test_red_day_still_answers_other_questions():
    p = {"name": "Rose", "birth_date": "1944-03-14", "place_keywords": ["home"], "checkin_time": "09:00",
         "evening_checkin": False, "evening_time": "19:00", "share_recordings": True}
    red = [{"date": "2026-10-21", "status": "possible_delirium", "headline": "Call their doctor today", "score": 10, "reasons": []}]
    evening = assistant._ask_guide(p, red, "What does the evening check-in do?")
    assert evening["reply"].startswith("The evening check-in") and "call their doctor today" in evening["reply"]
    assert evening["suggestions"][0]["setting"] == "evening_checkin"
    assert assistant._ask_guide(p, red, "Is Mom OK?")["reply"].startswith("Today's result for Rose is red")
