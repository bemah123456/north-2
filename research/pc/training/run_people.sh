#!/bin/bash
cd /home/user/work
export OMP_NUM_THREADS=2
A=/mnt/project-files/research-cloud/audio_people/manifest.jsonl
O=/home/user/work/hyps_people; mkdir -p $O
nice -n 10 python3 -I transcribe_set.py out/whisper-small-v2 $A $O/whisper-small-v2.jsonl
nice -n 10 python3 -I transcribe_set.py out/whisper-small-v2 $A $O/whisper-small-v2-monthhint.jsonl --month-hint --plain $O/whisper-small-v2.jsonl
cp $O/*.jsonl /mnt/project-files/research-cloud/hyps_people/ && echo PEOPLE_DONE
