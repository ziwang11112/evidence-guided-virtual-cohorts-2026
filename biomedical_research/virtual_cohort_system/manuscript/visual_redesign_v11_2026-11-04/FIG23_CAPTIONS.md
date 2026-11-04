# Integrated evidence-results figures, v11

These are presentation-only redraws of frozen results. No empirical model, generated table, reference estimate or statistical analysis was changed.

## Figure 2. Relational evidence changes scientific analyses unevenly across two cohorts

The composite groups all six prespecified analyses by reference cohort. Panels (a–c, e–g) show native-unit regression estimates for all five E0 and five E1 Agent constructions and one prescribed statistical construction per information condition. E0 provides basic/marginal evidence; E1 adds relational evidence. Within each Agent group, authors A01–A05 run from top to bottom and are not paired across conditions. Small dots retain all three fixed final seed estimates, open diamonds show their constructor means, and horizontal segments show their three-seed ranges. The statistical constructions are displayed separately in slate. Dashed vertical lines are selected-sample reference estimates; shaded bands are CHNS 95% community-cluster CR1-t intervals or ENSANUT cluster-resampling stability bands. These bands and seed ranges do not define equivalence. HbA1c effects are percentage points per the predictor increment shown on each axis.

Panels (d, h) summarize the six Agent information contrasts as `100 × (MAE_E1 − MAE_E0) / MAE_E0`. MAE first averages the three seed absolute reference discrepancies within each constructor, then averages across the five constructors. Each bar retains its own endpoint; there is no pooled cross-endpoint score or inference from the bar color. Negative values indicate lower discrepancy. In panel (h), “BMI + G” denotes the BMI analysis additionally adjusted for glucose. All **24 distinct constructions, 72 distinct final tables and 216 coefficient estimates** remain represented, including the CHNS BMI deterioration. The underlying contrasts are descriptive developmental comparisons, not new independent clinical confirmations.

Layout: 7 × 5.25 inches. `fig2-evidence-results.pdf` is the vector publication asset; SVG and 300-dpi PNG are supplied for editing/preview.

## Figure 3. Supplied summaries enable joint reconstruction across several scientific analyses

Each column is one independently authored construction; each row is an analysis of the same generated tables. All three external-literature constructions (L01–L03) and three literature-plus-summary constructions (R01–R03) are retained. Each cell gives its native-unit mean across the three final seeds. Regression rows are BMI adjusted for age/sex, glucose adjusted for age/sex, and age adjusted for sex/BMI/glucose, respectively. Correlation rows concern glucose–HbA1c. HbA1c regression units are percentage points per the stated predictor increment; correlations are dimensionless.

The cell background encodes absolute relative deviation of that mean: `100 × |mean − reference| / |reference|`, using the stated nonzero reference. Within each cell, three small dots show the three seed statistics on a common signed-relative-deviation track, `100 × (estimate − reference) / |reference|`, with endpoints −100% and +100%; the central tick is zero deviation. Dot vertical offsets separate seed identities and carry no quantitative meaning. The original native values and every reference interval remain in the numeric binding; uncertainty intervals are not plotted in this matrix, and the normalized scale is a visual comparison rather than a statistical equivalence criterion. No values exceed the displayed track or color limits.

The display retains **six constructions, 18 distinct final tables, 30 constructor means and 90 seed statistics**. R explicitly received the 30 target summaries and metadata; its closer agreement concerns reconstruction of supplied information. Initial and final values were identical and are shown once. The 42 actual executions, 24 unique contents including trials, and separate statistical-calibration supplement retain their original identities and are not added to this matrix.

Layout: 7 × 4.65 inches. `fig3-summary-results.pdf` is the vector publication asset; SVG and 300-dpi PNG are supplied for editing/preview.

## Reproduction and numeric binding

- `render_evidence_results.py` uses three exact SHA256-pinned aggregate JSON inputs and supports both local `work/` and public `reports/` layouts. `--output` writes a separate reproduction directory.
- `NUMERIC_BINDINGS_23.json` contains all 306 original seed statistics, 102 constructor means, native reference intervals, six derived evidence-change percentages, every matrix normalization, input/output hashes and the no-new-experiment scope.
- Palette: navy `#182647`, blue `#4169B1`, violet `#8264B5`, coral `#D97762`, slate `#778394`. No green or teal is used. Violet identifies E0/L, blue E1/R; reference/statistical marks use slate, and coral distinguishes positive discrepancy change or increasing matrix discrepancy.
- Figure 2's endpoint-specific scales are preserved. Figure 3's common relative scale is stated explicitly and does not replace its printed native values.
