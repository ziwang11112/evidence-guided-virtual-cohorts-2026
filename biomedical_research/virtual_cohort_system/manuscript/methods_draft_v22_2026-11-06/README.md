# Methods development edition, v0.22

[Read the manuscript](paper.pdf) or [open the Overleaf source package](overleaf_v22.zip). The 11-point single-column edition lets the method, tables and figures follow the manuscript’s reading order. Its main text occupies 11 pages. References start on page 12 and the supplements on page 14, for 28 pages in total. The author and affiliation fields await confirmation.

Figure 1 on page 2 follows the agent's proposal, generator trial, observation and decision. Tables 1 and 2 on page 4 distinguish the inputs that researchers and studies supply from modeling choices made by the agent. Figure 2 on page 5 follows one iron-status record through generation. Figure 3 on page 8 shows the scientific analyses of the sealed tables.

To rebuild from the complete project, run `python build_review_copy.py`, `python compile_review.py --render`, `python compile_review.py --standalone` and `python verify_review_copy.py` here. The verifier uses the review note at `tmp/pdfs/visual_review.txt` as its manual visual inspection record. The [input manifest](BUILD_INPUTS.json) binds the Markdown, TeX and eleven figure PDFs to their hashes. [Build QA](BUILD_QA.json) records figure and table placement, the log checks, and the page-text comparison with an independently compiled copy extracted from the ZIP.
