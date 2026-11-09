# GLYCEMIA: developmental task rubric

Scope: `whole_cohort`, 3,000 fictional rows, `all_requested_questions`. Apply this same rubric in both rubric conditions. Requirements come from bundle-relative `task.json` and `request.json`; no target outcomes, candidate results, or study-specific derived parameters define success.

## Task invariants

Verify the declared columns, units, unique nonmissing `row_id`, finite complete values, integer age 25–79, binary `female`, positive BMI and HbA1c, and glucose strictly between 0 and 126 mg/dL. Require exactly 375 rows in each `female` × age-band cell (25–39, 40–54, 55–69, 70–79). Preserve the declared Mexico selection context, 8–12-hour fasting and measurement restrictions; do not assert medication or anemia exclusions. Unrepresented selection features require a stated construction assumption, not claimed row-level verification.

Use equal-cell WLS with 1/8 total mass per cell. This is an analytical design, with no national-survey interpretation. Define `age10=(age-50)/10`, `bmi5=(bmi-25)/5`, `glucose10=(glucose-100)/10`. HbA1c is in percent; coefficient differences are percentage points.

## Stable analysis goals

| Goal ID | Required calculation | Relevant variation and joint checks |
|---|---|---|
| `Q1_age10` | `hba1c ~ 1 + age10 + female + bmi5 + glucose10`; age10 coefficient, percentage points per 10 years | Check age variation after the other covariates, design rank, age–glucose–BMI dependence, and HbA1c residual variation across the prescribed cells. |
| `Q2_bmi5` | `hba1c ~ 1 + age10 + female + bmi5`; bmi5 coefficient, percentage points per 5 kg/m² | Check BMI variation conditional on age and female, and the BMI–HbA1c joint distribution. |
| `Q3_bmi5` | `hba1c ~ 1 + age10 + female + bmi5 + glucose10`; bmi5 coefficient, percentage points per 5 kg/m² | Check remaining BMI variation after glucose adjustment, collinearity, and HbA1c residual variation. Describe the Q2/Q3 difference without prescribing attenuation, direction, or magnitude. |

Run all three on the delivered cohort. Report all provider-defined marginal, quantile, joint/conditional, invalid-row, duplicate-row and uncomputable diagnostics. Distinguish duplicate identifiers from repeated covariate profiles. Inspect truncation near the glucose eligibility boundary, covariate support within cells, and deterministic or collapsed biomarker relationships. These are descriptive checks, not additional clinical outcomes or invented acceptance cutoffs.

## Evidence and assumptions

For each adopted source claim, retain its exact estimator, units, selection, adjustment, weighting, uncertainty and locator. Reproduction in its source context does not establish transfer to this cohort. Separate individual dispersion from uncertainty of an estimate; name assumptions for joint dependence, distribution shape, selection and transfer. Unreported relationships are not automatically zero.

Examples of estimator distinctions in admitted evidence:

- PMC2551641, `sources/gateway/fac9d24329896a04d65a0f5858c64238365c01bc0b9616e64ee5bc00271c64f6.xml`, **Statistical analysis / NHANES**: complex-survey weighting differs from this equal-cell design.
- PMC6458679, `sources/gateway/e36df343e42bf6e96a6c392fd5f3409a0eaa612a6f4797c1e626ba7917d327fb.xml`, **Statistical analysis**, paragraph beginning “Linear regression was applied”: distinguish age/sex-adjusted coefficients from predictive margins and R².

## Assessment record

For every goal record `id`, `analysis`, `basis`, `reference_role`, `check`, `comparison`, `finding` with artifact, `assessment`, and `next_action`. Roles are task invariant, source reconstruction, or no numerical reference; target evaluation remains external. Comparisons are descriptive unless an exact task invariant applies. Use demonstrated-for-stated-scope, contradicted, unresolved, or not-applicable-with-reason. Planned checks and noncomputable results cannot establish success. A computable coefficient alone does not demonstrate scientific support. Report assumption dependencies and permitted descriptive claims; provide no overall quality score.
