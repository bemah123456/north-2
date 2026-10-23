# HANDOFF: delirium voice research, PC side (updated 2026-10-20 22:45)

Folder on the PC: %USERPROFILE%\Documents\Delirium Speech Research (not the Roblox repo).
This PC has no GitHub login for bemah123456/north-2, so results go to the project files and the
cloud thread puts them in the repo under research/.

## Where things stand
- Research rounds 1-3 done: findings.md (sources, studies, regulation, data strategy).
  Main finding: no public delirium speech dataset; a voice-scored 4AT has not been published.
- Prototype: prototype/index.html + scorer.js (official 4AT rules, "ask again" when exactly one
  month is missing; 16 tests pass with `node --test`).
- Speech model training (CPU, i5-9400, ~40 s per step for Whisper small):
  - Data: Common Voice 17 English speakers aged 60+ (CC0, Hugging Face copy, no sign-up).
    31,500 training clips (44 h, 454 speakers); test = 360 clips from 44 held-out speakers.
  - Models in training/out (kept on the PC; too big to share): whisper-base (12.4% WER),
    whisper-small (8.3%), whisper-small-v2 (8.3% in quiet; trained with background talk mixed in).
  - Best setup so far: our tuned Whisper small + month-list prompt: 8.3% WER vs 8.6% stock small,
    0% false 4AT failures in quiet, 2% in noise, 0 missed impairments (synthetic 4AT probes).
    With background talk, tuned small 22.9% WER vs 32.9% stock.
- Results: research-pc/RESULTS.md; training/out/*.md tables.

## Move to the cloud (2026-10-21): PC going offline
- Everything except model weights and audio is in /mnt/project-files/research-pc-final.zip:
  training/*.py, *.ps1, *.js, logs, out/*.md result tables, manifests (train_v2.csv lists the
  43,067 training clips and test.csv the 360 test clips by Common Voice file name and client_id),
  prototype/, findings.md, research_log.md, RESULTS.md, this file.
- Not shared: tuned models (out/whisper-base 290 MB, whisper-small 926 MB, whisper-small-v2 926 MB;
  project-file limit is 20 MB) and the audio (data/cv17_older, ~3 GB). To rebuild in the cloud:
  run training/fetch_cv17_older.py (Hugging Face dataset saeedzou/common-voice-17-en-age-gender-accent,
  CC0, no sign-up; needs Hugging Face reachable), then extend_train_manifest.py, then
  finetune_whisper.py from openai/whisper-small with the settings in research_log.md.
- Round 3 was planned (from the best model: --augment --key-frac 0.35, 900 steps, lr 4e-6) but not
  started, per the user's move to the cloud.

## Running / next (as of the move)
- Round 2 comparison (stock small, Distil-Whisper, tuned small, tuned small v2; quiet + background
  talk) -> training/out/comparison_round2.md. Then update RESULTS.md and share.
- Santa Barbara corpus (unscripted speech, 8 speakers aged 60-90): segment list built on the PC
  (research-pc/speaker_days_unscripted/segments.csv, names removed). Downloading audio and sharing
  are blocked by the safety check until the user types approval in the PC thread.

## Rules from the user
- No emails or outside contact. No sign-ups. New app features are on hold.
- Keep this file current; get work into GitHub (via the cloud thread) before the weekly limit.
- Never share model weights or personal data; share scripts and result tables.

## How to resume
- Read research_log.md (full history) then this file.
- Python venv: training\.venv. Re-run a comparison:
  `training\.venv\Scripts\python.exe -I training\compare_models.py --talk <models...>`
