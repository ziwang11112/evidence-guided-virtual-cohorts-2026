"""Allowlisted curation of the invented M12-C actual-Agent integration only."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

P = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import sha256, read_json
from cohort_harness.scientific_loop import verify_loop
from cohort_harness.calibration import verify_calibration

BASE = "66067e2f8ae90b1227ce6797ebe227375fd8b8c7"
DEST = P / "reports/m12c_2026-10-30"
ORIGIN = P / "work/m12c/run01"
EXPORT = P.parent / "github_virtual_cohort_2026-10-27"


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    state = verify_loop(ORIGIN)
    result = verify_calibration(ORIGIN, "initial_fit")
    original = read_json(ORIGIN / "agent_exchange/initial_input_manifest.json")["files"]
    assert all(sha256(ORIGIN / name) == digest for name, digest in original.items())
    assert read_json(ORIGIN / "task.json")["task_id"] == "m12c-invented-study-composition"
    DEST.mkdir(parents=True, exist_ok=True)
    copied = DEST / "run"
    if not copied.exists():
        shutil.copytree(ORIGIN, copied)
    else:
        expected = {f.relative_to(ORIGIN): sha256(f) for f in ORIGIN.rglob("*") if f.is_file()}
        actual = {f.relative_to(copied): sha256(f) for f in copied.rglob("*") if f.is_file()}
        assert actual == expected
    assert verify_loop(copied) == state
    assert verify_calibration(copied, "initial_fit") == result
    for name in ("pytest.xml", "pytest_output.txt", "integration_audit.json"):
        shutil.copyfile(P / "work/m12c" / name, DEST / name)
    prefix = "biomedical_research/virtual_cohort_system/"
    names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASE, "--", prefix+"cohort_harness"], cwd=EXPORT, text=True).splitlines()
    engines = {}
    for name in names:
        if name.endswith(".py"):
            original_bytes = subprocess.check_output(["git", "show", BASE+":"+name], cwd=EXPORT)
            relative = name.removeprefix(prefix)
            assert (P/relative).read_bytes() == original_bytes, relative
            engines[relative] = sha256(P/relative)
    reports = {}
    for name in ("source_location_transfer_2026-10-30", "source_context_engineering_2026-10-30", "m12b_2026-10-30"):
        folder = P / "reports" / name
        items = read_json(folder / "file_manifest.json")["files"]
        assert all(sha256(folder / rel) == digest for rel, digest in items.items())
        reports[name] = len(items)
    write(DEST / "historical_preservation.json", {"baseline_commit": BASE, "engines": engines, "reports": reports})
    selected = result["selected_trial"]
    write(DEST / "summary.json", {"scope": "invented_actual_agent_source_only_integration",
        "calibration_status": result["status"], "trials": len(result["trials"]),
        "fit_loss": result["trials"][selected]["fit"]["loss"], "replay_loss": result["replay"]["loss"],
        "executions": result["usage"]["executions"], "loop_usage": state["usage"],
        "choice": state["actions"]["source_review_01"]["decision"]["choice"], "pending": state["pending"],
        "parameter_changes": 0, "structural_repair_demonstrated": False, "target_validity_tested": False,
        "standalone_model_launcher": False, "copied_run_verified": True})
    shutil.copyfile(__file__, DEST / "curation_script.py")
    write(DEST / "file_manifest.json", {"scope": "Invented-only allowlisted archive; no patient data",
        "files": {f.relative_to(DEST).as_posix(): sha256(f) for f in sorted(DEST.rglob("*"))
                  if f.is_file() and f != DEST / "file_manifest.json"}})
    print(json.dumps({"copied_run_verified": True, "old_engines_preserved": len(engines),
        "old_report_files_preserved": reports, "manifest_files": len(read_json(DEST/"file_manifest.json")["files"])}, indent=2))


if __name__ == "__main__":
    main()
