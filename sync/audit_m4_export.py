"""Verify M4 current bindings and preserve M3 evidence at its original Git commit."""
from __future__ import annotations

import json
import subprocess

from audit_m3_export import PREFIX, audit_m3_export, digest, records_digest


M3_COMMIT = "495dd827c3eca4847fbeaf3a1a7740a5d85bfef0"
CURATED = PREFIX + "reports/source_portfolio_2026-10-28/"
RECEIPT = "sync/M4_EXPORT_RECEIPT.json"
HISTORICAL_LOCAL = {
    "sync/TEST_RESULTS.json", "sync/M2_EXPORT_RECEIPT.json", "docs/M2_EXPORT.md",
    "sync/M3_EXPORT_RECEIPT.json", "docs/M3_EXPORT.md",
}


def historical_bytes(root, path):
    """Use a fixed full commit ID; no mutable ref can redefine the M3 evidence."""
    result = subprocess.run(
        ["git", "show", M3_COMMIT + ":" + path], cwd=root,
        capture_output=True, check=True,
    )
    return result.stdout


def audit_m4_export(root, manifest, m2_receipt, m2_validation, m3_receipt, receipt, findings, *, read_bytes=None):
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

    baseline_bytes = historical_bytes(root, "sync/EXPORT_MANIFEST.json")
    baseline = json.loads(baseline_bytes)
    baseline_receipt_bytes = historical_bytes(root, "sync/M3_EXPORT_RECEIPT.json")
    baseline_receipt = json.loads(baseline_receipt_bytes)
    check(receipt["base_commit"] == M3_COMMIT, RECEIPT, "m4_wrong_historical_commit")
    check(receipt["previous_export_manifest_sha256"] == digest(baseline_bytes),
          RECEIPT, "m4_prior_manifest_binding_mismatch")
    check(receipt["historical_m3_export_receipt_sha256"] == digest(baseline_receipt_bytes) ==
          file_hash("sync/M3_EXPORT_RECEIPT.json"), RECEIPT, "historical_m3_receipt_changed")
    check(m3_receipt == baseline_receipt, RECEIPT, "historical_m3_receipt_content_changed")

    prior = {r["destination"]: r["export_sha256"] for r in baseline["files"]
             if r["destination"].startswith(PREFIX)}
    current = {r["destination"]: r["export_sha256"] for r in manifest["files"]
               if r["destination"].startswith(PREFIX)}
    revisions = {path: {"historical_sha256": old, "current_sha256": current.get(path)}
                 for path, old in prior.items() if current.get(path) != old}
    added = {path: value for path, value in current.items() if path not in prior}
    check(set(prior) <= set(current), RECEIPT, "historical_project_file_removed")
    check(receipt["revised_project_files"] == revisions, RECEIPT, "m4_revision_chain_mismatch")
    check(receipt["added_project_files"] == added, RECEIPT, "m4_added_scope_mismatch")
    check(receipt["curated_export_sha256"] == current, RECEIPT, "m4_curated_scope_mismatch")
    # Earlier experiment evidence and milestone claims are immutable. Only current
    # implementation, tests, skills and documentation may have recorded revisions.
    for path in revisions:
        relative = path.removeprefix(PREFIX)
        permitted = relative == "README.md" or relative.startswith((
            "cohort_harness/", "tests/", "skills/", "docs/", "examples/"))
        check(permitted, path, "historical_experiment_or_milestone_rewritten")

    historical = {path: old for path, old in prior.items() if path not in revisions}
    historical.update({path: digest(historical_bytes(root, path)) for path in HISTORICAL_LOCAL})
    check(receipt["historical_file_sha256"] == historical, RECEIPT, "m4_historical_scope_mismatch")
    for path, expected in historical.items():
        check(file_hash(path) == expected, path, "historical_export_file_changed")
    prior_nonproject = [r for r in baseline["files"] if not r["destination"].startswith(PREFIX)]
    nonproject = [r for r in manifest["files"] if not r["destination"].startswith(PREFIX)]
    check(nonproject == prior_nonproject and len(nonproject) ==
          receipt["historical_nonproject_records_preserved"] == 838,
          RECEIPT, "historical_nonproject_records_changed")
    check(records_digest(nonproject) == receipt["historical_nonproject_records_sha256"],
          RECEIPT, "historical_nonproject_digest_mismatch")

    for milestone, validation in (
            ("m2", m2_validation),
            ("m3", json.loads(historical_bytes(root, PREFIX + "m3_validation.json")))):
        expected_revisions = {
            path: {"historical_sha256": old, "current_sha256": current.get(PREFIX + path)}
            for path, old in validation["code_sha256"].items()
            if current.get(PREFIX + path) != old}
        check(receipt["historical_" + milestone + "_code_revisions"] == expected_revisions,
              RECEIPT, "historical_" + milestone + "_code_revision_mismatch")

    validation_path = PREFIX + "m4_validation.json"
    validation = json.loads(read_bytes(validation_path))
    hashes = validation["code_sha256"]
    check(bool(hashes), validation_path, "m4_code_hashes_missing")
    for path, expected in hashes.items():
        check(current.get(PREFIX + path) == expected == file_hash(PREFIX + path),
              PREFIX + path, "m4_current_code_hash_mismatch")
    curated_hashes = json.loads(read_bytes(CURATED + "curated_file_hashes.json"))
    check(set(path.removeprefix(CURATED) for path in current if path.startswith(CURATED)) ==
          set(curated_hashes) | {"curated_file_hashes.json"}, RECEIPT, "m4_curated_manifest_scope_mismatch")
    for path, expected in curated_hashes.items():
        check(file_hash(CURATED + path) == expected, CURATED + path, "m4_curated_file_hash_mismatch")
    for field, path in {
        "report_sha256": PREFIX + "MILESTONE_4_RESULTS.md",
        "curated_file_manifest_sha256": CURATED + "curated_file_hashes.json",
    }.items():
        check(validation[field] == file_hash(path), path, "m4_validation_artifact_hash_mismatch")
    if "postrun_audit_sha256" in validation:
        check(validation["postrun_audit_sha256"] == file_hash(CURATED + "POSTRUN_AUDIT.md"),
              CURATED + "POSTRUN_AUDIT.md", "m4_validation_artifact_hash_mismatch")
    for path in current:
        parts = path.removeprefix(PREFIX).split("/")
        check(not set(parts) & {"work", ".pytest_runs", "__pycache__", ".pytest_cache",
                               "runtime", "runtimes", "raw", "downloads"},
              path, "m4_forbidden_directory")
    check(receipt["experiments_or_tests_rerun"] is False and
          receipt["participant_or_generated_output_rows_exported"] is False,
          RECEIPT, "m4_export_boundary_mismatch")

    historical_audit = audit_m3_export(
        root, baseline, m2_receipt, m2_validation, baseline_receipt, findings,
        read_bytes=lambda path: historical_bytes(root, path),
    )
    historical_audit["binding"] = "historical_git_snapshot"
    historical_audit["commit"] = M3_COMMIT
    return {
        "project_source_files": len(current), "project_files_added": len(added),
        "project_files_revised": len(revisions), "current_code_hashes_verified": len(hashes),
        "curated_file_hashes_verified": len(curated_hashes),
        "historical_export_files_preserved": len(historical),
        "historical_nonproject_records_preserved": len(nonproject),
        "historical_m3_audit": historical_audit,
        "experiments_or_tests_rerun": False,
    }
