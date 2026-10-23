"""Download a Kaggle job's output files, resuming when the connection drops.

`kaggle kernels output` restarts large files from zero, and Kaggle's storage cuts long downloads
partway (a 187 MB file never finished), so this asks the Kaggle API for each file's link and
fetches it with `curl -C -`, which continues from the bytes already saved.

    python3 fetch_kaggle_output.py <user>/<job> <folder> [<regex on the file path>]
    python3 fetch_kaggle_output.py benjaminmahmutovic/north2-whisper-round5 ~/models/round5 whisper-round5-best-ct2/

Needs the kaggle package and its usual credentials (~/.kaggle); they are only used by that package.
"""
import re
import subprocess
import sys
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.kernels.types.kernels_api_service import ApiListKernelSessionOutputRequest


def main():
    job, dest = sys.argv[1], Path(sys.argv[2]).expanduser()
    pattern = re.compile(sys.argv[3]) if len(sys.argv) > 3 else None
    user, slug = job.split("/")
    api = KaggleApi()
    api.authenticate()
    files, token = [], None
    with api.build_kaggle_client() as k:
        while True:
            req = ApiListKernelSessionOutputRequest()
            req.user_name, req.kernel_slug, req.page_size = user, slug, 200
            if token:
                req.page_token = token
            resp = k.kernels.kernels_api_client.list_kernel_session_output(req)
            files += resp.files
            token = resp.next_page_token
            if not token:
                break
    for f in files:
        if pattern and not pattern.search(f.file_name):
            continue
        out = dest / f.file_name
        out.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(30):
            if subprocess.run(["curl", "-sS", "-L", "-C", "-", "--max-time", "600", "-o", str(out), f.url]).returncode == 0:
                break
        else:
            sys.exit(f"could not download {f.file_name}")
        print(f"{f.file_name}: {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
