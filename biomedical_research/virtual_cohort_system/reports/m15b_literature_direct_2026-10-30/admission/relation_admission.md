# M15B relation admission — original-paper review

Decision date: 2026-10-30. Scope: evidence admission and operator identification only. No cohort was generated, no relation was imposed in code, and no target outcome or target analysis result was accessed. This is a scientific eligibility recommendation, not a manufactured harness source-approval record.

## Decision and first eligible case

**Conditional GO for a source-informed, cross-sectional whole-cohort pilot of serum urate, BMI, age and sex, retaining race as an auxiliary variable, for Black/White adults aged 20–56.** A nondiabetic, Bogalusa-like population is the closest first case. Extension to all US adults, other racial/ethnic groups, disease/treatment strata, or national prevalence is an explicit transport hypothesis. The data can support an inspectable joint-model experiment; they do not identify a unique population distribution or establish downstream scientific usefulness.

The two known originals are sufficient to admit this first experiment. Yun 2021 supplies the exact 20–56 age range and race/sex-specific means and individual-level SDs; Sun 2014 supplies a native, age-adjusted **BMI-on-urate** relationship with the same basic measurements and race/sex strata. A published reverse-direction regression is a usable constraint on a joint distribution and a usable analysis of generated rows. It need not be inverted into an urate-on-BMI equation. A perfectly reported conditional residual SD is not an admission prerequisite. Published marginal SDs are legitimate model inputs, with the unreported conditional variance and age relationships kept as assumptions.

For a first bounded **transport test**, enriching 200 permitted real age/sex/race/BMI covariate rows with urate is preferable: it holds covariate composition fixed and tests the additional variable. The builder must receive no real urate or target outcome summaries. Whole-cohort synthesis of 200 rows remains eligible when exercising requested row count and column expansion is the central objective, but its later evaluation combines covariate-distribution transport with conditional-urate transport. Neither design establishes national representativeness, and small four-stratum cells limit precision. Any later urate-on-BMI analysis is a related directional analysis of the same joint relation, not an independent novel relationship merely because the regression is reversed. This mode advice does not authorize or perform target-data access in this admission task.

The first agent-built candidate should declare which source defines its main population and which source supplies a transfer or sensitivity constraint. A coherent choice is Yun's nondiabetic 20–56 population and marginal anchors, with Sun's native regressions admitted as approximate transported relationship checks. A separate Sun-shaped context should retain Sun's original 19–54 range and selection when the interface permits it. If the task instead fixes all adults 20–56, Sun coefficients remain approximate because the source includes age 19, excludes ages 55–56, and excludes several treated groups. Do not call a 20–56 check an exact replication of Sun.

**PARK only the stronger claims:** an identified conditional urate model; an empirically known age effect; causal effects; individual prediction; calibrated tails/hyperuricemia prevalence; national representativeness; or a claim that reproduced source summaries establish validity of unreported target analyses. These limitations do not require parking the joint pilot itself.

## Originals inspected and selection

| Item | Original and exact locators | Adult population and selection | Measurement / adjustment context |
|---|---|---|---|
| U1 | Yun et al., 2021, DOI [10.1038/s41366-021-00810-9](https://doi.org/10.1038/s41366-021-00810-9), PMC8236402 version 1; Methods `Sec3`–`Sec5`, adult portion of `Tab2`, `Fig2` caption/formula | Bogalusa, Louisiana; 3,402 nondiabetic Black/White adults, age 20–56. Cross-sectional records selected once per participant from adult surveys in 1995–2000, 2001–04 and 2009–16. Hypertension treatment was not an exclusion; treated BP was adjusted for BP analyses. | Height/weight measured twice and averaged; BMI kg/m². Serum urate mg/dL by uricase, Olympus Au-5000. Adult mediation models adjust age, race, sex, smoking and alcohol drinking. |
| U2 | Sun et al., 2014, DOI [10.1371/journal.pone.0089696](https://doi.org/10.1371/journal.pone.0089696), PMC4208749; Methods `s2b`–`s2e`, `pone-0089696-t001`, `pone-0089696-t002`, Results `s3` paragraph introducing Table 2 | Bogalusa; 2,447 Black/White adults, age 19–54, from eight surveys in 1988–2010. Excluded treatment for hypertension/dyslipidemia/diabetes, nonfasting samples, and missing study variables. The paper does not say that exclusion of diabetes treatment equals exclusion of all diabetes. | Participants instructed to fast 12–14 hours; compliance interviewed. Replicate anthropometry averaged. Urate measured by uricase, Olympus Au-5000. Table 2 BMI outcomes are adjusted for age; BMI is explicitly excluded as a covariate in its own outcome model. |

Both sources concern Bogalusa and share investigators and overlapping survey periods. Their adult populations are not independent replications; exact participant overlap is not reported. Do not pool sample sizes or estimate precision as if independent. Yun's later survey mix, older age distribution and broader treatment inclusion can explain some differences, but the originals do not isolate their causes.

## Admitted descriptive anchors

The following are **reported arithmetic means (SD)** within race/sex groups, not conditional residual SDs or standard errors. Group sizes are reported counts, not US population weights. Sun's group comparisons used age adjustment; that does not turn its displayed SDs into age-conditional residual SDs.

| Source / adult stratum | n | Age, years | BMI, kg/m² | Urate, mg/dL |
|---|---:|---:|---:|---:|
| U1 White male | 1,012 | 36.9 (11.0) | 28.6 (6.0) | 6.1 (1.3) |
| U1 White female | 1,209 | 37.1 (10.9) | 28.0 (7.4) | 4.5 (1.2) |
| U1 Black male | 509 | 34.3 (11.5) | 28.2 (7.3) | 6.2 (1.5) |
| U1 Black female | 672 | 35.1 (11.8) | 31.4 (8.7) | 4.6 (1.7) |
| U2 White male | 743 | 33.2 (8.8) | 27.6 (5.6) | 6.1 (1.3) |
| U2 White female | 939 | 32.7 (8.9) | 26.4 (6.8) | 4.2 (1.1) |
| U2 Black male | 329 | 31.3 (9.1) | 27.2 (6.7) | 6.0 (1.5) |
| U2 Black female | 436 | 30.4 (8.5) | 29.1 (7.9) | 4.2 (1.2) |

Eligible checks: arithmetic mean and sample SD of each numeric variable after selecting the appropriate source age/population and race/sex stratum. The harness `mean` and `sd` operators are suitable. Matching rounded values needs a declared rounding/Monte Carlo policy; the originals do not provide full uncertainty distributions for these summaries. There is no hidden-SD test here: the full source SDs can enter the evidence bundle and construction.

## Admitted relationship operators

### U2: native raw BMI-on-urate coefficients — preferred first joint constraints

Table 2 reports the urate coefficient in `BMI = intercept + b × urate + age term + error`, fitted separately in each race/sex stratum. The raw coefficient's units are `(kg/m²)/(mg/dL)`.

| Adult stratum | Reported raw b | Reported standardized coefficient | Reported significance |
|---|---:|---:|---|
| White male | 1.38 | 0.33 | p < 0.001 |
| White female | 2.59 | 0.44 | p < 0.001 |
| Black male | 1.29 | 0.28 | p < 0.001 |
| Black female | 2.14 | 0.33 | p < 0.001 |
| All adults | 1.87 | 0.43 | p < 0.001 |

The four stratum-specific raw coefficients are suitable first operators. Required declaration: `kind=ols_coefficient`, `outcome=bmi`, `predictors=[urate, age]`, `term=urate`, `include_intercept=true`; select the given race and sex in a Sun-shaped adult context. Predictor values must be numeric and the design full rank. All these fields are supported by `docs/SOURCE_CHECKS.md`. Intercept inclusion and a linear age term are conventional reconstructions of the described multivariable linear regression, not supplied model code. Label that detail as an analysis-reconstruction assumption if exact implementation is required.

The all-adult coefficient is secondary: Table 2 and surrounding text clearly state age adjustment and the BMI footnote, but do not explicitly enumerate whether the pooled linear model also included race and sex. Table 3 enumerates race/sex for its separate logistic model; it cannot settle Table 2's design. Do not silently choose a pooled adjustment set and mark that check exact. The four stratified coefficients avoid this ambiguity.

No SE or confidence interval for these coefficients is given in Table 2. The p-value threshold is not a known SE, and the standardized coefficient is not a correlation. Do not fabricate inverse-variance weights. A failure to reproduce a transported Sun coefficient can reflect source context, model assumptions, extraction or implementation; it is not automatically evidence about the hidden target.

For clarity, residualize BMI and urate on the same age adjustment within a stratum and denote the residuals B* and U*. The reported slope constrains `Cov(B*, U*) / Var(U*)`. The reverse slope would be `Cov(B*, U*) / Var(B*)`, so it is **not 1/b**. Unknown residual variances and age covariances prevent identification of a unique forward slope from the reported raw slope plus marginal SDs. An agent may propose a joint distribution satisfying native summaries and regression constraints; the model's other features remain declared assumptions.

### U1: standardized urate-on-BMI path — informative, conditional operator

Figure 2 reports adult beta1 = **0.322** for the BMI-to-urate component of the cross-sectional mediation model. The caption labels the coefficients standardized. The methods put age, race, sex, smoking and alcohol drinking in the adult adjustment set. This is not a raw mg/dL-per-BMI-unit coefficient and not an unadjusted Pearson correlation.

Exact reproduction requires source-compatible coding and joint distributions for age, race, sex, BMI, smoking, alcohol and urate, plus the paper's standardization convention. The main text does not fully specify smoking/alcohol definitions, coding or the exact standardization implementation for this mediation coefficient. The separate cross-lag analysis explicitly residualizes and Z-transforms within race/sex; do not automatically transfer that preprocessing to the mediation model.

The current declarative OLS operator performs no implicit encoding or standardization. A predeclared compatible derived-variable procedure or an appropriate standardized-coefficient operator would be needed for a numeric check. Until then, retain 0.322 as reported standardized evidence and a directional/context clue or mark its replay approximate/not computable. It is **not a hard admission requirement** when the native U2 operators are available. No multiplication by a convenient SD ratio will be presented as a reported raw slope.

U1's longitudinal adult coefficient 0.068 concerns baseline BMI to later urate, with baseline/follow-up controls and follow-up time. It belongs to a different temporal operator and must not be substituted for the same-visit cross-sectional relation. Its adult longitudinal sample is also not the 3,402-person marginal cohort.

## Exact information needed before a builder is launched

1. A frozen task contract states whole-cohort synthesis versus enrichment, row count, units, allowed cells, adult age range, intended target population and permitted source artifacts. For the first whole-cohort pilot, include ID, age, recorded sex, BMI and urate, and retain race as an auxiliary variable or stratum. If the visible panel has only age/sex/BMI/urate, a race mixture cannot be inferred uniquely from it.
2. Define disease/treatment and fasting eligibility or explicitly declare their transport mismatch. Sun's treatment exclusions must not be recast as Yun's nondiabetic definition. Define how ages 55–56 are covered, and retain the original Sun age range when replaying a separate source context. No study reports the requested 20–56 national adult joint distribution.
3. Admit both complete originals, their hashes, source locators, extracted reported values and the distinction between primary marginal anchors and approximate relationship constraints. The controller, not this note, performs any harness registration.
4. An agent chooses the joint distribution and relationship handling; it records shape/tail assumptions, bounds, age–BMI and age–urate dependence, conditional residual variation, heterogeneity and source-to-target transport. It checks that the implied covariance/variance structure is mathematically valid and does not silently default unreported relationships to independence. Missing age slopes do not prevent calculating the native BMI-on-urate coefficient on simulated rows, but they leave construction underidentified.
5. If U1's standardized path is used quantitatively, add compatible smoking and alcohol variables/coding and the standardization definition. Their marginal prevalence alone is insufficient to reconstruct their joint effects. Otherwise admit that path as context without pretending to check it.
6. Freeze source operators and scientific assumptions before generation and keep any later target outcomes outside builder feedback. A future source-statistic match is a construction/replay check, not independent target validation. No candidate, tests on generated rows, or execution-backed checks have been run during this admission task.

The unreported relationships can be explored by a small set of named sensitivity assumptions. Such scenarios are not extra empirical samples and have no automatic probability interpretation. Differences between U1 and U2 may motivate sensitivity contexts; they should not be erased by fitting one synthetic population simultaneously to incompatible population summaries.

## Access, budget and incidental exposure

Complete records are in `evidence_access.json`. U1 was read from the supplied cache and copied byte-for-byte into this task's private source directory. U2 was downloaded once from the exact Europe PMC full-text XML endpoint after two browser-renderer access failures. No search query was issued, no third paper was opened and no target dataset was opened. Budget used: **0/3 search queries; 1/2 new primary full texts**. Successful network full-text downloads: 1. Browser-renderer failures: 2. They yielded no article contents.

Sun Discussion `s4`, paragraph 2 (`/article/body/sec[4]/p[2]`), contains a pediatric NHANES comparison, and its references include the associated publication. This exposure occurred while reading the authorized source's original text and is retained in the access record. No linked NHANES original was searched/opened/downloaded; those incidental comparison findings are excluded from admitted parameters and decision criteria. Yun's inspected original contains no NHANES string. This is an exposure disclosure, not a claim that the reader never encountered the term or any external-study result.

Yun links one supplementary DOCX; it was identified but not downloaded. Sun's retrieved XML has no supplementary-material element. The main originals already contain the required marginal and native regression anchors, so no additional full text or supplement was needed to decide this conditional admission. Unretrieved supplements are not treated as inspected evidence.

Private originals: `private/source/PMC8236402.cached-original.fullText.xml` and `private/source/PMC4208749.fullText.xml`. Small private locator extracts retain the inspected methods/tables. Neither the source numbers nor construction instructions have been sent to any builder.
