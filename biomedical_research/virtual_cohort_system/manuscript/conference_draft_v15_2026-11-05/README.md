# Conference-style reading edition v0.15

This is a locally compiled reading edition, not an official venue template or an uploaded Overleaf project. The body prioritizes four scientific figures; complete earlier displays and numeric tables remain in the supplement. Venue recommendations are separate from scientific results.

Upload `overleaf_v15.zip` into Overleaf, select `paper.tex` and LuaLaTeX, and compile twice. For this repository layout, `python build_reading_copy.py` rebuilds TeX from the adjacent Markdown draft and figure PDFs, then `lualatex -interaction=nonstopmode -halt-on-error paper.tex` compiles it. The standalone ZIP compiles the supplied TeX directly.

No participant-level data, third-party original papers, experimental rerun or new reference estimate is included in this editorial edition. Authorship, declarations and venue-specific requirements remain to be completed.
