#!/bin/bash
# Runs training chain and the people transcription side by side; both resume if restarted.
cd /home/user/work
./run_people.sh >> people.log 2>&1 &
./run_chain.sh >> chain.log 2>&1
wait
