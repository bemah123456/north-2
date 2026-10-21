"""Proposed changes to the app's answer rules, tried here without editing
the app. Each one stops a transcription slip from counting as a mistake.
Only the two re-readings ("9-5" as 95, "2000 in 26" as 2026) can make an
answer pass; everything else becomes "ask again" or "unsure".

  split_age    an age heard only as single digits or as an impossible
               number ("I made a 7", "721" for seventy-one, "295") is
               misheard, not a wrong age. "9-5" and "9 to 5" are read as
               95 first.
  dropped_unit a birthday whose day or year is the right one with the last
               digit dropped ("February the 20th" for the 28th, "the 3rd"
               for the 31st, "1930" for 1938) is unsure instead of wrong.
  year_split   "2000 in 26", "20,026" and "20, 26" are read as 2026.

apply(A, S) patches the app's answers (A) and scoring (S) modules in place.
"""

import re

YEAR = re.compile(r"\b(?:2000\s*(?:in|and|&|n)?\s*|20\s*,\s*0?)(\d\d)\b", re.I)
SPLIT = re.compile(r"\b([2-9])\s*(?:-|to|too)\s*([0-9])\b", re.I)


def apply(A, S):
    old_misheard, old_age, old_dob, old_year = A.misheard, A.check_age, A.check_dob, A.check_year

    def check_year(answer, today):
        return old_year(YEAR.sub(r"20\1", answer), today)

    def join(text):
        return SPLIT.sub(r"\1\2", text)

    def misheard(kind, answer):
        if kind == "age":
            answer = join(answer)
            nums = A.numbers(A.normalize(answer))
            if nums and not A.DONT_KNOW.search(answer) and not any(10 <= n <= 120 for n in nums):
                return True
        return old_misheard(kind, answer)

    def check_age(answer, birth, today):
        return old_age(join(answer), birth, today)

    def check_dob(answer, birth):
        r = old_dob(answer, birth)
        if r is not False:
            return r
        t = A.normalize(answer)
        nums, months = A.numbers(t), A.months_in(t)
        if months and birth.month - 1 not in months:
            return r
        days = [n for n in nums if 1 <= n <= 31]
        years = [n for n in nums if 1900 <= n <= 2020]
        day_slip = days and birth.day not in days and any(
            (d % 10 == 0 and d // 10 == birth.day // 10) or d == birth.day // 10 for d in days)
        year_slip = years and birth.year not in years and any(y % 10 == 0 and y // 10 == birth.year // 10 for y in years)
        day_ok = not days or birth.day in days or day_slip
        year_ok = not years or birth.year in years or year_slip
        return None if (day_slip or year_slip) and day_ok and year_ok else r

    A.misheard, A.check_age, A.check_dob, A.check_year = misheard, check_age, check_dob, check_year
