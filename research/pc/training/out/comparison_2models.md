# Model comparison (2026-10-19 19:26)

## Older speakers held out from training (360 Common Voice clips, 44 speakers aged 60+)

| Model | Size | Word error rate (95% interval) | Month/number/day recall | False month/number/day insertions | Time per clip (CPU) |
|---|---|---|---|---|---|
| distil-whisper/distil-small.en | 166M | 8.5% (5.9% to 10.5%) | 97.4% of 39 | 0 (0.0 per 100) | 1.54 s |
| out/whisper-base | 73M | 12.4% (10.2% to 14.1%) | 94.9% of 39 | 1 (2.6 per 100) | 0.61 s |

## 4AT answer probes (90 synthetic clips per condition)

False positive: a correct answer judged wrong, which would raise a healthy person's 4AT score. Missed impairment: a wrong answer judged right.

| Model | Audio | False positives | Missed impairments |
|---|---|---|---|
| distil-whisper/distil-small.en | clean | 9/42 (21%) | 0/48 (0%) |
| distil-whisper/distil-small.en | noisy 10 dB | 6/42 (14%) | 0/48 (0%) |
| out/whisper-base | clean | 10/42 (24%) | 0/48 (0%) |
| out/whisper-base | noisy 10 dB | 10/42 (24%) | 0/48 (0%) |

## Every probe error

- distil-whisper/distil-small.en, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october august july june may april march february january" (false positive)
- distil-whisper/distil-small.en, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november august july" (false positive)
- distil-whisper/distil-small.en, clean: said "December, November, November, October, September, August, July, June, May" -> heard "december november november september august july june may" (false positive)
- distil-whisper/distil-small.en, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november august july june" (false positive)
- distil-whisper/distil-small.en, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november july june may april march february january" (false positive)
- distil-whisper/distil-small.en, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july" (false positive)
- distil-whisper/distil-small.en, clean: said "December, November, November, October, September, August, July, June, May" -> heard "december november november august july june may" (false positive)
- distil-whisper/distil-small.en, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november august july june" (false positive)
- distil-whisper/distil-small.en, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july june" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july june" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "I'm eighty four" -> heard "i may be poor" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november september august july june may april march february january" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july june" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november november october august july june" (false positive)
- distil-whisper/distil-small.en, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november october august july june" (false positive)
- out/whisper-base, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october august july june may april march february january" (false positive)
- out/whisper-base, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november september august a july june" (false positive)
- out/whisper-base, clean: said "December, November, November, October, September, August, July, June, May" -> heard "december november november october august july june may" (false positive)
- out/whisper-base, clean: said "I'm eighty four" -> heard "i'm a d four" (false positive)
- out/whisper-base, clean: said "December, November, November, October, September, August, July, June, May" -> heard "december november november october august july june may" (false positive)
- out/whisper-base, clean: said "I'm eighty four" -> heard "i'm ad four" (false positive)
- out/whisper-base, clean: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october august july june may april march february january" (false positive)
- out/whisper-base, clean: said "December... November... um... October... September... August... uh... July... June" -> heard "december november umbh october september august umbh july shun" (false positive)
- out/whisper-base, clean: said "December, November, November, October, September, August, July, June, May" -> heard "december november november september august july june may" (false positive)
- out/whisper-base, clean: said "December, November, November, October, September, August, July, June, May" -> heard "december november november october august july june may" (false positive)
- out/whisper-base, noisy 10 dB: said "December, November, October, September, August, July, June, May, April, March, February, January" -> heard "december november october august july june may april march february january" (false positive)
- out/whisper-base, noisy 10 dB: said "I'm eighty four" -> heard "i may be poor" (false positive)
- out/whisper-base, noisy 10 dB: said "It is twenty twenty six" -> heard "it is twenty two six" (false positive)
- out/whisper-base, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "december november of october august of july june" (false positive)
- out/whisper-base, noisy 10 dB: said "I'm eighty four" -> heard "i'm avie bore" (false positive)
- out/whisper-base, noisy 10 dB: said "December... November... um... October... September... August... uh... July... June" -> heard "november of october september august of july june" (false positive)
- out/whisper-base, noisy 10 dB: said "December, November, November, October, September, August, July, June, May" -> heard "december november november october august july june may" (false positive)
- out/whisper-base, noisy 10 dB: said "It is twenty twenty six" -> heard "it is twenty two six" (false positive)
- out/whisper-base, noisy 10 dB: said "The fourth of May, nineteen forty two" -> heard "before the may nineteen forty two" (false positive)
- out/whisper-base, noisy 10 dB: said "It is twenty twenty six" -> heard "it is twenty twond six" (false positive)

Limits: probes use two synthetic adult voices, not older speakers, and do not test real delirium. A clinical false-positive rate needs recordings from people with and without delirium.