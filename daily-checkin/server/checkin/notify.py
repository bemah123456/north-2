"""Reminders to the senior and alerts to the family.

Nothing leaves the server unless NOTIFY_LIVE=1. Until then every message is
only recorded, which is what the demo and tests use. When live: push
notifications go through Expo's push service and family texts through
Twilio (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM).
"""

from __future__ import annotations

import os

import httpx


def live() -> bool:
    return os.environ.get("NOTIFY_LIVE") == "1"


def send(person: dict, action: dict) -> bool:
    """Returns True if the message was actually delivered somewhere."""
    if not live():
        return False
    if action["to"] == "senior":
        return _push(person.get("senior_push_token"), "Clari", action["message"])
    delivered = _push(person.get("family_push_token"), action.get("title", "Clari"), action["message"])
    return _sms(person.get("family_phone"), action["message"]) or delivered


def _push(token: str | None, title: str, body: str) -> bool:
    if not token:
        return False
    r = httpx.post("https://exp.host/--/api/v2/push/send",
                   json={"to": token, "title": title, "body": body, "sound": "default"}, timeout=20)
    return r.status_code == 200


def _sms(phone: str | None, body: str) -> bool:
    sid, auth, sender = (os.environ.get(k) for k in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM"))
    if not (phone and sid and auth and sender):
        return False
    r = httpx.post(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                   auth=(sid, auth), data={"To": phone, "From": sender, "Body": body}, timeout=20)
    return r.status_code in (200, 201)
