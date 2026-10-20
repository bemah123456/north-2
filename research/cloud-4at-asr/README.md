# Which speech model to use for the spoken 4AT, and how often it raises false alarms

Run in the cloud on 2026-10-19, after the PC became unreachable. The PC
session owns the real older-speaker accuracy test and the fine-tuned Whisper
model; this folder is the 4AT false-alarm study. Hugging Face is blocked from
this cloud environment, so every model here came from the sherpa-onnx GitHub
releases (ONNX exports of the same weights).

> **Real voices come first.** The PC session tested the same models on 44
> real older speakers ([../pc/RESULTS.md](../pc/RESULTS.md) in the repo).
> Where its ranking differs from the synthetic one here, go with the PC.
> It found Whisper small best overall, Distil-Whisper as accurate on read
> sentences but bad at month lists, and a months prompt for Whisper that cut
> its 4AT false positives to 0% clean and 2% noisy.

## Short answer

1. **Keep Whisper small (the app's current default), and add the transcript
   fixes below.** It is the only model that stays usable with a TV on
   (15.8% word errors, against 32.8% or more for every other model). In a quiet
   room Whisper small.en and Parakeet are a little more accurate.
2. **The fixes roughly halve false alarms for every model** and never pass
   a wrong answer on perfect transcripts. With Whisper small, a healthy
   person's check-in raised any concern 24% of the time with the app's
   current rules and 10% with the fixes, in the slowed, shaky "older" voices.
3. **Background TV is the biggest cause of false alarms.** Even with the
   fixes, 37% of healthy check-ins (Whisper small) raised a concern, because
   the model writes down the TV's dates and numbers. The app should ask for
   a quiet room and check for background speech before scoring.
4. **No healthy check-in reached "call their doctor today" (4 or more) from
   the spoken parts** in quiet conditions. With TV it happened at most 0.5%
   of the time (Whisper tiny). False alarms are almost all "keep an eye on
   it" (1 to 3 points).
5. **Avoid Distil-Whisper small.en.** It wrote "1945" for "nineteen forty
   four" in most birthday answers, so it fails healthy people on their
   birthday.
6. **Bug in the app:** the local Whisper path can't read an m4a recording
   whose index is at the end of the file, which is how Android (and often
   iOS) save them. The upload fails instead of being transcribed. Fix in
   [app-patch/transcribe-m4a-fix.diff](app-patch/transcribe-m4a-fix.diff);
   all 40 server tests pass with it. Not yet checked against a real phone
   recording.

## What was tested

- **Answers:** 49 spoken 4AT answers for one made-up person (born
  14 March 1944, aged 82, at home in Springfield): 34 healthy answers worded
  the way people actually answer ("I'll be eighty three in March, so eighty
  two"), and 15 impaired ones (wrong year, "I don't know where I am", months
  backwards that stall). The app's rules score all 49 correctly from perfect
  text, so every error below comes from speech recognition.
  [scripts/answers_set.py](scripts/answers_set.py)
- **Voices:** 12 synthetic voices (6 LibriTTS-R, 3 VCTK, 3 Kokoro; 23 were
  made, 12 used for the full comparison to fit the CPU time).
- **Three conditions:** clean; "older" (20% slower with a 6 Hz voice
  tremor); "TV" (older, phone-quality sound, with a TV newsreader 10 dB
  quieter in the background reading dates and numbers on purpose).
- **8 models:** Whisper tiny, tiny.en, base.en, small, small.en,
  Distil-Whisper small.en, NVIDIA Parakeet TDT 0.6B v2, Moonshine base.
  1,764 clips each.
- **Scoring:** each transcript goes through the app's own `answers.py`
  rules. A full check-in is four orientation answers plus one attention task;
  every mix of healthy answers per voice is scored (75,000 healthy check-ins
  per model and condition) and 3,024 impaired check-ins.

## Results

"False alarms" = share of healthy check-ins whose spoken parts (4AT parts 2
and 3) score 1 or more, with the app's current rules, then with the fixes.
Sorted by the "older" result with fixes.

| Model | WER clean | WER older | WER TV | False alarms clean | False alarms older | False alarms TV | Seconds per second of audio |
|---|---|---|---|---|---|---|---|
| Whisper small.en | 8.8% | 8.9% | 43.0% | 12% → 0% | 23% → 9% | 64% → 53% | 0.31 |
| Whisper small (app default) | 11.5% | 9.9% | 15.8% | 24% → 9% | 24% → 10% | 49% → 37% | 0.33 |
| Parakeet TDT 0.6B v2 | 6.7% | 6.9% | 58.9% | 28% → 5% | 27% → 15% | 89% → 40% | 0.08 |
| Whisper base.en | 13.7% | 13.7% | 32.8% | 31% → 12% | 33% → 23% | 52% → 41% | 0.10 |
| Moonshine base | 15.2% | 16.3% | 86.0% | 54% → 14% | 62% → 26% | 55% → 47% | 0.06 |
| Whisper tiny.en | 16.5% | 16.9% | 43.8% | 42% → 19% | 57% → 39% | 76% → 61% | 0.07 |
| Whisper tiny | 18.0% | 20.3% | 62.1% | 64% → 44% | 67% → 53% | 88% → 79% | 0.07 |
| Distil-Whisper small.en | 16.9% | 17.9% | 33.1% | 55% → 50% | 75% → 68% | 86% → 83% | 0.18 |

| Model | Healthy answers marked wrong, older (app → fixed) | Asked again (fixed) | Impaired answers marked right, all conditions | Impaired check-ins still flagged (fixed, worst condition) |
|---|---|---|---|---|
| Whisper small.en | 16 → 7 of 360 | 11 | 0 of 684 | 100% |
| Whisper small (app default) | 16 → 7 of 360 | 8 | 0 of 684 | 100% |
| Parakeet TDT 0.6B v2 | 18 → 9 of 360 | 12 | 0 of 684 | 97.7% |
| Whisper base.en | 24 → 16 of 360 | 6 | 1 of 684 | 100% |
| Moonshine base | 52 → 20 of 360 | 37 | 0 of 684 | 98.4% |
| Whisper tiny.en | 50 → 32 of 360 | 13 | 0 of 684 | 100% |
| Whisper tiny | 65 → 47 of 360 | 25 | 1 of 684 | 100% |
| Distil-Whisper small.en | 82 → 71 of 360 | 8 | 0 of 684 | 100% |

The two impaired answers marked right were "Ninety one" heard as "81": the
app allows one year either side of the true age (82), so a one-digit
mishearing passed.

## How loud a TV can be, and a check that catches it

Even a quiet TV hurts. With Whisper small and the fixes, healthy check-ins
raised a concern 10% of the time in a quiet room, 22% with the TV 20 dB
below the speaker (barely audible), 37% at 10 dB and 64% at 5 dB. Parakeet
went from 15% to 20%, 40% and 91%. So the app should not try to work
through a TV; it should ask for it to be turned off.

[scripts/noise_check.py](scripts/noise_check.py) detects that from the
recording alone. It measures how much the loudness jumps in the gaps
between the person's words: another voice flickers, while a fan, hiss or a
quiet room stays steady. Per clip, it flagged 96% of TV clips even at
20 dB, 0% of clips with steady fan noise and about 5% of quiet clips.
Deciding per check-in (3 or more of 5 answers flagged) it asked for the TV
to be turned off on every TV check-in and never in a quiet one, so the
false-alarm rate drops back to the quiet-room figure.

| Whisper small, fixed rules | Quiet | TV -20 dB | TV -15 dB | TV -10 dB | TV -5 dB |
|---|---|---|---|---|---|
| Healthy check-ins raising a concern | 10% | 22% | 22% | 37% | 64% |
| ... with the quiet-room check | 10% | 10% | 10% | 10% | 10% |
| Check-ins asked to turn the TV off | 0% | 100% | 100% | 100% | 100% |

The "with the check" row assumes the person turns the TV off and answers
again. The TV here is a synthetic newsreader with no music, and the quiet
clips have no room noise, so the threshold (4.4 dB) should be tuned on real
recordings first: the PC's Common Voice clips would show how often it
fires on real microphones. Numbers per model are in
`results/levels.json`.

**On real microphones the first version fires too often.** On the PC's
200 Common Voice clips from 20 speakers aged 60+ (their own devices, MP3
compressed, no TV known), it flagged 24% of clips and would have asked
16% of check-ins to turn the TV off. Compression and microphone noise
flicker too. A second condition fixes most of that: the gaps must also
be no more than 40 dB quieter than the speech, which a TV keeps them and
a real quiet room does not
([scripts/noise_check_real.py](scripts/noise_check_real.py)).

| Check-ins asked to turn the TV off | Flicker only | Flicker and gap |
|---|---|---|
| Real recordings, no TV known | 16.2% | 1.7% |
| Synthetic, quiet | 3.6% | 0.3% |
| Synthetic, TV -20 dB | 100% | 99.2% |
| Synthetic, TV -10 dB | 100% | 100% |

The 40 dB line was picked on these same clips, so it needs checking on
new recordings, and some of the real clips may really have had something
playing in the background.

## Does the room trip the voice-change alarm?

The app can also score 4AT part 4 ("acute change") from the voice: it
compares answer delay, speaking rate, pauses, "um"s and repeats with the
person's own normal days, and a change probability of 0.7 or more scores
4 points, which is "call their doctor today" on its own.
[scripts/voice_change.py](scripts/voice_change.py) gives each of 12 voices
5 quiet-room days, uses 4 as the baseline and tests the fifth (60 tests per
condition, word timestamps from Parakeet).

| Test day | Voice alone scored 4 points | Mean change probability | ... with the quiet-room check |
|---|---|---|---|
| Quiet, same voice | 10% | 0.15 | 10% |
| Slower, with a tremor (a real change) | 15% | 0.22 | 15% |
| TV -20 dB | 32% | 0.42 | 0% |
| TV -10 dB | 45% | 0.58 | 0% |

Three findings:

1. **A TV alone makes healthy people look changed.** The background speech
   fills the gaps, so the timestamps show "longer pauses than usual" and
   "pausing more than usual" (all 27 TV -10 dB alarms gave one of those).
   The quiet-room check above catches every one of these check-ins.
2. **A healthy person on an ordinary day already alarms 10% of the time**
   from 4 baseline days. With such a short baseline the spread is
   underestimated, so normal day-to-day variation reads as change. The app
   should wait for more baseline days (or use a wider floor on the spread)
   before the voice alone can score 4 points.
3. **The slowed, shaky voice was barely told apart from a normal day**
   (15% against 10%). Part of that is probably the synthetic slowdown, which stretches
   the whole clip evenly, so pauses and answer delay grow little relative
   to each other. It still means the voice alarm should not be trusted to
   catch change until it has been checked on real recordings.

The change model (`model.json` in the app) was itself trained on synthetic
data, so these numbers say more about the setup than about real people.
Raw features per voice and day are in `results/voice_change.json`.

## How many normal days the voice-change score needs

The quiet-room test above found healthy days alarming 10% of the time
against 4 normal days. To see whether more normal days fix that, two sets
of days were scored with the app's own features and model:

- **Real older speakers:** 20 Common Voice speakers aged 60+, 10 read
  sentences each, one sentence standing for one day (CC0, prepared by the
  PC session). Each day was also made "slowed + tremor" (20% slower, 6 Hz
  tremor) and "hesitant" (1 s slower to start, a 0.7 s pause after every
  third word, 10% slower).
- **Synthetic check-ins:** the 12 voices above, 16 days each, every day a
  random wording of the four orientation answers and one attention task.

Each test compares one day with up to 20 random sets of N other normal days
of the same person. Word timestamps come from Parakeet.
[scripts/voice_baseline_study.py](scripts/voice_baseline_study.py)

| Healthy days that alarmed | 2 days | 5 days | 9 days | 14 days |
|---|---|---|---|---|
| Synthetic check-ins, current app | 8.1% | 6.5% | 6.7% | 6.8% |
| Synthetic check-ins, capped | 3.5% | 2.8% | 3.3% | 3.6% |
| Real speakers, current app | 0.2% | 0.1% | 0.0% | |

| With 5 normal days | Synthetic healthy | Synthetic slowed + tremor | Real healthy | Real slowed + tremor | Real hesitant |
|---|---|---|---|---|---|
| Current app | 6.5% | 12.5% | 0.1% | 2.5% | 92.6% |
| Capped | 2.8% | 7.4% | 0.0% | 2.0% | 89.2% |
| Learned from other speakers | 2.9% | 5.3% | 3.5% | 34.1% | 100% |

What this shows:

1. **More normal days don't fix the false alarms.** From 2 to 14 days the
   synthetic rate stays between 6.5% and 8%. The alarms come from single
   words: on nearly half of them the biggest change was a single "um",
   and most of the rest were one repeated word or one longer pause.
2. **Capping one-off words halves them.** If "um" and repeated words can
   count at most 1.5 spreads, and speaking rate is judged against a spread
   of at least 20 words a minute, healthy days alarm 3% of the time instead
   of 6.7%, and hesitant days are still caught 89% of the time.
3. **A 20% slowdown can't be told from a normal day by timing.** Real
   older speakers' speaking rate moves by about 21 words a minute from day
   to day (the app's floor assumes 12), which is as much as the slowdown.
   Weights learned from the other speakers caught it 34% of the time, but
   raised real healthy alarms to 3.5%, above their 2% target, and they
   were learned from changes made up for this test.
4. **Hesitation is the change the score reliably catches.** Longer starts
   and extra pauses were caught about 9 times in 10 with almost no alarms
   on real healthy days.

Limits: the real days are read sentences, which have almost no pauses,
"um"s or repeats, so they only test speaking rate and start time; the
synthetic days vary only in wording, not in how the voice sounds day to
day. Neither contains delirium. The changes are made up, so "caught"
means caught this kind of change, not delirium. None of this is applied
to the app: the capped scoring is a candidate to try once real check-ins
exist.

## The transcript fixes

In [scripts/robust.py](scripts/robust.py). Each comes from a mistake seen
in the comparison:

1. Sound-alike digits after a tens word: "eighty too" and "80 too" become 82.
2. Years split by punctuation: "20/26" becomes 2026.
3. A bare "twenty six" for the year, when no full year was said.
4. Countdown numbers glued into a year: "20, 1918, 17" becomes 20, 19, 18, 17.
5. An empty transcript when the clip has speech in it: ask again instead of
   counting a mistake.
6. An age, year or birthday answer with no number in it and no "don't
   know": ask again. This catches "I made it too" for "I'm eighty two",
   the most common single failure.

Fixes 5 and 6 ask the question again instead of scoring it. The tables
count a re-asked answer as correct for healthy people and as 0 points for
impaired ones, which is why a few impaired check-ins drop below 100%. With
Whisper small, about 1 check-in in 8 would need one question asked again.
The app should count a second answer with no number as a mistake.

## Limits

- The voices are synthetic. They are slowed and shaky, but they are not
  real 80-year-olds. Many "eighty two" failures come from the LibriTTS
  voices running "I'm eighty" together, which real people also do but maybe
  less often. The PC's held-out older speakers are the real-voice check.
- Models ran as sherpa-onnx ONNX exports, not the PyTorch weights the app
  loads; word error rates can differ by a point or so.
- The fixes were designed on this same test set. They are simple rules, but
  they should be re-checked on the PC's real recordings before trusting the
  exact numbers.
- Alertness and the family's "acute change" answer (4AT parts 1 and 4) were
  not tested; they don't depend on the transcript wording.

## Parakeet as a free option

Parakeet was the most accurate model in quiet rooms and four times faster
than Whisper small on CPU, but the worst with a TV on. If the app adds a
quiet-room check, it is worth offering.
[app-patch/sherpa_parakeet.py](app-patch/sherpa_parakeet.py) is a drop-in
`STT_PROVIDER=parakeet` option. It returns word timestamps in the app's
`Word` format, which was checked on an m4a clip through the app's
`clip_features`.

## Files

The m4a fix, the transcript fixes and the Parakeet option have since been
applied to the app in [PR #2](https://github.com/bemah123456/north-2/pull/2);
the copies under `app-patch/` and `scripts/robust.py` are the versions this
study measured.


- `scripts/`: build the clips (`make_audio.py`, and `make_tv_levels.py` for
  the TV levels), the quiet-room check (`noise_check.py`,
  `analyze_levels.py`), run a model
  (`run_asr.py` for ONNX, `run_hf.py` for a Hugging Face folder such as the
  PC's fine-tuned model), score (`analyze.py`), fixes (`robust.py`), the voice-change
  tests (`voice_change.py`, and `voice_days_transcribe.py`,
  `voice_days_synth.py` and `voice_baseline_study.py` for the normal-days study).
- `results/summary.json`: every number above, per model, condition and scorer.
- `results/errors.jsonl`: every healthy answer marked wrong and impaired
  answer marked right, with what was said and what the model heard.
- `results/transcripts.jsonl`, `results/clips_manifest.jsonl`: raw outputs.
- `app-patch/`: the m4a fix (diff with tests) and the Parakeet provider.

The 449 MB of generated audio is not kept; `make_audio.py` rebuilds it
from the voice models in about half an hour.
