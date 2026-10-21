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

import numpy as np  # noqa: E402
import torch  # noqa: E402
from jiwer import wer  # noqa: E402
from transformers import WhisperForConditionalGeneration, WhisperProcessor  # noqa: E402

from common import KEY_WORDS, key_word_recall, load_audio, normalise, read_manifest  # noqa: E402


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


def mix_at_snr(speech, noise, snr_db):
    if len(noise) < len(speech):
        noise = np.tile(noise, int(np.ceil(len(speech) / max(len(noise), 1))))
    noise = noise[: len(speech)]
    p_s, p_n = np.mean(speech ** 2) + 1e-9, np.mean(noise ** 2) + 1e-9
    return (speech + noise * np.sqrt(p_s / (p_n * 10 ** (snr_db / 10)))).astype(np.float32)


def babble(rows, rng, n_talkers):
    """Several other speakers talking at once, like a TV or a room in the background."""
    parts = [load_audio(rows[rng.integers(len(rows))]["path"]) for _ in range(n_talkers)]
    length = max(len(p) for p in parts)
    return sum(np.pad(p, (0, length - len(p))) for p in parts).astype(np.float32)


def augment(audio, rows, rng):
    """Half the clips get background talk at 0-15 dB SNR, some get hiss, the rest stay clean."""
    r = rng.random()
    if r < 0.5:
        return mix_at_snr(audio, babble(rows, rng, int(rng.integers(1, 4))), rng.uniform(0, 15))
    if r < 0.65:
        return mix_at_snr(audio, rng.standard_normal(len(audio)).astype(np.float32), rng.uniform(10, 25))
    return audio


def train(model, processor, rows, steps, lr, batch, accum, aug=False, key_frac=0.0, freeze_encoder=False,
          ckpt=None, ckpt_every=50):
    """ckpt: folder for resumable checkpoints (weights, optimiser, step), so a restarted machine
    picks up where it stopped instead of starting over."""
    start = 0
    if ckpt and (ckpt / "state.pt").exists():
        state = torch.load(ckpt / "state.pt", weights_only=False)
        model.load_state_dict(state["model"])
        start = state["step"] + 1
        print(f"resuming from checkpoint at step {start}", flush=True)
    rng = np.random.default_rng(21 + start)
    # Clips that mention months, numbers or days: the words the 4AT depends on.
    key_idx = [i for i, r in enumerate(rows) if any(w in KEY_WORDS for w in normalise(r["sentence"]).split())]
    if key_frac:
        print(f"{len(key_idx)} clips with month/number/day words; {key_frac:.0%} of each batch drawn from them")
    model.train()
    model.config.forced_decoder_ids = None
    model.generation_config.forced_decoder_ids = None
    if freeze_encoder:
        # Encoder frozen: about 4x faster on CPU, and the decoder is where months/numbers are spelled out.
        for p in model.model.encoder.parameters():
            p.requires_grad = False
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 100) * max(0.0, 1 - s / steps))
    processor.tokenizer.set_prefix_tokens(language="en", task="transcribe")
    g = torch.Generator().manual_seed(13 + start)
    if start:
        opt.load_state_dict(state["opt"])
        for _ in range(start):
            sched.step()
        del state
    t0 = time.time()
    for step in range(start, steps):
        opt.zero_grad()
        for _ in range(accum):
            idx = torch.randint(len(rows), (batch,), generator=g).tolist()
            if key_frac and key_idx:
                idx = [key_idx[int(rng.integers(len(key_idx)))] if rng.random() < key_frac else i for i in idx]
            audio = [load_audio(rows[i]["path"]) for i in idx]
            if aug:
                audio = [augment(a, rows, rng) for a in audio]
            feats = processor(audio, sampling_rate=16000, return_tensors="pt").input_features
            labels = processor.tokenizer([rows[i]["sentence"] for i in idx], return_tensors="pt",
                                         padding=True).input_ids
            labels = labels.masked_fill(labels == processor.tokenizer.pad_token_id, -100)
            # The model adds the start token itself when given labels; drop our copy.
            if (labels[:, 0] == model.config.decoder_start_token_id).all():
                labels = labels[:, 1:]
            loss = model(input_features=feats, labels=labels).loss / accum
            loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        sched.step()
        if step % 25 == 0:
            el = (time.time() - t0) / 60
            print(f"step {step}/{steps}  loss {loss.item() * accum:.3f}  {el:.0f} min elapsed", flush=True)
        if ckpt and (step + 1) % ckpt_every == 0 and step + 1 < steps:
            ckpt.mkdir(parents=True, exist_ok=True)
            torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "step": step}, ckpt / "state.tmp")
            (ckpt / "state.tmp").replace(ckpt / "state.pt")
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
    ap.add_argument("--train-manifest", default="train.csv")
    ap.add_argument("--augment", action="store_true", help="add background talk and hiss while training")
    ap.add_argument("--out-name", default=None, help="folder under out/ (default: model name)")
    ap.add_argument("--freeze-encoder", action="store_true", help="train the decoder only (faster on CPU)")
    ap.add_argument("--skip-start-eval", action="store_true", help="the starting model was already scored")
    ap.add_argument("--key-frac", type=float, default=0.0,
                    help="share of each batch drawn from clips with months/numbers/days")
    args = ap.parse_args()

    torch.set_num_threads(max(1, torch.get_num_threads()))
    train_rows = read_manifest(HERE / "manifests" / args.train_manifest)
    test_rows = read_manifest(HERE / "manifests" / "test.csv")[: args.eval_n]
    model_path = HERE / args.model if (HERE / args.model).exists() else args.model
    processor = WhisperProcessor.from_pretrained(model_path)
    model = WhisperForConditionalGeneration.from_pretrained(model_path)

    results = [] if args.skip_start_eval else [evaluate(model, processor, test_rows, f"{args.model} (start)")]
    if not args.eval_only:
        out = HERE / "out" / (args.out_name or args.model.split("/")[-1])
        train(model, processor, train_rows, args.steps, args.lr, args.batch, args.accum, aug=args.augment,
              key_frac=args.key_frac, freeze_encoder=args.freeze_encoder, ckpt=HERE / "ckpt" / out.name)
        model.save_pretrained(out)
        processor.save_pretrained(out)
        if test_rows:  # --eval-n 0 leaves scoring to compare_models.py
            results.append(evaluate(model, processor, test_rows, f"{out.name} (tuned on older speakers)"))

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
