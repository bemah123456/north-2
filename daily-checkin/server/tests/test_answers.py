from datetime import date

import pytest

from checkin import answers as A

TODAY = date(2026, 10, 19)
BIRTH = date(1944, 3, 14)


@pytest.mark.parametrize("text,expected", [
    ("2026", [2026]),
    ("it's twenty twenty six", [2026]),
    ("two thousand and twenty six I think", [2026]),
    ("nineteen forty four", [1944]),
    ("nineteen oh five", [1905]),
    ("I'm eighty two", [82]),
    ("march fourteenth", [14]),
    ("twenty, nineteen, eighteen", [20, 19, 18]),
    ("March 14, 1944", [14, 1944]),
])
def test_numbers(text, expected):
    assert A.numbers(text) == expected


def test_year():
    assert A.check_year("It's 2026", TODAY) is True
    assert A.check_year("twenty twenty six", TODAY) is True
    assert A.check_year("nineteen eighty", TODAY) is False
    assert A.check_year("I don't know", TODAY) is False


def test_age_allows_birthday_slip():
    assert A.age_on(BIRTH, TODAY) == 82
    assert A.check_age("eighty two", BIRTH, TODAY) is True
    assert A.check_age("I'm 83", BIRTH, TODAY) is True
    assert A.check_age("seventy", BIRTH, TODAY) is False
    assert A.check_age("", BIRTH, TODAY) is False


def test_dob():
    assert A.check_dob("March fourteenth, nineteen forty four", BIRTH) is True
    assert A.check_dob("3/14/1944", BIRTH) is True
    assert A.check_dob("June 2nd 1944", BIRTH) is False
    assert A.check_dob("March 14th 1950", BIRTH) is False
    assert A.check_dob("in March", BIRTH) is None  # can't tell; goes to review


def test_place():
    kws = ["home", "Springfield"]
    assert A.check_place("I'm at home", kws) is True
    assert A.check_place("my house in Springfield", kws) is True
    assert A.check_place("I don't know", kws) is False
    assert A.check_place("the kitchen", kws) is None


def test_months_backwards_4at_rules():
    full = "December November October September August July June May April March February January"
    assert A.score_attention("months_backwards", full)["score"] == 0
    seven = "December November October September August July June um"
    assert A.score_attention("months_backwards", seven)["score"] == 0
    short = "December November October uh September"
    r = A.score_attention("months_backwards", short)
    assert (r["correct_items"], r["score"]) == (4, 1)
    # A month said out of turn isn't counted, and neither is going back for it.
    jumbled = "December October November May"
    assert A.score_attention("months_backwards", jumbled)["correct_items"] == 1
    assert A.score_attention("months_backwards", "")["score"] == 2


def test_other_attention_tasks():
    assert A.score_attention("days_backwards", "Sunday Saturday Friday Thursday Wednesday")["score"] == 0
    assert A.score_attention("days_backwards", "Sunday Monday")["score"] == 1
    count = "twenty nineteen eighteen seventeen sixteen fifteen fourteen thirteen twelve eleven ten nine"
    assert A.score_attention("countdown_20", count)["score"] == 0
    assert A.score_attention("countdown_20", "20 19 18")["score"] == 1


def test_speech_to_text_slips_are_fixed():
    birth, today = date(1944, 3, 14), date(2026, 10, 19)
    assert A.check_age("eighty too", birth, today) is True
    assert A.check_age("I'm eighty for", birth, today) is False  # 84 is still wrong
    assert A.check_age("80 too", birth, today) is True
    assert A.check_year("it's 20/26", today) is True
    assert A.check_year("twenty six, I think", today) is True
    assert A.check_year("twenty five", today) is False
    glued = A.score_attention("countdown_20", "20, 1918, 17, 16, 15, 14, 13, 12, 11, 10, 9")
    assert glued["correct_items"] == 12 and glued["score"] == 0


def test_misheard():
    assert A.misheard("age", "")
    assert A.misheard("age", "I made it too")
    assert not A.misheard("age", "I don't know")
    assert not A.misheard("dob", "March I think")
    assert not A.misheard("place", "at the station")


def test_one_month_dropped():
    assert A.one_month_dropped("December November October August July June May")
    assert not A.one_month_dropped("December November October July June May April")  # two missing
    assert not A.one_month_dropped("December November October")  # stopped early
    assert not A.one_month_dropped("January February March April May June July")  # forwards


# Slips found by testing healthy answers in accented synthetic voices
# (research/cloud-4at-asr, PR #27).
def test_split_numbers_are_read_whole():
    old = date(1931, 3, 14)  # 95 on TODAY
    assert A.check_age("9-5", old, TODAY) is True
    assert A.check_age("I'm 9 to 5", old, TODAY) is True
    assert A.check_age("nine to five years old", old, TODAY) is True
    assert A.check_age("Nine-five", old, TODAY) is True
    assert A.check_year("2000 in 26", TODAY) is True
    assert A.check_year("20, 26", TODAY) is True
    assert A.check_year("2000 in 25", TODAY) is False


@pytest.mark.parametrize("heard", ["721", "I made a 7", "295"])
def test_impossible_age_is_asked_again(heard):
    assert A.misheard("age", heard)


def test_possible_ages_and_dont_know_are_not_misheard():
    assert not A.misheard("age", "seventy")
    assert not A.misheard("age", "I don't know, 5 maybe")


def test_dropped_digit_in_a_birthday_goes_to_a_person():
    birth = date(1938, 2, 28)
    assert A.check_dob("February the 20th, 1938", birth) is None
    assert A.check_dob("February 28th 1930", birth) is None
    assert A.check_dob("February 2nd 1938", birth) is None
    # Wrong month, or a day that isn't a slip, is still wrong.
    assert A.check_dob("March 28th 1938", birth) is False
    assert A.check_dob("February 14th 1938", birth) is False
    assert A.check_dob("February 28th 1950", birth) is False
