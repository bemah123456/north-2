# Sharper detection check (PR #12)

`eval_voice.py` replays the cloud research's voice days (`research/cloud-4at-asr/results/voice_days*.jsonl`) through the app's combined change score (`daily-checkin/server/checkin/change.py`), using 5 normal days as each speaker's baseline. It compares how often the old voice-only rule gave 4 points with how often the combined score says "keep an eye" or "big change".

Run from the repo root: `python3 research/sharper-detection/eval_voice.py` (needs numpy).

Result on 2026-10-21: hesitant real voices reach "keep an eye" 88% of the time but never "big change" on voice alone; healthy normal days stay at 0% (real) and 2.1% (synthetic). The weights are hand-set on simulated days and still need checking on real check-ins.

`screenshots/` shows the digit span question (morning and evening), the evening check-in setting, and the family detail view as built in PR #12.
