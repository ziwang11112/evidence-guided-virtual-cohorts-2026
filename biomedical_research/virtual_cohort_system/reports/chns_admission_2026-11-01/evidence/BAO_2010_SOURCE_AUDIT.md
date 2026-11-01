# Bao 2010 external-source audit

1 November 2026. **Potentially useful new source evidence: a marginal HbA1c–fasting-plasma-glucose Pearson correlation and selected marginal summaries. This is a candidate extraction, not an approved builder packet or an admitted CHNS case.** It does not identify an adjusted five-variable model or the relationship in a population excluding all diabetes.

Original: Bao et al., *Glycated haemoglobin A1c for diagnosing diabetes in Chinese population: cross sectional epidemiological survey*, BMJ 2010;340:c2249, [DOI 10.1136/bmj.c2249](https://doi.org/10.1136/bmj.c2249). The [publisher full text](https://www.bmj.com/content/340/bmj.c2249) was read through the requested Chrome extension in a separate research tab. Methods, relevant Results and limitations were inspected; Tables 1, 2, 4 and 5 were expanded and read. Table 3's caption and surrounding high-risk-subgroup description were inspected; its cells were not extracted because the subgroup rule remains insufficiently precise for this task. All locators below refer to that original, not a review or search snippet.

## Population and source independence

Methods, **Study design and population**: Shanghai Diabetes Study II (SHDS II), six Shanghai communities, May 2007–August 2008; multistage stratified sampling. Age strata were 20–29, 30–39, 40–49, 50–59 and at least 60, with allocation based on community age structure. The survey enrolled 5,372 participants aged 14–79. Exclusions included cancer, severe psychiatric disturbance, chronic kidney disease, pregnancy and glucocorticoid treatment. The analysis then excluded 360 previously diagnosed diabetes cases, 87 with missing questionnaires and 39 younger than 20, leaving 4,886 (1,828 men; 3,058 women).

The text describes the analysed participants as **over 20**, whereas its explicit age exclusion is **under 20**. Do not silently resolve the exact age-20 boundary. The full-survey upper observed age is not by itself an explicit population-support rule. No separate anemia exclusion was stated in the inspected eligibility paragraph; the Discussion's anemia caveat is not an implemented exclusion.

This is a **no previously diagnosed diabetes** sample, not an all-diabetes-excluded sample. It retains normal glucose tolerance (NGT; 3,748), impaired glucose regulation (837), and screen-detected diabetes (301). Conditioning on FPG below 7.0 mmol/L would change the reported correlation and margins; the paper does not supply that restricted correlation.

The original identifies SHDS II, rather than CHNS, as its sampling frame. Its place/time and study identity support treating it as an external source family, not a CHNS target-results paper. Individual-level non-overlap was not tested or proved. The coordinator reports that the prior workspace exact-DOI search found no existing audit; this reviewer did not repeat a whole-workspace search. Citations to other Shanghai studies and other glycemia papers were visible in the article, but none was followed or imported as new evidence.

## Measurements and statistical operators

Methods, **Anthropometric and biochemical measurements**: 6 am attendance following a stated 10-hour overnight fast; height and weight measured, BMI defined in kg/m². A fasting venous sample preceded a 75 g oral glucose tolerance test. **Plasma** glucose used the glucose oxidase method, in mmol/L. HbA1c used HPLC, with instrument printed **HLC-73G7, Tosoh**, in percent. Do not silently correct this printed model name to a different familiar instrument. HbA1c/FPG/two-hour glucose were measured within two hours of collection. Participation in the Chinese Ministry of Health HbA1c quality-assessment programme is reported; direct NGSP/IFCC certification is not established by that statement. Reported assay coefficients of variation are analytical precision, not participant SD or an association's SE.

Methods, **Statistical analysis**: Pearson correlation is named for HbA1c versus fasting and two-hour glucose. No age, sex, BMI or other covariate adjustment is specified for those correlations. The text reports means/SDs for some variables and medians/IQR for skewed variables, so table-specific labels control. It does not explicitly state analytic survey weights, a correlation missingness rule, a quantile algorithm, or correlation uncertainty calculation. Multistage sampling is reported, but neither weighted nor explicitly unweighted estimation is confirmed. These are recorded as unknown in the candidate JSON; a future reviewer must not mechanically turn absence of a weighting statement into an S1 `weights: none` assertion.

## Extracted constraints and uncertainty

Results, paragraph immediately following Table 1: **Pearson r(HbA1c, FPG) = 0.619, P<0.001**. The corresponding two-hour-glucose correlation is 0.622, P<0.001; it is contextual because a matching CHNS OGTT field has not been established. The paper gives no SE or CI for either correlation in that paragraph. The overall analysis n is 4,886; pair-specific correlation n is not explicitly stated. No Fisher interval was manufactured. The threshold-analysis 95% CIs in Table 2 are not uncertainty for r.

[Table 1](https://www.bmj.com/content/340/bmj.c2249#T1) supplies the following directly reported marginal summaries. Brackets are **Q1–Q3 endpoints**, not an SD, SE, range or IQR width:

| Variable | Overall | Men | Women |
|---|---:|---:|---:|
| Age, years: median [Q1–Q3] | 49.4 [37.9–57.7] | 49.0 [37.4–59.0] | 49.5 [38.2–56.9] |
| BMI, kg/m² | Median 23.5 [21.4–25.9] | **Mean 24.1, SD 3.3** | Median 23.2 [21.2–25.5] |
| FPG, mmol/L: median [Q1–Q3] | 5.2 [4.8–5.6] | 5.2 [4.7–5.6] | 5.2 [4.8–5.6] |
| HbA1c, %: median [Q1–Q3] | 5.6 [5.3–5.9] | 5.6 [5.4–5.9] | 5.6 [5.3–5.8] |

Results, threshold paragraph before Table 2: NGT-subgroup HbA1c **mean 5.5%, individual SD 0.4%**. These are restricted-group moments, not overall moments. NGT membership depends on the glucose-tolerance classification, including two-hour glucose; it cannot be approximated by an HbA1c cut-off or FPG alone and called the same source selection.

[Table 5](https://www.bmj.com/content/340/bmj.c2249#T5) reports mean/SD for age and BMI in two overlapping selected groups: OGTT-defined diabetes (n=301), age 54.2/11.9 years and BMI 25.5/3.7 kg/m²; HbA1c≥6.3% (n=367), age 56.4/10.4 and BMI 25.8/3.5. Their overlap is 189. These are not independent groups or unselected population moments. Their FPG and HbA1c summaries remain medians/IQR despite the explicit age/BMI mean labels. No conversion to Gaussian moments was attempted.

## Threshold evidence has exact denominator requirements

Methods, **Definitions**, applies the paper's historical WHO 1999 reference: diabetes if FPG≥7.0 mmol/L **or** two-hour plasma glucose≥11.1 mmol/L. This is the source's analytic definition, not current clinical advice. [Table 4](https://www.bmj.com/content/340/bmj.c2249#T4) reports HbA1c≥6.3% counts 74/3,748 NGT, 104/837 impaired glucose regulation, 189/301 diabetes; at ≥6.5%, counts are 33/3,748, 56/837 and 152/301. Percentages use the **column glucose-tolerance group**, not the people with high HbA1c, as denominator. Nested Table 1 percentages for high FPG similarly use the diabetes group, not all 4,886.

Table 2 gives 95% CIs for diagnostic sensitivity/specificity and predictive values. Their denominators differ by statistic. FPG is also part of the reference diabetes definition, so its reported perfect specificity is partly definitional, not an independent validation of a test. The source-selected 6.3% threshold must not become a prospectively chosen CHNS clinical optimum. High-risk Table 3 is quarantined: the phrase naming age over 45 and BMI over 24 does not uniquely establish an executable AND/OR/other-risk-factor selection rule. No reference was opened to fill that gap.

## Consequence for the proposed CHNS construction

The paper closes part of the **unadjusted glycemic joint-evidence gap** in a Chinese community source that retains undiagnosed diabetes. It does not supply HbA1c-on-FPG slope/intercept, residual variance, age/BMI-adjusted effects, predictor covariance, or subgroup-specific correlations. A Pearson correlation plus quartiles does not recover a unique covariance, copula or joint tail. Splicing this r into Lifelines/Pani's more restrictive populations is a modelling assumption, not a pooled empirical result.

Current CHNS `GLUCOSE` is a serum measurement candidate; Bao explicitly measures plasma. Shared glucose-oxidase terminology, percent HbA1c units or similar instrument names do not establish measurement identity. Intended fasting duration, specimen timing, population exclusions and diabetes definitions also differ. The acquired schema has not established two-hour OGTT, so OGTT-defined subgroup constraints and diagnostic checks are currently unavailable for faithful CHNS replay. These are applicability gaps even when the numerical operator is supported.

Keep the marginal correlation and clearly labelled summaries as **pending constraint candidates**. Under semantic feedback v1, unknown essential weighting/quantile/selection semantics must remain unresolved or `not_computable`; missing sampling SE alone does not justify inventing one. Any approximation requires explicit source-population and measurement assumptions and cannot override a known operator mismatch. No target sign or desired target coefficient was chosen, and no CHNS relationship was inspected.

## Deliverables and resource accounting

[BAO_2010_CONSTRAINT_CANDIDATES.json](BAO_2010_CONSTRAINT_CANDIDATES.json) contains selected aggregate candidates, original locators, population/measurement definitions, uncertainty roles, unknowns and non-admission flags. It is not an executable S1 sidecar and must not be copied into one without source/recipe review.

Exactly **one allocated new original** was deeply read in this subtask. The coordinator separately allocated MIND-China; its actual consumption and the global counter are coordinator-managed. One publisher article was navigated; inline tables are parts of that same article, not additional original studies. No reference article, target paper, raw data, generator or target computation was opened/run. No article/PDF/body file or screenshot was saved. Direct-download bytes: **0**; browser page/table/ad traffic was unmetered, so this is not a zero-network-byte claim. Only this authored audit and the candidate JSON were written; STATE and all frozen files remain unchanged.
