# Complete source-feedback appendix

All 20 fixed checks per construction are computable with status approximate. Differences are computed minus reported. A/B share the same reported quantities and operator definitions. Each source table contains 6,000 fictional rows at seed 18101; age-band checks use the selected counts shown below. Finals reuse the initial source outputs. No source threshold or pooled pass score was specified.

Lifelines source projections each adjust for age and female, separately; Pani's age projection adjusts for female, BMI and glucose. Source slopes use raw units (years, kg/m², mg/dL, HbA1c %), unlike scaled target slopes. Source SD is sample SD. Pani means are originally survey-weighted; reconstructions are unweighted approximate projections. Source mean uncertainty is reported SE, not individual SD or CI. Unknown Jansen interval levels are not assigned a confidence level here; the feedback report's not_reported tag is retained.

## lifelines

| Check (unit) | Reported | Reported SE | A | A − source | A n | B | B − source | B n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| J_T1_age_mean_task (year) | 55.5 | Not reported | 55.701 | 0.201 | 6000 | 55.538167 | 0.038167 | 6000 |
| J_T1_age_sd_task (year) | 9.9 | Not reported | 9.787129 | -0.112871 | 6000 | 9.990571 | 0.090571 | 6000 |
| J_T1_bmi_mean_task (kg/m^2) | 26.5 | Not reported | 26.357327 | -0.142673 | 6000 | 26.400677 | -0.099323 | 6000 |
| J_T1_bmi_sd_task (kg/m^2) | 4.1 | Not reported | 4.124493 | 0.024493 | 6000 | 4.144427 | 0.044427 | 6000 |
| J_T1_glucose_mean_mg_dL_derived (mg/dL) | 91.8 | Not reported | 91.690226 | -0.109774 | 6000 | 91.635147 | -0.164853 | 6000 |
| J_T1_glucose_sd_mg_dL_derived (mg/dL) | 9 | Not reported | 9.042745 | 0.042745 | 6000 | 8.995305 | -0.004695 | 6000 |
| J_T1_hba1c_mean_pct (%) | 5.6 | Not reported | 5.598997 | -0.001003 | 6000 | 5.596215 | -0.003785 | 6000 |
| J_T1_hba1c_sd_pct (%) | 0.3 | Not reported | 0.296019 | -0.003981 | 6000 | 0.294515 | -0.005485 | 6000 |
| J_T1_female_proportion_derived (1) | 0.597 | Not reported | 0.596 | -0.001 | 6000 | 0.592833 | -0.004167 | 6000 |
| J_T2_bmi_slope_task_derived (% per kg/m^2) | 0.011892 | Not reported | 0.010533 | -0.00136 | 6000 | 0.012153 | 0.000261 | 6000 |
| J_T2_glucose_slope_task_derived (% per mg/dL) | 0.011638 | Not reported | 0.011549 | -0.000089 | 6000 | 0.011399 | -0.00024 | 6000 |

## pani

| Check (unit) | Reported | Reported SE | A | A − source | A n | B | B − source | B n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P_NHANES_age_slope (% per year) | 0.01 | Not reported | 0.009918 | -0.000082 | 6000 | 0.009649 | -0.000351 | 6000 |
| P_NHANES_hba1c_age_lt40_mean (%) | 5.2 | 0.01 | 5.142241 | -0.057759 | 1832 | 5.171499 | -0.028501 | 1901 |
| P_NHANES_hba1c_age_40_44_mean (%) | 5.28 | 0.02 | 5.251823 | -0.028177 | 616 | 5.295509 | 0.015509 | 593 |
| P_NHANES_hba1c_age_45_49_mean (%) | 5.37 | 0.02 | 5.308592 | -0.061408 | 597 | 5.334112 | -0.035888 | 600 |
| P_NHANES_hba1c_age_50_54_mean (%) | 5.4 | 0.02 | 5.376748 | -0.023252 | 509 | 5.384609 | -0.015391 | 479 |
| P_NHANES_hba1c_age_55_59_mean (%) | 5.44 | 0.02 | 5.403005 | -0.036995 | 350 | 5.431262 | -0.008738 | 346 |
| P_NHANES_hba1c_age_60_64_mean (%) | 5.46 | 0.03 | 5.488665 | 0.028665 | 502 | 5.503039 | 0.043039 | 502 |
| P_NHANES_hba1c_age_65_69_mean (%) | 5.5 | 0.03 | 5.52853 | 0.02853 | 424 | 5.5656 | 0.0656 | 355 |
| P_NHANES_hba1c_age_ge70_mean (%) | 5.51 | 0.02 | 5.632612 | 0.122612 | 1170 | 5.657427 | 0.147427 | 1224 |

