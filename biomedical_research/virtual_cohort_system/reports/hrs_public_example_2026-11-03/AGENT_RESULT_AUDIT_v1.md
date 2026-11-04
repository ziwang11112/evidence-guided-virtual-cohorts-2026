# Agent-only HRS result audit v1

**PASS for recorded computation and independent baseline arithmetic.** Three fixed-seed outputs of one frozen Agent-authored law each contain 11,509 subjects and 46,036 visits. No generator or mixed model was rerun. The audit independently recomputed all 27 baseline distribution metrics (81 values) and checked retained coefficient/SE GLS results and execution/hash records.

## Scientific usefulness and limits

The below-6.5 age interaction is negative in all three outputs: mean **-0.044635**, range **-0.051059 to -0.038247**, versus supplied source coefficient **-0.046837**. This supports reconstruction of the source's negative longitudinal association under the supplied law.

The above-6.5 interaction has mean **0.026485**, range **0.013677 to 0.036768**, versus **0.012867**. Its direction is positive in every output, but the magnitude is higher on average. One of three synthetic model-conditional Wald intervals excludes zero, whereas the source's published interval includes zero. Treating binary significance as a scientific identity would overstate agreement.

Distribution reconstruction is uneven against the original sample. The high-HbA1c subgroup is much less dispersed than the original paper reports, while remaining close to the paper's own synthetic-law summary. This is evidence of reproducing a supplied generating model, not evidence that original upper-tail heterogeneity has been recovered. All metrics below retain this distinction.

## All 16 fixed effects

Estimates and SEs come from the already fitted native evaluator; its retained independent GLS check passes for every term. Source references below come directly from the single original printed memory-model block, with exactly16 unique terms; they do not use the faulty multi-block parser. Three-seed ranges are not confidence intervals.

| Term | Source estimate (SE) | Seed6101 | Seed6102 | Seed6103 | Mean | Seed range | Mean absolute discrepancy |
|---|---:|---:|---:|---:|---:|---|---:|
| (Intercept) | 0.674696 (0.038480) | 0.686912 | 0.666444 | 0.681226 | 0.678194 | 0.666444 to 0.686912 | 0.008999 |
| age60 | -0.530801 (0.026566) | -0.524198 | -0.511184 | -0.513108 | -0.516163 | -0.524198 to -0.511184 | 0.014638 |
| hba1c_U65 | 0.013327 (0.022384) | 0.025019 | -0.005478 | 0.010556 | 0.010032 | -0.005478 to 0.025019 | 0.011089 |
| hba1c_O65 | -0.073332 (0.015265) | -0.123896 | -0.032887 | -0.072487 | -0.076423 | -0.123896 to -0.032887 | 0.030618 |
| raceBlack | -0.478198 (0.029763) | -0.487243 | -0.480728 | -0.438243 | -0.468738 | -0.487243 to -0.438243 | 0.017177 |
| educHS | -0.389693 (0.031511) | -0.376615 | -0.407550 | -0.402590 | -0.395585 | -0.407550 to -0.376615 | 0.014610 |
| educLessThanHS | -0.837970 (0.042149) | -0.870287 | -0.838904 | -0.869064 | -0.859418 | -0.870287 to -0.838904 | 0.021448 |
| sexMale | -0.351786 (0.021277) | -0.386377 | -0.396927 | -0.361701 | -0.381668 | -0.396927 to -0.361701 | 0.029882 |
| cses | 0.051445 (0.010355) | 0.058274 | 0.045705 | 0.043677 | 0.049219 | 0.043677 to 0.058274 | 0.006779 |
| age60:hba1c_U65 | -0.046837 (0.015005) | -0.051059 | -0.038247 | -0.044599 | -0.044635 | -0.051059 to -0.038247 | 0.005017 |
| age60:hba1c_O65 | 0.012867 (0.012910) | 0.036768 | 0.013677 | 0.029011 | 0.026485 | 0.013677 to 0.036768 | 0.013618 |
| age60:raceBlack | 0.054426 (0.021355) | 0.070225 | 0.061368 | 0.041711 | 0.057768 | 0.041711 to 0.070225 | 0.011819 |
| age60:educHS | 0.035008 (0.022580) | 0.016134 | 0.027195 | 0.027133 | 0.023487 | 0.016134 to 0.027195 | 0.011521 |
| age60:educLessThanHS | 0.043667 (0.027971) | 0.020638 | 0.029569 | 0.024282 | 0.024829 | 0.020638 to 0.029569 | 0.018838 |
| age60:sexMale | 0.036590 (0.014272) | 0.050230 | 0.049769 | 0.040858 | 0.046952 | 0.040858 to 0.050230 | 0.010362 |
| age60:cses | 0.015266 (0.007519) | 0.011030 | 0.015174 | 0.011421 | 0.012542 | 0.011030 to 0.015174 | 0.002724 |

Every seed's16 SEs and Wald intervals are retained in the JSON; no mean estimate is substituted for a seed's uncertainty.

## All 27 baseline distribution metrics

One baseline row per subject; HbA1c below uses <6.5 and above uses >=6.5. SDs are sample SDs. Source columns reproduce the paper's rounded original/synthetic aggregate references, with no invented acceptance margin. The published synthetic column averages5000 repetitions; this table averages only the three fixed output seeds.

| Metric | Original paper | Published synthetic | Agent mean | Agent seed range | Mean absolute discrepancy from original |
|---|---:|---:|---:|---|---:|
| subject_count | 11509.000000 | 11509.000000 | 11509.000000 | 11509.000000 to 11509.000000 | 0.000000 |
| baseline_age_mean | 69.000000 | 70.000000 | 70.159019 | 70.134840 to 70.175153 | 1.159019 |
| baseline_age_sd | 10.000000 | 11.000000 | 11.330500 | 11.254754 to 11.384708 | 1.330500 |
| hba1c_mean | 5.900000 | 5.900000 | 5.872477 | 5.866649 to 5.882411 | 0.027523 |
| hba1c_sd | 1.000000 | 0.960000 | 0.967560 | 0.966246 to 0.969500 | 0.032440 |
| hba1c_below_mean | 5.600000 | 5.500000 | 5.453828 | 5.448937 to 5.459769 | 0.146172 |
| hba1c_below_sd | 0.400000 | 0.700000 | 0.654312 | 0.651186 to 0.657122 | 0.254312 |
| hba1c_above_mean | 7.700000 | 7.200000 | 7.151487 | 7.145208 to 7.155548 | 0.548513 |
| hba1c_above_sd | 1.400000 | 0.600000 | 0.563046 | 0.557992 to 0.565762 | 0.836954 |
| sex_female_count | 6810.000000 | 6810.000000 | 6840.666667 | 6770.000000 to 6893.000000 | 57.333333 |
| sex_female_percent | 59.000000 | 59.000000 | 59.437542 | 58.823529 to 59.892258 | 0.555189 |
| sex_male_count | 4699.000000 | 4699.000000 | 4668.333333 | 4616.000000 to 4739.000000 | 57.333333 |
| sex_male_percent | 41.000000 | 41.000000 | 40.562458 | 40.107742 to 41.176471 | 0.555189 |
| race_white_count | 9972.000000 | 9971.000000 | 9933.333333 | 9887.000000 to 10020.000000 | 70.666667 |
| race_white_percent | 87.000000 | 87.000000 | 86.309265 | 85.906682 to 87.062299 | 0.732268 |
| race_black_count | 1537.000000 | 1538.000000 | 1575.666667 | 1489.000000 to 1622.000000 | 70.666667 |
| race_black_percent | 13.000000 | 13.000000 | 13.690735 | 12.937701 to 14.093318 | 0.732268 |
| educ_LessThanHS_count | 2458.000000 | 2551.000000 | 2534.333333 | 2446.000000 to 2632.000000 | 84.333333 |
| educ_LessThanHS_percent | 21.000000 | 22.000000 | 22.020448 | 21.252932 to 22.869059 | 1.020448 |
| educ_HS_count | 7718.000000 | 7657.000000 | 7662.000000 | 7581.000000 to 7733.000000 | 66.000000 |
| educ_HS_percent | 67.000000 | 67.000000 | 66.573986 | 65.870189 to 67.190894 | 0.553277 |
| educ_College_count | 1333.000000 | 1301.000000 | 1312.666667 | 1296.000000 to 1330.000000 | 20.333333 |
| educ_College_percent | 12.000000 | 11.000000 | 11.405567 | 11.260752 to 11.556173 | 0.594433 |
| cses_mean | 0.070000 | 0.050000 | 0.047753 | 0.044843 to 0.051458 | 0.022247 |
| cses_sd | 1.050000 | 1.060000 | 1.052582 | 1.047724 to 1.060612 | 0.004492 |
| baseline_mem_s_mean | -0.390000 | -0.440000 | -0.447845 | -0.463237 to -0.439108 | 0.057845 |
| baseline_mem_s_sd | 1.100000 | 1.190000 | 1.192406 | 1.189926 to 1.196705 | 0.092406 |

## Computational record

| Seed | Generator seconds | Native fit seconds | Optimizer | Singular | Warnings | Random intercept SD | Random slope SD | Residual SD | REML logLik |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|
| 6101 | 1.594 | 4.135 | bobyqa / code 0 | False | 0 | 0.603898 | 0.104534 | 0.761899 | -60872.614916 |
| 6102 | 1.641 | 4.022 | bobyqa / code 0 | False | 0 | 0.622412 | 0.096964 | 0.760627 | -60712.732569 |
| 6103 | 1.578 | 3.624 | bobyqa / code 0 | False | 0 | 0.615511 | 0.107265 | 0.760782 | -60769.078860 |

All three native fits and retained GLS checks completed with return code0. Independent distribution maximum absolute arithmetic difference was 1.42e-14. These runtimes exclude evidence preparation, authoring and review.

## Interpretation boundary

- All original scientific coefficients and generating details were admissible inputs; recovery is source-informed reconstruction, not hidden-relation validation.
- One Agent-authored structure with three sampling seeds is not three independent Agent constructions or three real cohorts.
- Published original and synthetic references are rounded aggregates; synthetic paper results summarize5000 repetitions, while this experiment has3 fixed seeds.
- Balanced synthetic46036 visits differ from source43500 visits; model-conditional synthetic SEs do not add real patient information.
- The native comparison requires separate technical recovery; its parser failure must not count as evidence against the published method.
- GLS verifies fixed-effect/SE arithmetic conditional on fitted variance; it is not an independent optimizer or scientific-validity proof.

The original six attempt records remain unchanged. The coordinator reported a native-source parser defect affecting its three outputs; separate corrected reconstruction/release is required before any comparison. No native failure is counted here as Agent superiority.
