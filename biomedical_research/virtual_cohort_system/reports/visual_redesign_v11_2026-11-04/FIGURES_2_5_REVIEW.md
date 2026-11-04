# Independent review of redesigned Figures 2–5

2026-11-04. **PASS: no scientific, numerical or visual blocking issue found.** This reviewer did not author/edit artwork, read patient/generated records, execute a generator or refit a scientific model. Native aggregate records and source code were inspected. Original PNGs and independently Poppler-rendered PDFs for all four figures were actually viewed. Exact reviewed hashes are in `FIGURES_2_5_REVIEW.json`.

## Scientific and numerical preservation

**Figure 2:** all six original scientific outcomes remain grouped by the two reference cohorts. All 216 seed statistics and 72 constructor-by-endpoint means match the pinned aggregate source. The six new percentage-change bars were independently recalculated from each seed's absolute reference discrepancy, then averaged within author and across the five authors in each condition. Every percentage matches; there is no pooled cross-endpoint score. Positive CHNS BMI discrepancy change and its native effect estimates remain visible. Agent authors are not paired across conditions. The statistical constructions remain separate. CHNS coefficient confidence intervals and ENSANUT stability bands retain their distinct meanings.

**Figure 3:** all 30 native constructor means and 90 seed values match the source exactly. All 30 cell colors and 90 seed-track coordinates were independently recomputed from their stated formulas. No shade exceeds the 0–100% scale, and no seed exceeds the −100% to +100% track, so no result is clipped or saturated by those limits. The matrix prints native-unit means and presents three-seed sampling behavior, not a new uncertainty estimate. The caption accurately says original reference intervals remain in the binding but are not plotted. Both visible footer and caption state that R received the target summaries: this is reconstruction, not a new hidden-target validation.

**Figure 4:** all 12 native estimates, conditional Wald limits and two source coefficients match v0.10. The structural inset uses the verified 11,509 subjects at four visits, years 0, 2, 4 and 6, producing 46,036 records; it is explicitly a schedule schematic, not an invented memory-score trajectory. Both displayed interactions are spline branches of the same mixed model. Lower-branch agreement and upper-branch uncertainty/disagreement are both visible. No unplotted source confidence interval is claimed.

**Figure 5:** all 21 generated estimates and intervals, seven native reference estimates and intervals, and two analytical dependence points match v0.10 exactly. Each estimate and each interval bound was independently transformed and inverted using `(value − reference)/reference_interval_half_width`; all checks passed. Reference asymmetry is retained. The dashed zero represents the sample-reference estimate, not biological zero. The caption makes clear that the coordinates do not define a statistical test, equivalence region or quality threshold. The two sensitivity points remain analytical scenarios only; there is no interpolating curve or new generated cohort. Primary glucose/female disagreements and all secondary terms remain visible.

## Visual and design inspection

The changes are structural and substantive: Figure 2 combines cohort-specific native effects with endpoint-specific change summaries; Figure 3 is an annotated analysis-by-construction matrix with visible seed glyphs; Figure 4 combines longitudinal output structure with a unified interaction display; Figure 5 combines one aligned seven-effect profile with a clearly distinct sensitivity card. Navy, blue, violet, coral and slate are used. No green/teal was observed. All labels, native-unit annotations, legends, reference marks and uncertainty bars fit their canvases. No clipping, overlapping annotations or missing panel was observed in either PNG or actual PDF render.

Captions are necessary parts of these figures: they identify adjustment sets, information conditions, distinct uncertainty meanings and the two normalized display formulas. Retain those explanations when integrating v0.11. Final size should be checked in the actual manuscript/template; this pass does not certify a venue's font-size policy.

## Decision

Approve Figures 2–5 and their supplied captions for v0.11 integration without changing results or experiments. A separate Figure 1 review and final integrated-paper layout check are still required. The supporting record retains historic failures and full original numerical outputs.
