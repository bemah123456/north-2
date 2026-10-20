"""Fine-tune a small Whisper model on older speakers, CPU-only, then compare with the original.

Usage (after prepare_cv.py):
    python -I finetune_whisper.py --model openai/whisper-base --steps 2000
    python -I finetune_whisper.py --eval-only --model openai/whisper-base     # baseline numbers only

Writes training/out/<model>/ (weights) and training/out/results.md (word error rate and
month/number recall on held-out older speakers, before and after).
"""
import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # run with python -I, which drops the script folder from the path

import torch  # noqa: E402
from jiwer import wer  # noqa: E402
from transformers import WhisperForConditionalGeneration, WhisperProcessor  # noqa: E402

from common import key_word_recall, load_audio, normalise, read_manifest  # noqa: E402


def transcribe(model, processor, rows, batch=8):
    model.eval()
    hyps = []
    with torch.no_grad():
        for i in range(0, len(rows), batch):
            audio = [load_audio(r["path"]) for r in rows[i:i + batch]]
            feats = processor(audio, sampling_rate=16000, return_tensors="pt").input_features
            ids = model.generate(feats, language="en", task="transcribe", max_new_tokens=128)
            hyps += processor.batch_decode(ids, skip_special_tokens=True)
    return [normalise(h) for h in hyps]


def evaluate(model, processor, rows, label):
    t = time.time()
    refs = [normalise(r["sentence"]) for r in rows]
    hyps = transcribe(model, processor, rows)
    recall, n_key = key_word_recall(refs, hyps)
    res = {"label": label, "wer": wer(refs, hyps), "key_recall": recall, "n_key": n_key,
           "n": len(rows), "minutes": (time.time() - t) / 60}
    print(res)
    return res


def train(model, processor, rows, steps, lr, batch, accum):
    model.train()
    model.config.forced_decoder_ids = None
    model.generation_config.forced_decoder_ids = None
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 100) * max(0.0, 1 - s / steps))
    processor.tokenizer.set_prefix_tokens(language="en", task="transcribe")
    g = torch.Generator().manual_seed(13)
    t0 = time.time()
    for step in range(steps):
        opt.zero_grad()
        for _ in range(accum):
            idx = torch.randint(len(rows), (batch,), generator=g).tolist()
            audio = [load_audio(rows[i]["path"]) for i in idx]
            feats = processor(audio, sampling_rate=16000, return_tensors="pt").input_features
            labels = processor.tokenizer([rows[i]["sentence"] for i in idx], return_tensors="pt",
                                         padding=True).input_ids
            labels = labels.masked_fill(labels == processor.tokenizer.pad_token_id, -100)
            # The model adds the start token itself when given labels; drop our copy.
            if (labels[:, 0] == model.config.decoder_start_token_id).all():
                labels = labels[:, 1:]
            loss = model(input_features=feats, labels=labels).loss / accum
            loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if step % 25 == 0:
            el = (time.time() - t0) / 60
            print(f"step {step}/{steps}  loss {loss.item() * accum:.3f}  {el:.0f} min elapsed", flush=True)
    model.eval()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/whisper-base")
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--accum", type=int, default=2)
    ap.add_argument("--eval-n", type=int, default=500, help="held-out clips to score")
    ap.add_argument("--eval-only", action="store_true")
    args = ap.parse_args()

    torch.set_num_threads(max(1, torch.get_num_threads()))
    train_rows = read_manifest(HERE / "manifests" / "train.csv")
    test_rows = read_manifest(HERE / "manifests" / "test.csv")[: args.eval_n]
    processor = WhisperProcessor.from_pretrained(args.model)
    model = WhisperForConditionalGeneration.from_pretrained(args.model)

    results = [evaluate(model, processor, test_rows, f"{args.model} (original)")]
    if not args.eval_only:
        train(model, processor, train_rows, args.steps, args.lr, args.batch, args.accum)
        out = HERE / "out" / args.model.split("/")[-1]
        model.save_pretrained(out)
        processor.save_pretrained(out)
        results.append(evaluate(model, processor, test_rows, f"{args.model} (tuned on older speakers)"))

    lines = ["| Model | Word error rate | Month/number/day recall | Clips |", "|---|---|---|---|"]
    for r in results:
        kr = "n/a" if r["key_recall"] is None else f"{r['key_recall']:.1%} of {r['n_key']}"
        lines.append(f"| {r['label']} | {r['wer']:.1%} | {kr} | {r['n']} |")
    report = HERE / "out" / "results.md"
    report.parent.mkdir(exist_ok=True)
    with report.open("a", encoding="utf-8") as f:
        f.write(f"\n## {time.strftime('%Y-%m-%d %H:%M')}  steps={0 if args.eval_only else args.steps}\n")
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
