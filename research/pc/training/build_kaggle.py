"""Pack the training scripts into one Kaggle job (a private script kernel on a T4 GPU).

    python3 build_kaggle.py <kaggle username> [--smoke]   -> kaggle/<kernel>/ ; then
    kaggle kernels push -p kaggle/<kernel>

The job unpacks the scripts, installs jiwer and ctranslate2, and runs kaggle_rounds.py.
Its results (results.md, the best model) are the kernel's output: kaggle kernels output <id>.
--smoke runs a quick end-to-end check first (2 shards, tiny rounds), about 15 minutes.
"""
import argparse
import base64
import io
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ["common.py", "compare_models.py", "fetch_cv17_older.py", "prepare_cv.py", "extend_train_manifest.py",
         "finetune_whisper.py", "kaggle_rounds.py"]

RUNNER = '''# North 2: Whisper small training rounds (built by research/pc/training/build_kaggle.py).
import base64, io, os, subprocess, sys, zipfile
CODE = "{code}"
work = "/tmp/work/training"
os.makedirs(work, exist_ok=True)
zipfile.ZipFile(io.BytesIO(base64.b64decode(CODE))).extractall(work)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "jiwer", "ctranslate2"], check=True)
import soundfile
print("libsndfile", soundfile.__libsndfile_version__, flush=True)  # 1.1+ reads mp3
env = dict(os.environ, SMOKE="{smoke}", OUT_DIR="/kaggle/working", DATA_DIR="/tmp/data", PYTHONUNBUFFERED="1",
           PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True")
subprocess.run([sys.executable, "-I", work + "/kaggle_rounds.py"], check=True, env=env)
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("user")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            z.write(HERE / f, f)
    slug = "north2-whisper-smoke" if args.smoke else "north2-whisper-rounds"
    out = HERE / "kaggle" / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.py").write_text(RUNNER.format(code=base64.b64encode(buf.getvalue()).decode(),
                                              smoke="1" if args.smoke else "0"))
    meta = {"id": f"{args.user}/{slug}", "title": slug, "code_file": "run.py", "language": "python",
            "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_tpu": False,
            "enable_internet": True, "machine_shape": "NvidiaTeslaT4", "dataset_sources": [],
            "competition_sources": [], "kernel_sources": [], "model_sources": []}
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))
    print(f"built {out}; push with: kaggle kernels push -p {out}")


if __name__ == "__main__":
    main()
