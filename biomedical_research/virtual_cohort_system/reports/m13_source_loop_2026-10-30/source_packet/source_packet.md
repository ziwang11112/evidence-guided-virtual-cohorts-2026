# Screened body-fat source packet

Verified 30 October 2026. Source extraction only: no target data, generator, covariate dependence or scientific parameter choices. The JSON preserves published precision and marks missing uncertainty as `null`. Screening covers age/sex/BMI DXA models; extra-input anthropometric models and four-compartment models are excluded consistently.

## Pongchaiyakul 2005

[Primary publisher article](https://onlinelibrary.wiley.com/doi/full/10.1038/oby.2005.82), DOI 10.1038/oby.2005.82. Random community sample, rural Khon Kaen, Thailand; healthy adults aged 20-84. Recent/chronic illness, weight-affecting medication and weight training were excluded. Lunar DPX-IQ DXA; software version unreported. Methods and Table 1 define disjoint development/validation subsets of one cohort. Whole-cohort BMI>=30 prevalence was reported as 0%; minimum BMI and subgroup ranges were not provided.

All margins below are mean ± SD (Table 1).

| Subset | Sex | n | Age, y | BMI, kg/m² | DXA fat, % |
|---|---|---:|---:|---:|---:|
| Development | Men | 98 | 50.7 ± 17.0 | 22.3 ± 2.7 | 14.1 ± 6.5 |
| Development | Women | 125 | 49.4 ± 17.4 | 23.8 ± 4.0 | 31.8 ± 8.4 |
| Validation | Men | 83 | 47.2 ± 17.9 | 22.4 ± 3.0 | 14.0 ± 6.3 |
| Validation | Women | 130 | 51.8 ± 14.1 | 24.3 ± 4.1 | 32.2 ± 8.6 |

`bodyfat = -10.672 + 1.648*bmi + 0.065*age - 15.3*male`

`male=1` for men, `0` for women; bodyfat in percent. Development R²=0.83; development Pearson BMI-fat r=0.72 men and 0.77 women (Table 2, p<0.001). Validation predicted-measured r=0.93; agreement limits -8.9 to 8.6 percentage points (Table 4/Figure 5). Bias conflicts: text +0.16, text 95% CI [-0.75,0.44], table -0.2. Preserve but exclude bias from numerical calibration. Coefficient SE/covariance and residual SD are unreported.

Complete relevant validation diagnostics, prevalence thresholds, comparator results and conflicts are retained in `screened_sources/thai2005.json`; development and validation are never pooled as interchangeable constraints.

## Gallagher 2000

[Original article PDF mirror](https://zakboekdietetiek.nl/wp-content/uploads/2015/11/Am-J-Clin-Nutr-2000-Gallagher-694-701.pdf), DOI 10.1093/ajcn/72.3.694. Publisher retrieval failed; the original PDF was read and pp695-698 visually checked. Healthy convenience sample, BMI<=35; maximum age 97, lower adult age unspecified. Acute/chronic illness and vigorous training >6 h/week excluded. Japan: Lunar DPX-L/1.3z; US: Lunar DPX/3.6; UK: Hologic QDR1000/enhanced software. Japanese participants occur only at Japan, African Americans only at US; site and ethnicity are entangled.

Table 1 counts and Table 2 mean ± SD:

| Sex | Source ethnicity | US / Japan / UK | n | Age, y | BMI, kg/m² |
|---|---|---:|---:|---:|---:|
| Men | African American | 99 / 0 / 0 | 99 | 51.4 ± 17.6 | 26.2 ± 3.3 |
| Men | Japanese | 0 / 322 / 0 | 322 | 46.7 ± 15.4 | 23.1 ± 3.0 |
| Men | White | 94 / 0 / 98 | 192 | 48.1 ± 19.2 | 25.5 ± 3.8 |
| Women | African American | 155 / 0 / 0 | 155 | 56.2 ± 16.8 | 27.1 ± 4.3 |
| Women | Japanese | 0 / 633 / 0 | 633 | 39.3 ± 15.9 | 23.2 ± 3.9 |
| Women | White | 127 / 0 / 98 | 225 | 48.8 ± 17.6 | 24.5 ± 4.5 |

Equation 1, p696:

`bodyfat = 76.0 - 1097.8/bmi - 20.6*male + 0.053*age + 95.0*asian/bmi - 0.044*asian*age + 154*male/bmi + 0.034*male*age`

`asian=1` for the source Japanese group, `0` for white/African American groups; sex coding as above. Multiple R=0.90; SEE=4.31 percentage points. No development/validation split, coefficient SE/covariance, age-BMI joint distribution, exact age/BMI-stratum counts, or DXA outcome mean/SD is supplied. Figures/other DXA relationships remain in JSON. Four-compartment equations and predicted healthy-fat ranges are excluded from DXA calibration.

## Provenance and limits

- `evidence_packet.json` embeds both records and hashes the separately citable source files.
- `screened_sources/thai2005.json` and `screened_sources/gallagher2000.json` are screened factual transcriptions/paraphrases; they are not original publisher-byte copies.
- `retrieval_manifest.json` records actual retrievals, failures, locators, verification methods and the original PDF response SHA-256. Original Wiley response bytes were unavailable through the web tool; direct retrieval returned 403. No original-byte hash is invented.
- `selfcheck.json` records completed schema/precision, counts, coefficient, context and hash checks. These check extraction integrity, not scientific validity or transport performance.

Source articles do not report shared participants across the Thai and US/UK/Japan studies; linkage is unavailable. Within each article, repeated summaries/models reuse participants. Source instrument differences and marginal-only covariates remain unresolved. No full copyrighted articles or page renders are distributed in this screened packet.
