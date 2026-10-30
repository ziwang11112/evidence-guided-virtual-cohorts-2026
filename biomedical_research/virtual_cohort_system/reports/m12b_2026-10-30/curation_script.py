"""Curate only explicitly invented M12-B bundles; never traverses patient work."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

P = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(P))
from cohort_harness.calibration import verify_calibration
from cohort_harness.calibration_budget import get_budget
from cohort_harness.lifecycle import sha256

DEST = P / "reports/m12b_2026-10-30"
EXPORT = P.parent / "github_virtual_cohort_2026-10-27"
BASE = "4d3db0bf6a8d1376ad19a3d7f2c2c453e600f784"


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    results = {}
    for name in ("fit", "conflict", "undefined"):
        origin, copied = P / "work/m12b" / name, DEST / name
        assert "Invented M12-B calibration fixture" in (origin / "README.md").read_text()
        result = verify_calibration(origin, "s")
        if not copied.exists():
            shutil.copytree(origin, copied)
        else:
            files = [f for f in origin.rglob("*") if f.is_file()]
            assert {f.relative_to(origin) for f in files} == {f.relative_to(copied) for f in copied.rglob("*") if f.is_file()}
            assert all(sha256(f) == sha256(copied / f.relative_to(origin)) for f in files)
        assert verify_calibration(copied, "s") == result
        selected = result["selected_trial"]
        record = result["trials"][selected] if selected is not None else None
        results[name] = {"status": result["status"], "stop_reason": result["stop_reason"],
            "trials": len(result["trials"]), "usage": result["usage"], "selected_trial": selected,
            "selected_parameters": record["parameters"] if record else None,
            "initial_loss": result["trials"][0]["fit"]["loss"], "selected_loss": record["fit"]["loss"] if record else None,
            "replay": result["replay"], "budget": get_budget(copied), "copied_bundle_verified": True}
    old_engines = {}
    prefix = "biomedical_research/virtual_cohort_system/"
    tracked = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASE, "--", prefix + "cohort_harness"], cwd=EXPORT, text=True).splitlines()
    for name in tracked:
        if name.endswith(".py"):
            original = subprocess.check_output(["git", "show", BASE + ":" + name], cwd=EXPORT)
            path = P / name.removeprefix(prefix)
            assert path.read_bytes() == original, "Historical engine changed: " + name
            old_engines[name.removeprefix(prefix)] = sha256(path)
    preserved = {}
    for report in ("source_location_transfer_2026-10-30", "source_context_engineering_2026-10-30"):
        folder = P / "reports" / report
        manifest = json.loads((folder / "file_manifest.json").read_text())
        entries = manifest.get("files", manifest)
        # Historical manifests use path->SHA-256 mappings.
        for relative, digest in entries.items():
            assert sha256(folder / relative) == digest
        preserved[report] = len(entries)
    write(DEST / "summary.json", {"scope": "invented_engineering_only", "biomedical_utility_tested": False,
                                 "cases": results})
    write(DEST / "historical_preservation.json", {"baseline_commit": BASE,
                                                "unchanged_engines": old_engines, "unchanged_report_files": preserved})
    shutil.copyfile(__file__, DEST / "curation_script.py")
    manifest = {f.relative_to(DEST).as_posix(): sha256(f) for f in sorted(DEST.rglob("*"))
                if f.is_file() and f != DEST / "file_manifest.json"}
    write(DEST / "file_manifest.json", {"files": manifest})
    print(json.dumps({"cases": {n: {k: v for k, v in r.items() if k in
          {"status", "trials", "initial_loss", "selected_loss", "selected_parameters", "usage"}} for n, r in results.items()},
          "historical_engine_count": len(old_engines), "preserved_reports": preserved,
          "manifest_files": len(manifest)}, indent=2))


if __name__ == "__main__":
    main()
