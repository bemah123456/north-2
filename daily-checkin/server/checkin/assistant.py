"""Ask Clari: the family's helper in the Messages tab.

Answers questions about how Clari works (the daily check-in, the 4AT, the
score and colours, each button and setting) and how to set it up for their
family, using the app guide below plus this person's settings and recent
days. It can suggest a settings change; the app shows it as a button and
nothing changes until the family taps it.

It explains the app; it doesn't give medical advice. Anything urgent goes to
emergency services, and a red day goes to their doctor.

Claude answers when ASSISTANT_ENABLED=1 and an Anthropic credential is set.
Otherwise, or if the call fails, built-in answers to the common questions
reply instead, so the tab always works. Turning Claude on sends the person's
name, settings and recent results to Anthropic's API; say so in the consent.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date

MODEL = os.environ.get("ASSISTANT_MODEL", "claude-opus-5-5")

# Models that accept the server-side refusal fallback. Claude Haiku 5.5
# doesn't, and sending it there is rejected; on such models a refusal simply
# falls back to the built-in answers.
FALLBACK_MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}

GUIDE = """\
ABOUT CLARI
Clari is a phone app that helps families notice delirium early in an older relative. Delirium is sudden
confusion, often caused by an infection (like a urinary tract infection), a new medicine, dehydration or a
hospital stay. It comes on over hours or days, can come and go during the day, and is usually treatable when
caught early. Clari is a screening aid, not a diagnosis.

THE DAILY CHECK-IN (on the older person's phone)
Once a day, at the reminder time, the older person taps one big button. Clari reads about 7 short questions
aloud and they answer by talking. It takes about 2 minutes. They only ever type the code the family gave them,
once, at setup. If the room is noisy Clari asks them to move somewhere quieter; if it couldn't hear an answer
it asks once more.

THE 4AT (what the questions are based on)
The 4AT is a short bedside test hospitals use to screen for delirium. It has four parts:
1. Alertness: are they awake and responding normally? Drowsy, very slow or no reply scores 4.
2. Orientation (AMT4): their age, date of birth, where they are, and the year. 0 mistakes scores 0, 1 mistake
   scores 1, 2 or more score 2. Clari checks the answers against the details the family entered.
3. Attention: months of the year backwards (on some days weekdays backwards or counting down from 20). Getting
   7 or more in order scores 0, fewer scores 1, not able to start scores 2.
4. Acute change or fluctuating course: scores 4 if the family says "they seem different", if the evening
   check-in was clearly worse than the morning, or if Clari sees a big change from their usual days.
A total of 4 or more suggests possible delirium. 1 to 3 suggests a possible problem worth watching.
Clari also gives a short digit-span task (four numbers said back backwards) every day.

COMPARED WITH THEIR USUAL
Delirium is a change, so Clari also compares each day with the person's own recent normal days: mistakes,
remembered digits, speed on the backwards task, their voice (pauses, "um"s, speaking speed, how much they say),
drowsiness signs (slow to start, long silences, a much shorter or longer check-in, checking in much later than
usual, missing yesterday) and a worse evening. A small change makes the day "Keep an eye on it". A big change
on at least two kinds of evidence counts as the 4AT's acute change. The voice alone can't raise the alarm.
It needs a few normal days first to learn what "usual" is.

THE FAMILY VIEW
- Bottom bar: Messages on the left (texts from Clari, and this chat), Home in the middle, Settings on the right.
- Home: today's result card (the score in a circle, the headline, a short line like "4 or more: call their
  doctor", the top reasons, and "See today's details"), then a month calendar.
- Calendar colours: red = score 4 or more, call their doctor. Yellow = score 1 to 3 (keep an eye on it), a
  missed check-in, or a normal score where some answers were hard to hear. Green = 0, their usual self.
  Grey = no check-in yet or a day off. The number on each day is that day's score.
- Tapping a day opens its details: the score, Clari's notes (the reasons), the recorded conversation (play the
  whole check-in or each answer), what they said with right / wrong / needs a person to check, the comparison
  with their usual, "Did they seem different?" (answering Yes counts toward the score), and "Your notes", a
  free-text note for that day that is useful to show their doctor.
- Messages: texts Clari sent the family. After a missed check-in it asks "Was this a real concern?"; answering
  helps Clari learn which alerts are useful.

SETTINGS
- Their details: what Clari checks (age, birthday, where they are, the year), the phone's connection code, and
  "Edit their details". A wrong birthday or place makes right answers look wrong, so fix mistakes here.
- Daily reminder time: when the older person is reminded (8, 9, 10 or 11 am). If they haven't checked in 3
  hours later, the family gets a text. Two missed days in a row sends a stronger text.
- Evening check-in (off by default): a one-minute second check-in in the evening (default 7 pm), compared with
  the morning. Useful because delirium often comes and goes and can be worse later in the day.
- Recordings (on by default, only with the older person's OK): the family can listen to each check-in.
- Day off: no reminders and no missed-check-in text for that day, e.g. a hospital appointment or a trip.
- Change setup: disconnects this phone from the family view.

WHAT TO DO
- Red day ("Call their doctor today"): call their doctor or nurse line today and mention sudden confusion or
  drowsiness. Listening to the recording first can help, but an answer that sounds fine does not cancel the
  result, because confusion can come and go.
- Emergencies (not breathing, chest pain, a serious fall, unconscious, signs of a stroke): call emergency
  services (911 in the US) now. Don't wait for Clari.
"""

RULES = """\
You are Clari's help assistant, chatting with a family member of an older person who uses Clari.
Answer questions about how Clari works and how to set it up for their family, using the guide and the
person's information below. Be warm, plain and brief: 1 to 4 short sentences, no headings, no bullet lists
unless asked. Use the person's name.

You explain the app; you do not diagnose or give medical advice. If they describe an emergency, tell them to
call emergency services now. If a recent day is red, or they are worried, tell them to call the doctor.
If you don't know something about the app, say so; don't invent features.

You may suggest settings changes when they would help (for example the evening check-in when confusion seems
worse later in the day, a different reminder time, or a day off for an appointment). Put them in
"suggestions" with a short button label; the family confirms by tapping. Only use these settings:
evening_checkin ("on" or "off"), evening_time ("17:00" to "21:00"), checkin_time ("08:00", "09:00", "10:00" or
"11:00"), share_recordings ("on" or "off"), day_off_tomorrow ("yes"). Leave suggestions empty otherwise.
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "setting": {"type": "string", "enum": ["evening_checkin", "evening_time", "checkin_time",
                                                           "share_recordings", "day_off_tomorrow"]},
                    "value": {"type": "string"},
                    "label": {"type": "string"},
                },
                "required": ["setting", "value", "label"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["reply", "suggestions"],
    "additionalProperties": False,
}

CHECKIN_TIMES = {"08:00", "09:00", "10:00", "11:00"}


def enabled() -> bool:
    return os.environ.get("ASSISTANT_ENABLED") == "1"


def valid_suggestion(s: dict) -> bool:
    """Only changes the app can actually make, with sensible values."""
    v = s.get("value", "")
    match s.get("setting"):
        case "evening_checkin" | "share_recordings":
            return v in ("on", "off")
        case "evening_time":
            return bool(re.fullmatch(r"(1[7-9]|2[01]):[0-5]\d", v)) and v <= "21:00"
        case "checkin_time":
            return v in CHECKIN_TIMES
        case "day_off_tomorrow":
            return v == "yes"
    return False


def person_context(person: dict, days: list[dict]) -> str:
    """Their settings and the last two weeks, newest first."""
    lines = [
        f"Name the family uses: {person['name']}",
        f"Birth date: {person['birth_date']}",
        f"Places that count as right for 'where are you': {', '.join(person['place_keywords']) or 'not set'}",
        f"Daily reminder: {person['checkin_time']}",
        f"Evening check-in: {'on at ' + person['evening_time'] if person.get('evening_checkin') else 'off'}",
        f"Recordings shared with family: {'on' if person.get('share_recordings') else 'off'}",
        f"Today: {date.today().isoformat()}",
        "Recent days (newest first):",
    ]
    for d in days[:14]:
        score = f", score {d['score']}" if d.get("score") is not None else ""
        reasons = "; ".join(d.get("reasons", [])[:4])
        note = f" Family note: {d['note']}" if d.get("note") else ""
        lines.append(f"- {d['date']}: {d['headline']}{score}{'. ' + reasons if reasons else ''}{note}")
    return "\n".join(lines)


def ask(person: dict, days: list[dict], message: str, history: list[dict]) -> dict:
    """{"reply", "suggestions", "source": "claude" | "guide"}."""
    if enabled():
        answer = _ask_claude(person, days, message, history)
        if answer:
            answer["suggestions"] = [s for s in answer["suggestions"] if valid_suggestion(s)]
            return answer | {"source": "claude"}
    return _ask_guide(person, days, message) | {"source": "guide"}


def _ask_claude(person: dict, days: list[dict], message: str, history: list[dict]) -> dict | None:
    import anthropic

    messages = [{"role": h["role"], "content": h["text"]} for h in history[-12:]
                if h.get("role") in ("user", "assistant") and h.get("text")]
    # The conversation must start with the family's own message.
    while messages and messages[0]["role"] != "user":
        messages.pop(0)
    messages.append({"role": "user", "content": message})
    fallback = {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"} if MODEL in FALLBACK_MODELS else {}
    try:
        response = anthropic.Anthropic().beta.messages.create(
            model=MODEL,
            max_tokens=4000,
            **fallback,
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
            # Stable guide first so it can be cached; the person's details change daily.
            system=[
                {"type": "text", "text": RULES + "\n" + GUIDE, "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": "THIS PERSON\n" + person_context(person, days)},
            ],
            messages=messages,
        )
    except (anthropic.APIConnectionError, anthropic.APIStatusError):
        return None
    if response.stop_reason in ("refusal", "max_tokens"):
        return None
    text = next((b.text for b in response.content if b.type == "text"), None)
    try:
        return json.loads(text) if text else None
    except json.JSONDecodeError:
        return None


# ---------- built-in answers (no Claude needed) ----------

URGENT = re.compile(r"\b(911|emergency|can'?t breathe|not breathing|chest pain|unconscious|passed out|"
                    r"stroke|seizure|fell|fall(en)?|bleeding)\b", re.I)

# "Should I be worried?", "What should I do?", "Is Mom OK?": on a red day these get a straight answer.
WORRIED = re.compile(r"worr|should i (call|be|do)|what should i do|scared|concern|\bis (she|he|they|mom|dad|mum)\b.*\b(ok|okay|alright|fine)\b", re.I)

FAQ: list[tuple[re.Pattern, str]] = [
    (re.compile(r"4\s?at|test|questions?|what (does|do) (it|clari) ask", re.I),
     "Clari's questions come from the 4AT, a 2-minute bedside test hospitals use for delirium. It checks four "
     "things: alertness, orientation (their age, birthday, where they are and the year), attention (months "
     "backwards) and sudden change. 4 or more points suggests possible delirium; 1 to 3 is worth watching."),
    (re.compile(r"colou?r|red|yellow|green|grey|gray|calendar|score|number", re.I),
     "Each day on the calendar shows that day's score. Red means 4 or more: call their doctor. Yellow means 1 "
     "to 3, a missed check-in, or some answers were hard to hear. Green means 0, their usual self. Grey means "
     "no check-in yet or a day off. Tap any day for its details."),
    (re.compile(r"evening", re.I),
     "The evening check-in is a one-minute second check-in, compared with the morning. Delirium often comes and "
     "goes and can be worse later in the day, so it can catch what one morning check-in misses. Turn it on in "
     "Settings."),
    (re.compile(r"record|listen|hear|play", re.I),
     "With their OK, you can listen to each check-in: open a day and tap Play the whole check-in, or Hear their "
     "answer under any answer. An answer that sounds fine doesn't cancel the result, since confusion comes and "
     "goes. You can turn recordings off in Settings."),
    (re.compile(r"remind|time|when", re.I),
     "They're reminded at their daily reminder time, and again an hour later. If they haven't checked in 3 hours "
     "after the reminder, you get a text. You can change the reminder time with Edit their details in Settings."),
    (re.compile(r"day off|away|trip|appointment|hospital", re.I),
     "If they'll be away, make tomorrow a day off in Settings: no reminders and no missed-check-in text that day."),
    (re.compile(r"detail|birthday|birth|wrong|place|city|edit|change", re.I),
     "Clari checks their answers against the details you entered: age, birthday, where they are and the year. "
     "If any of them are wrong, right answers will look wrong, so fix them with Edit their details in Settings."),
    (re.compile(r"note", re.I),
     "Open any day and use Your notes to write down things like a fall, a new medicine or a bad night. They're "
     "saved with that day and handy to show their doctor."),
    (re.compile(r"usual|baseline|compare|voice", re.I),
     "Clari compares each day with their own recent normal days: mistakes, remembered numbers, speed, their "
     "voice and drowsiness signs. It needs a few normal days first. The voice alone can never raise the alarm."),
    (re.compile(r"delirium|confus", re.I),
     "Delirium is sudden confusion, often from an infection, a new medicine, dehydration or a hospital stay. It "
     "comes on over hours or days and is usually treatable if caught early. Clari is a screening aid, not a "
     "diagnosis, so if you're worried, call their doctor."),
    (re.compile(r"missed|didn'?t check|messages?|text", re.I),
     "If they haven't checked in 3 hours after the reminder, Clari texts you; two missed days in a row sends a "
     "stronger text. In Messages you can say whether it was a real concern, which helps Clari learn."),
]


def _ask_guide(person: dict, days: list[dict], message: str) -> dict:
    name = person["name"]
    if URGENT.search(message):
        return {"reply": f"If {name} needs urgent help, call emergency services (911 in the US) now. Clari can't "
                         "help in an emergency. For sudden confusion that isn't an emergency, call their doctor today.",
                "suggestions": []}
    latest = days[0] if days else None
    red_today = bool(latest and latest.get("status") == "possible_delirium")
    if red_today and WORRIED.search(message):
        return {"reply": f"Today's result for {name} is red, so call their doctor today and mention sudden "
                         "confusion or drowsiness. You can listen to the check-in first, but an answer that sounds "
                         "fine doesn't cancel the result.", "suggestions": []}
    reply = ("I can explain anything in Clari: the daily check-in, the 4AT questions, what the colours and scores "
             "mean, recordings, notes, and each setting. Try asking about one of those.")
    suggestions: list[dict] = []
    for pattern, answer in FAQ:
        if pattern.search(message):
            reply = answer
            if pattern.pattern.startswith("evening") and not person.get("evening_checkin"):
                suggestions = [{"setting": "evening_checkin", "value": "on", "label": "Turn on the evening check-in"}]
            break
    if red_today:
        reply += f" And a reminder: today's result for {name} is red, so call their doctor today."
    return {"reply": reply, "suggestions": suggestions}
