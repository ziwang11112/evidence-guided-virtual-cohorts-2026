"""Verify a bounded M5 case export while preserving M1-M4 evidence."""
from __future__ import annotations

import json
import subprocess

from audit_m3_export import PREFIX, digest, records_digest
from audit_m4_export import audit_m4_export


M4_COMMIT = "efd8d43e9fd941197af44239acda19d8f26e2670"
CURATED = PREFIX + "reports/structure_robustness_2026-10-28/"
RECEIPT = "sync/M5_EXPORT_RECEIPT.json"
HISTORICAL_LOCAL = {
    "sync/TEST_RESULTS.json", "sync/M2_EXPORT_RECEIPT.json", "docs/M2_EXPORT.md",
    "sync/M3_EXPORT_RECEIPT.json", "docs/M3_EXPORT.md",
    "sync/M4_EXPORT_RECEIPT.json", "docs/M4_EXPORT.md",
}


def historical_bytes(root, path):
    result = subprocess.run(
        ["git", "cat-file", "blob", M4_COMMIT + ":" + path], cwd=root,
        capture_output=True, check=True,
    )
    return result.stdout


def audit_m5_export(root, manifest, m2_receipt, m2_validation, m3_receipt, m4_receipt,
                    receipt, findings):
    if receipt is None:
        return {"status": "not_exported"}

    def check(condition, path, rule):
        if not condition:
            findings.append({"file": path, "rule": rule})

    def file_hash(path):
        full = root / path
        return digest(full.read_bytes()) if full.is_file() else None

    baseline_bytes = historical_bytes(root, "sync/EXPORT_MANIFEST.json")
    baseline = json.loads(baseline_bytes)
    baseline_receipt_bytes = historical_bytes(root, "sync/M4_EXPORT_RECEIPT.json")
    baseline_receipt = json.loads(baseline_receipt_bytes)
    check(receipt["base_commit"] == M4_COMMIT, RECEIPT, "m5_wrong_historical_commit")
    check(receipt["previous_export_manifest_sha256"] == digest(baseline_bytes),
          RECEIPT, "m5_prior_manifest_binding_mismatch")
    check(receipt["historical_m4_export_receipt_sha256"] == digest(baseline_receipt_bytes) ==
          file_hash("sync/M4_EXPORT_RECEIPT.json"), RECEIPT, "historical_m4_receipt_changed")
    check(m4_receipt == baseline_receipt, RECEIPT, "historical_m4_receipt_content_changed")

    prior = {r["destination"]: r["export_sha256"] for r in baseline["files"]
             if r["destination"].startswith(PREFIX)}
    current = {r["destination"]: r["export_sha256"] for r in manifest["files"]
               if r["destination"].startswith(PREFIX)}
    revisions = {path: {"historical_sha256": old, "current_sha256": current.get(path)}
                 for path, old in prior.items() if current.get(path) != old}
    added = {path: value for path, value in current.items() if path not in prior}
    check(set(prior) <= set(current), RECEIPT, "historical_project_file_removed")
    check(set(revisions) <= {PREFIX + "README.md"}, RECEIPT,
          "m5_changed_historical_code_or_experiment")
    check(all(path.startswith(CURATED) or path in {
        PREFIX + "MILESTONE_5_RESULTS.md", PREFIX + "m5_validation.json"} for path in added),
        RECEIPT, "m5_added_file_outside_case_scope")
    check(receipt["revised_project_files"] == revisions, RECEIPT, "m5_revision_chain_mismatch")
    check(receipt["added_project_files"] == added, RECEIPT, "m5_added_scope_mismatch")
    check(receipt["curated_export_sha256"] == current, RECEIPT, "m5_curated_scope_mismatch")

    historical = {path: old for path, old in prior.items() if path not in revisions}
    historical.update({path: digest(historical_bytes(root, path)) for path in HISTORICAL_LOCAL})
    check(receipt["historical_file_sha256"] == historical, RECEIPT, "m5_historical_scope_mismatch")
    for path, expected in historical.items():
        check(file_hash(path) == expected, path, "historical_export_file_changed")
    prior_nonproject = [r for r in baseline["files"] if not r["destination"].startswith(PREFIX)]
    nonproject = [r for r in manifest["files"] if not r["destination"].startswith(PREFIX)]
    check(nonproject == prior_nonproject and len(nonproject) ==
          receipt["historical_nonproject_records_preserved"] == 838,
          RECEIPT, "historical_nonproject_records_changed")
    check(records_digest(nonproject) == receipt["historical_nonproject_records_sha256"],
          RECEIPT, "historical_nonproject_digest_mismatch")
    for milestone in ("m2", "m3"):
        field = "historical_" + milestone + "_code_revisions"
        check(receipt[field] == baseline_receipt[field], RECEIPT,
              "m5_changed_historical_code_revision_map")

    validation_path = PREFIX + "m5_validation.json"
    validation = json.loads((root / validation_path).read_bytes())
    check(validation["schema_version"] == 1 and validation["milestone"] == "M5",
          validation_path, "m5_validation_identity_mismatch")
    hashes = validation["code_sha256"]
    check(bool(hashes), validation_path, "m5_code_hashes_missing")
    for path, expected in hashes.items():
        check(current.get(PREFIX + path) == expected == file_hash(PREFIX + path),
              PREFIX + path, "m5_current_code_hash_mismatch")
    curated_hashes = json.loads((root / CURATED / "file_manifest.json").read_bytes())
    check(set(path.removeprefix(CURATED) for path in current if path.startswith(CURATED)) ==
          set(curated_hashes) | {"file_manifest.json"}, RECEIPT, "m5_curated_manifest_scope_mismatch")
    for path, expected in curated_hashes.items():
        check(file_hash(CURATED + path) == expected, CURATED + path, "m5_curated_file_hash_mismatch")
    provenance = json.loads((root / CURATED / "curation_provenance.json").read_bytes())["records"]
    check(len({record["path"] for record in provenance}) == len(provenance) and
          {record["path"] for record in provenance} ==
          set(curated_hashes) - {"README.md", "curation_provenance.json"},
          RECEIPT, "m5_curation_provenance_scope_mismatch")
    normalized = {}
    for record in provenance:
        check(curated_hashes.get(record["path"]) == record["curated_sha256"],
              CURATED + record["path"], "m5_curation_provenance_hash_mismatch")
        check((record["original_sha256"] != record["curated_sha256"]) ==
              (record["path_replacements"] > 0), CURATED + record["path"],
              "m5_curation_normalization_disclosure_mismatch")
        if record["path_replacements"]:
            normalized[record["path"]] = record
    check({path: record["path_replacements"] for path, record in normalized.items()} == {
        "curate_results.py": 3, "evaluation/release_receipt.json": 1,
        "evaluation_commitment.json": 26, "methods/fresh_overlap_inventory.json": 24,
    }, RECEIPT, "m5_unexpected_curated_path_normalizations")
    check(receipt["curated_path_normalizations"] == normalized, RECEIPT,
          "m5_curation_normalization_receipt_mismatch")
    audited_hashes = {}
    if CURATED + "curated_file_hashes_at_audit.json" in current:
        audited_hashes = json.loads((root / CURATED / "curated_file_hashes_at_audit.json").read_bytes())
        for path, expected in audited_hashes.items():
            check(curated_hashes.get(path) == expected, CURATED + path,
                  "m5_scientific_file_changed_after_audit")
    for field, path in {
        "report_sha256": PREFIX + "MILESTONE_5_RESULTS.md",
        "curated_file_manifest_sha256": CURATED + "file_manifest.json",
        "postrun_audit_sha256": CURATED + "POSTRUN_AUDIT.md",
    }.items():
        check(validation[field] == file_hash(path), path, "m5_validation_artifact_hash_mismatch")
    for path in current:
        parts = path.removeprefix(PREFIX).split("/")
        check(not set(parts) & {"work", ".pytest_runs", "__pycache__", ".pytest_cache",
                               "runtime", "runtimes", "raw", "downloads"},
              path, "m5_forbidden_directory")
    check(receipt["experiments_or_tests_rerun"] is False and
          receipt["participant_or_generated_output_rows_exported"] is False,
          RECEIPT, "m5_export_boundary_mismatch")

    historical_audit = audit_m4_export(
        root, baseline, m2_receipt, m2_validation, m3_receipt, baseline_receipt, findings,
        read_bytes=lambda path: historical_bytes(root, path),
    )
    historical_audit["binding"] = "historical_git_snapshot"
    historical_audit["commit"] = M4_COMMIT
    return {
        "project_source_files": len(current), "project_files_added": len(added),
        "project_files_revised": len(revisions), "current_code_hashes_verified": len(hashes),
        "curated_file_hashes_verified": len(curated_hashes),
        "curation_provenance_records_verified": len(provenance),
        "curated_path_normalizations_verified": len(normalized),
        "scientific_files_unchanged_since_postrun_audit": len(audited_hashes),
        "historical_export_files_preserved": len(historical),
        "historical_nonproject_records_preserved": len(nonproject),
        "historical_m4_audit": historical_audit,
        "experiments_or_tests_rerun": False,
    }
