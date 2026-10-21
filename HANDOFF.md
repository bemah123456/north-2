# Handoff

Last updated 2026-10-21 (PR #24). A short, current summary of North 2. Every piece of finished work updates this file in the same pull request.

## Goal

A voice check-in that helps families catch delirium in older relatives early. The older person answers a few short spoken questions each day (based on the 4AT test); the app scores the answers and compares their voice with their own normal days, and tells family when something has changed.

## Built and merged into `main`

- **The app** (`daily-checkin/`), PRs #1 to #5, #8, #10 to #15: Python scoring server, Expo phone app for the older person and their family, Supabase schema, reminders, missed check-in alerts, the in-app server address setting, a Dockerfile, and the senior-friendly redesign (#15). How to run it: `daily-checkin/README.md`. Launch steps: `daily-checkin/LAUNCH.md`.
- **Sharper detection** (#12): daily digit span, an optional evening check-in, drowsiness signs, and a combined change score so the voice alone can't trigger "call the doctor". Check script: `research/sharper-detection/`.
- **Research**: speech model comparison and transcript fixes (`research/cloud-4at-asr/`), normal-days study (#6: ignoring one-off "um"s and repeats halved voice false alarms), PC model training (`research/pc/`, including the fine-tune results in `RESULTS-finetune-2026-10-20.md`), speech sources and competitors (`research/*.md`).
- **Recommended speech setup**: Whisper small with a month-list hint, the transcript fixes (`robust.py`), plus "ask again if exactly one month is missing". Our fine-tuned Whisper small is slightly better (8.3% vs 8.6% word errors on 44 older speakers, intervals overlap) with the same 0% clean / 2% noisy false positives; the 926 MB model stays on the PC. Not yet tested on real delirium recordings. Comparison dashboard: https://claude.ai/artifact/9o9DLdos6uvuh5eGuhJ4Dj
- **Background TV** is the biggest cause of false alarms. The quiet-room check asks 1.7% of real no-TV check-ins and 99% of TV check-ins to turn the TV off.
- **Android test app**: built 2026-10-20 from the redesign. The 36 MB APK is in the Claude project files at `launch/daily-checkin-test.apk`; install steps in `daily-checkin/ANDROID-TEST-APP.md`.
- **Family hears the check-in** (claude/family-listen): when a check-in with recorded answers is done, the family gets a message with the result and a private link that plays the whole check-in (question read aloud, then their answer). The family view has the same, plus "Hear their answer" per answer. Sharing is on by default (the setup screen already tells families the answers are recorded and shared) and can be turned off. Set `PUBLIC_URL` to the tunnel address so the link goes in the message.

- **Clari redesign** (claude/clari-redesign): the app is now called Clari, with the logo, its navy and blue-to-mint colours, Nunito and Atkinson Hyperlegible type, SVG icons, and calm animations (listening rings that follow the voice, a breathing start button, a done tick). All of it respects the phone's reduce-motion setting; text stays at 7:1 contrast. Screens: `daily-checkin/screenshots/clari/`.

## In progress

- PC training round 2 is finished: Whisper small v2 (trained with background talk mixed in, 31,500 clips from 454 speakers over 60) gets 8.3% word errors in quiet, the same as v1, with month/number recall 37/39. The background-talk comparison (stock small, Distil-Whisper, tuned v1 and v2) is running on the PC, about 1.5 hours left as of 2026-10-21 02:41 UTC; results go to `research/pc/training/out/comparison_round2.md`. Earlier run: with background talk, tuned small got 22.9% word errors vs 32.9% for stock. The PC side's own notes: `research/pc/HANDOFF-pc.md`.
- Rerunning the voice-change test on unscripted speech from people over 60 (Santa Barbara Corpus), once the PC thread delivers it. All voice tests so far use read or synthetic speech.
- Open PRs from the hackathon build thread, all with green checks and waiting on the user's typed merge line in that thread:
  - #16: brings the home test plan (`daily-checkin/HOME-TESTING.md`) up to date with the merged app.
  - #17: copies of the pitch deck, pitch script and one-page summary in `daily-checkin/submission/` (the live versions are Claude artifacts: deck https://claude.ai/artifact/NSYfpvN1PXQqLioYZnZRzV, script https://claude.ai/artifact/CVy5eqNcaKWJTkT1Qtn5bJ, summary https://claude.ai/artifact/C9ZRMchkCXuRyZsPstwZ8x).
  - #19: server survives bad settings and broken recordings; no "missed" text on setup day; worded hand scores don't crash the report.
  - #20: a check-in that runs past midnight is scored against its own questions (it gave "call the doctor" to healthy answers); one dropped digit costs one point, not two.
  - #21: family view can undo "they seem different"; "day off tomorrow" marks the right day.
  - #22: malformed check-ins get a clear 400 instead of a 500; evening ratings count in the testing report.
  - #23: senior home screen notices the evening check-in opening; real birth dates at setup; greeting no longer says "Good morning" in the afternoon.
  - #25: with a check-in time of 21:00 or later, the family alert falls after midnight and was never sent; now it is.
  - #28: split numbers ("9-5" for 95, "2000 in 26") are read whole, impossible ages are asked again, and a birthday with one dropped digit goes to a person; from the accented-voice test in PR #27 (healthy answers scored wrong 12% to about 1%).
  - All of these merge together cleanly in PR-number order; together they pass 106 server tests and the app typecheck (checked 2026-10-21).

## Waiting on the user

- In the PC thread, type "yes, download and share the Santa Barbara list" so the unscripted older-speaker data can be used.
- Team names for the hackathon, and a yes to make the code public.
- To merge the hackathon build PRs, the user types "merge PRs 16, 17, 19, 20, 21, 22, 23, 24, 25 and 28" in that thread (relayed approval is blocked).
- For a store release: an Expo account, where to host the server, Apple/Google developer accounts, and the medical-device wording (see `daily-checkin/LAUNCH.md`).

## On hold

- Six suggested features, until the user says so: FAM-CAM questions, post-hospital mode, trigger questions, doctor report, guided first week, consented recordings.
- Outreach emails for real delirium speech data (Northwell, Edinburgh, DementiaBank). Drafts are kept in PR #9; nothing is sent.

## Kept out of the repo

These live only in the Claude project files:

- `launch/daily-checkin-test.apk` (36 MB): a built binary; rebuild from `daily-checkin/app` instead.
- `speaker_days.zip` (7.8 MB, 200 Common Voice MP3s): audio input to the normal-days study; the per-clip features it produced are in `research/cloud-4at-asr/results/voice_days.jsonl`.
- `research-pc-results.zip`: unpacked into `research/pc/` instead of committing the zip; the raw training logs are in `research/pc/training/logs/` (Windows user folder replaced by `%USERPROFILE%`, duplicate `compare_first3.log` dropped). Its `RESULTS.md` is older than the repo's.
- Trained model weights (Whisper base/small/small-v2, ~926 MB each for small): stay on the PC.
- `daily-checkin/daily-checkin.git.bundle` and the old `daily-checkin/` copy: the original import, superseded by this repo's history.
- `outreach/`: in PR #9 (on hold).
- `.pyc` files, `app-redesign/before-after.png` and `daily-checkin/submission/*.png`: caches or older versions of screenshots already here.
- The Santa Barbara speaker list and anything else with personal data is never added here.
