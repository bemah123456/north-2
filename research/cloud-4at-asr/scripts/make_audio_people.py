"""Read the six made-up people's answers in accented voices, clean and
"older" (20% slower with a 6 Hz tremor).

Voices: 12 VCTK speakers chosen for their accents (Piper's VCTK model, which
was fine-tuned from a US voice, so accents are softened) and 2 British
Kokoro voices. None of these voices was in the main study.

Usage: make_audio_people.py MODELS_DIR OUT_DIR
"""

import json
import sys
from pathlib import Path

import soundfile as sf

import make_audio as MA
from answers_people import all_items

# VCTK speaker -> accent, as VCTK's speaker list gives it.
VCTK = {"p237": "Scottish", "p249": "Scottish", "p245": "Irish", "p283": "Irish",
        "p270": "Northern English", "p227": "Northern English", "p248": "Indian", "p251": "Indian",
        "p294": "American", "p347": "South African", "p326": "Australian", "p335": "New Zealand"}
KOKORO = {7: "Southern English (Kokoro bf_emma)", 9: "Southern English (Kokoro bm_george)"}


def main():
    models, out = Path(sys.argv[1]), Path(sys.argv[2])
    MA.MODELS = models
    vctk = MA.piper("vits-piper-en_GB-vctk-medium")
    ids = json.loads((models / "vits-piper-en_GB-vctk-medium" / "en_GB-vctk-medium.onnx.json").read_text())["speaker_id_map"]
    kok = MA.kokoro("kokoro-en-v0_19")
    voices = [(f"vctk-{p}", vctk, ids[p], acc) for p, acc in VCTK.items()]
    voices += [(f"kokoro-{s}", kok, s, acc) for s, acc in KOKORO.items()]
    rows = []
    for vid, tts, sid, acc in voices:
        for it in all_items():
            clean = MA.pad(MA.say(tts, it["text"], sid, 1.0))
            older = MA.pad(MA.ffmpeg(MA.say(tts, it["text"], sid, 0.8), MA.SR, "vibrato=f=6:d=0.25"))
            for cond, x in (("clean", clean), ("older", older)):
                path = out / cond / vid / f"{it['id']}.wav"
                path.parent.mkdir(parents=True, exist_ok=True)
                sf.write(path, x, MA.SR)
                rows.append({**it, "voice": vid, "accent": acc, "condition": cond, "path": str(path.relative_to(out))})
        print(vid, flush=True)
    (out / "manifest.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(len(rows), "clips")


if __name__ == "__main__":
    main()
