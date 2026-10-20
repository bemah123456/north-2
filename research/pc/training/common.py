"""Shared helpers: audio loading, text normalisation, and the 4AT-relevant word set."""
import csv
import re

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

SR = 16000

MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]
NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
                "sixty", "seventy", "eighty", "ninety", "hundred", "thousand"]
# Words the spoken 4AT depends on: months, numbers (age, dates, years), days.
KEY_WORDS = set(MONTHS) | set(NUMBER_WORDS) | {
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}


def load_audio(path):
    """Read an mp3/wav clip as mono float32 at 16 kHz (libsndfile 1.1+ decodes mp3)."""
    audio, sr = sf.read(path, dtype="float32", always_2d=True)
    audio = audio.mean(axis=1)
    if sr != SR:
        audio = resample_poly(audio, SR, sr).astype(np.float32)
    return audio


_ONES = NUMBER_WORDS[:20]
_TENS = {20: "twenty", 30: "thirty", 40: "forty", 50: "fifty", 60: "sixty", 70: "seventy",
         80: "eighty", 90: "ninety"}


def _under_100(n):
    if n < 20:
        return _ONES[n]
    return _TENS[n - n % 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])


def number_to_words(n):
    """84 -> 'eighty four'; 1942 -> 'nineteen forty two'; 2005 -> 'two thousand five'.
    Whisper writes digits while Common Voice spells numbers out, so both sides are spelled."""
    if n < 100:
        return _under_100(n)
    if 1100 <= n <= 2099 and not (2000 <= n <= 2009):
        hi, lo = divmod(n, 100)
        return _under_100(hi) + (" hundred" if lo == 0 else (" oh " + _ONES[lo] if lo < 10 else " " + _under_100(lo)))
    if n < 1000:
        h, r = divmod(n, 100)
        return _ONES[h] + " hundred" + ("" if r == 0 else " " + _under_100(r))
    if n < 10000:
        th, r = divmod(n, 1000)
        return _ONES[th] + " thousand" + ("" if r == 0 else " " + number_to_words(r))
    return " ".join(_ONES[int(d)] for d in str(n))


_ORD = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth",
        "nine": "ninth", "twelve": "twelfth"}


def ordinal_words(n):
    """4 -> 'fourth', 21 -> 'twenty first', 30 -> 'thirtieth'."""
    words = number_to_words(n).split()
    last = words[-1]
    if last in _ORD:
        last = _ORD[last]
    elif last.endswith("y"):
        last = last[:-1] + "ieth"
    else:
        last += "th"
    return " ".join(words[:-1] + [last])


def normalise(text):
    text = text.lower().replace("’", "'")
    text = re.sub(r"(\d),(\d{3})", r"\1\2", text)
    text = re.sub(r"\b(\d+)(st|nd|rd|th)\b", lambda m: " " + ordinal_words(int(m.group(1))) + " ", text)
    text = re.sub(r"\d+", lambda m: " " + number_to_words(int(m.group())) + " ", text)
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z' ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def read_manifest(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key_word_recall(refs, hyps):
    """Share of month/number/day words in the references that also appear in the hypotheses."""
    hit = total = 0
    for ref, hyp in zip(refs, hyps):
        hyp_words = hyp.split()
        for w in ref.split():
            if w in KEY_WORDS:
                total += 1
                if w in hyp_words:
                    hit += 1
    return (hit / total) if total else None, total
