# Two-column reading copy of manuscript v0.10

This folder contains a ten-page working reading PDF and its LaTeX source. It is a generic article-class layout, not an official ICML, KDD or EMNLP submission template. No venue or author block is finalized.

- [Reading PDF](paper.pdf)
- [LaTeX source](paper.tex)
- [Overleaf upload bundle](overleaf_v10.zip)
- [Reviewed Markdown manuscript](../DRAFT_v0_10.md)
- [Build inputs and hashes](BUILD_INPUTS.json)

Upload `overleaf_v10.zip` as a new Overleaf project, select **LuaLaTeX**, and compile `paper.tex`. The bundle includes all five original vector figure PDFs. It contains no participant records, generated tables or third-party paper copies. Local fonts use Times New Roman/Arial/Courier New when installed, with TeX Gyre alternatives for portability; pagination may vary slightly with fonts and TeX versions. Overleaf compilation has not been remotely tested.

For local reproduction, run `build_reading_copy.py` from this repository to convert the reviewed Markdown and copy its figure PDFs, then run `lualatex paper.tex` twice. The manuscript's local supporting-artifact links display as labels in the PDF; the Markdown version retains working artifact links. External citations remain clickable. The source Markdown and all figure input hashes are recorded in `BUILD_INPUTS.json`.

The package was compiled and visually inspected locally. It changes presentation only. Full numerical and negative-result records remain available through the Markdown manuscript and preceding v0.9. Author declarations, release terms and the selected venue's official format are still required before submission.
