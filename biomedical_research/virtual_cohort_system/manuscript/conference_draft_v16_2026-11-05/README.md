# v0.16 conference review edition

The local review PDF uses the ACM `acmart` class with `sigconf,anonymous,review`. The body fills pages 1–8. References occupy pages 9–10 and the two-column appendix begins on page 11. All four main figures, four supplementary figures and seven tables remain in the review copy.

To use the standalone source, import `overleaf_v16.zip`, select `paper.tex` and compile twice with LuaLaTeX. The zip includes the TeX source, the eight figure PDFs and a short build note. It can compile independently of the project workspace.

To rebuild from the scientific Markdown in this checkout:

```powershell
python build_review_copy.py
lualatex -interaction=nonstopmode -halt-on-error paper.tex
lualatex -interaction=nonstopmode -halt-on-error paper.tex
```

`BUILD_INPUTS.json` records the Markdown hash and the eight original figure paths and hashes. `BUILD_QA.json` records the review PDF and ZIP hashes, exact section and display placement, isolated compilation and visual checks. The review edition omits the identifying project link and internal declaration-status notes from the PDF. The canonical Markdown preserves the public scientific record and workspace links. Review-stage copyright and ACM citation metadata use draft settings.

For the verified edition, the local MiKTeX installation supplied the standard ACM dependencies, including `luacode`. The output was compiled with LuaLaTeX and `acmart` v2.20. The archive is intended for a current TeX Live environment with the standard ACM class installed.

