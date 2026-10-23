"""Score Gemini (listening to the audio directly) on the same test clips as round 5, and compare
any set of transcripts with paired, speaker-resampled intervals.

    python -I gemini_bench.py run <testset folder> [--model gemini-3.6-flash] [--prompt server]
    python -I gemini_bench.py score <testset folder> <hyps.jsonl> [<hyps.jsonl> ...]

The testset folder holds export_testset.py's testset.npz and testset.json. The key is read from
~/.config/gemini/api_key (or GEMINI_API_KEY) and sent only to Google's API, in a header.
Gemini gets the clip and a transcription instruction, never the expected answer or anything
about the speaker, so it can't hear what it expects. Transcripts are cached in
<testset folder>/gemini-<model>[-server].jsonl, so a rerun continues where it stopped.

gemini-2.5-flash is closed to new API keys (404 "no longer available to new users",
2026-10-22); the default is gemini-3.6-flash, the model the check-in server pins (PR #41).
--prompt server sends exactly what the server sends (checkin/gemini.py: its transcription
prompt, JSON reply, thinking level low), so the result says what GEMINI_TRANSCRIBE=1 would
give. That prompt asks for fillers, which the references don't have, so fillers are left
out of both sides when scoring.
"""
import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
from jiwer import process_words  # noqa: E402

from common import normalise  # noqa: E402

CONDS = ["quiet", "talk", "voices"]
# What the check-in server sends with GEMINI_TRANSCRIBE=1 (checkin/gemini.py, TRANSCRIBE_PROMPT).
SERVER_PROMPT = (
    "Transcribe the main speaker in this recording verbatim, exactly as spoken, "
    "including filler words (um, uh), repetitions, false starts and mistakes. "
    "Do not correct or complete anything. Leave out background voices, TV, radio "
    "and other people. Write numbers as digits. If the main speaker says nothing, "
    "return an empty transcript."
)
FILLERS = {"um", "uh", "er", "erm", "hmm", "uhm", "ah", "mm"}

PROMPT = ("Transcribe what the main speaker in this recording says, word for word, in English. "
          "Other people or a TV may be talking in the background: leave them out. "
          "Reply with the transcript only. If the main speaker says nothing, reply with nothing.")


def load(folder):
    rows = json.loads((folder / "testset.json").read_text())
    z = np.load(folder / "testset.npz")
    audio = {}
    for c in CONDS:
        a, off = z[c], z[c + "_offsets"]
        audio[c] = [a[off[i]:off[i + 1]] for i in range(len(off) - 1)]
    return rows, audio


def wav_bytes(x):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(x.astype(np.int16).tobytes())
    return buf.getvalue()


def key():
    f = Path.home() / ".config" / "gemini" / "api_key"
    return os.environ.get("GEMINI_API_KEY") or f.read_text().strip()


def ask(model, clip, api_key, prompt="plain"):
    cfg = {"temperature": 0}
    if model.startswith("gemini-2.5-flash"):
        cfg["thinkingConfig"] = {"thinkingBudget": 0}  # plain transcription needs no thinking
    elif model.startswith("gemini-3"):
        cfg["thinkingConfig"] = {"thinkingLevel": "low"}  # the lowest every Gemini 3 flash accepts
    if prompt == "server":
        cfg |= {"responseMimeType": "application/json", "responseSchema": {
            "type": "OBJECT", "properties": {"transcript": {"type": "STRING"}}, "required": ["transcript"]}}
    body = json.dumps({"contents": [{"role": "user", "parts": [
        {"inline_data": {"mime_type": "audio/wav", "data": base64.b64encode(wav_bytes(clip)).decode()}},
        {"text": SERVER_PROMPT if prompt == "server" else PROMPT}]}], "generationConfig": cfg}).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    for attempt in range(8):
        req = urllib.request.Request(url, data=body, headers={"x-goog-api-key": api_key,
                                                              "Content-Type": "application/json"})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=120))
            parts = d.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
            if prompt != "server" or not text:
                return text
            try:
                return str(json.loads(text)["transcript"]).strip()
            except (ValueError, KeyError, TypeError):
                return ""  # the server would fall back to Whisper here; scored as nothing heard
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 503) and attempt < 7:
                time.sleep(min(120, 5 * 2 ** attempt))
                continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("gave up after retries")


def run(args):
    rows, audio = load(args.folder)
    tag = args.model + ("-server" if args.prompt == "server" else "")
    out = args.folder / f"gemini-{tag}.jsonl"
    done = {}
    if out.exists():
        for line in out.read_text().splitlines():
            r = json.loads(line)
            done[(r["cond"], r["i"])] = r["text"]
    todo = [(c, i) for c in CONDS for i in range(len(rows)) if (c, i) not in done]
    print(f"{len(done)} cached, {len(todo)} to go", flush=True)
    api_key = key()
    t = time.time()
    with out.open("a") as f, ThreadPoolExecutor(args.workers) as pool:
        for n, ((c, i), text) in enumerate(zip(todo, pool.map(lambda ci: ask(args.model, audio[ci[0]][ci[1]], api_key, args.prompt),
                                                               todo))):
            f.write(json.dumps({"cond": c, "i": i, "text": text}) + "\n")
            f.flush()
            if n % 50 == 0:
                print(f"{n + 1}/{len(todo)} ({time.time() - t:.0f}s)", flush=True)
    # Same layout as kaggle_round5.py's hyps files.
    done = {(json.loads(x)["cond"], json.loads(x)["i"]): json.loads(x)["text"] for x in out.read_text().splitlines()}
    hyps = args.folder / f"hyps-gemini-{tag}.jsonl"
    with hyps.open("w") as f:
        for i, r in enumerate(rows):
            f.write(json.dumps({"path": r["path"], "ref": r["ref"], **{c: done[(c, i)] for c in CONDS}}) + "\n")
    print("wrote", hyps)


# ---------- scoring ----------

def errors(refs, hyps):
    e, n = [], []
    for r, h in zip(refs, hyps):
        r = " ".join(w for w in r.split() if w not in FILLERS)
        h = " ".join(w for w in normalise(h or "").split() if w not in FILLERS)
        e.append(process_words(r, h).wer * len(r.split()) if r else len(h.split()))
        n.append(len(r.split()))
    return np.array(e), np.array(n, float)


def per_speaker(spk, v):
    ids = sorted(set(spk))
    pos = {s: k for k, s in enumerate(ids)}
    out = np.zeros(len(ids))
    for s, x in zip(spk, v):
        out[pos[s]] += x
    return out


def score(args):
    rows, _ = load(args.folder)
    refs, spk = [r["ref"] for r in rows], [r["speaker"] for r in rows]
    names = {r["path"]: k for k, r in enumerate(rows)}
    idx = np.random.default_rng(7).integers(0, len(set(spk)), size=(2000, len(set(spk))))
    models = []
    for p in args.hyps:
        h = {c: [""] * len(rows) for c in CONDS}
        for line in Path(p).read_text().splitlines():
            r = json.loads(line)
            for c in CONDS:
                h[c][names[r["path"]]] = r[c]
        err = {c: errors(refs, h[c]) for c in CONDS}
        models.append((Path(p).stem.removeprefix("hyps-").removeprefix("greedy-").removeprefix("server-"), err))
    base = models[0][1]
    print(f"| Model | Quiet | Background talk 10 dB | Quiet + talk | vs {models[0][0]} (quiet + talk) | Unseen voices 10 dB |")
    print("|---|---|---|---|---|---|")
    for name, err in models:
        cells = []
        for c in CONDS:
            E, N = per_speaker(spk, err[c][0]), per_speaker(spk, err[c][1])
            v = E[idx].sum(1) / N[idx].sum(1)
            cells.append(f"{E.sum() / N.sum():.1%} ({np.percentile(v, 2.5):.1%} to {np.percentile(v, 97.5):.1%})")
        tot, d = 0, 0
        for c in ("quiet", "talk"):
            Ea, Eb, N = per_speaker(spk, base[c][0]), per_speaker(spk, err[c][0]), per_speaker(spk, err[c][1])
            tot = tot + (Eb[idx].sum(1) - Ea[idx].sum(1)) / N[idx].sum(1)
            d += (Eb.sum() - Ea.sum()) / N.sum()
        lo, hi = np.percentile(tot, 2.5), np.percentile(tot, 97.5)
        s = sum(err[c][0].sum() / err[c][1].sum() for c in ("quiet", "talk"))
        verdict = "-" if err is base else (f"{d:+.1%} ({lo:+.1%} to {hi:+.1%}), "
                                           + ("better" if hi < 0 else "worse" if lo > 0 else "within noise"))
        print(f"| {name} | {cells[0]} | {cells[1]} | {s:.1%} | {verdict} | {cells[2]} |")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("folder", type=Path)
    r.add_argument("--model", default="gemini-3.6-flash")
    r.add_argument("--prompt", choices=["plain", "server"], default="plain")
    r.add_argument("--workers", type=int, default=4)
    s = sub.add_parser("score")
    s.add_argument("folder", type=Path)
    s.add_argument("hyps", nargs="+")
    a = ap.parse_args()
    run(a) if a.cmd == "run" else score(a)


if __name__ == "__main__":
    main()
