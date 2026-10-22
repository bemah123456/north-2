"""Pack the training scripts into one Kaggle job (a private script kernel on a T4 GPU).

    python3 build_kaggle.py <kaggle username> [--smoke]   -> kaggle/<kernel>/ ; then
    kaggle kernels push -p kaggle/<kernel>

The job unpacks the scripts, installs jiwer and ctranslate2, and runs kaggle_rounds.py.
Its results (results.md, the best model) are the kernel's output: kaggle kernels output <id>.
--smoke runs a quick end-to-end check first (2 shards, tiny rounds), about 15 minutes.

Further rounds from an earlier job's best model:
    python3 build_kaggle.py <user> --slug north2-whisper-round4 --from-kernel <user>/north2-whisper-rounds \
        --start-label "round 3a" --rounds rounds4.json
The earlier job's output is mounted read-only; nothing is uploaded from this computer.

Round 5 (a bigger base model, scored as the server decodes too; needs round 3a's job):
    python3 build_kaggle.py <user> --slug north2-whisper-round5 --from-kernel <user>/north2-whisper-rounds \
        --script kaggle_round5.py      [--smoke for a quick check first]
"""
import argparse
import base64
import io
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ["common.py", "compare_models.py", "fetch_cv17_older.py", "prepare_cv.py", "extend_train_manifest.py",
         "finetune_whisper.py", "kaggle_rounds.py", "kaggle_round5.py", "fw_score.py"]

RUNNER = '''# North 2: Whisper small training rounds (built by research/pc/training/build_kaggle.py).
import base64, io, os, subprocess, sys, zipfile
CODE = "{code}"
work = "/tmp/work/training"
os.makedirs(work, exist_ok=True)
zipfile.ZipFile(io.BytesIO(base64.b64decode(CODE))).extractall(work)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "jiwer", "ctranslate2", {extra}], check=True)
import soundfile
print("libsndfile", soundfile.__libsndfile_version__, flush=True)  # 1.1+ reads mp3
start = ""
for root, dirs, files in os.walk("/kaggle/input"):
    if os.path.basename(root) == "whisper-small-best-fp16" and "config.json" in files:
        start = root
print("start model:", start or "(none: rebuild from stock)", flush=True)
env = dict(os.environ, SMOKE="{smoke}", START_FROM=start if {follow} else "", START_LABEL={label!r},
           ROUNDS={rounds!r}, R3A=start, OUT_DIR="/kaggle/working", DATA_DIR="/tmp/data", PYTHONUNBUFFERED="1",
           PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True")
# CTranslate2 finds the GPU's cuDNN/cuBLAS in the pip-installed nvidia packages.
import glob, site
libs = [d for sp in site.getsitepackages() for d in glob.glob(sp + "/nvidia/*/lib")]
env["LD_LIBRARY_PATH"] = ":".join(libs + [env.get("LD_LIBRARY_PATH", "")])
subprocess.run([sys.executable, "-I", work + "/{script}"], check=True, env=env)
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("user")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--from-kernel", default=None, help="user/slug whose best model to continue from")
    ap.add_argument("--start-label", default="")
    ap.add_argument("--rounds", type=Path, default=None, help="JSON list of rounds to run from that model")
    ap.add_argument("--script", default="kaggle_rounds.py", help="kaggle_round5.py for round 5")
    args = ap.parse_args()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            z.write(HERE / f, f)
    slug = args.slug or ("north2-whisper-smoke" if args.smoke else "north2-whisper-rounds")
    out = HERE / "kaggle" / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.py").write_text(RUNNER.format(code=base64.b64encode(buf.getvalue()).decode(),
                                              smoke="1" if args.smoke else "0",
                                              follow=bool(args.from_kernel) and args.script == "kaggle_rounds.py",
                                              label=args.start_label, script=args.script,
                                              extra=", ".join(repr(x) for x in (["faster-whisper", "bitsandbytes"]
                                                              if args.script != "kaggle_rounds.py" else [])) or "",
                                              rounds=args.rounds.read_text() if args.rounds else "[]"))
    meta = {"id": f"{args.user}/{slug}", "title": slug, "code_file": "run.py", "language": "python",
            "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_tpu": False,
            "enable_internet": True, "machine_shape": "NvidiaTeslaT4", "dataset_sources": [],
            "competition_sources": [], "kernel_sources": [args.from_kernel] if args.from_kernel else [], "model_sources": []}
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))
    print(f"built {out}; push with: kaggle kernels push -p {out}")


if __name__ == "__main__":
    main()
