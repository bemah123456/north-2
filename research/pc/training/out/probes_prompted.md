# Model comparison (2026-10-19 20:15)

## Older speakers held out from training (0 Common Voice clips, 0 speakers aged 60+)

| Model | Size | Word error rate (95% interval) | Month/number/day recall | False month/number/day insertions | Time per clip (CPU) |
|---|---|---|---|---|---|

## 4AT answer probes (90 synthetic clips per condition)

False positive: a correct answer judged wrong, which would raise a healthy person's 4AT score. Missed impairment: a wrong answer judged right. Ask again: exactly one month missing, so the app repeats the question instead of scoring it.

| Model | Audio | False positives | Ask again (correct answers) | Missed impairments | Ask again (wrong answers) |
|---|---|---|---|---|---|
| openai/whisper-base@prompt | clean | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-base@prompt | noisy 10 dB | 2/42 (5%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-small@prompt | clean | 0/42 (0%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-small@prompt | noisy 10 dB | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |
| distil-whisper/distil-small.en@prompt | clean | 14/42 (33%) | 2/42 | 0/48 (0%) | 0/48 |
| distil-whisper/distil-small.en@prompt | noisy 10 dB | 15/42 (36%) | 2/42 | 0/48 (0%) | 0/48 |
| openai/whisper-tiny@prompt | clean | 2/42 (5%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-tiny@prompt | noisy 10 dB | 3/42 (7%) | 0/42 | 0/48 (0%) | 0/48 |

## Every probe error

- openai/whisper-base@prompt, clean: said "I'm eighty four" -> heard "i'm a d four" (false positive)
- openai/whisper-base@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i may be poor" (false positive)
- openai/whisper-base@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- openai/whisper-small@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october january january january" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november august july june" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December, November, November, October, September, August, July, June, May" -> heard "december november october october october may" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october september january" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october june" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october october august july june" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november april february january" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november august july" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December, November, November, October, September, August, July, June, May" -> heard "december november october october may" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october january january" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october september august july april january" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july june" (false positive)
- distil-whisper/distil-small.en@prompt, clean: said "December, November, November, October, September, August, July, June, May" -> heard "december november october august july may" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october january january january january" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october june" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December, November, November, October, September, August, July, June, May" -> heard "december november october october october october december december december november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i may be poor" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october september august january january" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october october june" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october october august july april april january" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august june" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December, November, November, October, September, August, July, June, May" -> heard "december november november august july june may" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october february january" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December, November, November, October, September, August, July, June, May" -> heard "december november october october october december december november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november november" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october september january january" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october june" (false positive)
- distil-whisper/distil-small.en@prompt, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july june" (false positive)
- openai/whisper-tiny@prompt, clean: said "I'm eighty four" -> heard "i made it for" (false positive)
- openai/whisper-tiny@prompt, clean: said "I'm eighty four" -> heard "i'm a d four" (false positive)
- openai/whisper-tiny@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i may be poor" (false positive)
- openai/whisper-tiny@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- openai/whisper-tiny@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm a v fork" (false positive)

Limits: probes use two synthetic adult voices, not older speakers, and do not test real delirium. A clinical false-positive rate needs recordings from people with and without delirium.