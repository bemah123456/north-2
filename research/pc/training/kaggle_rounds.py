"""Whisper small training rounds on a Kaggle GPU, from public data only.

The PC is offline and the round 2 weights live only in the Claude project files, so this
rebuilds everything from the public Common Voice copy and checks it lands on the same numbers:

  1. Fetch the older-speaker clips in the same shard order as the PC and rebuild the same
     manifests: test = 360 clips from 44 held-out speakers (stops if the counts differ).
  2. Score stock Whisper small (the PC got 8.6% quiet, 32.9% with background talk).
  3. Rebuild round 1 and round 2 with the PC's settings (should land near 8.3% / 12.9%).
  4. Round 3, two ways, from the rebuilt round 2, training the whole model on the GPU:
     a) the PC's planned round 3: all clips, background talk, months/numbers 35% of each
        batch, 900 steps, lr 4e-6;
     b) longer: 3,000 steps at lr 5e-6 (round 2 saw under half of its clips once), with
        months/numbers 25% of each batch, scored at 1,000, 2,000 and 3,000 steps.
  5. Keep the model with the lowest quiet + background-talk word error rate, as 16-bit
     weights and as int8 CTranslate2 for faster-whisper (LOCAL_WHISPER_ENGINE=faster-whisper).

Scoring is compare_models.py's part 1: the same 44 speakers, the same background talk (the
same random draws, so the 4AT probes' draws are skipped first), word error rate with a 95%
interval from resampling speakers, and month/number/day recall. The synthetic 4AT probes are
not on Kaggle, so they are left for a later check.

Run by build_kaggle.py's kernel. SMOKE=1 does a quick end-to-end check instead.
"""
import csv
import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from jiwer import wer  # noqa: E402
from transformers import WhisperForConditionalGeneration, WhisperProcessor  # noqa: E402

from common import KEY_WORDS, SR, load_audio, normalise, read_manifest  # noqa: E402
from compare_models import key_stats, speaker_bootstrap_wer  # noqa: E402
from finetune_whisper import augment, babble, mix_at_snr  # noqa: E402

SMOKE = os.environ.get("SMOKE") == "1"
DATA = Path(os.environ.get("DATA_DIR", "/tmp/data"))
OUT = Path(os.environ.get("OUT_DIR", "/kaggle/working"))
MODELS = Path("/tmp/models")
DEV = "cuda" if torch.cuda.is_available() else "cpu"
PROBE_TALK_DRAWS = 90 * 2  # compare_models mixes talk into 90 probes (2 talkers each) before the test clips
REPORT = OUT / "results.md"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def run(*cmd):
    log("$", " ".join(map(str, cmd)))
    subprocess.run([sys.executable, "-I", *map(str, cmd)], check=True)


def manifest(name):
    return read_manifest(HERE / "manifests" / name)


# ---------- data ----------

def build_data():
    fetch = HERE / "fetch_cv17_older.py"
    if SMOKE:
        run(fetch, DATA, "--target", 1500)
        run(HERE / "prepare_cv.py", DATA, "--hours", 14)
        run(HERE / "extend_train_manifest.py", DATA, "--max", 100000)
        shutil.copy(HERE / "manifests" / "train_v2.csv", HERE / "manifests" / "train_r2.csv")
        shutil.copy(HERE / "manifests" / "train_v2.csv", HERE / "manifests" / "train_all.csv")
        return
    # Round 1's data: the PC stopped after 14 shards with 12,569 clips.
    run(fetch, DATA, "--target", 12000)
    run(HERE / "prepare_cv.py", DATA, "--hours", 14)
    train, test = manifest("train.csv"), manifest("test.csv")
    spk = len({r["client_id"] for r in test})
    log(f"round 1 manifests: train {len(train)}, test {len(test)} clips from {spk} speakers")
    if (len(train), len(test), spk) != (10080, 360, 44):
        sys.exit("The rebuilt manifests differ from the PC's (10,080 / 360 / 44), so results would not compare.")
    # Round 2's data: 36 shards, 32,440 clips, 31,500 for training.
    run(fetch, DATA, "--target", 32000)
    run(HERE / "extend_train_manifest.py", DATA, "--max", 31500)
    shutil.copy(HERE / "manifests" / "train_v2.csv", HERE / "manifests" / "train_r2.csv")
    # Everything (49 shards): round 3.
    run(fetch, DATA, "--target", 10 ** 9)
    run(HERE / "extend_train_manifest.py", DATA, "--max", 100000)
    shutil.copy(HERE / "manifests" / "train_v2.csv", HERE / "manifests" / "train_all.csv")
    log("train_r2", len(manifest("train_r2.csv")), "train_all", len(manifest("train_all.csv")))


# ---------- scoring ----------

class TestSet:
    def __init__(self):
        self.rows = manifest("test.csv")
        if SMOKE:
            self.rows = self.rows[:40]
        self.refs = [normalise(r["sentence"]) for r in self.rows]
        self.quiet = [load_audio(r["path"]) for r in self.rows]
        # Background talk exactly as compare_models.py --talk makes it.
        pool = manifest("train.csv")
        prng = random.Random(11)
        for _ in range(PROBE_TALK_DRAWS):
            prng.choice(pool)

        def with_talk(a):
            parts = [load_audio(prng.choice(pool)["path"]) for _ in range(2)]
            n = sum(np.pad(np.resize(p, len(a)), (0, 0)) for p in parts)
            return (a + n * np.sqrt((np.mean(a ** 2) + 1e-9) / ((np.mean(n ** 2) + 1e-9) * 10))).astype(np.float32)
        self.talk = [with_talk(a) for a in self.quiet]


def transcribe(model, processor, audios, batch=16):
    hyps = []
    with torch.no_grad():
        for i in range(0, len(audios), batch):
            feats = processor(audios[i:i + batch], sampling_rate=SR, return_tensors="pt").input_features.to(DEV)
            ids = model.generate(feats, max_new_tokens=160, language="en", task="transcribe")
            hyps += processor.batch_decode(ids, skip_special_tokens=True)
    return [normalise(h) for h in hyps]


RESULTS = []


def score(label, model, processor, ts):
    model.eval()
    t = time.time()
    q = transcribe(model, processor, ts.quiet)
    k = transcribe(model, processor, ts.talk)
    recall, inserted, n_key = key_stats(ts.refs, q)
    r = {"label": label, "quiet": wer(ts.refs, q), "quiet_ci": speaker_bootstrap_wer(ts.rows, ts.refs, q),
         "talk": wer(ts.refs, k), "talk_ci": speaker_bootstrap_wer(ts.rows, ts.refs, k),
         "recall": recall, "n_key": n_key, "inserted": inserted, "minutes": (time.time() - t) / 60}
    r["sum"] = r["quiet"] + r["talk"]
    RESULTS.append(r)
    log(f"SCORE {label}: quiet {r['quiet']:.1%}, talk {r['talk']:.1%}, recall {recall:.1%} of {n_key}")
    write_report()
    return r


def write_report(extra=""):
    lines = ["# Kaggle GPU rounds", "",
             "Same 44 held-out older speakers (360 Common Voice clips) as the PC. Lower is better.", "",
             "| Model | Word error rate (95% interval) | With background talk 10 dB | Month/number/day recall | "
             "False month/number/day insertions |", "|---|---|---|---|---|"]
    for r in RESULTS:
        lines.append(f"| {r['label']} | {r['quiet']:.1%} ({r['quiet_ci'][0]:.1%} to {r['quiet_ci'][1]:.1%}) | "
                     f"{r['talk']:.1%} ({r['talk_ci'][0]:.1%} to {r['talk_ci'][1]:.1%}) | "
                     f"{r['recall']:.1%} of {r['n_key']} | {r['inserted']} |")
    lines += ["", "PC reference: stock small 8.6% / 32.9%, round 2 (best so far) 8.3% / 12.9%.", "", extra]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


# ---------- training ----------

def harder_talk(audio, rows, rng, talk=0.65, lo=0.0, hi=10.0):
    """Like augment(), but more clips get background talk, and louder (0-10 dB), since a TV
    behind the speaker is what still trips the app up."""
    r = rng.random()
    if r < talk:
        return mix_at_snr(audio, babble(rows, rng, int(rng.integers(1, 4))), rng.uniform(lo, hi))
    if r < talk + 0.1:
        return mix_at_snr(audio, rng.standard_normal(len(audio)).astype(np.float32), rng.uniform(10, 25))
    return audio


class Clips(torch.utils.data.Dataset):
    """One item per (step, slot): the clip, with background talk or hiss mixed in when asked."""

    def __init__(self, rows, plan, aug, seed):
        self.rows, self.plan, self.aug, self.seed = rows, plan, aug, seed

    def __len__(self):
        return len(self.plan)

    def __getitem__(self, i):
        r = self.rows[self.plan[i]]
        audio = load_audio(r["path"])
        if self.aug:
            mix = harder_talk if self.aug == "harder" else augment
            audio = mix(audio, self.rows, np.random.default_rng(self.seed * 1_000_003 + i))
        return audio, r["sentence"]


def train(model, processor, rows, steps, lr, aug, key_frac, seed, batch=8, accum=2, checkpoints=(),
          on_checkpoint=None, optim="adamw", grad_ckpt=False):
    """The PC's recipe (AdamW, 100-step warm-up then linear decay, clip 1.0, 8 clips x 2
    accumulated = 16 a step), on the GPU with mixed precision and the whole model trained.
    16 clips at once runs a 15 GB T4 out of memory. For large models: optim="adamw8bit" keeps
    Adam's two running averages in 8 bits, and grad_ckpt recomputes activations instead of
    storing them."""
    rng = np.random.default_rng(seed)
    key_idx = [i for i, r in enumerate(rows) if any(w in KEY_WORDS for w in normalise(r["sentence"]).split())]
    plan = []
    for _ in range(steps * batch * accum):
        if key_frac and rng.random() < key_frac:
            plan.append(int(key_idx[rng.integers(len(key_idx))]))
        else:
            plan.append(int(rng.integers(len(rows))))
    tok = processor.tokenizer
    tok.set_prefix_tokens(language="en", task="transcribe")

    def collate(items):
        feats = processor([a for a, _ in items], sampling_rate=SR, return_tensors="pt").input_features
        labels = tok([s for _, s in items], return_tensors="pt", padding=True).input_ids
        labels = labels.masked_fill(labels == tok.pad_token_id, -100)
        if (labels[:, 0] == model.config.decoder_start_token_id).all():
            labels = labels[:, 1:]
        return feats, labels

    loader = torch.utils.data.DataLoader(Clips(rows, plan, aug, seed), batch_size=batch, num_workers=4,
                                         collate_fn=collate, prefetch_factor=4, persistent_workers=False)
    model.config.forced_decoder_ids = None
    model.generation_config.forced_decoder_ids = None
    if grad_ckpt:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.train()
    params = [p for p in model.parameters() if p.requires_grad]
    if optim == "adamw8bit":
        import bitsandbytes as bnb
        opt = bnb.optim.AdamW8bit(params, lr=lr, weight_decay=0.01)
    else:
        opt = torch.optim.AdamW(params, lr=lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 100) * max(0.0, 1 - s / steps))
    scaler = torch.amp.GradScaler("cuda", enabled=DEV == "cuda")
    t0 = time.time()
    batches = iter(loader)
    for step in range(steps):
        opt.zero_grad(set_to_none=True)
        for _ in range(accum):
            feats, labels = next(batches)
            with torch.autocast(DEV, dtype=torch.float16, enabled=DEV == "cuda"):
                loss = model(input_features=feats.to(DEV), labels=labels.to(DEV)).loss / accum
            scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        scaler.step(opt)
        scaler.update()
        sched.step()
        if step % 50 == 0:
            mem = torch.cuda.max_memory_allocated() / 2 ** 30 if DEV == "cuda" else 0
            log(f"step {step}/{steps} loss {loss.item() * accum:.3f} ({(time.time() - t0) / 60:.1f} min, "
                f"peak GPU memory {mem:.1f} GB)")
        if on_checkpoint and step + 1 in checkpoints:
            on_checkpoint(step + 1)
            model.train()
    del batches, loader
    if grad_ckpt:
        model.gradient_checkpointing_disable()
    model.eval()


def save(model, processor, name):
    path = MODELS / name
    model.save_pretrained(path)
    processor.save_pretrained(path)
    return path


def load(path):
    processor = WhisperProcessor.from_pretrained(path)
    model = WhisperForConditionalGeneration.from_pretrained(path).float().to(DEV)
    return model, processor


# ---------- main ----------

def next_rounds(start, rounds):
    """Further rounds from a saved model (START_FROM), each scored the same way. The best is
    kept only if it beats the starting model."""
    ts = TestSet()
    s = lambda n: max(10, n // 100) if SMOKE else n  # noqa: E731
    model, proc = load(start)
    start_label = f"start: {os.environ.get('START_LABEL', start)}"
    score(start_label, model, proc, ts)
    candidates = {start_label: Path(start)}
    for spec in rounds:
        model, proc = load(start)
        train(model, proc, manifest(spec.get("manifest", "train_all.csv")), s(spec["steps"]), spec["lr"],
              aug=spec.get("aug", True), key_frac=spec.get("key_frac", 0.0), seed=spec["seed"])
        score(spec["label"], model, proc, ts)
        candidates[spec["label"]] = save(model, proc, spec["name"])
    best = min((r for r in RESULTS if r["label"] in candidates), key=lambda r: r["sum"])
    start_r = RESULTS[0]
    won = best["label"] != start_label
    verdict = (f"Best: **{best['label']}** ({best['quiet']:.1%} quiet + {best['talk']:.1%} talk = {best['sum']:.1%}; "
               f"start = {start_r['sum']:.1%}). " + ("It beats the start." if won else "Nothing beat the start; no new model."))
    log(verdict)
    write_report(verdict)
    if won:
        export(candidates[best["label"]], best, ts)
    log("DONE")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log("device", DEV, torch.cuda.get_device_name(0) if DEV == "cuda" else "")
    build_data()
    if os.environ.get("START_FROM"):
        return next_rounds(os.environ["START_FROM"], json.loads(os.environ["ROUNDS"]))
    ts = TestSet()
    s = lambda n: max(10, n // 100) if SMOKE else n  # noqa: E731

    model, proc = load("openai/whisper-small")
    score("openai/whisper-small (stock)", model, proc, ts)

    # Rebuild rounds 1 and 2 with the PC's settings.
    train(model, proc, manifest("train.csv"), s(600), 5e-6, aug=False, key_frac=0.0, seed=1)
    score("round 1 rebuilt (600 steps, lr 5e-6)", model, proc, ts)
    train(model, proc, manifest("train_r2.csv"), s(900), 5e-6, aug=True, key_frac=0.0, seed=2)
    score("round 2 rebuilt (+900 steps with background talk)", model, proc, ts)
    r2 = save(model, proc, "round2")
    candidates = {"round 2 rebuilt (+900 steps with background talk)": r2}
    all_rows = manifest("train_all.csv")

    # Round 3a: the PC's planned round 3, now on the whole model.
    model, proc = load(r2)
    train(model, proc, all_rows, s(900), 4e-6, aug=True, key_frac=0.35, seed=3)
    label = "round 3a (+900 steps, months/numbers 35%, lr 4e-6)"
    score(label, model, proc, ts)
    candidates[label] = save(model, proc, "round3a")

    # Round 3b: longer, scored along the way.
    model, proc = load(r2)

    def checkpoint(step):
        lab = f"round 3b at {step} steps (months/numbers 25%, lr 5e-6)"
        score(lab, model, proc, ts)
        candidates[lab] = save(model, proc, f"round3b-{step}")
    total = s(3000)
    train(model, proc, all_rows, total, 5e-6, aug=True, key_frac=0.25, seed=4,
          checkpoints={s(1000), s(2000), total}, on_checkpoint=checkpoint)

    best = min((r for r in RESULTS if r["label"] in candidates), key=lambda r: r["sum"])
    pc_best = 0.083 + 0.129
    verdict = (f"Best: **{best['label']}** ({best['quiet']:.1%} quiet + {best['talk']:.1%} talk = "
               f"{best['sum']:.1%}; PC round 2 = {pc_best:.1%}). "
               + ("It beats the PC's round 2." if best["sum"] < pc_best else "It does not beat the PC's round 2."))
    log(verdict)
    write_report(verdict)

    export(candidates[best["label"]], best, ts)


def export(path, best, ts):
    """Keep the winner, 16-bit, plus an int8 copy for faster-whisper."""
    final = OUT / "whisper-small-best-fp16"
    model, proc = load(path)
    model.half().save_pretrained(final)
    proc.save_pretrained(final)
    (final / "SCORES.json").write_text(json.dumps(best, default=float, indent=1))
    # Newer transformers saves processor_config.json; faster-whisper reads preprocessor_config.json.
    (final / "preprocessor_config.json").write_text(proc.feature_extractor.to_json_string())
    shutil.rmtree(MODELS, ignore_errors=True)
    try:
        ct2 = OUT / "whisper-small-best-ct2"
        subprocess.run(["ct2-transformers-converter", "--model", str(final), "--output_dir", str(ct2), "--force",
                        "--quantization", "int8", "--copy_files", "tokenizer.json", "preprocessor_config.json"],
                       check=True)
        # Check the copy the server would use: faster-whisper on a few held-out clips.
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "faster-whisper"], check=True)
        from faster_whisper import WhisperModel
        fw = WhisperModel(str(ct2), device="cpu", compute_type="int8")
        for row, ref in list(zip(ts.rows, ts.refs))[:5]:
            segs, _ = fw.transcribe(load_audio(row["path"]), language="en", word_timestamps=True)
            log(f"faster-whisper check: {normalise(''.join(x.text for x in segs))!r} (said: {ref!r})")
    except Exception as e:  # the 16-bit model above is still saved
        log(f"faster-whisper copy failed: {e}")
    log("DONE")


if __name__ == "__main__":
    main()
