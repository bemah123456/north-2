# Model comparison (2026-10-20 04:46)

## Older speakers held out from training (360 Common Voice clips, 44 speakers aged 60+)

| Model | Size | Word error rate (95% interval) | Month/number/day recall | False month/number/day insertions | Time per clip (CPU) |
|---|---|---|---|---|---|
| openai/whisper-small@prompt | 242M | 8.6% (6.4% to 10.4%) | 97.4% of 39 | 0 (0.0 per 100) | 3.03 s |
| out/whisper-small | 242M | 8.3% (6.2% to 9.8%) | 97.4% of 39 | 1 (2.6 per 100) | 3.12 s |
| out/whisper-small@prompt | 242M | 8.3% (6.2% to 9.8%) | 97.4% of 39 | 1 (2.6 per 100) | 3.09 s |

## 4AT answer probes (90 synthetic clips per condition)

False positive: a correct answer judged wrong, which would raise a healthy person's 4AT score. Missed impairment: a wrong answer judged right. Ask again: exactly one month missing, so the app repeats the question instead of scoring it.

| Model | Audio | False positives | Ask again (correct answers) | Missed impairments | Ask again (wrong answers) |
|---|---|---|---|---|---|
| openai/whisper-small@prompt | clean | 0/42 (0%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-small@prompt | noisy 10 dB | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small | clean | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small | noisy 10 dB | 2/42 (5%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small@prompt | clean | 0/42 (0%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small@prompt | noisy 10 dB | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |

## Every probe error

- openai/whisper-small@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- out/whisper-small, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november um october september august a july sune" (false positive)
- out/whisper-small, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- out/whisper-small, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november umm october september august a july sune" (false positive)
- out/whisper-small@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)

Limits: probes use two synthetic adult voices, not older speakers, and do not test real delirium. A clinical false-positive rate needs recordings from people with and without delirium.