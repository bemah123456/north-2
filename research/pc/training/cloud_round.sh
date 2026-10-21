#!/bin/bash
# One cloud training round: fine-tune from the best model so far, score it on the same 44 held-out
# older speakers (quiet + background talk + 4AT probes), and report whether it beat the best.
# Resumable: rerun the same command after a restart and training continues from its checkpoint.
# Usage: cloud_round.sh <out-name> [extra finetune args...]
set -e
cd "$(dirname "$0")"
NAME=$1; shift
BEST=$(python3 -I next_round.py)
echo "round $NAME from $BEST  $(date -u)"
if [ ! -f out/$NAME/model.safetensors ]; then
  python3 -I finetune_whisper.py --model "$BEST" --out-name "$NAME" --train-manifest train_v2.csv \
    --skip-start-eval --eval-n 0 "$@"
fi
python3 -I compare_models.py out/$NAME@prompt --talk --out comparison_$NAME.md
NEW=$(python3 -I next_round.py)
echo "best after $NAME: $NEW  $(date -u)"
