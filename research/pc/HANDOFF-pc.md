# HANDOFF: delirium voice research, PC side (copied from the PC thread 2026-10-21)

Folder on the PC: the "Delirium Speech Research" folder in Documents (not the Roblox repo).
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
- Results: research/pc/RESULTS.md and RESULTS-finetune-2026-10-20.md; training/out/*.md tables; raw console logs in training/logs/.

## Running / next
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
