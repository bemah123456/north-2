# Handoff

Last updated 2026-10-21. A short, current summary of North 2. Every piece of finished work updates this file in the same pull request.

## Goal

A voice check-in that helps families catch delirium in older relatives early. The older person answers a few short spoken questions each day (based on the 4AT test); the app scores the answers and compares their voice with their own normal days, and tells family when something has changed.

## Built and merged into `main`

- **The app** (`daily-checkin/`), PRs #1 to #5, #8, #10 to #15: Python scoring server, Expo phone app for the older person and their family, Supabase schema, reminders, missed check-in alerts, the in-app server address setting, a Dockerfile, and the senior-friendly redesign (#15). How to run it: `daily-checkin/README.md`. Launch steps: `daily-checkin/LAUNCH.md`.
- **Sharper detection** (#12): daily digit span, an optional evening check-in, drowsiness signs, and a combined change score so the voice alone can't trigger "call the doctor". Check script: `research/sharper-detection/`.
- **Research**: speech model comparison and transcript fixes (`research/cloud-4at-asr/`), normal-days study (#6: ignoring one-off "um"s and repeats halved voice false alarms), PC model training (`research/pc/`, including the fine-tune results in `RESULTS-finetune-2026-10-20.md`), speech sources and competitors (`research/*.md`).
- **Recommended speech setup**: Whisper small with a month-list hint, the transcript fixes (`robust.py`), plus "ask again if exactly one month is missing". Our fine-tuned Whisper small is slightly better (8.3% vs 8.6% word errors on 44 older speakers, intervals overlap) with the same 0% clean / 2% noisy false positives; the 926 MB model stays on the PC. Not yet tested on real delirium recordings. Comparison dashboard: https://claude.ai/artifact/9o9DLdos6uvuh5eGuhJ4Dj
- **Background TV** is the biggest cause of false alarms. The quiet-room check asks 1.7% of real no-TV check-ins and 99% of TV check-ins to turn the TV off.
- **Android test app**: built 2026-10-20 from the redesign. The 36 MB APK is in the Claude project files at `launch/daily-checkin-test.apk`; install steps in `daily-checkin/ANDROID-TEST-APP.md`.

## In progress

- PC training round 2 is finished: Whisper small v2 (trained with background talk mixed in, 31,500 clips from 454 speakers over 60) gets 8.3% word errors in quiet, the same as v1, with month/number recall 37/39. The background-talk comparison (stock small, Distil-Whisper, tuned v1 and v2) is running on the PC, about 1.5 hours left as of 2026-10-21 02:41 UTC; results go to `research/pc/training/out/comparison_round2.md`. Earlier run: with background talk, tuned small got 22.9% word errors vs 32.9% for stock. The PC side's own notes: `research/pc/HANDOFF-pc.md`.
- Rerunning the voice-change test on unscripted speech from people over 60 (Santa Barbara Corpus), once the PC thread delivers it. All voice tests so far use read or synthetic speech.
- PR #16: brings the home test plan (`daily-checkin/HOME-TESTING.md`) up to date with the merged app.

## Waiting on the user

- In the PC thread, type "yes, download and share the Santa Barbara list" so the unscripted older-speaker data can be used.
- Team names for the hackathon, and a yes to make the code public.
- A yes to merge PR #16 (and this one).
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
