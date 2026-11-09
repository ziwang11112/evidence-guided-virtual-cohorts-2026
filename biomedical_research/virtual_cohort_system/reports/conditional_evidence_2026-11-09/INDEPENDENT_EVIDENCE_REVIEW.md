# Independent evidence review

2026-11-09. Scope: original Soares 2019/2020 articles and Soares 2020 supplement, and original Liu 2023 article and Supplementary Figure 1. The review was conducted independently of the discovery agents' extraction by inspecting the original XML, PDF page renders and embedded supplementary image/caption. No target, old result, candidate, generated cohort, coefficient tuning, generator or dataset run was accessed. The reviewer issued zero web discovery/retrieval requests; original artifacts were supplied by the source agents. The broad filename lookup used before the allowed source location was clarified exposed filenames only, not old-file contents.

## Decision

**Partial scientific admission is supported. No exactly matching raw-unit pooled age/sex BMI coefficient, and no exactly matching age/sex/BMI TC-HDL residual correlation, was verified in these sources.** Useful continuous conditional-association evidence nevertheless exists. Admit the separately labelled source operators below; keep implementation readiness and transfer separate from source authenticity. A source-supported replay specification may now be written. This review authorizes no cohort generation and does not validate a target population.

## Soares 2020: verified continuous BMI-lipid associations

Primary source: [Soares et al., 2020](https://doi.org/10.1186/s12916-020-01648-0), original main XML and Additional file 1. Independently inspected Supplementary Table S7 pages 12-13 and Figure S4 page 21 visually, and main Methods/Statistical analysis/Missing data text. Table S7 reports lipid differences in **mmol/L per one source BMI SD**, with 95% confidence intervals:

| Malawi source stratum | TC | HDL-C |
|---|---:|---:|
| Women age 40-60, n=1,487 | 0.15 [0.10, 0.20] | -0.05 [-0.06, -0.03] |
| Men age 43-70, n=790 | 0.20 [0.13, 0.27] | -0.05 [-0.08, -0.03] |

These are urban Lilongwe participants from the MEIRU study, selected for complete anthropometry and fasting lipids and the stated age ranges. Blood was collected after at least eight hours of fasting and assayed enzymatically with a Beckman Coulter AU480. The point estimands are sex-specific continuous linear-regression associations, adjusted for age, ethnicity, education, household assets score, marital status, parity for women, lipid-lowering medication, smoking, alcohol, physical activity, and HIV status. The source uses household-cluster robust standard errors and chained-equation imputation of missing covariates; HIV status was missing for 9.2% of Malawi adults. It is therefore inaccurate to describe these as age/sex-only pooled regressions or complete-case analyses of all covariates.

**Admission:** `different-source-operator`, with the printed units and full adjustment retained. A model can compare its within-source-stratum coefficient of standardized BMI with these estimates. The source-law standardization reference and BMI SD must be declared and supported or varied; these values cannot be inserted as mmol/L per kg/m2. The publication's imputation-pooled estimates can inform a complete source-law projection under declared missingness/estimation assumptions. Exact replay of the original imputation procedure is not established.

**Limitations:** Figure S4 is age-adjusted and stratified by age/sex, but both outcome and BMI use SD units and the estimates appear only as plotted markers/intervals. It is not a printed raw-unit coefficient table. No numeric plot extraction was performed here. Table S9 differs in adjustment and contains substantially different HDL numbers despite a similar raw-unit heading. That discrepancy is not silently resolved by guessing a transform or choosing one magnitude. Admission of S7 is as its independently verified printed operator; alternative-table/scale sensitivity remains unresolved. Neither S7 nor S4 supplies TC-HDL residual covariance or conditional outcome SDs.

## Soares 2019: verified broader adult strata, overlapping evidence

Primary source: [Soares et al., 2019](https://doi.org/10.1136/bmjgh-2019-001542), original XML Table 3, Methods and selection/missingness text. The table confirms mmol/L per one BMI SD under extended covariate adjustment:

| Source stratum | BMI-model n | TC, 95% CI | HDL-C, 95% CI |
|---|---:|---:|---:|
| Rural women | 4,971 | 0.23 [0.19, 0.26] | -0.03 [-0.04, -0.02] |
| Rural men | 3,548 | 0.20 [0.16, 0.23] | -0.03 [-0.04, -0.02] |
| Urban women | 7,455 | 0.13 [0.11, 0.15] | -0.05 [-0.05, -0.04] |
| Urban men | 3,705 | 0.15 [0.12, 0.18] | -0.04 [-0.05, -0.04] |

The source includes eligible resident adults aged at least 18, excludes missing lipids/nonfasting measurements, and reports additional covariate missingness. It adjusts age, ethnicity, education, household assets, marital status, parity for women, lipid-lowering medication, smoking, alcohol, physical activity, and HIV/ART status, with household-robust inference. Assay and fasting methods are consistent with the same MEIRU study family.

**Admission:** `different-source-operator`. These are useful conditional continuous associations, with source sex/location strata, scaling, selection and all adjustment retained. They are not independent replication of Soares 2020: the latter is an age-restricted urban comparison from the same cohort family. Do not multiply precision as if the samples were independent. Table 3 regression n differs from the full fasting-lipid sample, so SDs from broader descriptive samples cannot silently supply an exact unit conversion. No exact requested-use coefficient or joint residual relation follows from this table alone.

## Liu 2023: verified joint partial correlations with extra batch adjustment

Primary source: [Liu et al., 2023](https://doi.org/10.1111/acel.13934), original XML and `ACEL-22-e13934-s001.docx` Supplementary Figure 1. The original embedded matrix visibly reports:

```
r(TC, HDL | source age, sex, batch) = 0.16
r(TC, BMI | source age, sex, batch) = 0.05
r(HDL, BMI | source age, sex, batch) = -0.35
```

The original Results and figure caption include batch adjustment; Methods 4.8 describes age/sex adjustment without batch. The review retains the more specific caption and records the discrepancy. The article explicitly describes Pearson correlations and z-transformation; affine z-transformation preserves Pearson partial correlations. Conventional clinical TC/HDL were measured in mg/dL by the local clinical chemistry laboratory, distinct from the article's lipidomic mass-spectrometry measurements. Overnight-fasted blood was obtained in the Rhineland Study, a Bonn population cohort recruiting residents aged at least 30. The relevant analytic subset and exact shared matrix n need confirmation; the article says complete data without imputation but this does not by itself prove all displayed pairs used identical records.

**Admission:** the three rounded reported correlations are a `different-source-operator` under the published age/sex/batch label, with the adjustment discrepancy retained. This is authentic joint evidence. Source scientific admission is broader than current implementation readiness: batch design/encoding and common-row processing are unresolved, so an executable replay must declare these source assumptions or clarify them. A model is free to represent the source nuisance adjustment in different scientifically defensible ways; it cannot silently omit it and call the result exact age/sex evidence.

Conditional on the three entries using the same records and the same linear age/sex/batch residualization, the recursive partial-correlation identity gives:

```
r(TC,HDL | age,sex,batch,BMI)
 = (0.16 - 0.05*(-0.35))/sqrt((1-0.05^2)*(1-(-0.35)^2))
 = 0.1897222833
```

The 3x3 rounded correlation submatrix is positive definite (determinant 0.8438). If each printed entry was rounded to nearest 0.01, its rounding-only propagated range is approximately [0.181864, 0.197680]. This is **not** a confidence interval: it excludes sampling uncertainty, selection, the adjustment ambiguity and transfer uncertainty. No uncertainty was derived from a guessed matrix n. The extra batch adjustment cannot be removed without further compatible covariance information or an explicit additional model assumption. The result is therefore a conditional algebraic illustration for a different operator, not the requested exact age/sex/BMI residual correlation.

## Follow-on conditions and remaining gaps

A bounded replay specification can use the authentic Soares continuous projections and/or the Liu joint matrix as labelled source constraints. For per-SD projections, compute standardization from the declared source-law distribution, with its SD supported or varied. For Liu, retain batch and explicitly state the shared-record/common-residual-basis assumption before applying the recursion. Keep reported CIs distinct from rounding intervals, and track MEIRU overlap. If a source procedure cannot be represented, mark that replay unready instead of filling missing variables, weights, or selection with target rows.

No evidence here identifies conditional residual SDs for both requested outcome models. The Soares associations and Liu covariance evidence concern different populations, adjustments, and selection; combining them into one covariance matrix requires an explicit transfer/model layer. Different compatible models may reproduce all admitted operators while giving different requested-use results. Do not force that remaining uncertainty into a single coefficient, residual SD, or correlation. Assessment is of source consistency, not clinical validity.

Greiner remains outside this independent numerical review; root review reports unresolved original regression-scale ambiguity. No Greiner numerical constraint is admitted here. Other discovery candidates are the responsibility of their source inventories; this review does not imply independent validation of uninspected sources.

## Local original artifacts and integrity

All paths below are relative to this review directory. Originals remain local and must not be published wholesale.

| Original artifact | SHA-256 |
|---|---|
| `source_bodies_associations/Soares2020.xml` | `60ad9f8e4716e4663c59082cb2dcfb2cce36d3ceaa0793c7ed6398f999ceed81` |
| `source_bodies_associations/Soares2020_supp.pdf` | `b8878f6b5b21b2a4b1d18746c1ff0e4f3f4e212aaf10646740cc4b5ae3359963` |
| `source_bodies_associations/Soares2019.xml` | `0ae152fdf556f868af152f3b1afb49602b357d71325c41dae493b382ec38b08f` |
| `sources_local_joint/lipidomic_aging.xml` | `4d5b8bf5c470ed1e1cdc8774869a80d5aef5c28a0123338465c142b4c4badc74` |
| `sources_local_joint/ACEL-22-e13934-s001.docx` | `bf7954c7e140237268db2c77302a5c3c6d8f711b2186a45946e1103a3009451e` |
