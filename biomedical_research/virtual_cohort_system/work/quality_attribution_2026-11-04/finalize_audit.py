"""Record completion and verify recorded aggregate/specification input hashes only."""
from pathlib import Path
import hashlib
import json
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent


def read_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


expected = {}


def add(path, digest):
    path = str(Path(path).resolve())
    assert expected.get(path, digest) == digest, f"Inconsistent recorded hash: {path}"
    expected[path] = digest


for path, item in read_json("AGGREGATE_DIAGNOSIS.json")["inputs"].items():
    add(path, item["sha256"])
for item in read_json("ANALYTIC_C01_C02.json")["inputs"]:
    add(item["path"], item["sha256"])
for item in read_json("ANALYTIC_C01_C02_RUN_METADATA.json")["artifacts"]:
    add(item["path"], item["sha256"])
for item in read_json("FEEDBACK_AUDIT_METADATA.json")["authors"]:
    add(item["combined_feedback_path"], item["combined_feedback_sha256"])

checked = []
for name, digest in sorted(expected.items()):
    path = Path(name)
    actual = sha256(path)
    assert actual == digest, f"Recorded input/artifact changed: {name}"
    checked.append({"path": name, "sha256": actual, "bytes": path.stat().st_size})

report = (ROOT / "RESULTS_ZH.md").read_text(encoding="utf-8")
links = re.findall(r"\]\(([^)]+)\)", report)
local_links = [x for x in links if not x.startswith(("https://", "http://"))]
for link in local_links:
    assert (ROOT / link).is_file(), f"Broken local report link: {link}"

now = datetime.now(timezone.utc).isoformat()
state = {
    "status": "completed_diagnosis_no_new_generation",
    "completed_at_utc": now,
    "started_local_date": "2026-11-04",
    "completed_local_date": "2026-11-05",
    "scope": "Post-evaluation diagnosis of four frozen models across two existing cohort cases; not independent confirmation.",
    "root_report": "RESULTS_ZH.md",
    "independent_audits": ["MECHANISM_C01_C02.md", "EVIDENCE_E01_E02.md", "METHOD_AND_FEEDBACK_AUDIT.md", "NUMERICAL_REVIEW.md"],
    "evidence": {
        "frozen_models": ["C01", "C02", "E01", "E02"],
        "cached_original_papers_reread_by_source_audit": 6,
        "existing_aggregate_endpoint_rows": 366,
        "root_model_law_diagnostics": 9,
        "actual_feedback_approximate_comparisons": 29,
        "actual_feedback_unavailable_items": 39,
        "approximate_does_not_mean_passed": True,
        "diagnostic_figure_visually_checked": True,
        "local_report_links_verified": len(local_links)
    },
    "activity": {
        "new_scientific_generation": False,
        "candidate_execution": False,
        "participant_or_synthetic_rows_read": False,
        "new_downloads": False,
        "target_fitting": False,
        "frozen_experiment_mutation": False,
        "training_or_hpc": False,
        "new_paid_api": False,
        "github_sync": False
    },
    "finding": "Observed outputs largely realize declared model laws. Important limitations arise from unverified evidence-to-conditional-model transformations, source applicability and frozen acquisition policy; their causal contributions are not identified.",
    "decision": "Continue with targeted evidence-use and acquisition-policy improvement; no generic optimizer or larger generation batch justified by this audit alone.",
    "next_proposed_unit": "Use-to-evidence-gap action prototype on existing source packs without target-reference inputs or new generation. Treat reused cases as development, not confirmation.",
    "verified_recorded_files": checked
}
(ROOT / "STATE.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
manifest = {
    "recorded_at_utc": now,
    "scope": "Local original diagnostic deliverables; excludes this manifest to avoid recursive hashes.",
    "artifacts": [
        {"file": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)}
        for p in sorted(ROOT.iterdir()) if p.is_file() and p.name != "MANIFEST.json"
    ]
}
(ROOT / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": state["status"], "verified_recorded_files": len(checked), "report_links": len(local_links), "manifest_artifacts": len(manifest["artifacts"])}))
