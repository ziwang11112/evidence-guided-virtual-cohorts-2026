"""Additive M9/M10 export custody; retain the complete fixed M8 audit."""
from __future__ import annotations

from functools import lru_cache
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

from audit_m3_export import PREFIX, digest, records_digest
from audit_m8_export import audit_m8_export

M8_COMMIT = "72daa75a5c212ca511c0df5d72c5770685aa597e"
CURATED = PREFIX + "reports/analysis_utility_feasibility_2026-10-30/"
PLAN = "sync/M10_EXPORT_PLAN.json"
RECEIPT = "sync/M10_EXPORT_RECEIPT.json"
HISTORICAL_LOCAL = {"sync/TEST_RESULTS.json"} | {
    p for n in range(2, 9)
    for p in (f"sync/M{n}_EXPORT_RECEIPT.json", f"docs/M{n}_EXPORT.md")
} | {f"sync/audit_m{n}_export.py" for n in range(3, 8)}
FORBIDDEN_PARTS = {"work", "raw", "downloads", "cache", ".cache", "runtime", "runtimes",
                   "__pycache__", ".pytest_cache", "source_contexts", ".git", "credentials"}
FORBIDDEN_NAMES = {"observed.csv", "reference.csv", "generated.csv", "design_weights.csv",
                   "id_mapping.csv", ".env", "credentials.json"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def filesystem_root(path):
    """Use Windows extended paths so unchanged deep historical files stay readable."""
    resolved = Path(path).resolve()
    prefix = chr(92) * 2 + "?" + chr(92)
    if os.name == "nt" and not str(resolved).startswith(prefix):
        return Path(prefix + str(resolved))
    return resolved


def portable_path(value):
    require(isinstance(value, str) and bool(value), "Missing relative path")
    parts = value.split("/")
    require(not PurePosixPath(value).is_absolute() and
            all(p not in {"", ".", ".."} and not p.endswith((".", " ")) for p in parts) and
            not any(c in value for c in "\\:\x00*?[]<>|\"") and
            not any(ord(c) < 32 for c in value), "Unsafe exact relative path")
    require(not {p.lower() for p in parts} & FORBIDDEN_PARTS and
            parts[-1].lower() not in FORBIDDEN_NAMES, "Forbidden export path")
    return value


def validate_plan(plan, prior):
    """Only approved exact files; no discovery, wildcard expansion or transformations."""
    require(plan.get("schema_version") == 1 and plan.get("milestone") == "M10" and
            plan.get("base_commit") == M8_COMMIT, "Wrong M10 plan identity or base")
    require(plan.get("content_review_complete") is True and
            plan.get("participant_or_generated_output_rows_exported") is False and
            plan.get("experiments_or_tests_rerun") is False, "Content/boundary review is incomplete")
    roots = plan.get("curated_roots", [])
    require(isinstance(roots, list) and CURATED in roots and len(roots) == len(set(roots)),
            "Exact M9/M10 curated roots required")
    for root in roots:
        require(re.fullmatch(re.escape(PREFIX) + r"reports/[A-Za-z0-9_-]+/", root) is not None,
                "A curated root must name one reports package")
        portable_path(root.rstrip("/"))
    documents = plan.get("project_documents", [])
    require(isinstance(documents, list) and len(documents) == len(set(documents)) and
            PREFIX + "MILESTONE_10_RESULTS.md" in documents, "Exact project documents required")
    for path in documents:
        portable_path(path)
        require((path.startswith(PREFIX) and "/" not in path.removeprefix(PREFIX) and
                 PurePosixPath(path).suffix in {".md", ".json"}) or
                path == PREFIX + "docs/SCIENTIFIC_ANALYSIS_UTILITY_PLAN.md", "Invalid project document")
    files = plan.get("files", [])
    require(isinstance(files, list) and bool(files), "No exact reviewed files")
    paths = []
    for item in files:
        path = portable_path(item["destination"])
        require(item["source"] == path and item.get("transform") == "none",
                "Copy only pre-curated bytes at matching relative paths")
        require(re.fullmatch(r"[0-9a-f]{64}", item.get("reviewed_sha256", "")) is not None,
                "Every source requires its reviewed SHA-256")
        require(isinstance(item.get("classification"), str) and bool(item["classification"]),
                "Every source requires a reviewed classification")
        require(path in documents or any(path.startswith(root) for root in roots),
                "File outside the exact reviewed package/document scope")
        if path in prior:
            require(path == PREFIX + "README.md", "Only the historical project README may be revised")
        if PurePosixPath(path).suffix.lower() in {".csv", ".tsv"}:
            schema = item.get("aggregate_table", {})
            require(type(schema.get("rows")) is int and schema["rows"] >= 0 and
                    isinstance(schema.get("required_keys"), list) and bool(schema["required_keys"]),
                    "New tables require explicit aggregate row/schema review")
        paths.append(path)
    require(len(paths) == len(set(paths)), "Duplicate exact destination")
    require(set(documents) <= set(paths) and
            all(any(path.startswith(root) for path in paths) for root in roots),
            "Unused document or curated-root declaration")
    return {item["destination"]: item for item in files}


@lru_cache(maxsize=None)
def historical_bytes(root, path):
    return subprocess.run(["git", "cat-file", "blob", M8_COMMIT + ":" + path],
                          cwd=root, capture_output=True, check=True).stdout


def audit_m10_export(root, manifest, receipt, findings):
    if receipt is None:
        return {"status": "not_exported"}

    def check(ok, path, rule):
        if not ok:
            findings.append({"file": path, "rule": rule})

    def file_hash(path):
        full = root / path
        return digest(full.read_bytes()) if full.is_file() else None

    base_bytes = historical_bytes(root, "sync/EXPORT_MANIFEST.json")
    base = json.loads(base_bytes)
    old_records = {r["destination"]: r for r in base["files"]}
    current_records = {r["destination"]: r for r in manifest["files"]}
    plan_bytes = (root / PLAN).read_bytes()
    plan = json.loads(plan_bytes)
    approved = validate_plan(plan, old_records)
    check(receipt["base_commit"] == M8_COMMIT and
          receipt["previous_export_manifest_sha256"] == digest(base_bytes) and
          receipt["plan_sha256"] == digest(plan_bytes), RECEIPT, "m10_snapshot_or_plan_binding_mismatch")
    expected_paths = set(old_records) | set(approved)
    check(set(current_records) == expected_paths and len(current_records) == len(manifest["files"]),
          RECEIPT, "m10_exact_file_scope_mismatch")
    for path, record in current_records.items():
        if path not in approved:
            check(record == old_records.get(path), path, "m10_historical_record_changed")
        else:
            item = approved[path]
            check(all(record.get(k) == v for k, v in item.items()) and
                  record["source_sha256"] == record["export_sha256"] == item["reviewed_sha256"],
                  path, "m10_reviewed_source_binding_mismatch")
        check(file_hash(path) == record["export_sha256"], path, "m10_current_file_hash_mismatch")
    prior = {p: r["export_sha256"] for p, r in old_records.items() if p.startswith(PREFIX)}
    current = {p: r["export_sha256"] for p, r in current_records.items() if p.startswith(PREFIX)}
    revised = {p: {"historical_sha256": h, "current_sha256": current.get(p)}
               for p, h in prior.items() if current.get(p) != h}
    added = {p: h for p, h in current.items() if p not in prior}
    check(receipt["revised_project_files"] == revised and receipt["added_project_files"] == added and
          receipt["curated_export_sha256"] == current, RECEIPT, "m10_successor_hash_binding_mismatch")
    historical = {p: h for p, h in prior.items() if p not in revised}
    historical.update({p: digest(historical_bytes(root, p)) for p in HISTORICAL_LOCAL})
    check(receipt["historical_file_sha256"] == historical, RECEIPT, "m10_historical_scope_mismatch")
    for path, expected in historical.items():
        check(file_hash(path) == expected, path, "m10_historical_file_changed")
    nonproject = [r for r in manifest["files"] if not r["destination"].startswith(PREFIX)]
    check(nonproject == [r for r in base["files"] if not r["destination"].startswith(PREFIX)] and
          receipt["historical_nonproject_records_sha256"] == records_digest(nonproject) and
          receipt["historical_nonproject_records_preserved"] == len(nonproject),
          RECEIPT, "m10_nonproject_records_changed")
    m8_bytes = historical_bytes(root, "sync/M8_EXPORT_RECEIPT.json")
    m8 = json.loads(m8_bytes)
    check(receipt["historical_m8_export_receipt_sha256"] == digest(m8_bytes) ==
          file_hash("sync/M8_EXPORT_RECEIPT.json"), RECEIPT, "m10_historical_m8_receipt_changed")
    for n in range(2, 7):
        key = f"historical_m{n}_code_revisions"
        check(receipt[key] == m8[key], RECEIPT, "m10_historical_code_revision_changed")
    check(receipt["experiments_or_tests_rerun"] is False and
          receipt["participant_or_generated_output_rows_exported"] is False,
          RECEIPT, "m10_export_boundary_mismatch")
    package_counts = {}
    for package in plan["curated_roots"]:
        hashes = json.loads((root / package / "file_manifest.json").read_bytes())
        package_paths = {p.removeprefix(package) for p in current if p.startswith(package)}
        check(package_paths == set(hashes) | {"file_manifest.json"}, package,
              "m10_curated_manifest_scope_mismatch")
        for relative, expected in hashes.items():
            check(file_hash(package + relative) == expected, package + relative,
                  "m10_curated_manifest_hash_mismatch")
        package_counts[package] = len(package_paths)
    for path, revision in receipt["local_document_revisions"].items():
        check(path == "README.md" and revision == {
            "historical_sha256": digest(historical_bytes(root, path)),
            "current_sha256": file_hash(path)}, path, "m10_local_document_revision_mismatch")
    check(receipt["precopy_review_sha256"] == file_hash("sync/M10_PRECOPY_REVIEW.json"),
          RECEIPT, "m10_precopy_review_binding_mismatch")
    old = lambda path: historical_bytes(root, path)
    receipts = [json.loads(old(f"sync/M{n}_EXPORT_RECEIPT.json")) for n in range(2, 8)]
    historical_audit = audit_m8_export(root, base, receipts[0],
        json.loads(old(PREFIX + "m2_validation.json")), *receipts[1:], m8, findings, read_bytes=old)
    historical_audit.update(binding="historical_git_snapshot", commit=M8_COMMIT)
    return {"project_source_files": len(current), "project_files_added": len(added),
            "project_files_revised": len(revised), "reviewed_exact_files": len(approved),
            "historical_export_files_preserved": len(historical),
            "historical_nonproject_records_preserved": len(nonproject),
            "curated_package_files": package_counts,
            "experiments_or_tests_rerun": False, "historical_m8_audit": historical_audit}
