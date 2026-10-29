# Independent final-candidate review before target generation

## Conclusion and scope

**No blocking implementation or provenance issue found.** Proceeding to the prespecified target-generation grid is consistent with the scientific artifacts reviewed, conditional on completion of the entire final source schedule and the normal release guard. This is not a finding of source compatibility or target validity.

Reviewed `FINAL_READY.json`, `REVISION_PLAN.json`, final code/specification/decision/check metadata, initial/final freeze receipts, and bound aggregate initial source feedback. No source covariate CSV, generated-row CSV, hidden participant table, prior target results, or current target analyses were read. No candidate generator was imported or executed; no frozen file was modified.

## S1 revision

The only biological parameter changes are the common BMI slope becoming male/female slopes `[9.557309727577666, 5.2]` and the corresponding residual CVs becoming `[0.7153743796657551, 0.5468139785420796]`. Age slopes, source centering, positive regularization, and assay parameters are unchanged. The code change correctly indexes the BMI slope by sex. The additive arithmetic-mean family is retained while adding a sex-by-BMI interaction.

The revised pooled-slope algebra checks out. With the declared source approximation,

`w = (1029 × 3.1²) / (1029 × 3.1² + 1643 × 3.2²) = 0.37018254401132633`,

the variance-weighted male/female slope is `w × 9.557309727577666 + (1−w) × 5.2 = 6.813000000000001`.

This is a population approximation under within-sex age/BMI independence and unregularized additive means. It does not guarantee the finite generated source OLS estimate, family-adjusted estimates, or the true sex-specific associations. The final decision correctly states those limits.

For outcome `Y = mu × R`, with independent mean-one residual multiplier and `Var(R)=CV²`, the correct law of total variance is:

`Var(Y) = Var(mu) + CV² × E(mu²)`

`= Var(mu) + CV² × (E(mu)² + Var(mu))`.

The stored CVs use exactly this denominator. Independent scalar recomputation reconstructs source TG variances `11599.29` and `3721`, matching the squared reported source SD anchors. Thus residual variability is not incorrectly added as `CV² × E(mu)²` alone, nor is covariate-driven variability double counted. The soft mean floor and imperfect source covariate reconstruction still prevent an exact marginal guarantee; this is acknowledged.

The source rationale matches the retained feedback: excessive female-source BMI Spearman association and excessive BMI separation across generated TG tertiles motivate the lower assumed female response, while the source pooled slope and marginal moments motivate the balancing calculation. The female coefficient is explicitly an unreported sensitivity choice, not a conversion of Spearman correlation to a conditional slope. The decision acknowledges the potential adverse location/quantile trade-off and leaves age slopes unchanged because the available age diagnostics give mixed guidance. No final-fit improvement is claimed before replay.

## S2/S3 retention and scientific scope

Both retained candidates have byte-identical generator and model specification files relative to their initial parents and correct `retain` lineage. Their decisions match the initial source summaries. S2 explicitly retains unresolved dependence discrepancies. S3 is explicitly a **source-challenged sensitivity parameterization**, not a numerically source-compatible model.

All three remain in the fixed target grid. Their inclusion supports a transparent comparison of the proposed alternatives; it does not justify describing every final candidate as source-compatible. Retention is not an automatic pass, and target agreement must not retroactively erase source mismatches.

## Integrity checks performed

- All final freeze/code/specification/evidence/replay hashes match `FINAL_READY.json`; both structure-plan and revision-plan hashes match their recorded identities.
- Every final has revision index one and the corresponding verified initial receipt hash as parent; s1 is marked `revise`, s2/s3 `retain`.
- Evidence, source recipe, unsupported-check definitions, shared source assumptions, and assay settings are unchanged. The assay function's AST is unchanged for all three candidates.
- Every checks-artifact hash matches its final candidate copy.
- Each final's `f1/f2/f3.json` matches the original complete initial portfolios for all three structures; its `r1/r2/r3.json` matches its own three original initial source replay reports.
- Each final's compact feedback copy matches `source_feedback/initial_compact.json`, and that hash matches `REVISION_PLAN.json`.
- The principal numerical source statements used in all three revision/retention rationales match the aggregate initial portfolio values.
- Only source-summary scalar algebra was calculated. No generator, target analysis, or new source simulation was run by this review.

Final freeze identities: s1 `686a8bc3fd327652088926d2a88c026ccba3c106074ed0d3af964fb229cacba9`; s2 `839a5f991fec04a4db2013b5098f837cb3c01658518d8ec27ee95af9031bd009`; s3 `0ed8f7c869576c3906b407c42fe98461df87196ff6e808f283e33bdee9bcd1c9`.

The structural-scope limits in the initial review continue to apply: positive BMI effects, selected sex-specific age patterns, assay transfer, joint-covariate assumptions, and restricted response geometries are shared choices. A fresh target comparison tests their prespecified projections; it does not identify a unique scientific structure, calibrate synthetic uncertainty, or establish an automatic winner.
