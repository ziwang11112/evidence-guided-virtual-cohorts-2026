"""Refresh only a reviewed exact-path allowlist. Never upload or push anything."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "sync/source_allowlist.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def under(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("Only repository-relative paths are allowed")
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Path escapes declared root")
    return path


def normalize_review(value, workspace):
    if isinstance(value, dict):
        return {normalize_review(k, workspace): normalize_review(v, workspace) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_review(v, workspace) for v in value]
    if isinstance(value, str):
        portable = value.replace("\\", "/")
        prefix = workspace.as_posix().rstrip("/") + "/"
        if portable.lower().startswith(prefix.lower()):
            return portable[len(prefix):]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--only-source", action="append", help="Refresh this exact allowlisted source path only; repeat as needed")
    args = parser.parse_args()
    workspace = args.workspace.resolve(strict=True)
    if workspace == ROOT:
        raise ValueError("Source workspace must differ from export root")
    allowlist_bytes = ALLOWLIST.read_bytes()
    items = json.loads(allowlist_bytes)["files"]
    destinations = [item["destination"] for item in items]
    if len(destinations) != len(set(destinations)):
        raise ValueError("Duplicate destination")
    selected = set(args.only_source or (item["source"] for item in items))
    if not selected.issubset({item["source"] for item in items}):
        raise ValueError("Requested source is not an exact allowlist entry")
    previous = {}
    if args.only_source:
        previous = {r["destination"]: r for r in json.loads((ROOT / "sync/EXPORT_MANIFEST.json").read_text(encoding="utf-8"))["files"]}
    prepared = []
    for item in items:
        if item["source"] not in selected:
            old = previous.get(item["destination"])
            if old is None or any(old.get(k) != v for k, v in item.items()) or sha(under(ROOT, item["destination"]).read_bytes()) != old["export_sha256"]:
                raise ValueError(f"Unselected allowlist/export changed: {item['destination']}")
            continue
        source = under(workspace, item["source"])
        destination = under(ROOT, item["destination"])
        raw = source.read_bytes()
        if item.get("reviewed_sha256") and sha(raw) != item["reviewed_sha256"]:
            raise ValueError(f"Source changed since content review: {item['source']}")
        if item.get("required_candidate_manifest"):
            candidate_path = under(workspace, item["required_candidate_manifest"])
            candidate = json.loads(candidate_path.read_text(encoding="utf-8-sig"))
            key = source.relative_to(candidate_path.parent).as_posix()
            if candidate["files"].get(key) != sha(raw):
                raise ValueError(f"Candidate commitment mismatch: {item['source']}")
        if item["transform"] == "none":
            exported = raw
        elif item["transform"] == "normalize_review_workspace_paths":
            obj = normalize_review(json.loads(raw.decode("utf-8-sig")), workspace)
            exported = (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        elif item["transform"] == "normalize_workspace_paths_text":
            text = raw.decode("utf-8-sig")
            for prefix in (str(workspace).rstrip("\\/") + "\\", workspace.as_posix().rstrip("/") + "/"):
                text = text.replace(prefix, "")
            exported = text.encode("utf-8")
        elif item["transform"] == "normalize_python_runtime_command":
            text, count = re.subn(r"[A-Za-z]:[\\/]Users[\\/][^ \t\r\n`'\"]+[\\/]python\.exe", "python", raw.decode("utf-8-sig"), flags=re.I)
            if count != item["runtime_paths_replaced"]:
                raise ValueError("Unexpected local runtime command count")
            exported = text.encode("utf-8")
        else:
            raise ValueError("Unknown reviewed transformation")
        prepared.append((item, source, destination, raw, exported))
    updated = {}
    for item, source, destination, raw, exported in prepared:
        # Detect source edits during preparation; never silently mix snapshots.
        if source.read_bytes() != raw:
            raise ValueError(f"Source changed during refresh: {item['source']}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(exported)
        updated[item["destination"]] = {**item, "source_bytes": len(raw), "export_bytes": len(exported),
                                       "source_sha256": sha(raw), "export_sha256": sha(exported)}
    records = [updated[item["destination"]] if item["destination"] in updated else previous[item["destination"]] for item in items]
    manifest = {"schema_version": 1, "allowlist_sha256": sha(allowlist_bytes),
                "source_file_count": len(records), "source_workspace": "supplied locally; intentionally not recorded",
                "scope": "Sanitized code and aggregate evidence export; full clinical replay is not self-contained",
                "files": records}
    (ROOT / "sync/EXPORT_MANIFEST.json").write_bytes((json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"copied_reviewed_files": len(updated), "total_source_files": len(records), "export_bytes": sum(r['export_bytes'] for r in records)}))


if __name__ == "__main__":
    main()
