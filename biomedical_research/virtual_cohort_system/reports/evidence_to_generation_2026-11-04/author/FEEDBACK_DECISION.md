# Retain the frozen initial candidate

Retain `candidates/initial` unchanged. I reviewed all four fixed scheduled feedback reports and all four generated-only diagnostics, including every 34-entry source-check set, all 36 regression coefficients/intervals, all marginal and relationship summaries, and all quality/design results. No new candidate, table, seed or source was selected.

All four reports record successful linked generator execution. Each output has 3,000 rows, zero reported nonfinite, out-of-scope age, invalid-sex or nonpositive-value counts, primary rank 5/5 and secondary rank 4/4. Every run retains 11 approximate numeric source comparisons and 23 unavailable checks. The source declarations and unavailable reasons are identical across runs. These are execution and consistency findings, not target-population validation.

## Every scheduled regression result remains visible

The intervals below are the controller's HC3-t 95% conditional synthetic-draw intervals. They do not include source, structural, transport or patient uncertainty.

| Scheduled run | Primary BMI, percent per kg/m^2 | Secondary BMI without glucose, percent per kg/m^2 |
|---|---:|---:|
| b_initial_trial_7400 | 0.012538 [0.001768, 0.023309] | 0.042764 [0.030515, 0.055012] |
| b_initial_delivery_7401 | 0.018107 [0.006213, 0.030001] | 0.051758 [0.039154, 0.064362] |
| b_initial_delivery_7402 | 0.003803 [-0.007994, 0.015601] | 0.042168 [0.029771, 0.054564] |
| b_initial_delivery_7403 | 0.007870 [-0.003585, 0.019325] | 0.044723 [0.031784, 0.057663] |

The prespecified unrounded-law BMI projections were 0.012986 primary and 0.045549 secondary. Two delivery primary intervals include zero. This is retained as observed draw variation; neither interval direction nor a desired sign is a revision criterion. All primary terms and all secondary terms were compared with the pre-execution model projections. The only one of 36 displayed intervals not containing its model projection is the trial's secondary female term: estimate 0.034948, interval [-0.035174, 0.105070], versus model -0.041256. The intervals are dependent and this descriptive check is not a calibrated multiple-test procedure. An isolated departure does not identify a model or implementation error and is not grounds to choose another seed.

## Source comparisons and discrepancy interpretation

| Source summary | Reported | Trial 7400 | Delivery 7401 | Delivery 7402 | Delivery 7403 |
|---|---:|---:|---:|---:|---:|
| Hainan_male_age_mean | 49.160000 | 51.426774 | 51.626838 | 51.498630 | 51.889096 |
| Hainan_male_glucose_mean | 5.560000 | 5.454461 | 5.492545 | 5.502929 | 5.590440 |
| Hainan_male_hba1c_mean | 5.780000 | 5.729389 | 5.814422 | 5.772780 | 5.763819 |
| Hainan_male_HG_spearman | 0.440000 | 0.400975 | 0.446813 | 0.474907 | 0.470216 |
| Hainan_female_age_mean | 47.430000 | 50.737679 | 50.866109 | 50.954856 | 50.735859 |
| Hainan_female_glucose_mean | 5.430000 | 5.426900 | 5.415021 | 5.460603 | 5.441276 |
| Hainan_female_hba1c_mean | 5.660000 | 5.687937 | 5.662218 | 5.671787 | 5.646021 |
| Hainan_female_HG_spearman | 0.500000 | 0.481664 | 0.492202 | 0.495014 | 0.500884 |
| Hainan_female_fraction | 0.640912 | 0.629000 | 0.637333 | 0.635000 | 0.642333 |
| JDPP_male_BH_pearson | 0.290000 | 0.290923 | 0.298148 | 0.261002 | 0.309881 |
| JDPP_female_BH_pearson | 0.080000 | 0.065543 | 0.106795 | 0.069922 | 0.063851 |

The age differences are systematic and expected from the chosen age law. Restricting and rounding the source-normal parameters to ages 35-74 yields model male mean 51.502808 (SD 9.632663) and female mean 50.750371 (SD 9.624602); the source unrestricted means are 49.16 and 47.43. The observed shifts of about 2.27-2.73 years in men and 3.31-3.52 in women should not be corrected to the unrestricted source means. This remains an assumed normal-age remapping, not a reconstructed source age-selected subgroup.

Glycaemic mean discrepancies change across draws and do not reveal a persistent implementation defect. Male glucose differences range from -0.105539 to 0.030440 mmol/L; male HbA1c differences from -0.050611 to 0.034422 percentage points. The female counterparts are smaller. Sex-specific HbA1c-glucose Spearman and BMI-HbA1c Pearson results fluctuate around their explicit transported calibrations. These raw source differences have no source sampling precision attached. The repeated generated cohorts are not independent biomedical evidence.

Pooled marginal means, SDs and central quantiles vary modestly across runs: age means 50.993-51.153 years, BMI means 23.873-23.973 kg/m^2, HbA1c means 5.688-5.717 percent and glucose means 5.437-5.495 mmol/L. The supplied marginal and Pearson/Spearman diagnostics agree with the intended qualitative family behavior; they cannot validate the family or its extreme tails. Pooled correlations are not equated with sex-specific source correlations. Both models remain full rank; raw uncentered condition numbers around 567-597 are scale-dependent and are not themselves proof of a covariance failure.

The 23 unavailable checks remain unavailable: six Hainan SDs with unreported denominator convention; six JDPP BMI quantiles with unreported interpolation convention; two unresolved JDPP Betas; two Pani coefficients whose source weighting/measurement/adjustment are not reproduced; five LifeLines native-unit/adjustment/scale entries; and two Hoorn quartile contrasts with different adjustment sets. LifeLines and Hoorn are still incompatible estimands for direct target coefficient checking. Their absence from numeric feedback is not agreement, and their uncertainty has not been silently reclassified.

## Why retain

The permitted feedback reveals no concrete extraction, semantic, numerical or implementation failure requiring a scientific correction. It shows expected age remapping and finite-draw fluctuations of the specified law. Adjusting parameters to improve these same source fits or stabilize one draw's BMI interval would lack new evidence and risk fitting the simulation realization.

The major limitations are unchanged: IGT-selected Japanese BMI information is combined with Hainan all-adult glycaemic margins; missing age/BMI/glucose dependencies are assumed; a weighted US age association is transported; serum/plasma and fasting adherence are unresolved; aggregate disease/treatment effects and tail behavior are not identified. Successful source-consistency feedback cannot remove these limitations. The primary and secondary regressions therefore remain model-dependent descriptive results, not causal or externally validated target estimates.

The single feedback decision is consumed by this justified retain choice. The frozen candidate and all prior drafts stay intact. `FEEDBACK_READ_MANIFEST.json` binds all eight actual feedback files and the initial freeze; `FEEDBACK_REVIEW_ALL_RUNS.json` preserves the complete 136 source-record and 36 coefficient review. No further construction search, execution, revision or favorable-seed selection was performed.
