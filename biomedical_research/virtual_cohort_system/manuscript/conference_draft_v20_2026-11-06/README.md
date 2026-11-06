# Conference manuscript v0.20

The [reading PDF](paper.pdf) has seven main pages. Page 2 shows the general method using an iron-status research question. The iron results are on page 4, the glycemia evidence comparison on page 5 and the cross-task results on page 6. The worked projection equations for one CHNS constructor appear in Supplement S11 on page 20.

Import [the Overleaf project](overleaf_v20.zip), choose `paper.tex` as the main file and compile twice with LuaLaTeX. An isolated build of that package reproduced the text of every page. [Verification record](BUILD_QA.json) · [source and figure hashes](BUILD_INPUTS.json).

To reproduce the package from the Markdown manuscript and figure sources, run `python build_review_copy.py`, `python compile_review.py --render` and `python compile_review.py --standalone` in this directory. The author and affiliation fields are placeholders in this reading draft.
