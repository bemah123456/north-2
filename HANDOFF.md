# Handoff

Last updated 2026-10-23 (all hackathon PRs merged). A short, current summary of North 2. Every piece of finished work updates this file in the same pull request.

## Goal

A voice check-in that helps families catch delirium in older relatives early. The older person answers a few short spoken questions each day (based on the 4AT test); the app scores the answers and compares their voice with their own normal days, and tells family when something has changed.

## Built and merged into `main`

- **The app** (`daily-checkin/`), PRs #1 to #5, #8, #10 to #15: Python scoring server, Expo phone app for the older person and their family, Supabase schema, reminders, missed check-in alerts, the in-app server address setting, a Dockerfile, and the senior-friendly redesign (#15). How to run it: `daily-checkin/README.md`. Launch steps: `daily-checkin/LAUNCH.md`.
- **Sharper detection** (#12): daily digit span, an optional evening check-in, drowsiness signs, and a combined change score so the voice alone can't trigger "call the doctor". Check script: `research/sharper-detection/`.
- **Research**: speech model comparison and transcript fixes (`research/cloud-4at-asr/`), normal-days study (#6: ignoring one-off "um"s and repeats halved voice false alarms), PC model training (`research/pc/`, including the fine-tune results in `RESULTS-finetune-2026-10-20.md`), speech sources and competitors (`research/*.md`).
- **Hackathon build, merged 2026-10-23** (PRs #16 to #42, except #9): home test plan, pitch deck, script, summary and demo videos (`daily-checkin/submission/`), server robustness and scoring fixes, the accent answer fixes (#27, #28), faster-whisper, the Clari redesign and everything stacked on it (easy join, questions read aloud, quieter-spot prompt, family calendar, family tabs and text, How Clari works and Ask Clari), the locally built Android APK (`daily-checkin/app/BUILD-ANDROID.md`), Gemini (off by default), and the cloud and Kaggle speech training rounds.
- **Recommended speech setup**: faster-whisper with our fine-tuned Whisper small (round 3a), a month-list hint, the transcript fixes (`robust.py`), plus "ask again if exactly one month is missing": 8.4% word errors in quiet and 12.6% with background talk on 44 held-out older speakers, 39/39 months and numbers, about 2 to 3.5 s per answer on a CPU. Round 5's fine-tuned Whisper large-v3-turbo is clearly more accurate (5.6% / 8.4%, a third fewer errors) but 3.5 to 4.5 times slower (7 to 12 s per answer on a CPU), so use it only on a GPU or a fast server; swap steps and results in `research/pc/CLOUD-TRAINING.md`. Weights are not committed (Kaggle job outputs and Claude project files). Not yet tested on real delirium recordings. Comparison dashboard: https://claude.ai/artifact/9o9DLdos6uvuh5eGuhJ4Dj
- **Background TV** is the biggest cause of false alarms. The quiet-room check asks 1.7% of real no-TV check-ins and 99% of TV check-ins to turn the TV off.
- **Android app**: build the signed Clari APK locally with `daily-checkin/app/scripts/build-android.sh` (`daily-checkin/app/BUILD-ANDROID.md`). The older 2026-10-20 test APK is in the Claude project files at `launch/daily-checkin-test.apk`.
- **Family hears the check-in** (claude/family-listen): when a check-in with recorded answers is done, the family gets a message with the result and a private link that plays the whole check-in (question read aloud, then their answer). The family view has the same, plus "Hear their answer" per answer. Sharing is on by default (the setup screen already tells families the answers are recorded and shared) and can be turned off. Set `PUBLIC_URL` to the tunnel address so the link goes in the message.

- **Clari redesign** (claude/clari-redesign): the app is now called Clari, with the logo recoloured to one solid teal, flat solid colours only (no gradients: navy text and buttons, teal graphics), Nunito and Atkinson Hyperlegible type, SVG icons, and calm animations (listening rings that follow the voice, a breathing start button, a done tick). All of it respects the phone's reduce-motion setting; text stays at 7:1 contrast. Screens: `daily-checkin/screenshots/clari/`.

- **Gemini, off by default** (claude/gemini-integration): three flags, each with a fallback to today's behaviour. `GEMINI_TRANSCRIBE=1` takes the words from Gemini and keeps Whisper's word timings for the voice measures; `JUDGE_ENGINE=gemini` lets Gemini listen to answers the rules can't settle; `GEMINI_SPEECH_NOTE=1` adds a 0-3 "unusual speech" rating worth at most 1 point of the change score, never more than the other evidence, so it can't alarm alone. Vertex AI (production, zero data retention + BAA) or a Developer API key (synthetic audio only). Model pinned to `gemini-3.6-flash` (2.5-flash is closed to new keys). Whether Gemini's words become the default waits on the older-speaker benchmark. Env vars: `daily-checkin/README.md`; privacy: `daily-checkin/LAUNCH.md`.

## In progress

- Gemini against our Whisper on the same 360 older-speaker clips (`research/pc/training/gemini_bench.py`, both the plain and the server's prompt, `gemini-3.6-flash`): waiting on billing for the Gemini key, since the free tier allows 20 requests a day and each prompt needs about 1,080. Gemini's words stay off until it beats round 5 turbo there.
- Rerunning the voice-change test on unscripted speech from people over 60 (Santa Barbara Corpus), once the PC thread delivers it. All voice tests so far use read or synthetic speech.

## Waiting on the user

- In the PC thread, type "yes, download and share the Santa Barbara list" so the unscripted older-speaker data can be used.
- Team names for the hackathon, and a yes to make the code public.
- Billing on the Gemini API key (roughly $1 to $2 per benchmark prompt), so the Gemini benchmark can run. For real people's voices, Vertex AI with zero data retention and a BAA instead (see `daily-checkin/LAUNCH.md`).
- A last look at the pitch deck and demo video against the current app before submitting (due 2026-10-26).
- For a store release: an Expo account, where to host the server, Apple/Google developer accounts, and the medical-device wording (see `daily-checkin/LAUNCH.md`).

## On hold

- Six suggested features, until the user says so: FAM-CAM questions, post-hospital mode, trigger questions, doctor report, guided first week, consented recordings.
- Outreach emails for real delirium speech data (Northwell, Edinburgh, DementiaBank). Drafts are kept in PR #9; nothing is sent.

## Kept out of the repo

These live only in the Claude project files:

- `launch/daily-checkin-test.apk` (36 MB): a built binary; rebuild from `daily-checkin/app` instead.
- `speaker_days.zip` (7.8 MB, 200 Common Voice MP3s): audio input to the normal-days study; the per-clip features it produced are in `research/cloud-4at-asr/results/voice_days.jsonl`.
- `research-pc-results.zip`: unpacked into `research/pc/` instead of committing the zip; the raw training logs are in `research/pc/training/logs/` (Windows user folder replaced by `%USERPROFILE%`, duplicate `compare_first3.log` dropped). Its `RESULTS.md` is older than the repo's.
- Trained model weights and training audio: project files `models/` and the Kaggle jobs' private outputs; the user asked not to commit or share them.
- `daily-checkin/daily-checkin.git.bundle` and the old `daily-checkin/` copy: the original import, superseded by this repo's history.
- `outreach/`: in PR #9 (on hold).
- `.pyc` files, `app-redesign/before-after.png` and `daily-checkin/submission/*.png`: caches or older versions of screenshots already here.
- The Santa Barbara speaker list and anything else with personal data is never added here.
