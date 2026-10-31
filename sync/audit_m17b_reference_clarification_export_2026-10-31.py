"""Verify the exact M17-B reference-interpretation documentation export delta; never upload or push."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = "sync/M17B_REFERENCE_CLARIFICATION_EXPORT_RECEIPT_2026-10-31.json"
OUTPUT = "sync/M17B_REFERENCE_CLARIFICATION_EXPORT_AUDIT_2026-10-31.json"
SELF = "sync/audit_m17b_reference_clarification_export_2026-10-31.py"
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
    for item in records:
        destination = safe(ROOT, item["destination"])
        raw = destination.read_bytes()
        if sha(raw) != item["export_sha256"]:
            findings.append({"file": item["destination"], "rule": "export_hash_mismatch"})
        if item.get("source"):
            source = safe(workspace, item["source"])
            if sha(source.read_bytes()) != item["source_sha256"]:
                findings.append({"file": item["destination"], "rule": "source_changed"})
        if destination.suffix.lower() not in {".md", ".json", ".py"}:
            findings.append({"file": item["destination"], "rule": "unapproved_payload_type"})
        text = raw.decode("utf-8-sig")
        for rule, pattern in SECRET_RULES.items():
            if pattern.search(text):
                findings.append({"file": item["destination"], "rule": rule})
        if MACHINE_PATH.search(text):
            findings.append({"file": item["destination"], "rule": "machine_path"})
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
        "findings": findings,
        "scope": "Documentation-only clarification of sample-relative comparisons. All prior scientific code, protocol, numerical artifacts, plots and export receipts remain unchanged. No scientific or mean-uncertainty analysis rerun.",
    }
    safe(ROOT, OUTPUT).write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: audit[k] for k in ("status", "file_bindings_checked", "historical_tracked_paths_outside_delta", "local_links_checked", "findings")}, indent=2))
    raise SystemExit(bool(findings))


if __name__ == "__main__":
    main()
