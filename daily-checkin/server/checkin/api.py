"""HTTP API the app talks to.

Run locally:  uvicorn checkin.api:app --reload --port 8000
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field, field_validator

from . import listen, notify, report, store, transcribe
from .baseline import load_model
from .change import duration_z
from .exercises import build_checkin, build_session
from .features import FEATURE_DIRECTIONS
from .missed import FAMILY_ALERT_MIN, day_statuses, due_actions, is_late, local_now
from .scoring import apply_evening, finalize, retry_reason, score_checkin, score_evening, words_from_json

DEMO_MODE = os.environ.get("DEMO_MODE") == "1"

log = logging.getLogger(__name__)

app = FastAPI(title="Daily check-in")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(listen.router)  # the family's private listening links


def auth(authorization: str | None = Header(default=None)) -> None:
    token = os.environ.get("API_TOKEN")
    if token and authorization != f"Bearer {token}":
        raise HTTPException(401, "Missing or wrong API token")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def person_or_404(pid: str) -> dict:
    p = store.get_person(pid)
    if not p:
        raise HTTPException(404, "No such person")
    return p


# A 24-hour clock time, 00:00 to 23:59.
CLOCK = r"^([01]\d|2[0-3]):[0-5]\d$"


def _check_timezone(tz: str) -> None:
    try:
        ZoneInfo(tz)
    except Exception:
        raise HTTPException(422, f"Unknown time zone {tz}")


def _check_birth_date(d: date | None) -> date | None:
    """Their real date of birth: Clari checks their answers against it, so a
    typo would mark them wrong every day."""
    if d is not None and not (date(1900, 1, 1) <= d <= date.today()):
        raise ValueError("Birth date should be a real date in the past, like 1944-03-14")
    return d


class PersonIn(BaseModel):
    name: str = Field(min_length=1, description="What the family calls them, e.g. Mom")
    birth_date: date
    check_birth = field_validator("birth_date")(_check_birth_date)
    timezone: str = "America/New_York"
    checkin_time: str = Field("09:00", pattern=CLOCK)
    place_keywords: list[str] = Field(default_factory=list,
                                      description="Accepted answers to 'where are you', e.g. home, Springfield")
    family_name: str | None = None
    family_phone: str | None = None
    senior_push_token: str | None = None
    family_push_token: str | None = None
    share_recordings: bool = Field(True, description="Send the family each check-in's recording when it's done")
    evening_checkin: bool = Field(False, description="A shorter second check-in in the evening, compared with the morning")
    evening_time: str = Field("19:00", pattern=CLOCK)


class PersonPatch(BaseModel):
    name: str | None = Field(None, min_length=1)
    birth_date: date | None = None
    check_birth = field_validator("birth_date")(_check_birth_date)
    timezone: str | None = None
    checkin_time: str | None = Field(None, pattern=CLOCK)
    place_keywords: list[str] | None = None
    family_name: str | None = None
    family_phone: str | None = None
    senior_push_token: str | None = None
    family_push_token: str | None = None
    share_recordings: bool | None = None
    evening_checkin: bool | None = None
    evening_time: str | None = Field(None, pattern=CLOCK)


class FamilyReport(BaseModel):
    different: bool


class Ease(BaseModel):
    rating: int = Field(ge=1, le=5)


class AlertFeedback(BaseModel):
    date: date
    kind: str
    was_real: bool
    note: str | None = None


class DayOff(BaseModel):
    date: date
    off: bool = True


@app.get("/health")
def health() -> dict:
    model = load_model()
    return {
        "ok": True,
        "speech_to_text": transcribe.provider() or "none (typed answers only)",
        "notifications_live": notify.live(),
        "model": {k: model[k] for k in ("trained_on", "synthetic", "n_rows", "held_out_people_auc")},
    }


@app.post("/people", dependencies=[Depends(auth)])
def create_person(body: PersonIn) -> dict:
    _check_timezone(body.timezone)
    data = body.model_dump()
    data["birth_date"] = body.birth_date.isoformat()
    now = local_now(utcnow(), body.timezone)
    first_day = now.date()
    # Set up after today's family alert would have gone out: today can't
    # count as missed, so their first day is tomorrow.
    alert_at = datetime.combine(first_day, time.fromisoformat(body.checkin_time), now.tzinfo) \
        + timedelta(minutes=FAMILY_ALERT_MIN)
    if now >= alert_at:
        first_day += timedelta(days=1)
    return store.create_person(data, first_day)


@app.get("/people/{pid}", dependencies=[Depends(auth)])
def get_person(pid: str) -> dict:
    return person_or_404(pid)


@app.patch("/people/{pid}", dependencies=[Depends(auth)])
def patch_person(pid: str, body: PersonPatch) -> dict:
    person_or_404(pid)
    if body.timezone is not None:
        _check_timezone(body.timezone)
    changes = body.model_dump(exclude_none=True)
    if "birth_date" in changes:
        changes["birth_date"] = changes["birth_date"].isoformat()
    return store.update_person(pid, changes)


def _local_day(person: dict, override: str | None) -> tuple[date, datetime]:
    now = local_now(utcnow(), person["timezone"])
    if override:
        if not DEMO_MODE:
            raise HTTPException(400, "Setting the date is only allowed in demo mode")
        try:
            d = date.fromisoformat(override)
        except ValueError:
            raise HTTPException(400, "date_override is a date like 2026-10-20")
        return d, now.replace(year=d.year, month=d.month, day=d.day)
    return now.date(), now


def _answer_day(person: dict, form) -> tuple[date, datetime]:
    """The day answers are for. The app sends plan_date, the day its
    questions were built for, so a check-in that runs past midnight is
    scored against them and not the next day's."""
    day, now = _local_day(person, form.get("date_override"))
    planned = form.get("plan_date")
    if planned and not form.get("date_override"):
        try:
            planned = date.fromisoformat(planned)
        except ValueError:
            raise HTTPException(400, "plan_date is a date like 2026-10-20")
        if planned == day - timedelta(days=1):
            day = planned
    return day, now


EVENING_OPENS_EARLY_MIN = 60


def _done(pid: str, day: date, session: str) -> bool:
    return any(c["local_date"] == day.isoformat() for c in store.checkins(pid, session))


def _session(value, p: dict, day: date) -> str:
    """Which check-in an answer belongs to. The evening one only exists when
    the family turned it on and the morning one is done."""
    session = value or "morning"
    if session not in ("morning", "evening"):
        raise HTTPException(400, "session is morning or evening")
    if session == "evening" and not (p["evening_checkin"] and _done(p["id"], day, "morning")):
        raise HTTPException(409, "The evening check-in is off, or the morning one isn't done yet")
    return session


@app.get("/people/{pid}/today", dependencies=[Depends(auth)])
def today_plan(pid: str, date_override: str | None = None, session: str | None = None) -> dict:
    """The next check-in to do today. Once the morning one is done, and if
    the family turned it on, the evening one opens an hour before its time.
    `session=evening` asks for the evening one whatever the time."""
    p = person_or_404(pid)
    day, now = _local_day(p, date_override)
    morning_done = _done(pid, day, "morning")
    evening_at = p["evening_time"] if p["evening_checkin"] else None
    if session == "evening" or (morning_done and evening_at):
        opens = datetime.combine(day, time.fromisoformat(p["evening_time"]), now.tzinfo) \
            - timedelta(minutes=EVENING_OPENS_EARLY_MIN)
        if session == "evening" or now >= opens:
            _session("evening", p, day)
            return {"date": day.isoformat(), "session": "evening", "evening_at": evening_at,
                    "already_done": _done(pid, day, "evening"),
                    "exercises": [e.to_dict() for e in build_session(pid, day, "evening")]}
    return {
        "date": day.isoformat(),
        "session": "morning",
        "evening_at": evening_at,
        "already_done": morning_done,
        "exercises": [e.to_dict() for e in build_checkin(pid, day)],
    }


# Recent transcriptions by clip, so an answer checked during the check-in
# isn't transcribed a second time when the whole check-in arrives.
_heard: dict[str, dict] = {}


# An empty or broken clip is an answer nobody heard, not a reason to lose
# the whole check-in.
NOTHING_HEARD = {"transcript": "", "words": [], "heard_speech": False, "noisy": False}


def _hear(ex, data: bytes, content_type: str | None) -> dict:
    if not data:
        return dict(NOTHING_HEARD)
    key = hashlib.sha256(ex.kind.encode() + data).hexdigest()
    if key not in _heard:
        try:
            expect = transcribe.MONTHS_BACKWARDS if ex.kind == "months_backwards" else None
            text, words = transcribe.transcribe(data, content_type, expect)
        except transcribe.UnreadableRecording:
            return dict(NOTHING_HEARD)
        except transcribe.TranscriptionUnavailable:
            raise HTTPException(503, "Speech-to-text isn't set up on the server yet; "
                                     "set STT_PROVIDER or use typed answers")
        heard = {"transcript": text, "words": words}
        heard.update(transcribe.clip_check(data) or {})
        if len(_heard) >= 200:
            _heard.pop(next(iter(_heard)))
        _heard[key] = heard
    return dict(_heard[key])


@app.post("/people/{pid}/answers/check", dependencies=[Depends(auth)])
async def check_answer(pid: str, request: Request) -> dict:
    """Multipart form: exercise_id and audio (one recorded answer). Says
    whether the app should ask the question again because the answer
    couldn't be made out, and whether another voice (a TV) seemed to be
    talking in the background. Nothing is saved."""
    p = person_or_404(pid)
    form = await request.form()
    day, _ = _answer_day(p, form)
    session = _session(form.get("session"), p, day)
    ex = next((e for e in build_session(pid, day, session) if e.id == form.get("exercise_id")), None)
    f = form.get("audio")
    if ex is None or f is None or isinstance(f, str):
        raise HTTPException(400, "Send exercise_id and audio")
    heard = _hear(ex, await f.read(), f.content_type)
    reason = retry_reason(ex, heard)
    return {"ask_again": reason is not None, "reason": reason, "noisy": bool(heard.get("noisy"))}


@app.post("/people/{pid}/checkins", dependencies=[Depends(auth)])
async def submit_checkin(pid: str, request: Request) -> dict:
    """Multipart form. Field `answers` is JSON: a list of
    {exercise_id, transcript?, words?}. Recorded audio goes in file fields
    named `audio_<exercise_id>` and is transcribed here. Typed answers
    (demo mode on the web) send a transcript and no words, so they are
    scored on content only. `session` is "evening" for the evening check-in."""
    p = person_or_404(pid)
    form = await request.form()
    day, now_local = _answer_day(p, form)
    session = _session(form.get("session"), p, day)
    if _done(pid, day, session):
        raise HTTPException(409, "Already checked in today")

    exercises = build_session(pid, day, session)
    given: dict[str, dict] = {}
    try:
        for a in json.loads(form.get("answers") or "[]"):
            given[a["exercise_id"]] = {"transcript": a.get("transcript") or "",
                                       "words": words_from_json(a.get("words"))}
    except (ValueError, TypeError, KeyError, AttributeError):
        raise HTTPException(400, "answers is a JSON list of {exercise_id, transcript?, words?}; "
                                 "each word has text, start and end")
    audio = {}
    for ex in exercises:
        f = form.get(f"audio_{ex.id}")
        if f is None or isinstance(f, str):
            continue
        data = await f.read()
        audio[ex.id] = (data, f.content_type or "audio/m4a", (f.filename or "a.m4a").rsplit(".", 1)[-1])
        given[ex.id] = _hear(ex, data, f.content_type)

    hour = now_local.hour + now_local.minute / 60
    duration = form.get("duration_s")
    try:
        duration = float(duration) if duration else None
    except ValueError:
        raise HTTPException(400, "duration_s is a number of seconds")
    if session == "evening":
        return _submit_evening(p, day, exercises, given, audio, hour, duration)

    previous = store.checkins(pid)
    usual = [c for c in previous
             if c["result"]["band"] != "possible_delirium" and not c["result"].get("noisy")]
    history = [c["features"] for c in usual if c["features"]]
    past = [c["result"].get("measures") for c in usual]
    family = form.get("family_says_different")
    family_flag = None if family in (None, "") else family in ("1", "true", "yes")
    yesterday = day - timedelta(days=1)
    routine = {
        "late": is_late([c["local_hour"] for c in previous], hour),
        "missed_yesterday": yesterday >= date.fromisoformat(p["created_date"])
        and not any(c["local_date"] == yesterday.isoformat() for c in previous)
        and yesterday not in store.days_off(pid),
        "duration_z": duration_z([c["duration_s"] for c in usual], duration),
    }
    result = score_checkin(p, day, exercises, given, history, family_flag, past, routine)
    late = "checked in much later in the day than usual"
    if routine["late"] and late not in result["reasons"]:
        result["reasons"].append(late)

    cid = store.add_checkin(pid, day, utcnow().isoformat(), hour, result, result["features"], family_flag,
                            duration)
    for ex_id, (data, _, ext) in audio.items():
        store.save_audio(cid, ex_id, data, ext)
    listen.after_checkin(p, cid, result, day.isoformat(), "morning", utcnow().isoformat())
    result["checkin_id"] = cid
    return result


def _submit_evening(p: dict, day: date, exercises, given: dict, audio: dict, hour: float,
                    duration: float | None) -> dict:
    """Score the evening against this morning, and add the comparison to
    the day's result, which is what the family sees."""
    pid = p["id"]
    morning = next(c for c in store.checkins(pid) if c["local_date"] == day.isoformat())
    ratios = [c["result"]["comparison"]["latency_ratio"] for c in store.checkins(pid, "evening")
              if c["result"].get("comparison", {}).get("latency_ratio")]
    evening = score_evening(p, day, exercises, given, morning["result"], ratios)
    cid = store.add_checkin(pid, day, utcnow().isoformat(), hour, evening, evening["features"], None,
                            duration, session="evening")
    for ex_id, (data, _, ext) in audio.items():
        store.save_audio(cid, ex_id, data, ext)
    store.update_checkin_result(morning["id"], apply_evening(morning["result"], cid, evening))
    listen.after_checkin(p, cid, evening, day.isoformat(), "evening", utcnow().isoformat())
    evening["checkin_id"] = cid
    evening["session"] = "evening"
    return evening


def apply_family_report(result: dict, different: bool) -> dict:
    """Re-score the acute-change item after the family answers."""
    result = json.loads(json.dumps(result))
    result["family_says_different"] = different
    return finalize(result)


@app.post("/checkins/{cid}/family-report", dependencies=[Depends(auth)])
def family_report(cid: str, body: FamilyReport) -> dict:
    c = store.get_checkin(cid)
    if not c:
        raise HTTPException(404, "No such check-in")
    result = apply_family_report(c["result"], body.different)
    store.update_checkin_result(cid, result, body.different)
    return result | {"checkin_id": cid}


@app.get("/checkins/{cid}", dependencies=[Depends(auth)])
def get_checkin(cid: str) -> dict:
    c = store.get_checkin(cid)
    if not c:
        raise HTTPException(404, "No such check-in")
    return c["result"] | {"checkin_id": cid}


@app.get("/people/{pid}/days", dependencies=[Depends(auth)])
def days(pid: str) -> dict:
    """The family view: one row per day since they joined, newest first."""
    p = person_or_404(pid)
    now = local_now(utcnow(), p["timezone"])
    results = {}
    for c in store.checkins(pid):
        results[date.fromisoformat(c["local_date"])] = c["result"] | {"checkin_id": c["id"]}
    since = min([date.fromisoformat(p["created_date"]), *results.keys()])
    last = max([now.date(), *results.keys()])
    rows = day_statuses(since, last, results, store.days_off(pid), now, p["checkin_time"])
    return {"person": p, "days": rows, "alerts": store.alerts(pid)[:20]}


@app.post("/people/{pid}/days-off", dependencies=[Depends(auth)])
def day_off(pid: str, body: DayOff) -> dict:
    person_or_404(pid)
    store.set_day_off(pid, body.date, body.off)
    return {"date": body.date.isoformat(), "off": body.off}


@app.delete("/people/{pid}/recordings", dependencies=[Depends(auth)])
def delete_recordings(pid: str) -> dict:
    person_or_404(pid)
    return {"deleted_files": store.delete_recordings(pid)}


@app.post("/jobs/missed-checkins", dependencies=[Depends(auth)])
def missed_job(now: str | None = None) -> dict:
    """Run every 5 to 15 minutes (Supabase cron, a GitHub Action, or any
    scheduler). Sends each reminder or alert once."""
    if now and not DEMO_MODE:
        raise HTTPException(400, "Setting the time is only allowed in demo mode")
    now_utc = datetime.fromisoformat(now) if now else utcnow()
    out = []
    errors = []
    for p in store.all_people():
        done = {date.fromisoformat(c["local_date"]) for c in store.checkins(p["id"])}
        try:
            actions = due_actions(p, now_utc, done, store.days_off(p["id"]), store.sent_alerts(p["id"]))
        except Exception as e:  # one bad setting mustn't stop everyone else's alerts
            log.exception("missed check-in job failed for %s", p["id"])
            errors.append({"person_id": p["id"], "error": str(e)})
            continue
        for action in actions:
            delivered = False if action.get("skipped") else notify.send(p, action)
            store.record_alert(p["id"], action["date"], action["kind"], now_utc.isoformat(),
                               delivered, action["message"])
            out.append(action | {"delivered": delivered})
    return {"actions": out, "errors": errors, "notifications_live": notify.live()}


@app.get("/export/features.csv", dependencies=[Depends(auth)], response_class=PlainTextResponse)
def export_features() -> str:
    """Rows for `python -m checkin.train --csv`. Fill in the label column
    ("normal" or "off") by hand before training."""
    buf = io.StringIO()
    w = csv.writer(buf)
    names = list(FEATURE_DIRECTIONS)
    w.writerow(["person_id", "date", "label", *names])
    for p in store.all_people():
        for c in store.checkins(p["id"]):
            if c["features"]:
                w.writerow([p["id"], c["local_date"], "", *(round(c["features"][k], 4) for k in names)])
    return buf.getvalue()


@app.post("/checkins/{cid}/ease", dependencies=[Depends(auth)])
def ease(cid: str, body: Ease) -> dict:
    """The senior's answer to "How easy was that?" (1 to 5)."""
    if not store.get_checkin(cid):
        raise HTTPException(404, "No such check-in")
    store.set_ease(cid, body.rating)
    return {"rating": body.rating}


@app.post("/people/{pid}/alerts/feedback", dependencies=[Depends(auth)])
def alert_feedback(pid: str, body: AlertFeedback) -> dict:
    """The family's answer to "was this missed check-in a real concern?"."""
    if not store.set_alert_feedback(pid, body.date.isoformat(), body.kind, body.was_real, body.note):
        raise HTTPException(404, "No such alert")
    return {"ok": True}


@app.get("/checkins/{cid}/recording", dependencies=[Depends(auth)])
def recording(cid: str) -> dict:
    """The whole check-in for the family to listen to: each question in
    order, what the app heard, and where its recording is."""
    return listen.recording(cid)


@app.get("/checkins/{cid}/audio/{exercise_id}", dependencies=[Depends(auth)])
def audio(cid: str, exercise_id: str) -> FileResponse:
    path = store.audio_path(cid, exercise_id)
    if not path:
        raise HTTPException(404, "No recording")
    return FileResponse(path)


HAND_COLUMNS = ["checkin_id", "person", "date", "exercise_id", "kind", "prompt", "transcript",
                "app_says", "noisy_room", "recording", "file", "hand_score"]


@app.get("/export/hand-scoring.csv", dependencies=[Depends(auth)], response_class=PlainTextResponse)
def export_hand_scoring(request: Request) -> str:
    """One row per answer for the team to score by ear. In hand_score write
    "right" or "wrong" for orientation answers, and for the backwards task
    the number of items said in the right order. Leave rows you skip blank,
    then send the file back to POST /import/hand-scoring."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HAND_COLUMNS)
    done = store.hand_scores()
    base = str(request.base_url).rstrip("/")
    for p in store.all_people():
        for c in store.checkins(p["id"], None):
            for item in c["result"]["items"]:
                if item["part"] == "alertness":
                    continue
                if item["part"] == "orientation":
                    app_says = {True: "right", False: "wrong", None: "unsure"}[item.get("correct")]
                else:
                    app_says = f"{item['correct_items']} in order"
                path = store.audio_path(c["id"], item["exercise_id"])
                w.writerow([c["id"], p["name"], c["local_date"], item["exercise_id"], item["kind"],
                            item["prompt"], item["transcript"], app_says,
                            "yes" if c["result"].get("noisy") else "no",
                            f"{base}/checkins/{c['id']}/audio/{item['exercise_id']}" if path else "",
                            str(path) if path else "",  # opens on the server's computer, no token needed
                            done.get(c["id"], {}).get(item["exercise_id"], "")])
    return buf.getvalue()


@app.post("/import/hand-scoring", dependencies=[Depends(auth)])
async def import_hand_scoring(request: Request) -> dict:
    """Body: the CSV from /export/hand-scoring.csv with hand_score filled in."""
    text = (await request.body()).decode("utf-8-sig")
    per: dict[str, dict[str, str]] = {}
    for row in csv.DictReader(io.StringIO(text)):
        value = (row.get("hand_score") or "").strip()
        if value:
            per.setdefault(row["checkin_id"], {})[row["exercise_id"]] = value
    for cid, values in per.items():
        if store.get_checkin(cid):
            store.set_hand_scores(cid, values)
    return {"checkins": len(per), "answers": sum(len(v) for v in per.values())}


@app.get("/reports/testing", dependencies=[Depends(auth)])
def testing_report(format: str = "json"):
    r = report.testing_report()
    return PlainTextResponse(report.to_markdown(r)) if format == "md" else r
