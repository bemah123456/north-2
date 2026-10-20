from datetime import date, timedelta

from checkin.exercises import NUMBER_WORDS, build_checkin
from checkin.features import checkin_features
from checkin.scoring import score_checkin

from helpers import spoken

PERSON = {"birth_date": "1944-03-14", "place_keywords": ["home", "Springfield"]}
DAY = date(2026, 10, 19)

GOOD = {
    "greeting": "I slept pretty well thank you and I'm going to see my daughter for lunch today",
    "age": "I'm eighty two",
    "dob": "March fourteenth nineteen forty four",
    "place": "I'm at home",
    "year": "it's twenty twenty six",
    "months_backwards": "December November October September August July June May April March February January",
    "days_backwards": "Sunday Saturday Friday Thursday Wednesday Tuesday Monday",
    "countdown_20": "twenty nineteen eighteen seventeen sixteen fifteen fourteen thirteen twelve eleven ten nine eight",
}


def said_back(ex):
    return " ".join(NUMBER_WORDS[int(d)] for d in ex.expect)


def answers(day, overrides=None, plan=None, **voice):
    overrides = overrides or {}
    out = {}
    for ex in plan or build_checkin("p1", day):
        key = ex.id if ex.part != "attention" else ex.kind
        text = overrides.get(key, said_back(ex) if ex.kind == "digit_span" else GOOD[key])
        out[ex.id] = {"transcript": text, "words": spoken(text, **voice) if text else []}
    return out


def history(days=4):
    hist = []
    for i in range(days):
        d = DAY - timedelta(days=days - i)
        given = answers(d, latency=1.0 + 0.1 * i, words_per_min=130 + 4 * i, pause_every=8)
        hist.append(checkin_features({k: v["words"] for k, v in given.items()}))
    return hist


def test_plan_rotates_but_is_stable():
    a = build_checkin("p1", DAY)
    assert a == build_checkin("p1", DAY)
    assert [e.part for e in a] == ["alertness"] + ["orientation"] * 4 + ["attention"] * 2
    plans = {tuple(e.prompt for e in build_checkin("p1", DAY + timedelta(days=i))) for i in range(6)}
    assert len(plans) > 1


def test_usual_day_looks_normal():
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY), answers(DAY, pause_every=8), history())
    assert r["band"] == "unlikely", r["reasons"]
    assert r["total"] == 0
    assert r["voice"]["baseline_days"] == 4


def test_confused_slow_day_says_call_doctor():
    bad = {"year": "nineteen eighty I think", "place": "I'm not sure where I am",
           "months_backwards": "December November um October", "days_backwards": "Sunday Saturday",
           "countdown_20": "twenty nineteen", "greeting": "um tired"}
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY),
                      answers(DAY, bad, latency=5.0, words_per_min=70, pause_every=2, pause=2.0), history())
    assert r["band"] == "possible_delirium"
    assert r["headline"] == "Call their doctor today"
    assert r["parts"]["amt4"] == 2
    assert r["parts"]["attention"] == 1
    assert r["parts"]["acute_change"] == 4
    assert any("slower" in x or "pausing" in x for x in r["reasons"])


def test_one_slip_is_keep_an_eye():
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY), answers(DAY, {"year": "2025"}, pause_every=8),
                      history())
    assert r["band"] == "possible_impairment"
    assert r["headline"] == "Keep an eye on it"
    assert "got the year wrong" in r["reasons"]


def test_family_report_alone_scores_acute_change():
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY), answers(DAY), [], family_says_different=True)
    assert r["parts"]["acute_change"] == 4
    assert r["band"] == "possible_delirium"


def test_no_baseline_yet_still_scores_content():
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY), answers(DAY), [])
    assert r["voice"]["baseline_days"] == 0
    assert r["voice"]["change_probability"] is None
    assert r["band"] == "unlikely"


def test_silence_counts_as_not_alert():
    empty = {k: "" for k in GOOD}
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY), answers(DAY, empty), [])
    assert r["parts"]["alertness"] == 4
    assert r["parts"]["attention"] == 2


def test_typed_answers_skip_voice():
    typed = {k: {"transcript": v["transcript"], "words": None} for k, v in answers(DAY).items()}
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY), typed, history())
    assert r["voice"]["measured"] is False
    assert r["band"] == "unlikely"


def test_unclear_place_goes_to_review_not_mistake():
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY), answers(DAY, {"place": "in the kitchen"}), [])
    assert r["needs_review"] == 1
    assert r["parts"]["amt4"] == 0


def test_misheard_recordings_wait_for_a_person():
    given = answers(DAY, {"age": "I made it too", "year": ""})
    plain = score_checkin(PERSON, DAY, build_checkin("p1", DAY), given, history())
    for v in given.values():
        v["heard_speech"] = True
    heard = score_checkin(PERSON, DAY, build_checkin("p1", DAY), given, history())
    assert plain["parts"]["amt4"] == 2
    assert heard["parts"]["amt4"] == 0 and heard["needs_review"] == 2
    assert {i["kind"] for i in heard["items"] if i.get("misheard")} == {"age", "year"}


def test_unheard_attention_is_not_a_failure():
    given = answers(DAY)
    att = next(ex for ex in build_checkin("p1", DAY) if ex.part == "attention")
    given[att.id] = {"transcript": "", "words": [], "heard_speech": True}
    r = score_checkin(PERSON, DAY, build_checkin("p1", DAY), given, history())
    assert r["parts"]["attention"] == 0 and r["needs_review"] == 1


def test_noisy_checkin_is_flagged_but_scored_the_same():
    given = answers(DAY)
    quiet = score_checkin(PERSON, DAY, build_checkin("p1", DAY), given, history())
    for v in given.values():
        v["noisy"] = True
    noisy = score_checkin(PERSON, DAY, build_checkin("p1", DAY), given, history())
    assert noisy["noisy"] and not quiet["noisy"]
    assert noisy["total"] == quiet["total"]
    assert not any("noise" in r for r in noisy["reasons"])  # a clear day needs no caveat
    age = next(ex.id for ex in build_checkin("p1", DAY) if ex.kind == "age")
    given[age]["transcript"] = "I'm sixty"
    worse = score_checkin(PERSON, DAY, build_checkin("p1", DAY), given, history())
    assert worse["total"] and any("background noise" in r for r in worse["reasons"])


def test_one_dropped_month_waits_for_a_person():
    att = next(ex for ex in build_checkin("p1", DAY) if ex.part == "attention")
    assert att.kind == "months_backwards"  # on DAY
    given = answers(DAY)
    given[att.id]["transcript"] = "December November October August July June May"
    typed = score_checkin(PERSON, DAY, build_checkin("p1", DAY), given, history())
    given[att.id]["heard_speech"] = True
    heard = score_checkin(PERSON, DAY, build_checkin("p1", DAY), given, history())
    assert typed["parts"]["attention"] == 1  # a typed answer is taken as given
    assert heard["parts"]["attention"] == 0 and heard["needs_review"] == 1
    assert next(i for i in heard["items"] if i["kind"] == "months_backwards")["one_month_dropped"]
