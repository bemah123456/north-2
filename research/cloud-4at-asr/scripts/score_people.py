"""Score the six people's answers with the app's merged code (main).

Each transcript goes through the app's own path: its clip check (speech
heard?), retry_reason (ask again when misheard or exactly one month is
missing) and the orientation and attention rules. An answer is right,
wrong, "ask again" or "unsure" (the rules couldn't decide; the app would
ask Claude or a person).

With FIXES=1, fixes_people.py's proposed rule changes are applied first.

Usage: score_people.py APP_SERVER_DIR AUDIO_DIR HYP_DIR OUT_DIR
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, sys.argv[1])
from checkin import answers as A  # noqa: E402
from checkin import scoring as S  # noqa: E402
from checkin import transcribe as T  # noqa: E402

from answers_people import DAY, PEOPLE  # noqa: E402

if os.environ.get("FIXES"):
    import fixes_people
    fixes_people.apply(A, S)

AUDIO, HYPS, OUT = Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
TODAY = date.fromisoformat(DAY)
PERSON = {p["id"]: {"birth_date": p["birth_date"], "place_keywords": ["home", p["town"]]} for p in PEOPLE}


def outcome(r, text, heard):
    ex = SimpleNamespace(kind=r["kind"])
    if S.retry_reason(ex, {"transcript": text, "heard_speech": heard}):
        return "ask again"
    if r["kind"] == "months_backwards":
        return "wrong" if A.score_attention(r["kind"], text)["score"] else "right"
    ok, _ = S._check_orientation(ex, text, PERSON[r["person"]], TODAY)
    return "unsure" if ok is None else "right" if ok else "wrong"


def main():
    rows = [json.loads(l) for l in (AUDIO / "manifest.jsonl").read_text().splitlines()]
    OUT.mkdir(parents=True, exist_ok=True)
    cache_f = OUT / "clip_check.json"
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    for r in rows:
        if r["path"] not in cache:
            cache[r["path"]] = T.clip_check((AUDIO / r["path"]).read_bytes())
    cache_f.write_text(json.dumps(cache))
    perfect = Counter(outcome(r, r["text"], True) == ("right" if r["label"] == "healthy" else "wrong")
                      for r in rows if r["condition"] == "clean" and r["voice"] == rows[0]["voice"])
    print("perfect transcripts scored as intended:", dict(perfect))
    summary, errors = [], []
    for f in sorted(HYPS.glob("*.jsonl")):
        hyp = {json.loads(l)["path"]: json.loads(l)["hyp"] for l in f.read_text().splitlines()}
        model = f.stem
        groups = defaultdict(Counter)
        for r in rows:
            if r["path"] not in hyp:
                continue
            o = outcome(r, hyp[r["path"]], bool((cache[r["path"]] or {}).get("heard_speech", True)))
            for g in (("all", r["condition"]), ("accent:" + r["accent"], r["condition"]),
                      ("person:" + r["person"], r["condition"]), ("kind:" + r["kind"], r["condition"])):
                groups[g][f"{r['label']}_{o}"] += 1
                groups[g][r["label"]] += 1
            bad = (r["label"] == "healthy" and o != "right") or (r["label"] == "impaired" and o == "right")
            if bad:
                errors.append({"model": model, **{k: r[k] for k in ("condition", "voice", "accent", "person", "kind", "label", "text")},
                               "heard": hyp[r["path"]], "outcome": o})
        for (g, cond), c in sorted(groups.items()):
            summary.append({"model": model, "group": g, "condition": cond, **c})
            if g == "all" or g.startswith("accent:"):
                h, i = c["healthy"], c["impaired"]
                print(f"{model[12:]:28}{g:44}{cond:6} healthy wrong {c['healthy_wrong'] / h:6.1%} "
                      f"ask again {c['healthy_ask again'] / h:5.1%} unsure {c['healthy_unsure'] / h:5.1%} | "
                      f"impaired passed {c['impaired_right'] / i:5.1%}")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1))
    (OUT / "errors.jsonl").write_text("".join(json.dumps(e) + "\n" for e in errors))


if __name__ == "__main__":
    main()
