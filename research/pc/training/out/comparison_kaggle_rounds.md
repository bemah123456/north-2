# Kaggle GPU rounds

Same 44 held-out older speakers (360 Common Voice clips) as the PC. Lower is better.

| Model | Word error rate (95% interval) | With background talk 10 dB | Month/number/day recall | False month/number/day insertions |
|---|---|---|---|---|
| openai/whisper-small (stock) | 8.6% (6.4% to 10.4%) | 32.9% (21.0% to 52.1%) | 97.4% of 39 | 0 |
| round 1 rebuilt (600 steps, lr 5e-6) | 8.1% (6.1% to 9.7%) | 23.6% (16.8% to 36.6%) | 97.4% of 39 | 1 |
| round 2 rebuilt (+900 steps with background talk) | 8.6% (6.4% to 10.3%) | 13.5% (10.9% to 15.6%) | 97.4% of 39 | 1 |
| round 3a (+900 steps, months/numbers 35%, lr 4e-6) | 8.4% (6.4% to 10.1%) | 12.6% (10.2% to 14.6%) | 100.0% of 39 | 1 |
| round 3b at 1000 steps (months/numbers 25%, lr 5e-6) | 8.6% (6.5% to 10.3%) | 15.3% (10.9% to 22.3%) | 97.4% of 39 | 0 |
| round 3b at 2000 steps (months/numbers 25%, lr 5e-6) | 8.8% (6.7% to 10.5%) | 18.5% (11.0% to 33.0%) | 100.0% of 39 | 0 |
| round 3b at 3000 steps (months/numbers 25%, lr 5e-6) | 8.8% (6.7% to 10.5%) | 16.3% (11.3% to 24.5%) | 100.0% of 39 | 0 |

PC reference: stock small 8.6% / 32.9%, round 2 (best so far) 8.3% / 12.9%.

Best: **round 3a (+900 steps, months/numbers 35%, lr 4e-6)** (8.4% quiet + 12.6% talk = 21.0%; PC round 2 = 21.2%). It beats the PC's round 2.