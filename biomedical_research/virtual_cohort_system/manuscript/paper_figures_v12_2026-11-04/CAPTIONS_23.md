# Captions for native-unit result figures v12

## Figure 2

**External relational evidence improves several, but not all, generated analyses.** All six prespecified regression coefficients are shown in their native units: CHNS (a–c) and ENSANUT (d–f). E0 provides basic/marginal evidence; E1 adds relational evidence. Each Agent condition contains five independently authored generators, ordered A01–A05 from left to right; the statistical conditions each contain one prescribed generator. Small dots show all three final seed estimates per generator, open diamonds their means, and thin vertical segments their min–max ranges. Seed offsets only separate marks; matching author identifiers do not pair E0 and E1. Dashed lines are the selected-sample reference estimates. Gray regions show CHNS 95% community-cluster CR1-t intervals or ENSANUT cluster-resampling stability bands. These are distinct from within-generator seed ranges and do not define equivalence.

The figure retains 24 constructions, 72 distinct final tables and 216 coefficient estimates. Relative to E0, the E1 arm's mean absolute reference discrepancy decreased by 82.0% for CHNS glucose, 33.3% for CHNS age, 61.4% for ENSANUT age, 58.3% for ENSANUT BMI, and 47.4% for glucose-adjusted ENSANUT BMI; CHNS BMI discrepancy increased by 54.8%. Discrepancy is averaged across three seeds within each author and then across the five authors. These descriptive information contrasts do not imply that every E1 author or every generated coefficient is accurate. All reference populations were previously exposed during development.

## Figure 3

**Accessible summaries can be reconstructed as a joint dataset supporting several analyses.** Panels (a–c) show the three CHNS regression summaries in native HbA1c percentage-point units; (d–e) show the glucose–HbA1c Pearson and Spearman correlations. Purple L01–L03 constructions use external literature; blue R01–R03 constructions additionally receive 30 target summaries and metadata. Every constructor's three final seed estimates is shown, with open diamonds for means and thin min–max segments. The x-axis names denote independently authored generators, not paired versions of one generator. Dashed lines are reference summaries, explicitly available as inputs to R. Gray bands are the available 95% community-cluster CR1-t intervals for the regression references; no correlation interval is supplied. Vertical axes retain their native units and have endpoint-specific ranges.

The display contains all six constructors, 18 distinct final tables, 30 constructor means and 90 seed statistics. R reconstructs the regression summaries and both correlations more closely across these constructions; this tests supplied-information reconstruction, not independent prediction of hidden reference summaries. Initial and final outputs were identical and are displayed once. The physical execution and unique-content counts, source assumptions, marginal diagnostics and later statistical supplement remain separate in the supporting record.

## Figure files and reproduction

- `fig2-evidence-results.svg/png/pdf`, 7 × 4.65 inches.
- `fig3-summary-results.svg/png/pdf`, 7 × 4.6 inches.
- `render_evidence_results.py` reads three exact SHA256-pinned aggregate JSON files and supports local `work/` and public `reports/` layouts. `--output` creates a separate reproduction destination.
- `NUMERIC_BINDINGS_23.json` preserves every native plotted value, reference interval, source pointer, input/output hash and the six contrasts used in the caption. There is no normalized or reconstructed scatterplot in either figure.
- Interpretation in Chinese: `work/paper_figure_revision_v12_2026-11-04/FIG23_READING_GUIDE_ZH.md`.

This revision changes presentation only. It does not read participant records, regenerate data, refit scientific models or reinterpret the empirical design.
