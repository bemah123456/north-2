# Kaggle GPU rounds

Same 44 held-out older speakers (360 Common Voice clips) as the PC. Lower is better.

| Model | Word error rate (95% interval) | With background talk 10 dB | Month/number/day recall | False month/number/day insertions |
|---|---|---|---|---|
| start: round 3a (best so far) | 8.4% (6.4% to 10.1%) | 12.6% (10.3% to 14.6%) | 100.0% of 39 | 1 |
| round 4a: gentle polish (+600 steps, lr 2e-6, months/numbers 35%) | 8.5% (6.4% to 10.3%) | 16.1% (11.0% to 24.4%) | 100.0% of 39 | 1 |
| round 4b: louder background talk on 65% of clips (+900 steps, lr 3e-6, months/numbers 35%) | 8.5% (6.3% to 10.3%) | 15.5% (10.7% to 23.1%) | 100.0% of 39 | 1 |

PC reference: stock small 8.6% / 32.9%, round 2 (best so far) 8.3% / 12.9%.

Best: **start: round 3a (best so far)** (8.4% quiet + 12.6% talk = 21.1%; start = 21.1%). Nothing beat the start; no new model.