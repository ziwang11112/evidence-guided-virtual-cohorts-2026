# KDD AI for Sciences manuscript, v0.18

The reading copy has seven main pages. References start on page 8 and supplementary results start on page 10. The main results figures for the evidence comparison and iron-status example are on page 5, with the glycemia/lipid study on page 6. Figure S6 contains the longitudinal HRS comparison.

Open [paper.pdf](paper.pdf) to read the compiled manuscript. Import [overleaf_v18.zip](overleaf_v18.zip) as a new project, set `paper.tex` as the main document and choose LuaLaTeX. The author and affiliation fields need confirmation before submission. The package includes both main disclosure sections, all ten figure PDFs and the complete English TeX.

To rebuild the source from the project Markdown, run `python build_review_copy.py`, `python compile_review.py --render` and `python compile_review.py --standalone` from this directory. The source and figure hashes are recorded in [BUILD_INPUTS.json](BUILD_INPUTS.json). [BUILD_QA.json](BUILD_QA.json) records the page map, package contents, independent build comparison, figure identities and visual review. Two LuaLaTeX passes on an extracted project reproduced the working PDF's text on every page. This package uses standard ACM acmart with sigconf and review options.
