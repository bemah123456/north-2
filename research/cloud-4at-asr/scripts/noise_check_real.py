"""How often the quiet-room check fires on real microphones.

Real recordings: the PC's 20 Common Voice speakers aged 60+, 10 clips each,
recorded on their own devices and compressed to MP3. None is known to have
a TV on. Synthetic: the main study's quiet "older" clips and TV clips at
-20 and -10 dB, all 12 voices.

A check-in is asked to turn the TV off when 3 or more of its 5 answers
are flagged; real check-ins are 5 random clips of one speaker, synthetic
ones 5 random healthy answers of one voice.

Two rules: the first version (flicker in the gaps above 4.4 dB), and the
same with the gaps also no more than 40 dB below the speech.

Usage: noise_check_real.py SPEAKER_DAYS_DIR AUDIO_DIR OUT_JSON
"""

import csv
import json
import random
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf

import noise_check as NC

RULES = {
    "flicker only": lambda f, g: f > NC.FLICKER_DB,
    "flicker and gap": lambda f, g: f > NC.FLICKER_DB and g < NC.GAP_DB,
}


def decode(p):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32)


def main():
    days, audio, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    clips = defaultdict(list)  # (set, group) -> [(flicker, gap)]
    for r in csv.DictReader((days / "speakers.csv").open(encoding="utf-8")):
        x = decode(days / r["file"])
        clips[("Real, no TV known", r["speaker"])].append((NC.background_flicker(x), NC.background_gap(x)))
    names = {"older": "Synthetic, quiet", "tv20": "Synthetic, TV -20 dB", "tv": "Synthetic, TV -10 dB"}
    for f in ("manifest.jsonl", "manifest_levels.jsonl"):
        for l in (audio / f).read_text().splitlines():
            r = json.loads(l)
            if r["condition"] in names and r["id"].startswith("healthy"):
                x, sr = sf.read(audio / r["path"], dtype="float32")
                clips[(names[r["condition"]], r["voice"])].append((NC.background_flicker(x, sr), NC.background_gap(x, sr)))
    rng = random.Random(3)
    rows = []
    for name in ["Real, no TV known"] + list(names.values()):
        groups = [v for (s, _), v in clips.items() if s == name]
        for rule, fn in RULES.items():
            flags = [[fn(*c) for c in g] for g in groups]
            per_clip = sum(map(sum, flags)) / sum(map(len, flags))
            hits = n = 0
            for fl in flags:
                for _ in range(500):
                    n += 1
                    hits += sum(rng.sample(fl, 5)) >= 3
            rows.append({"recordings": name, "rule": rule, "clips": sum(map(len, flags)),
                         "clips_flagged": round(per_clip, 4), "checkins_asked_tv_off": round(hits / n, 4)})
            print(f"{name:24}{rule:18} clips flagged {per_clip:6.1%}  check-ins asked to turn TV off {hits / n:6.1%}")
    out.write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
