"""One new-version dependency-only bwrap check; never reruns cohort slots."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
sys.path.insert(0, str(PROJECT))
from cohort_harness import execution

ROOT = Path("D:/Codex/home/tmp/vc_runtime_special_20261102_v2")
CODE = """import resource
resource.setrlimit(resource.RLIMIT_AS,(1024*1024**2,1024*1024**2))
import hashlib, json, pathlib, platform, sys, importlib.metadata
import numpy, scipy
from scipy import special
p=float(special.betainc(2.,3.,.5))
x=float(special.betaincinv(2.,3.,p))
assert abs(p-.6875)<1e-14 and abs(x-.5)<1e-14
files=[pathlib.Path(scipy.__file__),pathlib.Path(special.__file__),pathlib.Path(special._ufuncs.__file__)]
print(json.dumps({'scope':'pure_invented_dependency_check_no_cohort','python':platform.python_version(),'executable':sys.executable,'numpy':numpy.__version__,'pandas':importlib.metadata.version('pandas'),'scipy':scipy.__version__,'betainc':p,'inverse':x,'maximum_absolute_error':max(abs(p-.6875),abs(x-.5)),'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}))
"""


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=False)
    (ROOT / "input").mkdir()
    (ROOT / "output").mkdir()
    for name in ("generated.csv", "worker_report.json"):
        (ROOT / "output" / name).write_bytes(b"")
    command = execution._command(execution.DEFAULT_RUNTIME, ROOT, 30)
    command[-1:] = ["-c", CODE]
    result = execution._capture(command, ROOT, 40, 10000, ROOT / "stdout.log", ROOT / "stderr.log")
    result.update(kind="new_version_single_dependency_probe", actual_bwrap=True, cohort_generator_dispatched=False,
                  prior_failed_cohort_slots_rerun=False, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  command=command)
    if result["returncode"] == 0:
        result["probe"] = json.loads((ROOT / "stdout.log").read_text(encoding="utf-8"))
    else:
        result["error"] = (ROOT / "stderr.log").read_text(encoding="utf-8", errors="replace")
    result["generated_csv_placeholder_bytes"] = (ROOT / "output/generated.csv").stat().st_size
    with (ROOT / "RESULT.json").open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2); handle.write("\n")
    print(json.dumps(result, indent=2))
