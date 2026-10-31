# Independent final numerical audit

25 October 2026 (client date). **Passed for cohort construction, target correlations, point losses, group aggregation and prediction-lock integrity.** This audit was authorized after target evaluation. It uses the same frozen queries and eligibility; no new model, outcome, subgroup or query was introduced. No root report or forecast was edited.

## Independent calculation

Read the original target Excel/CSV files directly. Rebuilt NAGALA eligibility using finite positive BMI/TG/FPG, age 20–75, FPG <6.1 mmol/L and actual recorded sex codes 0/1. Rebuilt DIETFITS pairs with a participant-by-event pivot, positive finite baseline/six-month weight, insulin and glucose, positive baseline TG and known baseline sex. Checked unique participant/event keys and sex consistency. Six-month TG was not an inclusion requirement.

For every query, regressed both queried variables on an intercept plus the fixed controls using `numpy.linalg.lstsq`, then computed their residual dot-product correlation. This implementation does not call the evaluator's covariance/Schur-complement function. For the intervention HOMA change, independently used the sum of the log insulin ratio and log glucose ratio.

| Target | Deposited participants | Eligible | Q1 | Q2 | Q3 |
|---|---:|---:|---:|---:|---:|
| NAGALA | 15,464 | 15,450 | 0.346918743481 | 0.069054257019 | 0.205441615889 |
| DIETFITS | 609 | 464 | 0.409731256746 | 0.008529414407 | -0.180164414141 |

Maximum absolute discrepancy from the evaluator's target correlations was **1.11e-14**.

## Forecast and aggregation checks

Independently loaded all **22 model/case forecast arrays**, recomputed each point as `mean(tanh(z), axis=0)`, and calculated the three squared errors against the independently obtained targets. All point estimates matched exactly; maximum loss discrepancy was **2.28e-15**.

Recomputed every group in `results/group_summary.json`, including the two single-source references and both heterogeneity-prior sensitivities. Agent group values are the **mean of individual run losses**, not loss of an ensemble point estimate. Cases receive equal weight. All reported group loss values matched within **2.28e-15**.

| Procedure | Population Q1 MSE | Intervention Q1 MSE | Equal-case Q1 MSE | Equal-case three-query MSE |
|---|---:|---:|---:|---:|
| Direct Agent A, mean of three runs | 0.0001283751 | 0.0021461084 | 0.0011372417 | 0.0052054325 |
| Cohort Agent B, mean of three runs | 0.0002394308 | 0.0027601125 | 0.0014997717 | 0.0054338075 |
| Conventional random-effects C, main prior | 0.0022773849 | 0.0102144993 | 0.0062459421 | 0.0042864483 |

These values support the stated descriptive conclusions:

- B's mean run loss does **not** beat A on the primary Q1 in either case, and B has higher equal-case primary loss. This is a group-level statement; it must not be rewritten as every B run losing to every A run.
- Both Agent groups have lower primary Q1 loss than the particular main random-effects baseline in these two cases. That favorable primary result does not establish an advantage of virtual records over direct Agent inference.
- C has lower equal-case loss over all three fixed queries than either Agent group. This is a **secondary, mixed pattern**, not permission to replace the primary endpoint or claim C wins every case: in the intervention case C's three-query loss is higher than A's and B's, while its population performance drives the aggregate advantage.
- Source 1 is the strongest Q1 source reference for the population case; source 2 is strongest for intervention. Choosing those sources after seeing the target is an oracle-style diagnostic, **not a deployable prespecified source-selection method**. The fixed source-specific forecasts can be reported individually, but their post-hoc best-per-case combination is not a fair primary comparator.

## Loader repair and freeze integrity

The deposited NAGALA header says `Sex, 1:Men, 2:Women`, but the actual data contain **8,430 code-1 records and 7,034 code-0 records**. The initial loader's 1/2 restriction retained only one sex and caused a singular adjustment matrix. The recorded repair admits the actual 0/1 codes and adjusts for the corresponding binary indicator. Correcting binary-label polarity alone would not change an intercept-adjusted partial correlation; restoring the excluded sex is the material eligibility correction.

Read `EVALUATOR_REPAIR.json` and checked the original prediction freeze. All **52 saved hash comparisons** passed, covering **40 distinct run/forecast files**; the forecast-index hash also remained unchanged. Thus all scored forecast arrays are byte-identical to the pre-access frozen artifacts. The evaluator was repaired after target access, as transparently recorded. These targets are now exposed and cannot be presented as untouched tests for subsequent adaptive redesign.

## Audit scope and interpretation

This final audit independently recomputed the target point associations, all point losses and their aggregation. It did not independently regenerate all 500 bootstrap replicates or the WIS noise-convolution draws. Their formula/control-flow checks and numerical scoring primitives were covered in the preceding source-only audit and smoke check; this document does not assert a separate full stochastic uncertainty replication.

The ranking describes two retrospective target studies and a small set of Agent constructions. It does not establish calibrated superiority across studies, biological discovery, or patient recruitment replacement. As recorded in `EXECUTION_AUDIT.md`, B's scored forecasts are analytical functions of joint model draws; the representative synthetic rows validate the sampler. No additional inferential information comes from their count.

**Supported decision:** the pilot has not demonstrated that the virtual-cohort procedure improves over a capable direct Agent. Preserve the negative primary comparison and the mixed secondary results; do not expand the system on an asserted virtual-data advantage.
