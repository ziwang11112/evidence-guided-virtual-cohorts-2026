"""Verify bounded M6 identifiability evidence and preserve M1-M5 exports."""
from __future__ import annotations

from functools import lru_cache
import csv
import itertools
import json
import subprocess

from audit_m3_export import PREFIX, digest, records_digest
from audit_m5_export import audit_m5_export


M5_COMMIT = "ecdef87b537e066872552f8b29354ab5b17c0e0b"
CURATED = PREFIX + "reports/source_identifiability_2026-10-29/"
RECEIPT = "sync/M6_EXPORT_RECEIPT.json"
HISTORICAL_LOCAL = {
    "sync/TEST_RESULTS.json", "sync/M2_EXPORT_RECEIPT.json", "docs/M2_EXPORT.md",
    "sync/M3_EXPORT_RECEIPT.json", "docs/M3_EXPORT.md",
    "sync/M4_EXPORT_RECEIPT.json", "docs/M4_EXPORT.md",
    "sync/M5_EXPORT_RECEIPT.json", "docs/M5_EXPORT.md",
}


@lru_cache(maxsize=None)
def historical_bytes(root, path):
    result = subprocess.run(
        ["git", "cat-file", "blob", M5_COMMIT + ":" + path], cwd=root,
        capture_output=True, check=True,
    )
    return result.stdout


def audit_m6_export(root, manifest, m2_receipt, m2_validation, m3_receipt, m4_receipt,
                    m5_receipt, receipt, findings):
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
    baseline_receipt_bytes = historical_bytes(root, "sync/M5_EXPORT_RECEIPT.json")
    baseline_receipt = json.loads(baseline_receipt_bytes)
    check(receipt["base_commit"] == M5_COMMIT, RECEIPT, "m6_wrong_historical_commit")
    check(receipt["previous_export_manifest_sha256"] == digest(baseline_bytes),
          RECEIPT, "m6_prior_manifest_binding_mismatch")
    check(receipt["historical_m5_export_receipt_sha256"] == digest(baseline_receipt_bytes) ==
          file_hash("sync/M5_EXPORT_RECEIPT.json"), RECEIPT, "historical_m5_receipt_changed")
    check(m5_receipt == baseline_receipt, RECEIPT, "historical_m5_receipt_content_changed")

    prior = {r["destination"]: r["export_sha256"] for r in baseline["files"]
             if r["destination"].startswith(PREFIX)}
    current = {r["destination"]: r["export_sha256"] for r in manifest["files"]
               if r["destination"].startswith(PREFIX)}
    revisions = {path: {"historical_sha256": old, "current_sha256": current.get(path)}
                 for path, old in prior.items() if current.get(path) != old}
    added = {path: value for path, value in current.items() if path not in prior}
    check(set(prior) <= set(current), RECEIPT, "historical_project_file_removed")
    check(set(revisions) <= {PREFIX + "README.md"}, RECEIPT,
          "m6_changed_historical_code_or_experiment")
    check(all(path.startswith(CURATED) or path in {
        PREFIX + "MILESTONE_6_RESULTS.md", PREFIX + "m6_validation.json"} for path in added),
        RECEIPT, "m6_added_file_outside_case_scope")
    check(receipt["revised_project_files"] == revisions, RECEIPT, "m6_revision_chain_mismatch")
    check(receipt["added_project_files"] == added, RECEIPT, "m6_added_scope_mismatch")
    check(receipt["curated_export_sha256"] == current, RECEIPT, "m6_curated_scope_mismatch")

    historical = {path: old for path, old in prior.items() if path not in revisions}
    historical.update({path: digest(historical_bytes(root, path)) for path in HISTORICAL_LOCAL})
    check(receipt["historical_file_sha256"] == historical, RECEIPT, "m6_historical_scope_mismatch")
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
              "m6_changed_historical_code_revision_map")

    validation_path = PREFIX + "m6_validation.json"
    validation = json.loads((root / validation_path).read_bytes())
    check(validation["schema_version"] == 1 and validation["milestone"] == "M6",
          validation_path, "m6_validation_identity_mismatch")
    hashes = validation["code_sha256"]
    check(bool(hashes), validation_path, "m6_code_hashes_missing")
    for path, expected in hashes.items():
        check(current.get(PREFIX + path) == expected == file_hash(PREFIX + path),
              PREFIX + path, "m6_current_code_hash_mismatch")
    curated_hashes = json.loads((root / CURATED / "file_manifest.json").read_bytes())
    check(set(path.removeprefix(CURATED) for path in current if path.startswith(CURATED)) ==
          set(curated_hashes) | {"file_manifest.json"}, RECEIPT, "m6_curated_manifest_scope_mismatch")
    for path, expected in curated_hashes.items():
        check(file_hash(CURATED + path) == expected, CURATED + path, "m6_curated_file_hash_mismatch")
    provenance = json.loads((root / CURATED / "curation_provenance.json").read_bytes())["records"]
    original_hashes = {record["path"]: record["original_sha256"] for record in provenance}
    check(len(original_hashes) == len(provenance) and set(original_hashes) ==
          set(curated_hashes) - {"README.md", "curation_provenance.json"},
          RECEIPT, "m6_curation_provenance_scope_mismatch")
    normalized = {}
    for record in provenance:
        check(curated_hashes.get(record["path"]) == record["curated_sha256"],
              CURATED + record["path"], "m6_curation_provenance_hash_mismatch")
        check((record["original_sha256"] != record["curated_sha256"]) ==
              (record["path_replacements"] > 0), CURATED + record["path"],
              "m6_curation_normalization_disclosure_mismatch")
        if record["path_replacements"]:
            normalized[record["path"]] = record
    check({path: record["path_replacements"] for path, record in normalized.items()} == {
        "analysis/frozen_gate.json": 1, "curate_results.py": 4,
        "evaluation_commitment.json": 81, "results/aggregate_report.json": 81,
        "source_analysis/aggregate_report.json": 72, "source_commitment.json": 72,
    }, RECEIPT, "m6_unexpected_curated_path_normalizations")
    check(receipt["curated_path_normalizations"] == normalized, RECEIPT,
          "m6_curation_normalization_receipt_mismatch")
    for field, path in {
        "protocol_commitment_sha256": "protocol_commitment.json",
        "source_commitment_sha256": "source_commitment.json",
        "evaluation_commitment_sha256": "evaluation_commitment.json",
        "aggregate_result_sha256": "results/aggregate_report.json",
    }.items():
        check(validation["execution"][field] == original_hashes.get(path),
              CURATED + path, "m6_original_execution_hash_mismatch")
    grid_path = CURATED + "results/probe_grid.csv"
    with (root / grid_path).open(encoding="utf-8-sig", newline="") as stream:
        grid = list(csv.DictReader(stream))
    grid_keys = [(row["label"], int(row["seed"]), int(row["sex"]),
                  int(row["age"]), float(row["bmi"])) for row in grid]
    expected_grid = set(itertools.product(
        ("zero", "minus", "plus"), (78201, 78202, 78203), (1, 2), range(20, 80), range(18, 41)))
    check(len(grid) == len(set(grid_keys)) == 24840 and set(grid_keys) == expected_grid and
          all(int(row["n"]) == 10 for row in grid), grid_path,
          "m6_synthetic_grid_cell_aggregate_scope_mismatch")
    for field, path in {
        "report_sha256": PREFIX + "MILESTONE_6_RESULTS.md",
        "curated_file_manifest_sha256": CURATED + "file_manifest.json",
        "postrun_audit_sha256": CURATED + "POSTRUN_AUDIT.md",
    }.items():
        check(validation[field] == file_hash(path), path, "m6_validation_artifact_hash_mismatch")
    for path in current:
        parts = path.removeprefix(PREFIX).split("/")
        check(not set(parts) & {"work", ".pytest_runs", "__pycache__", ".pytest_cache",
                               "runtime", "runtimes", "raw", "downloads"},
              path, "m6_forbidden_directory")
    check(receipt["experiments_or_tests_rerun"] is False and
          receipt["participant_or_generated_output_rows_exported"] is False and
          receipt["new_target_evaluation_in_source_milestone"] is False and
          validation["interpretation"]["new_real_target_evaluation"] is False,
          RECEIPT, "m6_export_boundary_mismatch")

    historical_audit = audit_m5_export(
        root, baseline, m2_receipt, m2_validation, m3_receipt, m4_receipt,
        baseline_receipt, findings, read_bytes=lambda path: historical_bytes(root, path),
    )
    historical_audit["binding"] = "historical_git_snapshot"
    historical_audit["commit"] = M5_COMMIT
    return {
        "project_source_files": len(current), "project_files_added": len(added),
        "project_files_revised": len(revisions), "current_code_hashes_verified": len(hashes),
        "curated_file_hashes_verified": len(curated_hashes),
        "curation_provenance_records_verified": len(provenance),
        "curated_path_normalizations_verified": len(normalized),
        "synthetic_grid_cell_aggregate_rows_verified": len(grid),
        "synthetic_replicates_per_grid_cell": 10,
        "historical_export_files_preserved": len(historical),
        "historical_nonproject_records_preserved": len(nonproject),
        "historical_m5_audit": historical_audit,
        "experiments_or_tests_rerun": False,
    }
