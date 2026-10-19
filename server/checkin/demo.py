"""Fill the local database with one demo senior for the video and judges:
five ordinary days, one missed day, then a confused day.

  python -m checkin.demo

The voices are simulated (word timings made up from the text), so the
demo shows the flow, not real accuracy.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from . import store
from .exercises import build_checkin
from .features import Word, checkin_features
from .missed import local_now
from .scoring import score_checkin

GOOD = {
    "greeting": "Good morning I slept well and my daughter is taking me to the garden center after lunch",
    "age": "I'm eighty two", "dob": "March fourteenth nineteen forty four",
    "place": "I'm at home in Springfield", "year": "it's twenty twenty six",
    "months_backwards": "December November October September August July June May April March February January",
    "days_backwards": "Sunday Saturday Friday Thursday Wednesday Tuesday Monday",
    "countdown_20": "twenty nineteen eighteen seventeen sixteen fifteen fourteen thirteen twelve eleven ten nine eight",
}
CONFUSED = {
    "greeting": "um I don't uh tired",
    "place": "I'm at the um the station I think",
    "year": "nineteen ninety",
    "months_backwards": "December November um October uh",
    "days_backwards": "Sunday um Saturday Friday",
    "countdown_20": "twenty nineteen uh eighteen",
}


def spoken(text: str, latency: float, wpm: float, pause_every: int, pause: float = 1.0) -> list[Word]:
    step, t, out = 60.0 / wpm, latency, []
    for i, w in enumerate(text.split()):
        if pause_every and i and i % pause_every == 0:
            t += pause
        out.append(Word(w, t, t + step * 0.8))
        t += step
    return out


def given_for(pid: str, day: date, texts: dict, **voice) -> dict:
    out = {}
    for ex in build_checkin(pid, day):
        key = ex.kind if ex.part == "attention" else ex.id
        text = texts.get(key, GOOD[key])
        out[ex.id] = {"transcript": text, "words": spoken(text, **voice)}
    return out


def main() -> None:
    tz = "America/New_York"
    today = local_now(datetime.now(timezone.utc), tz).date()
    start = today - timedelta(days=6)
    p = store.create_person({
        "name": "Grandma Rose", "birth_date": "1944-03-14", "timezone": tz, "checkin_time": "09:00",
        "place_keywords": ["home", "Springfield"], "family_name": "Sam",
    }, start)
    history = []
    for i in range(7):
        day = start + timedelta(days=i)
        if i == 5:
            continue  # the missed day
        confused = i == 6
        given = given_for(
            p["id"], day, CONFUSED if confused else {},
            latency=4.5 if confused else 1.1 + 0.15 * (i % 3),
            wpm=72 if confused else 128 + 5 * (i % 3),
            pause_every=2 if confused else 8, pause=2.0 if confused else 0.8,
        )
        result = score_checkin(p, day, build_checkin(p["id"], day), given, history)
        feats = checkin_features({k: v["words"] for k, v in given.items()})
        store.add_checkin(p["id"], day, datetime.now(timezone.utc).isoformat(), 9.2 + 0.1 * i,
                          result, feats, None)
        if result["band"] != "possible_delirium":
            history.append(feats)
        print(day, result["headline"], "|", "; ".join(result["reasons"]) or "-")
    print(f"\nDemo person id: {p['id']}  (database: {store.DB_PATH})")


if __name__ == "__main__":
    main()
