# Source-only review of the frozen structural pilot

Retain both frozen candidates for the prespecified exploratory target comparison, without tuning or revision. The reviewed source diagnostics show no integrity, missing-data, nonfinite-value or computability blocker. They also show material trade-offs; neither candidate is established as scientifically valid or superior for the target analyses. Target outcomes, target executions and target analytical results were not read.

This review compares every one of the 46 unchanged declarative checks across the same two source contexts and fixed seeds 80201, 80202 and 80203. Twelve checks describe covariates alone. Thirty-four involve generated TG directly or use TG to select a covariate subgroup; the latter remain outcome-related checks. The identical source-replay recipe hash, exact per-check definitions and context-input hashes were checked. The six scheduled replay JSON hashes match their portfolio entries; all six reports and all twelve contexts record success and generation linkage. All 276 check-runs are approximate, finite, generation-linked and have no dropped missing rows. This review checked those receipts and numerical correspondence; it did not rerun the sandbox or independently revalidate its isolation.

Only the two supplied portfolios and their six named source replay reports were read for this review. Physical replay paths are under ${EXECUTION_BUNDLE}/source_replays as supplied by the controller. The baseline's embedded historical seed wording was not used as the current schedule: the actual bound replay schedule above governs. Updated shared source-assumption wording does not change the covariate CSVs or diagnostic definitions.

The 12 covariate-only checks are exactly equal between candidates and invariant across all three seeds. They confirm preservation and the declared source-covariate reconstruction, not TG fit. Small deviations from published marginal summaries persist from discretization/approximation; the largest listed age deviation is Bansal age SD 7.205858 years versus 7.2 years. These covariate matches are excluded from the substantive TG assessment.

In Oh, mean TG remains near the published anchors. Male three-seed mean changes from 141.501 to 141.204 mg/dL against 141.6, and female mean from 97.491 to 97.443 against 97.2. The male average signed discrepancy moves farther below its anchor even though its average absolute discrepancy decreases slightly because the baseline draws straddle it; this is not described as a uniform mean-fit improvement. Sex-specific SD discrepancies increase: male 107.142 to 106.896 against 107.7, female 61.213 to 61.354 against 61.0. These shifts are small relative to some three-draw ranges and do not establish a new marginal-fit calibration.

Oh's pooled age/sex-adjusted BMI coefficient changes from 6.83363 to 6.71186 mg/dL per kg/m^2 against the reported 6.813. The joint-model range 6.70758-6.71763 lies below the report; the baseline range is 6.82841-6.84091. This discrepancy is persistent across the scheduled seeds. Male cumulative TG proportions below 150, 200 and 500 move slightly closer but remain low; the joint values are 0.664885, 0.802014 and 0.986276 against 0.684159, 0.810496 and 0.990282. Thus the excess high-TG tail remains. Female below-150 moves closer, below-200 remains high with little change, and below-500 moves farther below its reported value. Rare-tail comparisons remain dependent on few modeled tail events and do not supply independent evidence.

In Bansal, all three TG quantiles and all six cumulative category proportions move closer to their corresponding source values, without reaching them. Q25 changes 76.730 to 77.426 mg/dL against 81; median 111.785 to 113.415 against 115; Q75 162.173 to 165.591 against 169. Every joint-model quantile draw remains below its report, and every joint cumulative-proportion draw remains above its report. These are distributional trade-offs within one approximate source context, not evidence of overall or target superiority.

The Bansal age Spearman correlation moves slightly toward 0.18 (0.142734 to 0.145805), while BMI Spearman moves farther from 0.33 (0.342741 to 0.377133). All joint BMI-correlation draws lie in 0.374371-0.379916, so the larger positive discrepancy is not explained by the displayed seed spread. This accords with worse reverse-conditional BMI means: TG-tertile-1 BMI moves 24.058 to 23.847 kg/m^2 against 24.2, and tertile-3 BMI moves 27.939 to 28.068 against 27.6. The high-minus-low BMI mean contrast widens from 3.881 to 4.221 kg/m^2 against the reported 3.4. Tertile-2 BMI mean gets closer; BMI SDs in tertiles 1 and 3 get closer, whereas tertile-2 BMI SD moves farther below 5.0. These reverse-conditional summaries are not substituted for TG-on-BMI coefficients.

Bansal age summaries conditional on TG tertiles show mixed changes: age means in tertiles 1 and 3 and age SDs in tertiles 1 and 3 move closer; tertile-2 age mean and SD move farther from their reported values. Joint-model tertile-3 age SD remains high at 7.956 years against 7.2; tertile-1 age SD remains low at 6.352 against 6.9. Every conditional age/BMI summary, including those with only small changes, is retained in the tables below.

The fixed same-seed differences arise from the structural change under identical approximate covariates; they are not changes in the submitted source extraction. The available diagnostics cannot distinguish biological misspecification from the source context's unreported age-BMI dependence, omitted medication/lifestyle variables, assay mapping and other transport assumptions. They also do not replay the newly used Tromso adjusted log-ratio surface or the China-PAR longitudinal coefficients: those remain explicitly unsupported by the supplied operators. Reconstructing the source interaction algebra and executing the same generator on Oh/Bansal contexts does not validate its Tromso population bridge.

No combined score is calculated. Each discrepancy remains in its native unit and estimand; proportion differences are fractions, not percentages. A negative change in mean absolute discrepancy in the tables means closer only for that single diagnostic across these three seeds. It is not an acceptance threshold, uncertainty interval or significance test. The checks share participants and outcomes, and the three seeds vary residual draws only. No interpretation is made about target signs, effect sizes, p-values, subgroup validity or expected target performance. Both frozen candidates remain unchanged for the planned evaluation.

## All 12 covariate-only checks

| Check | Unit | Reported | Baseline mean [range] | Joint mean [range] | Change in mean absolute discrepancy |
|---|---|---:|---:|---:|---:|
| e_oh_male_age_mean | years | 43.9 | 43.9 [43.9, 43.9] | 43.9 [43.9, 43.9] | 0 |
| e_oh_male_age_sd | years | 13.6 | 13.6001 [13.6001, 13.6001] | 13.6001 [13.6001, 13.6001] | 0 |
| e_oh_male_bmi_mean | kg/m^2 | 24.4 | 24.4 [24.4, 24.4] | 24.4 [24.4, 24.4] | 0 |
| e_oh_male_bmi_sd | kg/m^2 | 3.1 | 3.1 [3.1, 3.1] | 3.1 [3.1, 3.1] | 0 |
| e_oh_female_age_mean | years | 43.3 | 43.3 [43.3, 43.3] | 43.3 [43.3, 43.3] | 0 |
| e_oh_female_age_sd | years | 12.7 | 12.7001 [12.7001, 12.7001] | 12.7001 [12.7001, 12.7001] | 0 |
| e_oh_female_bmi_mean | kg/m^2 | 23 | 23 [23, 23] | 23 [23, 23] | 0 |
| e_oh_female_bmi_sd | kg/m^2 | 3.2 | 3.20001 [3.20001, 3.20001] | 3.20001 [3.20001, 3.20001] | 0 |
| e_bansal_age_mean | years | 54.5 | 54.4997 [54.4997, 54.4997] | 54.4997 [54.4997, 54.4997] | 0 |
| e_bansal_age_sd | years | 7.2 | 7.20586 [7.20586, 7.20586] | 7.20586 [7.20586, 7.20586] | 0 |
| e_bansal_bmi_mean | kg/m^2 | 25.9 | 25.9 [25.9, 25.9] | 25.9 [25.9, 25.9] | 0 |
| e_bansal_bmi_sd | kg/m^2 | 5 | 4.99995 [4.99995, 4.99995] | 4.99995 [4.99995, 4.99995] | 0 |

## All 11 Oh outcome-related checks

| Check | Unit | Reported | Baseline mean [range] | Joint mean [range] | Change in mean absolute discrepancy |
|---|---|---:|---:|---:|---:|
| e_oh_male_tg_mg_dl_mean | mg/dL | 141.6 | 141.501 [140.791, 141.903] | 141.204 [140.497, 141.602] | -0.0431374 |
| e_oh_male_tg_mg_dl_sd | mg/dL | 107.7 | 107.142 [106.462, 107.766] | 106.896 [106.235, 107.518] | 0.202079 |
| e_oh_male_tg_below_150 | 1 | 0.684159 | 0.664027 [0.661581, 0.666958] | 0.664885 [0.662925, 0.667752] | -0.000858439 |
| e_oh_male_tg_below_200 | 1 | 0.810496 | 0.801058 [0.799789, 0.803515] | 0.802014 [0.800826, 0.804389] | -0.00095562 |
| e_oh_male_tg_below_500 | 1 | 0.990282 | 0.986189 [0.986119, 0.986281] | 0.986276 [0.986152, 0.986395] | -8.63838e-05 |
| e_oh_female_tg_mg_dl_mean | mg/dL | 97.2 | 97.4911 [97.2138, 97.7255] | 97.443 [97.1687, 97.671] | -0.0272273 |
| e_oh_female_tg_mg_dl_sd | mg/dL | 61 | 61.2126 [60.6225, 61.5642] | 61.3536 [60.7456, 61.7392] | 0.058928 |
| e_oh_female_tg_below_150 | 1 | 0.852708 | 0.84834 [0.846348, 0.851177] | 0.849642 [0.847718, 0.852333] | -0.00130182 |
| e_oh_female_tg_below_200 | 1 | 0.932441 | 0.937107 [0.935464, 0.938984] | 0.937073 [0.935342, 0.938892] | -3.38135e-05 |
| e_oh_female_tg_below_500 | 1 | 0.999391 | 0.999229 [0.999097, 0.99931] | 0.999175 [0.999026, 0.999249] | 5.41016e-05 |
| e_oh_bmi_age_sex_slope | mg/dL per kg/m^2 | 6.813 | 6.83363 [6.82841, 6.84091] | 6.71186 [6.70758, 6.71763] | 0.0805057 |

## All 23 Bansal outcome-related checks

| Check | Unit | Reported | Baseline mean [range] | Joint mean [range] | Change in mean absolute discrepancy |
|---|---|---:|---:|---:|---:|
| e_bansal_q25 | mg/dL | 81 | 76.7299 [76.5048, 76.9455] | 77.4263 [77.1682, 77.6464] | -0.696373 |
| e_bansal_median | mg/dL | 115 | 111.785 [111.526, 112.111] | 113.415 [113.172, 113.714] | -1.63005 |
| e_bansal_q75 | mg/dL | 169 | 162.173 [161.595, 162.554] | 165.591 [164.969, 166.035] | -3.41802 |
| e_bansal_spearman_age | 1 | 0.18 | 0.142734 [0.139223, 0.144637] | 0.145805 [0.142429, 0.14761] | -0.0030706 |
| e_bansal_spearman_bmi | 1 | 0.33 | 0.342741 [0.33993, 0.345627] | 0.377133 [0.374371, 0.379916] | 0.0343925 |
| e_bansal_tertile_cum1 | 1 | 0.327567 | 0.352006 [0.350432, 0.354223] | 0.344758 [0.34325, 0.346804] | -0.0072489 |
| e_bansal_tertile_cum2 | 1 | 0.665673 | 0.692245 [0.690625, 0.694913] | 0.680108 [0.6779, 0.682995] | -0.0121367 |
| e_bansal_quintile_cum1 | 1 | 0.194602 | 0.225996 [0.224066, 0.227756] | 0.221862 [0.220164, 0.223283] | -0.00413394 |
| e_bansal_quintile_cum2 | 1 | 0.392484 | 0.410163 [0.408092, 0.412106] | 0.401274 [0.399307, 0.403656] | -0.00888922 |
| e_bansal_quintile_cum3 | 1 | 0.597922 | 0.620452 [0.617904, 0.621844] | 0.608655 [0.606024, 0.610597] | -0.0117971 |
| e_bansal_quintile_cum4 | 1 | 0.799334 | 0.816785 [0.814445, 0.818459] | 0.805833 [0.803969, 0.807647] | -0.010952 |
| e_bansal_tertile1_age_mean | years | 53.1 | 53.3434 [53.3232, 53.3743] | 53.3323 [53.3157, 53.3645] | -0.0110991 |
| e_bansal_tertile1_age_sd | years | 6.9 | 6.31596 [6.29621, 6.33413] | 6.35164 [6.34813, 6.35616] | -0.0356828 |
| e_bansal_tertile1_bmi_mean | kg/m^2 | 24.2 | 24.058 [24.0349, 24.0814] | 23.8474 [23.817, 23.8767] | 0.210606 |
| e_bansal_tertile1_bmi_sd | kg/m^2 | 4.1 | 4.41283 [4.38886, 4.43874] | 4.37776 [4.34715, 4.40924] | -0.0350712 |
| e_bansal_tertile2_age_mean | years | 54.8 | 54.4984 [54.4697, 54.5204] | 54.4566 [54.4345, 54.4814] | 0.0417769 |
| e_bansal_tertile2_age_sd | years | 7.3 | 7.08541 [7.05845, 7.10237] | 7.06811 [7.0457, 7.09272] | 0.0173069 |
| e_bansal_tertile2_bmi_mean | kg/m^2 | 25.9 | 25.961 [25.9551, 25.9666] | 25.9418 [25.9337, 25.9554] | -0.0191244 |
| e_bansal_tertile2_bmi_sd | kg/m^2 | 5 | 4.695 [4.69118, 4.7013] | 4.63861 [4.63204, 4.64456] | 0.0563973 |
| e_bansal_tertile3_age_mean | years | 55.6 | 55.8238 [55.8074, 55.8325] | 55.8031 [55.7772, 55.8178] | -0.02067 |
| e_bansal_tertile3_age_sd | years | 7.2 | 8.0192 [7.99571, 8.04377] | 7.95599 [7.94136, 7.9731] | -0.0632078 |
| e_bansal_tertile3_bmi_mean | kg/m^2 | 27.6 | 27.9394 [27.9262, 27.9489] | 28.0683 [28.0513, 28.0787] | 0.12886 |
| e_bansal_tertile3_bmi_sd | kg/m^2 | 5.1 | 5.15237 [5.13071, 5.17307] | 5.06917 [5.0489, 5.08631] | -0.0215404 |

Exact inputs, frozen parent identities, all individual seed values and per-check paired differences are bound in AGENT_REVIEW.json. The review changes no scientific candidate artifact.
