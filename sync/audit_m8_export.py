"""Verify the bounded M8 aggregate export and fixed M7 historical snapshot."""
from __future__ import annotations

import csv
from functools import lru_cache
import json
import subprocess

from audit_m3_export import PREFIX, digest, records_digest
from audit_m7_export import audit_m7_export

M7_COMMIT = "6e082b386d04f8071a5df0db72dfec29e95e3075"
CURATED = PREFIX + "reports/joint_evidence_pilot_2026-10-29/"
RECEIPT = "sync/M8_EXPORT_RECEIPT.json"
HISTORICAL_LOCAL = {"sync/TEST_RESULTS.json"} | {
    path for n in range(2, 8)
    for path in (f"sync/M{n}_EXPORT_RECEIPT.json", f"docs/M{n}_EXPORT.md")
}
TABLES = {
    "research/Mikkelsen2023_joint_age_BMI_sex_TG.csv": (30, [
        "source_id", "sex", "model_n_reported_in_supplement", "age_category_years",
        "bmi_category_kg_m2", "estimate", "estimate_unit", "ci_level", "ci_lower",
        "ci_upper", "reference", "raw_estimate", "raw_ci", "docx_table_index_1based",
        "docx_row_index_1based", "locator", "status"]),
    "evaluation/results/endpoint_comparison.csv": (402, [
        "variant", "seed", "endpoint", "estimate", "scale", "point_direction", "n",
        "exp_estimate", "reference_estimate", "reference_ci_low", "reference_ci_high",
        "reference_point_direction", "reference_ci_direction", "point_direction_agrees",
        "signed_error", "absolute_error", "mean_mg_dl"]),
}


@lru_cache(maxsize=None)
def historical_bytes(root, path):
    return subprocess.run(["git", "cat-file", "blob", M7_COMMIT + ":" + path],
                          cwd=root, capture_output=True, check=True).stdout


def audit_m8_export(root, manifest, m2_receipt, m2_validation, m3_receipt, m4_receipt,
                    m5_receipt, m6_receipt, m7_receipt, receipt, findings):
    if receipt is None:
        return {"status": "not_exported"}

    def check(ok, path, rule):
        if not ok:
            findings.append({"file": path, "rule": rule})

    def file_hash(path):
        full = root / path
        return digest(full.read_bytes()) if full.is_file() else None

    def curated_json(path):
        return json.loads((root / CURATED / path).read_bytes())

    base_bytes = historical_bytes(root, "sync/EXPORT_MANIFEST.json")
    base = json.loads(base_bytes)
    prior_receipt_bytes = historical_bytes(root, "sync/M7_EXPORT_RECEIPT.json")
    prior_receipt = json.loads(prior_receipt_bytes)
    check(receipt["base_commit"] == M7_COMMIT and
          receipt["previous_export_manifest_sha256"] == digest(base_bytes), RECEIPT,
          "m8_previous_snapshot_binding_mismatch")
    check(receipt["historical_m7_export_receipt_sha256"] == digest(prior_receipt_bytes) ==
          file_hash("sync/M7_EXPORT_RECEIPT.json") and m7_receipt == prior_receipt,
          RECEIPT, "m8_historical_receipt_changed")
    prior = {r["destination"]: r["export_sha256"] for r in base["files"]
             if r["destination"].startswith(PREFIX)}
    current = {r["destination"]: r["export_sha256"] for r in manifest["files"]
               if r["destination"].startswith(PREFIX)}
    revised = {p: {"historical_sha256": h, "current_sha256": current.get(p)}
               for p, h in prior.items() if current.get(p) != h}
    added = {p: h for p, h in current.items() if p not in prior}
    check(set(prior) <= set(current) and set(revised) == {PREFIX + "README.md"},
          RECEIPT, "m8_historical_source_scope_changed")
    check(all(p.startswith(CURATED) or p in
              {PREFIX + "MILESTONE_8_RESULTS.md", PREFIX + "m8_validation.json"}
              for p in added), RECEIPT, "m8_addition_outside_scope")
    check(receipt["revised_project_files"] == revised and receipt["added_project_files"] == added
          and receipt["curated_export_sha256"] == current, RECEIPT, "m8_receipt_scope_mismatch")
    historical = {p: h for p, h in prior.items() if p not in revised}
    historical.update({p: digest(historical_bytes(root, p)) for p in HISTORICAL_LOCAL})
    check(receipt["historical_file_sha256"] == historical, RECEIPT, "m8_historical_hash_scope_mismatch")
    for path, expected in historical.items():
        check(file_hash(path) == expected, path, "m8_historical_file_changed")
    nonproject = [r for r in manifest["files"] if not r["destination"].startswith(PREFIX)]
    check(nonproject == [r for r in base["files"] if not r["destination"].startswith(PREFIX)] and
          len(nonproject) == receipt["historical_nonproject_records_preserved"] == 838 and
          records_digest(nonproject) == receipt["historical_nonproject_records_sha256"],
          RECEIPT, "m8_nonproject_records_changed")
    for milestone in ("m2", "m3", "m4", "m5", "m6"):
        key = "historical_" + milestone + "_code_revisions"
        check(receipt[key] == prior_receipt[key], RECEIPT, "m8_historical_code_revision_changed")

    validation = json.loads((root / PREFIX / "m8_validation.json").read_bytes())
    check(validation["milestone"] == "M8" and validation["new_harness_core_changes"] is False,
          RECEIPT, "m8_validation_identity_or_core_change")
    for path, expected in validation["harness_code_bindings"].items():
        check(prior.get(PREFIX + path) == current.get(PREFIX + path) == expected ==
              file_hash(PREFIX + path), PREFIX + path, "m8_harness_code_binding_mismatch")
    hashes = curated_json("file_manifest.json")
    check({p.removeprefix(CURATED) for p in current if p.startswith(CURATED)} ==
          set(hashes) | {"file_manifest.json"} and len(hashes) + 1 == validation["curated_files"],
          RECEIPT, "m8_curated_manifest_scope_mismatch")
    for path, expected in hashes.items():
        check(file_hash(CURATED + path) == expected, CURATED + path, "m8_curated_hash_mismatch")
        parts = path.split("/")
        check(not set(parts) & {"work", "source_contexts", "raw", "cache", ".cache",
                               "runtime", "runtimes", "__pycache__", ".pytest_cache"} and
              not any(p.startswith("pytest-") for p in parts), CURATED + path,
              "m8_forbidden_directory")
    for key, path in {"report_sha256": PREFIX + "MILESTONE_8_RESULTS.md",
                      "readme_sha256": PREFIX + "README.md",
                      "curated_manifest_sha256": CURATED + "file_manifest.json"}.items():
        check(validation[key] == file_hash(path), path, "m8_validation_artifact_hash_mismatch")
    pairs = curated_json("curation_provenance.json")["pairs"]
    originals = {r["curated_relative"]: r["original_sha256"] for r in pairs}
    check(len(originals) == len(pairs) and set(originals) ==
          set(hashes) - {"README.md", "curation_provenance.json", "curation_repair.json"}, RECEIPT,
          "m8_provenance_scope_mismatch")
    normalized = {}
    for record in pairs:
        path = record["curated_relative"]
        check(hashes.get(path) == record["copied_sha256"], CURATED + path,
              "m8_provenance_copied_hash_mismatch")
        check((record["original_sha256"] != record["copied_sha256"]) ==
              record["machine_paths_normalized"], CURATED + path,
              "m8_normalization_disclosure_mismatch")
        if record["machine_paths_normalized"]:
            normalized[path] = record
    check(receipt["curated_path_normalizations"] == normalized, RECEIPT,
          "m8_normalization_receipt_mismatch")
    repair = curated_json("curation_repair.json")
    check(validation["curation_repair_sha256"] == file_hash(CURATED + "curation_repair.json") and
          repair["original_execution_receipts_unchanged"] is True and
          repair["scientific_values_or_code_changed"] is False, RECEIPT,
          "m8_curation_repair_binding_mismatch")
    repaired_paths = {f"execution_bundle/executions/{v}_{s}/execution.json"
                      for v in ("baseline", "joint_evidence") for s in (80101, 80102, 80103)}
    check({r["curated_relative"] for r in repair["changes"]} == repaired_paths,
          RECEIPT, "m8_curation_repair_scope_mismatch")
    for record in repair["changes"]:
        path = record["curated_relative"]
        runtime = curated_json(path)["runtime"]
        check(record["fields"] == ["runtime.venv_root", "runtime.bwrap"] and
              record["prior_copied_sha256"] == originals[path] and
              record["copied_sha256"] == file_hash(CURATED + path) and
              runtime["venv_root"] == "${RUNTIME_ROOT}/venv" and
              runtime["bwrap"] == "${RUNTIME_ROOT}/bubblewrap/usr/bin/bwrap", CURATED + path,
              "m8_curation_repair_content_mismatch")
    for label, expected in validation["candidate_hashes"].items():
        path = "agent_bundle/candidates/" + label + "/freeze.json"
        check(file_hash(CURATED + path) == expected == originals[path], CURATED + path,
              "m8_candidate_freeze_mismatch")
        freeze = curated_json(path)
        for name, original in originals.items():
            if name.startswith("agent_bundle/candidates/" + label + "/") and name != path:
                check(freeze["commitments"].get(name.removeprefix("agent_bundle/")) == original,
                      CURATED + name, "m8_candidate_commitment_mismatch")
    check({p for p in hashes if p.endswith(".csv")} == set(TABLES), RECEIPT,
          "m8_aggregate_table_scope_mismatch")
    table_rows = {}
    for path, (count, fields) in TABLES.items():
        with (root / CURATED / path).open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
        check(reader.fieldnames == fields and len(rows) == count, CURATED + path,
              "m8_aggregate_table_schema_mismatch")
        table_rows[path] = rows
    endpoint_rows = table_rows["evaluation/results/endpoint_comparison.csv"]
    groups = {}
    for row in endpoint_rows:
        groups.setdefault((row["variant"], row["seed"]), []).append(row["endpoint"])
    check(set(groups) == {(v, s) for v in ("baseline", "joint_evidence")
                         for s in ("80101", "80102", "80103")} and
          all(len(es) == len(set(es)) == 67 for es in groups.values()) and
          len({tuple(sorted(es)) for es in groups.values()}) == 1,
          RECEIPT, "m8_endpoint_grid_incomplete")
    for path, expected in curated_json("evaluation/results/result_hashes.json").items():
        check(originals.get("evaluation/results/" + path) == expected, CURATED + path,
              "m8_original_result_hash_mismatch")
    audit = curated_json("review/POSTRUN_CONCLUSION_AUDIT.json")
    check(audit["status"] == "passed" and audit["checks_count"] == len(audit["checks"]) == 49
          and all(r["passed"] is True for r in audit["checks"]), RECEIPT,
          "m8_postrun_audit_not_passed")
    check(validation["target_endpoint_comparisons"] == 402 and validation["source_replays"] == 6
          and validation["source_generator_executions"] == 12
          and validation["target_generator_executions"] == 6
          and validation["target_feedback_used_for_revision"] is False
          and validation["post_target_candidate_change"] is False
          and receipt["experiments_or_tests_rerun"] is False
          and receipt["participant_or_generated_output_rows_exported"] is False,
          RECEIPT, "m8_execution_or_export_boundary_mismatch")
    historical_audit = audit_m7_export(
        root, base, m2_receipt, m2_validation, m3_receipt, m4_receipt, m5_receipt,
        m6_receipt, prior_receipt, findings, read_bytes=lambda p: historical_bytes(root, p))
    historical_audit["binding"] = "historical_git_snapshot"
    historical_audit["commit"] = M7_COMMIT
    return {"project_source_files": len(current), "project_files_added": len(added),
            "project_files_revised": len(revised),
            "harness_code_hashes_verified": len(validation["harness_code_bindings"]),
            "curated_file_hashes_verified": len(hashes), "curation_provenance_pairs_verified": len(pairs),
            "curated_path_normalizations_verified": len(normalized),
            "published_aggregate_rows": 30, "target_endpoint_comparison_rows": 402,
            "postrun_audit_checks_verified": 49, "historical_export_files_preserved": len(historical),
            "historical_nonproject_records_preserved": len(nonproject),
            "experiments_or_tests_rerun": False, "historical_m7_audit": historical_audit}
