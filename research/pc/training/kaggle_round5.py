"""Round 5 on a Kaggle GPU: a bigger base model, also scored the way the server decodes.

Rounds 3b, 4a and 4b showed that more steps on Whisper small no longer help, so this round
changes other things:

  * A bigger base model. Whisper large-v3-turbo has large-v3's 32-layer encoder (trained on
    about 5 million hours) with a 4-layer decoder: it hears a voice under other voices far
    better than small, and decoding stays cheap. distil-large-v3 (2 decoder layers) is scored
    too. Turbo is then fine-tuned with round 3a's recipe (all older-speaker clips, background
    talk mixed in, months/numbers oversampled), the whole model, with 8-bit Adam and
    gradient checkpointing so it fits a 15 GB T4.
  * Checkpoint averaging: the average of the last three checkpoints is scored as its own model
    (it usually smooths out the last steps' noise).
  * Scored as the server runs it. The keep rule is unchanged (greedy transformers decoding,
    quiet + background-talk word error rate below round 3a's, recall not lower), but every
    model is also run through faster-whisper int8 with beam 5, like checkin/transcribe.py,
    and timed on the CPU.
  * Paired intervals: each model's difference from round 3a, resampling the 44 speakers on the
    same clips, says whether a gain is real or within noise.
  * Unseen voices: LibriSpeech readers (audiobooks, never used in training) mixed in at 10 dB,
    to check a model didn't only learn to ignore Common Voice babble, which is what the
    training noise and the background-talk test both use.

Needs R3A (round 3a's 16-bit folder, mounted from the earlier job). SMOKE=1: quick check.
"""
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from jiwer import process_words  # noqa: E402

import kaggle_rounds as kr  # noqa: E402
from common import load_audio, normalise  # noqa: E402
from compare_models import key_stats  # noqa: E402

SMOKE, OUT, DEV, log = kr.SMOKE, kr.OUT, kr.DEV, kr.log
WORK = Path("/tmp/round5")
CONDS = ["quiet", "talk", "voices"]
COND_NAMES = {"quiet": "quiet", "talk": "background talk 10 dB", "voices": "unseen voices 10 dB"}
REPORT = OUT / "results.md"
HYPS = OUT / "hyps"
ENV = dict(os.environ)


def s(n):
    return max(6, n // 100) if SMOKE else n


# ---------- test audio ----------

def librispeech_voices(test_audio):
    """Two LibriSpeech dev-clean readers (CC BY 4.0) behind each test clip at 10 dB."""
    root = Path(kr.DATA) / "librispeech"
    if not root.exists():
        tgz = Path(kr.DATA) / "dev-clean.tar.gz"
        for url in ("https://us.openslr.org/resources/12/dev-clean.tar.gz",
                    "https://www.openslr.org/resources/12/dev-clean.tar.gz"):
            try:
                log("downloading", url)
                urllib.request.urlretrieve(url, tgz)
                break
            except Exception as e:  # try the other mirror
                log("download failed:", e)
        with tarfile.open(tgz) as t:
            t.extractall(root, filter="data")
        tgz.unlink()
    files = sorted(root.rglob("*.flac"))
    by_spk = defaultdict(list)
    for f in files:
        by_spk[f.name.split("-")[0]].append(f)
    rng = random.Random(23)
    spks = sorted(by_spk)
    out = []
    for a in test_audio:
        parts = [load_audio(rng.choice(by_spk[sp])) for sp in rng.sample(spks, 2)]
        n = sum(np.resize(p, len(a)) for p in parts)
        out.append((a + n * np.sqrt((np.mean(a ** 2) + 1e-9) / ((np.mean(n ** 2) + 1e-9) * 10))).astype(np.float32))
    log(f"unseen voices: {len(files)} LibriSpeech clips from {len(spks)} readers")
    return out


class Tests:
    def __init__(self):
        ts = kr.TestSet()  # quiet + background talk, exactly as every earlier round
        self.rows, self.refs = ts.rows, ts.refs
        self.audio = {"quiet": ts.quiet, "talk": ts.talk, "voices": librispeech_voices(ts.quiet)}
        self.spk = [r["client_id"] for r in self.rows]
        # Saved once for fw_score.py.
        self.folder = WORK / "audio"
        self.folder.mkdir(parents=True, exist_ok=True)
        for c in CONDS:
            a = self.audio[c]
            np.save(self.folder / f"{c}.npy", np.concatenate(a))
            np.save(self.folder / f"{c}_offsets.npy", np.cumsum([0] + [len(x) for x in a]))
        (self.folder / "conditions.json").write_text(json.dumps(CONDS))


# ---------- scoring ----------

def clip_errors(refs, hyps):
    """Word errors and reference words per clip, so speaker resampling is just sums."""
    e, n = [], []
    for r, h in zip(refs, hyps):
        if r:
            o = process_words(r, h or "")
            e.append(o.substitutions + o.deletions + o.insertions)
        else:
            e.append(len(h.split()))
        n.append(len(r.split()))
    return np.array(e, float), np.array(n, float)


def by_speaker(spk, values):
    ids = sorted(set(spk))
    pos = {k: i for i, k in enumerate(ids)}
    out = np.zeros(len(ids))
    for k, v in zip(spk, values):
        out[pos[k]] += v
    return out


def resample_idx(n_spk, n=2000):
    return np.random.default_rng(7).integers(0, n_spk, size=(n, n_spk))


def wer_ci(spk, e, n):
    E, N = by_speaker(spk, e), by_speaker(spk, n)
    idx = resample_idx(len(E))
    v = E[idx].sum(1) / N[idx].sum(1)
    return e.sum() / n.sum(), np.percentile(v, 2.5), np.percentile(v, 97.5)


def paired_ci(spk, a, b, conds=("quiet", "talk")):
    """Difference b - a in (quiet + talk) word error rate, speakers resampled together."""
    idx = None
    tot = 0.0
    point = 0.0
    for c in conds:
        Ea, Eb, N = by_speaker(spk, a[c][0]), by_speaker(spk, b[c][0]), by_speaker(spk, a[c][1])
        idx = resample_idx(len(N)) if idx is None else idx
        tot = tot + (Eb[idx].sum(1) - Ea[idx].sum(1)) / N[idx].sum(1)
        point += (Eb.sum() - Ea.sum()) / N.sum()
    return point, np.percentile(tot, 2.5), np.percentile(tot, 97.5)


def slug(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:60]


RESULTS = []


def hf_hyps(model, proc, tests):
    model.eval()
    return {c: kr.transcribe(model, proc, tests.audio[c]) for c in CONDS}


def evaluate(label, tests, hyps, kind):
    """kind 'greedy' (the rule, transformers) or 'server' (faster-whisper int8, beam 5)."""
    hyps = {c: [normalise(h) for h in hyps[c]] for c in CONDS}
    r = {"label": label, "kind": kind, "err": {}}
    for c in CONDS:
        e, n = clip_errors(tests.refs, hyps[c])
        r["err"][c] = (e, n)
        r[c] = wer_ci(tests.spk, e, n)
    r["sum"] = r["quiet"][0] + r["talk"][0]
    r["recall"], r["inserted"], r["n_key"] = key_stats(tests.refs, hyps["quiet"])
    # Runaway transcripts: more than twice the words that were said (loops, the TV written down).
    r["runaway"] = {c: int(sum(len(h.split()) > 2 * len(ref.split()) + 3 for ref, h in zip(tests.refs, hyps[c])))
                    for c in CONDS}
    HYPS.mkdir(parents=True, exist_ok=True)
    with (HYPS / f"{kind}-{slug(label)}.jsonl").open("w") as f:
        for i, row in enumerate(tests.rows):
            f.write(json.dumps({"path": Path(row["path"]).name, "speaker": row["client_id"][:10], "ref": tests.refs[i],
                                **{c: hyps[c][i] for c in CONDS}}) + "\n")
    RESULTS.append(r)
    log(f"SCORE [{kind}] {label}: quiet {r['quiet'][0]:.1%}, talk {r['talk'][0]:.1%}, voices {r['voices'][0]:.1%}, "
        f"recall {r['recall']:.1%} of {r['n_key']}, runaway {r['runaway']}")
    write_report()
    return r


def server_score(label, hf_dir, tests, latency):
    """Convert to int8 CTranslate2 and run fw_score.py; returns the CT2 folder."""
    ct2 = WORK / "ct2" / slug(label)
    try:
        subprocess.run(["ct2-transformers-converter", "--model", str(hf_dir), "--output_dir", str(ct2), "--force",
                        "--quantization", "int8", "--copy_files", "tokenizer.json", "preprocessor_config.json"],
                       check=True, capture_output=True, text=True)
        out = WORK / f"fw-{slug(label)}.json"
        for device in ("cuda", "cpu"):
            p = subprocess.run([sys.executable, "-I", str(HERE / "fw_score.py"), str(ct2), str(tests.folder), str(out),
                                device], env=ENV, capture_output=True, text=True)
            print(p.stdout[-2000:], p.stderr[-3000:] if p.returncode else "", flush=True)
            if p.returncode == 0:
                break
            if device == "cuda" and "large" in label.lower():
                raise RuntimeError("faster-whisper failed on the GPU; too slow to run a large model on the CPU")
        res = json.loads(out.read_text())
        latency[label] = res["cpu_sec"]
        evaluate(label, tests, res["hyps"], "server")
    except Exception as e:  # the rule's greedy score still stands
        log(f"server-style scoring failed for {label}: {e}")
        if isinstance(e, subprocess.CalledProcessError):
            print(e.stdout[-2000:], e.stderr[-2000:], flush=True)
    return ct2


def save_hf(model, proc, folder, half=False):
    folder = Path(folder)
    (model.half() if half else model).save_pretrained(folder)
    if half:
        model.float()
    proc.save_pretrained(folder)
    # Newer transformers saves processor_config.json; faster-whisper reads preprocessor_config.json.
    (folder / "preprocessor_config.json").write_text(proc.feature_extractor.to_json_string())
    return folder


def stock_dir(name):
    from huggingface_hub import snapshot_download
    return snapshot_download(name, allow_patterns=["*.json", "*.safetensors", "*.txt"])


# ---------- report ----------

LATENCY = {}
VERDICT = [""]


def write_report():
    greedy = [r for r in RESULTS if r["kind"] == "greedy"]
    server = [r for r in RESULTS if r["kind"] == "server"]
    base = {r["kind"]: r for r in RESULTS if r["label"].startswith("round 3a")}
    pct = lambda t: f"{t[0]:.1%} ({t[1]:.1%} to {t[2]:.1%})"  # noqa: E731

    def diff(r):
        b = base.get(r["kind"])
        if not b or b is r:
            return "-"
        d, lo, hi = paired_ci(TESTS.spk, b["err"], r["err"])
        verdict = "better" if hi < 0 else "worse" if lo > 0 else "within noise"
        return f"{d:+.1%} ({lo:+.1%} to {hi:+.1%}), {verdict}"

    lines = ["# Kaggle round 5: bigger base model, server-style scoring", "",
             f"Same 44 held-out older speakers (360 Common Voice clips) as every round. Lower is better. "
             f"95% intervals resample speakers; \"vs round 3a\" is the paired difference in quiet + talk "
             f"word error rate (both models on the same resampled speakers), so it is much tighter than "
             f"comparing two intervals.", "",
             "## The rule: greedy decoding (as every earlier round)", "",
             "| Model | Quiet | Background talk 10 dB | Quiet + talk | vs round 3a (quiet + talk) | Unseen voices 10 dB "
             "(LibriSpeech) | Month/number/day recall | False insertions | Runaway transcripts (quiet/talk/voices) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in greedy:
        lines.append(f"| {r['label']} | {pct(r['quiet'])} | {pct(r['talk'])} | {r['sum']:.1%} | {diff(r)} | "
                     f"{pct(r['voices'])} | {r['recall']:.1%} of {r['n_key']} | {r['inserted']} | "
                     f"{r['runaway']['quiet']}/{r['runaway']['talk']}/{r['runaway']['voices']} |")
    lines += ["", "## As the server runs it: faster-whisper, int8, beam 5, word timestamps", "",
              "| Model | Quiet | Background talk 10 dB | Quiet + talk | vs round 3a | Unseen voices 10 dB | "
              "Recall | Runaway (q/t/v) | CPU s per answer, 2 threads / 4 threads |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in server:
        lat = LATENCY.get(r["label"], {})
        lat_s = " / ".join(f"{lat[k]:.1f}" for k in sorted(lat, key=int)) if lat else "-"
        lines.append(f"| {r['label']} | {pct(r['quiet'])} | {pct(r['talk'])} | {r['sum']:.1%} | {diff(r)} | "
                     f"{pct(r['voices'])} | {r['recall']:.1%} of {r['n_key']} | "
                     f"{r['runaway']['quiet']}/{r['runaway']['talk']}/{r['runaway']['voices']} | {lat_s} |")
    lines += ["", "CPU times are Kaggle's CPU (a 2.2 GHz Xeon), 8 quiet clips, median; a laptop core is usually faster.",
              "", VERDICT[0]]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


# ---------- main ----------

TESTS = None


def main():
    global TESTS
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    log("device", DEV, torch.cuda.get_device_name(0) if DEV == "cuda" else "", "GPUs:", torch.cuda.device_count())
    kr.build_data()
    TESTS = tests = Tests()
    candidates = {}  # label -> HF folder

    def stock_and_server(label, path):
        model, proc = kr.load(path)
        evaluate(label, tests, hf_hyps(model, proc, tests), "greedy")
        del model
        torch.cuda.empty_cache()
        server_score(label, path, tests, LATENCY)

    r3a = os.environ["R3A"]
    stock_and_server("round 3a (current best, Whisper small)", r3a)
    stock_and_server("Whisper small, stock", stock_dir("openai/whisper-small"))
    turbo = stock_dir("openai/whisper-large-v3-turbo")
    stock_and_server("Whisper large-v3-turbo, stock", turbo)
    candidates["Whisper large-v3-turbo, stock"] = Path(turbo)
    if not SMOKE:
        distil = stock_dir("distil-whisper/distil-large-v3")
        stock_and_server("distil-large-v3, stock", distil)
        candidates["distil-large-v3, stock"] = Path(distil)

    # Fine-tune turbo: round 3a's recipe from stock, the whole model.
    steps, lr, key_frac = s(1200), 3e-6, 0.3
    model, proc = kr.load(turbo)
    avg_at = {s(800), s(1000), steps}
    running = {}

    def checkpoint(step):
        if step in avg_at:
            for k, v in model.state_dict().items():
                running[k] = running.get(k, 0) + v.detach().float().cpu()
        if step in (s(600), steps):
            label = f"turbo fine-tuned, {step} steps (lr 3e-6, months/numbers 30%)"
            evaluate(label, tests, hf_hyps(model, proc, tests), "greedy")
            candidates[label] = save_hf(model, proc, WORK / f"turbo-{step}")
    kr.train(model, proc, kr.manifest("train_all.csv"), steps, lr, aug=True, key_frac=key_frac, seed=5,
             checkpoints={s(600), s(800), s(1000), steps}, on_checkpoint=checkpoint,
             optim="adamw8bit", grad_ckpt=True)
    avg_label = f"turbo fine-tuned, average of steps {', '.join(map(str, sorted(avg_at)))}"
    model.load_state_dict({k: (v / len(avg_at)) for k, v in running.items()})
    del running
    evaluate(avg_label, tests, hf_hyps(model, proc, tests), "greedy")
    candidates[avg_label] = save_hf(model, proc, WORK / "turbo-avg")
    del model
    torch.cuda.empty_cache()
    for label in (f"turbo fine-tuned, {steps} steps (lr 3e-6, months/numbers 30%)", avg_label):
        server_score(label, candidates[label], tests, LATENCY)

    # The rule: lowest quiet + talk (greedy) below round 3a's, recall not lower.
    greedy = {r["label"]: r for r in RESULTS if r["kind"] == "greedy"}
    start = greedy["round 3a (current best, Whisper small)"]
    ok = [greedy[label] for label in candidates if label in greedy
          and greedy[label]["sum"] < start["sum"] and greedy[label]["recall"] >= start["recall"]]
    best = min(ok, key=lambda r: r["sum"]) if ok else None
    if best:
        d, lo, hi = paired_ci(tests.spk, start["err"], best["err"])
        VERDICT[0] = (f"Best: **{best['label']}** ({best['quiet'][0]:.1%} quiet + {best['talk'][0]:.1%} talk = "
                      f"{best['sum']:.1%}; round 3a = {start['sum']:.1%}; paired difference {d:+.1%}, "
                      f"95% interval {lo:+.1%} to {hi:+.1%}). It beats round 3a.")
    else:
        VERDICT[0] = "Nothing beat round 3a with recall kept; no new model."
    log(VERDICT[0])
    write_report()
    if best:
        export(candidates[best["label"]], best)
    log("DONE")


def export(path, best):
    """The winner as 16-bit weights plus int8 CTranslate2 for faster-whisper."""
    final = OUT / "whisper-round5-best-fp16"
    model, proc = kr.load(path)
    save_hf(model, proc, final, half=True)
    (final / "SCORES.json").write_text(json.dumps({k: v for k, v in best.items() if k != "err"}, default=float, indent=1))
    ct2 = OUT / "whisper-round5-best-ct2"
    subprocess.run(["ct2-transformers-converter", "--model", str(final), "--output_dir", str(ct2), "--force",
                    "--quantization", "int8", "--copy_files", "tokenizer.json", "preprocessor_config.json"], check=True)
    from faster_whisper import WhisperModel
    fw = WhisperModel(str(ct2), device="cpu", compute_type="int8")
    for row, ref in list(zip(TESTS.rows, TESTS.refs))[:3]:
        segs, _ = fw.transcribe(load_audio(row["path"]), language="en", beam_size=5, word_timestamps=True)
        log(f"faster-whisper check: {''.join(x.text for x in segs)!r} (said: {ref!r})")
    shutil.rmtree(WORK / "ct2", ignore_errors=True)


if __name__ == "__main__":
    main()
