"""Letting the family hear the check-in.

When a check-in with recorded answers is saved, the family gets a message
that it's done, with its result and a private link that plays the whole
check-in: each question, then their answer, in order. Hearing the answer
helps when the app may have misheard ("got the year wrong" when they
clearly said 2026). It never changes the result, and the page says so,
because delirium comes and goes and one answer that sounds fine isn't the
whole picture.

The link works without the app (it's meant for a text message), so each
check-in gets its own random key. Turning sharing off in the family view,
or deleting the recordings, makes the link stop working.

PUBLIC_URL is the server's address as phones reach it (e.g. the Cloudflare
tunnel address). Without it the message says to open the app instead.
"""

from __future__ import annotations

import html
import os
import secrets

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from . import notify, store


def public_url() -> str | None:
    url = (os.environ.get("PUBLIC_URL") or "").strip().rstrip("/")
    return url or None


def parts(checkin: dict) -> list[dict]:
    """The check-in in the order it was asked, with which answers have a
    recording."""
    out = []
    for item in checkin["result"].get("items", []):
        out.append({
            "exercise_id": item["exercise_id"],
            "prompt": item["prompt"],
            "transcript": item.get("transcript", ""),
            "correct": item.get("correct"),
            "correct_items": item.get("correct_items"),
            "out_of": item.get("out_of"),
            "has_audio": store.audio_path(checkin["id"], item["exercise_id"]) is not None,
        })
    return out


def link(cid: str, key: str) -> str | None:
    base = public_url()
    return f"{base}/listen/{cid}/{key}" if base else None


def message(person: dict, result: dict, session: str, url: str | None) -> str:
    name = person["name"]
    if session == "evening":
        done = f"{name} just finished their evening check-in."
    else:
        done = f"{name} just finished today's check-in: {result['headline']}."
    if url:
        return f"{done} Listen to it here: {url}"
    return f"{done} Open the app to listen to it."


def after_checkin(person: dict, cid: str, result: dict, day: str, session: str, now_iso: str) -> dict | None:
    """Tell the family the check-in is done and give them a way to hear it.
    Does nothing when sharing is off or no answer was recorded (typed
    answers in the web demo)."""
    if not person.get("share_recordings"):
        return None
    checkin = store.get_checkin(cid)
    if not checkin or not any(p["has_audio"] for p in parts(checkin)):
        return None
    key = store.set_listen_key(cid, secrets.token_urlsafe(16))
    kind = "evening_recording" if session == "evening" else "recording"
    action = {"person_id": person["id"], "date": day, "kind": kind, "to": "family",
              "title": "Check-in done", "message": message(person, result, session, link(cid, key))}
    delivered = notify.send(person, action)
    store.record_alert(person["id"], day, kind, now_iso, delivered, action["message"])
    return action | {"delivered": delivered}


router = APIRouter()


def _shared(cid: str) -> tuple[dict, dict]:
    checkin = store.get_checkin(cid)
    if not checkin:
        raise HTTPException(404, "No such check-in")
    person = store.get_person(checkin["person_id"])
    return checkin, person


def recording(cid: str) -> dict:
    """For the family view in the app (behind the API token)."""
    checkin, person = _shared(cid)
    shared = bool(person.get("share_recordings"))
    return {
        "checkin_id": cid,
        "date": checkin["local_date"],
        "session": checkin["session"],
        "shared": shared,
        "parts": [p | {"audio": f"/checkins/{cid}/audio/{p['exercise_id']}" if shared and p["has_audio"] else None}
                  for p in parts(checkin)],
    }


def _by_key(cid: str, key: str) -> tuple[dict, dict]:
    checkin = store.get_checkin(cid)
    stored = checkin.get("listen_key") if checkin else None
    if not stored or not secrets.compare_digest(stored, key):
        raise HTTPException(404, "This link doesn't work. It may have been typed wrong or turned off.")
    person = store.get_person(checkin["person_id"])
    if not person.get("share_recordings"):
        raise HTTPException(404, "The family turned off sharing recordings.")
    return checkin, person


@router.get("/listen/{cid}/{key}/{exercise_id}")
def listen_audio(cid: str, key: str, exercise_id: str) -> FileResponse:
    _by_key(cid, key)
    path = store.audio_path(cid, exercise_id)
    if not path:
        raise HTTPException(404, "No recording")
    return FileResponse(path)


@router.get("/listen/{cid}/{key}", response_class=HTMLResponse)
def listen_page(cid: str, key: str) -> str:
    checkin, person = _by_key(cid, key)
    return page(person, checkin, parts(checkin), f"/listen/{cid}/{key}")


def _answer_note(p: dict) -> str:
    if p["out_of"]:
        return f"{p['correct_items']} of {p['out_of']} in order"
    return {True: "scored right", False: "scored wrong"}.get(p["correct"], "")


def page(person: dict, checkin: dict, items: list[dict], base: str) -> str:
    """A plain page that plays the whole check-in: the question is read by
    the browser, then their recorded answer plays."""
    e = html.escape
    name = e(person["name"])
    result = checkin["result"]
    when = "evening check-in" if checkin["session"] == "evening" else "check-in"
    rows = []
    for i, p in enumerate(items):
        audio = (f'<audio preload="none" controls src="{e(base)}/{e(p["exercise_id"])}"></audio>'
                 if p["has_audio"] else '<p class="none">No recording for this one.</p>')
        note = _answer_note(p)
        rows.append(
            f'<li data-i="{i}" data-prompt="{e(p["prompt"])}">'
            f'<p class="q">{e(p["prompt"])}</p>{audio}'
            f'<p class="heard">The app heard: "{e(p["transcript"]) or "(no answer)"}"'
            f'{f" <span>({e(note)})</span>" if note else ""}</p></li>')
    headline = "" if checkin["session"] == "evening" else \
        f'<p class="result">Result: <b>{e(result["headline"])}</b></p>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>{name}'s {when}, {e(checkin["local_date"])}</title>
<style>
:root{{--bg:#F4F8FB;--card:#fff;--text:#0F2236;--muted:#3A4B5E;--primary:#1A457D;--on-primary:#fff;--line:#D3DEE8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0E1A28;--card:#16263A;--text:#EAF1F8;--muted:#B5C3D2;--primary:#8FC2F0;--on-primary:#0E1A28;--line:#2B3E55}}}}
body{{margin:0;background:var(--bg);color:var(--text);font:20px/1.5 -apple-system,system-ui,sans-serif}}
.brand{{display:flex;align-items:center;gap:10px;margin:0 0 18px;font-weight:800;font-size:22px;color:var(--primary)}}
.brand i{{width:28px;height:28px;border-radius:50%;background:#3694A1}}
main{{max-width:640px;margin:0 auto;padding:24px 16px 48px}}
h1{{font-size:30px;line-height:1.2;margin:0 0 8px}}
.result{{margin:0 0 16px}} .muted{{color:var(--muted);font-size:17px}}
button{{font:inherit;font-weight:800;width:100%;padding:18px;border-radius:18px;border:0;background:var(--primary);color:var(--on-primary);cursor:pointer}}
ol{{list-style:none;padding:0;margin:20px 0}} li{{background:var(--card);border:2px solid var(--line);border-radius:18px;padding:14px 16px;margin-bottom:12px}}
li.now{{border-color:var(--primary)}} .q{{font-weight:700;margin:0 0 8px}} audio{{width:100%}}
.heard{{color:var(--muted);font-size:17px;margin:8px 0 0}} .none{{color:var(--muted);margin:0}}
</style></head><body><main>
<p class="brand"><i aria-hidden="true"></i>Clari</p>
<h1>{name}'s {when}</h1>
<p class="muted">{e(checkin["local_date"])}</p>
{headline}
<button id="all" type="button">&#9654; Play the whole {when}</button>
<ol id="parts">{"".join(rows)}</ol>
<p class="muted">Hearing an answer that sounds fine doesn't cancel the result. Confusion can come and go,
so if you're worried, call their doctor. Screening only, not a diagnosis.</p>
</main>
<script>
(function(){{
  var btn=document.getElementById('all');
  var items=[].slice.call(document.querySelectorAll('#parts li')).filter(function(li){{return li.querySelector('audio');}});
  var playing=false, at=0;
  function stop(){{playing=false;btn.innerHTML='&#9654; Play the whole {when}';
    if(window.speechSynthesis)speechSynthesis.cancel();
    items.forEach(function(li){{li.classList.remove('now');var a=li.querySelector('audio');if(a)a.pause();}});}}
  function next(){{
    if(!playing)return; if(at>=items.length){{stop();return;}}
    var li=items[at++]; items.forEach(function(x){{x.classList.toggle('now',x===li);}});
    li.scrollIntoView({{behavior:'smooth',block:'center'}});
    var a=li.querySelector('audio');
    function answer(){{ if(!playing)return; if(!a){{next();return;}} a.currentTime=0; a.onended=next; a.onerror=next;
      var p=a.play(); if(p&&p.catch)p.catch(next); }}
    if(window.speechSynthesis){{var u=new SpeechSynthesisUtterance(li.dataset.prompt);u.rate=0.9;
      u.onend=answer;u.onerror=answer;speechSynthesis.speak(u);}} else answer();
  }}
  btn.addEventListener('click',function(){{ if(playing){{stop();return;}} playing=true;at=0;btn.textContent='Stop';next(); }});
}})();
</script></body></html>"""
