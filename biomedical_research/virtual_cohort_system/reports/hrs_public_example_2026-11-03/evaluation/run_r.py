"""Run Rscript with the project-only extracted libraries inside WSL."""
from pathlib import Path
import os
import subprocess
import sys

root = Path(__file__).resolve().parent
runtime = root / "runtime/extracted"
env = dict(os.environ)
env["R_LIBS_USER"] = ":".join(str(runtime / q) for q in ["usr/lib/R/site-library", "usr/lib/R/library"])
env["LD_LIBRARY_PATH"] = str(runtime / "usr/lib/x86_64-linux-gnu") + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
try:
    completed = subprocess.run(["Rscript", "--vanilla", *sys.argv[1:]], env=env, timeout=300)
    raise SystemExit(completed.returncode)
except subprocess.TimeoutExpired:
    print("R subprocess exceeded the fixed 300-second evaluation limit; no retry.", file=sys.stderr)
    raise SystemExit(124)
