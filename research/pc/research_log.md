# Research log (read this first on each check-in)

Goal: detect delirium in older adults from their voice; current plan is a spoken 4AT app (phone), family member answers the "acute change" item.

Rules: work only in this folder; never touch the Roblox game repo. No accounts, no payments, no large downloads, no emailing authors without asking the user.

## Rounds
- Round 1 (2026-10-19, done): public clips and datasets -> delirium_speech_sources.md. Finding: no open delirium speech corpus; best clips are 3D-CAM Vimeo videos (P2, P3 Day 2 = delirium).
- Round 2 (2026-10-19, done): GPT studies + Gemini feature spec, checked and merged into findings.md. Helper scheduled task: script written (helpers\run_helpers.ps1), waiting for the user's in-thread yes before queueing questions and registering it.

- Round 3 (2026-10-19, done): data strategy, regulation, speech recognition -> findings.md. Prototype built in prototype/ (scorer.js, index.html, 15 tests pass). Research judged enough for the prototype. Training a real delirium detector is blocked on data; asked the user which path (Common Voice elderly ASR tuning / DementiaBank application / contacting research groups). Do not start any of these without their answer.

- Training (2026-10-19): user chose paths A and B. A: scripts ready in training/ (prepare_cv.py selects speakers 60+ from Common Voice and splits by speaker; finetune_whisper.py fine-tunes whisper-base on CPU and reports word error rate and month/number recall before and after). Python 3.12 installed (user said "proceed"); venv at training\.venv with torch 2.14 CPU + transformers; pipeline smoke-tested on synthetic clips (works; digits/ordinals normalised so Whisper "84" matches "eighty four"). Run: training\.venv\Scripts\python.exe -I training\prepare_cv.py data --hours 10, then finetune_whisper.py --eval-only first, then --steps 2000 in the background. Still waiting on the user downloading Common Voice from mozilladatacollective.com into data\ (sign-in needed; we must not create accounts). PC: i5-9400, 32 GB RAM, AMD RX 5500 (no CUDA), 783 GB free. B: user sent DementiaBank sign-up steps; needs institutional status or a sponsor.

- Data (2026-10-19): MDC needs an account, so used the public HF copy saeedzou/common-voice-17-en-age-gender-accent (CC0) via training\fetch_cv17_older.py: 12,569 clips aged 60+ from 449 speakers in data\cv17_older. Manifests: 10,080 train clips (~14 h), 360 test clips from 44 held-out speakers.
- Training started 2026-10-19 ~14:00: whisper-base, 1200 steps, CPU (log: training\train.log; weights -> training\out\whisper-base; numbers -> training\out\results.md).
- User asked (2026-10-19): after training, compare against other models and assess false positives. Ready: compare_models.py (tiny/base/small/distil-small.en/tuned on held-out older speakers + 90 synthetic 4AT probes clean and 10 dB noise, scored with prototype/scorer.js via probe_score.js) -> training\out\comparison.md. Run: .venv\Scripts\python.exe -I compare_models.py openai/whisper-tiny openai/whisper-base openai/whisper-small distil-whisper/distil-small.en out/whisper-base

- Coordinator note (2026-10-19): the daily check-in app (other thread, /mnt/project-files/daily-checkin/server/checkin/transcribe.py) uses the transformers ASR pipeline with return_timestamps="word"; LOCAL_WHISPER_MODEL takes an HF id or folder. After training, verify training\out\whisper-base gives word timestamps (alignment_heads kept in generation_config) so that app can load it.

## Queue for later rounds (rounds 3-4 below are now covered)
- Round 3: data strategy without a public corpus (consent, recording protocol, synthetic/acted data, partnering with Northwell or Edinburgh groups); regulatory basics (FDA SaMD / wellness claims).
- Round 4: on-device tech check (Whisper/Vosk word timings on elderly speech, months-backward scoring from transcript).
- Next step once enough: build a prototype spoken-4AT web page (browser mic + speech recognition), rule-based scoring, tested on the public demo videos. "Training" a model is not possible yet: no labelled delirium audio is available.
