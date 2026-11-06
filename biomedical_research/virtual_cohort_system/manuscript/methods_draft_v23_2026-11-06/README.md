# Methods development edition, v0.23

[Read the manuscript](paper.pdf) or [open its Overleaf package](overleaf_v23.zip). The 11-point, single-column draft has 11 pages of main text and 28 pages overall. References begin on page 12 and the supplement begins on page 14. Author and affiliation details await confirmation.

Figure 1 on page 2 follows the scientific agent, its generator and the isolated worker through the construction loop. The action label “Write or revise” is attached to the arrow connecting the agent to the generator. The [native draw.io source](../paper_figures_v23_2026-11-06/fig1-agent-loop.drawio) keeps the label with the arrow when the diagram is edited.

To reproduce the published PDF and ZIP from the project, run `python build_review_copy.py`, `python compile_review.py --render`, `python compile_review.py --standalone` and `python verify_review_copy.py` from this directory. The [input manifest](BUILD_INPUTS.json) identifies the manuscript, TeX and eleven vector figures. [Build QA](BUILD_QA.json) records the relative edge-label check, figure and table placement and the comparison of all 28 pages and clickable external links with the extracted ZIP.
