# Older-voice speech recognition, run on the PC

Results from the PC session (2026-10-19 to 20), copied from the project's
`research-pc-results.zip`. Start with [RESULTS.md](RESULTS.md).

- Real older speakers: 360 Common Voice 17 clips from 44 held-out speakers
  aged 60+, comparing Whisper tiny, base, small, Distil-Whisper small.en and
  Whisper base fine-tuned on 14 h of older speakers.
- 4AT false positives: 90 Windows-voice answer clips scored with
  `prototype/scorer.js`, with and without a months prompt for Whisper.
- `findings.md` and `research_log.md` are the earlier research rounds
  (studies, regulation, data strategy) behind the prototype.

Left out: the training logs (the tables are in `training/out/`), the
duplicate `delirium_speech_sources.md` (already in `research/`) and the
fine-tuned model weights (256 MB, kept on the PC; not the recommended model).
