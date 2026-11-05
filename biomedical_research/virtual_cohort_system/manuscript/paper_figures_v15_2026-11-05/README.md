# v15 scientific result figures

Four presentation-only redraws preserve the reviewed aggregate values, all constructors and all final seeds. The figures use a common blue (`#4266AD`), violet (`#8071BA`), terracotta (`#CE7F60`) and gray palette. They have no full-figure titles or prose warning blocks; scientific qualifications and adjustment sets are provided in [CAPTIONS_RESULTS.md](CAPTIONS_RESULTS.md).

| Figure | Files | Size (inches) | Endpoints | Seed estimates |
|---|---|---|---:|---:|
| 2, evidence comparison | [PDF](fig2-evidence-results.pdf), [SVG](fig2-evidence-results.svg), [PNG](fig2-evidence-results.png) | 7 x 4.35 | 6 | 216 |
| 3, cross-task analyses | [PDF](fig3-cross-task.pdf), [SVG](fig3-cross-task.svg), [PNG](fig3-cross-task.png) | 7 x 5.85 | 6 | 54 |
| 4, supplied-summary reconstruction | [PDF](fig4-summary-results.pdf), [SVG](fig4-summary-results.svg), [PNG](fig4-summary-results.png) | 7 x 4.35 | 5 | 90 |
| S3, dispersion | [PDF](figS3-dispersion.pdf), [SVG](figS3-dispersion.svg), [PNG](figS3-dispersion.png) | 7 x 4.2 | 4 | 36 |

Figure 3 uses three rows and two columns: the left column contains HbA1c age (a), BMI (c), and glucose-adjusted BMI (e); the right contains HDL BMI (b), TC BMI (d), and TC-HDL residual correlation (f). This is a presentation reordering of the same six endpoints. The TC reference interval crosses zero; residual correlation has no reference interval. Figure 2 retains the original panel order. Figure 4 retains all five summary-study endpoints and the L/R supplied-information design. Historical figures were not modified.

The [plot builder](render_results.py) reads four SHA256-pinned aggregate inputs and supports local `work/` or public `reports/` layouts. It does not read patient-level or generated-table data, invoke a constructor, run an experiment, or fit a scientific model. Figure 2 and Figure 4 bindings exactly equal their v12 counterparts. Cross-task seed values and references are copied from the reviewed aggregate; means and ranges use the identical display-only arithmetic in the v14 renderer. No units are pooled or normalized, and constructors are not paired across E0/E1 or L/R.

Reproduce in a separate destination from the project root:

```powershell
python manuscript/paper_figures_v15_2026-11-05/render_results.py --output path/to/new-results
```

Python and matplotlib are required. The system Python 3.12 environment supplied matplotlib for this render; the bundled Python runtime was checked but did not include matplotlib. The PDF artifact-start marker was run successfully once with an expected output count of four before authoring.

[NUMERIC_BINDINGS_RESULTS.json](NUMERIC_BINDINGS_RESULTS.json) records all source paths, source pointers, reference definitions, constructor/seed counts, input hashes, plot values and output hashes. [SHA256SUMS_RESULTS.txt](SHA256SUMS_RESULTS.txt) lists the four input hashes and all twelve image-export hashes. These hashes cover the final files, after the Fig3 column reordering. There are no scientific semantic changes.

All PDFs are vector figures with embedded text, fixed 7-inch widths and no raster image objects. Axis labels use 8-point text; panel titles use 8.8 points; the smallest labels are 7.5 points except Figure 4 constructor IDs at 7.2 points. A 7.06-inch manuscript placement slightly enlarges them. These sizes are not intended for single-column reduction.

## Preserved supporting displays

Four additional displays are copied byte-for-byte from the previous edition, with new supplementary numbering where appropriate:

- [Figure 1: worked evidence-to-model construction](fig1-agent-framework.drawio.pdf), also in [SVG](fig1-agent-framework.drawio.svg).
- [Figure S1: open-retrieval analyses](figS1-open-retrieval.pdf).
- [Figure S2: published longitudinal-model use](figS2-longitudinal-use.pdf).
- [Figure S4: dependence sensitivity and analysis use](figS4-analysis-use.pdf).

The typography statements above concern the four redesigned plots. The retained supporting displays preserve their earlier fonts; the actual reading-PDF review records their smaller labels. Their byte identity is recorded in the editorial unit's figure-reuse manifest.

[FIGURE_QA_RESULTS.json](FIGURE_QA_RESULTS.json) records the actual-PDF text, font, vector and overlap checks. Every final PDF was rendered through Poppler at 100 dpi and visually inspected at 700-pixel/7-inch width; the review images are in [qa/](qa). No clipped text, overlapping labels, or missing panels were observed. The figures retain the original distinct meanings of reference bands and within-constructor seed ranges; complete caption language is required when embedding them.
