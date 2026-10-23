"""Save the round 5 test audio (quiet, background talk 10 dB, unseen voices 10 dB) so other
speech services can be scored on exactly the same clips off Kaggle (gemini_bench.py).

Runs as a CPU-only Kaggle job (build_kaggle.py --script export_testset.py --cpu). Writes
testset.npz (16 kHz, 16-bit) and testset.json (clip name, speaker, normalised reference).
The clips are Common Voice (CC0) and LibriSpeech (CC BY 4.0).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402

import kaggle_rounds as kr  # noqa: E402
from kaggle_round5 import CONDS, librispeech_voices  # noqa: E402


def main():
    kr.OUT.mkdir(parents=True, exist_ok=True)
    kr.build_data()
    ts = kr.TestSet()
    audio = {"quiet": ts.quiet, "talk": ts.talk, "voices": librispeech_voices(ts.quiet)}
    arrays = {}
    for c in CONDS:
        arrays[c] = (np.clip(np.concatenate(audio[c]), -1, 1) * 32767).astype(np.int16)
        arrays[c + "_offsets"] = np.cumsum([0] + [len(x) for x in audio[c]])
    np.savez_compressed(kr.OUT / "testset.npz", **arrays)
    rows = [{"path": Path(r["path"]).name, "speaker": r["client_id"], "ref": ref} for r, ref in zip(ts.rows, ts.refs)]
    (kr.OUT / "testset.json").write_text(json.dumps(rows))
    kr.log(f"saved {len(rows)} clips x {len(CONDS)} conditions")


if __name__ == "__main__":
    main()
