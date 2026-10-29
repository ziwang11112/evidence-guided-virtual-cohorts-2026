"""Verify bounded M7 evidence-map work and preserve M1-M6 snapshots."""
from __future__ import annotations

from functools import lru_cache
import json
import subprocess

from audit_m3_export import PREFIX, digest, records_digest
from audit_m6_export import audit_m6_export


M6_COMMIT = "15787a0898562a7c7bebad7cbdcda124113af2f9"
CURATED = PREFIX + "reports/analysis_evidence_gap_2026-10-29/"
RECEIPT = "sync/M7_EXPORT_RECEIPT.json"
PERMITTED_REVISIONS = {
    PREFIX + "README.md", PREFIX + "cohort_harness/__main__.py",
    PREFIX + "cohort_harness/lifecycle.py",
}
PERMITTED_ADDITIONS = {
    PREFIX + "MILESTONE_7_RESULTS.md", PREFIX + "m7_validation.json",
    PREFIX + "cohort_harness/analysis_evidence.py", PREFIX + "tests/test_analysis_evidence.py",
    PREFIX + "docs/ANALYSIS_EVIDENCE.md",
}
HISTORICAL_LOCAL = {
    "sync/TEST_RESULTS.json", "sync/M2_EXPORT_RECEIPT.json", "docs/M2_EXPORT.md",
    "sync/M3_EXPORT_RECEIPT.json", "docs/M3_EXPORT.md",
    "sync/M4_EXPORT_RECEIPT.json", "docs/M4_EXPORT.md",
    "sync/M5_EXPORT_RECEIPT.json", "docs/M5_EXPORT.md",
    "sync/M6_EXPORT_RECEIPT.json", "docs/M6_EXPORT.md",
}


@lru_cache(maxsize=None)
def historical_bytes(root, path):
    result = subprocess.run(
        ["git", "cat-file", "blob", M6_COMMIT + ":" + path], cwd=root,
        capture_output=True, check=True,
    )
    return result.stdout


def audit_m7_export(root, manifest, m2_receipt, m2_validation, m3_receipt, m4_receipt,
                    m5_receipt, m6_receipt, receipt, findings):
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
    baseline_receipt_bytes = historical_bytes(root, "sync/M6_EXPORT_RECEIPT.json")
    baseline_receipt = json.loads(baseline_receipt_bytes)
    check(receipt["base_commit"] == M6_COMMIT, RECEIPT, "m7_wrong_historical_commit")
    check(receipt["previous_export_manifest_sha256"] == digest(baseline_bytes),
          RECEIPT, "m7_prior_manifest_binding_mismatch")
    check(receipt["historical_m6_export_receipt_sha256"] == digest(baseline_receipt_bytes) ==
          file_hash("sync/M6_EXPORT_RECEIPT.json"), RECEIPT, "historical_m6_receipt_changed")
    check(m6_receipt == baseline_receipt, RECEIPT, "historical_m6_receipt_content_changed")

    prior = {r["destination"]: r["export_sha256"] for r in baseline["files"]
             if r["destination"].startswith(PREFIX)}
    current = {r["destination"]: r["export_sha256"] for r in manifest["files"]
               if r["destination"].startswith(PREFIX)}
    revisions = {path: {"historical_sha256": old, "current_sha256": current.get(path)}
                 for path, old in prior.items() if current.get(path) != old}
    added = {path: value for path, value in current.items() if path not in prior}
    check(set(prior) <= set(current), RECEIPT, "historical_project_file_removed")
    check(set(revisions) <= PERMITTED_REVISIONS, RECEIPT, "m7_unpermitted_historical_revision")
    check(all(path.startswith(CURATED) or path in PERMITTED_ADDITIONS for path in added),
          RECEIPT, "m7_added_file_outside_scope")
    check(receipt["revised_project_files"] == revisions, RECEIPT, "m7_revision_chain_mismatch")
    check(receipt["added_project_files"] == added, RECEIPT, "m7_added_scope_mismatch")
    check(receipt["curated_export_sha256"] == current, RECEIPT, "m7_curated_scope_mismatch")

    historical = {path: old for path, old in prior.items() if path not in revisions}
    historical.update({path: digest(historical_bytes(root, path)) for path in HISTORICAL_LOCAL})
    check(receipt["historical_file_sha256"] == historical, RECEIPT, "m7_historical_scope_mismatch")
    for path, expected in historical.items():
        check(file_hash(path) == expected, path, "historical_export_file_changed")
    prior_nonproject = [r for r in baseline["files"] if not r["destination"].startswith(PREFIX)]
    nonproject = [r for r in manifest["files"] if not r["destination"].startswith(PREFIX)]
    check(nonproject == prior_nonproject and len(nonproject) ==
          receipt["historical_nonproject_records_preserved"] == 838,
          RECEIPT, "historical_nonproject_records_changed")
    check(records_digest(nonproject) == receipt["historical_nonproject_records_sha256"],
          RECEIPT, "historical_nonproject_digest_mismatch")
    for milestone in ("m2", "m3", "m4", "m5", "m6"):
        validation = json.loads(historical_bytes(root, PREFIX + milestone + "_validation.json"))
        expected_revisions = {
            path: {"historical_sha256": old, "current_sha256": current.get(PREFIX + path)}
            for path, old in validation["code_sha256"].items()
            if current.get(PREFIX + path) != old}
        check(receipt["historical_" + milestone + "_code_revisions"] == expected_revisions,
              RECEIPT, "m7_historical_" + milestone + "_code_revision_mismatch")

    validation_path = PREFIX + "m7_validation.json"
    validation = json.loads((root / validation_path).read_bytes())
    check(validation["schema_version"] == 1 and validation["milestone"] == "M7",
          validation_path, "m7_validation_identity_mismatch")
    hashes = validation["code_sha256"]
    check(bool(hashes), validation_path, "m7_code_hashes_missing")
    for path, expected in hashes.items():
        check(current.get(PREFIX + path) == expected == file_hash(PREFIX + path),
              PREFIX + path, "m7_current_code_hash_mismatch")
    curated_hashes = json.loads((root / CURATED / "file_manifest.json").read_bytes())
    check(set(path.removeprefix(CURATED) for path in current if path.startswith(CURATED)) ==
          set(curated_hashes) | {"file_manifest.json"}, RECEIPT, "m7_curated_manifest_scope_mismatch")
    for path, expected in curated_hashes.items():
        check(file_hash(CURATED + path) == expected, CURATED + path, "m7_curated_file_hash_mismatch")
    check(not set(curated_hashes) & {"controller.py", "release_guard.py", "protocol.json",
                                   "evaluation_commitment.json"}, RECEIPT,
          "m7_unexecuted_controller_or_release_draft_exported")
    provenance = json.loads((root / CURATED / "curation_provenance.json").read_bytes())["records"]
    original_hashes = {record["curated_relative"]: record["original_sha256"] for record in provenance}
    check(len(original_hashes) == len(provenance) and set(original_hashes) ==
          set(curated_hashes) - {"README.md", "curation_provenance.json", "curation_repair.json"},
          RECEIPT, "m7_curation_provenance_scope_mismatch")
    normalized = {}
    for record in provenance:
        path = record["curated_relative"]
        check(curated_hashes.get(path) == record["copied_sha256"],
              CURATED + path, "m7_curation_provenance_hash_mismatch")
        check((record["original_sha256"] != record["copied_sha256"]) ==
              (record["path_replacements"] > 0), CURATED + path,
              "m7_curation_normalization_disclosure_mismatch")
        check(not record["scientific_bytes_preserved"] or
              record["original_sha256"] == record["copied_sha256"], CURATED + path,
              "m7_preserved_scientific_bytes_changed")
        if record["path_replacements"]:
            normalized[path] = record
    check(set(normalized) == {
        "baseline_import.json", "curate_results.py", "review/FULL_HARNESS_TESTS.json",
        "review/RETENTION_AUDIT_CHECKS.json",
        "candidates/evidence_augmented/research_audit/candidate_cli_validation.json",
        "candidates/evidence_augmented/research_audit/candidate_cli_validation_wording_fix.json",
        "methods/novelty_audit.json",
    }, RECEIPT, "m7_unexpected_curated_path_normalizations")
    check(receipt["curated_path_normalizations"] == normalized, RECEIPT,
          "m7_curation_normalization_receipt_mismatch")
    repair = json.loads((root / CURATED / "curation_repair.json").read_bytes())
    check(validation["curation_repair_sha256"] == file_hash(CURATED + "curation_repair.json") and
          repair["frozen_candidate_and_custodian_originals_unchanged"] is True and
          repair["scientific_execution_or_target_analysis"] is False,
          RECEIPT, "m7_curation_repair_binding_mismatch")
    check({record["file"] for record in repair["changed_copies"]} == {
        "curate_results.py", "review/FULL_HARNESS_TESTS.json", "review/RETENTION_AUDIT_CHECKS.json",
        "candidates/evidence_augmented/research_audit/candidate_cli_validation.json",
        "candidates/evidence_augmented/research_audit/candidate_cli_validation_wording_fix.json",
    }, RECEIPT, "m7_curation_repair_scope_mismatch")
    for record in repair["changed_copies"]:
        check(file_hash(CURATED + record["file"]) == record["new_copied_sha256"],
              CURATED + record["file"], "m7_curation_repair_hash_mismatch")

    def read_curated(path):
        return json.loads((root / CURATED / path).read_bytes())

    retention = read_curated("retention_freeze.json")
    stage = read_curated("stage_decision.json")
    revision = read_curated("candidates/evidence_augmented/revision.json")
    freezes = {label: read_curated("candidates/" + label + "/freeze.json")
               for label in ("baseline", "evidence_augmented")}
    for label, freeze in freezes.items():
        candidate = "candidates/" + label + "/"
        check(file_hash(CURATED + candidate + "freeze.json") ==
              validation["retention"]["candidate_freezes"][label] ==
              retention["candidate_freezes"][label], CURATED + candidate + "freeze.json",
              "m7_candidate_freeze_hash_mismatch")
        for path, original in original_hashes.items():
            if path.startswith(candidate) and path != candidate + "freeze.json":
                check(freeze["commitments"].get(path) == original, CURATED + path,
                      "m7_candidate_original_commitment_mismatch")
    for name, field in (("generator.py", "generator_sha256"), ("model_spec.json", "model_spec_sha256")):
        values = [file_hash(CURATED + "candidates/" + label + "/" + name)
                  for label in ("baseline", "evidence_augmented")]
        check(values[0] == values[1] == retention[field] == validation["retention"][field],
              RECEIPT, "m7_scientific_retention_hash_mismatch")
    check(revision["kind"] == validation["retention"]["kind"] == "retain" and
          freezes["evidence_augmented"]["revision"] == revision and
          freezes["evidence_augmented"]["parent"]["sha256"] ==
          validation["retention"]["candidate_freezes"]["baseline"],
          RECEIPT, "m7_retention_parent_or_revision_mismatch")
    evidence = [read_curated("candidates/" + label + "/evidence.json")
                for label in ("baseline", "evidence_augmented")]
    check([len(value["sources"]) for value in evidence] == [2, 4] and
          [len(value["items"]) for value in evidence] == [71, 79] and
          evidence[1]["sources"][:2] == evidence[0]["sources"] and
          evidence[1]["items"][:71] == evidence[0]["items"], RECEIPT,
          "m7_evidence_addition_or_original_prefix_mismatch")
    for name in ("analysis_evidence.json", "decision.md", "evidence.json"):
        check(file_hash(CURATED + "candidates/baseline/" + name) !=
              file_hash(CURATED + "candidates/evidence_augmented/" + name),
              RECEIPT, "m7_expected_evidence_declaration_update_missing")
    check(all(len(read_curated("candidates/" + label + "/analysis_evidence.json")["analyses"]) == 3
              for label in freezes), RECEIPT, "m7_requested_analysis_count_mismatch")
    check(stage["authorization_target_evaluation"] is False and
          stage["generator_execution_authorized"] is False and
          retention["generator_executed"] is False and retention["target_evaluated"] is False and
          all(validation["execution"][key] == 0 for key in
              ("scientific_generator_runs", "source_replays", "target_analyses")) and
          validation["reserved_case"]["outcome_statistics_evaluated"] is False,
          RECEIPT, "m7_scientific_execution_boundary_mismatch")
    check(retention["stage_decision_sha256"] == original_hashes["stage_decision.json"] and
          validation["retention"]["retention_freeze_sha256"] == original_hashes["retention_freeze.json"] and
          retention["retention_audit_sha256"] == original_hashes["review/RETENTION_AUDIT.md"],
          RECEIPT, "m7_retention_decision_audit_binding_mismatch")
    tests = read_curated("review/FULL_HARNESS_TESTS.json")
    check(validation["tests"]["receipt_sha256"] == file_hash(CURATED + "review/FULL_HARNESS_TESTS.json") and
          tests["returncode"] == validation["tests"]["exit_code"] == 0,
          RECEIPT, "m7_test_receipt_binding_mismatch")
    for path, expected in tests["code_hashes"].items():
        check(file_hash(PREFIX + path) == expected == hashes.get(path), PREFIX + path,
              "m7_tested_code_hash_mismatch")
    retry_logs = ("research/supplement_retry_log.jsonl",
                  "candidates/evidence_augmented/research_audit/supplement_retry_log.jsonl")
    for path in retry_logs:
        rows = [json.loads(line) for line in (root / CURATED / path).read_text(encoding="utf-8-sig").splitlines() if line]
        check(len(rows) == 4 and all(isinstance(row, list) and len(row) in (3, 4) and
              isinstance(row[0], str) and row[0].startswith("https://") and
              (len(row) == 3 or isinstance(row[3], str) and len(row[3]) <= 128)
              for row in rows), CURATED + path, "m7_retrieval_response_log_scope_mismatch")
    check(file_hash(CURATED + retry_logs[0]) == file_hash(CURATED + retry_logs[1]),
          RECEIPT, "m7_retrieval_log_copy_mismatch")
    for field, path in {
        "report_sha256": PREFIX + "MILESTONE_7_RESULTS.md",
        "curated_file_manifest_sha256": CURATED + "file_manifest.json",
        "postrun_audit_sha256": CURATED + "review/RETENTION_AUDIT.md",
    }.items():
        check(validation[field] == file_hash(path), path, "m7_validation_artifact_hash_mismatch")
    for path in current:
        parts = path.removeprefix(PREFIX).split("/")
        check(not set(parts) & {"work", ".pytest_runs", "__pycache__", ".pytest_cache",
                               "runtime", "runtimes", "raw", "downloads", "cache", ".cache"}
              and not any(part.startswith("pytest-analysis-") for part in parts),
              path, "m7_forbidden_directory")
    check(receipt["experiments_or_tests_rerun"] is False and
          receipt["participant_or_generated_output_rows_exported"] is False and
          receipt["new_target_evaluation_in_source_milestone"] is False and
          receipt["generator_executions_in_source_milestone"] == 0,
          RECEIPT, "m7_export_boundary_mismatch")

    historical_audit = audit_m6_export(
        root, baseline, m2_receipt, m2_validation, m3_receipt, m4_receipt,
        m5_receipt, baseline_receipt, findings, read_bytes=lambda path: historical_bytes(root, path),
    )
    historical_audit["binding"] = "historical_git_snapshot"
    historical_audit["commit"] = M6_COMMIT
    return {
        "project_source_files": len(current), "project_files_added": len(added),
        "project_files_revised": len(revisions), "current_code_hashes_verified": len(hashes),
        "curated_file_hashes_verified": len(curated_hashes),
        "curation_provenance_records_verified": len(provenance),
        "curated_path_normalizations_verified": len(normalized),
        "retained_candidate_scientific_file_pairs_verified": 2,
        "test_receipt_code_hashes_verified": len(tests["code_hashes"]),
        "scientific_generator_runs": 0, "source_replays": 0, "target_analyses": 0,
        "historical_export_files_preserved": len(historical),
        "historical_nonproject_records_preserved": len(nonproject),
        "historical_m6_audit": historical_audit,
        "experiments_or_tests_rerun": False,
    }
