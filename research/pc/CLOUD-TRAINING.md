# Speech model training in the cloud (from 2026-10-21)

The PC is offline, so training moved to the Claude cloud machine (4 CPUs, 15 GB RAM, no GPU).
Hugging Face is blocked from the cloud, so the PC's models and audio were copied over directly
and checked against their SHA-256 sums (models) and zip CRCs (audio).

## Where things are kept (Claude project files, `models/`)
- `whisper-small-v2-fp16/`: the best model so far (round 2), 16-bit, in 32 pieces under 19 MB with
  `model.safetensors.sha256`. Rebuild: `cat model.safetensors.part* > model.safetensors`.
- `training-data/`: all 44,352 Common Voice clips from speakers aged 60+ (CC0) plus the manifests,
  the 360 test clips from 44 held-out speakers and the 90 synthetic 4AT probes, as tar pieces.
- Model weights and audio are not committed here (too big, and the user asked not to share them).

## Round results (same 44 held-out older speakers, month hint on)

| Round | Trained on | Quiet WER | With background talk 10 dB | Month/number recall | 4AT false positives (clean / hiss / talk) |
|---|---|---|---|---|---|
| Stock Whisper small | - | 8.6% | 32.9% | 38/39 | 0 / 1 / 1 of 42 |
| 1 (PC) | 10k clips, 600 steps | 8.3% | 22.9% | 38/39 | 0 / 1 / 0 of 42 |
| **2 (PC), best** | 31.5k clips with background talk mixed in, 900 steps | **8.3%** | **12.9%** | 37/39 | 0 / 2 / 1 of 42 |
| 3 (cloud) | from round 2: months/numbers oversampled (35% of each batch), background talk, decoder only, 600 steps | running | | | |

Full tables: `training/out/comparison_round2.md` (PC). Cloud tables are added as `comparison_<model>.md`.
Without the month hint, round 2 has the same word errors but 3/42 false positives with hiss, so keep the hint on.

## How a round works
- `training/cloud_round.sh <new-name> <finetune args>`: trains from the current best
  (`next_round.py`: lowest quiet + background-talk WER among models scored in the cloud), then scores the new model.
  It is kept as the new best only if its combined score is lower. Checkpoints every 50 steps, so rerunning
  the same command after a restart resumes.
- The round 2 model was re-scored in the cloud first (`comparison_cloud_baseline.md`) so every later round
  is compared on the same machine and software.
- On CPU, training the whole model takes about 80 s per 8 clips here (4x the PC). Freezing the encoder
  (`--freeze-encoder`) brings that to about 18 s, so cloud rounds train the decoder, which is where months
  and numbers get written out.
- New session: `training/restore_cloud.sh` rebuilds the work folder from the project files.

## Paid option (not used)
A rented GPU would make full-model rounds take minutes instead of a day, at roughly $0.50 to $1 an hour,
but it needs an account and money, so it waits for the user's yes.
