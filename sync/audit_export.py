"""Fail-closed export inventory and content audit. Prints findings, never matched secrets."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCAL_FILES = {
    ".gitignore", ".gitattributes", "README.md", "docs/REPRODUCTION.md",
    "docs/EARLIER_LIMITATIONS.md", "sync/source_allowlist.json",
    "sync/sync_export.py", "sync/audit_export.py", "sync/EXPORT_MANIFEST.json",
    "sync/EXPORT_AUDIT.json", "sync/FILE_INVENTORY.tsv", "sync/TEST_RESULTS.json",
}
GENERATED_AUDIT = {"sync/EXPORT_AUDIT.json", "sync/FILE_INVENTORY.tsv"}
ALLOWED_SUFFIXES = {".md", ".py", ".json", ".csv", ".tsv"}
CSV_ROWS = {"all_results.csv": 5040, "completion_pooled.csv": 36, "full_synthetic_summary.csv": 35}
BLOCKED_COLUMNS = {"person_id", "patient_id", "subject_id", "participant_id", "name", "email", "address", "date_of_birth", "weight_kg", "pfs", "gng", "dd100", "dd1000"}
SECRET_RULES = {
    "github_token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,})"),
    "provider_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "credential_assignment": re.compile(r'''(?i)(?:api_key|access_token|password|client_secret)\s*[:=]\s*["'][^"'\s]{12,}["']'''),
}
ABSOLUTE_PATH = re.compile(r"(?:[A-Za-z]:[\\/](?:Users|AIR-|Codex)|[/](?:home|Users)/[^\s/]+/)")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((ROOT / "sync/EXPORT_MANIFEST.json").read_text(encoding="utf-8"))
    allowed = {r["destination"] for r in manifest["files"]} | LOCAL_FILES
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
        if path.suffix.lower() not in ALLOWED_SUFFIXES and relative not in {".gitignore", ".gitattributes"}:
            findings.append({"file": relative, "rule": "blocked_type"})
        if relative in GENERATED_AUDIT:
            continue  # Audit outputs are regenerated below, avoiding self-hashes.
        text = path.read_text(encoding="utf-8-sig")
        for name, pattern in SECRET_RULES.items():
            if pattern.search(text):
                findings.append({"file": relative, "rule": name})
        if ABSOLUTE_PATH.search(text):
            findings.append({"file": relative, "rule": "machine_absolute_path"})
        if path.suffix.lower() == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                columns = reader.fieldnames or []
                rows = list(reader)
            if path.name not in CSV_ROWS or len(rows) != CSV_ROWS.get(path.name):
                findings.append({"file": relative, "rule": "unapproved_table_or_row_count"})
            if set(columns) & BLOCKED_COLUMNS or not {"analysis", "term"}.issubset(columns):
                findings.append({"file": relative, "rule": "possible_participant_table"})
            table_audit.append({"file": relative, "rows": len(rows), "columns": columns, "unit": "analysis summary"})
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
    with (ROOT / "sync/FILE_INVENTORY.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["file", "bytes", "sha256"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(inventory)
    audit = {"status": "PASS" if not findings else "FAIL", "files_audited": len(inventory),
             "bytes_audited": sum(r["bytes"] for r in inventory), "source_files": len(manifest["files"]),
             "findings": findings, "aggregate_tables": table_audit,
             "original_batch_output_hashes_verified": len(outputs["files"]),
             "excluded_from_self_hash_inventory": sorted(GENERATED_AUDIT),
             "manual_content_review": "Exact allowlist and source prose/code reviewed; earlier patient-bearing reports excluded. Regex alone cannot establish data privacy.",
             "omitted": ["participant reference tables", "masked and completed participant tables", "mask keys", "full synthetic tables", "paper PDFs and HTML", "patient-bearing prompts", "environments", "credentials", "original absolute-path source freezes"]}
    (ROOT / "sync/EXPORT_AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: audit[k] for k in ("status", "files_audited", "bytes_audited", "source_files", "findings")}, indent=2))
    sys.exit(bool(findings))


if __name__ == "__main__":
    main()
