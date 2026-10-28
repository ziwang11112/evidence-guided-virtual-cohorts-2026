"""Fail-closed export inventory and content audit. Prints findings, never matched secrets."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
from audit_insulin_export import audit_insulin
from audit_gap_loop_export import audit_gap_loop
from audit_three_model_review import audit_three_model_review
from audit_m3_export import audit_m3_export

ROOT = Path(__file__).resolve().parents[1]
LOCAL_FILES = {
    ".gitignore", ".gitattributes", "README.md", "docs/REPRODUCTION.md",
    "docs/EARLIER_LIMITATIONS.md", "docs/STAGE1_EXPORT.md", "sync/source_allowlist.json",
    "sync/sync_export.py", "sync/audit_export.py", "sync/EXPORT_MANIFEST.json",
    "sync/EXPORT_AUDIT.json", "sync/FILE_INVENTORY.tsv", "sync/TEST_RESULTS.json",
    "sync/CURRENT_SCOPE_REVISION.json",
    "sync/INSULIN_PILOT_REVISION.json", "sync/INSULIN_EXPORT_RECEIPT.json",
    "sync/audit_insulin_export.py", "docs/INSULIN_EXPORT.md",
    "sync/DESIGN_REVIEW_SYNC_2026-10-28.json",
    "sync/DESIGN_REVIEW_SYNC_2026-10-28_v2.json",
    "sync/GAP_LOOP_EXPORT_RECEIPT_2026-10-28.json",
    "sync/audit_gap_loop_export.py", "docs/GAP_LOOP_EXPORT.md",
    "sync/audit_three_model_review.py",
    "sync/M2_EXPORT_RECEIPT.json", "docs/M2_EXPORT.md",
    "sync/audit_m3_export.py", "sync/M3_EXPORT_RECEIPT.json", "docs/M3_EXPORT.md",
    "biomedical_research/three_model_review_2026-10-28/README.md",
    "biomedical_research/three_model_review_2026-10-28/REVIEW_PACKAGE_MANIFEST.json",
}
GENERATED_AUDIT = {"sync/EXPORT_AUDIT.json", "sync/FILE_INVENTORY.tsv"}
ALLOWED_SUFFIXES = {".md", ".py", ".json", ".csv", ".tsv", ".png", ".svg", ".pdf", ".txt"}
REVIEWED_CONFIG_FILES = {"biomedical_research/virtual_cohort_system/.gitignore",
                         "biomedical_research/virtual_cohort_system/pyproject.toml",
                         "biomedical_research/virtual_cohort_system/docs/system-explorer/index.html",
                         "biomedical_research/virtual_cohort_system/docs/system-explorer/architecture.drawio",
                         "biomedical_research/virtual_cohort_system/docs/system-explorer/verify_explorer.cjs"}
CSV_ROWS = {"all_results.csv": 5040, "completion_pooled.csv": 36, "full_synthetic_summary.csv": 35}
BLOCKED_COLUMNS = {"person_id", "patient_id", "subject_id", "participant_id", "name", "email", "address", "date_of_birth", "weight_kg", "pfs", "gng", "dd100", "dd1000"}
SECRET_RULES = {
    "github_token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,})"),
    "provider_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "credential_assignment": re.compile(r'''(?i)(?:api_key|access_token|password|client_secret)\s*[:=]\s*["'][^"'\s]{12,}["']'''),
}
ABSOLUTE_PATH = re.compile(r"(?:[A-Za-z]:[\\/]+(?:Users|AIR-|Codex)|[/](?:home|Users)/[^\s/]+/)")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((ROOT / "sync/EXPORT_MANIFEST.json").read_text(encoding="utf-8"))
    allowed = {r["destination"] for r in manifest["files"]} | LOCAL_FILES
    source_records = {r["destination"]: r for r in manifest["files"]}
    m2_receipt = json.loads((ROOT / "sync/M2_EXPORT_RECEIPT.json").read_text(encoding="utf-8"))
    runtime_prefix = "/" + "/".join(("home", "zwang", ".cache", "evidence-cohort-runtime", "m2"))
    runtime_paths = {
        "biomedical_research/virtual_cohort_system/cohort_harness/execution.py": 1,
        "biomedical_research/virtual_cohort_system/docs/EXECUTION_ADAPTER.md": 2,
    }
    findings, inventory, table_audit = [], [], []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT).as_posix()
        if ".git" in path.relative_to(ROOT).parts:
            continue
        if path.is_symlink():
            findings.append({"file": relative, "rule": "symlink"})
            continue
        if not path.is_file():
            continue
        if relative not in allowed:
            findings.append({"file": relative, "rule": "not_allowlisted"})
        if path.suffix.lower() not in ALLOWED_SUFFIXES and relative not in {".gitignore", ".gitattributes"} | REVIEWED_CONFIG_FILES:
            findings.append({"file": relative, "rule": "blocked_type"})
        if relative in GENERATED_AUDIT:
            continue  # Audit outputs are regenerated below, avoiding self-hashes.
        if path.suffix.lower() in {".png", ".pdf"}:
            raw = path.read_bytes()
            magic = b"%PDF-" if path.suffix.lower() == ".pdf" else b"\x89PNG\r\n\x1a\n"
            if not raw.startswith(magic) or source_records.get(relative, {}).get("classification") != "aggregate_plot":
                findings.append({"file": relative, "rule": "unapproved_binary_plot"})
            text = raw.decode("utf-8", errors="ignore")
        else:
            text = path.read_text(encoding="utf-8-sig")
        for name, pattern in SECRET_RULES.items():
            if pattern.search(text):
                findings.append({"file": relative, "rule": name})
        path_text = text
        if relative in runtime_paths:
            exception = m2_receipt["reviewed_runtime_configuration"][relative]
            if (exception["sha256"] != sha(path) or
                    exception["prefix_occurrences"] != runtime_paths[relative] or
                    text.count(runtime_prefix) != runtime_paths[relative]):
                findings.append({"file": relative, "rule": "runtime_configuration_exception_mismatch"})
            path_text = text.replace(runtime_prefix, "REVIEWED_RUNTIME_ROOT")
        if ABSOLUTE_PATH.search(path_text):
            findings.append({"file": relative, "rule": "machine_absolute_path"})
        schema = source_records.get(relative, {}).get("aggregate_table")
        if path.suffix.lower() in {".csv", ".tsv"} and relative != "sync/FILE_INVENTORY.tsv":
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream, delimiter="\t" if path.suffix.lower() == ".tsv" else ",")
                columns = reader.fieldnames or []
                rows = list(reader)
            expected_rows = schema["rows"] if schema else CSV_ROWS.get(path.name)
            required = set(schema["required_keys"]) if schema else {"analysis", "term"}
            if expected_rows is None or len(rows) != expected_rows:
                findings.append({"file": relative, "rule": "unapproved_table_or_row_count"})
            if set(columns) & BLOCKED_COLUMNS or not required.issubset(columns):
                findings.append({"file": relative, "rule": "possible_participant_table"})
            table_audit.append({"file": relative, "rows": len(rows), "columns": columns, "unit": "analysis summary"})
        elif path.suffix.lower() == ".json" and schema:
            rows = json.loads(text)
            if not isinstance(rows, list) or len(rows) != schema["rows"]:
                findings.append({"file": relative, "rule": "aggregate_json_row_count"})
            elif any(not isinstance(r, dict) or not set(schema["required_keys"]).issubset(r) or set(r) & BLOCKED_COLUMNS for r in rows):
                findings.append({"file": relative, "rule": "aggregate_json_schema"})
            table_audit.append({"file": relative, "rows": len(rows), "unit": "analysis summary"})
        inventory.append({"file": relative, "bytes": path.stat().st_size, "sha256": sha(path)})
    if sha(ROOT / "sync/source_allowlist.json") != manifest["allowlist_sha256"]:
        findings.append({"file": "sync/source_allowlist.json", "rule": "allowlist_changed_since_export"})
    for item in manifest["files"]:
        p = ROOT / item["destination"]
        if not p.is_file() or sha(p) != item["export_sha256"]:
            findings.append({"file": item["destination"], "rule": "export_hash_mismatch"})
    batch = ROOT / "biomedical_research/evidence_virtual_cohort_framework_2026-10-27/development_batch/attempt_02/results"
    outputs = json.loads((batch / "output_manifest.json").read_text(encoding="utf-8"))
    for name, expected in outputs["files"].items():
        if sha(batch / name) != expected:
            findings.append({"file": (batch / name).relative_to(ROOT).as_posix(), "rule": "original_output_hash_mismatch"})
    stage_eval = ROOT / "biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/custodian/evaluation_v1"
    stage_output_count = 0
    if (stage_eval / "evaluation_manifest.json").is_file():
        stage_outputs = json.loads((stage_eval / "evaluation_manifest.json").read_text(encoding="utf-8"))
        for name, expected in stage_outputs["files"].items():
            if not (stage_eval / name).is_file() or sha(stage_eval / name) != expected:
                findings.append({"file": (stage_eval / name).relative_to(ROOT).as_posix(), "rule": "stage1_output_hash_mismatch"})
        stage_output_count = len(stage_outputs["files"])
    report = stage_eval.parents[1] / "reporting"
    report_output_count = 0
    if (report / "reporting_manifest.json").is_file():
        report_manifest = json.loads((report / "reporting_manifest.json").read_text(encoding="utf-8"))
        for name, expected in report_manifest["generated_files"].items():
            if not (report / name).is_file() or sha(report / name) != expected:
                findings.append({"file": (report / name).relative_to(ROOT).as_posix(), "rule": "reporting_output_hash_mismatch"})
        if sha(report.parent / "RESULTS.md") != report_manifest["results_md_sha256"]:
            findings.append({"file": (report.parent / "RESULTS.md").relative_to(ROOT).as_posix(), "rule": "reporting_results_hash_mismatch"})
        report_output_count = len(report_manifest["generated_files"])
    delivery_path = stage_eval.parents[2] / "delivery_stage1.json"
    delivery_count = 0
    delivery_revision_count = 0
    followup_revision_count = 0
    if delivery_path.is_file():
        delivery = json.loads(delivery_path.read_text(encoding="utf-8"))
        receipt_path = ROOT / "sync/CURRENT_SCOPE_REVISION.json"
        revisions = {}
        if receipt_path.is_file():
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            revisions = {r["path"]: r for r in receipt["revised_delivery_documents"]}
            permitted_revision_documents = {"README.md", "METHODS_AND_EXPERIMENT_PLAN.md", "AGENT_STRATEGIES.md", "MANUSCRIPT_SKELETON.md"}
            if not set(revisions).issubset(permitted_revision_documents) or len(revisions) != len(receipt["revised_delivery_documents"]):
                findings.append({"file": "sync/CURRENT_SCOPE_REVISION.json", "rule": "invalid_revision_document_scope"})
            if receipt["historical_delivery_manifest_sha256"] != sha(delivery_path):
                findings.append({"file": "sync/CURRENT_SCOPE_REVISION.json", "rule": "historical_delivery_manifest_changed"})
        followup_path = ROOT / "sync/INSULIN_PILOT_REVISION.json"
        followups = {}
        if followup_path.is_file():
            followup = json.loads(followup_path.read_text(encoding="utf-8"))
            followups = {r["path"]: r for r in followup["revised_delivery_documents"]}
            if set(followups) != {"README.md"} or len(followup["revised_delivery_documents"]) != 1:
                findings.append({"file": "sync/INSULIN_PILOT_REVISION.json", "rule": "invalid_followup_revision_scope"})
            if followup["previous_revision_receipt"] != "sync/CURRENT_SCOPE_REVISION.json" or followup["previous_revision_receipt_sha256"] != sha(receipt_path) or followup["historical_delivery_manifest_sha256"] != sha(delivery_path):
                findings.append({"file": "sync/INSULIN_PILOT_REVISION.json", "rule": "revision_chain_hash_mismatch"})
        used_revisions = set()
        used_followups = set()
        for entry in delivery["artifacts"]:
            path = delivery_path.parent / entry["path"]
            actual = sha(path) if path.is_file() else None
            if actual == entry["sha256"]:
                delivery_count += 1
                continue
            revision = revisions.get(entry["path"])
            followup = followups.get(entry["path"])
            expected_current = revision["current_sha256"] if revision else None
            if followup and revision and followup["previous_sha256"] == expected_current:
                expected_current = followup["current_sha256"]
                used_followups.add(entry["path"])
                followup_revision_count += 1
            if revision and revision["historical_sha256"] == entry["sha256"] and expected_current == actual:
                delivery_revision_count += 1
                used_revisions.add(entry["path"])
            else:
                findings.append({"file": path.relative_to(ROOT).as_posix(), "rule": "delivery_artifact_hash_mismatch"})
        if used_revisions != set(revisions):
            findings.append({"file": "sync/CURRENT_SCOPE_REVISION.json", "rule": "unused_or_unmatched_document_revision"})
        if used_followups != set(followups):
            findings.append({"file": "sync/INSULIN_PILOT_REVISION.json", "rule": "unused_or_unmatched_followup_revision"})
    insulin_audit = audit_insulin(ROOT, source_records, findings)
    gap_loop_audit = audit_gap_loop(ROOT, source_records, findings)
    review_audit = audit_three_model_review(ROOT, source_records, findings)
    m2_root = ROOT / "biomedical_research/virtual_cohort_system"
    m2_validation = json.loads((m2_root / "m2_validation.json").read_text(encoding="utf-8"))
    m3_path = ROOT / "sync/M3_EXPORT_RECEIPT.json"
    m3_receipt = json.loads(m3_path.read_text(encoding="utf-8")) if m3_path.is_file() else None
    m2_revisions = m3_receipt["historical_m2_code_revisions"] if m3_receipt else {}
    for name, expected in m2_validation["code_sha256"].items():
        current = sha(m2_root / name)
        if current != expected and m2_revisions.get(name) != {
                "historical_sha256": expected, "current_sha256": current}:
            findings.append({"file": "biomedical_research/virtual_cohort_system/" + name, "rule": "m2_code_hash_mismatch"})
    for section in ("historical_m1_files", "agent_authored_specimen"):
        for name, expected in m2_receipt[section].items():
            if sha(m2_root / name) != expected:
                findings.append({"file": "biomedical_research/virtual_cohort_system/" + name, "rule": section + "_hash_mismatch"})
    current_m2 = {name: item["export_sha256"] for name, item in source_records.items()
                  if name.startswith("biomedical_research/virtual_cohort_system/")}
    expected_curated = (m3_receipt or m2_receipt)["curated_export_sha256"]
    if current_m2 != expected_curated:
        findings.append({"file": "sync/M3_EXPORT_RECEIPT.json" if m3_receipt else "sync/M2_EXPORT_RECEIPT.json",
                         "rule": "curated_scope_mismatch"})
    m3_audit = audit_m3_export(ROOT, manifest, m2_receipt, m2_validation, m3_receipt, findings)
    with (ROOT / "sync/FILE_INVENTORY.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["file", "bytes", "sha256"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(inventory)
    audit = {"status": "PASS" if not findings else "FAIL", "files_audited": len(inventory),
             "bytes_audited": sum(r["bytes"] for r in inventory), "source_files": len(manifest["files"]),
             "findings": findings, "aggregate_tables": table_audit,
             "original_batch_output_hashes_verified": len(outputs["files"]),
             "stage1_output_hashes_verified": stage_output_count,
             "reporting_output_hashes_verified": report_output_count,
             "delivery_artifact_hashes_verified": delivery_count,
             "documented_delivery_revisions_verified": delivery_revision_count,
             "followup_document_revisions_verified": followup_revision_count,
             "insulin_export": insulin_audit,
             "gap_loop_export": gap_loop_audit,
             "three_model_review": review_audit,
             "virtual_cohort_m2": {"source_files": len(current_m2),
                                   "unchanged_code_hashes_verified": len(m2_validation["code_sha256"]) - len(m2_revisions),
                                   "documented_historical_code_revisions": len(m2_revisions),
                                   "historical_m1_files_preserved": len(m2_receipt["historical_m1_files"]),
                                   "agent_specimen_hashes_verified": len(m2_receipt["agent_authored_specimen"]),
                                   "runtime_configuration_exceptions": len(runtime_paths),
                                   "experiments_or_tests_rerun": False},
             "virtual_cohort_m3": m3_audit,
             "excluded_from_self_hash_inventory": sorted(GENERATED_AUDIT),
             "manual_content_review": "Exact allowlist and source prose/code reviewed; earlier patient-bearing reports excluded. Regex alone cannot establish data privacy.",
             "omitted": ["participant reference tables", "masked and completed participant tables", "mask keys", "full synthetic tables", "paper PDFs and HTML", "patient-bearing prompts", "environments", "credentials", "original absolute-path source freezes"]}
    (ROOT / "sync/EXPORT_AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: audit[k] for k in ("status", "files_audited", "bytes_audited", "source_files", "findings")}, indent=2))
    sys.exit(bool(findings))


if __name__ == "__main__":
    main()
