# Live Agent integration: two research requests

The bounded live integration produced scientifically analyzable whole-cohort data for both requests. It demonstrated some useful relationships, but the glucose-adjusted BMI relationship in request B did not match the real reference. Both authors retained their initial models after feedback, so this run provides no evidence of post-feedback revision benefit.

This is a developmental comparison against the previously exposed CHNS 2009 selected sample: 6,631 complete cases, ages 35–74, and 218 communities. It is not a new untouched confirmation, a nationally representative estimate or known population truth. The generator authors did not receive target outcome values or results. Both authors closed before the evaluator read the reference.

## Actual work and counts

- Two fresh authors retrieved the approved original literature, extracted evidence, authored distinct stochastic programs and parameter specifications, received generated-only diagnostics and semantic source-check statuses, and explicitly chose retention.
- Eight physical executions succeeded: one trial and three delivery seeds per request. Each output has 3,000 rows; 24,000 physical synthetic rows include trials. The six unique delivery tables contain 18,000 rows. Six final-stage records alias those same tables and are not additional samples.
- All 12 initial/final evaluation slots are preserved. Seeds are 7301, 7302 and 7303; the two trials use 7300. No revision-trial or new final-generation run was needed.
- The v1 feedback interface ran, but all nine A and eight B declared source checks were unavailable. A completed feedback artifact is not a successful source replay or numeric calibration.

## All model coefficients

A: HbA1c ~ intercept + BMI + age + female. B adds serum glucose. Units are HbA1c percentage points per predictor unit (BMI kg/m²; glucose mmol/L; age years; female 0/1). The reference interval is community-cluster CR1-t 95%. Generated ranges span the three fixed seeds and are not confidence intervals.

| Request | Term | Reference estimate [95% CI] | Generated point-estimate range | Generated conditional interval directions |
|---|---|---:|---:|---|
| A | const | 3.59026 [3.34708, 3.83344] | 4.08280 to 4.53662 | positive, positive, positive |
| A | bmi | 0.05495 [0.04573, 0.06417] | 0.02445 to 0.03894 | positive, positive, positive |
| A | age | 0.01530 [0.01322, 0.01739] | 0.01337 to 0.01483 | positive, positive, positive |
| A | female | -0.04530 [-0.08971, -0.00088] | -0.04781 to -0.00765 | inconclusive, inconclusive, inconclusive |
| B | const | 2.54518 [2.32942, 2.76095] | 3.34327 to 3.65876 | positive, positive, positive |
| B | bmi | 0.02246 [0.01526, 0.02967] | -0.00949 to -0.00098 | negative, inconclusive, inconclusive |
| B | glucose | 0.39291 [0.36175, 0.42406] | 0.39164 to 0.43870 | positive, positive, positive |
| B | age | 0.00811 [0.00639, 0.00983] | 0.00152 to 0.00275 | inconclusive, positive, inconclusive |
| B | female | 0.02599 [-0.00776, 0.05974] | -0.04907 to -0.01457 | negative, inconclusive, inconclusive |

Final estimates are byte-identical to initial estimates because both final decisions retain the same frozen candidates and output files. There is no before/after improvement to infer.

Generated HC3-t intervals condition on each model and synthetic draw. They exclude source, parameter, transport and model uncertainty. Their overlap with a reference interval is not an equivalence test.

## Scientific interpretation

Request A recovers positive BMI and age associations. Its BMI association is weaker than the reference estimate across all three seeds. Its age estimates are on a similar scale to the reference. Female point estimates are negative, but all three generated conditional intervals include zero, whereas the selected real sample has a narrowly negative interval.

Request B reproduces a strong positive glucose association of roughly the reference scale. Its primary, glucose-adjusted BMI coefficient is negative in all three draws, whereas the reference coefficient is positive with a positive interval. Only one generated BMI interval is entirely negative; the other two cross zero. Its age coefficient is positive but appreciably smaller than the reference. The reference female interval includes zero, so its positive point estimate is not evidence of an established positive female effect.

The important limitation is joint structure: positive marginal BMI–HbA1c association and a realistic glucose–HbA1c association do not determine the BMI coefficient after glucose adjustment. This is an algebraic property of the requested multivariable analysis, not a new post-hoc endpoint. The sources did not identify the needed conditional slopes, and the authors marked them as assumptions.

## Marginal distributions

These are descriptive checks, not targets imposed on the authors or proof that a real sample mean equals a population mean.

| Request | Variable | Summary | Reference | Generated range |
|---|---|---|---:|---:|
| A | age | mean | 52.74257 | 54.12500 to 54.83100 |
| A | age | sd | 10.43179 | 11.42962 to 11.50405 |
| A | age | q10 | 39.00000 | 38.00000 to 39.00000 |
| A | age | median | 53.00000 | 54.00000 to 55.00000 |
| A | age | q90 | 68.00000 | 70.00000 to 71.00000 |
| A | female | mean | 0.53687 | 0.54333 to 0.55733 |
| A | female | sd | 0.49868 | 0.49678 to 0.49820 |
| A | female | q10 | 0.00000 | 0.00000 to 0.00000 |
| A | female | median | 1.00000 | 1.00000 to 1.00000 |
| A | female | q90 | 1.00000 | 1.00000 to 1.00000 |
| A | bmi | mean | 23.69989 | 23.81013 to 23.99155 |
| A | bmi | sd | 3.40632 | 3.45609 to 3.51257 |
| A | bmi | q10 | 19.53125 | 19.64408 to 19.81418 |
| A | bmi | median | 23.42399 | 23.58939 to 23.70895 |
| A | bmi | q90 | 28.10096 | 28.39912 to 28.63144 |
| A | hba1c | mean | 5.67531 | 5.79646 to 5.81722 |
| A | hba1c | sd | 0.95357 | 0.91776 to 0.96699 |
| A | hba1c | q10 | 5.00000 | 5.07457 to 5.08584 |
| A | hba1c | median | 5.50000 | 5.58829 to 5.61116 |
| A | hba1c | q90 | 6.30000 | 6.47463 to 6.60751 |
| B | age | mean | 52.74257 | 54.12500 to 54.83100 |
| B | age | sd | 10.43179 | 11.42962 to 11.50405 |
| B | age | q10 | 39.00000 | 38.00000 to 39.00000 |
| B | age | median | 53.00000 | 54.00000 to 55.00000 |
| B | age | q90 | 68.00000 | 70.00000 to 71.00000 |
| B | female | mean | 0.53687 | 0.54333 to 0.55733 |
| B | female | sd | 0.49868 | 0.49678 to 0.49820 |
| B | female | q10 | 0.00000 | 0.00000 to 0.00000 |
| B | female | median | 1.00000 | 1.00000 to 1.00000 |
| B | female | q90 | 1.00000 | 1.00000 to 1.00000 |
| B | bmi | mean | 23.69989 | 24.83494 to 24.97899 |
| B | bmi | sd | 3.40632 | 3.17641 to 3.44427 |
| B | bmi | q10 | 19.53125 | 21.21797 to 21.30375 |
| B | bmi | median | 23.42399 | 24.30950 to 24.36940 |
| B | bmi | q90 | 28.10096 | 29.11972 to 29.46803 |
| B | hba1c | mean | 5.67531 | 5.72701 to 5.76341 |
| B | hba1c | sd | 0.95357 | 0.83048 to 0.91678 |
| B | hba1c | q10 | 5.00000 | 5.03969 to 5.04439 |
| B | hba1c | median | 5.50000 | 5.56755 to 5.57500 |
| B | hba1c | q90 | 6.30000 | 6.39298 to 6.44180 |
| B | glucose | mean | 5.48777 | 5.49483 to 5.52523 |
| B | glucose | sd | 1.54455 | 1.37700 to 1.48088 |
| B | glucose | q10 | 4.41900 | 4.21350 to 4.25911 |
| B | glucose | median | 5.17000 | 5.17295 to 5.20520 |
| B | glucose | q90 | 6.57900 | 6.98847 to 7.06754 |

A has a somewhat higher HbA1c mean but similar individual dispersion. B has a higher BMI distribution and somewhat lower HbA1c dispersion. Its serum-glucose mean and median are near the sample reference, while its upper quantile is higher. Both use a chosen uniform age composition, which differs from the selected sample composition.

## Joint relationships

| Request | Pair | Statistic | Reference | Generated range |
|---|---|---|---:|---:|
| A | bmi_hba1c | pearson | 0.19419 | 0.10913 to 0.16306 |
| A | bmi_hba1c | spearman | 0.25710 | 0.14476 to 0.15307 |
| B | bmi_hba1c | pearson | 0.19419 | 0.12359 to 0.13509 |
| B | bmi_hba1c | spearman | 0.25710 | 0.10617 to 0.13246 |
| B | glucose_hba1c | pearson | 0.66097 | 0.65535 to 0.69995 |
| B | glucose_hba1c | spearman | 0.36146 | 0.49188 to 0.52073 |

B shows close Pearson glucose–HbA1c correlation but higher rank correlation than the reference. This difference reinforces that one matching correlation does not establish the whole joint distribution.

## Verification and implementation findings

- The closure gate verified both decisions, initial/final lineage, all charged attempts, execution receipts, source bindings, table hashes and fixed seeds before the exclusive reference read receipt.
- The four CHNS input hashes and original fixed selection were preserved. A separate linkage order and BMI/eligibility calculation reproduced the selected records. No target-guided recoding, exclusion or parameter change occurred.
- Independent QR regression and covariance calculations verified all reference and generated coefficients, standard errors and interval endpoints; independent NumPy/rank expressions verified the marginal and pairwise diagnostics. Maximum reference discrepancy was below 5.3e-14. Existing E1 and E3 helper calculations also agreed.
- Root review found a pre-freeze divergent-moment risk in B: positive exp(k×lognormal BMI) terms. The author preserved the original draft and replaced those BMI links with positive linear multipliers before any execution. This was a mathematical implementation repair, not a post-feedback or target-driven improvement.
- The original runner lacked cross-stage model-family enforcement. This was corrected before scientific execution and checked with eight isolated mocks. An initial mock failed due to a missing mocked read_json method, then passed after the mock was fixed.
- A broad statsmodels import was blocked by Windows Application Control. No policy bypass or installation occurred; NumPy/SciPy implementations were independently checked instead.
- The full Jansen original was unavailable through the approved gateway. Both authors used its original abstract only and did not represent its conditional numeric coefficients as retrieved. Two full originals were available. Precise retrieval counts and source audit are recorded in the parent run artifacts; no paid API, training, HPC or additional clinical download was used here.

## Supported conclusion and next action

The implemented Agent can retrieve original evidence, construct whole-cohort generators for two related analysis requests, produce executable data, and expose assumptions and unsupported checks. This run supports partial scientific usefulness, especially the A age relation and B glucose relation. It does not establish reliable conditional BMI recovery, automatic numerical source calibration, post-feedback improvement or robustness across independent clinical datasets.

Keep these candidates frozen and preserve the unfavorable B result. The next framework decision should address how requested conditional relationships acquire usable source constraints and a genuine source-context numerical check. A failure to compute every source check should be surfaced as an evidence-coverage limitation, not hidden behind a completed feedback status. Merely increasing synthetic row counts cannot resolve that missing identification.

Full seed-specific values, conditional intervals, failures, aliases and recomputation receipts are in `REPORT.json`. There is no pooled success score.
