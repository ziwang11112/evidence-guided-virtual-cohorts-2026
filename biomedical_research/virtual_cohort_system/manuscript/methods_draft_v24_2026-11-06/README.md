# Methods development edition, v0.24

[Read the manuscript](paper.pdf) or [open its Overleaf package](overleaf_v24.zip). The 11-point, single-column draft has 11 pages of main text and 28 pages overall. References begin on page 12 and the supplement begins on page 14. Author and affiliation details await confirmation.

Figure 1 restores the v0.22 artwork. The “Author or revise” label belongs to the diagonal arrow from the scientific agent to the generator. The [editable figure](../paper_figures_v24_2026-11-06/fig1-agent-loop.drawio) keeps the label anchored to that edge when the connector is edited.

To reproduce the published PDF and ZIP from the project, run `python build_review_copy.py`, `python compile_review.py --render`, `python compile_review.py --standalone` and `python verify_review_copy.py` from this directory. The [input manifest](BUILD_INPUTS.json) identifies the manuscript, TeX and eleven vector figures. [Build QA](BUILD_QA.json) records the relative edge-label check, figure and table placement and the comparison of all 28 pages and clickable external links with the extracted ZIP.
