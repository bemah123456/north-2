"""Gemini for words, the judge and the unusual-speech note, with Gemini
mocked: nothing here touches the network."""

import base64
import json
import sys
import time
import types

import httpx
import numpy as np
import pytest

from checkin import change as C
from checkin import gemini, judge, transcribe
from checkin.exercises import build_checkin
from checkin.scoring import score_checkin

from test_api import client, person, typed  # noqa: F401  (client is a fixture)
from test_faster_whisper import FakeModel
from test_scoring import DAY, PERSON, answers, history

GEMINI_ENV = ("GEMINI_API_KEY", "GEMINI_BACKEND", "GEMINI_MODEL", "GEMINI_TRANSCRIBE", "GEMINI_SPEECH_NOTE",
              "GEMINI_TIMEOUT_S", "GEMINI_THINKING_LEVEL", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION",
              "JUDGE_ENABLED", "JUDGE_ENGINE")


@pytest.fixture(autouse=True)
def no_gemini_env(monkeypatch):
    for k in GEMINI_ENV:
        monkeypatch.delenv(k, raising=False)


class FakeGemini:
    """Stands in for httpx.post inside gemini.py and records each request."""

    def __init__(self, reply=None, fail=None, delay=0.0):
        self.reply, self.fail, self.delay, self.calls = reply or {}, fail, delay, []

    def __call__(self, url, headers=None, json=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "body": json, "timeout": timeout})
        if self.delay:
            time.sleep(self.delay)
        if self.fail:
            raise self.fail
        text = self.reply if isinstance(self.reply, str) else __import__("json").dumps(self.reply)
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": text}]}}]},
                              request=httpx.Request("POST", url))

    def prompt(self, i=-1):
        return " ".join(p["text"] for p in self.calls[i]["body"]["contents"][0]["parts"] if "text" in p)

    def audio(self, i=-1):
        return [p["inlineData"] for p in self.calls[i]["body"]["contents"][0]["parts"] if "inlineData" in p]


def whisper(monkeypatch):
    """Local faster-whisper, faked: says "It's 2026." with timings."""
    monkeypatch.setenv("STT_PROVIDER", "local")
    monkeypatch.setenv("LOCAL_WHISPER_ENGINE", "faster-whisper")
    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=FakeModel))
    monkeypatch.setattr(transcribe, "_faster_model", None)
    monkeypatch.setattr(transcribe, "_decode_16k", lambda audio: np.zeros(16000, dtype=np.float32))
    monkeypatch.setattr(FakeModel, "prob", 0.95)
    monkeypatch.setattr(FakeModel, "logprob", -0.2)


def fake(monkeypatch, **kw):
    g = FakeGemini(**kw)
    monkeypatch.setattr(gemini.httpx, "post", g)
    return g


# 1. Words from Gemini, timings from Whisper

def test_off_by_default_sends_nothing(monkeypatch):
    whisper(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")  # a key alone turns nothing on
    g = fake(monkeypatch, reply={"transcript": "nope"})
    d = transcribe.transcribe_detail(b"clip", "audio/m4a")
    assert d["transcript"] == "It's 2026." and "transcript_by" not in d
    assert g.calls == []
    assert gemini.status()["transcribe"] is False


def test_gemini_words_with_whisper_timings(monkeypatch):
    whisper(monkeypatch)
    monkeypatch.setenv("GEMINI_TRANSCRIBE", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    g = fake(monkeypatch, reply={"transcript": "  Uh, it's 2026.  "})
    d = transcribe.transcribe_detail(b"clip", "audio/m4a", transcribe.MONTHS_BACKWARDS)

    assert d["transcript"] == "Uh, it's 2026." and d["transcript_by"] == "gemini"
    assert d["timing_transcript"] == "It's 2026."
    assert [(w.text, w.start, w.end) for w in d["words"]] == [("It's", 0.2, 0.5), ("2026.", 0.5, 1.4)]
    assert d["unsure"] is False and d["confidence"]["words"] == 2  # Whisper's doubt still reported
    assert 0 < d["agreement"] < 1

    call = g.calls[0]
    assert call["url"] == ("https://generativelanguage.googleapis.com/v1beta/models/"
                           "gemini-3.6-flash:generateContent")
    assert call["headers"] == {"x-goog-api-key": "test-key"}
    config = call["body"]["generationConfig"]
    assert config["temperature"] == 0 and config["responseMimeType"] == "application/json"
    assert list(config["responseSchema"]["properties"]) == ["transcript"]
    assert config["thinkingConfig"] == {"thinkingLevel": "low"}
    # No expected answer and nothing about the person: a transcription instruction only.
    assert g.prompt() == gemini.TRANSCRIBE_PROMPT
    assert "December" not in json.dumps(call["body"]) and FakeModel.calls[-1]["initial_prompt"]  # only Whisper is primed
    clip = g.audio()[0]
    assert clip["mimeType"] == "audio/wav" and base64.b64decode(clip["data"])[:4] == b"RIFF"


def test_model_doubt_still_works_with_gemini_words(monkeypatch):
    whisper(monkeypatch)
    monkeypatch.setenv("GEMINI_TRANSCRIBE", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    fake(monkeypatch, reply={"transcript": "It's 2026."})
    monkeypatch.setattr(FakeModel, "prob", 0.5)
    d = transcribe.transcribe_detail(b"clip", "audio/m4a")
    assert d["unsure"] is True and d["transcript_by"] == "gemini" and d["agreement"] == 1.0


@pytest.mark.parametrize("trouble", [
    {"fail": httpx.ConnectError("down")},
    {"reply": "not json"},
    {"reply": {"something": "else"}},
])
def test_any_gemini_failure_keeps_whispers_transcript(monkeypatch, trouble):
    whisper(monkeypatch)
    monkeypatch.setenv("GEMINI_TRANSCRIBE", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    fake(monkeypatch, **trouble)
    d = transcribe.transcribe_detail(b"clip", "audio/m4a")
    assert d["transcript"] == "It's 2026." and "transcript_by" not in d and len(d["words"]) == 2


def test_http_error_falls_back(monkeypatch):
    whisper(monkeypatch)
    monkeypatch.setenv("GEMINI_TRANSCRIBE", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini.httpx, "post", lambda url, **kw: httpx.Response(
        429, json={"error": {}}, request=httpx.Request("POST", url)))
    assert transcribe.transcribe_detail(b"clip", "audio/m4a")["transcript"] == "It's 2026."


def test_slow_gemini_times_out_to_whisper(monkeypatch):
    whisper(monkeypatch)
    monkeypatch.setenv("GEMINI_TRANSCRIBE", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_TIMEOUT_S", "0.2")
    fake(monkeypatch, reply={"transcript": "too late"}, delay=1.0)
    t = time.monotonic()
    d = transcribe.transcribe_detail(b"clip", "audio/m4a")
    assert d["transcript"] == "It's 2026." and time.monotonic() - t < 0.8


def test_latest_aliases_are_refused(monkeypatch):
    whisper(monkeypatch)
    monkeypatch.setenv("GEMINI_TRANSCRIBE", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-flash-latest")
    g = fake(monkeypatch, reply={"transcript": "x"})
    assert transcribe.transcribe_detail(b"clip", "audio/m4a")["transcript"] == "It's 2026."
    assert g.calls == [] and gemini.status()["refused_model"] is True


def test_vertex_is_preferred_and_uses_credentials(monkeypatch):
    whisper(monkeypatch)
    monkeypatch.setenv("GEMINI_TRANSCRIBE", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "clari-prod")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "europe-west4")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    monkeypatch.setattr(gemini, "_access_token", lambda: "adc-token")
    g = fake(monkeypatch, reply={"transcript": "It's 2026."})
    assert transcribe.transcribe_detail(b"clip", "audio/m4a")["transcript_by"] == "gemini"
    assert g.calls[0]["url"] == ("https://europe-west4-aiplatform.googleapis.com/v1/projects/clari-prod/"
                                 "locations/europe-west4/publishers/google/models/gemini-2.5-flash:generateContent")
    assert g.calls[0]["headers"] == {"Authorization": "Bearer adc-token"}
    assert g.calls[0]["body"]["generationConfig"]["thinkingConfig"] == {"thinkingBudget": 0}
    monkeypatch.setenv("GEMINI_BACKEND", "developer")
    assert gemini.backend() == "developer"


def test_vertex_token_from_the_metadata_server(monkeypatch):
    monkeypatch.setitem(sys.modules, "google", None)  # google-auth not installed
    monkeypatch.setattr(gemini, "_token", {})
    asked = []

    def fake_get(url, headers=None, timeout=None):
        asked.append(headers)
        return httpx.Response(200, json={"access_token": "md-token", "expires_in": 3599},
                              request=httpx.Request("GET", url))

    monkeypatch.setattr(gemini.httpx, "get", fake_get)
    assert gemini._access_token() == "md-token" and gemini._access_token() == "md-token"
    assert asked == [{"Metadata-Flavor": "Google"}]  # cached until it expires


def test_speech_note_alone_keeps_whispers_words(monkeypatch):
    whisper(monkeypatch)
    monkeypatch.setenv("GEMINI_SPEECH_NOTE", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    g = fake(monkeypatch, reply={"unusual_rating": 7, "unusual_reason": "long pauses"})
    d = transcribe.transcribe_detail(b"clip", "audio/m4a")
    assert d["transcript"] == "It's 2026." and "transcript_by" not in d
    assert d["speech_note"] == {"rating": 3, "reason": "long pauses"}  # clamped to 0-3
    assert g.prompt() == gemini.NOTE_ONLY_PROMPT


def test_words_and_note_come_from_one_call(monkeypatch):
    whisper(monkeypatch)
    monkeypatch.setenv("GEMINI_TRANSCRIBE", "1")
    monkeypatch.setenv("GEMINI_SPEECH_NOTE", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    g = fake(monkeypatch, reply={"transcript": "it's 2026", "unusual_rating": 0, "unusual_reason": "clear"})
    d = transcribe.transcribe_detail(b"clip", "audio/m4a")
    assert len(g.calls) == 1 and d["transcript"] == "it's 2026" and d["speech_note"]["rating"] == 0
    assert set(g.calls[0]["body"]["generationConfig"]["responseSchema"]["required"]) == {
        "transcript", "unusual_rating", "unusual_reason"}


# 2. The Gemini audio judge, still only for answers the rules can't settle

def test_gemini_judge_listens_to_the_answer(monkeypatch):
    monkeypatch.setenv("JUDGE_ENABLED", "1")
    monkeypatch.setenv("JUDGE_ENGINE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(transcribe, "_decode_16k", lambda audio: np.zeros(16000, dtype=np.float32))
    g = fake(monkeypatch, reply={"heard": "in my kitchen at home", "correct": True, "reason": "at home"})
    v = judge.judge_answer("Where are you right now?", "in the kitchen", "The person is at home", b"clip")
    assert v == {"correct": True, "reason": "at home", "heard": "in my kitchen at home", "by": "gemini"}
    assert len(g.audio()) == 1 and "The person is at home" in g.prompt()
    assert "in the kitchen" not in g.prompt()  # it listens; the transcript is what the rules couldn't settle


def test_gemini_judge_failure_leaves_it_for_a_person(monkeypatch):
    monkeypatch.setenv("JUDGE_ENABLED", "1")
    monkeypatch.setenv("JUDGE_ENGINE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    fake(monkeypatch, fail=httpx.ReadTimeout("slow"))
    assert judge.judge_answer("Where are you?", "kitchen", "at home", None) is None
    fake(monkeypatch, reply={"heard": "x", "correct": "maybe", "reason": ""})
    assert judge.judge_answer("Where are you?", "kitchen", "at home", None) is None


def test_scoring_sends_only_unsure_answers_with_their_audio(monkeypatch):
    monkeypatch.setenv("JUDGE_ENABLED", "1")
    monkeypatch.setenv("JUDGE_ENGINE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(transcribe, "_decode_16k", lambda audio: np.zeros(16000, dtype=np.float32))
    g = fake(monkeypatch, reply={"heard": "in the kitchen", "correct": True, "reason": "kitchen is at home"})
    given = answers(DAY, {"place": "in the kitchen"})
    for v in given.values():
        v["audio"] = b"clip"
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY), given, [])
    place = next(i for i in r["items"] if i["kind"] == "place")
    assert place["correct"] is True and place["checked_by"] == "gemini"
    assert r["needs_review"] == 0
    assert len(g.calls) == 1  # the rules settled every other answer


def test_claude_stays_the_default_judge(monkeypatch):
    monkeypatch.setenv("JUDGE_ENABLED", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    g = fake(monkeypatch, reply={})
    monkeypatch.setattr(judge, "_claude", lambda q, a, f: {"correct": False, "reason": "no"})
    assert judge.judge_answer("q", "a", "f", b"clip") == {"correct": False, "reason": "no", "by": "claude"}
    assert g.calls == []


# 3. The unusual-speech note can add to other evidence but never alarm alone

def test_speech_note_alone_cannot_call_the_doctor():
    # The worst possible note, on a day nothing else moved.
    e = {"answers": 0.0, "digits": 0.0, "speed": 0.0, "voice": 0.0, "drowsy": 0.0, "evening": 0.0,
         "speech_note": C.speech_note_evidence(3)}
    assert e["speech_note"] == C.SPEECH_NOTE_CAP == 1.0
    assert C.combine(e)["level"] == "usual" and C.combine(e)["total"] == 0
    # Every answer rated 3 on an otherwise healthy day, through the whole scoring.
    given = answers(DAY, pause_every=8)
    for v in given.values():
        v["speech_note"] = {"rating": 3, "reason": "slurred"}
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY), given, history())
    assert r["change"]["evidence"]["speech_note"] == 1.0
    assert r["change"]["level"] == "usual" and r["band"] == "unlikely" and r["total"] == 0
    assert r["headline"] != "Call their doctor today"
    assert not any("unusual" in x for x in r["reasons"])


def test_speech_note_never_counts_as_a_second_kind():
    # One strong kind of evidence plus the maximum note: the total passes 4.5
    # but a big change needs two kinds besides the note.
    e = {"answers": 3.0, "drowsy": 0.75, "speech_note": 1.0}
    out = C.combine(e)
    assert out["total"] == 4.75 and out["level"] == "some"


def test_speech_note_adds_no_more_than_the_rest():
    assert C.combine({"drowsy": 0.75, "speech_note": 1.0})["total"] == 1.5
    assert C.combine({"answers": 1.5, "speech_note": 1.0})["level"] == "some"  # it can tip existing evidence
    assert C.combine({"answers": 1.5, "speech_note": 1.0}, noisy=True)["total"] == 2.0  # halved with a TV on


def test_ordinary_hesitation_adds_nothing():
    assert C.speech_note_evidence(None) == 0 and C.speech_note_evidence(1) == 0
    assert C.speech_note_evidence(2) == 0.5 and C.speech_note_evidence(3) == 1.0


# End to end through the API, with Whisper and Gemini both faked

def test_checkin_end_to_end_with_gemini(client, monkeypatch):
    from checkin import api

    whisper(monkeypatch)
    for k in ("GEMINI_TRANSCRIBE", "GEMINI_SPEECH_NOTE", "JUDGE_ENABLED"):
        monkeypatch.setenv(k, "1")
    monkeypatch.setenv("JUDGE_ENGINE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(transcribe, "clip_check", lambda data: {"heard_speech": True, "noisy": False})
    monkeypatch.setattr(api, "_heard", {})
    g = fake(monkeypatch, reply={"transcript": "twenty twenty six", "unusual_rating": 1, "unusual_reason": "fine"})
    p = person(client)
    plan = client.get(f"/people/{p['id']}/today", params={"date_override": "2026-10-19"}).json()
    rest = [a for a in json.loads(typed(plan)) if a["exercise_id"] != "year"]
    r = client.post(f"/people/{p['id']}/checkins", data={"answers": json.dumps(rest), "date_override": "2026-10-19"},
                    files={"audio_year": ("a.m4a", b"year", "audio/m4a")})
    assert r.status_code == 200, r.text
    year = next(i for i in r.json()["items"] if i["exercise_id"] == "year")
    assert year["transcript"] == "twenty twenty six" and year["transcript_by"] == "gemini"
    assert year["correct"] is True and year["speech_note"]["rating"] == 1 and "latency_s" in year
    assert r.json()["band"] == "unlikely" and len(g.calls) == 1
    h = client.get("/health").json()["gemini"]
    assert h == {"backend": "developer", "model": "gemini-3.6-flash", "transcribe": True, "speech_note": True,
                 "judge": True, "refused_model": False}
    assert "test-key" not in json.dumps(h)
