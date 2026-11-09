"""Prepare a finite public file transport; never upload, alter Git, or copy the bundle.

Run only after the author is closed and publication reports are ready. Default
stdout is metadata. --blob INDEX reads one prepared item; large items require
--chunk N. Source rows, source bodies and raw tool responses are never selected.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import posixpath
import re
import subprocess
from urllib.parse import unquote, urlsplit, urlunsplit

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
MIRROR = PROJECT.parent / "github_virtual_cohort_2026-10-27"
BUNDLE = PROJECT.parents[1] / "evcAdaptiveL01"
UNIT = "adaptive_case_loop_2026-11-09"
PREFIX = "biomedical_research/virtual_cohort_system/"
REPORT = PREFIX + "reports/" + UNIT + "/"
BASE_HEAD = "23b54c66611e9267f1a1b0c4bff7cd2f8969c6e1"

# Every source file is enumerated here or is one of the exact candidate fields
# below. No rglob/glob-based publication and no caller-supplied arbitrary files.
PROJECT_FILES = (
    "cohort_harness/adaptive_session_v1.py", "tests/test_adaptive_session_v1.py",
    "docs/ADAPTIVE_SESSION_V1.md", "README.md",
)
UNIT_REQUIRED = (
    "prepare_public.py", "prepare.py", "generated_analysis.py", "close_author.py",
    "evaluate.py", "evaluate_v2.py", "independent_recompute.py", "plot_results.py",
    "test_generated_analysis.py", "test_evaluate_v2.py", "PROTOCOL.json",
    "EVALUATION_PLAN.md", "EVALUATION_REVIEW_PROTOCOL.md", "DESIGN_LOCK.json",
    "EVALUATOR_AMENDMENT.json", "IMPLEMENTATION_REVIEW.md", "IMPLEMENTATION_REVIEW.json",
    "EVALUATOR_V2_REVIEW.md", "EVALUATOR_V2_REVIEW.json", "CONTROLLER_QA.json",
    "EVALUATION.json", "RESULTS.md", "ACTION_SUMMARY.json", "summarize_actions.py",
    "SOURCE_REVIEW.json", "SOURCE_REVIEW.md", "SOURCE_REVIEW_STAGE2.json", "SOURCE_REVIEW_STAGE2.md",
    "RECOMPUTATION.json", "INDEPENDENT_RESULT_REVIEW.json", "INDEPENDENT_RESULT_REVIEW.md",
    "SESSION_CONFIG.json", "STATE.json",
)
UNIT_OPTIONAL = (
    "RESULTS.json", "RESULTS_ZH.md", "EVALUATION.md", "ACTION_SUMMARY.md",
    "HOST_CLARIFICATION.json", "INDEPENDENT_RECOMPUTE.json", "EVALUATION_INDEPENDENT_CHECK.json",
    "scientific_analyses.png", "scientific_analyses.pdf", "scientific_analyses.svg",
)
CANDIDATE_REQUIRED = ("model_spec.json", "evidence.json", "checks.json", "decision.md",
                      "whole_cohort_feedback.json", "source_semantics_v1.json")
CANDIDATE_OPTIONAL = ("generator.py", "analysis_evidence.json")
BUNDLE_FILES = ("task.json", "request.json")
FORBIDDEN_SUFFIXES = {".csv", ".tsv", ".parquet", ".feather", ".xlsx", ".xls", ".doc", ".docx",
                      ".xml", ".zip", ".sqlite", ".db", ".jsonl"}
SECRET = re.compile(r"(?:\b(?:sk-proj-|sk-|ghp_|github_pat_)[A-Za-z0-9_-]{24,}|"
                    r"\bAKIA[A-Z0-9]{16}\b|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
LINK = re.compile(r"(!?\[[^\]]*\])\((<[^>]+>|[^)]+)\)")
RAW_TEXT_KEYS = {"abstract", "abstracttext", "full_text", "fulltext", "article_body", "paper_text",
                 "raw_text", "raw_response", "raw_retrieval_response", "quotation", "excerpt"}
ROW_KEYS = {"rows", "records", "patients", "participants", "generated_data", "output_rows", "patient_data"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def regular(path):
    if not path.is_file() or any(p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction())
                                 for p in (path, *path.parents)):
        raise ValueError("Missing regular file or linked publication input: " + str(path))
    return path


def read_tree(mirror):
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", "-C", str(mirror), *args])
    head = git("rev-parse", "HEAD").decode().strip()
    if head != BASE_HEAD:
        raise ValueError("Mirror base changed; review a new publication base explicitly")
    if git("status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("Mirror has local changes; this preparation never modifies or cleans it")
    tree = {}
    for entry in git("ls-tree", "-rz", "--full-tree", head).split(b"\0"):
        if entry:
            metadata, name = entry.split(b"\t", 1)
            tree[name.decode()] = metadata.split()[2].decode()
    return tree


def safe_json(value, location="root"):
    if isinstance(value, dict):
        for key, item in value.items():
            lower = str(key).lower()
            if lower in RAW_TEXT_KEYS and item:
                raise ValueError("Raw third-party text/response field is forbidden: " + location + "." + str(key))
            if lower in ROW_KEYS and isinstance(item, list) and item:
                check_records=(lower=='records' and all(isinstance(x,dict) and set(x)=={'name','status','detail'}
                    and x['status'] in {'pass','fail','not_computable'} and all(isinstance(v,str) for v in x.values()) for x in item))
                if not check_records:
                    raise ValueError("Potential individual-record collection is forbidden: " + location + "." + str(key))
            safe_json(item, location + "." + str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            safe_json(item, location + "[" + str(index) + "]")


def inspect_public(path, raw):
    suffix = Path(path).suffix.lower()
    if suffix in FORBIDDEN_SUFFIXES or any(segment in path.split("/") for segment in
                                           ("gateway", "executions", "sources", "author_notes", "private_bundle")):
        raise ValueError("Forbidden public artifact: " + path)
    if len(raw) > 1_500_000:
        raise ValueError("Publication artifact exceeds reviewed size cap: " + path)
    if suffix in {".py", ".md", ".json", ".svg"}:
        text = raw.decode("utf-8-sig")
        if SECRET.search(text):
            raise ValueError("Credential-shaped content requires manual review: " + path)
        if suffix == ".json":
            safe_json(json.loads(text))
        if suffix == ".svg" and re.search(r"<(?:script|foreignObject)\b", text, re.I):
            raise ValueError("Active SVG content is not allowed")
    elif suffix == ".pdf" and not raw.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF header")
    elif suffix == ".png" and not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG header")
    elif suffix not in {".pdf", ".png"}:
        raise ValueError("Unknown public file type: " + path)


def mapping(project, bundle, candidates):
    unit = project / "work" / UNIT
    closed = read_json(regular(unit / "AUTHOR_CLOSED.json"))
    if closed.get("status") != "author_finished_no_further_revision":
        raise ValueError("Author must be closed before public preparation")
    selected = ["candidates/" + name for name in candidates]
    if not candidates or len(candidates) > 3 or len(set(candidates)) != len(candidates):
        raise ValueError("Explicitly select one to three distinct candidate names")
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name) for name in candidates):
        raise ValueError("Unsafe candidate name")
    if selected != closed.get("candidates"):
        raise ValueError("Publish every submitted stage in its sealed order, not a favorable subset")
    selected_files = {}
    for name in PROJECT_FILES:
        selected_files[PREFIX + name] = regular(project / name)
    selected_files["README.md"] = regular(project / "README.md")
    for name in UNIT_REQUIRED:
        selected_files[REPORT + name] = regular(unit / name)
    for name in UNIT_OPTIONAL:
        if (unit / name).is_file():
            selected_files[REPORT + name] = regular(unit / name)
    for name in BUNDLE_FILES:
        selected_files[REPORT + "author_context/" + name] = regular(bundle / name)
    for candidate in selected:
        for name in CANDIDATE_REQUIRED:
            selected_files[REPORT + candidate + "/" + name] = regular(bundle / candidate / name)
        for name in CANDIDATE_OPTIONAL:
            if (bundle / candidate / name).is_file():
                selected_files[REPORT + candidate + "/" + name] = regular(bundle / candidate / name)
        # Direct-row routes remain legitimate but their rows are deliberately absent.
        route_count = sum((bundle / candidate / name).is_file() for name in ("generator.py", "generated.csv"))
        if route_count != 1:
            raise ValueError("Candidate route is ambiguous")
    for public, local in selected_files.items():
        if local.is_relative_to(bundle):
            name = local.relative_to(bundle).as_posix()
            if sha(local.read_bytes()) != closed["files"].get(name):
                raise ValueError("Author artifact differs from closure: " + name)
    return selected_files, closed


def rewrite_markdown(raw, source, destination, selected_files, available, project, bundle, rewrites, checked):
    reverse = {str(local.resolve()).casefold(): public for public, local in selected_files.items()}
    # Prefer the nested project README for links originating inside the project.
    reverse[str((project / "README.md").resolve()).casefold()] = PREFIX + "README.md"
    def resolve(match):
        label, href = match.groups()
        href = href.strip("<>")
        url = urlsplit(href)
        if url.scheme in {"https", "http", "mailto"} or href.startswith("#"):
            return match[0]
        windows_absolute=bool(re.match(r'^[A-Za-z]:[/\\]',href))
        if windows_absolute:
            target_local=Path(unquote(href.split('#',1)[0].split('?',1)[0])).resolve()
            if str(target_local).casefold() not in reverse:
                raise ValueError('Absolute link is not a selected public artifact: '+href)
        elif url.scheme or url.netloc or url.path.startswith(("/", "\\")):
            raise ValueError("Absolute/private Markdown link must be replaced before publication: " + href)
        else:
            target_local = (source.parent / unquote(url.path)).resolve()
        target = reverse.get(str(target_local).casefold())
        if target is None and target_local.is_relative_to(project):
            relative = target_local.relative_to(project).as_posix()
            target = PREFIX + ("reports/" + relative[5:] if relative.startswith("work/") else relative)
        if target is None or (target not in available and not any(p.startswith(target.rstrip("/") + "/") for p in available)):
            raise ValueError("Unpublished/private Markdown link in " + destination + ": " + href)
        checked.append({"file": destination, "target": target})
        relative = posixpath.relpath(target, posixpath.dirname(destination) or ".")
        updated = urlunsplit(("", "", relative, url.query, url.fragment))
        if updated != href:
            rewrites.append({"file": destination, "old": href, "new": updated})
        return label + "(" + ("<" + updated + ">" if " " in updated else updated) + ")"
    return LINK.sub(resolve, raw.decode("utf-8-sig")).encode("utf-8")


def acquisition_metadata(bundle, closed):
    path = regular(bundle / "registry.json")
    raw = path.read_bytes()
    if sha(raw) != closed["files"].get("registry.json"):
        raise ValueError("Source registry differs from author closure")
    registry = json.loads(raw)
    artifacts = []
    for item in registry["artifacts"]:
        if set(item) != {"source_id", "path", "sha256", "origin", "screening"}:
            raise ValueError("Unexpected registry schema")
        artifacts.append({"source_id": item["source_id"], "content_sha256": item["sha256"],
                          "format": Path(item["path"]).suffix.lower(), "origin": item["origin"],
                          "screening": item["screening"], "source_bytes_published": False})
    return {"schema_version": 1, "scope": "Acquisition metadata only; no source text, abstract or source table copied.",
            "registry_sha256": sha(raw), "artifacts": artifacts,
            "original_structured_facts": "Author evidence.json contains original structured scientific fact records needed to inspect each model; underlying curator/full-text artifacts remain local."}


def prepare(project, mirror, bundle, candidates, output):
    project, mirror, bundle, output = (p.resolve() for p in (project, mirror, bundle, output))
    if output.exists():
        raise ValueError("Output already exists; choose a fresh --output directory")
    if not output.parent.is_dir() or not output.is_relative_to(project / "work" / UNIT):
        raise ValueError("Transport output must be a new directory inside the publication work unit")
    tree = read_tree(mirror)
    selected, closed = mapping(project, bundle, candidates)
    derived_names = {REPORT + n for n in ("ACQUISITION_METADATA.json", "AUTHOR_CLOSED_PUBLIC.json",
                                           "PUBLICATION_MANIFEST.json", "PUBLICATION_QA.json")}
    available = set(tree) | set(selected) | derived_names
    payload, records, rewrites, checked = {}, [], [], []
    for destination, source in selected.items():
        raw = source.read_bytes()
        public = rewrite_markdown(raw, source, destination, selected, available, project, bundle, rewrites, checked) if source.suffix.lower() == ".md" else raw
        inspect_public(destination, public)
        source_label = ("bundle/" + source.relative_to(bundle).as_posix()) if source.is_relative_to(bundle) else source.relative_to(project).as_posix()
        payload[destination] = public
        records.append({"path": destination, "local_source": source_label, "local_sha256": sha(raw),
                        "public_sha256": sha(public), "bytes": len(public), "git_blob_sha": git_blob(public),
                        "base_git_blob_sha": tree.get(destination), "same_as_base": tree.get(destination) == git_blob(public)})
    public_closed = {key: closed[key] for key in ("status", "final_candidate", "reason", "candidates", "runs")}
    public_closed["scope"] = "Selection and schedule metadata only; the complete private-bundle inventory is not published."
    derived = {"ACQUISITION_METADATA.json": acquisition_metadata(bundle, closed), "AUTHOR_CLOSED_PUBLIC.json": public_closed}
    for name, value in derived.items():
        destination, raw = REPORT + name, encoded(value)
        inspect_public(destination, raw)
        payload[destination] = raw
        records.append({"path": destination, "local_source": "derived_metadata_only", "local_sha256": None,
                        "public_sha256": sha(raw), "bytes": len(raw), "git_blob_sha": git_blob(raw),
                        "base_git_blob_sha": tree.get(destination), "same_as_base": tree.get(destination) == git_blob(raw)})
    qa = {"schema_version": 1, "status": "finite_allowlist_checks_passed", "base_head": BASE_HEAD,
          "selected_candidates": candidates, "all_sealed_stages_included": True,
          "local_rows_source_bodies_and_raw_responses_selected": False,
          "mirror_modified": False, "remote_access_or_upload_performed": False,
          "markdown_links_checked": len(checked), "markdown_rewrites": rewrites,
          "checks": ["exact filename allowlists", "sealed author artifact hashes", "full submitted-stage selection",
                     "forbidden extension/path checks", "credential-pattern scan", "raw-text/individual-collection JSON key checks",
                     "figure signatures and size caps", "Markdown links resolve to planned files or immutable base tree"],
          "limitations": ["Structural export checks are not semantic certification that every prose statement is accurate.",
                          "No original source or local dataset bytes are redistributed; reproduction requires authorized local inputs.",
                          "Source-code paths are preserved; report links alone are rewritten from work/ to reports/."]}
    public_manifest = {"schema_version": 1, "base_head": BASE_HEAD, "files": records,
                       "scope": "Local/public SHA mapping for selected original artifacts and derived metadata. This manifest and its companion QA are omitted from their own hash list to avoid circular commitments."}
    payload[REPORT + "PUBLICATION_MANIFEST.json"] = encoded(public_manifest)
    payload[REPORT + "PUBLICATION_QA.json"] = encoded(qa)
    for destination in (REPORT + "PUBLICATION_MANIFEST.json", REPORT + "PUBLICATION_QA.json"):
        raw = payload[destination]
        inspect_public(destination, raw)
        records.append({"path": destination, "local_source": "derived_publication_record", "local_sha256": None,
                        "public_sha256": sha(raw), "bytes": len(raw), "git_blob_sha": git_blob(raw),
                        "base_git_blob_sha": tree.get(destination), "same_as_base": tree.get(destination) == git_blob(raw)})
    blobs = [{"index": index, "path": path, "git_blob_sha": git_blob(raw), "public_sha256": sha(raw),
              "bytes": len(raw), "mode": "100644", "type": "blob", "encoding": "base64",
              "content": base64.b64encode(raw).decode("ascii")}
             for index, (path, raw) in enumerate((p, b) for p, b in sorted(payload.items()) if tree.get(p) != git_blob(b))]
    transport = {"schema_version": 1, "base_head": BASE_HEAD, "files": blobs}
    transport_raw = encoded(transport)
    manifest = {"schema_version": 1, "status": "prepared_not_uploaded", "base_head": BASE_HEAD,
                "files": records, "transport_files": [{k: v for k, v in b.items() if k != "content"} for b in blobs],
                "transport_sha256": sha(transport_raw), "planned_files": len(payload), "changed_files": len(blobs),
                "total_changed_bytes": sum(b["bytes"] for b in blobs), "markdown_rewrites": rewrites,
                "instructions": "Use --blob INDEX, or --blob INDEX --chunk N for large items; reassemble base64 chunks before creating a Git blob. Upload only after explicit publication authorization and a fresh remote-head check."}
    # No mirror copy, Git mutation, network request or source modification occurs.
    output.mkdir()
    for name, raw in (("TRANSPORT.json", transport_raw), ("PUBLIC_MANIFEST.json", encoded(manifest)), ("ALLOWLIST_QA.json", encoded(qa))):
        with (output / name).open("xb") as out:
            out.write(raw)
    return {"status": manifest["status"], "base_head": BASE_HEAD, "output": str(output),
            "planned_files": len(payload), "changed_files": len(blobs), "total_changed_bytes": manifest["total_changed_bytes"],
            "transport_sha256": manifest["transport_sha256"]}


def read_blob(output, index, chunk=None, chunk_chars=48000):
    manifest = read_json(regular(output / "PUBLIC_MANIFEST.json"))
    raw = regular(output / "TRANSPORT.json").read_bytes()
    if sha(raw) != manifest["transport_sha256"]:
        raise ValueError("Prepared transport changed")
    transport = json.loads(raw)
    if type(index) is not int or not 0 <= index < len(transport["files"]):
        raise ValueError("Blob index is outside transport")
    item = transport["files"][index]
    decoded = base64.b64decode(item["content"], validate=True)
    if git_blob(decoded) != item["git_blob_sha"] or sha(decoded) != item["public_sha256"]:
        raise ValueError("Blob bytes no longer match prepared hashes")
    if chunk is None:
        if len(item["content"]) > 120000:
            raise ValueError("Large blob: use --chunk 0, --chunk 1, ...; default chunk size is 48000 base64 characters")
        return item
    if chunk < 0 or not 4 <= chunk_chars <= 96000 or chunk_chars % 4:
        raise ValueError("Chunk index must be nonnegative; chunk size must be 4..96000 and divisible by four")
    start, end = chunk * chunk_chars, (chunk + 1) * chunk_chars
    if start >= len(item["content"]):
        raise ValueError("Chunk index is outside blob")
    return {**{k: v for k, v in item.items() if k != "content"}, "encoding": "base64_fragment",
            "chunk": chunk, "chunk_count": (len(item["content"]) + chunk_chars - 1) // chunk_chars,
            "base64_offset": start, "base64_total_chars": len(item["content"]), "content": item["content"][start:end]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--mirror", type=Path, default=MIRROR)
    parser.add_argument("--bundle", type=Path, default=BUNDLE)
    parser.add_argument("--output", type=Path, default=HERE / "publication_transport")
    parser.add_argument("--candidate", action="append", default=[])
    parser.add_argument("--blob", type=int)
    parser.add_argument("--chunk", type=int)
    parser.add_argument("--chunk-chars", type=int, default=48000)
    args = parser.parse_args(argv)
    result = read_blob(args.output, args.blob, args.chunk, args.chunk_chars) if args.blob is not None else prepare(
        args.project, args.mirror, args.bundle, args.candidate, args.output)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
