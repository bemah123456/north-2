"""Score every model's transcripts with the app's 4AT rules, with and
without the fixes in robust.py.

Usage: analyze.py AUDIO_DIR HYP_DIR OUT_DIR
"""

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from itertools import product
from pathlib import Path

import jiwer
import soundfile as sf
from num2words import num2words

import robust
from answers_set import DAY, HEALTHY, IMPAIRED, PERSON

sys.path.insert(0, "/mnt/project-files/daily-checkin/server")
from checkin import answers as A  # noqa: E402

AUDIO, HYPS, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
TODAY = date.fromisoformat(DAY)
BIRTH = date.fromisoformat(PERSON["birth_date"])
ORIENT = ["age", "dob", "place", "year"]
ATTN = ["months_backwards", "days_backwards", "countdown_20"]
TEXT = {f"{lab}-{k}-{i}": t for lab, tab in (("healthy", HEALTHY), ("impaired", IMPAIRED))
        for k, ts in tab.items() for i, t in enumerate(ts)}


def app_verdict(kind, text):
    if kind == "age":
        return A.check_age(text, BIRTH, TODAY)
    if kind == "dob":
        return A.check_dob(text, BIRTH)
    if kind == "place":
        return A.check_place(text, PERSON["place_keywords"])
    if kind == "year":
        return A.check_year(text, TODAY)
    return A.score_attention(kind, text)


def fixed_verdict(kind, text, speech):
    return robust.verdict(kind, text, BIRTH, TODAY, PERSON["place_keywords"], speech)


def part_score(v):
    """Points this answer adds to the 4AT, or None if it must be asked again."""
    if isinstance(v, dict):
        return v["score"]
    return None if v is None else (0 if v else 1)


def spell(text):
    """Lower case, no punctuation, numbers as words, for word error rate."""
    def num(m):
        s, suffix = m.group(1), m.group(2)
        n = int(s)
        if suffix:
            return num2words(n, to="ordinal")
        if 1900 <= n <= 2099 and len(s) == 4:
            return num2words(n, to="year")
        return num2words(n)
    text = text.lower()
    text = re.sub(r"(\d+)(st|nd|rd|th)?", num, text)
    text = re.sub(r"[^a-z' ]", " ", text.replace("-", " "))
    text = re.sub(r"\band\b", " ", text)
    return " ".join(text.split())


def main():
    rows = [json.loads(l) for l in (AUDIO / "manifest.jsonl").read_text().splitlines()]
    meta = {r["path"]: r for r in rows}
    hyps = defaultdict(dict)
    for f in sorted(HYPS.glob("*.jsonl")):
        for l in f.read_text().splitlines():
            h = json.loads(l)
            hyps[h["model"]][h["path"]] = h["hyp"]

    # Compare models on the clips every model has heard.
    common = set.intersection(*(set(p) for p in hyps.values()))
    voices = sorted({meta[p]["voice"] for p in common})
    OUT.mkdir(parents=True, exist_ok=True)
    speech_cache = OUT / "speech.json"
    speech = json.loads(speech_cache.read_text()) if speech_cache.exists() else {}
    for p in common - set(speech):
        x, sr = sf.read(AUDIO / p, dtype="float32")
        speech[p] = robust.has_speech(x, sr)
    speech_cache.write_text(json.dumps(speech))

    summary, errors = [], []
    for model, by_path in sorted(hyps.items()):
        for cond in ("clean", "older", "tv"):
            paths = sorted(p for p in common if meta[p]["condition"] == cond)
            if not paths:
                continue
            refs = [spell(meta[p]["text"]) for p in paths]
            outs = [spell(by_path[p]) or "<empty>" for p in paths]
            base = {"model": model, "condition": cond, "voices": len(voices), "answers": len(paths),
                    "wer": round(jiwer.wer(refs, outs), 4),
                    "empty": sum(1 for p in paths if not by_path[p].strip()),
                    "months_inserted": sum(sum((Counter(A.months_in(by_path[p])) - Counter(A.months_in(meta[p]["text"]))).values()) for p in paths),
                    "numbers_inserted": sum(sum((Counter(A.numbers(by_path[p], False)) - Counter(A.numbers(meta[p]["text"], False))).values()) for p in paths)}
            for scorer in ("app", "fixed"):
                c = Counter()
                score = defaultdict(dict)  # voice -> item id -> part score
                for p in paths:
                    r, hyp = meta[p], by_path[p]
                    v = app_verdict(r["kind"], hyp) if scorer == "app" else fixed_verdict(r["kind"], hyp, speech[p])
                    s = part_score(v)
                    score[r["voice"]][r["id"]] = s
                    healthy = r["label"] == "healthy"
                    c["healthy" if healthy else "impaired"] += 1
                    if s is None:
                        c["healthy_reask" if healthy else "impaired_reask"] += 1
                    elif healthy and s > 0:
                        c["healthy_marked_wrong"] += 1
                        errors.append({"model": model, "condition": cond, "scorer": scorer, "voice": r["voice"],
                                       "said": r["text"], "heard": hyp, "type": "healthy marked wrong"})
                    elif not healthy and s == 0:
                        c["impaired_marked_right"] += 1
                        errors.append({"model": model, "condition": cond, "scorer": scorer, "voice": r["voice"],
                                       "said": r["text"], "heard": hyp, "type": "impaired marked right"})

                # Whole check-ins (4AT parts 2 and 3; alertness and acute
                # change come from the family and the voice baseline).
                # Healthy: every mix of one healthy answer per orientation
                # item and one attention answer; the right total is 0.
                # Impaired: two wrong orientation answers plus a failed
                # attention task; compared with the perfect-transcript total.
                for voice, got in score.items():
                    if len(got) < len(TEXT):
                        continue
                    attn_ids = [f"healthy-{k}-{i}" for k in ATTN for i in range(len(HEALTHY[k]))]
                    orient_ids = [[f"healthy-{k}-{i}" for i in range(len(HEALTHY[k]))] for k in ORIENT]
                    for combo in product(*orient_ids, attn_ids):
                        parts = [got[i] for i in combo]
                        c["healthy_checkins"] += 1
                        if None in parts:
                            c["healthy_checkin_reask"] += 1
                            parts = [x or 0 for x in parts]
                        total = min(sum(parts[:4]), 2) + parts[4]
                        c["healthy_checkin_flagged"] += total >= 1
                        c["healthy_checkin_4plus"] += total >= 4
                    for k1, k2 in (("year", "age"), ("place", "dob"), ("year", "place"), ("age", "dob")):
                        others = [k for k in ORIENT if k not in (k1, k2)]
                        for i1, i2 in product(range(len(IMPAIRED[k1])), range(len(IMPAIRED[k2]))):
                            ids = [f"impaired-{k1}-{i1}", f"impaired-{k2}-{i2}"] + [f"healthy-{k}-0" for k in others]
                            truth_o = min(sum(part_score(app_verdict(i.split("-")[1], TEXT[i])) or 0 for i in ids), 2)
                            for ka in ATTN:
                                for ia in range(len(IMPAIRED[ka])):
                                    aid = f"impaired-{ka}-{ia}"
                                    truth = truth_o + app_verdict(ka, TEXT[aid])["score"]
                                    parts = [got[i] for i in ids + [aid]]
                                    total = min(sum(x or 0 for x in parts[:4]), 2) + (parts[4] or 0)
                                    c["impaired_checkins"] += 1
                                    c["impaired_checkin_flagged"] += total >= 1
                                    c["impaired_checkin_exact"] += total == truth
                summary.append({**base, "scorer": scorer, **c})

    (OUT / "summary.json").write_text(json.dumps(summary, indent=1))
    (OUT / "errors.jsonl").write_text("".join(json.dumps(e) + "\n" for e in errors))
    print(f"{len(common)} common clips, {len(voices)} voices")
    for s in summary:
        print(f"{s['model'][12:]:<32}{s['condition']:<6}{s['scorer']:<6}WER {s['wer']:.3f} "
              f"healthy wrong {s.get('healthy_marked_wrong', 0):>3}/{s.get('healthy', 0)} reask {s.get('healthy_reask', 0):>3} "
              f"impaired right {s.get('impaired_marked_right', 0):>2}/{s.get('impaired', 0)} "
              f"checkin FP {s.get('healthy_checkin_flagged', 0) / max(s.get('healthy_checkins', 1), 1):.1%} "
              f"impaired flagged {s.get('impaired_checkin_flagged', 0) / max(s.get('impaired_checkins', 1), 1):.1%}")


if __name__ == "__main__":
    main()
