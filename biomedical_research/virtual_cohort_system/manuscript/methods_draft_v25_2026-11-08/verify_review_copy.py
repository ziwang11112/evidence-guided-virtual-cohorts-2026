"""Verify and compare the two compiled v0.25 copies, then report layout checks."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
from xml.etree import ElementTree

import fitz

HERE = Path(__file__).resolve().parent
STANDALONE = HERE / "tmp/pdfs/standalone"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_source_assets(manifest):
    assert sha(HERE.parent / manifest["source_markdown"]) == manifest["source_sha256"]
    assert sha(HERE / "paper.tex") == manifest["source_tex_sha256"]
    expected = {"paper.tex", "OVERLEAF_README.md"}
    with zipfile.ZipFile(HERE / "overleaf_v25.zip") as archive:
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


def external_links(path):
    with fitz.open(path) as doc:
        return sorted((page.number + 1, link["uri"]) for page in doc
                      for link in page.get_links()
                      if link["kind"] == fitz.LINK_URI and link.get("uri"))


def run():
    manifest = json.loads((HERE / "BUILD_INPUTS.json").read_text())
    files = compare_source_assets(manifest)
    local = HERE / "paper.pdf"
    pages = page_texts(local)
    assert pages == page_texts(STANDALONE / "paper.pdf")
    links = external_links(local)
    assert links and links == external_links(STANDALONE / "paper.pdf"), "External links differ"
    tex = (HERE / "paper.tex").read_text(encoding="utf8")
    assert r"\documentclass[11pt,letterpaper]{article}" in tex
    assert "Author and affiliation details pending confirmation" in tex
    assert r"\onecolumn" not in tex
    main_tex=tex.split(r"\section*{References}")[0]
    assert r"\begin{lstlisting}" not in tex and not re.search(r"\\theta(?![A-Za-z])", main_tex)
    assert re.search(r"\\theta(?![A-Za-z])", tex.split(r"\section*{Supplementary results}")[-1])
    assert manifest['figures'][0]['source']=='paper_figures_v24_2026-11-06/fig1-agent-loop.drawio.pdf'
    assert manifest['figures'][1]['source']=='paper_figures_v20_2026-11-06/fig1-agent-method.drawio.pdf'
    native = (HERE.parent / manifest['figures'][0]['source']).with_suffix('')
    cells = {c.attrib['id']: c for c in ElementTree.parse(native).iter('mxCell')}
    def label(cell):
        return re.sub(r"<[^>]+>", "", cell.get("value", "")).strip().casefold()
    action = next(c for c in cells.values() if label(c) == 'author or revise')
    edge = cells[action.attrib['parent']]
    assert (edge.get('edge'), edge.get('id')) == ('1', 'agent-writes')
    assert action.find('mxGeometry').get('relative') == '1', 'Action must travel with its edge'
    # Verify that the restored v22 connector itself keeps its original direction
    # and control points. Legacy Draw.io arcs are positioned by endpoints.
    legacy = HERE.parent / 'paper_figures_v22_2026-11-06/fig1-agent-loop.drawio'
    old_cells = {c.attrib['id']: c for c in ElementTree.parse(legacy).iter('mxCell')}
    assert set(old_cells) == set(cells), 'Restoration should preserve all original diagram cells'
    def structure(el):
        return (el.tag, tuple(sorted(el.attrib.items())), (el.text or '').strip(),
                tuple(structure(child) for child in el))
    assert action.get('id') == 'author-action'
    assert structure(old_cells[edge.get('id')].find('mxGeometry')) == structure(edge.find('mxGeometry'))
    assert all(structure(old_cells[k]) == structure(cells[k])
               for k in cells if k != action.attrib['id']), 'A cell beyond the action label changed'

    # Uncropped draw.io export can yield a white Letter-size page. Check the
    # actual vector labels before treating a matching SHA as a valid figure.
    with fitz.open(HERE/'figures'/manifest['figures'][0]['file']) as diagram:
        page = diagram[0]
        assert len(diagram) == 1 and page.rect.width > page.rect.height
        assert page.get_drawings() and len(page.get_text().split()) > 3
        assert 'author or revise' in ' '.join(page.get_text().lower().split())
        pix = page.get_pixmap(colorspace=fitz.csGRAY, matrix=fitz.Matrix(1,1))
        assert sum(v < 230 for v in pix.samples) / len(pix.samples) > .015, 'Blank overview export'
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
                for match in re.finditer(r"^" + typ + r"\s+(S?\d+)[.:]", text, re.M):
                    key = match.group(1)
                    assert key not in catalog, (typ, key)
                    catalog[key] = page_no
    assert set(figures) == {"1", "2", "3", "4", "5", "S1", "S2", "S3", "S4", "S5", "S6"}, figures
    expected_tables = {str(n) for n in range(1, manifest["main_table_count"]+1)}
    expected_tables.update(f"S{n}" for n in range(1, manifest["supplementary_table_count"]+1))
    assert set(tables) == expected_tables, tables
    assert tables["1"] <= tables["2"] < headings["References"], tables
    assert max(figures[str(n)] for n in range(1,6)) < headings["References"]
    # Rasterize both papers with the same renderer. A page-by-page comparison
    # includes every visible element even when PDF metadata differs.
    prior_pdf = HERE.parent / "methods_draft_v24_2026-11-06" / "paper.pdf"
    with fitz.open(prior_pdf) as prior, fitz.open(local) as current:
        visually_changed_pages = [
            i+1 for i in range(max(len(prior),len(current)))
            if i >= len(prior) or i >= len(current) or prior[i].get_pixmap(alpha=False).samples != current[i].get_pixmap(alpha=False).samples
        ]
    logs = {}
    for directory in (HERE, STANDALONE):
        lines = (directory / "paper.log").read_text(encoding="utf8", errors="replace").splitlines()
        logs[directory.name] = [s for s in lines if re.search(r"Overfull \\[hv]box|Missing character:|Float too large|^! ", s)]
    assert not any(logs.values()), logs
    end = headings["References"] - 1
    assert end > 0
    report = {
        "main_pages": end, "page_limit": None,
        "references_first_page": headings["References"], "appendix_first_page": headings["Supplementary results"],
        "total_pages": len(pages), "figure_pages": figures, "table_pages": tables,
        "figure_sha256_match": True, "markdown_sha256": manifest["source_sha256"],
        "pdf_sha256": sha(local), "zip_sha256": sha(HERE / "overleaf_v25.zip"),
        "zip_independent_build_text_matches": True, "zip_entries": files,
        "clickable_external_links": len(links), "standalone_external_links_match": True,
        "author_revise_is_relative_agent_to_program_edge_label": True,
        "v22_native_cells_changed": [action.get('id')],
        "v24_rendered_pages_changed": visually_changed_pages,
        "class": "article [11pt,letterpaper], single-column methods development edition", "layout_errors": logs,
        "author_status": "placeholder until authors confirm real author and affiliation details",
        "visual_review": ((HERE / "tmp/pdfs/visual_review.txt").read_text(encoding="utf8").strip()
                          if (HERE / "tmp/pdfs/visual_review.txt").is_file()
                          else "No manual page inspection has been recorded for this build."),
    }
    (HERE / "BUILD_QA.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print(json.dumps({k: report[k] for k in ("main_pages","total_pages","figure_pages","table_pages","page_limit")}, indent=2))


if __name__ == "__main__":
    run()
