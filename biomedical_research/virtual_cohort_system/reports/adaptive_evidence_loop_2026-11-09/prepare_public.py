"""Finite postclosure public transport. No upload, Git mutation or bundle write.

Exact file lists only. Default output is metadata; --blob INDEX --chunk N
returns bounded base64 for a reviewed tool transport, never raw source bodies.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import posixpath
import re
import subprocess
from urllib.parse import unquote, urlsplit, urlunsplit

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
MIRROR = PROJECT.parent / "github_virtual_cohort_2026-10-27"
BUNDLE = PROJECT.parents[1] / "evcAdaptiveL02"
UNIT = "adaptive_evidence_loop_2026-11-09"
PREFIX = "biomedical_research/virtual_cohort_system/"
REPORT = PREFIX + "reports/" + UNIT + "/"
BASE_HEAD = "2d20ec13e6edb1f67bc7230eeeb3de56bbf73382"
PROJECT_FILES = (
    "cohort_harness/adaptive_session_v2.py", "cohort_harness/descriptive_feedback_v1.py",
    "cohort_harness/web_evidence_v1.py", "docs/ADAPTIVE_SESSION_V2.md",
    "docs/DESCRIPTIVE_FEEDBACK_V1.md", "docs/WEB_EVIDENCE_V1.md",
    "tests/test_adaptive_session_v2.py", "tests/test_descriptive_feedback_v1.py",
    "tests/test_web_evidence_v1.py",
)
UNIT_REQUIRED = (
    "prepare_public.py", "test_prepare_public.py", "prepare.py", "generated_analysis.py",
    "close_author.py", "evaluate.py", "independent_recompute.py", "plot_results.py",
    "summarize_actions.py", "compare_previous.py", "test_evaluate.py", "test_generated_analysis.py",
    "EVALUATION_PLAN.md", "PROTOCOL_REVIEW_DRAFT.md", "IMPLEMENTATION_REPORT.json",
    "IMPLEMENTATION_REVIEW.md", "IMPLEMENTATION_REVIEW.json", "DESIGN_LOCK.json",
    "EXPORTER_REVIEW.md", "EXPORTER_REVIEW.json",
    "PUBLIC_ALLOWLIST_DRAFT.md", "PUBLIC_ALLOWLIST_DRAFT.json",
    "EVALUATION.json", "EVALUATION.md", "RECOMPUTATION.json", "RESULTS.md",
    "ACTION_SUMMARY.json", "PREVIOUS_COMPARISON.json", "SOURCE_REVIEW.json", "SOURCE_REVIEW.md",
    "INDEPENDENT_RESULT_REVIEW.json", "INDEPENDENT_RESULT_REVIEW.md",
    "scientific_analyses.png", "scientific_analyses.pdf",
)
RESEARCH_UNIT = "retrieval_validation_analysis_2026-11-09"
RESEARCH_FILES = ("LOCAL_CHECK_AUDIT.md", "OFFICIAL_KNOWLEDGE.md",
                  "PUBLISHED_VALIDATION_PATTERNS.md", "RECOMMENDATIONS.md")
DERIVED_NAMES = ("PROTOCOL_PUBLIC.json", "AUTHOR_CLOSED_PUBLIC.json", "ACQUISITION_METADATA.json",
                 "PUBLICATION_MANIFEST.json", "PUBLICATION_QA.json")
FORBIDDEN_SUFFIXES = {".csv", ".tsv", ".parquet", ".feather", ".xlsx", ".xls", ".doc", ".docx",
                      ".xml", ".zip", ".sqlite", ".db", ".jsonl", ".raw", ".txt"}
SECRET = re.compile(r"(?:\b(?:sk-proj-|sk-|ghp_|github_pat_)[A-Za-z0-9_-]{24,}|"
                    r"\bAKIA[A-Z0-9]{16}\b|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
LINK = re.compile(r"(!?\[[^\]]*\])\((<[^>]+>|[^)]+)\)")
REFERENCE_LINK = re.compile(r"(?m)^(\s*\[[^\]]+\]:\s*)(<[^>]+>|\S+)(\s*)$")
RAW_TEXT_KEYS = {"abstract", "abstracttext", "full_text", "fulltext", "article_body", "paper_text",
                 "raw_text", "raw_response", "raw_retrieval_response", "quotation", "excerpt",
                 "snippet", "source_body", "extracted_text"}
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

def aggregate_verification_records(value, location, public_path):
    """One reviewed report schema; never a generic exception for record lists."""
    if (public_path != REPORT + "INDEPENDENT_RESULT_REVIEW.json"
            or location != "root.additional_independent_row_checks"
            or set(value) != {"method", "checks", "maximum_absolute_difference", "records"}):
        return False
    records = value["records"]
    finite = lambda x: type(x) in {int, float} and math.isfinite(x)
    if (not isinstance(value["method"], str) or not value["method"].strip()
            or type(value["checks"]) is not int or value["checks"] != len(records)
            or not 1 <= len(records) <= 30
            or not finite(value["maximum_absolute_difference"]) or value["maximum_absolute_difference"] < 0):
        return False
    endpoints = {"K02-TC-BMI", "K02-HDL-BMI", "K02-LIPID-RESIDUAL",
                 "total_cholesterol.sd_sample", "hdl_cholesterol.sd_sample"}
    seen = set()
    for record in records:
        if (not isinstance(record, dict)
                or set(record) != {"run_id", "endpoint", "recomputed", "reported", "absolute_difference"}
                or not isinstance(record["run_id"], str)
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", record["run_id"])
                or not isinstance(record["endpoint"], str) or record["endpoint"] not in endpoints
                or any(not finite(record[k]) for k in ("recomputed", "reported", "absolute_difference"))
                or record["absolute_difference"] < 0):
            return False
        key = (record["run_id"], record["endpoint"])
        if key in seen:
            return False
        seen.add(key)
    return value["maximum_absolute_difference"] == max(r["absolute_difference"] for r in records)


def safe_json(value, location="root", public_path=None):
    if isinstance(value, dict):
        for key, item in value.items():
            lower = str(key).lower()
            if lower in RAW_TEXT_KEYS and item:
                raise ValueError("Raw third-party text/response field is forbidden: " + location + "." + str(key))
            if lower in ROW_KEYS and isinstance(item, list) and item:
                check_records=(lower=='records' and all(isinstance(x,dict) and set(x)=={'name','status','detail'}
                    and x['status'] in {'pass','fail','not_computable'} and all(isinstance(v,str) for v in x.values()) for x in item))
                aggregate_records = lower == "records" and aggregate_verification_records(value, location, public_path)
                if not check_records and not aggregate_records:
                    raise ValueError("Potential individual-record collection is forbidden: " + location + "." + str(key))
            safe_json(item, location + "." + str(key), public_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            safe_json(item, location + "[" + str(index) + "]", public_path)

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
            safe_json(json.loads(text), public_path=path)
        if suffix == ".svg" and re.search(r"<(?:script|foreignObject)\b", text, re.I):
            raise ValueError("Active SVG content is not allowed")
    elif suffix == ".pdf" and not raw.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF header")
    elif suffix == ".png" and not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG header")
    elif suffix not in {".pdf", ".png"}:
        raise ValueError("Unknown public file type: " + path)


def child(root, relative):
    if not isinstance(relative, str) or not relative or any(
            part in {"", ".", ".."} or any(c in part for c in "\\:\x00")
            for part in relative.split("/")):
        raise ValueError("Unsafe relative artifact path")
    path = root.joinpath(*relative.split("/"))
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Artifact escapes its root")
    return regular(path)


def closure_gate(project, bundle):
    """Read commitments and aggregate reports only; never import an author program."""
    unit = project / "work" / UNIT
    closure = read_json(regular(unit / "AUTHOR_CLOSED.json"))
    protocol = read_json(regular(unit / "PROTOCOL.json"))
    if closure.get("status") != "author_finished_no_further_revision":
        raise ValueError("Author must be closed before publication preparation")
    if Path(closure["bundle"]).resolve() != bundle or Path(protocol["bundle"]).resolve() != bundle:
        raise ValueError("Protocol/closure bundle mismatch")
    for relative, expected in read_json(regular(unit / "DESIGN_LOCK.json")).items():
        if sha(child(unit, relative).read_bytes()) != expected:
            raise ValueError("Locked design changed: " + relative)
    actual = set()
    for path in bundle.rglob("*"):
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise ValueError("Linked closed artifact")
        if path.is_file():
            actual.add(path.relative_to(bundle).as_posix())
    if actual != set(closure["files"]):
        raise ValueError("Closed bundle inventory changed")
    for relative, expected in closure["files"].items():
        if sha(child(bundle, relative).read_bytes()) != expected:
            raise ValueError("Closed artifact changed: " + relative)
    summary = closure["session"]
    if summary["status"] != "completed" or summary["pending"] is not None:
        raise ValueError("Closed session was not completed")
    if summary["candidates"] != closure["candidates"] or closure["final_candidate"] not in closure["candidates"]:
        raise ValueError("Closed candidate selection differs")
    slots = closure["execution_slots"]
    expected_slots = {(c, s) for c in closure["candidates"] for s in protocol["seeds"]}
    if len(slots) != len(expected_slots) or {(s["candidate"], s["seed"]) for s in slots} != expected_slots:
        raise ValueError("Closed execution schedule differs")
    if len(set(closure["runs"])) != len(slots) or set(closure["runs"]) != {s["run_id"] for s in slots}:
        raise ValueError("Closed run inventory differs")
    evaluation = read_json(regular(unit / "EVALUATION.json"))
    closure_hash = sha((unit / "AUTHOR_CLOSED.json").read_bytes())
    if evaluation["closure_sha256"] != closure_hash:
        raise ValueError("Evaluation closure binding differs")
    runs = evaluation["runs"]
    if (len(runs) != len(slots) or {r["run_id"] for r in runs} != set(closure["runs"])
            or {(r["candidate"], r["seed"]) for r in runs} != expected_slots):
        raise ValueError("Evaluation omitted, added or duplicated a scheduled run")
    if [s["candidate"] for s in evaluation["stages"]] != closure["candidates"]:
        raise ValueError("Evaluation stage coverage differs")
    if [s["candidate"] for s in evaluation["stages"] if s["selected_final"]] != [closure["final_candidate"]]:
        raise ValueError("Evaluation selection differs")
    recomputation = read_json(regular(unit / "RECOMPUTATION.json"))
    if (recomputation["closure_sha256"] != closure_hash
            or recomputation["evaluation_sha256"] != sha((unit / "EVALUATION.json").read_bytes())
            or type(recomputation["checks"]) is not int or recomputation["checks"] <= 0
            or recomputation["passed"] != recomputation["checks"]):
        raise ValueError("Independent recomputation is absent, stale or unsuccessful")
    return closure, protocol


def mapping(project):
    selected = {PREFIX + name: regular(project / name) for name in PROJECT_FILES}
    selected.update({REPORT + name: regular(project / "work" / UNIT / name) for name in UNIT_REQUIRED})
    selected.update({PREFIX + "reports/" + RESEARCH_UNIT + "/" + name:
                     regular(project / "work" / RESEARCH_UNIT / name) for name in RESEARCH_FILES})
    return selected


def public_url(value):
    parts = urlsplit(value)
    if parts.scheme not in {"https", "http"} or not parts.hostname or parts.username or parts.password:
        raise ValueError("Not a public HTTP(S) URL")
    if SECRET.search(value) or re.search(r"(?:^|[&;])(?:access_token|api_key|password|secret|signature|authorization|token)=", parts.query, re.I):
        raise ValueError("Credential-shaped URL")
    # Acquisition metadata deliberately omits arbitrary query strings/fragments.
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def rewrite_markdown(raw, source, destination, selected, available, project, rewrites, checked):
    reverse = {str(local.resolve()).casefold(): public for public, local in selected.items()}
    reverse[str((project / "work" / UNIT / "PROTOCOL.json").resolve()).casefold()] = REPORT + "PROTOCOL_PUBLIC.json"
    reverse[str((project / "work" / UNIT / "AUTHOR_CLOSED.json").resolve()).casefold()] = REPORT + "AUTHOR_CLOSED_PUBLIC.json"
    old_bundle = project.parents[1] / "evcAdaptiveL01"
    old_report = PREFIX + "reports/adaptive_case_loop_2026-11-09/"
    aliases = {"candidates/initial/source_semantics_v1.json": "candidates/initial/source_semantics_v1.json",
               "candidates/initial/whole_cohort_feedback.json": "candidates/initial/whole_cohort_feedback.json",
               "gateway/session/state.json": "ACTION_SUMMARY.json"}
    for local, public in aliases.items():
        reverse[str((old_bundle / local).resolve()).casefold()] = old_report + public
    accounting_key = str((old_bundle / "gateway/session/state.json").resolve()).casefold()
    label_overrides = {}
    text = raw.decode("utf-8-sig")
    if re.search(r"<(?:a|img|iframe|script)\b", text, re.I):
        raise ValueError("Raw HTML links/media require explicit public review")

    def resolve(href):
        original = href
        href = href.strip("<>")
        url = urlsplit(href)
        if href.startswith("#"):
            return original
        if url.scheme in {"https", "http"}:
            public_url(href)
            checked.append({"file": destination, "external_link": href})
            return original
        if url.scheme == "mailto":
            raise ValueError("Email link requires explicit publication review")
        local_path = unquote(url.path)
        fragment = url.fragment
        windows_absolute = bool(re.match(r"^[A-Za-z]:[/\\]", href))
        if windows_absolute:
            local_path = unquote(href.split("#", 1)[0].split("?", 1)[0])
        elif url.scheme == "file":
            if url.netloc:
                raise ValueError("Network file link is not public")
            if re.match(r"^/[A-Za-z]:/", local_path):
                local_path = local_path[1:]
        elif url.scheme or url.netloc:
            raise ValueError("Unsupported/private Markdown URI: " + href)
        line = re.search(r":([1-9][0-9]*)$", local_path)
        if line:
            local_path = local_path[:line.start()]
            fragment = fragment or "L" + line[1]
        target_local = Path(local_path)
        if not target_local.is_absolute():
            target_local = source.parent / target_local
        target_local = target_local.resolve()
        local_key = str(target_local).casefold()
        target = reverse.get(local_key)
        if target is None and target_local.is_relative_to(project):
            relative = target_local.relative_to(project).as_posix()
            target = PREFIX + ("reports/" + relative[5:] if relative.startswith("work/") else relative)
        if target is None or (target not in available and not any(x.startswith(target.rstrip("/") + "/") for x in available)):
            raise ValueError("Unpublished/private Markdown link in " + destination + ": " + href)
        checked.append({"file": destination, "target": target})
        updated = urlunsplit(("", "", posixpath.relpath(target, posixpath.dirname(destination)), "", fragment))
        if updated != href:
            rewrites.append({"file": destination, "target": target, "public_link": updated})
            if local_key == accounting_key:
                rewrites[-1]["projection"] = "Public accounting summary replaces private state link; not identical source bytes."
                label_overrides[original] = "[public acquisition summary (local state not redistributed)]"
        return "<" + updated + ">" if " " in updated else updated

    def inline(match):
        href = resolve(match[2])
        return label_overrides.get(match[2], match[1]) + "(" + href + ")"
    text = LINK.sub(inline, text)
    text = REFERENCE_LINK.sub(lambda m: m[1] + resolve(m[2]) + m[3], text)
    if label_overrides:
        text += "\n\nPublic link note: the acquisition-summary link is a public projection; the original local gateway state is not redistributed.\n"
    return text.encode("utf-8")


def acquisition_metadata(bundle, closure):
    registry_path = child(bundle, "registry.json")
    if sha(registry_path.read_bytes()) != closure["files"].get("registry.json"):
        raise ValueError("Source registry differs from closure")
    artifacts = []
    for item in read_json(registry_path)["artifacts"]:
        if set(item) != {"source_id", "path", "sha256", "origin", "screening"}:
            raise ValueError("Unexpected registry schema")
        artifacts.append({"source_id": item["source_id"], "content_sha256": item["sha256"],
                          "format": Path(item["path"]).suffix, "origin": item["origin"],
                          "screening": item["screening"]})
    web = read_json(child(bundle, "web_evidence_v1/state.json"))
    urls = sorted({public_url(record[key]) for record in web["retrievals"].values()
                   for key in ("requested_url", "final_url")})
    gateway = read_json(child(bundle, "gateway/session/state.json"))
    usage_fields = {"queries", "downloads", "auxiliary_requests", "http_attempts", "http_successes",
                    "command_elapsed_seconds", "response_bytes", "elapsed_seconds"}
    def usage(value):
        return {k: v for k, v in value.items() if k in usage_fields and type(v) in {int, float}}
    return {"schema_version": 1, "scope": "Identifiers, hashes, public URL paths and aggregate acquisition costs only.",
            "registry_sha256": sha(registry_path.read_bytes()), "artifacts": artifacts,
            "web_source_urls_without_query_or_fragment": urls,
            "web_usage": usage(web["usage"]), "shared_gateway_usage": usage(gateway["usage"]),
            "source_bytes_published": False, "raw_discovery_log_published": False,
            "native_discovery_cost": "See reviewed ACTION_SUMMARY.json; outside controller metering."}


def sanitize_allowlist(raw):
    value = json.loads(raw)
    value.pop("project_root", None)
    value.pop("local_mirror", None)
    value["export_note"] = "Historical draft metadata, not the effective export list. PUBLICATION_MANIFEST.json records the exact current export."
    return encoded(value)


def prepare(project, mirror, bundle, output):
    project, mirror, bundle, output = (p.resolve() for p in (project, mirror, bundle, output))
    if output.exists() or not output.parent.is_dir() or not output.is_relative_to(project / "work" / UNIT):
        raise ValueError("Output must be a new directory within this work unit")
    if any(p.is_symlink() or getattr(p, "is_junction", lambda: False)() for p in (output.parent, *output.parents)):
        raise ValueError("Linked output location")
    closed, protocol = closure_gate(project, bundle)
    selected = mapping(project)  # Missing final outputs refuse before transport creation.
    tree = read_tree(mirror)
    available = set(tree) | set(selected) | {REPORT + name for name in DERIVED_NAMES}
    payload, records, rewrites, checked = {}, [], [], []

    def add(destination, raw, source=None, original=None, transform="none"):
        inspect_public(destination, raw)
        payload[destination] = raw
        records.append({"path": destination, "local_source": source.relative_to(project).as_posix() if source else "derived_metadata_only",
                        "local_sha256": sha(original) if original is not None else None,
                        "public_sha256": sha(raw), "bytes": len(raw), "git_blob_sha": git_blob(raw),
                        "base_git_blob_sha": tree.get(destination), "same_as_base": tree.get(destination) == git_blob(raw),
                        "transform": transform})

    for destination, source in selected.items():
        original = source.read_bytes()
        if source.name == "PUBLIC_ALLOWLIST_DRAFT.json":
            raw, transform = sanitize_allowlist(original), "remove_local_roots_from_historical_draft"
        elif source.suffix == ".md":
            raw = rewrite_markdown(original, source, destination, selected, available, project, rewrites, checked)
            transform = "public_markdown_links" if raw != original else "none"
        else:
            raw, transform = original, "none"
        add(destination, raw, source, original, transform)
    public_protocol = {k: v for k, v in protocol.items() if k != "bundle"}
    public_protocol.update(bundle_label="evcAdaptiveL02", local_protocol_sha256=sha((project / "work" / UNIT / "PROTOCOL.json").read_bytes()),
                           transformation="Only the absolute bundle path is omitted; this is a public projection, not original locked bytes.")
    public_closure = {key: closed[key] for key in ("status", "final_candidate", "candidates", "runs", "execution_slots")}
    public_closure["scope"] = "Selection and schedule only; private inventory, local paths and author free text omitted."
    for name, value in (("PROTOCOL_PUBLIC.json", public_protocol), ("AUTHOR_CLOSED_PUBLIC.json", public_closure),
                        ("ACQUISITION_METADATA.json", acquisition_metadata(bundle, closed))):
        add(REPORT + name, encoded(value), transform="bounded_public_projection")
    qa = {"schema_version": 1, "status": "finite_transport_checks_passed_pending_human_content_review",
          "base_head": BASE_HEAD, "mirror_modified": False, "remote_access_or_upload_performed": False,
          "bundle_written": False, "candidate_artifacts_selected": False,
          "rows_source_bodies_raw_logs_selected": False, "markdown_links_checked": len(checked),
          "markdown_rewrites": rewrites,
          "checks": ["exclusive exact file lists", "closed inventory and hashes", "locked design hashes",
                     "all candidate/seed runs and selected stage", "evaluation/recomputation bindings",
                     "secret patterns and forbidden content keys", "finite sizes/types", "local/public hash mapping",
                     "selected/existing-public Markdown link targets", "fresh local mirror head and clean tree"],
          "limits": ["No remote freshness assertion; recheck remote head before separately authorized upload.",
                     "Pattern checks cannot certify absence of every secret or individual record; actual content and aggregate figures require review.",
                     "No candidate implementation or full source is published; this is a restricted implementation-and-aggregate release.",
                     "The original design lock refers to local originals, not transformed public projections."]}
    manifest = {"schema_version": 1, "base_head": BASE_HEAD, "files": list(records),
                "scope": "Exact selected files and local/public SHA mapping. Manifest/QA omit themselves to avoid circular hashes."}
    add(REPORT + "PUBLICATION_MANIFEST.json", encoded(manifest), transform="derived_publication_record")
    add(REPORT + "PUBLICATION_QA.json", encoded(qa), transform="derived_publication_record")
    # Refuse races in source files, closure, and mirror before writing any transport.
    for record in records:
        if record["local_sha256"] and sha(regular(project / record["local_source"]).read_bytes()) != record["local_sha256"]:
            raise ValueError("Selected source changed during preparation")
    closure_gate(project, bundle)
    if read_tree(mirror) != tree:
        raise ValueError("Mirror changed during preparation")
    blobs = [{"index": index, "path": path, "git_blob_sha": git_blob(raw), "public_sha256": sha(raw),
              "bytes": len(raw), "mode": "100644", "type": "blob", "encoding": "base64",
              "content": base64.b64encode(raw).decode("ascii")}
             for index, (path, raw) in enumerate((p, b) for p, b in sorted(payload.items()) if tree.get(p) != git_blob(b))]
    transport_raw = encoded({"schema_version": 1, "base_head": BASE_HEAD, "files": blobs})
    local_manifest = {"schema_version": 1, "status": "prepared_not_uploaded", "base_head": BASE_HEAD,
                      "files": records, "transport_files": [{k: v for k, v in x.items() if k != "content"} for x in blobs],
                      "transport_sha256": sha(transport_raw), "planned_files": len(payload), "changed_files": len(blobs),
                      "total_changed_bytes": sum(x["bytes"] for x in blobs),
                      "instructions": "Review final bytes. Recheck remote head before any separately authorized upload. Use --blob INDEX --chunk N (at most 32000 base64 characters)."}
    output.mkdir()
    for name, raw in (("TRANSPORT.json", transport_raw), ("PUBLIC_MANIFEST.json", encoded(local_manifest)),
                      ("ALLOWLIST_QA.json", encoded(qa))):
        with (output / name).open("xb") as stream:
            stream.write(raw)
    return {"status": local_manifest["status"], "base_head": BASE_HEAD, "output": str(output),
            "planned_files": len(payload), "changed_files": len(blobs),
            "total_changed_bytes": local_manifest["total_changed_bytes"], "transport_sha256": sha(transport_raw)}


def read_blob(output, index, chunk=None, chunk_chars=32000):
    manifest = read_json(regular(output / "PUBLIC_MANIFEST.json"))
    raw = regular(output / "TRANSPORT.json").read_bytes()
    if sha(raw) != manifest["transport_sha256"]:
        raise ValueError("Prepared transport changed")
    transport = json.loads(raw)
    if transport["base_head"] != BASE_HEAD or manifest["base_head"] != BASE_HEAD:
        raise ValueError("Transport base differs")
    if type(index) is not int or not 0 <= index < len(transport["files"]):
        raise ValueError("Blob index outside transport")
    item = transport["files"][index]
    decoded = base64.b64decode(item["content"], validate=True)
    if git_blob(decoded) != item["git_blob_sha"] or sha(decoded) != item["public_sha256"]:
        raise ValueError("Blob bytes differ from commitments")
    if chunk is None:
        if len(item["content"]) > 32000:
            raise ValueError("Large blob: use --chunk 0, --chunk 1, ...")
        return item
    if type(chunk) is not int or chunk < 0 or type(chunk_chars) is not int or not 4 <= chunk_chars <= 32000 or chunk_chars % 4:
        raise ValueError("Chunk must be nonnegative; size must be 4..32000 and divisible by four")
    start = chunk * chunk_chars
    if start >= len(item["content"]):
        raise ValueError("Chunk index outside blob")
    return {**{k: v for k, v in item.items() if k != "content"}, "encoding": "base64_fragment",
            "chunk": chunk, "chunk_count": (len(item["content"]) + chunk_chars - 1) // chunk_chars,
            "base64_offset": start, "base64_total_chars": len(item["content"]),
            "content": item["content"][start:start + chunk_chars]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--mirror", type=Path, default=MIRROR)
    parser.add_argument("--bundle", type=Path, default=BUNDLE)
    parser.add_argument("--output", type=Path, default=HERE / "publication_transport")
    parser.add_argument("--blob", type=int)
    parser.add_argument("--chunk", type=int)
    parser.add_argument("--chunk-chars", type=int, default=32000)
    args = parser.parse_args(argv)
    result = read_blob(args.output, args.blob, args.chunk, args.chunk_chars) if args.blob is not None else prepare(
        args.project, args.mirror, args.bundle, args.output)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
