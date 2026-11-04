"""Prepare the reviewed v0.13 allowlisted public payload; never publish or push.

Default is a read-only validation. Use --prepare only after the coordinator says
the final package is ready. Existing verified Git blobs are reused by SHA; new
binary entries use content_base64 for a subsequent GitHub create-blob operation.
Text is decoded directly from raw bytes, preserving CRLF and UTF-8 BOMs. Only
Markdown link destinations are rewritten from local work/ to public reports/.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import io
import json
import posixpath
import re
import subprocess
from urllib.parse import unquote, urlsplit
import zipfile

R = Path(__file__).resolve().parent
P = R.parents[1]
PREFIX = "biomedical_research/virtual_cohort_system/"
UNIT = "manuscript_integration_v13_2026-11-04"
DEST = PREFIX + "reports/" + UNIT + "/"
FIGDIR = "manuscript/paper_figures_v13_2026-11-04/"
OLD_FIGDIR = "manuscript/paper_figures_v12_2026-11-04/"
PAPERDIR = "manuscript/conference_draft_v13_2026-11-04/"
HEAD = "baeaf8cf11be00a6f79df5971ad3279a8c6f5aa3"
FIGURES = ["fig1-agent-framework.drawio", "fig2-evidence-results", "fig3-summary-results",
           "fig4-longitudinal-use", "fig5-open-retrieval", "figS1-analysis-use"]
REUSED_STEMS = {s: s for s in FIGURES[:4]} | {"figS1-analysis-use": "fig5-analysis-use"}
REPORT_FILES = [
    "DRAFT_INTEGRATION_AUDIT.json", "EXPERIMENT_GAP_REVIEW.md", "FIGURE_REUSE_MANIFEST.json",
    "FINAL_PDF_REVIEW.json", "FINAL_PDF_REVIEW.md", "INDEPENDENT_DRAFT_REVIEW.json",
    "INDEPENDENT_DRAFT_REVIEW.md", "NEW_FIGURE_REVIEW_NOTES.md", "PDF_PAGE_MAP.json",
    "SOURCE_BIBLIOGRAPHIC_METADATA.json", "independent_draft_checks.py", "prepare_draft.py",
    "PUBLIC_SCOPE.md", "export_reviewed.py",
]
COORDINATOR_REPORT_FILES = ["STORY_AND_FIGURE_PLAN.md", "STATE.json", "PACKAGE_INVENTORY.json"]
FIGURE_FILES = ["render_open_retrieval.py", "FIG5_NUMERIC_BINDINGS.json", "FIG5_SEED_VALUES.csv",
                "FIG5_AUTHOR_SUMMARIES.csv", "CAPTION_FIG5.md", "FIG5_READING_GUIDE_ZH.md", "README.md"]
PAPER_FILES = ["paper.tex", "paper.pdf", "BUILD_INPUTS.json", "build_reading_copy.py", "README.md",
               "OVERLEAF_README.md", "overleaf_v13.zip"]
SECRET = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{30,})\b")
MD_LINK = re.compile(r"(!?\[[^\]]*\])\(([^)]+)\)")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes().decode("utf-8-sig"))


def mapping():
    files = {DEST + name: R / name for name in REPORT_FILES + COORDINATOR_REPORT_FILES}
    for name in ["README.md", "manuscript/README.md", "docs/CURRENT_RESEARCH_FOCUS.md", "manuscript/DRAFT_v0_13.md",
                 "manuscript/KEY_EXPERIMENT_GAPS_v13_2026-11-04.md"]:
        files[PREFIX + name] = P / name
    for name in FIGURE_FILES + [s + ext for s in FIGURES for ext in (".svg", ".png", ".pdf")]:
        files[PREFIX + FIGDIR + name] = P / FIGDIR / name
    for name in PAPER_FILES + ["figures/" + s + ".pdf" for s in FIGURES]:
        files[PREFIX + PAPERDIR + name] = P / PAPERDIR / name
    files["README.md"] = R / "ROOT_README.md"
    return files


def verify_zip(raw):
    required = {"paper.tex", "README.md"} | {"figures/" + s + ".pdf" for s in FIGURES}
    allowed = required | {"paper.pdf", "BUILD_INPUTS.json", "build_reading_copy.py"}
    records = []
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or not required.issubset(names) or set(names) - allowed:
            raise ValueError("Unexpected or missing Overleaf ZIP members: " + repr(names))
        for name in names:
            if name.startswith("/") or ".." in name.split("/") or "\\" in name:
                raise ValueError("Unsafe ZIP member path: " + name)
            member = archive.read(name)
            source = P / PAPERDIR / ("OVERLEAF_README.md" if name == "README.md" else name)
            if not source.is_file() or source.read_bytes() != member:
                raise ValueError("ZIP member differs from reviewed package bytes: " + name)
            if name.endswith(".pdf"):
                if not member.startswith(b"%PDF-"):
                    raise ValueError("Invalid packaged PDF: " + name)
            elif SECRET.search(member.decode("utf-8")):
                raise ValueError("Credential-pattern match in ZIP text: " + name)
            records.append(dict(path=name, bytes=len(member), sha256=sha(member)))
    return records


def rewrite_links(content, target, available, rewrites, checked):
    def replace(match):
        label, original = match.groups()
        value = original[1:-1] if original.startswith("<") and original.endswith(">") else original
        parsed = urlsplit(value)
        if parsed.scheme in ("http", "https", "mailto") or value.startswith("#"):
            return match.group(0)
        if parsed.scheme or parsed.netloc or value.startswith("/"):
            raise ValueError(f"Nonportable Markdown link in {target}: {original}")
        path = re.sub(r"(^|/)work/", r"\1reports/", unquote(parsed.path))
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(target), path))
        if target.startswith(DEST) and path == "ROOT_README.md":
            resolved = "README.md"
        if resolved not in available and "/reports/" in "/" + resolved:
            suffix = ("/" + resolved).split("/reports/", 1)[1]
            candidates = [name for name in available if name.endswith("/reports/" + suffix)]
            if len(candidates) == 1:
                resolved = candidates[0]
        if resolved not in available:
            raise FileNotFoundError(f"Unresolved public link; no reference will be dropped: {target}: {original} -> {resolved}")
        new = posixpath.relpath(resolved, posixpath.dirname(target))
        if parsed.query:
            new += "?" + parsed.query
        if parsed.fragment:
            new += "#" + parsed.fragment
        if " " in new:
            new = "<" + new + ">"
        checked.append(dict(file=target, original=original, resolved=resolved))
        if new != original:
            rewrites.append(dict(file=target, old=original, new=new))
        return label + "(" + new + ")"
    return MD_LINK.sub(replace, content)


def verify_review_gates():
    """Require independent approvals and bind them to actual reviewed bytes."""
    state = read_json(R / "STATE.json")
    if state.get("status") != "complete_manuscript_integration":
        raise ValueError("Coordinator STATE is not complete_manuscript_integration.")
    draft_path = P / "manuscript/DRAFT_v0_13.md"
    draft = draft_path.read_bytes()
    draft_review = read_json(R / "INDEPENDENT_DRAFT_REVIEW.json")
    if draft_review.get("status") != "PASS" or draft_review.get("failed_checks"):
        raise ValueError("Independent draft review has not passed.")
    if not all(item.get("pass") is True for item in draft_review["checks"]):
        raise ValueError("Independent draft review contains a failed check.")
    bindings = {name.replace("\\", "/"): digest for name, digest in draft_review["sha256_bindings"].items()}
    required_bindings = ["manuscript/DRAFT_v0_13.md", "work/" + UNIT + "/DRAFT_INTEGRATION_AUDIT.json",
                         FIGDIR + "FIG5_NUMERIC_BINDINGS.json", FIGDIR + "fig5-open-retrieval.svg",
                         FIGDIR + "figS1-analysis-use.svg"]
    for name in required_bindings:
        if name not in bindings or sha((P / name).read_bytes()) != bindings[name]:
            raise ValueError("Current artifact differs from independent draft review: " + name)
    pdf_review = read_json(R / "FINAL_PDF_REVIEW.json")
    if pdf_review.get("decision") != "PASS_FOR_GENERIC_READING_COPY" or pdf_review.get("blockers"):
        raise ValueError("Final reading-copy review has not passed.")
    for kind, name in [("pdf", "paper.pdf"), ("tex", "paper.tex")]:
        if sha((P / PAPERDIR / name).read_bytes()) != pdf_review[kind]["sha256"]:
            raise ValueError("Reading package changed after final visual review: " + name)
    audit = read_json(R / "DRAFT_INTEGRATION_AUDIT.json")
    if audit["new_draft_sha256"] != sha(draft) or audit["input_draft_sha256"] != sha((P / "manuscript/DRAFT_v0_12.md").read_bytes()):
        raise ValueError("Draft integration audit is stale.")
    if not audit["original_tables_2_3_identical"] or audit["historical_frozen_outputs_modified"]:
        raise ValueError("Historical result preservation failed.")
    if audit["new_generations"] != 0 or audit["new_patient_reads_or_fits"] != 0:
        raise ValueError("Unexpected new empirical work in this manuscript export.")
    numeric = read_json(P / FIGDIR / "FIG5_NUMERIC_BINDINGS.json")
    if numeric["builder_sha256"] != sha((P / FIGDIR / "render_open_retrieval.py").read_bytes()):
        raise ValueError("Figure 5 builder changed after numeric binding.")
    for name, info in numeric["outputs"].items():
        if sha((P / FIGDIR / name).read_bytes()) != info["sha256"]:
            raise ValueError("Figure 5 output changed: " + name)
    if numeric["coverage"]["primary_seed_estimates"] != 36 or numeric["new_generation"] or numeric["new_clinical_reads_or_fits"]:
        raise ValueError("Unexpected new Figure 5 scope.")
    reuse = read_json(R / "FIGURE_REUSE_MANIFEST.json")["reused"]
    expected_reused = {s + ext for s in REUSED_STEMS for ext in (".svg", ".png", ".pdf")}
    if len(reuse) != 15 or {r["destination"].replace("\\", "/").split("/")[-1] for r in reuse} != expected_reused:
        raise ValueError("Historical figure reuse manifest must contain exactly 15 exports.")
    for item in reuse:
        old = (P / "manuscript" / item["source"].replace("\\", "/")).read_bytes()
        new = (P / "manuscript" / item["destination"].replace("\\", "/")).read_bytes()
        if old != new or sha(new) != item["sha256"] or item["bytes_preserved"] is not True:
            raise ValueError("Historical figure bytes changed: " + item["destination"])
    build = read_json(P / PAPERDIR / "BUILD_INPUTS.json")
    if build["source_sha256"] != sha(draft) or build["source_tex_sha256"] != sha((P / PAPERDIR / "paper.tex").read_bytes()):
        raise ValueError("Build inputs do not bind the reviewed manuscript and TeX.")
    if {f["name"] for f in build["figures"]} != {s + ".pdf" for s in FIGURES}:
        raise ValueError("Reading-copy figure inventory differs from reviewed six figures.")
    for item in build["figures"]:
        original = (P / FIGDIR / item["name"]).read_bytes()
        copied = (P / PAPERDIR / "figures" / item["name"]).read_bytes()
        if original != copied or sha(original) != item["sha256"]:
            raise ValueError("Reading-copy figure differs from source: " + item["name"])
    return dict(independent_draft_status="PASS", final_pdf_decision=pdf_review["decision"],
                coordinator_status=state["status"], state_sha256=sha((R / "STATE.json").read_bytes()),
                draft_sha256=sha(draft), pdf_sha256=pdf_review["pdf"]["sha256"], tex_sha256=pdf_review["tex"]["sha256"],
                independent_draft_review_sha256=sha((R / "INDEPENDENT_DRAFT_REVIEW.json").read_bytes()),
                final_pdf_review_sha256=sha((R / "FINAL_PDF_REVIEW.json").read_bytes()),
                historical_figure_exports_bound=15, new_figure_exports_bound=3,
                copied_figure_pdfs_match=True, new_generations=0, new_patient_reads_or_fits=0)


def reused_public_source(target):
    """Reuse only old figure blobs; verify their content before accepting SHA."""
    for stem, previous in REUSED_STEMS.items():
        for extension in (".svg", ".png", ".pdf"):
            if target == PREFIX + FIGDIR + stem + extension:
                return PREFIX + OLD_FIGDIR + previous + extension
        if target == PREFIX + PAPERDIR + "figures/" + stem + ".pdf":
            return PREFIX + OLD_FIGDIR + previous + ".pdf"
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, default=P.parent / "github_virtual_cohort_2026-10-27")
    parser.add_argument("--prepare", action="store_true", help="Write local payload/manifest after coordinator readiness.")
    args = parser.parse_args()
    def git(*arguments):
        return subprocess.check_output(["git", *arguments], cwd=args.checkout)
    if git("rev-parse", "HEAD").decode().strip() != HEAD:
        raise ValueError("Unexpected base checkout HEAD; re-review the export parent.")
    if git("status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("Base checkout must be clean; exporter never changes it.")
    tree = {}
    for row in git("ls-tree", "-r", HEAD).decode().splitlines():
        head, path = row.split("\t", 1)
        mode, kind, digest = head.split()
        if kind == "blob":
            tree[path] = digest
    files = mapping()
    missing = [str(path) for path in files.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Required package artifacts are missing:\n" + "\n".join(missing))
    review_binding = verify_review_gates()
    available = set(tree) | set(files) | {DEST + "PUBLIC_EXPORT_MANIFEST.json"}
    entries, manifests, rewrites, checked, zip_members = [], [], [], [], []
    reused_count = 0
    for target, source in files.items():
        raw = source.read_bytes()
        extension = source.suffix.lower()
        entry = dict(path=target, mode="100644", type="blob")
        old_path = reused_public_source(target)
        if old_path:
            if old_path not in tree:
                raise ValueError("Previously published figure blob is missing: " + old_path)
            existing = git("cat-file", "blob", tree[old_path])
            if sha(existing) != sha(raw) or existing != raw:
                raise ValueError("Public historical figure blob differs from reviewed local bytes: " + old_path)
            public = raw
            entry["sha"] = tree[old_path]
            transport = "sha"
            reused_count += 1
        elif extension in (".pdf", ".png", ".zip"):
            if extension == ".pdf" and not raw.startswith(b"%PDF-"):
                raise ValueError("Invalid PDF bytes: " + str(source))
            if extension == ".png" and not raw.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("Invalid PNG bytes: " + str(source))
            if extension == ".zip":
                zip_members = verify_zip(raw)
            public = raw
            entry["content_base64"] = base64.b64encode(raw).decode("ascii")
            transport = "content_base64"
        else:
            if extension not in {".md", ".json", ".py", ".svg", ".tex", ".csv"}:
                raise ValueError("Unapproved text extension: " + str(source))
            text = raw.decode("utf-8")  # Never read_text(): preserve CRLF and any UTF-8 BOM.
            if SECRET.search(text):
                raise ValueError("Credential-pattern match in export text: " + str(source))
            if extension == ".json":
                json.loads(raw.decode("utf-8-sig"))
            if extension == ".md":
                text = rewrite_links(text, target, available, rewrites, checked)
            public = text.encode("utf-8")
            if extension != ".md" and public != raw:
                raise ValueError("Text byte identity was not preserved: " + str(source))
            if public.count(b"\r\n") != raw.count(b"\r\n"):
                raise ValueError("CRLF count changed: " + str(source))
            entry["content"] = text
            transport = "content"
        entries.append(entry)
        info = dict(path=target, bytes=len(public), sha256=sha(public), local_source_sha256=sha(raw),
                    payload_field=transport)
        if old_path:
            info.update(reused_from=old_path, git_blob_sha=entry["sha"])
        manifests.append(info)
    if reused_count != 20:
        raise ValueError("Expected 15 historical exports plus five copied figure PDFs to reuse verified public blobs.")
    record = dict(parent=HEAD, status="reviewed_payload_prepared_not_published",
                  scope="Versioned v0.13 integration of completed open-retrieval replication, original figures, reading/Overleaf package and independent review records.",
                  individual_records_included=False, third_party_originals_included=False,
                  rendered_review_pages_included=False, logs_included=False,
                  review_bindings=review_binding, files=manifests.copy(), links_checked=len(checked),
                  navigation_rewrites=rewrites, unresolved_links=[], references_removed=0,
                  overleaf_zip_members=zip_members, existing_blob_entries=reused_count,
                  file_count_including_export_manifest=len(entries)+1,
                  new_binary_entries=sum("content_base64" in e for e in entries),
                  text_entries_including_export_manifest=sum("content" in e for e in entries)+1,
                  hash_semantics="Review hashes bind original local bytes. Public hashes bind exported bytes. JSON/code/CSV/TeX/SVG bytes are preserved; Markdown changes only resolve public link destinations, preserving CRLF. Frozen local work/ paths inside scientific bindings remain unchanged.",
                  binary_transport="Reuse entries with sha directly. For content_base64 entries create Git blobs with base64 encoding and replace that field with returned sha before tree creation. No publishing operation is performed by this script.")
    body = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    target = DEST + "PUBLIC_EXPORT_MANIFEST.json"
    entries.append(dict(path=target, mode="100644", type="blob", content=body))
    manifests.append(dict(path=target, bytes=len(body.encode("utf-8")), sha256=sha(body.encode("utf-8")), payload_field="content"))
    parts, part, size = [], [], 0
    for entry in entries:
        count = len(json.dumps(entry, ensure_ascii=False).encode("utf-8"))
        if part and size + count > 220000:
            parts.append(part)
            part, size = [], 0
        part.append(entry)
        size += count
    if part:
        parts.append(part)
    summary = dict(files=len(entries), parts=len(parts), public_bytes=sum(x["bytes"] for x in manifests),
                   links_checked=len(checked), unresolved_links=0, references_removed=0,
                   existing_blob_entries=reused_count, new_binary_entries=sum("content_base64" in e for e in entries),
                   text_entries=sum("content" in e for e in entries), prepared=args.prepare,
                   note="Local validation/payload only; no checkout change, Git object creation, publication or push.")
    if args.prepare:
        (R / "PUBLIC_EXPORT_MANIFEST.json").write_bytes(body.encode("utf-8"))
        (R / "PUBLIC_MANIFEST.json").write_bytes((json.dumps(manifests, indent=2) + "\n").encode("utf-8"))
        summary["part_sizes"] = []
        for index, values in enumerate(parts):
            serialized = json.dumps({"tree": values}, ensure_ascii=False).encode("utf-8")
            (R / f"PUBLIC_PAYLOAD_PART_{index}.json").write_bytes(serialized)
            summary["part_sizes"].append(dict(part=index, bytes=len(serialized), entries=len(values),
                                               existing_blob_entries=sum("sha" in e for e in values),
                                               binary_entries=sum("content_base64" in e for e in values)))
        (R / "PUBLIC_PREPARATION.json").write_bytes((json.dumps(summary, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
