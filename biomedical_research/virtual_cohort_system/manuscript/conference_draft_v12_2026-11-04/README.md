# Manuscript v0.12: scientific-figure reading edition

- [Reading PDF](paper.pdf)
- [LaTeX source](paper.tex)
- [Overleaf bundle](overleaf_v12.zip)
- [Source Markdown](../DRAFT_v0_12.md)
- [Figure-reading guide in Chinese](../paper_figures_v12_2026-11-04/READING_GUIDE_ZH.md)
- [Build input hashes](BUILD_INPUTS.json)

This is a generic two-column article-class reading copy, not an official venue submission template. Five original vector figures replace the previous dashboard styling. Scientific prose, three tables, fifteen references and all experimental results are unchanged; figure captions explain the new encodings.

Upload `overleaf_v12.zip`, select **LuaLaTeX**, and compile `paper.tex`. The archive includes five vector figure PDFs and no patient records, generated tables, third-party papers or credentials. Local fonts use Times New Roman/Arial/Courier New with TeX Gyre fallbacks; pagination may vary across environments. Remote Overleaf compilation has not been tested.

For repository reproduction, run `build_reading_copy.py` and compile twice with LuaLaTeX. The script consumes the versioned Markdown and figure PDFs, not individual records. External citations remain clickable; local supporting-artifact links display as labels in the PDF and remain clickable in the Markdown. A final journal/conference choice, official formatting and author declarations are still needed before submission.
