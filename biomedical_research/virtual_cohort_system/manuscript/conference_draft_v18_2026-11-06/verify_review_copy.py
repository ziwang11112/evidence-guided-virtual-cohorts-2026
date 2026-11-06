"""Verify and compare the two compiled v0.18 copies, then report layout checks."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

import fitz

HERE = Path(__file__).resolve().parent
STANDALONE = HERE / "tmp/pdfs/standalone"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_source_assets(manifest):
    assert sha(HERE.parent / manifest["source_markdown"]) == manifest["source_sha256"]
    assert sha(HERE / "paper.tex") == manifest["source_tex_sha256"]
    expected = {"paper.tex", "OVERLEAF_README.md"}
    with zipfile.ZipFile(HERE / "overleaf_v18.zip") as archive:
        for figure in manifest["figures"]:
            name = "figures/" + figure["file"]
            expected.add(name)
            assert figure["sha256"] == sha(HERE.parent / figure["source"]) == sha(HERE / name)
            assert hashlib.sha256(archive.read(name)).hexdigest() == figure["sha256"]
        assert set(archive.namelist()) == expected
        for item in expected:
            assert archive.read(item) == (HERE / item).read_bytes() == (STANDALONE / item).read_bytes()
    return sorted(expected)


def page_texts(path):
    with fitz.open(path) as doc:
        return [" ".join(p.get_text(sort=True).split()) for p in doc]


def run():
    manifest = json.loads((HERE / "BUILD_INPUTS.json").read_text())
    files = compare_source_assets(manifest)
    local = HERE / "paper.pdf"
    pages = page_texts(local)
    assert pages == page_texts(STANDALONE / "paper.pdf")
    tex = (HERE / "paper.tex").read_text(encoding="utf8")
    assert r"\documentclass[sigconf,review]{acmart}" in tex
    assert r"\author{Author details pending confirmation}" in tex
    assert r"\onecolumn" not in tex
    for heading in ("Limitations and Ethical Considerations", "Generative AI Usage"):
        assert tex.index("{" + heading + "}") < tex.index(r"\section*{References}")
    headings, figures, tables = {}, {}, {}
    with fitz.open(local) as doc:
        for page_no, page in enumerate(doc, 1):
            text = page.get_text()
            for heading in ("References", "Supplementary results"):
                if re.search(r"^" + heading + r"$", text, re.M):
                    headings[heading] = page_no
            for typ, catalog in (("Figure", figures), ("Table", tables)):
                for match in re.finditer(r"^" + typ + r" (S?\d+):", text, re.M):
                    key = match.group(1)
                    assert key not in catalog, (typ, key)
                    catalog[key] = page_no
    assert set(figures) == {"1", "2", "3", "4", "S1", "S2", "S3", "S4", "S5", "S6"}, figures
    assert len(tables) == manifest["table_count"], tables
    assert max(figures[str(n)] for n in range(1,5)) < headings["References"]
    logs = {}
    for directory in (HERE, STANDALONE):
        lines = (directory / "paper.log").read_text(encoding="utf8", errors="replace").splitlines()
        logs[directory.name] = [s for s in lines if re.search(r"Overfull \\[hv]box|Missing character:|Float too large|^! ", s)]
    assert not any(logs.values()), logs
    end = headings["References"] - 1
    report = {
        "main_pages": end, "maximum_main_pages": 8, "main_within_eight": end <= 8,
        "references_first_page": headings["References"], "appendix_first_page": headings["Supplementary results"],
        "total_pages": len(pages), "figure_pages": figures, "table_pages": tables,
        "figure_sha256_match": True, "markdown_sha256": manifest["source_sha256"],
        "pdf_sha256": sha(local), "zip_sha256": sha(HERE / "overleaf_v18.zip"),
        "zip_independent_build_text_matches": True, "zip_entries": files,
        "class": "acmart [sigconf,review]", "layout_errors": logs,
        "author_status": "placeholder until authors confirm real author and affiliation details",
        "visual_review": (HERE / "tmp/pdfs/visual_review.txt").read_text(encoding="utf8").strip(),
    }
    (HERE / "BUILD_QA.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print(json.dumps({k: report[k] for k in ("main_pages","total_pages","figure_pages","table_pages","main_within_eight")}, indent=2))


if __name__ == "__main__":
    run()
