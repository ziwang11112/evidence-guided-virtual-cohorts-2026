# Independent review of the three frozen initial candidates

## Scope and conclusion

Inspected `INITIAL_READY.json`, `STRUCTURE_PLAN.json`, and each initial candidate's generator, specification, evidence, source-replay/check metadata, decision record, and freeze receipt. No source covariate rows, generated rows, hidden participant rows, or target results were read. No candidate program was imported or executed. No frozen artifact was modified.

**No blocking implementation/specification mismatch was found.** The three candidates differ mathematically, not just by seeds or cosmetic parameters. Their decisions distinguish a proposed source-compatible construction from demonstrated source fit and explicitly await controller replay. This review does not establish numerical source compatibility or independently re-extract the cited papers.

## Mathematical implementation

| Candidate | Implemented construction | Audit finding |
|---|---|---|
| s1 | Additive arithmetic conditional mean, smooth positive regularization, sex-specific constant-CV mean-one lognormal noise | `exp(sigma*Z - sigma²/2)` correctly preserves the regularized conditional arithmetic mean. `sigma²=log(1+CV²)` is correct. The stated independent-covariate variance decomposition exactly reproduces both stored CVs. The smooth floor is a mean regularizer, not outcome truncation. |
| s2 | Tanh-saturating BMI effect on log location, sigmoid female age effect, linear male log-age effect, normal log residuals | Exponentiating log location without subtracting residual variance is correct for the declared median/log-location parameterization. Arithmetic conditional mean includes `exp(sigma²/2)`. The stored moment-equivalent marginal median and local slope `6.813/source mean` reproduce their declared formulas; their use as conditional anchors is explicitly approximate. |
| s3 | Logistic probability of an elevated latent state; sex/state-specific gamma components | Gamma shape `1/CV²` and scale `mean/shape` correctly yield the stated component means and CVs. The stated local-link slopes and logistic-normal intercept adjustment reproduce the stored values. The intercept adjustment changes the probability at the centered covariates, so the original local slope anchor is not an exact derivative at the adjusted center; the specification already disclaims an exact marginal slope match. |

Scalar specification algebra was independently checked with NumPy. It passed for s1 CVs, s2 median and slope conversions, and s3 probability-link slopes/intercept. This was algebra only, not simulation or fitting.

All generators use only `age`, `sex`, `bmi`, `tg_assay`, and the supplied RNG seed. No ID, row position threshold, cohort label, target-case name, fitted target statistic, filesystem read, network call, or hidden-data lookup is present. Row order determines allocation of random draws, but does not select a biological model. The returned DataFrame is a deep copy of the input with one appended outcome column.

The identical measurement function leaves `legacy_proxy` values unchanged and applies `12.45 + 1.022*legacy` only to `unblanked_2021_2023`. It rejects unknown regimes. This matches the task-supplied forward bridge. The builder explicitly treats equivalence of the literature assays to the legacy proxy as uncertain, especially for Oh, and does not represent the equation as population association evidence. Coefficient uncertainty is not propagated.

## Evidence and shared diagnostic design

Evidence, source recipe, unsupported-check file bytes, and every shared assumption definition are identical across all three candidates. The declared source-context input hashes are identical as well; this review did not open those CSVs. The evidence references two admitted sources, their retained artifact hashes, reported populations/selection, units, locators, adjustment sets, and uncertainty. Reported moments, transformed anchors, and modeling assumptions are separated in parameter provenance.

The 71 evidence entries consist of 46 replayed statistics, 23 explicitly unreplayed/ambiguous statistics, and two contextual assay entries. All replayed statistics are labeled approximate. Twelve of the 46 replay checks are source-input age/BMI moments fixed by the covariate construction; **34 depend on generated TG**. The fixed-input checks are useful reconstruction diagnostics, but must not be counted as twelve extra validations of generator behavior. Multiple statistics and seeds share inputs and source participants.

The recipe keeps arithmetic moments, Spearman correlations, quantiles, cumulative threshold counts, and covariate moments conditional on generated TG categories as distinct estimands. It does not reverse conditional distributions or turn marginal correlations into regression coefficients. Ambiguous Oh Table 2 summaries remain `reported_other`, and metabolic-adjusted, mixed-model, and co-twin estimates remain unreplayed rather than being silently substituted. Unsupported statistics are not dropped from the evidence record.

The large declared source-context row counts are numerical Monte Carlo sample sizes. They do not multiply clinical source sample sizes or reduce uncertainty in the published studies. Age-BMI independence within sex, source marginal shapes/support, assay transfer, and cross-population transport remain common assumptions.

## What apparent robustness could follow from construction

All three candidates impose a positive BMI effect and a weakly decreasing male age effect together with an increasing female age effect. These choices are informed by selected source summaries but are not identified conditional relationships from those summaries. The common independence assumption in source covariates further restricts the possible joint distributions. The pooled adjusted age coefficient is still a projection under the target covariate distribution and need not mechanically have either sex-specific sign.

For s1, away from positive regularization, `E[log(TG)|x] = log(mu(x)) - sigma²/2` on the legacy scale. A positive additive BMI slope therefore produces negative log-mean curvature even though the arithmetic mean is linear. The positive assay offset changes magnitudes but preserves concavity with respect to an affine positive mean under the common noise law. Near the soft floor, the regularization can change curvature.

For s2, legacy conditional log mean contains `beta*w*tanh((BMI-center)/w)`: it is convex below the center and concave above it, with a prescribed plateau. The assay offset adds a further nonlinear transformation, so native-scale expected log curvature is not simply the unmodified tanh curvature.

For s3, raw conditional mean is `low + (high-low)*p(x)` with logistic `p`. Both raw mean and expected log outcome are weighted combinations of two fixed component expectations. Their curvature follows logistic membership, changing at its inflection and saturating at the extremes. The latent state is not an observed diagnosis or evidence of two actual biological classes.

Consequently, agreement among these three families would demonstrate stability **within these selected structural and shared transport assumptions**. It would not show that the literature identifies the shape, that all source-compatible joint laws agree, or that the shape is novel. Disagreement would reveal sensitivity within this set. The fresh target period adds a held-out empirical check of the prespecified projected age/curvature conclusions; it does not remove underidentification in the source evidence or establish calibrated uncertainty. Full-domain quadratic contrasts must remain distinguished from local conditional curvature.

## Frozen identities reviewed

- s1 initial freeze: `d43e2c8c615429931c22aff978e8df30289da9504e5b3d9c7674dc87dcace3fa`, UTC 2026-10-29 00:51:00.573476.
- s2 initial freeze: `a20729ac78a1ecf36c9e0d6ddf36f7fe179e7ffaf9139c5fec89f96bc2cc3f6b`, UTC 2026-10-29 00:51:01.443844.
- s3 initial freeze: `6c63aa25c279a65bb287f4af39fcdf299cd90011663193a7279a0157b085e7db`, UTC 2026-10-29 00:51:02.293599.

All three freeze receipts match `INITIAL_READY.json`. Scientific revisions remain the builder's decision from the complete source-only feedback, without controller-prescribed coefficient changes or desired target signs.
