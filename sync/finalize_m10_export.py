"""Preflight an exact reviewed M9/M10 plan; --apply copies bytes but never commits/pushes."""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import subprocess

from audit_m3_export import PREFIX, digest, records_digest
from audit_m10_export import (HISTORICAL_LOCAL, M8_COMMIT, PLAN, RECEIPT,
                             filesystem_root, historical_bytes, require, validate_plan)
from audit_export import ALLOWED_SUFFIXES, ABSOLUTE_PATH, BLOCKED_COLUMNS, SECRET_RULES

ROOT = filesystem_root(Path(__file__).resolve().parents[1])


def under(root, relative):
    path = root / relative
    require(path.resolve().is_relative_to(root.resolve()), "Path escapes declared root")
    current = path
    while current != root:
        require(not current.is_symlink() and not getattr(current, "is_junction", lambda: False)(),
                "Linked path is not permitted")
        current = current.parent
    return path


def inspect_bytes(item, raw):
    """Defense in depth after human content review; no matched content is printed."""
    path = item["destination"]
    suffix = Path(path).suffix.lower()
    require(suffix in ALLOWED_SUFFIXES, f"Unapproved file type: {path}")
    if suffix in {".png", ".pdf"}:
        magic = b"%PDF-" if suffix == ".pdf" else b"\x89PNG\r\n\x1a\n"
        require(item["classification"] == "aggregate_plot" and raw.startswith(magic),
                f"Unapproved binary plot: {path}")
        text = raw.decode("utf-8", errors="ignore")
    else:
        text = raw.decode("utf-8-sig")
    for name, pattern in SECRET_RULES.items():
        require(not pattern.search(text), f"Content rule {name}: {path}")
    require(not ABSOLUTE_PATH.search(text), f"Machine-local path: {path}")
    if suffix in {".csv", ".tsv"}:
        reader = csv.DictReader(io.StringIO(text, newline=""), delimiter="\t" if suffix == ".tsv" else ",")
        rows = list(reader)
        fields = reader.fieldnames or []
        schema = item["aggregate_table"]
        require(len(rows) == schema["rows"] and set(schema["required_keys"]) <= set(fields),
                f"Aggregate table schema/row count mismatch: {path}")
        require(not {f.lower() for f in fields} & (BLOCKED_COLUMNS | {"row_id", "seqn", "source_excel_row"}),
                f"Possible participant table: {path}")
        require(all(None not in row and None not in row.values() for row in rows),
                f"Malformed aggregate table: {path}")
    if suffix == ".json":
        value = json.loads(text)
        if "aggregate_table" in item:
            schema = item["aggregate_table"]
            require(isinstance(value, list) and len(value) == schema["rows"] and
                    all(isinstance(row, dict) and set(schema["required_keys"]) <= set(row) and
                        not {k.lower() for k in row} & (BLOCKED_COLUMNS | {"row_id", "seqn"})
                        for row in value), f"Aggregate JSON schema mismatch: {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True,
                        help="Local parent of biomedical_research; never written into receipts")
    parser.add_argument("--apply", action="store_true", help="Copy only after preflight; default makes no changes")
    args = parser.parse_args(argv)
    workspace = filesystem_root(args.workspace.resolve(strict=True))
    require(workspace != ROOT, "Source and export roots must differ")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, check=True, text=True).stdout.strip()
    require(head == M8_COMMIT, "Export base advanced; review and pin the new snapshot explicitly")
    require(not (ROOT / RECEIPT).exists(), "M10 already finalized; do not overwrite its receipt")
    base_bytes = historical_bytes(ROOT, "sync/EXPORT_MANIFEST.json")
    base = json.loads(base_bytes)
    base_allowlist_bytes = historical_bytes(ROOT, "sync/source_allowlist.json")
    base_allowlist = json.loads(base_allowlist_bytes)
    require((ROOT / "sync/EXPORT_MANIFEST.json").read_bytes() == base_bytes and
            (ROOT / "sync/source_allowlist.json").read_bytes() == base_allowlist_bytes,
            "Current export metadata differs from the pinned M8 snapshot")
    old_records = {r["destination"]: r for r in base["files"]}
    plan_bytes = (ROOT / PLAN).read_bytes()
    plan = json.loads(plan_bytes)
    approved = validate_plan(plan, old_records)
    for record in base["files"]:
        path = under(ROOT, record["destination"])
        require(path.is_file() and digest(path.read_bytes()) == record["export_sha256"],
                f"Existing export changed: {record['destination']}")
    for path in HISTORICAL_LOCAL:
        require((ROOT / path).read_bytes() == historical_bytes(ROOT, path),
                f"Historical milestone artifact changed: {path}")
    prepared = {}
    for path, item in approved.items():
        destination = under(ROOT, path)
        require(path in old_records or not destination.exists(), f"Untracked destination collision: {path}")
        source = under(workspace, item["source"])
        raw = source.read_bytes()
        require(digest(raw) == item["reviewed_sha256"], f"Reviewed source bytes changed: {path}")
        inspect_bytes(item, raw)
        prepared[path] = raw
    items = [approved.get(item["destination"], item) for item in base_allowlist["files"]]
    items.extend(item for path, item in approved.items() if path not in old_records)
    records = [{**item, "source_bytes": len(prepared[item["destination"]]),
                "export_bytes": len(prepared[item["destination"]]),
                "source_sha256": item["reviewed_sha256"], "export_sha256": item["reviewed_sha256"]}
               if item["destination"] in prepared else old_records[item["destination"]] for item in items]
    allowlist = {**base_allowlist, "files": items}
    encode = lambda value: (json.dumps(value, indent=2) + "\n").encode("utf-8")
    allowlist_bytes = encode(allowlist)
    manifest = {**base, "files": records, "source_file_count": len(records),
                "allowlist_sha256": digest(allowlist_bytes)}
    prior = {p: r["export_sha256"] for p, r in old_records.items() if p.startswith(PREFIX)}
    current = {r["destination"]: r["export_sha256"] for r in records if r["destination"].startswith(PREFIX)}
    revised = {p: {"historical_sha256": h, "current_sha256": current[p]}
               for p, h in prior.items() if current[p] != h}
    historical = {p: h for p, h in prior.items() if p not in revised}
    historical.update({p: digest(historical_bytes(ROOT, p)) for p in HISTORICAL_LOCAL})
    nonproject = [r for r in records if not r["destination"].startswith(PREFIX)]
    m8_bytes = historical_bytes(ROOT, "sync/M8_EXPORT_RECEIPT.json")
    m8 = json.loads(m8_bytes)
    precopy = (ROOT / "sync/M10_PRECOPY_REVIEW.json").read_bytes()
    require(json.loads(precopy)["status"] == "passed_after_repair", "Pre-copy content review did not pass")
    receipt = {"schema_version": 1, "milestone": "M10", "base_commit": M8_COMMIT,
               "scope": "Exact reviewed M9 preparation and M10 aggregate inspection archive",
               "previous_export_manifest_sha256": digest(base_bytes), "plan_sha256": digest(plan_bytes),
               "historical_m8_export_receipt_sha256": digest(m8_bytes),
               "precopy_review_sha256": digest(precopy),
               "local_document_revisions": {"README.md": {
                   "historical_sha256": digest(historical_bytes(ROOT, "README.md")),
                   "current_sha256": digest((ROOT / "README.md").read_bytes())}},
               "historical_file_sha256": historical, "revised_project_files": revised,
               "added_project_files": {p: h for p, h in current.items() if p not in prior},
               "curated_export_sha256": current,
               "historical_nonproject_records_preserved": len(nonproject),
               "historical_nonproject_records_sha256": records_digest(nonproject),
               "participant_or_generated_output_rows_exported": False, "experiments_or_tests_rerun": False,
               **{f"historical_m{n}_code_revisions": m8[f"historical_m{n}_code_revisions"] for n in range(2, 7)}}
    for path, raw in prepared.items():
        require(under(workspace, path).read_bytes() == raw, f"Source changed during preflight: {path}")
    require((ROOT / PLAN).read_bytes() == plan_bytes, "Plan changed during preflight")
    if args.apply:
        for path, raw in prepared.items():
            destination = under(ROOT, path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
        (ROOT / "sync/source_allowlist.json").write_bytes(allowlist_bytes)
        (ROOT / "sync/EXPORT_MANIFEST.json").write_bytes(encode(manifest))
        with (ROOT / RECEIPT).open("xb") as stream:
            stream.write(encode(receipt))
    print(json.dumps({"status": "copied_pending_full_audit" if args.apply else "preflight_passed_no_changes",
                      "reviewed_files": len(prepared), "added_project_files": len(receipt["added_project_files"]),
                      "revised_project_files": len(revised), "committed": False, "pushed": False}))


if __name__ == "__main__":
    main()
