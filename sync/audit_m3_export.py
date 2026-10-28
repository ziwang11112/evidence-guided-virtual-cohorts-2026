"""Check the bounded M3 revision without rewriting historical M1/M2 evidence."""
from __future__ import annotations

import hashlib
import json


PREFIX = "biomedical_research/virtual_cohort_system/"


def digest(value):
    return hashlib.sha256(value).hexdigest()


def records_digest(records):
    """Canonical digest preserves all fields of the prior nonproject records."""
    return digest(json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def audit_m3_export(root, manifest, m2_receipt, m2_validation, receipt, findings, *, read_bytes=None):
    if receipt is None:
        return {"status": "not_exported"}

    def check(condition, path, rule):
        if not condition:
            findings.append({"file": path, "rule": rule})

    if read_bytes is None:
        read_bytes = lambda path: (root / path).read_bytes()

    def file_hash(path):
        try:
            return digest(read_bytes(path))
        except FileNotFoundError:
            return None

    receipt_path = "sync/M3_EXPORT_RECEIPT.json"
    prior = m2_receipt["curated_export_sha256"]
    current = {r["destination"]: r["export_sha256"] for r in manifest["files"]
               if r["destination"].startswith(PREFIX)}
    revisions = {path: {"historical_sha256": old, "current_sha256": current.get(path)}
                 for path, old in prior.items() if current.get(path) != old}
    added = {path: value for path, value in current.items() if path not in prior}
    check(set(prior) <= set(current), receipt_path, "historical_project_file_removed")
    check(receipt["revised_project_files"] == revisions, receipt_path, "project_revision_chain_mismatch")
    check(receipt["added_project_files"] == added, receipt_path, "m3_added_scope_mismatch")
    check(receipt["curated_export_sha256"] == current, receipt_path, "m3_curated_scope_mismatch")
    check(receipt["historical_m2_export_receipt_sha256"] == file_hash("sync/M2_EXPORT_RECEIPT.json"),
          receipt_path, "historical_m2_receipt_changed")
    for path, expected in receipt["historical_file_sha256"].items():
        check(file_hash(path) == expected, path, "historical_milestone_file_changed")
    required_historical = {PREFIX + path for path in (
        "MILESTONE_1_REPORT.md", "milestone_validation.json",
        "MILESTONE_2_PROGRESS.md", "m2_validation.json")}
    required_historical |= {"sync/TEST_RESULTS.json", "sync/M2_EXPORT_RECEIPT.json", "docs/M2_EXPORT.md"}
    check(set(receipt["historical_file_sha256"]) == required_historical,
          receipt_path, "historical_milestone_scope_mismatch")
    nonproject = [r for r in manifest["files"] if not r["destination"].startswith(PREFIX)]
    check(len(nonproject) == receipt["historical_nonproject_records_preserved"] == 838,
          receipt_path, "historical_nonproject_count_mismatch")
    check(records_digest(nonproject) == receipt["historical_nonproject_records_sha256"],
          receipt_path, "historical_nonproject_records_changed")
    expected_code_revisions = {
        path: {"historical_sha256": old, "current_sha256": current.get(PREFIX + path)}
        for path, old in m2_validation["code_sha256"].items()
        if current.get(PREFIX + path) != old}
    check(receipt["historical_m2_code_revisions"] == expected_code_revisions,
          receipt_path, "historical_m2_code_revision_mismatch")
    validation = json.loads(read_bytes(PREFIX + "m3_validation.json"))
    hashes = validation["code_sha256"]
    check(bool(hashes), PREFIX + "m3_validation.json", "m3_code_hashes_missing")
    for path, expected in hashes.items():
        check(current.get(PREFIX + path) == expected == file_hash(PREFIX + path),
              PREFIX + path, "m3_current_code_hash_mismatch")
    curated = PREFIX + "reports/source_feedback_2026-10-28/"
    curated_hashes = json.loads(read_bytes(curated + "curated_file_hashes.json"))
    audited_hashes = json.loads(read_bytes(curated + "curated_file_hashes_at_audit.json"))
    check(set(path.removeprefix(curated) for path in current if path.startswith(curated)) ==
          set(curated_hashes) | {"curated_file_hashes.json"}, receipt_path, "m3_curated_manifest_scope_mismatch")
    for path, expected in curated_hashes.items():
        check(file_hash(curated + path) == expected, curated + path, "m3_curated_file_hash_mismatch")
    for path, expected in audited_hashes.items():
        check(curated_hashes.get(path) == expected, curated + path, "m3_scientific_file_changed_after_audit")
    for field, path in {
        "report_sha256": PREFIX + "MILESTONE_3_RESULTS.md",
        "curated_file_manifest_sha256": curated + "curated_file_hashes.json",
        "postrun_audit_sha256": curated + "POSTRUN_AUDIT.md",
    }.items():
        check(validation[field] == file_hash(path), path, "m3_validation_artifact_hash_mismatch")
    for path in current:
        parts = path.removeprefix(PREFIX).split("/")
        check(not set(parts) & {"work", ".pytest_runs", "__pycache__", ".pytest_cache", "runtime", "runtimes"},
              path, "m3_forbidden_directory")
    check(receipt["experiments_or_tests_rerun"] is False and
          receipt["participant_or_generated_output_rows_exported"] is False,
          receipt_path, "m3_export_boundary_mismatch")
    return {
        "project_source_files": len(current), "project_files_added": len(added),
        "project_files_revised": len(revisions), "current_code_hashes_verified": len(hashes),
        "curated_file_hashes_verified": len(curated_hashes),
        "scientific_files_unchanged_since_postrun_audit": len(audited_hashes),
        "historical_milestone_files_preserved": len(required_historical),
        "historical_nonproject_records_preserved": len(nonproject),
        "experiments_or_tests_rerun": False,
    }
