# L01 source proposal review

5 November 2026. **PASS_TO_IMPLEMENT.** The proposed law is mathematically feasible and its source uses are sufficiently qualified for this bounded construction. No numerical-model correction, additional source search or extra draw is required. The source-feedback wording correction below must be carried into the implementation and corrected proposal before candidate freeze. This approves implementation, not a finished candidate or target validity.

Reviewed the L01 source request, construction proposal, deterministic check, search ledger, registry, curated source extracts, task/request metadata and the independent source audit in `SOURCE_AND_CODE_REVIEW.md`. Source artifact hashes match the registry. No old target result, patient/generated table, other candidate, or generator was read or executed. No random rows were created. The frozen controller was unchanged.

## Source meaning and construction

The rural Ashanti values are unadjusted Spearman correlations. The formula `r = 2 sin(pi rho_S / 6)` correctly supplies latent-normal correlation under the chosen continuous Gaussian copula. Monotone marginal transformations preserve its within-stratum Spearman relationship. It does not convert the reported source statistic into a raw Pearson correlation or adjusted BMI coefficient. L01 correctly names the additional assumption that community-pooled source dependence can be applied within each sex stratum; the synthetic pooled correlation can differ because sex-dependent margins induce a mixture.

Agongo arithmetic means and between-person marginal SDs remain distinct from conditional residual SDs, regression uncertainty and geometric means. L01 correctly quarantines the unresolved log-regression coefficients. Its BMI lognormal conversion reproduces the two reported sex-specific mean/SD pairs.

The Greiner rural sex ratios are geometric-mean ratios. Applying them as arithmetic-mean ratios is mathematically valid inside this model because each lipid has the same log variance in both sex strata. That is an explicitly declared model restriction. Combining these ratios with Agongo pooled arithmetic moments is a cross-study bridge; it is not a reported joint distribution. Subtracting between-sex variance before allocating within-sex lognormal variance is correct and leaves positive variance for both lipids. No rounded confidence interval is used as individual variability or precision weight.

The sex fraction, age support and within-quartile shape, age dependence, common copula across sexes, absent site clusters and external female/male-to-F/M mapping are honestly marked as assumptions. The averaged source age quartiles are described as shape choices, not the actual quantiles of a mixed source population. Full identification is not required for this construction; these assumptions must remain visible in the candidate and all three requested analyses should retain `partial` assessment.

## Independent deterministic checks

`recheck_l01_proposal.py` independently reconstructed the source numbers and algebra without sampling. Its retained result is `L01_ANALYTIC_RECHECK.json`.

- The correlation matrix is positive definite: eigenvalues 0.7003680, 0.8885673, 1.0871773 and 1.3238873. Its Cholesky factor matches the submitted deterministic check.
- The raw BMI/TC/HDL covariance matrices are also positive definite within each sex; smallest eigenvalues are 0.132679 and 0.145682 in the stated numerical units. This does not mean every pairwise covariance is positive.
- The lipid mixture recovers arithmetic TC mean/SD 3.23/0.92 mmol/L and HDL 1.14/0.38 mmol/L. Remaining within-sex variance is 0.82970736 and 0.1436971336 respectively, before division by the mixture squared means in the log-variance formula.
- Exact piecewise-linear quantile integration gives age mean 39.75 and SD 19.1322154145 years, matching the proposal.
- Positive lognormal margins, bounded age, binary sex and a finite mixture give all finite moments needed for the requested OLS and Pearson functionals. Positive-definite latent variation does not guarantee every finite sample has a usable design; retain the ordinary validation and unavailable-result rules.

The acknowledged TC<HDL support is real: the proposed law gives approximately 0.487% in M and 0.381% in F. These are analytic model probabilities, not generated or clinical observations. The task does not impose TC>=HDL, and the proposal does not use non-HDL clinically. Keep this limitation visible; do not silently clip or redraw to remove it.

## Required interface correction during implementation

`PROPOSED_CONSTRUCTION.md:119` currently suggests approximate executable source comparisons for Agongo moments, the six Ashanti correlations and Greiner age quantiles once conventions are assumed. The admitted audit is narrower: original source weighting is unreported; the source SD denominator, correlation tie/missingness details and quantile convention are also unresolved where stated. Under the frozen semantic-feedback v1 contract, unknown weighting or undefined/unsupported operators remain **not_computable**. An equal-weight model or assumed linear quantile convention does not establish the published study's method.

Replace that sentence with wording that retains the proposed comparisons as declared, unavailable source checks unless their reported semantics satisfy the existing adapter. Preserve `weights: not_reported` and unknown definitions in the sidecar. Generated-only diagnostics and deterministic model algebra can still be recorded with their actual scopes; they must not be presented as verified source comparisons. Geometric means/ratios and unresolved log regressions remain unsupported. No adapter extension or new acquisition is requested.

## Schema and measurement

The proposed six columns, 3,000 rows, adult age support, strictly positive BMI/lipids, F/M literals and string identifiers are compatible with the task. Lipids remain mmol/L in delivery; multiplying by 38.67 and reporting the raw-BMI coefficient times five matches mg/dL per 5 kg/m². Centering/scaling age and BMI is algebraically equivalent. Pearson residual correlation must use the two models with the identical intercept/age/F/BMI design and rows. The proposal correctly does not infer source pregnancy, diabetes, HIV, fasting or lifestyle exclusions for target rows, and unit conversion is not assay equivalence.

Implementation still needs the ordinary code/specification, actual-path, frozen-artifact and semantic gate reviews. Bind this decision and its analytic check honestly; neither artifact contains execution-backed source feedback. All reviewed file hashes and the exact correction are retained in `L01_SOURCE_PROPOSAL.json`.
