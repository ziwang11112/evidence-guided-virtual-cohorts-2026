# KDD AI for Sciences manuscript v0.21

The [reading copy](paper.pdf) places the system architecture on page 2 and the iron-status example on page 3. Figure 3 on page 4 shows three analyses of the same delivered records. Figure 4 on page 6 reports the relationship-evidence contrast and Figure 5 on page 7 reports the cross-task results. References begin on page 8. The appendix begins on page 10, and Supplement S12 identifies the implementation points for the architecture on page 20.

Import the [Overleaf ZIP](overleaf_v21.zip), choose `paper.tex` as the main document, and compile twice with LuaLaTeX. It includes the eleven figure PDFs. Author and affiliation details await confirmation before submission.

To build locally, run `python build_review_copy.py`, `python compile_review.py --render`, and `python compile_review.py --standalone`. The [manifest](BUILD_INPUTS.json) records the source and figure digests. The [verification](BUILD_QA.json) compares paginated text against a separate compilation of the extracted ZIP and reports figure locations, caption numbering, completeness and layout checks.

