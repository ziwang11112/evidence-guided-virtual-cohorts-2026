# Methods development edition, v0.25

[Read the manuscript](paper.pdf) or [open its Overleaf package](overleaf_v25.zip). The 11-point, single-column draft has 12 pages of main text and 31 pages overall. References begin on page 13 and the supplement begins on page 16. Author and affiliation details await confirmation.

This revision completes the statistical comparator columns, reports dispersion and complete-case limits, updates related work and adds the bounded artificial diagnostic in Supplement S13. The additional consistency instruction showed no benefit over ordinary construction. Existing clinical experiments and their frozen files are unchanged.

Figure 1 retains the v0.24 artwork. The “Author or revise” label belongs to the arrow from the scientific agent to the generator. The [editable figure](../paper_figures_v24_2026-11-06/fig1-agent-loop.drawio) keeps the label anchored to that edge.

To reproduce the PDF and ZIP from the project, run `python build_review_copy.py`, `python compile_review.py --render`, `python compile_review.py --standalone` and `python verify_review_copy.py` from this directory. The [input manifest](BUILD_INPUTS.json) identifies the manuscript, TeX and eleven vector figures. [Build QA](BUILD_QA.json) records figure/table placement, layout checks, final page count and agreement of the independently compiled ZIP text and links with the reading PDF.
