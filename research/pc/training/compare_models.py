"""Compare speech models on (1) held-out older speakers and (2) 4AT answer probes.

Usage (after finetune_whisper.py and make_probes.ps1):
    python -I compare_models.py openai/whisper-tiny openai/whisper-base openai/whisper-small \
        distil-whisper/distil-small.en out/whisper-base

Part 1, older speakers (Common Voice, speakers never seen in training):
  word error rate with a 95% interval from resampling speakers, month/number/day recall,
  and false month/number/day insertions (words the model "heard" that were never said).
Part 2, 4AT probes (synthetic voices, clean and with noise at 10 dB SNR): each answer is scored
  with the app's own scorer (prototype/scorer.js).
  False positive = a correct answer judged wrong (would push a healthy person's score up).
  Missed impairment = a wrong answer judged right.
Writes out/comparison.md.
"""
import json
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from jiwer import wer  # noqa: E402
from transformers import WhisperForConditionalGeneration, WhisperProcessor  # noqa: E402

from common import KEY_WORDS, SR, load_audio, normalise, read_manifest  # noqa: E402


MONTH_PROMPT = "December, November, October, September, August, July, June, May, April, March, February, January."


def transcribe_audio(model, processor, audios, batch=8, prompt=None):
    hyps = []
    # English-only checkpoints (".en") reject language/task arguments.
    kw = {} if getattr(model.generation_config, "is_multilingual", True) is False else \
        {"language": "en", "task": "transcribe"}
    if prompt:
        kw["prompt_ids"] = processor.get_prompt_ids(prompt, return_tensors="pt")
        batch = 1  # prompted generation is done one clip at a time
    with torch.no_grad():
        for i in range(0, len(audios), batch):
            feats = processor(audios[i:i + batch], sampling_rate=SR, return_tensors="pt").input_features
            ids = model.generate(feats, max_new_tokens=160, **kw)
            # generate() returns only the new tokens, so a correct answer may equal the prompt.
            hyps += processor.batch_decode(ids, skip_special_tokens=True)
    return [normalise(h) for h in hyps]


def key_stats(refs, hyps):
    hit = total = inserted = 0
    for ref, hyp in zip(refs, hyps):
        r = Counter(w for w in ref.split() if w in KEY_WORDS)
        h = Counter(w for w in hyp.split() if w in KEY_WORDS)
        total += sum(r.values())
        hit += sum(min(c, h[w]) for w, c in r.items())
        inserted += sum(max(0, c - r[w]) for w, c in h.items())
    return hit / max(total, 1), inserted, total


def speaker_bootstrap_wer(rows, refs, hyps, n=1000, seed=7):
    by_spk = defaultdict(list)
    for i, r in enumerate(rows):
        by_spk[r["client_id"]].append(i)
    spks = list(by_spk)
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        idx = [i for s in rng.choices(spks, k=len(spks)) for i in by_spk[s]]
        vals.append(wer([refs[i] for i in idx], [hyps[i] for i in idx]))
    return np.percentile(vals, 2.5), np.percentile(vals, 97.5)


def add_noise(audio, snr_db, rng):
    noise = rng.standard_normal(len(audio)).astype(np.float32)
    p_sig = np.mean(audio ** 2) + 1e-9
    noise *= np.sqrt(p_sig / (10 ** (snr_db / 10)) / np.mean(noise ** 2))
    return audio + noise


def score_probes(probes, transcripts):
    payload = json.dumps([{"kind": p["kind"], "transcript": t} for p, t in zip(probes, transcripts)])
    res = subprocess.run(["node", str(HERE / "probe_score.js")], input=payload, capture_output=True,
                         text=True, check=True)
    return [r["judgedHealthy"] for r in json.loads(res.stdout)]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="+", help="HF id or local folder; add @prompt to prompt the months task")
    ap.add_argument("--probes-only", action="store_true")
    ap.add_argument("--out", default="comparison.md")
    ap.add_argument("--talk", action="store_true",
                    help="also test with background talk (2 other speakers at 10 dB), like a TV")
    args = ap.parse_args()
    models = args.models
    test_rows = [] if args.probes_only else read_manifest(HERE / "manifests" / "test.csv")
    test_audio = [load_audio(r["path"]) for r in test_rows]
    refs = [normalise(r["sentence"]) for r in test_rows]

    probes = json.loads((HERE / "probes" / "probes.json").read_text(encoding="utf-8-sig"))
    rng = np.random.default_rng(3)
    clean = [load_audio(p["path"]) for p in probes]
    noisy = [add_noise(a, 10, rng) for a in clean]
    conditions = [("clean", clean), ("noisy 10 dB", noisy)]
    test_talk = []
    if args.talk:
        # Background talkers come from training speakers (never the test speakers).
        pool = read_manifest(HERE / "manifests" / "train.csv")
        prng = random.Random(11)

        def with_talk(a):
            parts = [load_audio(prng.choice(pool)["path"]) for _ in range(2)]
            n = sum(np.pad(np.resize(p, len(a)), (0, 0)) for p in parts)
            return (a + n * np.sqrt((np.mean(a ** 2) + 1e-9) / ((np.mean(n ** 2) + 1e-9) * 10))).astype(np.float32)
        conditions.append(("background talk 10 dB", [with_talk(a) for a in clean]))
        test_talk = [with_talk(a) for a in test_audio]

    table1, table2, examples = [], [], []
    months_idx = [i for i, p in enumerate(probes) if p["kind"] == "months"]
    for spec in models:
        name, _, flag = spec.partition("@")
        prompt = MONTH_PROMPT if flag == "prompt" else None
        path = HERE / name if (HERE / name).exists() else name
        t = time.time()
        processor = WhisperProcessor.from_pretrained(path)
        model = WhisperForConditionalGeneration.from_pretrained(path).float().eval()  # some ship fp16
        params = sum(p.numel() for p in model.parameters()) / 1e6

        if test_rows:
            hyps = transcribe_audio(model, processor, test_audio)
            w = wer(refs, hyps)
            lo, hi = speaker_bootstrap_wer(test_rows, refs, hyps)
            recall, inserted, n_key = key_stats(refs, hyps)
            sec_per_clip = (time.time() - t) / len(test_rows)
            talk_col = ""
            if test_talk:
                talk_hyps = transcribe_audio(model, processor, test_talk)
                tw = wer(refs, talk_hyps)
                tlo, thi = speaker_bootstrap_wer(test_rows, refs, talk_hyps)
                talk_col = f" {tw:.1%} ({tlo:.1%} to {thi:.1%}) |"
            table1.append(f"| {spec} | {params:.0f}M | {w:.1%} ({lo:.1%} to {hi:.1%}) |{talk_col} {recall:.1%} of {n_key} | "
                          f"{inserted} ({inserted / max(n_key, 1) * 100:.1f} per 100) | {sec_per_clip:.2f} s |")
            print(table1[-1], flush=True)

        for cond, audios in conditions:
            trans = transcribe_audio(model, processor, audios)
            if prompt:  # the app would prompt only the months question
                prompted = transcribe_audio(model, processor, [audios[i] for i in months_idx], prompt=prompt)
                for i, tr in zip(months_idx, prompted):
                    trans[i] = tr
            judged = score_probes(probes, trans)
            healthy = [p["healthy"] for p in probes]
            fp = sum(1 for h, j in zip(healthy, judged) if h and j is False)
            fn = sum(1 for h, j in zip(healthy, judged) if not h and j is True)
            ask_h = sum(1 for h, j in zip(healthy, judged) if h and j is None)
            ask_i = sum(1 for h, j in zip(healthy, judged) if not h and j is None)
            n_h = sum(healthy)
            n_i = len(healthy) - n_h
            table2.append(f"| {spec} | {cond} | {fp}/{n_h} ({fp / n_h:.0%}) | {ask_h}/{n_h} | "
                          f"{fn}/{n_i} ({fn / n_i:.0%}) | {ask_i}/{n_i} |")
            for p, tr, h, j in zip(probes, trans, healthy, judged):
                if j is not None and h != j:
                    examples.append(f"- {spec}, {cond}: said \"{p['text']}\" -> heard \"{tr}\" "
                                    f"({'false positive' if h else 'missed impairment'})")
            print(table2[-1], flush=True)
        del model

    report = [
        f"# Model comparison ({time.strftime('%Y-%m-%d %H:%M')})", "",
        f"## Older speakers held out from training ({len(test_rows)} Common Voice clips, "
        f"{len({r['client_id'] for r in test_rows})} speakers aged 60+)", "",
        ("| Model | Size | Word error rate (95% interval) | With background talk 10 dB | Month/number/day recall | "
         "False month/number/day insertions | Time per clip (CPU) |" if test_talk else
         "| Model | Size | Word error rate (95% interval) | Month/number/day recall | False month/number/day insertions | Time per clip (CPU) |"),
        "|---|---|---|---|---|---|" + ("---|" if test_talk else ""), *table1, "",
        f"## 4AT answer probes ({len(probes)} synthetic clips per condition)", "",
        "False positive: a correct answer judged wrong, which would raise a healthy person's 4AT score. "
        "Missed impairment: a wrong answer judged right. Ask again: exactly one month missing, so the app "
        "repeats the question instead of scoring it.", "",
        "| Model | Audio | False positives | Ask again (correct answers) | Missed impairments | Ask again (wrong answers) |",
        "|---|---|---|---|---|---|", *table2, "",
        "## Every probe error", "", *(examples or ["None."]), "",
        "Limits: probes use two synthetic adult voices, not older speakers, and do not test real delirium. "
        "A clinical false-positive rate needs recordings from people with and without delirium.",
    ]
    out = HERE / "out" / args.out
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
