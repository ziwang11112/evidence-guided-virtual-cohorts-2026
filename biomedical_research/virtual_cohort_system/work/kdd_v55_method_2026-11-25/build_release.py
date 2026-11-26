"""Compile the v0.55 portable source archive and inspect references and layout."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

import fitz

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "manuscript/kdd_draft_v55_2026-11-25"
BUILD = Path(__file__).resolve().parent
TEX = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-no-shell-escape", "main.tex"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    main = (PAPER / "main.tex").read_text(encoding="utf8")
    appendix = (PAPER / "appendix.tex").read_text(encoding="utf8")
    figures = sorted(set(re.findall(r"\\includegraphics\s*(?:\[[^]]+\])?\s*\{([^}]+)\}", main + appendix)))
    editable = [name.removesuffix(".pdf") for name in figures if name.endswith(".drawio.pdf")]
    names = ["main.tex", "appendix.tex", "grip_groups_table.tex", "references.bib", *figures, *editable]
    items = {name: (PAPER / name).read_bytes() for name in names}
    archive = PAPER / "overleaf_v55.zip"
    with zipfile.ZipFile(archive, "w") as zipped:
        for name, data in items.items():
            entry = zipfile.ZipInfo(name, (2026, 11, 25, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            zipped.writestr(entry, data)
    private = BUILD / "private"
    private.mkdir(exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="compile-", dir=private))
    with zipfile.ZipFile(archive) as zipped:
        assert zipped.testzip() is None
        zipped.extractall(folder)
    for name, data in items.items():
        assert (folder / name).read_bytes() == data
    for number, command in enumerate([TEX, ["bibtex", "main"], TEX, TEX, TEX], 1):
        result = subprocess.run(command, cwd=folder, capture_output=True)
        (folder / f"pass-{number}.log").write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(result.stdout[-4000:].decode("utf8", "replace"))
    log = (folder / "main.log").read_text(encoding="utf8", errors="replace")
    warning = re.compile(r"LaTeX Warning: (?:Reference|Citation)|undefined (?:references|citations)|Rerun to get|Overfull \\[hv]box|undefined control sequence", re.I)
    warnings = [line for line in log.splitlines() if warning.search(line)]
    print("Build", folder, flush=True)
    print("Warnings", warnings, flush=True)
    # Preserve the preview even when a layout issue needs another edit.
    shutil.copyfile(folder / "main.pdf", PAPER / "paper.pdf")
    figures_by_page, tables_by_page = {}, {}
    methods, algorithm, references, appendix_page = [], [], None, None
    with fitz.open(PAPER / "paper.pdf") as doc:
        for number, page in enumerate(doc, 1):
            text = page.get_text()
            for kind, lookup in (("Figure", figures_by_page), ("Table", tables_by_page)):
                for label in re.findall(rf"^{kind} (\d+):", text, re.M):
                    lookup[label] = number
            if "Translate the evidence into a joint sampling program" in text or "Hold the evidence fixed and vary the pairing" in text:
                methods.append(number)
            if "Algorithm 1 Construct and test" in text:
                algorithm.append(number)
            if references is None and re.search(r"^References$", text, re.M):
                references = number
            if appendix_page is None and "Construction, data and reproducibility" in text:
                appendix_page = number
        render = folder / "render"
        render.mkdir()
        selected = sorted(set([1, *methods, *algorithm, figures_by_page.get("2", 2), references or 1]))
        for page in selected:
            doc[page - 1].get_pixmap(matrix=fitz.Matrix(1.7, 1.7)).save(render / f"page-{page}.png")
        report = {
            "release": "0.55 working draft",
            "source_zip_sha256": sha(archive),
            "paper_sha256": sha(PAPER / "paper.pdf"),
            "compiled_from_portable_source_zip": True,
            "source_files": names,
            "paper_pages": len(doc),
            "references_begin_page": references,
            "appendix_begins_page": appendix_page,
            "figures_by_page": figures_by_page,
            "tables_by_page": tables_by_page,
            "method_pages": methods,
            "algorithm_pages": algorithm,
            "unresolved_citations_or_cross_references": len([s for s in warnings if "Overfull" not in s]),
            "overfull_boxes": len([s for s in warnings if "Overfull" in s]),
            "resolved_bibliography_entries": (folder / "main.bbl").read_text(encoding="utf8").count(r"\bibitem"),
        }
    (PAPER / "BUILD_CHECK.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print(json.dumps(report), flush=True)
    assert not warnings, warnings
    return folder


if __name__ == "__main__":
    build()

