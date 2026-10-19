"""HTTP API the app talks to.

Run locally:  uvicorn checkin.api:app --reload --port 8000
"""

from __future__ import annotations

import csv
import io
import json
import os
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from . import notify, store, transcribe
from .baseline import load_model
from .exercises import build_checkin
from .features import FEATURE_DIRECTIONS
from .missed import day_statuses, due_actions, is_late, local_now
from .scoring import HEADLINES, score_checkin, words_from_json

DEMO_MODE = os.environ.get("DEMO_MODE") == "1"

app = FastAPI(title="Daily check-in")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


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


class PersonIn(BaseModel):
    name: str = Field(description="What the family calls them, e.g. Mom")
    birth_date: date
    timezone: str = "America/New_York"
    checkin_time: str = Field("09:00", pattern=r"^\d{2}:\d{2}$")
    place_keywords: list[str] = Field(default_factory=list,
                                      description="Accepted answers to 'where are you', e.g. home, Springfield")
    family_name: str | None = None
    family_phone: str | None = None
    senior_push_token: str | None = None
    family_push_token: str | None = None


class PersonPatch(BaseModel):
    name: str | None = None
    timezone: str | None = None
    checkin_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    place_keywords: list[str] | None = None
    family_name: str | None = None
    family_phone: str | None = None
    senior_push_token: str | None = None
    family_push_token: str | None = None


class FamilyReport(BaseModel):
    different: bool


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
    try:
        ZoneInfo(body.timezone)
    except Exception:
        raise HTTPException(422, f"Unknown time zone {body.timezone}")
    data = body.model_dump()
    data["birth_date"] = body.birth_date.isoformat()
    today = local_now(utcnow(), body.timezone).date()
    return store.create_person(data, today)


@app.get("/people/{pid}", dependencies=[Depends(auth)])
def get_person(pid: str) -> dict:
    return person_or_404(pid)


@app.patch("/people/{pid}", dependencies=[Depends(auth)])
def patch_person(pid: str, body: PersonPatch) -> dict:
    person_or_404(pid)
    return store.update_person(pid, body.model_dump(exclude_none=True))


def _local_day(person: dict, override: str | None) -> tuple[date, datetime]:
    now = local_now(utcnow(), person["timezone"])
    if override:
        if not DEMO_MODE:
            raise HTTPException(400, "Setting the date is only allowed in demo mode")
        d = date.fromisoformat(override)
        return d, now.replace(year=d.year, month=d.month, day=d.day)
    return now.date(), now


@app.get("/people/{pid}/today", dependencies=[Depends(auth)])
def today_plan(pid: str, date_override: str | None = None) -> dict:
    p = person_or_404(pid)
    day, _ = _local_day(p, date_override)
    done = any(c["local_date"] == day.isoformat() for c in store.checkins(pid))
    return {
        "date": day.isoformat(),
        "already_done": done,
        "exercises": [e.to_dict() for e in build_checkin(pid, day)],
    }


@app.post("/people/{pid}/checkins", dependencies=[Depends(auth)])
async def submit_checkin(pid: str, request: Request) -> dict:
    """Multipart form. Field `answers` is JSON: a list of
    {exercise_id, transcript?, words?}. Recorded audio goes in file fields
    named `audio_<exercise_id>` and is transcribed here. Typed answers
    (demo mode on the web) send a transcript and no words, so they are
    scored on content only."""
    p = person_or_404(pid)
    form = await request.form()
    day, now_local = _local_day(p, form.get("date_override"))
    if any(c["local_date"] == day.isoformat() for c in store.checkins(pid)):
        raise HTTPException(409, "Already checked in today")

    exercises = build_checkin(pid, day)
    given: dict[str, dict] = {}
    for a in json.loads(form.get("answers") or "[]"):
        given[a["exercise_id"]] = {"transcript": a.get("transcript", ""),
                                   "words": words_from_json(a.get("words"))}
    audio = {}
    for ex in exercises:
        f = form.get(f"audio_{ex.id}")
        if f is None or isinstance(f, str):
            continue
        data = await f.read()
        audio[ex.id] = (data, f.content_type or "audio/m4a", (f.filename or "a.m4a").rsplit(".", 1)[-1])
        try:
            text, words = transcribe.transcribe(data, f.content_type)
        except transcribe.TranscriptionUnavailable:
            raise HTTPException(503, "Speech-to-text isn't set up on the server yet; "
                                     "set STT_PROVIDER or use typed answers")
        given[ex.id] = {"transcript": text, "words": words}

    previous = store.checkins(pid)
    history = [c["features"] for c in previous
               if c["features"] and c["result"]["band"] != "possible_delirium"]
    family = form.get("family_says_different")
    family_flag = None if family in (None, "") else family in ("1", "true", "yes")
    result = score_checkin(p, day, exercises, given, history, family_flag)

    hour = now_local.hour + now_local.minute / 60
    if is_late([c["local_hour"] for c in previous], hour):
        result["reasons"].append("checked in much later in the day than usual")

    cid = store.add_checkin(pid, day, utcnow().isoformat(), hour, result, result["features"], family_flag)
    for ex_id, (data, _, ext) in audio.items():
        store.save_audio(cid, ex_id, data, ext)
    result["checkin_id"] = cid
    return result


def apply_family_report(result: dict, different: bool) -> dict:
    """Re-score the acute-change item after the family answers."""
    reason = "family says they seem different today"
    result = json.loads(json.dumps(result))
    voice_change = (result["voice"]["change_probability"] or 0) >= 0.7
    result["reasons"] = [r for r in result["reasons"] if r != reason]
    if different:
        result["reasons"].insert(0, reason)
    result["parts"]["acute_change"] = 4 if (different or voice_change) else 0
    result["total"] = sum(result["parts"].values())
    t = result["total"]
    result["band"] = "possible_delirium" if t >= 4 else "possible_impairment" if t >= 1 else "unlikely"
    result["headline"] = HEADLINES[result["band"]]
    return result


@app.post("/checkins/{cid}/family-report", dependencies=[Depends(auth)])
def family_report(cid: str, body: FamilyReport) -> dict:
    c = store.get_checkin(cid)
    if not c:
        raise HTTPException(404, "No such check-in")
    result = apply_family_report(c["result"], body.different)
    store.update_checkin_result(cid, result, body.different)
    return result


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
    for p in store.all_people():
        done = {date.fromisoformat(c["local_date"]) for c in store.checkins(p["id"])}
        for action in due_actions(p, now_utc, done, store.days_off(p["id"]), store.sent_alerts(p["id"])):
            delivered = False if action.get("skipped") else notify.send(p, action)
            store.record_alert(p["id"], action["date"], action["kind"], now_utc.isoformat(),
                               delivered, action["message"])
            out.append(action | {"delivered": delivered})
    return {"actions": out, "notifications_live": notify.live()}


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
