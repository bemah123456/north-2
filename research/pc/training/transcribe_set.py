"""Transcribe another thread's clip set with one of our models, for its scoring code.

Usage: python -I transcribe_set.py <model folder> <manifest.jsonl> <out.jsonl> [--month-hint]
Writes one {"path", "hyp"} line per clip (raw Whisper text, not normalised). With --month-hint,
months_backwards clips get the month list as the prompt and the rest are copied from <out> without it.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import torch  # noqa: E402
from transformers import WhisperForConditionalGeneration, WhisperProcessor  # noqa: E402

from common import SR, load_audio  # noqa: E402
from compare_models import MONTH_PROMPT  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("manifest", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--month-hint", action="store_true")
    ap.add_argument("--plain", type=Path, help="no-hint output to copy non-months clips from")
    args = ap.parse_args()

    rows = [json.loads(line) for line in args.manifest.open(encoding="utf-8")]
    plain = {}
    if args.month_hint and args.plain:
        plain = {r["path"]: r["hyp"] for r in map(json.loads, args.plain.open(encoding="utf-8"))}
    done = set()
    if args.out.exists():  # resume
        done = {json.loads(line)["path"] for line in args.out.open(encoding="utf-8")}
    processor = WhisperProcessor.from_pretrained(args.model)
    model = WhisperForConditionalGeneration.from_pretrained(args.model).float().eval()
    prompt_ids = processor.get_prompt_ids(MONTH_PROMPT, return_tensors="pt")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("a", encoding="utf-8") as f, torch.no_grad():
        for n, r in enumerate(rows):
            if r["path"] in done:
                continue
            hinted = args.month_hint and r.get("kind") == "months_backwards"
            if not hinted and r["path"] in plain:
                hyp = plain[r["path"]]
            else:
                feats = processor(load_audio(args.manifest.parent / r["path"]), sampling_rate=SR,
                                  return_tensors="pt").input_features
                kw = {"prompt_ids": prompt_ids} if hinted else {}
                ids = model.generate(feats, language="en", task="transcribe", max_new_tokens=160, **kw)
                hyp = processor.batch_decode(ids, skip_special_tokens=True)[0].strip()
            f.write(json.dumps({"path": r["path"], "hyp": hyp}) + "\n")
            f.flush()
            if n % 200 == 0:
                print(n, len(rows), flush=True)


if __name__ == "__main__":
    main()
