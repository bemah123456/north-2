"""Spoken 4AT test answers for one made-up person.

Person: born 14 March 1944, aged 82 on 19 Oct 2026, at home in Springfield.
Each answer has the text the voice reads, the kind of check, and whether a
correct scorer should mark it right ("healthy") or wrong ("impaired").
"""

PERSON = {"birth_date": "1944-03-14", "place_keywords": ["home", "Springfield"]}
DAY = "2026-10-19"

HEALTHY = {
    "age": [
        "I'm eighty two.",
        "Eighty two years old.",
        "Um, I'm eighty two.",
        "I'll be eighty three in March, so eighty two.",
        "Let me think. Eighty two.",
    ],
    "dob": [
        "March fourteenth, nineteen forty four.",
        "The fourteenth of March, nineteen forty four.",
        "I was born on March the fourteenth, nineteen forty four.",
        "Uh, March fourteen, nineteen forty four.",
        "Fourteenth of March, forty four. Nineteen forty four.",
    ],
    "place": [
        "I'm at home.",
        "At home, in my living room.",
        "I'm in my house in Springfield.",
        "Well, I'm sitting at home.",
        "Home. My own home.",
    ],
    "year": [
        "It's twenty twenty six.",
        "Two thousand and twenty six.",
        "Twenty twenty six, I think.",
        "Um, it's twenty twenty six.",
        "The year is two thousand twenty six.",
    ],
    "months_backwards": [
        "December, November, October, September, August, July, June, May, April, March, February, January.",
        "December. November. October. September. August. July. June. May. April. March. February. January.",
        "December, November, um, October, September, August, uh, July, June, May, April, March, February, January.",
        "Okay. December, November, October, September, August, July, June, May.",
        "December, November, October, September, um, August, July, June, May, April.",
    ],
    "days_backwards": [
        "Sunday, Saturday, Friday, Thursday, Wednesday, Tuesday, Monday.",
        "Sunday. Saturday. Friday. Thursday. Wednesday. Tuesday. Monday.",
        "Sunday, Saturday, um, Friday, Thursday, Wednesday, Tuesday, Monday.",
    ],
    "countdown_20": [
        "Twenty, nineteen, eighteen, seventeen, sixteen, fifteen, fourteen, thirteen, twelve, eleven, ten, nine, eight, seven, six, five, four, three, two, one.",
        "Twenty. Nineteen. Eighteen. Seventeen. Sixteen. Fifteen. Fourteen. Thirteen. Twelve. Eleven. Ten. Nine. Eight.",
    ],
}

IMPAIRED = {
    "age": [
        "I'm sixty five.",
        "I don't know. Fifty?",
        "Ninety one.",
    ],
    "dob": [
        "June the second, nineteen fifty.",
        "March twentieth, nineteen sixty four.",
        "I don't remember.",
    ],
    "place": [
        "I don't know where I am.",
        "At the office. I have to get to work.",
        "On the train, I think.",
    ],
    "year": [
        "Nineteen eighty six.",
        "It's twenty twenty two.",
        "I'm not sure. What year is it?",
    ],
    "months_backwards": [
        "December, November, um, October. Uh. June? March.",
        "December, November, September, July.",
        "January, February, March, April.",
        "I can't do that.",
    ],
    "days_backwards": [
        "Sunday, Saturday, Thursday.",
        "Monday, Tuesday, Wednesday.",
    ],
    "countdown_20": [
        "Twenty, nineteen, eighteen, sixteen, twelve.",
    ],
}


def all_items():
    out = []
    for label, table in (("healthy", HEALTHY), ("impaired", IMPAIRED)):
        for kind, texts in table.items():
            for i, text in enumerate(texts):
                out.append({"id": f"{label}-{kind}-{i}", "label": label, "kind": kind, "text": text})
    return out
