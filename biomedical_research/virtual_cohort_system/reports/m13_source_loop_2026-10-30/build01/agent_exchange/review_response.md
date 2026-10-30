# Source-feedback decision: retain_structure

Retain selected trial6 as an imperfect development candidate. No new candidate or structural change is proposed. The initial candidate remains frozen. The record includes all18 source constraints, not only the aggregate score.

Selected scalar changes are `asian_blend:0.35 -> 0.50` and `male_shift:0 -> -1` percentage point. `level_shift:0` and `residual_scale:1` are unchanged; male/female residual SD anchors remain4.31/4.741 pp. Fit-seed loss fell from1.070225 to0.668102; selected independent-seed replay loss is0.793914. Selection was committed using seeds13101/13102 before replay seeds23101/23102. All four selected-trial replay reports succeeded; every check has verified generation linkage, remains scientifically approximate and matches the declared variable set. The9-trial/40-execution session stopped at its trial budget. The zero target loss was not achieved; it is not a clinical acceptance threshold or proof of a global optimum.

Each value below is averaged across its two fixed seeds; the last column gives the individual replay-seed range. Units remain those of the evidence/operator definitions (body-fat percentage points for location/SD, unitless correlation, and original predictor units for coefficients).

| Constraint | Reported | Initial fit | Selected fit | Selected replay | Replay range |
|---|---:|---:|---:|---:|---:|
| Thai men mean | 14.1 | 17.3569 | 15.6365 | 15.5248 | 15.4302 to 15.6194 |
| Thai men SD | 6.5 | 6.13443 | 6.08444 | 6.20462 | 6.17195 to 6.2373 |
| Thai men BMI Pearson r | 0.72 | 0.694167 | 0.692734 | 0.692292 | 0.691214 to 0.69337 |
| Thai women mean | 31.8 | 32.2088 | 32.1066 | 32.1554 | 32.1283 to 32.1825 |
| Thai women SD | 8.4 | 10.4058 | 9.84453 | 9.81025 | 9.77791 to 9.8426 |
| Thai women BMI Pearson r | 0.77 | 0.884309 | 0.867693 | 0.87153 | 0.869657 to 0.873403 |
| Thai coefficient: intercept | -10.672 | -20.4564 | -17.7771 | -18.4423 | -18.6184 to -18.2663 |
| Thai coefficient: bmi | 1.648 | 2.13356 | 2.00982 | 2.02379 | 2.01876 to 2.02882 |
| Thai coefficient: age | 0.065 | 0.0381871 | 0.0414977 | 0.0492213 | 0.0486282 to 0.0498144 |
| Thai coefficient: male | -15.3 | -11.7011 | -13.5094 | -13.6589 | -13.7873 to -13.5304 |
| Gallagher coefficient: intercept | 76 | 73.5422 | 72.1519 | 71.8174 | 71.702 to 71.9328 |
| Gallagher coefficient: inv_bmi | -1097.8 | -1043.9 | -1013.64 | -1008.14 | -1009.28 to -1007 |
| Gallagher coefficient: male | -20.6 | -18.6053 | -18.9465 | -18.1403 | -18.9966 to -17.2841 |
| Gallagher coefficient: age | 0.053 | 0.0631088 | 0.0646352 | 0.0686661 | 0.0668471 to 0.0704851 |
| Gallagher coefficient: asian_inv_bmi | 95 | 71.1418 | 62.8414 | 67.4716 | 60.5946 to 74.3485 |
| Gallagher coefficient: asian_age | -0.044 | -0.0434464 | -0.0437702 | -0.0494158 | -0.055993 to -0.0428386 |
| Gallagher coefficient: male_inv_bmi | 154 | 101.86 | 77.4747 | 58.2861 | 41.7341 to 74.8382 |
| Gallagher coefficient: male_age | 0.034 | 0.0272022 | 0.0311416 | 0.028117 | 0.0235903 to 0.0326438 |

On fitting seeds,11 of18 mean absolute discrepancies improve and7 worsen. Thai male mean, female mean/SD/correlation and all four regression coefficients improve. Thai male SD and correlation worsen slightly. Gallagher intercept, inverse-BMI, age, Asian/inverse-BMI and male/inverse-BMI coefficients worsen; its male, Asian/age and male/age terms improve on fit seeds. Independent replay does not preserve every apparent interaction gain: Asian/age moves farther from its printed value, male and male/age gains weaken, and male/inverse-BMI remains especially poor. These trade-offs are retained without dropping constraints or reweighting their engineering scales.

There is both simulation variation and persistent mismatch. Thai female SD, correlation and BMI slope stay far from their references relative to the observed replay-seed variation. Gallagher male/inverse-BMI ranges41.73-74.84 versus154; its correlated regression design can make individual projected coefficients unstable, but both replay seeds remain substantially displaced. These two draws are not sampling confidence intervals for the papers. The larger replay than fitting loss is compatible with finite-seed selection and does not identify a new biological mechanism.

The source reconstruction and conditional law cannot be separated using these summaries alone. In particular, imposing the unidentified15% BMI>=25 allocation within each Thai development sex while retaining female moments creates a strongly U-shaped lower BMI component. A reciprocal-BMI mean is sensitive to that shape. The fixed age-BMI copulas, lower support choices and partial Thai/Japanese transport add further uncertainty. Blending a linear Thai law with the inverse-BMI law changes the regression projections in Gallagher's original design. Adding terms could reduce this numerical conflict while merely fitting the assumed covariate shape. No permitted evidence identifies such a correction, and the beta residual family/sex ratio remain assumptions. More random seeds would not resolve source-population or device uncertainty.

Retention therefore preserves the prespecified source-only numerical choice and its limitations; it does not approve the fit for clinical use. An especially important transport consequence is visible directly from the generator: for `asian=0`, selection changes only the male raw conditional location by-1 pp (subject to bounds), leaving female location and residual scale unchanged. Improvement driven by the Asian blend does not imply benefit in the non-Asian qualification domain.

The next invented-grid run can establish executable output, preservation and declared-bound behavior, but no predictive accuracy because it has no outcomes. If a later independent, prespecified real-target evaluation is supplied, it can estimate comparative performance for that cohort and endpoint. It cannot establish universal transport, calibrated model uncertainty, device equivalence or causal validity, and its results must not be used retroactively to choose this source model.

Reviewed only the permitted plan/result/selection files, selected trial generator/specification and its four source replay reports. No generator was imported or executed, no frozen candidate was edited, and no target or sibling result was inspected.
