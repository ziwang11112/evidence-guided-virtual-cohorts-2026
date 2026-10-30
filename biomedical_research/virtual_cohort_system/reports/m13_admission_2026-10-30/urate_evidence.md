# Serum uric acid: source-only admission audit

Date: 2026-10-30. Scope: published non-NHANES evidence for enriching an entirely unmeasured serum marker; no model, generator, individual source dataset, target outcome file, or target analysis was constructed or opened. This is a bounded evidence audit, not a completed systematic review or registered source package.

## Decision

**PARK the broad adult obesity/urate case.** Useful primary evidence exists, including a substantially better independent US lead than the two previously flagged papers. However, the audited set does not yet provide a coherent, population-compatible package of sex/age/BMI conditional location and participant dispersion, interpretable adjusted continuous associations, and enough source covariate context for faithful replay. Do not bridge its gaps by treating survey SEs as SDs, marginal SDs as conditional residual SDs, reversing regression coefficients, or assigning an unreported transformation.

**Best next candidate:** a deliberately narrower, nondiabetic adult Bogalusa-like case, with the target population defined before outcome access. This is a research lead, not admission approval. Narrowing the age/ancestry/selection scope changes the scientific question and would need an explicit future task contract.

## Quantitative primary-source ledger

Reported quantities below remain in their original units. Parentheses denote the explicitly identified SD or confidence interval; no numerical conversions were performed.

### U1 — Yun et al., 2021: independent US cohort, strongest lead

[Primary article, DOI 10.1038/s41366-021-00810-9](https://www.nature.com/articles/s41366-021-00810-9); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8236402/); [retrieved full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8236402/fullTextXML).

Exact locators: Methods → Study cohort, Measurements, Statistical methods; Table 2 → Adult cohort; Figure 2 → adult mediation model.

Bogalusa, Louisiana: 3,402 nondiabetic adults pooled from surveys spanning reported ages 20–56. Assay: Olympus AU-5000, uricase method. Table 2 explicitly identifies means (SD):

| Group | n | Age, years | BMI, kg/m² | Urate, mg/dL |
|---|---:|---:|---:|---:|
| White men | 1,012 | 36.9 (11.0) | 28.6 (6.0) | 6.1 (1.3) |
| White women | 1,209 | 37.1 (10.9) | 28.0 (7.4) | 4.5 (1.2) |
| Black men | 509 | 34.3 (11.5) | 28.2 (7.3) | 6.2 (1.5) |
| Black women | 672 | 35.1 (11.8) | 31.4 (8.7) | 4.6 (1.7) |

Figure 2 reports cross-sectional BMI→urate standardized coefficient **0.322**, adjusting for age, race, sex, smoking and alcohol; no numerical CI. Longitudinal cross-lagged coefficients are different estimands.

Admission gap: no sex×age×BMI urate SD cells or exact cross-sectional standardization implementation here. The identified supplementary DOCX was not inspected.

### U2 — Sun et al., 2014: useful reverse-direction source check, overlapping cohort

[Primary article, DOI 10.1371/journal.pone.0089696](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0089696); [retrieved full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4208749/fullTextXML).

Exact locators: Methods → Study cohort, General examination, Laboratory Analysis; Tables 1 and 2, adult rows and Table 2 footnote.

Bogalusa adults aged 19–54, n=2,447; excluded treatment for hypertension, dyslipidemia or diabetes, nonfasting samples, and missing study variables. Fasting 12–14 hours; Olympus AU-5000 uricase assay. Table 1 urate mean±SD (mg/dL): White men 6.1±1.3 (n=743), White women 4.2±1.1 (939), Black men 6.0±1.5 (329), Black women 4.2±1.2 (436).

Table 2 has age-adjusted **BMI as dependent variable**, urate as predictor. Corresponding unstandardized slopes are 1.38, 2.59, 1.29, and 2.14 kg/m² per mg/dL; standardized coefficients 0.33, 0.44, 0.28, 0.33. Each has p<0.001; CIs are unreported there. BMI itself is expressly omitted from the covariate set for these rows.

These slopes can support a correctly oriented replay diagnostic; neither reciprocals nor casual rescaling yield urate-on-BMI slopes. U1/U2 share the Bogalusa study and overlapping survey periods, so they are not independent confirmations. This source's treatment exclusion also differs from U1.

### U3 — He et al., 2022: clear adjusted categorical BMI contrasts

[Primary full article, DOI 10.3389/fpubh.2022.936717](https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2022.936717/full).

Exact locators: Methods → Data resource and study population, Measurements, Statistical analyses; Table 3 and its footnote; Results → Basic characteristics.

BTH physical-examination cohort, 2017–2018, n=30,158, ages 18–80; stable employees sampled through examination centers. Exclusions include pregnancy, severe disorders and eGFR<60. At least eight-hour fast; Hitachi 7600 uricase assay.

Table 3 urate differences (µmol/L), reference BMI<24:

| BMI category, kg/m² | Men B (95% CI) | Women B (95% CI) |
|---|---:|---:|
| 24–<28 | 23.51 (20.61–26.41) | 25.86 (23.46–28.25) |
| ≥28 | 50.82 (47.30–54.35) | 50.04 (46.28–53.80) |

Adjusted covariates: age, geographic area, BMI, alcohol, smoking, sedentary time, creatinine; additionally menopause in women. These are categorical contrasts with a continuous outcome, not per-unit BMI slopes. Urate is summarized by sex as median/IQR, not mean/SD. Exact effective regression n, intercept, covariate joint distribution and missing-data handling need clarification. Table 3 also contains a CI/p-value inconsistency for men's prior drinking; do not silently repair that row.

### U4 — Qi et al., 2021: age/sex SDs available, but outcome and BMI trimming

[Primary article, DOI 10.1155/2021/2741131](https://doi.org/10.1155/2021/2741131); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8285201/); [retrieved XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8285201/fullTextXML).

Exact locators: §2.1 Subjects, §2.2 Measurement, §2.3 Statistics, Table 1, Table 2 footnote.

Chengdu examination-center records, October 2013–April 2017; analyzed n=122,351 aged 18–99. Ten-to-twelve-hour fast; Olympus AU5421. Table 1 contains sex-by-age mean±SD urate and BMI. Example women: total urate 281.61±58.44 µmol/L; ages 18–29, 283.35±54.51; ages 60–69, 296.24±61.99. Table 2 reports triglyceride-quartile urate contrasts adjusted for age, BMI, fasting glucose and eGFR.

Critical exclusions: urate <90 or >594 µmol/L; BMI <14.86 or >32.65 kg/m²; multiple lipid, glucose, creatinine and eGFR cutoffs. These are outcome/covariate-truncated summaries. They cannot supply unselected obesity-tail variance. No selection correction was attempted. Its center and sampling dates overlap the Liu 2019 source below; do not count them as independent cohorts.

### U5 — Koo et al., 2021: retain descriptive evidence with restrictions

[Primary full article, DOI 10.3904/kjim.2020.116](https://www.kjim.org/m/journal/view.php?number=170514).

Exact locators: Methods → Study population, Statistical analysis; Table 1, urate row and footnote; Figure 2C.

KoGES-HEXA, data collected 2004–2013, ages 40–79; n=172,970 after excluding 90 with missing key information and 297 taking gout medication. Table 1 gives mean±SD urate: men 5.71±1.27, women 4.21±0.96 mg/dL. These are valid descriptive SDs for that selected cohort. Figure 2C is an age/sex mean curve, not a tabulated conditional SD surface. The accessed Methods do not identify a specific assay platform/reagent. No adjusted continuous BMI→urate coefficient is reported. Restriction, medications and age range remain material; this paper alone does not close the admission gap.

### U6 — Zhou et al., 2019: quantitative distributions, unresolved regression scale

[Primary full article, DOI 10.1186/s12967-019-02142-9](https://link.springer.com/article/10.1186/s12967-019-02142-9).

Exact locators: Methods → Study population, Data collection, Statistical analyses; Results → Linear relationship and Nonlinear relationship; Tables 1–3; Figure 1 legend.

Coastal China, n=14,039; excludes weight/lipid/urate/glucose/BP-lowering medication and liver, severe renal or heart disease. Twelve-hour fasting, Sysmex Chemix-180. Reported sex means±SD are men 349.62±85.30 and women 267.37±70.79 µmol/L. The text describes coefficients both as per-SD and per-unit changes, calls them fold changes in the abstract, and reverses sign descriptions in places. Study dates also differ between abstract and Methods. Adjustments include age, smoking, alcohol, occupation, BP, glucose, renal function and lipids, with TG inconsistently described across sections.

Do not repair the coefficient scale by plausibility or by comparing expected target slopes. Keep regression rows quarantined pending an author clarification or authoritative correction. Descriptive means/SDs remain selected-population summaries, not a complete conditional model.

### U7 — KNHANES dietary-fiber study, 2024: survey SE is not SD

[Primary full text, PMC11165754](https://pmc.ncbi.nlm.nih.gov/articles/PMC11165754/).

Exact locators: Methods → Study population, Measurement and definition, Statistical analysis; Table 1 header and urate row.

KNHANES VII 2016–2018, adults >20, n=15,278; excludes eGFR<30. At least eight-hour fasting; Hitachi 7600-210 colorimetry. Table 1 explicitly labels **mean±SE**: men 5.94±0.02 and women 4.41±0.01 mg/dL. Survey weights and complex-sample analysis were used. These small numbers measure uncertainty in estimated means, not dispersion of individual urate values. Multiplying by √n without the survey design/effective sample size would not establish the desired SD. Reported dietary-fiber association is a different estimand from an adjusted BMI association.

### U8 — Liu et al., 2019: potentially relevant but full tables not recovered

[Primary publisher record, DOI 10.4158/EP-2018-0426](https://www.sciencedirect.com/science/article/pii/S1530891X20359000); [PubMed record](https://pubmed.ncbi.nlm.nih.gov/30657365/).

Title: Association Between Serum Uric Acid Level and Body Mass Index in Sex- and Age-Specific Groups in Southwestern China. The accessible record reports n=144,856 aged 20–79, Chengdu examination center, October 2013–April 2017. The full quantitative tables were not accessible in the retrieved publisher response. No table values, assay specification, dispersion or regression scale were inferred from its abstract. This is a retrieval lead only.

## What a faithful replay still needs

1. Fix the actual scientific target population and available observed covariates, including treatment and renal-function eligibility. Evidence from heterogeneous selections cannot be joined by assigning them one common population label.
2. Pick an internally consistent source context. U1 offers useful marginal moments and a standardized forward association; U2 offers well-oriented reverse associations; U3 offers categorical contrasts. These are different constraints, not interchangeable slopes.
3. Obtain the needed covariate-only source context or declare and stress-test its joint-distribution approximation. Means and marginal SDs do not identify age–BMI–smoking–alcohol dependence. Source replay on invented independent covariates would add an assumption, not reproduce the study population.
4. Resolve U1's standardization details, precision and supplement before treating 0.322 as an executable comparator. An operator must match the original estimand. Verify that the harness supports that estimator instead of substituting an easier regression.
5. Recover conditional spread or explicitly specify its assumption. Marginal SD includes explained variation and cannot simply become residual SD after adding age/BMI effects. IQR and SE conversions are not admitted substitutes.
6. Use documented assay/unit harmonization if sources are combined. This audit leaves mg/dL and µmol/L unconverted. Different instruments and fasting definitions still matter after unit conversion.

## Source fit versus independent scientific evaluation

All cited numbers are source evidence, not validation results. A check that reproduces a statistic used to choose parameters is a fitted-source check. A source statistic reserved before fitting can be an internal source holdout, but same-cohort publications are not external validation.

For a future public-target experiment, an evaluator should fix eligibility, survey design, estimands, uncertainty intervals, missing-data rules and a limited initial/final evaluation schedule before releasing any outcome information. The builder receives allowed observed covariates only and freezes the evidence package, generation rule and analysis plan before the evaluator uses measured target urate. Report discrepancies with measured-target analyses regardless of direction or significance. Reproducing a source-informed BMI coefficient in a new target is external transport evaluation, but it is not evidence for every unreported analysis.

Potential broader checks—conditional dispersion, hyperuricemia tails, age-by-sex patterns or renal-function associations—must be designated beforehand as fitted, held out, or unsupported. Do not call them independent after using their published or target values for calibration. Generated-person residuals, source-estimate uncertainty and transport uncertainty must remain distinct. No such checks were run in this audit.

## Information-boundary and retrieval record

No individual NHANES/target outcomes, target files, or target analysis outputs were accessed. No NHANES outcome paper was deliberately opened. **However, broad searches that explicitly excluded NHANES still returned incidental NHANES outcome snippets, and the Koo full article's discussion contained secondary NHANES summaries.** Those quantities were not extracted into this note, used as evidence, or used to choose a numerical parameter. Consequently this audit must not be described as guaranteeing zero target-related exposure.

Search was tightened to named primary articles and then to Europe PMC XML restricted to Methods/Results. If the later experiment requires strict literature-level target blindness, supply screened source-only artifacts to a fresh builder context; this reconnaissance context should not serve as a certified blind generator. Retain this limitation in the provenance record.

PMC browser pages sometimes returned anti-bot responses; successful XML reads were from Europe PMC, selecting only specified article sections. No data generation, source replay, model fitting, target scoring or source-admission registry mutation occurred. Only this Markdown report was written.
