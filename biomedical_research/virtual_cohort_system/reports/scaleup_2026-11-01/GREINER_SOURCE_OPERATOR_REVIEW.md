# Greiner et al. 2021: external lipid-source operator review

Prepared 1 November 2026 (America/Chicago). This is an original-paraphrase audit of one external original study, counted as study 2 of the current 12-study allowance; Turkana target-method inspection was study 1. The supplement and correction belong to this same study. No additional original, target participant data, generator, calibration or experiment was accessed or run.

## Decision

**Admit the paper as external relational and distributional evidence; retain numerical regression checks as provisional, not calibration-ready.** It provides substantially more than unrelated marginal means: sex-specific HDL–BMI and HDL–non-HDL relationships, cohort-specific geometric means, and explicitly defined low-HDL proportions. These are useful constraints for a declared construction scenario. They do not establish a universal African lipid law or identify the target joint distribution in Turkana.

For the proposed measured TC/HDL case, non-HDL is a useful derived quantity because it equals TC minus HDL and does not require triglycerides or calculated LDL. A relationship involving non-HDL can constrain the joint behavior of the two measured lipids. It must not be counted as an additional independently measured biomarker.

## Material independently inspected

- [Primary main article](https://gh.bmj.com/content/6/5/e005222), including Methods, relevant Results, figure captions and expanded Table 2.
- The publisher's linked [DC2 supplement dated 8 June 2021](https://gh.bmj.com/content/bmjgh/suppl/2021/06/08/bmjgh-2021-005222.DC2/bmjgh-2021-005222supp001_data_supplement.pdf), especially Supplementary Table 3 spanning PDF pp.3–4. The eight-page document was viewed through Chrome, not downloaded. The older DC1 file was not compared byte-for-byte, so this audit does not infer what changed between versions.
- [Published correction](https://gh.bmj.com/content/6/6/e005222corr1): corrects the names Moffat Nyirenda and Beverley Shields. It does not state a statistical correction and does not resolve the numerical or reporting ambiguities below.

All three were opened in separate agent-created wang Chrome tabs. No third-party file or screenshot was saved locally. The only new local artifact from this task is this review.

## The source population and measurement are part of every operator

The African evidence comes from Uganda's Masaka General Population Cohort and Malawi's MEIRU urban/rural survey. UK comparisons use EXTEND and the Exeter Family Study. These are distinct named sampling frames from the Turkana Kenya study, not an individual-level overlap audit. The paper's analyses exclude participants younger than 18, people with diabetes, HIV-positive participants and those reporting pregnancy; missing sex/lipid information also affects inclusion. Male/female analyses are separate, and Malawi urban/rural groups are separate in descriptive summaries and figures.

These health exclusions cannot be reproduced from the currently listed Turkana fields, which lack the necessary flags. A target without those exclusions is an explicitly different population. The builder must not declare the target diabetes-free, HIV-negative or nonpregnant, or invent prevalence weights to erase the difference. Restricting target age or substituting a single glucose threshold does not reproduce these source eligibility rules.

The source uses laboratory enzymatic assays: a Beckman Coulter Chemistry Analyser in Malawi and enzymatic colourimetric assays on a Cobas Integra 400 in Uganda. The principal Methods paragraph describes fasted blood collection, but the detailed Malawi protocol allows a random sample after two unsuccessful fasting visits. Consequently, the source should not be represented as uniformly verified fasting. The inspected main text does not supply a validated conversion from those laboratory methods to Turkana's immediate CardioChek Plus panel on venous EDTA blood. Unit conversion does not establish assay, specimen or fasting equivalence. Source values are reported in mmol/L, whereas Turkana repository metadata reports mg/dL.

## Regression extraction and operator meaning

The following are reported coefficients for the pooled sub-Saharan-Africa columns in Supplementary Table 3, not separate Kenyan, Ugandan or Malawian conditional equations. Brackets are reported 95% confidence intervals, not participant variation or residual SD.

| Predictor and adjustment | Men: coefficient [95% CI] | Women: coefficient [95% CI] |
|---|---:|---:|
| BMI, unadjusted | −0.007 [−0.009, −0.005] | −0.004 [−0.005, −0.003] |
| BMI, age and smoking | −0.007 [−0.009, −0.004] | −0.004 [−0.005, −0.003] |
| BMI, age, smoking and alcohol | −0.006 [−0.008, −0.003] | −0.004 [−0.005, −0.003] |
| Non-HDL, unadjusted | 0.046 [0.038, 0.054] | 0.041 [0.036, 0.047] |
| Non-HDL, age and smoking | 0.041 [0.033, 0.049] | 0.046 [0.040, 0.052] |
| Non-HDL, age, smoking and alcohol | 0.043 [0.035, 0.051] | 0.046 [0.040, 0.052] |

Table 3 gives BMI analysis counts of 10,667 men and 15,454 women in those African columns. The unadjusted non-HDL rows use 10,701 and 15,515; adjusted non-HDL rows use 10,699 and 15,510. These are operator-specific counts. Do not substitute a single cohort-wide denominator for every statistic or treat overlapping cohorts/adjustments as independent evidence replicates.

**Orientation.** Main Figures 2 and 4 explicitly display HDL at levels of BMI and non-HDL, respectively; the corresponding coefficient rows should be interpreted in that orientation. Table 3 itself describes relationships rather than printing a full model formula. These values are not correlations, standardized effects, reverse-regression slopes or causal effects. In particular, the reverse slope is not generally the reciprocal. Non-HDL must be derived from the same TC and HDL values, rather than generated independently and allowed to violate the identity.

**Transformation remains unresolved.** The main Analysis section says nonnormal variables were log-transformed and that geometric summaries were reported when the transformed variables were normal. It does not unambiguously map that statement onto each Table 3 regression response and predictor. Table 3 has no explicit raw/log formula or coefficient-unit annotation; the figures' raw-unit axes do not prove the exact linear-model scale. The audit therefore does not relabel these coefficients as raw mmol/L-per-BMI slopes or as log-scale effects. No software code or author clarification was obtained. Intercept and weighting conventions also are not explicitly specified in the inspected table.

A strict check needs the exact response and predictor transforms, weighting and source context. A declared raw-scale interpretation could be used as an assumption-defined scenario after review; it must not be described as a verified reconstruction. Under a raw/raw interpretation, converting both HDL and non-HDL by the same unit factor leaves their slope unchanged, whereas a raw HDL-on-BMI coefficient changes with the HDL unit factor. Log-scale formulas have different implications. This is why unit conversion must follow, not precede, resolution of the operator.

**Adjustment sets are not interchangeable.** An age/sex/lifestyle-adjusted target regression is not the same statistic as the unadjusted, sex-specific source slope. Nor can an age-only target fit reproduce an age-plus-smoking source estimate. Turkana's listed fields lack smoking and alcohol, so the adjusted source operators are currently unavailable on that table. One must not silently drop unavailable covariates. The reported stability across adjustment sets is useful contextual evidence, not evidence that omitted adjustment is immaterial in Turkana.

**Joint-model coefficients require care.** The unadjusted HDL–BMI and HDL–non-HDL slopes come from separate regressions. They cannot be inserted side-by-side as the partial coefficients of one HDL equation without additional information. Because non-HDL is TC minus HDL, its relationship with HDL contains both biological dependence and algebraic coupling. It is a constraint on the joint law, not an independent assay validation or a substitute for a TC–HDL correlation.

## Geometric means, threshold proportions and uncertainty

Table 2 explicitly labels starred lipid summaries as geometric means with 95% CIs. For a positive variable the corresponding point-summary operator is the exponential of the mean log value, not the arithmetic mean. The CI describes uncertainty in an estimated location. It is not an SD, a normal range, a residual distribution or a permissible range for every generated person. No individual-level SD should be manufactured from the CI and sample size without a justified, disclosed sampling/inference model; the rounded intervals are insufficient to certify such a reconstruction.

Table 2 also supplies low-HDL percentages at explicitly sex-specific thresholds: below 1.03 mmol/L for men and below 1.29 mmol/L for women. These can constrain marginal distribution scenarios jointly with geometric means under declared assumptions, but they do not identify a distribution family, tails, residual variance conditional on covariates or the full joint distribution. Using these historical cutoffs as source-statistic definitions is different from endorsing them as clinical risk thresholds in Turkana; this paper itself questions the latter interpretation.

One unresolved Table 2 reporting anomaly is independently visible: Malawi urban women's HDL is given as a geometric mean of 1.15 with interval 1.15–1.26. Retain those printed values and flag the interval rather than guessing a corrected endpoint. The point estimate can remain contextual evidence; that interval is not suitable for a quantitatively weighted fit pending resolution. The root also identified denominator inconsistencies between Tables 1 and 2, including Uganda and EXTEND women. This review independently confirmed the Table 2 counts but did not reopen Table 1; preserve the root's issue record rather than harmonizing counts by assumption. Table 3's analysis-specific counts above should remain attached to its own rows.

## Admission status by use

These labels describe scientific admission in this note, not automatic assignments to the harness schema. In a strict harness check, an unsupported exact operator should remain `not_computable`; a separately approved proxy must carry assumptions.

| Item/use | Status | Reason and permitted interpretation |
|---|---|---|
| Source population, measurement definitions and non-HDL identity | **Admitted** | Primary text supports the named cohorts, exclusions, devices, sampling qualifications and algebraic definition. |
| Reported sex-specific regression estimates and their CIs | **Admitted as reported evidence** | Main text and DC2 Table 3 agree on the unadjusted values; Table 3 separates adjustments. The numbers may inform scientific interpretation without implying a verified executable operator. |
| Exact reproduction of Table 3 slopes | **Unavailable at present** | Raw/log mapping and other operator details remain insufficiently resolved; source population reconstruction is absent. |
| Raw-scale HDL regression scenario using the reported slopes | **Provisional** | Requires an explicit scale interpretation plus population and measurement-transfer assumptions. It is not a calibrated source replay. |
| Age-plus-smoking or alcohol-adjusted check on the current Turkana table | **Unavailable** | Necessary adjustment fields are not listed; dropping them changes the estimand. |
| Source-specific geometric mean and low-HDL proportion definitions | **Admitted** | Their operator types, units and thresholds are explicit. Exact source comparison still requires the relevant source population and selection. |
| Geometric means/proportions imposed on Turkana | **Provisional** | Requires declared eligibility, composition and measurement transfer; no claim of universal regional applicability. |
| Person-level or conditional residual SD obtained directly from a CI | **Unavailable** | The CI is estimation uncertainty; it does not supply the requested variance operator. |
| Malawi urban female HDL CI for precision weighting | **Unavailable pending clarification** | Printed interval remains anomalous and uncorrected by the published name correction. |
| Cardiovascular-event risk prediction or clinical thresholds | **Unavailable for this purpose** | This is cross-sectional lipid-association evidence, not target event-outcome validation. |

## Consequence for the Turkana candidate

This study supports retaining a protocol-relative measured TC/HDL case: it supplies relevant external relationships and distributional information while demonstrating that their interpretation depends on population context. It does not remove Turkana's health-selection, assay and unknown-fasting differences, and it does not make the candidate ready for generation by itself.

The immediate unresolved task is narrow: decide which source quantities can be used with verified definitions and which, if any, will become explicitly assumption-defined proxies. Retain unavailable checks honestly. Do not extend the variable set, introduce an unidentified latent disease mixture, invent residual SDs, or launch a generator merely to make every reported number usable. No additional originals, target results or experiments were opened by this review.
