"""Check the exact review package, provenance mapping and private-reference exclusions."""
import hashlib
import json
from pathlib import Path
import re

PREFIX = "biomedical_research/three_model_review_2026-10-28/"


def audit_three_model_review(root, source_records, findings):
    package = root / PREFIX
    manifest_path = package / "REVIEW_PACKAGE_MANIFEST.json"
    if not manifest_path.is_file():
        return {"present": False}
    receipt = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = receipt["files"]
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    def check(ok, rule, name="REVIEW_PACKAGE_MANIFEST.json"):
        if not ok:
            findings.append({"file": PREFIX + name, "rule": rule})

    check(len(records) == 16 and len({r["destination"] for r in records}) == 16, "review_exact_file_count")
    actual_sources = {p for p in source_records if p.startswith(PREFIX)}
    check(actual_sources == {r["destination"] for r in records}, "review_exact_source_scope")
    private_ref = re.compile(r"sandbox:/workspace/|(?:[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12})/Pasted text\.txt|[?&]utm_source=")
    for entry in records:
        name = Path(entry["destination"]).name
        official = source_records.get(entry["destination"], {})
        check(all(official.get(k) == v for k, v in entry.items()), "review_source_export_mapping", name)
        check(entry["destination"].startswith(PREFIX) and Path(name).suffix in {".md", ".txt", ".json", ".py"}, "review_file_type", name)
        raw = (root / entry["destination"]).read_bytes()
        check(sha(raw) == entry["export_sha256"] and len(raw) == entry["export_bytes"], "review_hash_mismatch", name)
        check(not private_ref.search(raw.decode("utf-8-sig")), "review_private_reference", name)
    for item in receipt["export_owned_documents"]:
        check(sha((package / item["path"]).read_bytes()) == item["sha256"], "review_readme_hash", item["path"])
    appendix = json.loads((package / "appendix_manifest.json").read_text(encoding="utf-8"))
    check(appendix["commit"] == receipt["frozen_experiment_commit"], "review_snapshot_binding")
    check(sha((package / "IMPLEMENTATION_APPENDIX.txt").read_bytes()) == appendix["appendix_sha256"], "review_appendix_hash")
    check(len(appendix["files"]) == 13, "review_appendix_file_count")
    for entry in appendix["files"]:
        check(sha((root / entry["path"]).read_bytes()) == entry["sha256"], "review_embedded_source_changed")
    by_name = {Path(r["destination"]).name: r for r in records}
    for name in ("GEMINI_REVIEW_USER_SUPPLIED.md", "CLAUDE_REVIEW_USER_SUPPLIED.md"):
        item = by_name[name]
        check(item["source_sha256"] == item["export_sha256"] and item["transform"] == "none", "review_user_response_not_exact", name)
        check(receipt["provider_provenance"][name]["origin"] == "user-supplied complete response", "review_response_provenance", name)
    return {"present": True, "source_files": len(records), "export_bytes": sum(r["export_bytes"] for r in records),
            "normalized_files": sum(r["transform"] != "none" for r in records), "appendix_source_hashes_verified": 13,
            "experiments_rerun": False, "provenance": "provider statements and user-supplied responses; no full browser replay"}
