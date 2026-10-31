"""Verify the exact M17-B scientific-pilot export delta; never upload or push."""
from __future__ import annotations

import argparse
import csv
import io
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = "sync/M17B_EXPORT_RECEIPT_2026-10-31.json"
OUTPUT = "sync/M17B_EXPORT_AUDIT_2026-10-31.json"
SELF = "sync/audit_m17b_export_2026-10-31.py"
SECRET_RULES = {
    "github_token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,})"),
    "provider_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
MACHINE_PATH = re.compile(r"(?:[A-Za-z]:[\\/]+(?:Users|AIR-|Codex)|[/](?:home|Users)/[^\s/]+/)")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("Non-relative export path")
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Export path escapes root")
    return path


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).splitlines()


def contains_individual_records(value):
    """Reject recognizable measurement records; scalar model specifications are allowed."""
    if isinstance(value, list):
        for entry in value:
            if isinstance(entry, dict):
                measured = set(entry) & {"sample_id", "age", "female", "bmi", "urate", "SEQN"}
                if len(measured) >= 3 and all(not isinstance(entry[k], (dict, list)) for k in measured):
                    return True
            if contains_individual_records(entry):
                return True
    elif isinstance(value, dict):
        return any(contains_individual_records(child) for child in value.values())
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve(strict=True)
    receipt = json.loads(safe(ROOT, RECEIPT).read_text(encoding="utf-8"))
    findings = []
    records = receipt["files"]
    expected = {r["destination"] for r in records}
    if len(records) != len(expected):
        findings.append({"rule": "duplicate_destination"})
    allowed = expected | {RECEIPT, OUTPUT, SELF}
    actual_changes = set(git("diff", "--name-only", receipt["prior_head"]))
    actual_changes.update(git("ls-files", "--others", "--exclude-standard"))
    for name in sorted(actual_changes - allowed):
        findings.append({"file": name, "rule": "unreviewed_change"})
    if sha(safe(ROOT, SELF).read_bytes()) != receipt["audit_script_sha256"]:
        findings.append({"file": SELF, "rule": "audit_script_changed"})
    for name, expected_hash in receipt["preserved_historical_receipt_hashes"].items():
        if sha(safe(ROOT, name).read_bytes()) != expected_hash:
            findings.append({"file": name, "rule": "historical_receipt_changed"})
    for item in receipt["superseded_mutable_files"]:
        before = subprocess.check_output(["git", "show", receipt["prior_head"] + ":" + item["path"]], cwd=ROOT)
        if sha(before) != item["prior_sha256"] or sha(safe(ROOT, item["path"]).read_bytes()) != item["current_sha256"]:
            findings.append({"file": item["path"], "rule": "mutable_revision_binding_mismatch"})
    checked_links = 0
    aggregate_csvs = []
    provenance_path_files = []
    for item in records:
        destination = safe(ROOT, item["destination"])
        raw = destination.read_bytes()
        if sha(raw) != item["export_sha256"]:
            findings.append({"file": item["destination"], "rule": "export_hash_mismatch"})
        if item.get("source"):
            source = safe(workspace, item["source"])
            if sha(source.read_bytes()) != item["source_sha256"]:
                findings.append({"file": item["destination"], "rule": "source_changed"})
        if destination.suffix.lower() not in {".md", ".json", ".py", ".csv", ".svg", ".png"}:
            findings.append({"file": item["destination"], "rule": "unapproved_payload_type"})
        forbidden = {"private", "originals", "executions", "__pycache__"}.intersection(destination.relative_to(ROOT).parts)
        if forbidden or "/builders/" in item["destination"] and "/sources/" in item["destination"]:
            findings.append({"file": item["destination"], "rule": "forbidden_payload_location"})
        if destination.suffix.lower() == ".png":
            if not raw.startswith(b"\x89PNG\r\n\x1a\n") or item.get("classification") != "original_aggregate_figure":
                findings.append({"file": item["destination"], "rule": "invalid_aggregate_image"})
            continue
        text = raw.decode("utf-8-sig")
        if destination.suffix.lower() == ".json" and contains_individual_records(json.loads(text)):
            findings.append({"file": item["destination"], "rule": "individual_measurement_records"})
        if destination.suffix.lower() == ".svg" and re.search(r"<(?:script|foreignObject)\b|(?:href|src)=[\"'](?:https?:|data:)", text, re.I):
            findings.append({"file": item["destination"], "rule": "active_or_external_svg_content"})
        if destination.suffix.lower() == ".csv":
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
            if reader.fieldnames != item.get("aggregate_csv_header") or len(rows) != item.get("aggregate_csv_rows"):
                findings.append({"file": item["destination"], "rule": "aggregate_csv_contract_mismatch"})
            if not set(reader.fieldnames or ()) <= {"builder", "stage", "seed", "route", "endpoint", "generated_estimate", "reference_estimate", "reference_se_hc3", "reference_ci95_lo", "reference_ci95_hi", "generated_minus_reference", "reference_interval_spans_zero", "point_sign_agreement", "realizations", "min_estimate", "max_estimate", "mean_estimate", "min_signed_difference", "max_signed_difference", "initial_estimate", "final_estimate", "final_minus_initial", "change_in_absolute_target_difference", "same_path", "same_bytes"} or "endpoint" not in (reader.fieldnames or ()):
                findings.append({"file": item["destination"], "rule": "nonaggregate_csv_schema"})
            aggregate_csvs.append({"path": item["destination"], "rows": len(rows), "fields": reader.fieldnames})
        for rule, pattern in SECRET_RULES.items():
            if pattern.search(text):
                findings.append({"file": item["destination"], "rule": rule})
        if MACHINE_PATH.search(text):
            if not item.get("local_provenance_paths_retained"):
                findings.append({"file": item["destination"], "rule": "undocumented_machine_path"})
            else:
                provenance_path_files.append(item["destination"])
        if destination.suffix.lower() == ".md":
            for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
                target = match.group(1).strip("<>")
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                    continue
                target = unquote(target.split("#", 1)[0])
                if not target:
                    continue
                checked_links += 1
                linked = (destination.parent / target).resolve()
                if not linked.is_relative_to(ROOT.resolve()) or not linked.exists():
                    findings.append({"file": item["destination"], "rule": "broken_local_link", "target": target})
    baseline = git("ls-tree", "-r", "--name-only", receipt["prior_head"])
    audit = {
        "status": "PASS" if not findings else "FAIL",
        "prior_head": receipt["prior_head"],
        "file_bindings_checked": len(records),
        "changed_paths": sorted(actual_changes),
        "historical_tracked_paths_outside_delta": len(set(baseline) - allowed),
        "local_links_checked": checked_links,
        "historical_receipts_verified": len(receipt["preserved_historical_receipt_hashes"]),
        "mutable_revision_bindings_verified": len(receipt["superseded_mutable_files"]),
        "aggregate_csvs_checked": aggregate_csvs,
        "local_provenance_paths_documented": provenance_path_files,
        "findings": findings,
        "scope": "Reviewed original code, decisions, source factual extractions, aggregate scientific diagnostics and documentation; no patient rows, generated individual tables, full papers, source duplicates or execution bundles. No scientific experiment rerun during export.",
    }
    safe(ROOT, OUTPUT).write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: audit[k] for k in ("status", "file_bindings_checked", "historical_tracked_paths_outside_delta", "local_links_checked", "findings")}, indent=2))
    raise SystemExit(bool(findings))


if __name__ == "__main__":
    main()
