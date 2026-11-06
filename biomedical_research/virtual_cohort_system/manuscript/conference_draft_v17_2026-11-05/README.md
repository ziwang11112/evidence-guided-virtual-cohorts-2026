# v0.17 conference review edition

The review PDF uses the ACM `acmart` class with `sigconf,anonymous,review`. Pages 1–8 contain the main paper, pages 9–10 contain references, and the two-column appendix begins on page 11. The new prospective results section follows the cross-task glycemia and lipid study. Table S7 appears on page 19 and Figure S5 on page 20.

To use the standalone project, import `overleaf_v17.zip`, select `paper.tex`, choose LuaLaTeX and compile twice. The package contains the review TeX, nine figure PDFs and a short build note. An isolated copy of the extracted ZIP reproduced every page's text.

To rebuild the review source from the project checkout:

```powershell
python build_review_copy.py
lualatex -interaction=nonstopmode -halt-on-error paper.tex
lualatex -interaction=nonstopmode -halt-on-error paper.tex
```

`BUILD_INPUTS.json` binds the scientific Markdown, generated TeX and each figure to SHA256 digests, preserving the original paths across the v15, v16 and v17 figure directories. `BUILD_QA.json` gives the resulting PDF and ZIP digests, section boundaries, page locations and standalone checks. The anonymous review PDF omits the identifying project URL and internal publication-status notes. Its copyright and ACM citation block use draft settings.

The verified local compiler is LuaLaTeX with `acmart` v2.20. The source requires a standard TeX Live or MiKTeX installation with the ACM class. The scientific work remains in the versioned Markdown and the existing study records.

