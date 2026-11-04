# v0.13 reading copy and editable LaTeX

**Title:** Evidence-Guided Agents for Analyzable Virtual Biomedical Cohorts.

This is a 13-page generic two-column article reading copy, with references and supplementary results. It is not an official conference/journal template and is not submission-ready. The new edition integrates the completed four-author open-retrieval experiment, updates the abstract/contributions/method/results/discussion, adds a new main Figure 5, moves the earlier full Figure 5 to Supplementary Figure S1 and retains all unfavorable findings.

- [Reading PDF](paper.pdf)
- [Editable source](paper.tex)
- [Overleaf-ready ZIP](overleaf_v13.zip)
- [Full Markdown source](../DRAFT_v0_13.md)
- [Build input identities](BUILD_INPUTS.json)
- [Independent content review](../../reports/manuscript_integration_v13_2026-11-04/INDEPENDENT_DRAFT_REVIEW.md)
- [Final PDF review](../../reports/manuscript_integration_v13_2026-11-04/FINAL_PDF_REVIEW.md)

The document contains five main figures, three main tables, one supplementary figure, two supplementary tables and 24 references. Historical numerical Tables 2/3 and Results 4.2–4.4 are preserved except for versioned figure paths. The integration generates no cohorts or clinical fits. The original v0.12 and all frozen experiments remain unchanged.

Compile `paper.tex` with **LuaLaTeX**, twice for stable references. Times New Roman is used when installed; TeX Gyre Termes is the included-command fallback. The ZIP is a local editable source package, not an already uploaded Overleaf project. `build_reading_copy.py` reconstructs the LaTeX from the repository Markdown and figure package; it is not necessary for compiling the ZIP.

The exact final PDF has been visually inspected page by page. The supplementary float order was repaired so the section heading precedes Figure S1. Final compilation had no overfull boxes, missing glyphs, undefined references or unresolved rerun warnings. Underfull-box messages and the local MiKTeX update reminder are not compilation failures; final layout review determines readability.

Remaining submission work: authorship/affiliations, funding/conflicts, ethics/data-access/AI/software-license statements, final target venue and its formatting/page limits. The [experiment-gap checklist](../KEY_EXPERIMENT_GAPS_v13_2026-11-04.md) distinguishes these tasks from evidence needed only for stronger claims.
