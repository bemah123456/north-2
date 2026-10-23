# Model comparison (2026-10-21 01:19)

## Older speakers held out from training (360 Common Voice clips, 44 speakers aged 60+)

| Model | Size | Word error rate (95% interval) | With background talk 10 dB | Month/number/day recall | False month/number/day insertions | Time per clip (CPU) |
|---|---|---|---|---|---|---|
| openai/whisper-small@prompt | 242M | 8.6% (6.4% to 10.4%) | 32.9% (21.0% to 52.1%) | 97.4% of 39 | 0 (0.0 per 100) | 1.68 s |
| distil-whisper/distil-small.en | 166M | 8.5% (5.9% to 10.5%) | 29.1% (24.3% to 35.9%) | 97.4% of 39 | 0 (0.0 per 100) | 1.46 s |
| out/whisper-small@prompt | 242M | 8.3% (6.2% to 9.8%) | 22.9% (16.7% to 36.3%) | 97.4% of 39 | 1 (2.6 per 100) | 1.70 s |
| out/whisper-small-v2@prompt | 242M | 8.3% (6.4% to 9.9%) | 12.9% (10.2% to 15.0%) | 94.9% of 39 | 1 (2.6 per 100) | 1.71 s |
| out/whisper-small-v2 | 242M | 8.3% (6.4% to 9.9%) | 12.9% (10.2% to 15.0%) | 94.9% of 39 | 1 (2.6 per 100) | 1.88 s |

## 4AT answer probes (90 synthetic clips per condition)

False positive: a correct answer judged wrong, which would raise a healthy person's 4AT score. Missed impairment: a wrong answer judged right. Ask again: exactly one month missing, so the app repeats the question instead of scoring it.

| Model | Audio | False positives | Ask again (correct answers) | Missed impairments | Ask again (wrong answers) |
|---|---|---|---|---|---|
| openai/whisper-small@prompt | clean | 0/42 (0%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-small@prompt | noisy 10 dB | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-small@prompt | background talk 10 dB | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |
| distil-whisper/distil-small.en | clean | 7/42 (17%) | 2/42 | 0/48 (0%) | 0/48 |
| distil-whisper/distil-small.en | noisy 10 dB | 5/42 (12%) | 1/42 | 0/48 (0%) | 0/48 |
| distil-whisper/distil-small.en | background talk 10 dB | 1/42 (2%) | 2/42 | 0/48 (0%) | 0/48 |
| out/whisper-small@prompt | clean | 0/42 (0%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small@prompt | noisy 10 dB | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small@prompt | background talk 10 dB | 0/42 (0%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small-v2@prompt | clean | 0/42 (0%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small-v2@prompt | noisy 10 dB | 2/42 (5%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small-v2@prompt | background talk 10 dB | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small-v2 | clean | 0/42 (0%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small-v2 | noisy 10 dB | 3/42 (7%) | 0/42 | 0/48 (0%) | 0/48 |
| out/whisper-small-v2 | background talk 10 dB | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |

## Every probe error

- openai/whisper-small@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- openai/whisper-small@prompt, background talk 10 dB: said "I'm eighty four" -> heard "i'm az four" (false positive)
- distil-whisper/distil-small.en, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november august july" (false positive)
- distil-whisper/distil-small.en, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november august july june" (false positive)
- distil-whisper/distil-small.en, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november july june may april march february january" (false positive)
- distil-whisper/distil-small.en, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july" (false positive)
- distil-whisper/distil-small.en, clean: said "December, November, November, October, September, August, July, June, May" -> heard "december november november august july june may" (false positive)
- distil-whisper/distil-small.en, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november august july june" (false positive)
- distil-whisper/distil-small.en, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july june" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july june" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "I'm eighty four" -> heard "i may be poor" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july june" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november november october august july june" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july june" (false positive)
- distil-whisper/distil-small.en, background talk 10 dB: said "The fourth of May, nineteen forty two" -> heard "the fourth of may nine hundred forty two" (false positive)
- out/whisper-small@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- out/whisper-small-v2@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- out/whisper-small-v2@prompt, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "november of october september august of july june" (false positive)
- out/whisper-small-v2@prompt, background talk 10 dB: said "I'm eighty four" -> heard "i'm a z fork" (false positive)
- out/whisper-small-v2, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- out/whisper-small-v2, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "november of october september august of july june" (false positive)
- out/whisper-small-v2, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november umm october september august a july sune" (false positive)
- out/whisper-small-v2, background talk 10 dB: said "I'm eighty four" -> heard "i'm a z fork" (false positive)

Limits: probes use two synthetic adult voices, not older speakers, and do not test real delirium. A clinical false-positive rate needs recordings from people with and without delirium.