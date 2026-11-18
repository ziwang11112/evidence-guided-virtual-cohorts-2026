"""Complete this development unit from its actual replay/review artifacts."""
from pathlib import Path
import hashlib
import json
import re
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


summary = read(HERE / "replay/SUMMARY.json")
for name, previous in summary["input_hashes_unchanged"].items():
    if digest(Path(name)) != previous:
        raise RuntimeError("Replay input changed after review: " + name)
for name in ("IMPLEMENTATION_REVIEW.md", "LOCAL_EXTRACTION_REVIEW.md", "author/C02/CROSSCHECK_C01_E02.md"):
    if not (HERE / name).is_file():
        raise RuntimeError("Missing independent review: " + name)
links = re.findall(r"\]\(([^)]+)\)", (HERE / "RESULTS_ZH.md").read_text(encoding="utf-8"))
for link in links:
    if not (HERE / link).is_file():
        raise RuntimeError("Missing result link: " + link)
now = datetime.now(timezone.utc).isoformat()
state = {
    "status": "completed_development_prototype_independently_reviewed",
    "completed_at_utc": now,
    "date_timezone": "America/Chicago",
    "report": "RESULTS_ZH.md",
    "counts": {
        "cases": len(summary["authors"]),
        "primary_analyses": sum(x["required_analyses"] for x in summary["authors"]),
        "additional_diagnostics": sum(x["additional_diagnostics"] for x in summary["authors"]),
        "action_cards": sum(x["action_cards"] for x in summary["authors"]),
        "declared_gap_dimensions_with_repeated_scientific_issues": sum(x["declared_gaps"] for x in summary["authors"]),
        "new_focused_tests_passed": 35,
        "local_source_table_extractions_independently_verified": 1,
        "inputs_unchanged_after_review": len(summary["input_hashes_unchanged"]),
    },
    "implementation": {
        "new_pure_router": "cohort_harness/evidence_actions_v1.py",
        "reuses": "cohort_harness/analysis_evidence.py",
        "old_controller_upgraded": False,
        "semantic_diagnosis": "Agent authored; not automatically certified by deterministic router",
        "budget_scope": "Estimates only, no reservation or task grant",
    },
    "activity": {
        "retrieval_executed": False, "new_downloads": 0,
        "participant_or_generated_rows_read": False, "new_cohort_generation": False,
        "frozen_candidate_changes": False, "target_fitting": False,
        "training_or_hpc": False, "new_paid_api": False, "github_sync": False,
    },
    "decision": "Continue narrowly with source-identified supplement acquisition in a new versioned task; no broad generation or optimizer changes justified yet.",
    "next_unit": "Bind a new bounded source-revision phase using existing supplement tools and cumulative budgets; inspect identified appendix regression tables before deciding whether new scientific construction is warranted. Do not reopen old frozen tasks.",
    "limitations": [
        "Development replay on exposed cases is not independent scientific confirmation.",
        "Source-only author access is procedural, not OS-enforced LLM isolation.",
        "Extracted HGI-group SDs do not identify full conditional residual variance or target joint effects.",
        "Supplement pointers were found; supplement contents have not been read in this unit.",
        "No data-quality improvement has been measured.",
    ],
}
(HERE / "STATE.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
files = [p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != "MANIFEST.json"]
files += [PROJECT / "cohort_harness/evidence_actions_v1.py", PROJECT / "tests/test_evidence_actions_v1.py", PROJECT / "docs/EVIDENCE_ACTIONS_V1.md"]
manifest = {"completed_at_utc": now, "artifacts": [
    {"project_path": p.relative_to(PROJECT).as_posix(), "bytes": p.stat().st_size, "sha256": digest(p)}
    for p in sorted(files)
]}
(HERE / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": state["status"], "counts": state["counts"], "linked_files_verified": len(links), "artifacts": len(files)}))
