# Final source-only feedback review and retention

Decision: retain the initial generator.py and model_spec.json byte-for-byte. The frozen source recipes, common scientific family, target transfer rule, and all20 fixed operators are also retained. The existing source executions are reused; retention does not claim a new run or numerical improvement.

The controller reported successful isolated execution and bridge verification for both6000-row source contexts at seed18101. This review checked all five supplied JSON files: manifest hashes, initial-freeze binding, preparation/report consistency, report-to-individual-feedback identity, fixed panel/operator identity, and all20 calculations. No source output table, target data, generator import, bridge execution or additional scientific draws were used by the builder.

Lifelines diagnostics show differences in age mean(+0.201 years), age SD(-0.112871), BMI mean(-0.142673 kg/m^2), BMI SD(+0.024493), glucose mean(-0.109774 mg/dL), glucose SD(+0.042745), HbA1c mean(-0.001003 percentage points), HbA1c SD(-0.003981) and female proportion(-0.001). These are retained numerical differences, not evidence of exact marginal recovery. Finite Monte Carlo variation, rounded evidence and approximation of age/support/selection can contribute; one run does not identify their separate contributions. No seed-specific location or scale correction is justified by these values alone.

Lifelines HbA1c-on-BMI adjusted for age/female is0.01053256 versus reported0.0118924, difference-0.00135984. The glucose projection is0.01154940 versus0.01163829, difference-0.00008889. Both lie within the printed converted interval endpoints, but their confidence levels are unknown and this is not a calibrated acceptance test. The reported interval endpoints remain unchanged. No inference that residual correlation0.30 is correct follows: many joint laws can satisfy the source projections.

Pani adjusted age coefficient is0.00991839 versus reported0.010, difference-0.00008161. However, the source age-band mean profile is visibly incompatible with an exact reconstruction: differences are-0.05776(<40), -0.02818(40-44), -0.06141(45-49), -0.02325(50-54), -0.03700(55-59), +0.02866(60-64), +0.02853(65-69), and+0.12261(>=70) percentage points. The oldest mean is5.63261 versus5.51, whose reported survey SE is0.02. This patterned young-low/old-high discrepancy is treated as a substantive limitation of the assumed marginal age pattern; it is not dismissed as Monte Carlo noise. Survey SEs are retained as survey uncertainty and are not converted into individual SDs or a formal discrepancy z-test.

The discrepancy was possible under the initial construction because Pani's adjusted age projection and eight marginal age-band means do not identify the source covariate age patterns, nonlinear conditional age response, within-band ages, survey weights, or selection. A revised nonlinear age curve could alter the adjusted age projection; an age-specific covariate repair could force agreement through an unreported dependence; direct band intercepts would fit marginal outcomes without resolving conditional transport. The fixed source evidence supplies no discriminating information between these explanations. Retaining the transparent limited scenario is preferred to inventing one correction from this single run. This decision is not a claim that the current source age profile is adequate.

The target remains the same analytical scenario: exact supplied quotas, the identical Pani HbA1c anchor and shared Lifelines-based covariate law. The Pani age-band mismatch specifically weakens support for age-stratified target HbA1c summaries and any analysis sensitive to nonlinear age effects. No target statistic informed the decision, and no improvement in target validity is asserted. The final model is not suitable for claiming national prevalence, clinical replacement measurements or causal effects.

Remaining unsupported relationships are the residual BMI/glucose correlation, covariate age/sex trends, zero direct female HbA1c effect, linear age response and absence of interactions, normal homoskedastic residual law, target BMI/glucose marginals, source age tails and sex-age association, survey-to-unweighted estimator mapping, ancestry/selection effects, anemia/medication/pregnancy mechanisms and fasting-plasma-to-serum/assay equivalence. The Lifelines adult support18-95 and Pani declining70-95 tail remain explicit assumptions, including truncation beyond95. All20 fixed diagnostics were computable; causal, transport and scientific validity remain unassessed.

Individual residual variation and repeated seed variation are not evidence, model or transport uncertainty. No posterior or scientific pass score has been invented. Scientific changes: none. The allowed source-feedback opportunity is now closed by retention and final freeze.

All fixed diagnostic values follow. Units, adjustment sets, uncertainty types, assumptions and full metadata are preserved in the bound original feedback JSON files; differences are calculated minus reported.

| Check ID | Reported | Calculated | Difference | Rows used |
|---|---:|---:|---:|---:|
| J_T1_age_mean_task | 55.5 | 55.701 | +0.201 | 6000 |
| J_T1_age_sd_task | 9.9 | 9.78712915 | -0.112870851 | 6000 |
| J_T1_bmi_mean_task | 26.5 | 26.3573267 | -0.142673267 | 6000 |
| J_T1_bmi_sd_task | 4.1 | 4.12449331 | +0.0244933148 | 6000 |
| J_T1_glucose_mean_mg_dL_derived | 91.8 | 91.6902265 | -0.10977351 | 6000 |
| J_T1_glucose_sd_mg_dL_derived | 9 | 9.04274512 | +0.0427451221 | 6000 |
| J_T1_hba1c_mean_pct | 5.6 | 5.5989972 | -0.00100279788 | 6000 |
| J_T1_hba1c_sd_pct | 0.3 | 0.296018637 | -0.00398136291 | 6000 |
| J_T1_female_proportion_derived | 0.597 | 0.596 | -0.001 | 6000 |
| J_T2_bmi_slope_task_derived | 0.0118924 | 0.0105325572 | -0.00135984283 | 6000 |
| J_T2_glucose_slope_task_derived | 0.0116382889 | 0.0115494005 | -8.88884301e-05 | 6000 |
| P_NHANES_age_slope | 0.01 | 0.00991838875 | -8.16112459e-05 | 6000 |
| P_NHANES_hba1c_age_lt40_mean | 5.2 | 5.14224149 | -0.0577585137 | 1832 |
| P_NHANES_hba1c_age_40_44_mean | 5.28 | 5.25182349 | -0.0281765063 | 616 |
| P_NHANES_hba1c_age_45_49_mean | 5.37 | 5.30859188 | -0.0614081213 | 597 |
| P_NHANES_hba1c_age_50_54_mean | 5.4 | 5.37674801 | -0.0232519885 | 509 |
| P_NHANES_hba1c_age_55_59_mean | 5.44 | 5.40300477 | -0.0369952252 | 350 |
| P_NHANES_hba1c_age_60_64_mean | 5.46 | 5.48866473 | +0.0286647302 | 502 |
| P_NHANES_hba1c_age_65_69_mean | 5.5 | 5.52853014 | +0.0285301366 | 424 |
| P_NHANES_hba1c_age_ge70_mean | 5.51 | 5.63261237 | +0.122612367 | 1170 |
