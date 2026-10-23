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
- The round 2 model was re-scored in the cloud first (`training/out/comparison_cloud_baseline.md`): same 8.3% quiet,
  12.9% background talk and same probe results as on the PC, so the copied model and test set are intact.
- On CPU, training the whole model takes about 80 s per 8 clips here (4x the PC). Freezing the encoder
  (`--freeze-encoder`) brings that to about 18 s, so cloud rounds train the decoder, which is where months
  and numbers get written out.
- New session: `training/restore_cloud.sh` rebuilds the work folder from the project files.

## Kaggle GPU rounds (from 2026-10-21)

Training moved to Kaggle's free T4 GPU as private script jobs (`training/build_kaggle.py` packs the scripts,
`kaggle kernels push` runs them). Everything is rebuilt from public data (Common Voice 17 speakers aged 60+,
CC0), and the job stops unless the test set is the same 360 clips from 44 held-out speakers, so every round
is comparable. Keep rule: a model replaces the best only if its quiet + background-talk word error rate is
lower and month/number/day recall doesn't drop.

| Round | What changed | Quiet | Background talk 10 dB | Quiet + talk | Recall | Tables |
|---|---|---|---|---|---|---|
| Stock Whisper small | - | 8.6% | 32.9% | 41.5% | 38/39 | `out/comparison_kaggle_rounds.md` |
| 3a (Whisper small) | rounds 1-2 rebuilt, then months/numbers 35%, 900 steps | 8.4% | 12.6% | 21.1% | 39/39 | same |
| 3b, 4a, 4b | longer, gentler or louder-talk rounds on small | 8.5-8.8% | 15-18% | worse | | `out/comparison_kaggle_round4.md` |
| **5 (Whisper large-v3-turbo), best** | turbo fine-tuned with 3a's recipe, 1,200 steps | **5.6%** | **8.4%** | **14.1%** | 39/39 | `out/comparison_kaggle_round5.md` |

Round 5's paired 95% interval against 3a is -8.7 to -4.9 points (a third fewer errors, well outside noise).

### Why round 5 changed what it did
- **A bigger model, not more steps.** Rounds 3b-4b showed small had stopped improving on this data. Turbo has
  large-v3's 32-layer encoder (trained on about 5 million hours, so it separates one voice from others far
  better) with a 4-layer decoder, so it decodes almost as fast as small. Stock it was better in quiet but
  worse with background talk; fine-tuned on older speakers with background talk it beats 3a on both.
  The whole model is trained with 8-bit Adam and gradient checkpointing (11.3 GB peak on a 15 GB T4,
  about 12.5 s a step, 4.3 hours for 1,200 steps).
- **Scored the way the server decodes.** The rule still uses greedy decoding, as every earlier round, but each
  model is also run through faster-whisper int8 with beam 5 and word timestamps, exactly like
  `checkin/transcribe.py` (`training/fw_score.py`), and timed on the CPU.
- **Paired intervals.** A 360-clip test can't separate two models by overlapping intervals; resampling the 44
  speakers for both models together gives the interval of the difference, which says "better", "worse" or
  "within noise".
- **Unseen voices.** The background-talk test and the training noise are both Common Voice speech, so a third
  condition mixes in LibriSpeech readers (CC BY 4.0) at 10 dB. Turbo fine-tuned: 8.1% (3a: 12.3%), so the gain
  isn't just learning Common Voice's babble.
- **Checkpoint averaging** (steps 800/1,000/1,200) was within noise of the last checkpoint, so it isn't used.
- **More public older-speaker data** wasn't the lever: all 44k Common Voice English clips aged 60+ are already
  used; other English corpora with older speakers aren't permissively licensed or have no age labels.

### Cost: speed
Measured the server's way (faster-whisper int8, beam 5, word timestamps, median of short answers):

| Machine | Turbo (round 5) | Small (round 3a) |
|---|---|---|
| Kaggle CPU, 2 threads | 12.3 s | 3.5 s |
| Apple A18 Pro laptop, 2 threads | 12.6 s | 2.9 s |
| Apple A18 Pro laptop, 6 threads | 7.4 s | 2.1 s |

The encoder runs on a full 30-second window whatever the answer's length, so turbo is 3.5 to 4.5 times slower
on a CPU. A GPU server, or transcribing each answer while the next question is read out, hides the wait;
otherwise keep round 3a where 7 to 12 s per answer is too long.

### Swap the round 5 model into the testing server
```
python3 training/fetch_kaggle_output.py benjaminmahmutovic/north2-whisper-round5 ~/models/round5 whisper-round5-best-ct2/
LOCAL_WHISPER_ENGINE=faster-whisper FASTER_WHISPER_MODEL=~/models/round5/whisper-round5-best-ct2 FASTER_WHISPER_COMPUTE=int8
```
(`fetch_kaggle_output.py` resumes the 814 MB `model.bin` when Kaggle's storage drops the connection, which
`kaggle kernels output` doesn't.) Restart the server; nothing else changes (same tokenizer, same word timestamps; the folder carries the
128-band `preprocessor_config.json` turbo needs). To go back, point `FASTER_WHISPER_MODEL` at the round 3a
folder. The 16-bit weights are in the same job's output as `whisper-round5-best-fp16/`.

### Run a round
```
python3 build_kaggle.py <user> --slug north2-whisper-round5 --from-kernel <user>/north2-whisper-rounds --script kaggle_round5.py [--smoke]
kaggle kernels push -p kaggle/north2-whisper-round5
```
Kaggle's GPU jobs have two T4s; rounds use one, so splitting training across both would halve the time.

## Paid option (not used)
A rented GPU would make full-model rounds take minutes instead of a day, at roughly $0.50 to $1 an hour,
but it needs an account and money, so it waits for the user's yes.
