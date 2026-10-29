# Recovered Tromso joint age-BMI TG evidence

Exact Supplementary Table 1 was recovered from the current documented PMC public AWS archive. All 28 nonreference sex-specific age-by-BMI ratios and 95% CIs are available as table text; no graph estimates were used. This is source-only extraction for curator review, not harness admission.

Source: Mikkelsen et al., Frontiers in Nutrition (2023), DOI [10.3389/fnut.2023.1158383](https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2023.1158383/full). [Retrieved supplement](https://pmc-oa-opendata.s3.amazonaws.com/PMC10308115.1/Table_1.DOCX).

The statistic is a dimensionless back-transformed log-TG coefficient, labelled relative difference (RD), relative to age 40-49 and BMI <25 within the same sex. It is not an arithmetic mean or an individual residual variation estimate. Underlying TG is mmol/L.

| BMI (kg/m2) | Age (years) | Women RD [95% CI] | Men RD [95% CI] |
|---|---|---|---|
| <25 | 40-49 | 1 (reference) | 1 (reference) |
| <25 | 50-59 | 1.14 [1.10, 1.17] | 0.97 [0.92, 1.03] |
| <25 | 60-69 | 1.20 [1.16, 1.24] | 0.92 [0.87, 0.97] |
| <25 | 70-79 | 1.17 [1.11, 1.23] | 0.88 [0.82, 0.94] |
| <25 | 80+ | 1.16 [1.05, 1.28] | 0.85 [0.77, 0.94] |
| 25-29.9 | 40-49 | 1.24 [1.23, 1.28] | 1.32 [1.27, 1.38] |
| 25-29.9 | 50-59 | 1.44 [1.39, 1.49] | 1.30 [1.24, 1.36] |
| 25-29.9 | 60-69 | 1.50 [1.45, 1.56] | 1.18 [1.12, 1.23] |
| 25-29.9 | 70-79 | 1.40 [1.33, 1.47] | 1.08 [1.03, 1.15] |
| 25-29.9 | 80+ | 1.49 [1.37, 1.61] | 1.02 [0.93, 1.12] |
| ≥30 | 40-49 | 1.60 [1.54, 1.67] | 1.61 [1.54, 1.70] |
| ≥30 | 50-59 | 1.83 [1.75, 1.90] | 1.58 [1.50, 1.66] |
| ≥30 | 60-69 | 1.74 [1.66, 1.82] | 1.40 [1.32, 1.48] |
| ≥30 | 70-79 | 1.64 [1.55, 1.74] | 1.32 [1.23, 1.41] |
| ≥30 | 80+ | 1.55 [1.38, 1.75] | 1.15 [0.97, 1.36] |

Population and adjustment: Cross-sectional Tromso7 2015-2016, Norway, inhabitants aged 40+ invited (65% attendance). Missing TG and TG >10 mmol/L were excluded. S1 regression sample: women n=10,143; men n=9,583. Nonfasting blood collection; elapsed meal time entered as a categorical covariate, with >=7 hours as fasting reference. General S1 footnote and Figure 3 caption list physical activity, education, smoking, lipid-lowering drug use, recent exercise and recent alcohol, as well as meal time. Figure 2 explicitly identifies education and drug use as women-only; those rows appear only for women in S1. The unresolved general-wording discrepancy is retained in the evidence JSON.

Other retained issues: main Results 3.2.2 says men n=9,341, while S1 and Figure 2 say n=9,583. Women age 40-49/BMI 25-29.9 RD 1.24 [1.23, 1.28] is copied exactly despite the unusual log-scale asymmetry. No source value was corrected.

Source applicability: these estimates can constrain a generic model of the within-sex age-category by BMI-category conditional log-TG shape. They do not identify absolute reference levels, between-sex baselines, residual SD, within-category continuous slopes, or joint coefficient covariance. Transfer across population, meal measurement and omitted adjustment covariates remains assumption-dependent. Shared references mean marginal CIs do not supply uncertainty for arbitrary contrasts or independent coefficient draws.

Verification: DOCX is a valid ZIP; metadata DOI matches; published version PMC10308115.1 is the sole public version listed, CC BY and non-manuscript. DOCX MD5 and article XML MD5 match their source metadata. One native Word table provides 30 joint rows including two references, without duplicate keys; each estimate is inside its reported CI. The only embedded image is a Frontiers header logo, visually inspected. No OCR/digitization, target access, generator execution, or harness approval occurred.

DOCX SHA256: `14b0f6ddecd322bab4ea51220599008156599e9587e9f6b001eadcbbb640536c`.

Deliverables: `Mikkelsen2023_joint_evidence.json` contains every statistic, raw cell values, exact table row locators and full source context; `Mikkelsen2023_joint_age_BMI_sex_TG.csv` is the tidy extraction; original DOCX, article XML, metadata and public-access documentation are retained.
