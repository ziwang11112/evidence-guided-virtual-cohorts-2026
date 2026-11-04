# C01 response to initial-trial feedback

Decision: **retain candidates/initial**, with no scientific revision. This decision precedes all three final delivery slots.

Combined feedback: `D:\AIR-014_ECRC_Paper_Clean_2026-08-16\biomedical_research\virtual_cohort_system\work\core_workflow_replication_2026-11-04\sessions\C01\feedback_c01_initial_8100.json`; SHA256 `c2755f9ce33869bf713c28364371e08723d7aafb32c6c455a7678a4bbeed0263`. The exact feedback hash was verified before this decision. The report states reference_read=false and binds the frozen candidate SHA256 `5bc6012d5a2adf3383170cad7286b109d733e983ec52715ec05ac9a666dd8a5e`.

The actual isolated trial produced n=3000. E1/E2/E3 all computed with ranks 4/4/5; all 27 supplied diagnostics computed. The reported quality counters contain zero nonpositive glucose and zero nonpositive HbA1c. These facts support computability for this trial, not target validity. No extra quality counter is inferred from an absent field.

| Approximate all-row comparison | Source | Trial | Raw difference |
|---|---:|---:|---:|
| all_bmi_mean | 24.100000 | 23.970425 | -0.129575 |
| all_bmi_sd | 3.300000 | 3.481953 | +0.181953 |
| all_glucose_mean | 5.360000 | 5.420240 | +0.060240 |
| all_glucose_sd | 1.070000 | 1.224069 | +0.154069 |
| all_hba1c_mean | 5.700000 | 5.694034 | -0.005966 |
| all_hba1c_sd | 0.630000 | 0.694831 | +0.064831 |
| all_gh_pearson | 0.619000 | 0.656588 | +0.037588 |

The whole-mixture Pearson correlation of .656588 is not a failed exact .619 constraint: the .619 algebraic constraint belongs to the constructed latent background, which cannot be recovered from delivered columns. Its exact check remains unavailable. Added between-component variation and different demographic composition can raise full-cohort dispersion and alter means/correlation. These were declared structural/transport choices before the trial. Their scientific applicability remains uncertain.

The observed discrepancies combine population mismatch, model assumptions and finite-sample variation. I do not attribute them entirely to Monte Carlo or calculate a significance score from individual SDs. Source estimator precision and repeated-draw uncertainty are unreported/unestimated here. Adjusting the inclusive mixture to minimize discrepancies against no-known-diabetes source summaries would change the intended model without resolving the eligibility mismatch.

All thirteen unavailable checks remain unavailable: background membership; known-diabetes-surrogate BMI summaries; six subgroup glycemic quantiles with unreported interpolation; two differently adjusted/weighted US age coefficients; and two weighted Finnish R-squared statistics. No reduced adjustment, weighting substitute, fabricated subgroup or quantile convention is introduced.

The untreated-to-known-diabetes surrogate, selection-count weight, uniform age, sex independence/zero conditional sex effects, BMI dependence and plasma-to-serum measurement transport remain explicit limitations. This feedback supplies no new evidence to identify replacements. I retain the candidate instead of making an unsupported revision.

Actions in this decision phase: read the supplied combined feedback; compactly re-read its calculations/unavailable checks and verify its SHA256; create only FINAL_DECISION.json and this response. No existing root input, source, task, ledger or candidate was modified; no additional search, generator execution, freeze, final row creation or target/other-author inspection occurred.
