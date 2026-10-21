# Model comparison (2026-10-21 08:16)

## Older speakers held out from training (360 Common Voice clips, 44 speakers aged 60+)

| Model | Size | Word error rate (95% interval) | With background talk 10 dB | Month/number/day recall | False month/number/day insertions | Time per clip (CPU) |
|---|---|---|---|---|---|---|
| out/whisper-small-v2@prompt | 242M | 8.3% (6.4% to 9.9%) | 12.9% (10.2% to 15.0%) | 94.9% of 39 | 1 (2.6 per 100) | 3.06 s |

## 4AT answer probes (90 synthetic clips per condition)

False positive: a correct answer judged wrong, which would raise a healthy person's 4AT score. Missed impairment: a wrong answer judged right. Ask again: exactly one month missing, so the app repeats the question instead of scoring it.

| Model | Audio | False positives | Ask again (correct answers) | Missed impairments | Ask again (wrong answers) |
|---|---|---|---|---|---|
| out/whisper-small-v2@prompt | clean | 0/42 (0%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small-v2@prompt | noisy 10 dB | 2/42 (5%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small-v2@prompt | background talk 10 dB | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |

## Every probe error

- out/whisper-small-v2@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- out/whisper-small-v2@prompt, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "november of october september august of july june" (false positive)
- out/whisper-small-v2@prompt, background talk 10 dB: said "I'm eighty four" -> heard "i'm a z fork" (false positive)

Limits: probes use two synthetic adult voices, not older speakers, and do not test real delirium. A clinical false-positive rate needs recordings from people with and without delirium.