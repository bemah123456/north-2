set -e
cd /home/claude/work
P=/home/claude/venv/bin/python
$P make_audio_people.py /home/claude/models /home/claude/audio_people > /home/claude/out/people_tts.log 2>&1
mkdir -p /home/claude/hyps_people
MANIFEST=manifest.jsonl THREADS=8 $P run_asr.py /home/claude/models /home/claude/audio_people sherpa-onnx-whisper-small /home/claude/hyps_people/sherpa-onnx-whisper-small.jsonl > /home/claude/out/people_asr.log 2>&1
MANIFEST=manifest.jsonl THREADS=8 $P run_asr.py /home/claude/models /home/claude/audio_people sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8 /home/claude/hyps_people/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.jsonl >> /home/claude/out/people_asr.log 2>&1
echo done > /home/claude/out/people.done
