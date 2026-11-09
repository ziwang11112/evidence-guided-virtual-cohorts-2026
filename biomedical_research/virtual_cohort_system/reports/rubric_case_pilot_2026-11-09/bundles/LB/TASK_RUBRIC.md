# LIPIDS: developmental task rubric

Scope: `whole_cohort`, 3,000 fictional rows, `all_requested_questions`. Apply this same rubric in both rubric conditions. Requirements come from bundle-relative `task.json`, `request.json`, and `input/population_metadata.json`; no target outcomes, candidate results, or study-specific derived parameters define success.

## Task invariants

Verify ordered columns `id, age, sex, bmi, total_cholesterol, hdl_cholesterol`, unique nonmissing string identifiers, finite complete values, age ≥18 years, literal sex F/M, and positive BMI and both lipids. Deliver BMI in kg/m² and lipids in mmol/L. Do not invent an upper age limit, target age/sex/site/lifestyle mixture, or exclusions for fasting, pregnancy, HIV, diabetes, outliers, or TC≥HDL. Composition and joint covariate distributions are unspecified and require explicit evidence/assumptions.

For analysis multiply each lipid by 38.67 to mg/dL. Use unweighted OLS, an intercept, and the F indicator with M as reference. Raw age/BMI coding and `age10=(age-50)/10`, `bmi5=(bmi-25)/5` yield equivalent requested contrasts when scaling is handled consistently. Use the same eligible rows in both full models and the residual calculation.

## Stable analysis goals

| Goal ID | Required calculation | Relevant variation and joint checks |
|---|---|---|
| `K02-HDL-BMI` | `hdl_cholesterol ~ 1 + age + I(sex==F) + bmi`; five times the BMI coefficient, mg/dL per 5 kg/m² | Check design rank, BMI variation after age/sex adjustment, HDL distribution and conditional residual dispersion. |
| `K02-TC-BMI` | `total_cholesterol ~ 1 + age + I(sex==F) + bmi`; five times the BMI coefficient, mg/dL per 5 kg/m² | Check the same design and remaining BMI variation, TC distribution and conditional residual dispersion. |
| `K02-LIPID-RESIDUAL` | Pearson correlation of residuals from the two preceding models; dimensionless | Check matched rows/design, both nonzero residual variances, and TC–HDL joint dependence after adjustment. Marginal or rank correlation is a different statistic. |

Run every requested analysis. Report means, sample SDs and q10/q50/q90 for age, BMI and both lipids, both conditional RMS diagnostics, and the F fraction as specified in `request.json#/diagnostics`. Document diagnostic conventions, invalid/duplicate rows and all noncomputable results. Inspect subgroup support, tail behavior, collinearity and deterministic lipid relationships. Do not prescribe coefficient signs, correlation direction, effect magnitudes, or extra numerical success thresholds.

## Evidence and assumptions

For every adopted claim preserve its source population, selection, measurement, estimator, adjustment, unit, weighting, uncertainty and locator. Name distributional, composition and transfer assumptions; absence of a reported relation does not establish zero dependence. Source reconstruction and target transfer are separate findings.

Relevant definition boundaries, with exact admitted locators:

- `sources/curated/AGONGO_2018_CURATOR_EXTRACTION.json#/regression_context`: univariate log-lipid coefficients have unresolved log base and differ from requested adjusted raw-scale coefficients; reported confidence intervals are estimation uncertainty, not individual dispersion.
- `sources/curated/GREINER_2021_CURATOR_EXTRACTION.json#/operator_definitions/geometric_mean_positive` and `/implementation_disposition`: geometric means differ from arithmetic means; regression scale and adjustment remain unresolved for direct substitution.
- `sources/curated/OBIRIKORANG_2015_CURATOR_EXTRACTION.json#/operator`, locator **Table 7, lower-left rural / upper-right urban**: community-specific unadjusted Spearman correlations differ from adjusted Pearson residual correlation.
- `input/population_metadata.json#/measurements/lipids` (**Target supplement pp.5–6 lipid methods; repository units metadata**) describes immediate CardioChek Plus venous-EDTA measurement and unestablished fasting status. `/unit_mapping` specifies numerical conversion, not assay equivalence. Use this admitted metadata only, without opening the target supplement.

## Assessment record

For each goal record `id`, `analysis`, `basis`, `reference_role`, `check`, `comparison`, `finding` with artifact, `assessment`, and `next_action`. Roles are task invariant, source reconstruction, or no numerical reference; target evaluation remains external. Compare descriptively except for exact task invariants. Use demonstrated-for-stated-scope, contradicted, unresolved, or not-applicable-with-reason. Planned or noncomputable checks cannot establish success; computability alone cannot establish scientific support. State consequential assumptions and descriptive inference limits; provide no overall quality score.
