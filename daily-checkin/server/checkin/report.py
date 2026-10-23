"""The day 9 numbers: how the test with real families went.

  python -m checkin.report            # Markdown, ready for the evidence slide
  GET /reports/testing                # the same numbers as JSON

Targets come from the plan's "What to measure" table.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from statistics import mean

from . import store
from .missed import local_now

TARGETS = {
    "completion_rate": 0.80,
    "hand_agreement": 0.90,
    "avg_duration_s": 180,
    "avg_ease": 4.0,
}


def _hand_number(hand: str) -> int | None:
    """The count in a hand score such as "4" or "4 in order"; None when
    there isn't one, so a stray word skips the row instead of the report."""
    m = re.search(r"\d+", hand)
    return int(m.group()) if m else None


def _attention_score(kind: str, correct_items: int) -> int:
    needed = {"months_backwards": 7, "days_backwards": 5, "countdown_20": 12}[kind]
    return 0 if correct_items >= needed else 1 if correct_items > 0 else 2


def hand_agreement(checkins: list[dict], hands: dict[str, dict[str, str]]) -> dict:
    """Compare the app's verdict on each answer with the team's own scoring.
    Orientation answers are marked right/wrong; attention answers with the
    number of items said in the right order, compared on the 4AT score."""
    agree = disagree = unsure = 0
    misses = []
    for c in checkins:
        marks = hands.get(c["id"], {})
        for item in c["result"]["items"]:
            hand = marks.get(item["exercise_id"], "").strip().lower()
            if not hand:
                continue
            if item["part"] == "orientation":
                hand_ok = hand in ("right", "correct", "yes", "1", "true")
                app_ok = item.get("correct")
                if app_ok is None:
                    unsure += 1
                    continue
                same = app_ok == hand_ok
            elif item["kind"] == "digit_span":
                if item.get("misheard"):
                    unsure += 1
                    continue
                n = _hand_number(hand)
                if n is None:
                    continue
                same = item["correct_items"] == n
            elif item["part"] == "attention":
                n = _hand_number(hand)
                if n is None:
                    continue
                same = item["score"] == _attention_score(item["kind"], n)
            else:
                continue
            if same:
                agree += 1
            else:
                disagree += 1
                misses.append({"checkin_id": c["id"], "exercise_id": item["exercise_id"],
                               "transcript": item["transcript"], "hand": hand})
    scored = agree + disagree
    return {"answers_compared": scored, "agree": agree, "app_unsure": unsure,
            "rate": agree / scored if scored else None, "disagreements": misses}


def testing_report(now_utc: datetime | None = None) -> dict:
    now_utc = now_utc or datetime.now(timezone.utc)
    hands = store.hand_scores()
    people = []
    all_checkins = []
    evenings = []
    for p in store.all_people():
        today = local_now(now_utc, p["timezone"]).date()
        cs = store.checkins(p["id"])
        all_checkins += cs
        evenings += store.checkins(p["id"], "evening")
        done = {date.fromisoformat(c["local_date"]) for c in cs}
        off = store.days_off(p["id"])
        start = date.fromisoformat(p["created_date"])
        # Today only counts once it's done; it isn't missed until it's over.
        due = [start + timedelta(days=i) for i in range((today - start).days)]
        due = [d for d in due if d not in off] + ([today] if today in done else [])
        people.append({
            "name": p["name"],
            "since": start.isoformat(),
            "days_due": len(due),
            "days_done": len([d for d in due if d in done]),
            "days_missed": len([d for d in due if d not in done]),
            "bands": [c["result"]["band"] for c in cs],
        })
    due_total = sum(x["days_due"] for x in people)
    done_total = sum(x["days_done"] for x in people)
    durations = [c["duration_s"] for c in all_checkins if c.get("duration_s")]
    # Evening check-ins are rated and hand-scored too; days and durations
    # stay about the morning one.
    both = all_checkins + evenings
    eases = [c["ease"] for c in both if c.get("ease")]
    family_alerts = [a for a in store.all_alerts() if a["kind"] in ("missed", "missed_pattern")]
    marked = [a for a in family_alerts if a["was_real"] is not None]
    bands = [c["result"]["band"] for c in all_checkins]
    return {
        "generated": now_utc.isoformat(timespec="minutes"),
        "people": people,
        "completion_rate": done_total / due_total if due_total else None,
        "checkins": len(all_checkins),
        "results": {b: bands.count(b) for b in ("unlikely", "possible_impairment", "possible_delirium")},
        "evening_checkins": len(evenings),
        "hand_agreement": hand_agreement(both, hands),
        # The room check's own flag, so home tests show how much a TV costs.
        "hand_agreement_by_room": {
            room: hand_agreement([c for c in both if bool(c["result"].get("noisy")) == (room == "noisy")], hands)
            for room in ("quiet", "noisy")
        },
        "avg_duration_s": mean(durations) if durations else None,
        "avg_ease": mean(eases) if eases else None,
        "ease_ratings": len(eases),
        "missed_alerts": {
            "sent": len(family_alerts),
            "family_answered": len(marked),
            "were_real": len([a for a in marked if a["was_real"]]),
            "notes": [a["family_note"] for a in marked if a["family_note"]],
        },
        "targets": TARGETS,
    }


def _pct(x):
    return "n/a" if x is None else f"{100 * x:.0f}%"


def to_markdown(r: dict) -> str:
    def hit(value, target, higher=True):
        if value is None:
            return "no data yet"
        return "met" if (value >= target if higher else value <= target) else "missed"

    h = r["hand_agreement"]
    m = r["missed_alerts"]
    dur = r["avg_duration_s"]
    lines = [
        f"# Testing results ({r['generated'][:10]})",
        "",
        f"{len(r['people'])} people, {r['checkins']} check-ins.",
        "",
        "| Measure | Result | Target | |",
        "| --- | --- | --- | --- |",
        f"| Days checked in | {_pct(r['completion_rate'])} | 80%+ | {hit(r['completion_rate'], 0.8)} |",
        f"| Agreement with hand scoring | {_pct(h['rate'])} of {h['answers_compared']} answers"
        f" ({h['app_unsure']} left for review) | 90%+ | {hit(h['rate'], 0.9)} |",
        *(f"| ... in a {room} room | {_pct(x['rate'])} of {x['answers_compared']} answers | 90%+ |"
          f" {hit(x['rate'], 0.9)} |" for room, x in r["hand_agreement_by_room"].items()),
        f"| Average check-in length | {'n/a' if dur is None else f'{dur / 60:.1f} min'} | under 3 min"
        f" | {hit(dur, 180, higher=False)} |",
        f"| Ease for the senior (Easy 5, OK 3, Hard 1) | {'n/a' if r['avg_ease'] is None else f'{r['avg_ease']:.1f} / 5'}"
        f" ({r['ease_ratings']} ratings) | 4+ | {hit(r['avg_ease'], 4.0)} |",
        f"| Missed check-in alerts | {m['sent']} sent, {m['were_real']} of {m['family_answered']} answered"
        f" were real | count them all | |",
        "",
        "| Person | Since | Done | Missed | Results |",
        "| --- | --- | --- | --- | --- |",
    ]
    for p in r["people"]:
        counts = ", ".join(f"{p['bands'].count(b)} {b.replace('_', ' ')}" for b in sorted(set(p["bands"])))
        lines.append(f"| {p['name']} | {p['since']} | {p['days_done']} of {p['days_due']} | {p['days_missed']} | {counts or '-'} |")
    if h["disagreements"]:
        lines += ["", "Answers where the app and the hand score differ:", ""]
        lines += [f"- \"{d['transcript']}\" (hand: {d['hand']})" for d in h["disagreements"][:20]]
    if m["notes"]:
        lines += ["", "What families said about missed check-in alerts:", ""]
        lines += [f"- {n}" for n in m["notes"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    import sys
    r = testing_report()
    print(json.dumps(r, indent=2) if "--json" in sys.argv else to_markdown(r))


if __name__ == "__main__":
    main()
