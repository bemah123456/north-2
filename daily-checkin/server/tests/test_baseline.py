from checkin.baseline import Z_CAP, build_baseline, change_probability, change_scores

USUAL = {"latency_s": 1.2, "words_per_min": 130.0, "pauses_per_min": 8.0, "mean_pause_s": 0.6,
         "filler_rate": 0.0, "repeat_rate": 0.0, "greeting_words": 14.0}


def test_one_um_or_one_repeat_cannot_raise_the_alarm_alone():
    base = build_baseline([USUAL] * 5)
    for name in ("filler_rate", "repeat_rate"):
        one_off = USUAL | {name: 0.1}  # a single word in a short check-in; uncapped, z would be 3 or more
        z = change_scores(one_off, base)
        assert z[name] == Z_CAP[name]
        assert change_probability(z) < 0.7


def test_hesitant_day_still_alarms():
    base = build_baseline([USUAL] * 5)
    hesitant = USUAL | {"latency_s": 3.5, "pauses_per_min": 18.0, "mean_pause_s": 1.4, "words_per_min": 100.0}
    assert change_probability(change_scores(hesitant, base)) >= 0.7
