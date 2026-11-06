# KDD AI for Sciences manuscript, v0.19

The [reading copy](paper.pdf) contains eight main pages. Table 1 on page 3 follows the investigator, source, agent constructors and numerical tools through the iron-status example. Figure 3 on page 6 shows the implications of the program's transfer rules and the three analyses of the six delivered virtual cohorts. References start on page 9 and supplementary results on page 11.

Import [the Overleaf package](overleaf_v19.zip) into a new project, select `paper.tex` and compile twice with LuaLaTeX. The draft awaits author and affiliation confirmation.

To rebuild from the manuscript directory, run `python build_review_copy.py`, `python compile_review.py --render` and `python compile_review.py --standalone` inside this folder. Figure and manuscript identities are in [BUILD_INPUTS.json](BUILD_INPUTS.json). [BUILD_QA.json](BUILD_QA.json) gives page positions, ZIP contents, compilation checks and the result of visual review. An independent build of the twelve-member Overleaf package reproduced the text and page order on all 21 pages.
