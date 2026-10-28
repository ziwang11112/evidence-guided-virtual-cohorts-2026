"""Refresh only a reviewed exact-path allowlist. Never upload or push anything."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

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


def normalize_provider_review(raw, item):
    """Change reviewed transport references only; preserve response prose."""
    text = raw.decode("utf-8")
    counts = {"temporary_attachment_links_replaced": 0,
              "utm_source_parameters_removed": 0,
              "local_attachment_references_replaced": 0}
    text, counts["temporary_attachment_links_replaced"] = re.subn(
        r"sandbox:/workspace/scratch/[A-Za-z0-9_-]+/upload/(REVIEW_BRIEF\.txt|IMPLEMENTATION_APPENDIX\.txt)",
        lambda match: match.group(1), text)

    def strip_tracking(match):
        url = match.group(0)
        parsed = urlsplit(url)
        if not parsed.query:
            return url
        pairs = parsed.query.split("&")
        kept = [pair for pair in pairs if not pair.lower().startswith("utm_source=")]
        counts["utm_source_parameters_removed"] += len(pairs) - len(kept)
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "&".join(kept), parsed.fragment))

    text = re.sub(r'https?://[^\s<>\]\)"`]+', strip_tracking, text)
    target = item.get("attachment_reference_target")
    if target:
        if target not in {"GEMINI_REVIEW_USER_SUPPLIED.md", "CLAUDE_REVIEW_USER_SUPPLIED.md"}:
            raise ValueError("Unexpected reviewed attachment target")
        uuid = r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}"
        attachment_prefix = r"(?:[A-Za-z]:/" + "/".join(("Codex", "home", "attachments")) + r"/)?"
        text, counts["local_attachment_references_replaced"] = re.subn(
            attachment_prefix + uuid + r"/Pasted text\.txt", target, text)
    if counts != item["review_reference_counts"]:
        raise ValueError("Unexpected provider review reference counts")
    return text.encode("utf-8")


def normalize_explorer_runtime_references(raw, item):
    """Normalize reviewed GUI/QA setup references, without changing validated harness code."""
    text = raw.decode("utf-8")
    if item["source"].endswith("/diagram-build-notes.md"):
        text, count = re.subn(r"found at `[A-Za-z]:[/]Users[/][^`]+/draw\.io\.exe`",
                             "using a local `draw.io` executable (machine-local path omitted in export)", text)
        expected = 1
    elif item["source"].endswith("/verify_explorer.cjs"):
        text, count = re.subn(r"require\('[A-Za-z]:[/]Users[/][^']+/node_modules/playwright'\)",
                             "require('playwright')", text)
        text, chrome_count = re.subn(r"executablePath:'[A-Za-z]:/Program Files/Google/Chrome/Application/chrome\.exe'",
                                    "...(process.env.CHROME_EXECUTABLE_PATH ? {executablePath:process.env.CHROME_EXECUTABLE_PATH} : {channel:'chrome'})", text)
        count += chrome_count
        expected = 2
    else:
        raise ValueError("Unexpected explorer normalization target")
    if count != expected or count != item["runtime_references_replaced"]:
        raise ValueError("Unexpected explorer runtime reference count")
    return text.encode("utf-8")


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
        elif item["transform"] == "normalize_explorer_runtime_references":
            exported = normalize_explorer_runtime_references(raw, item)
        elif item["transform"] == "normalize_provider_review_references":
            exported = normalize_provider_review(raw, item)
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
        elif item["transform"] == "normalize_python_runtime_metadata":
            obj = json.loads(raw.decode("utf-8-sig"))
            executable = obj.get("python_executable", "")
            if not re.fullmatch(r"[A-Za-z]:[\\/]Users[\\/].+[\\/]python\.exe", executable, flags=re.I):
                raise ValueError("Unexpected runtime executable metadata")
            obj["python_executable"] = "python"
            exported = (json.dumps(obj, indent=2) + "\n").encode("utf-8")
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
