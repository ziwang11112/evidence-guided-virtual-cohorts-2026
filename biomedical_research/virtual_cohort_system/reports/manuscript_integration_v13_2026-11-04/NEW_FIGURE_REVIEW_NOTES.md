# New Figure 5: construction and review notes

2026-11-04. Figure author: `/root/v13_evidence_figure`. This is the figure author's numerical and visual QA record, not the manuscript's independent final review.

**Ready for integration:** `manuscript/paper_figures_v13_2026-11-04/fig5-open-retrieval.svg`, `.pdf`, and `.png`, with `CAPTION_FIG5.md`, `FIG5_READING_GUIDE_ZH.md`, two full-precision CSVs, `FIG5_NUMERIC_BINDINGS.json`, and `render_open_retrieval.py` in the same directory.

## Design and scientific content

The 7.2 × 4.45-inch figure has six panels in two rows: all three CHNS primary analyses above all three ENSANUT primary analyses. It retains all four authors and all twelve final tables, with 36 exact seed-level primary estimates. Colors match the surrounding paper's blue/purple/coral family, with no green. White background, editable SVG text, embedded-font vector PDF and 300 dpi PNG support two-column publication. No new diagram, raster illustration, inferred curve, pooled score or acceptance zone is introduced.

Each panel has separate author rows and a third reference row. Author circles retain exact x-coordinates and are staggered vertically in seed order 8101–8103 so that three nearly coincident values remain visible. A diamond and minimum–maximum segment sit below the circles, avoiding mean-marker occlusion. Coral reference squares and intervals appear on their own row rather than behind the generated points as shaded target regions. CHNS intervals are solid; ENSANUT stability bands are dashed. Their distinct meanings are labeled by row and in the caption. Author identifiers and marker shapes preserve meaning beyond color alone.

All x-axes retain zero and native units. The two ENSANUT BMI panels have identical limits and ticks to support the conditioning-set comparison. Other axes retain their own appropriate native scales; the CHNS per-year and ENSANUT per-decade age coefficients are not silently standardized. Adjustments are visible in every panel. Minimum font size is 8.3 pt at 7.2 inches, or **8.139 pt at the intended 7.06-inch manuscript width**. The figure is therefore intended for full two-column width.

The companion caption distinguishes seed range from confidence intervals, existing sample reference from population truth, and developmental workflow replication from new clinical replication. The Chinese guide explains axes, units, conditioning, marker encodings, useful patterns and limitations in accessible language. It links all 330 diagnostic estimates that are retained outside the main six-panel plot, including unfavorable rank-dependence and dispersion findings. No endpoint was selected on its result.

## Aggregate numerical validation

`python manuscript/paper_figures_v13_2026-11-04/render_open_retrieval.py` completed successfully. The builder:

- Verifies frozen SHA-256 identities for corrected `RESULTS.json`, `ALL_ENDPOINTS.csv`, the evaluation completion record and the endpoint contract; also verifies the completion record's declared output digests.
- Verifies twelve successful complete scheduled final tables of 3,000 rows, four expected authors, three prescribed seeds each and twelve distinct recorded table hashes.
- Verifies that the six panel keys equal the entire prespecified primary endpoint set.
- Cross-checks **all 366** primary/diagnostic CSV estimates and reference estimates against their aggregate JSON entries, with units and case identifiers; zero mismatches.
- Recomputes each of the twelve author/endpoint means and min–max ranges from its three aggregate estimates and compares them with the stored summaries; zero mismatches.
- Confirms every displayed seed estimate and contextual interval falls inside its plotted axis limits, and records every plotted value at full precision with its table hash and interval meaning.
- Checks that every visible text object is inside the figure boundary and every visible font is at least 8.3 pt. These checks complement, rather than replace, actual image inspection.

These comparisons inspect previously evaluated aggregate numbers. They do not independently refit regressions or establish model validity. The batch's separate 366-comparison numerical audit remains the authority for calculations from generated tables. The new figure does not open individual participant/generated rows, execute a generator, retrieve new clinical data or fit a new clinical reference.

## Actual visual inspection

Inspected the actual final PNG through the image viewer. All six panels, 36 open seed markers, twelve mean diamonds/ranges and six reference estimates/intervals are visible. The initial layout had a collision between the top-row x-axis labels and the ENSANUT row heading; this was corrected by expanding the figure height to 4.45 inches and moving the upper row. The final PNG has no observed title, adjustment, row-heading, axis-label, tick or legend collision and no clipping. All three nearly coincident E02 BMI seed points are visible as distinct vertically stacked circles. Some very short seed ranges are mostly covered by the mean diamond; the distinct seed points and full-precision CSV retain their spread.

The final PNG and vectors were regenerated after the numerical cross-check was extended to all 366 CSV entries. The visual outputs retained identical hashes, confirming that the added audit did not alter the plotted results. Final assembled manuscript PDF placement and page-scale inspection remain with the parent integration task.

## Source and output identities

The scientific report and original display builder were read for interpretation and figure semantics; their SHA-256 values are `14e809f25b2da8e5795e31e44fc502e9d976f52cf4d841bf3d6375be47a1613a` and `676b0bd2ba8385cab7d61f2fea642f7d00338074376ada463f8a82044693d04f`. No original display or frozen result was edited. Existing Figures 1–4 and the former Figure 5 are outside this new figure author's changes; the parent integration task controls their unchanged reuse and supplementary placement.

| New artifact | SHA-256 |
|---|---|
| `render_open_retrieval.py` | `dff554ff48a1fb8205eed8e144d9c81ba62d304e7188469dc977c1255723202d` |
| `fig5-open-retrieval.svg` | `1ba1db1adb2fbc4ac115beb0bb2d7d66717c3765079bba3b403e860ee3ff3ee1` |
| `fig5-open-retrieval.pdf` | `0272268925ecdd3aeabe5198dee4f2b570bf22fe110b30e32150a47ea0b910d7` |
| `fig5-open-retrieval.png` | `da2cb9c57bbcd8ba74d420f55400525bc2ff19a45b4cb132f7fd6b9aa6eebadd` |
| `FIG5_SEED_VALUES.csv` | `ad38d065851f4fc49f9f24de4be09dc351944fd9ef3603dd20c6ea215fb37a19` |
| `FIG5_AUTHOR_SUMMARIES.csv` | `351d4a86cc76bbb5ce8698ff5f8a97e0619ed374f1c357bf7c0a7a3ad50b2eab` |
| `FIG5_NUMERIC_BINDINGS.json` | `83b46a63ce8ee996d8fe53adb670d619a7c046256438ceb4418580c03e3fe682` |
| `CAPTION_FIG5.md` | `aca062b906babf8124e64758c8587f8c951d94a1a6c7d0259989d56157970368` |
| `FIG5_READING_GUIDE_ZH.md` | `10c568a85bd0f2dd5792ce6ae5a272cf631984cbbc3a113c1f9a8a35274ead73` |

Exact inputs and additional output metadata are recorded in `FIG5_NUMERIC_BINDINGS.json`. No frozen source, model, table or earlier manuscript was overwritten.
