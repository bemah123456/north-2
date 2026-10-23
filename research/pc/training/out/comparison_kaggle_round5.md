# Kaggle round 5: bigger base model, server-style scoring

Same 44 held-out older speakers (360 Common Voice clips) as every round. Lower is better. 95% intervals resample speakers; "vs round 3a" is the paired difference in quiet + talk word error rate (both models on the same resampled speakers), so it is much tighter than comparing two intervals.

## The rule: greedy decoding (as every earlier round)

| Model | Quiet | Background talk 10 dB | Quiet + talk | vs round 3a (quiet + talk) | Unseen voices 10 dB (LibriSpeech) | Month/number/day recall | False insertions | Runaway transcripts (quiet/talk/voices) |
|---|---|---|---|---|---|---|---|---|
| round 3a (current best, Whisper small) | 8.4% (6.5% to 10.3%) | 12.6% (10.3% to 14.8%) | 21.1% | - | 12.3% (9.8% to 14.5%) | 100.0% of 39 | 1 | 0/0/0 |
| Whisper small, stock | 8.6% (6.4% to 10.5%) | 32.9% (19.9% to 52.6%) | 41.5% | +20.4% (+7.7% to +40.2%), worse | 30.6% (21.0% to 46.1%) | 97.4% of 39 | 0 | 0/3/7 |
| Whisper large-v3-turbo, stock | 5.7% (4.2% to 7.0%) | 18.1% (12.6% to 27.9%) | 23.7% | +2.6% (-2.4% to +12.9%), within noise | 19.6% (13.7% to 28.8%) | 100.0% of 39 | 0 | 0/3/2 |
| distil-large-v3, stock | 7.0% (5.4% to 8.5%) | 25.3% (20.9% to 31.4%) | 32.3% | +11.2% (+6.8% to +18.0%), worse | 30.6% (25.1% to 38.6%) | 100.0% of 39 | 1 | 0/3/7 |
| turbo fine-tuned, 600 steps (lr 3e-6, months/numbers 30%) | 5.9% (4.5% to 7.2%) | 8.9% (7.2% to 10.5%) | 14.8% | -6.3% (-8.2% to -3.9%), better | 8.5% (7.0% to 10.1%) | 100.0% of 39 | 0 | 0/0/0 |
| turbo fine-tuned, 1200 steps (lr 3e-6, months/numbers 30%) | 5.6% (4.3% to 6.8%) | 8.4% (6.8% to 10.2%) | 14.1% | -7.0% (-8.7% to -4.9%), better | 8.1% (6.5% to 9.8%) | 100.0% of 39 | 0 | 0/0/0 |
| turbo fine-tuned, average of steps 800, 1000, 1200 | 5.8% (4.4% to 7.1%) | 8.4% (6.8% to 10.1%) | 14.3% | -6.8% (-8.4% to -4.9%), better | 8.3% (6.8% to 10.0%) | 100.0% of 39 | 0 | 0/0/0 |

## As the server runs it: faster-whisper, int8, beam 5, word timestamps

| Model | Quiet | Background talk 10 dB | Quiet + talk | vs round 3a | Unseen voices 10 dB | Recall | Runaway (q/t/v) | CPU s per answer, 2 threads / 4 threads |
|---|---|---|---|---|---|---|---|---|
| round 3a (current best, Whisper small) | 7.8% (6.0% to 9.4%) | 11.4% (9.3% to 13.3%) | 19.2% | - | 11.1% (8.9% to 13.1%) | 97.4% of 39 | 0/0/0 | 3.5 / 3.7 |
| Whisper small, stock | 7.9% (5.9% to 9.8%) | 19.2% (15.0% to 24.7%) | 27.0% | +7.9% (+4.3% to +12.5%), worse | 18.5% (15.1% to 23.1%) | 97.4% of 39 | 0/2/1 | 3.3 / 3.5 |
| Whisper large-v3-turbo, stock | 5.4% (4.1% to 6.7%) | 15.1% (11.6% to 19.8%) | 20.5% | +1.3% (-1.6% to +5.8%), within noise | 14.0% (10.7% to 18.6%) | 100.0% of 39 | 0/3/4 | 12.7 / 12.5 |
| distil-large-v3, stock | 7.4% (5.7% to 8.9%) | 17.8% (14.5% to 22.7%) | 25.2% | +6.0% (+2.7% to +10.5%), worse | 19.8% (16.1% to 25.4%) | 100.0% of 39 | 0/0/4 | 12.7 / 12.4 |
| turbo fine-tuned, 1200 steps (lr 3e-6, months/numbers 30%) | 5.7% (4.3% to 7.0%) | 8.3% (6.5% to 10.1%) | 14.0% | -5.2% (-6.5% to -3.7%), better | 7.8% (6.2% to 9.3%) | 100.0% of 39 | 0/0/0 | 12.3 / 12.3 |
| turbo fine-tuned, average of steps 800, 1000, 1200 | 5.9% (4.3% to 7.3%) | 8.3% (6.6% to 10.0%) | 14.2% | -5.0% (-6.1% to -3.7%), better | 8.2% (6.6% to 9.9%) | 100.0% of 39 | 0/0/0 | 12.0 / 12.1 |

CPU times are Kaggle's CPU (a 2.2 GHz Xeon), 8 quiet clips, median; a laptop core is usually faster.

Best: **turbo fine-tuned, 1200 steps (lr 3e-6, months/numbers 30%)** (5.6% quiet + 8.4% talk = 14.1%; round 3a = 21.1%; paired difference -7.0%, 95% interval -8.7% to -4.9%). It beats round 3a.

## What this means

- **Fine-tuned turbo is the new best, and not by luck.** On the same 44 speakers it makes about a third fewer
  word errors than round 3a (14.1% against 21.1% quiet + background talk; the paired 95% interval for the
  difference, -8.7 to -4.9 points, is far from zero). Clips written down perfectly: 233 against 194 of 360 in
  quiet, 199 against 143 with background talk. Recall of months, numbers and days stays 39/39.
- **It's a real gain, not just learning Common Voice's babble.** With voices it never trained on (LibriSpeech
  readers at 10 dB) it drops from 12.3% to 8.1%. Stock turbo was 19.6% there: the fine-tuning on older
  speakers with background talk is what brings it down.
- **Run the server's way, the gap holds:** 14.0% against 19.2% with faster-whisper int8, beam 5 (paired
  interval -6.5 to -3.7 points). Round 3a also misses one of the 39 month/number words this way; turbo misses none.
- **The bigger model alone isn't enough.** Stock turbo is better in quiet (5.7%) but worse with background talk
  (18.1%) than round 3a; distil-large-v3 is worse than round 3a with background talk, both stock.
- **Fewer steps or averaging: no difference.** 600 steps (14.8%), 1,200 steps (14.1%) and the average of
  steps 800/1,000/1,200 (14.3%) are within noise of each other; the 1,200-step model is kept.
- **The cost is speed.** On Kaggle's CPU turbo takes about 12 s per answer against 3.5 s for small (3.5 times
  slower; the 32-layer encoder runs on every 30-second window). On the 2-core test laptop that measured
  small at about 2 s, expect roughly 7 s. A GPU, or a 4+ core server, makes it comfortable.
- **Greedy decoding loops on noisy clips for stock models** (runaway transcripts 3 to 7 of 360); the
  server's beam search and the fine-tuned models don't.

The winner is the job's private output (`whisper-round5-best-fp16/`, 16-bit, and `whisper-round5-best-ct2/`,
int8 for faster-whisper); weights are not committed.
