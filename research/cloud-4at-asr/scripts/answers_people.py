"""Spoken 4AT answers for six made-up people, so the scoring is tested on
more ages, birthdays, places and years than the one person in answers_set.

Check-in day: 21 October 2026. Each person has 3 healthy wordings of each
orientation answer and 2 impaired ones; months backwards reuses the main
set's healthy and impaired answers.
"""

from datetime import date

from num2words import num2words

from answers_set import HEALTHY as BASE_HEALTHY, IMPAIRED as BASE_IMPAIRED

DAY = "2026-10-21"
PEOPLE = [
    {"id": "p1", "birth_date": "1931-07-02", "town": "Leeds"},
    {"id": "p2", "birth_date": "1938-11-23", "town": "Glasgow"},
    {"id": "p3", "birth_date": "1941-02-28", "town": "Cork"},
    {"id": "p4", "birth_date": "1947-09-09", "town": "Phoenix"},
    {"id": "p5", "birth_date": "1950-12-31", "town": "Brighton"},
    {"id": "p6", "birth_date": "1955-05-17", "town": "Auckland"},
]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def year_words(y):
    return num2words(y, to="year")


def age_on(b, d):
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day))


def items_for(p):
    today = date.fromisoformat(DAY)
    b = date.fromisoformat(p["birth_date"])
    age = age_on(b, today)
    a, a1 = num2words(age), num2words(age + 1)
    mon, nxt = MONTHS[b.month - 1], MONTHS[b.month % 12]
    ordn = num2words(b.day, to="ordinal")
    yw = year_words(b.year)
    healthy = {
        "age": [f"I'm {a}.", f"{a} years old.", f"I'll be {a1} in {mon}, so {a}." if (b.month, b.day) > (today.month, today.day)
                else f"Um, I turned {a} in {mon}."],
        "dob": [f"{mon} the {ordn}, {yw}.", f"The {ordn} of {mon}, {yw}.", f"I was born on {mon} {num2words(b.day)}, {yw}."],
        "place": [f"I'm at home in {p['town']}.", "At home.", f"In my own house, in {p['town']}."],
        "year": ["It's twenty twenty six.", "Two thousand and twenty six.", "Twenty twenty six, I think."],
        "months_backwards": BASE_HEALTHY["months_backwards"][:3],
    }
    impaired = {
        "age": [f"I'm {num2words(age - 12)}.", f"{num2words(age + 9)}, I think."],
        "dob": [f"{nxt} the {ordn}, {year_words(b.year + 3)}.", f"I don't remember my birthday."],
        "place": ["I'm at the train station.", "I don't know where I am."],
        "year": ["Nineteen ninety eight.", "It's two thousand and ten."],
        "months_backwards": BASE_IMPAIRED["months_backwards"][:2],
    }
    out = []
    for label, tab in (("healthy", healthy), ("impaired", impaired)):
        for kind, texts in tab.items():
            for i, t in enumerate(texts):
                t = t[0].upper() + t[1:]
                out.append({"id": f"{p['id']}-{label}-{kind}-{i}", "person": p["id"], "label": label,
                            "kind": kind, "text": t})
    return out


def all_items():
    return [it for p in PEOPLE for it in items_for(p)]


if __name__ == "__main__":
    for it in all_items()[:30]:
        print(it["id"], "|", it["text"])
    print(len(all_items()))
