# Reading manuscript v0.14

This is a locally compiled, two-column reading copy of **Evidence-Guided Agents for Analyzable Virtual Biomedical Cohorts**, not an official submission template.

Upload `overleaf_v14.zip` to Overleaf, select `paper.tex` as the main file and LuaLaTeX as the compiler. Compile twice. Eight vector figure PDFs are included. The compiled PDF is included for comparison; no online project has been created by this package.

To rebuild from this repository layout, run `python build_reading_copy.py` in this folder, then `lualatex -interaction=nonstopmode -halt-on-error paper.tex` twice. The Python builder consumes the adjacent Markdown draft and reviewed figure package; it performs no data analysis. In the standalone Overleaf ZIP, edit and compile `paper.tex` directly.

The seven main figures and one supplementary figure preserve all constructions in their respective studies. The new glycemic/lipid batch is separate from the historical information contrast, summary reconstruction and longitudinal model example. The final manuscript still requires authorship, declarations and venue-specific editing.
