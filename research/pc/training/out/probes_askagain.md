# Model comparison (2026-10-19 19:53)

## Older speakers held out from training (0 Common Voice clips, 0 speakers aged 60+)

| Model | Size | Word error rate (95% interval) | Month/number/day recall | False month/number/day insertions | Time per clip (CPU) |
|---|---|---|---|---|---|

## 4AT answer probes (90 synthetic clips per condition)

False positive: a correct answer judged wrong, which would raise a healthy person's 4AT score. Missed impairment: a wrong answer judged right. Ask again: exactly one month missing, so the app repeats the question instead of scoring it.

| Model | Audio | False positives | Ask again (correct answers) | Missed impairments | Ask again (wrong answers) |
|---|---|---|---|---|---|
| openai/whisper-tiny | clean | 3/42 (7%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-tiny | noisy 10 dB | 4/42 (10%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-base | clean | 3/42 (7%) | 4/42 | 0/48 (0%) | 0/48 |
| openai/whisper-base | noisy 10 dB | 2/42 (5%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-small | clean | 0/42 (0%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-small | noisy 10 dB | 1/42 (2%) | 0/42 | 0/48 (0%) | 0/48 |
| distil-whisper/distil-small.en | clean | 7/42 (17%) | 2/42 | 0/48 (0%) | 0/48 |
| distil-whisper/distil-small.en | noisy 10 dB | 5/42 (12%) | 1/42 | 0/48 (0%) | 0/48 |
| out/whisper-base | clean | 4/42 (10%) | 6/42 | 0/48 (0%) | 0/48 |
| out/whisper-base | noisy 10 dB | 8/42 (19%) | 2/42 | 0/48 (0%) | 0/48 |
| openai/whisper-base@prompt | clean | 7/42 (17%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-base@prompt | noisy 10 dB | 8/42 (19%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-small@prompt | clean | 6/42 (14%) | 0/42 | 0/48 (0%) | 0/48 |
| openai/whisper-small@prompt | noisy 10 dB | 7/42 (17%) | 0/42 | 0/48 (0%) | 0/48 |

## Every probe error

- openai/whisper-tiny, clean: said "I'm eighty four" -> heard "i made it for" (false positive)
- openai/whisper-tiny, clean: said "I'm eighty four" -> heard "i'm a d four" (false positive)
- openai/whisper-tiny, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october september august" (false positive)
- openai/whisper-tiny, noisy 10 dB: said "I'm eighty four" -> heard "i may be poor" (false positive)
- openai/whisper-tiny, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- openai/whisper-tiny, noisy 10 dB: said "I'm eighty four" -> heard "i'm a v fork" (false positive)
- openai/whisper-tiny, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october september august july" (false positive)
- openai/whisper-base, clean: said "I'm eighty four" -> heard "i'm a d four" (false positive)
- openai/whisper-base, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november umm october september august umm july" (false positive)
- openai/whisper-base, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november umm october august umm july june" (false positive)
- openai/whisper-base, noisy 10 dB: said "I'm eighty four" -> heard "i may be poor" (false positive)
- openai/whisper-base, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- openai/whisper-small, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
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
- out/whisper-base, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november september august a july june" (false positive)
- out/whisper-base, clean: said "I'm eighty four" -> heard "i'm a d four" (false positive)
- out/whisper-base, clean: said "I'm eighty four" -> heard "i'm ad four" (false positive)
- out/whisper-base, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november umbh october september august umbh july shun" (false positive)
- out/whisper-base, noisy 10 dB: said "I'm eighty four" -> heard "i may be poor" (false positive)
- out/whisper-base, noisy 10 dB: said "It is twenty twenty six" -> heard "it is twenty two six" (false positive)
- out/whisper-base, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november of october august of july june" (false positive)
- out/whisper-base, noisy 10 dB: said "I'm eighty four" -> heard "i'm avie bore" (false positive)
- out/whisper-base, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "november of october september august of july june" (false positive)
- out/whisper-base, noisy 10 dB: said "It is twenty twenty six" -> heard "it is twenty two six" (false positive)
- out/whisper-base, noisy 10 dB: said "The fourth of May, nineteen forty two" -> heard "before the may nineteen forty two" (false positive)
- out/whisper-base, noisy 10 dB: said "It is twenty twenty six" -> heard "it is twenty twond six" (false positive)
- openai/whisper-base@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, clean: said "I'm eighty four" -> heard "i'm a d four" (false positive)
- openai/whisper-base@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i may be poor" (false positive)
- openai/whisper-base@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- openai/whisper-base@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-base@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, noisy 10 dB: said "I'm eighty four" -> heard "i'm av four" (false positive)
- openai/whisper-small@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)
- openai/whisper-small@prompt, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "" (false positive)

Limits: probes use two synthetic adult voices, not older speakers, and do not test real delirium. A clinical false-positive rate needs recordings from people with and without delirium.