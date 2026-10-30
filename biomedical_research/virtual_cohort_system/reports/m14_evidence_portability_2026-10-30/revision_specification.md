# M14-A: one source-supported conditional-mean revision specification

30 October 2026. Status: specification only. No candidate was built, calibrated, generated or evaluated in M14-A. This is a limited structural sensitivity, not a demonstrated correction of M13-B.

## Decision and source

Retain one possible revision: substitute the complete conditional-mean equation from Pasco et al. (2012), Table 4 Model 3, for the incumbent mean equation. The study is selected for an adult, population-based, non-NHANES DXA model using the available predictors. It is not selected by evaluating its predictions on the exposed target. Models 4/5 require unobserved lean mass/BMC and are ineligible. Do not average coefficients from incompatible studies or optimize any coefficient against M13-B.

Source: https://doi.org/10.1371/journal.pone.0029580 . Outcome is fat mass as percent of DXA whole-body mass including BMC. Let c = BMI - 26.37, M = 1 for men and 0 for women, and A = age in years:

`mu = 37.8 - 16.7*M + 1.62*c - 0.06*c*c + 0.02*A - 0.17*M*c + 0.03*M*c*c + 0.04*M*A`.

Use the printed coefficients without recovering extra digits. The original model includes these terms simultaneously; it is not a set of independent marginal relationships. The published cohort is almost entirely White and uses Lunar DPX-L/Prodigy Pro. Device software, coefficient covariance and conditional residual law are not identified by this equation.

## Isolate one scientific change

The designated parent is the existing M13-A initial candidate `work/m13/build01/candidates/initial/`. It supplies one fixed residual mechanism for isolating the mean substitution; it is not selected by ranking target performance. If this later experiment is admitted, preserve its bounded beta residual mechanism, source-anchored base SD 4.31 pp, female/male SD ratio 1.10, scale 1.0, mean guards 0.5/99.5 pp and variance-fraction cap 0.95 unchanged in both arms. They remain inherited assumptions; this audit does not validate them. The old shared/male location shifts are zero and remain zero. Asian blending is inactive in the proposed White-only primary domain. Only the mean expression changes. The release's historical-integrity record binds the exact parent bytes.

Pasco's pooled regression S=4.07 pp is retained as a source descriptor. Do not replace the parent residual scale with it in the primary comparison: that would introduce another scientific change and would not establish a target conditional variance law. No new sex-, age- or BMI-specific spread parameters are allowed. The revised conditional mean should also be inspected algebraically so stochastic noise cannot disguise a transcription error. Deterministic means alone are not a virtual patient dataset.

No source-score optimizer is prescribed. Matching a published conditional equation is different from reconstructing source participants. Without their joint covariates, a simulated marginal S, R-squared or coefficient replay cannot be treated as an exact source-data check. Verify the expression, centering, coding, units, source membership and boundary behavior; do not invent source covariance to make summary fit appear exact.

## What this can and cannot change

The substitution can change mean levels, conditional BMI shape, sex differences and age association. Marginal spreads may change because the mean varies across covariates; that is not evidence of a corrected residual law. Target regression projections also depend on target covariates and are not equal to local derivatives of this formula.

Source algebra gives age effects of 0.20/0.60 pp per decade for women/men, and at BMI 26.37 local BMI derivatives of 8.10/7.25 pp per 5 units. The symmetric BMI contrast m(28)-2m(24)+m(20) is -1.92/-0.96 pp. These are formula properties, not new biological findings or predictions of target-analysis success.

This revision cannot establish scanner equivalence, repair sex-specific residual spread, identify transport uncertainty, recover individual true values or prove general utility. Do not treat separate coefficient CIs as a joint covariance matrix or give alternative source equations probability weights. Conditional simulation intervals must be labeled as excluding unresolved source/model/transport uncertainty.

## Requirements before any later execution

1. Register an actually accessible, separate adult cohort with measured age, BMI, sex and total-body DXA fat percentage, and metadata sufficient to define recruitment, scan completion, units, denominator, device, software and analysis settings. No M13-B participant/outcome or source-cohort participant can be reused as independent confirmation. A different paper using the same participants is not a new cohort.
2. Primary domain: White adults aged 20-59, BMI 18.5 to less than 30; any BMI 30-35 extension is separately labeled. These limits are a conservative test domain, not a claim of established validity. Other ancestries are outside the Pasco-supported primary transport claim. Verify estimability and sampling design before selecting analyses.
3. Prefer a demonstrably compatible measurement pipeline. A same-vendor name alone is insufficient. If an exact bridge is unavailable, register the identity mapping explicitly as an unverified transport scenario; its result can test empirical portability but cannot establish measurement calibration or identify the cause of a discrepancy. Do not synthesize a bridge from the three incomplete comparisons in this audit.
4. Freeze both arms, allowed inputs, evidence ledger, seed schedule, analysis operators and a small endpoint set before access to the new outcome. Use the same observed covariates, residual mechanism and seeds. Report the prior M13-B result as exposed development evidence.
5. Evaluate scientific uses with the same operators on real and generated data: adjusted BMI and age association, a predeclared nonlinear contrast, mean level and spread preservation. Keep at least one non-fitted subgroup/joint analysis if supported by the admitted data. Supplied equation relationships are transport tests, not unreported discoveries. Choose that additional analysis and any practical tolerances from the intended use before outcome access; no post-result substitution.
6. Report every scheduled analysis and both arms. No per-endpoint regeneration, target intercept/slope fitting, favorable-seed selection, significance-only success rule or averaging of dependent endpoint wins. Source uncertainty remains separate from Monte Carlo variation. If the small comparison does not improve useful analyses without unacceptable trade-offs, stop this mean-substitution branch.

No qualifying new cohort has been admitted here. Therefore this specification does not start another experiment. The bounded M14-A audit ends with this document; the old body-fat target-calibration branch remains closed.
