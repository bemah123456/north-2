# Speech model comparison on the PC (2026-10-19/20)

Goal: pick the speech recogniser for the spoken 4AT, make it more accurate on older voices,
and measure false positives (a correct answer judged wrong, which would push a healthy
person's 4AT score up).

## Data
- Older speakers: Mozilla Common Voice 17 English (CC0), public Hugging Face copy
  `saeedzou/common-voice-17-en-age-gender-accent`, speakers who self-report age 60+.
  12,569 clips from 449 speakers. Split by speaker: 10,080 clips (~14 h) for training,
  360 clips from 44 different speakers for testing. 88% of clips are in their sixties, so
  people over 70 are under-represented.
- 4AT probes: 15 answers (7 correct, 8 wrong; months backwards, age, birthday, place, year)
  read by the 2 Windows voices at 3 speeds = 90 clips, played clean and with noise at 10 dB SNR.
  Scored with the prototype's own 4AT rules (prototype/scorer.js). A perfect transcript scores
  all 15 correctly, so every probe error comes from speech recognition.

## 1. Accuracy on held-out older speakers (360 clips, 44 speakers)

| Model | Size | Word error rate (95% interval, resampling speakers) | Month/number/day recall | False month/number insertions | CPU time per clip |
|---|---|---|---|---|---|
| Whisper tiny | 38M | 17.2% (13.5-20.0) | 38/39 | 7 | 0.29 s |
| Whisper base | 73M | 12.8% (9.8-15.3) | 38/39 | 4 | 0.53 s |
| **Whisper base, tuned on older speakers (ours)** | 73M | 12.4% (10.2-14.1) | 37/39 | 1 | 0.61 s |
| Whisper small | 242M | 8.6% (6.4-10.4) | 38/39 | 0 | 1.85 s |
| Distil-Whisper small.en | 166M | 8.5% (5.9-10.5) | 38/39 | 0 | 1.54 s |
| **Whisper small, tuned on older speakers (ours, 600 steps, lr 5e-6)** | 242M | **8.3% (6.2-9.8)** | 38/39 | 1 | 3.1 s* |

*Measured in a later run where stock Whisper small also took 3.0 s per clip (vs 1.85 s in the first
run), so the difference is machine load, not the model; both are the same size.

Our tuned base model is slightly better than the original base (12.4% vs 12.8%) and inserts
fewer phantom numbers (1 vs 4), but the intervals overlap, so the gain is not proven.
Whisper small and Distil-Whisper are clearly more accurate than any base model.

## 2. False positives on 4AT answers (42 correct + 48 wrong answer clips per condition)

"Ask again" = exactly one month missing from an otherwise passing list: the app repeats the
question instead of scoring it (new rule in scorer.js, because recognisers often drop one month).

| Model | Audio | False positives | Ask again | Missed impairments |
|---|---|---|---|---|
| Whisper tiny | clean / noisy | 7% / 10% | 0 / 0 | 0 / 0 |
| Whisper base | clean / noisy | 7% / 5% | 4 / 0 | 0 / 0 |
| Whisper base tuned (ours) | clean / noisy | 10% / 19% | 6 / 2 | 0 / 0 |
| Whisper small | clean / noisy | 0% / 2% | 0 / 0 | 0 / 0 |
| Distil-Whisper small.en | clean / noisy | 17% / 12% | 2 / 1 | 0 / 0 |
| Whisper tiny + month prompt | clean / noisy | 5% / 7% | 0 / 0 | 0 / 0 |
| Whisper base + month prompt | clean / noisy | 2% / 5% | 0 / 0 | 0 / 0 |
| **Whisper small + month prompt** | clean / noisy | **0% / 2%** | 0 / 0 | **0 / 0** |
| Distil-Whisper + month prompt | clean / noisy | 33% / 36% | 2 / 2 | 0 / 0 |
| Whisper small tuned (ours) | clean / noisy | 2% / 5% | 0 / 0 | 0 / 0 |
| **Whisper small tuned (ours) + month prompt** | clean / noisy | **0% / 2%** | 0 / 0 | **0 / 0** |

Before the ask-again rule, false positives were higher (e.g. base 17%, tuned base 24%, Distil 21% clean).

"Month prompt": the months task is transcribed with Whisper's prompt set to the months in
backwards order. It did not make the model invent months: wrong answers (skips, stopping early,
going forwards) were still transcribed as said, 0 missed impairments.

## What causes the false positives
- Dropping one month from a list ("October, August" for "October, September, August"): the main cause.
  Fixed mostly by the month prompt and the ask-again rule.
- "Eighty four" heard as "a d four" / "may be poor", and "twenty twenty six" as "twenty two six" in noise.
  The cloud thread's robust.py fixes (sound-alike digits, ask again when a number answer has no number) target these.
- Our fine-tune on read sentences made list recognition worse (more dropped months), so tuning
  on Common Voice alone does not suit the 4AT. Next tuning data should include lists and numbers.

## Recommendation
Use **our tuned Whisper small with the month prompt** for the 4AT: lowest word error rate of all
models tested (8.3% vs 8.6% for stock Whisper small, 8.5% Distil-Whisper) and the same best
false-positive result (0% clean, 2% noisy, no missed impairments). The gain over stock Whisper
small is small and the 95% intervals overlap, so stock Whisper small + month prompt is an equally
safe choice. Unlike our base fine-tune, the gentler small fine-tune did not hurt month lists.
Add the ask-again rule and the cloud thread's mishearing fixes. Whisper base + prompt is the
fallback for phones that cannot run small. The tuned small model (926 MB) stays on the PC
(training/out/whisper-small); it is too big for the 20 MB project-file limit.

## Limits
Synthetic voices are not older or delirious speakers; Common Voice is read speech by healthy
volunteers. A clinical false-positive rate needs recordings from older people with and without
delirium, scored by a clinician.

## Files
- training/: scripts (prepare_cv.py, fetch_cv17_older.py, finetune_whisper.py, compare_models.py,
  make_probes.ps1, probe_score.js, common.py), logs and out/*.md result tables.
- prototype/scorer.js: 4AT scoring incl. ask-again rule (16 unit tests pass: `node --test`).
- Tuned model: whisper-base-older60 (transformers save_pretrained; word timestamps checked with
  the ASR pipeline, return_timestamps="word").
