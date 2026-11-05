# L01 source review request

Status: proposal only, awaiting controller scientific review. No candidate, generator, random draw, or individual table has been written or executed. The retained numerical calculation is deterministic parameter algebra in `ANALYTIC_PROPOSAL_CHECK.json`.

## Inputs actually inspected

I read AUTHOR_TASK.md, task.json, request.json, registry.json, CURATED_INPUTS.json, input/population_metadata.json, the three admitted curator extractions, the evidence-cohort-generation skill and its harness interface, and the allowed ANALYSIS_EVIDENCE, EVIDENCE_USE_V1, and WHOLE_COHORT_FEEDBACK interface documents. These extractions are approved artifacts, not evidence that I downloaded or independently reread their original full texts. No target rows, target summaries, previous candidates, other authors, or wider project summaries were inspected.

The initial delegation named the missing directory `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/work/evidence_use_cross_task_2026-11-05/interfaces`. One listing failed. AUTHOR_TASK.md supplied the existing authorized directory `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work/evidence_use_cross_task_2026-11-05/interfaces`, which I used. Task and contract files were not changed.

No optional literature action has been attempted. SEARCH_LEDGER.json records zero query/download consumption and the actual source choices. The existing gateway session is untouched.

## Source quantities and proposed roles

### Agongo 2018: arithmetic scale and dispersion

Admitted artifact: `sources/curated/AGONGO_2018_CURATOR_EXTRACTION.json`; source ID `agongo_2018_navrongo`; DOI 10.1371/journal.pone.0206326. Original article: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206326

Population: AWI-Gen Navrongo, rural northern Ghana, 2015, ages 40–60, resident at least 10 years, pregnant women excluded, complete investigated variables. Reported total 1,839; tables/abstract give 846 men and 993 women, whereas Methods prints 864 men. I do not use these counts to derive precision or target composition. BMI is measured weight/height squared. Lipids are overnight-fasting serum, direct Randox RX Daytona+ assays, mmol/L. Source weighting is not explicitly reported. Adjustment for the following arithmetic summaries: none.

| Evidence item | Reported quantity | Locator | Use |
|---|---|---|---|
| agongo_men_bmi_mean_sd | Mean 20.87, SD 3.15 kg/m² | Table 1, men, BMI | Sex-specific BMI arithmetic moments |
| agongo_women_bmi_mean_sd | Mean 22.28, SD 3.85 kg/m² | Table 1, women, BMI | Sex-specific BMI arithmetic moments |
| agongo_pooled_bmi_mean_sd | Mean 21.63, SD 3.61 kg/m² | Table 1, pooled BMI | Descriptive check; not simultaneously enforced with chosen 50:50 sex mixture |
| agongo_pooled_total_cholesterol_mean_sd | Mean 3.23, SD 0.92 mmol/L | Results, “Mean lipid levels stratified by sex and age category,” opening paragraph | Overall TC arithmetic moments |
| agongo_pooled_hdl_cholesterol_mean_sd | Mean 1.14, SD 0.38 mmol/L | Same Results paragraph | Overall HDL arithmetic moments |

These SDs describe between-person marginal variation; they are neither standard errors nor conditional residual SDs. Uncertainty of these moment estimates is not reported. The source SD denominator convention is unspecified. A later sample-SD check will use ddof=1 as an operational convention, with approximation retained.

Table 1 age means/SDs are men 50/6, women 52/6, pooled 51/6 years. I decline numerical transfer of this restricted-age distribution to the adult target. It supplies context only.

Tables 4–5 univariate BMI coefficients concern log(lipid), with log base unresolved, no adjustments, and unspecified intercept/weighting/row-specific N. Men log-HDL coefficient is −0.007 (95% CI −0.015, 0.001); men and women log-TC coefficients are each 0.013 (0.006, 0.020) per kg/m². They are not raw lipid slopes or the requested age/sex-adjusted coefficients and are excluded from numerical calibration. The published correction (10.1371/journal.pone.0213233) concerns hip/waist and a reference, not the extracted rows.

### Obirikorang 2015: rank dependence

Admitted artifact: `sources/curated/OBIRIKORANG_2015_CURATOR_EXTRACTION.json`; source ID `obirikorang_2015_ashanti`; DOI 10.1371/journal.pone.0129494. Original article: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0129494

Population: 2013 household recruitment in Jachie-Pramso rural (N=360) and Kumasi urban (N=312), Ashanti, Ghana. Prior hypertension, diabetes, coronary heart disease/treatment, pregnancy/lactation, and physical/mental disability were excluded. Age range and pair-specific N are not established in the admitted extraction. BMI is measured weight/height squared; lipids are 12–14-hour fasting venous serum, enzymatic Selectra Pro S assays, mmol/L.

Methods call the operator Spearman rank correlation by community. Table 7 uses lower-left rural and upper-right urban. All six correlations are unadjusted, dimensionless; weighting, tie method, and missing-pair policy are not explicitly reported. No correlation CIs/SEs are supplied. I do not derive them from group N or significance stars.

| Source item | Rural estimate | Urban counterpart | Proposed use |
|---|---:|---:|---|
| obirikorang_rural_bmi_tc | 0.212 | 0.293 | Rural rank constraint used in the joint model |
| obirikorang_rural_bmi_hdl | −0.100 | −0.040 | Rural rank constraint used in the joint model |
| obirikorang_rural_tc_hdl | 0.106 | 0.171 | Rural rank constraint used in the joint model |

Rural BMI–TC is marked p<0.05; rural BMI–HDL and TC–HDL have no star. Lack of a star is not evidence of independence. The urban triplet is context/check-only evidence of community variation; it is not averaged with rural, treated as an independent study, or used to select a preferred target answer.

I propose translating each rural Spearman value into a Gaussian latent correlation via `r = 2 sin(pi * rho_S / 6)`. This is exact under the chosen continuous bivariate Gaussian copula, not an empirically established transformation to Pearson correlation in the source. A further explicit assumption transfers the pooled-within-community rank relationships to each model sex stratum. Consequently neither target pooled Spearman values nor target adjusted OLS/residual statistics are asserted to equal the source numbers.

### Greiner 2021: relative sex scales and age-shape context

Admitted artifact: `sources/curated/GREINER_2021_CURATOR_EXTRACTION.json`; source ID `greiner_2021`; DOI 10.1136/bmjgh-2021-005222. Original article: https://gh.bmj.com/content/6/5/e005222

The article analyzes Malawi MEIRU rural/urban and Uganda Masaka GPC source cohorts, with age ≥18, sex and complete lipid data required, and exclusions for reported pregnancy, HIV positivity, and diabetes. Diabetes definition and row-specific Table 1 missingness are unresolved here. These are source selection conditions, not target exclusions. Malawi uses Beckman Coulter enzymatic laboratory assays; fasting was sought, but random blood accepted after a second failed fasting visit. Specimen matrix is unresolved. Uganda uses Cobas Integra 400 enzymatic colourimetric assays and a described fasted sample. No target assay bridge is established. Weighting is not explicitly reported.

I choose the Malawi rural strata as one coherent reference for two relative sex contrasts and age context; they are not asserted to be Turkana lifestyle categories:

| Quantity | Men | Women | Locator and uncertainty |
|---|---:|---:|---|
| TC geometric mean, mmol/L | 3.6 | 3.9 | Table 2; 95% CIs 3.6–3.7 and 3.9–3.9, rounded |
| HDL geometric mean, mmol/L | 1.05 | 1.10 | Table 2; 95% CIs 1.04–1.06 and 1.09–1.11 |
| Age Q1/median/Q3, years | 24/33/46 | 25/34/48 | Table 1; quantile convention not reported; no estimation uncertainty supplied |

Male group N is 4,534 in both tables; female N is 5,894 in Table 1 and 5,893 in Table 2. These are not guaranteed row-specific denominators. I preserve the discrepancy and do not infer precision weights. The correction is for coauthor names only.

Derived contrasts: TC female/male geometric-mean ratio = 3.9/3.6; HDL ratio = 1.10/1.05. Under common log variance within each lipid, these are also arithmetic-mean ratios in the proposed lognormal model. That equality is a distributional assumption, not a reported arithmetic contrast. I combine these ratios with Agongo pooled arithmetic moments using an explicit cross-study synthesis assumption. No precision weighting or CI for either ratio is claimed. A collapsed rounded CI does not imply zero variance.

The age interior knots 24.5, 33.5, and 47 years are simple averages of the two rural strata's reported Q1/median/Q3. This is a model shape choice, not a claim that an equally weighted mixture has those exact quantiles. The endpoints 18 and 90 years are modeling support choices.

Other Greiner geometric means, low-HDL threshold proportions, and non-HDL geometric means are context only. No geometric mean is relabeled arithmetic, no non-HDL geometric mean is formed by subtracting geometric means, and no source CI width supplies individual variability. All Supplementary Table 3 regression coefficients remain context-only because response/predictor transformations are unresolved and reported adjustments include smoking/alcohol that are absent from the requested design. The flagged urban-women HDL CI (1.15–1.26 around geometric mean 1.15) is unused.

## Review decisions requested

1. Accept or reject the finite-moment Gaussian-copula/lognormal construction and the explicit pooled-source-to-within-sex rank bridge.
2. Review the cross-study combination of Agongo pooled arithmetic moments with Greiner relative sex contrasts and common within-sex log variances.
3. Review the assumption-only demographic fraction, age tails, and modest latent age correlations; these quantities are not numerically identified by evidence.
4. Confirm that all three requested analyses are classified as partially supported, assumption-dependent analyses, with source weighting and assay/selection differences unresolved.
5. Release implementation only after this review. Any change will be recorded; no implementation or execution has occurred.

The sources are different named cohorts/geographies, but participant-level non-overlap has not been audited. Statistics from each paper are dependent constraints, not independent replications. The intended data would support inspection of a declared synthetic scenario; source agreement would not establish target validity, causality, assay equivalence, uncertainty calibration, or publication readiness.

