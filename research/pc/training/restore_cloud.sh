#!/bin/bash
# Rebuild the cloud training folder from the Claude project files (no PC, no Hugging Face needed).
# Usage: restore_cloud.sh [work dir, default /home/user/work]
set -e
W=${1:-/home/user/work}
P=/mnt/project-files/models
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$W/out" "$W/prototype"
cp "$HERE"/*.py "$HERE"/*.sh "$HERE"/probe_score.js "$W/"
cp "$HERE/../prototype/scorer.js" "$W/prototype/"
mkdir -p "$(dirname "$W")/prototype" && cp "$HERE/../prototype/scorer.js" "$(dirname "$W")/prototype/"  # probe_score.js loads ../prototype
cd "$W"
cat "$P"/training-data/eval-and-manifests.tar.part* | tar xf -
cat "$P"/training-data/train-clips.tar.part* | tar xf -
for m in "$P"/whisper-small-v*-fp16; do   # newest best model(s) saved as fp16 pieces
  name=$(basename "$m" -fp16); mkdir -p "out/$name"; cp "$m"/*.json "out/$name/"
  cat "$m"/model.safetensors.part* > "out/$name/model.safetensors"
  (cd "out/$name" && sha256sum -c "$m/model.safetensors.sha256")
done
echo "restored into $W; next: ./cloud_round.sh <new-name> <finetune args>"
