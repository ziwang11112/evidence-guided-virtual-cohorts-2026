# Joint conditional-evidence audit — 9 November 2026

**No exact adult TC–HDL Pearson residual correlation adjusted only for age, sex, and BMI was verified.** The best adult source supports a separately labelled correlation that additionally adjusts for laboratory batch, subject to common-record and design assumptions. This is useful exploratory source evidence, not an admitted African-population or latent-concentration constraint.

This branch read the permitted source packets and `registry.json`, then made eight discovery queries in four web calls: African joint/partial evidence first, followed by wider-population targeted retrieval. Full query strings, access failures, endpoint URLs and original-file hashes are in `SEARCH_JOINT.json`. No patient records, excluded target studies, generated candidates or old target statistics were acquired. No generator was edited or executed.

## Strongest adult source and exact interpretation

[Liu et al., 2023, Aging Cell](https://doi.org/10.1111/acel.13934), *The lipidomic correlates of epigenetic aging across the adult lifespan: A population-based study*, reports a supplementary Pearson partial-correlation matrix. Original XML: `sources_local_joint/lipidomic_aging.xml`; supplement: `sources_local_joint/ACEL-22-e13934-s001.docx`; extracted Figure S1: `sources_local_joint/image1.png`.

The figure includes **clinical total cholesterol and clinical HDL**, separately from lipidomic classes such as cholesteryl esters and phosphatidylcholines. Methods 5.5 places these clinical measures in a local University Hospital Bonn laboratory, in mg/dL. BMI is kg/m². Venous blood was obtained after overnight fasting; the clinical assay platform and specimen details are incompletely specified. The source measures are assay outputs; they do not identify error-free latent concentrations.

The cohort comprises 4,181 Rhineland Study participants aged 30–95 in Bonn, Germany, selected from the first participants with complex-lipid and methylation data. Recruitment was residential, with sufficient German for consent required. Complete data without imputation are stated for the analyses, and each variable has less than 5% missingness, but the exact matrix sample and pairwise denominators are unreported. These selection, age and measurement conditions do not establish transport to African adults.

**Adjustment discrepancy:** Methods 5.6 describes age/sex adjustment, whereas Results 2.2 and the Figure S1 caption explicitly include batch. The conservative extraction preserves batch. Its encoding, number of columns and complete-case construction are unresolved. Z-standardization is reported; this positive affine transformation preserves Pearson correlation. No log transformation is reported for this matrix.

The independently verified rounded entries are:

| Clinical pair | Partial Pearson r, given age, sex and batch |
|---|---:|
| Total cholesterol–HDL | 0.16 |
| Total cholesterol–BMI | 0.05 |
| HDL–BMI | −0.35 |

These are three dependent summaries of one cohort, not three independent studies. No confidence interval or figure-specific n is reported.

## Algebraic candidate, with extra batch adjustment retained

Let A contain intercept, age, sex and the source batch design, and B be BMI. On the **same records**, with the **same linear projection/weights**, the recursive partial-correlation identity is

`r(T,H | A,B) = [r(T,H | A) − r(T,B | A) r(H,B | A)] / sqrt[(1 − r(T,B | A)^2)(1 − r(H,B | A)^2)]`.

Using the displayed entries gives **0.1897222833**, labelled *TC–HDL Pearson residual correlation after adjustment for age, sex, BMI and batch in the Rhineland source population*. The calculation is dimensionless and invariant to positive linear unit conversions. It is not the requested age/sex/BMI-only correlation. Removing batch requires additional joint information and cannot be accomplished by ignoring the word “batch.”

If each displayed coefficient was rounded to the nearest 0.01, its ±0.005 rounding box gives a conservative envelope of **0.1818638727–0.1976803835**. The extrema follow the derivative signs over that box: increasing TC–HDL or TC–BMI increases the result, and increasing HDL–BMI decreases it. This is **rounding sensitivity, not a sampling confidence interval**. No Fisher interval is calculated because exact n and adjustment rank are unknown.

Required replay assumptions remain: common participant set across all three correlations; common age/sex/batch design including an intercept; compatible weights; raw or affine-transformed clinical lipids and BMI; positive residual variances; and the ordinary Pearson interpretation. Source complete-data wording supports but does not prove common rows for every matrix entry. The independent reviewer verified the original text, caption and all three values and agrees that this is a different source operator with unresolved replay details.

The matrix can be preserved as exploratory published evidence. The recursively computed value is conditional on the stated assumptions. It does not identify a complete conditional covariance matrix, residual variances, a joint individual-data law or the requested population relation. No generation follows from this branch.

## Other audited sources and gaps

| Primary source | Actual usable information | Why it does not identify the requested joint relation |
|---|---|---|
| [Obirikorang et al., Ghana 2015](https://doi.org/10.1371/journal.pone.0129494), existing approved extraction, Table 7 | Urban/rural unadjusted **Spearman** TC–HDL values; fasting serum mmol/L | Rank correlation is not Pearson correlation. Covariate conditioning and pair-specific n are absent. |
| [Kodaman et al., Ghana 2016](https://doi.org/10.1161/JAHA.116.003867), Methods and Tables 2–5 | Adult Sunyani/nearby villages; log-transformed variables; residual Pearson matrices and CIs; age/sex/residence and higher-order adjustments | TC was measured but excluded from the published matrices. HDL–TG or BMI–HDL coefficients do not supply TC–HDL covariance. Pairwise sample sizes differ. |
| [Michael et al., Nigeria 2019](https://doi.org/10.4314/mmj.v31i3.5), Tables 1 and 5 | 414 hypertensive adults aged 30–100; fasting lipids mmol/L; Pearson correlations of lipids with age and body-size measures | TC–HDL, age–BMI and other necessary joint predictor moments are missing. Sex-stratified means/SDs cannot supply them. Disease selection limits transport. |
| [Healthy Lebanese volunteers, 2022](https://doi.org/10.3390/metabo12080690), Table 3 and statistical methods | n=303, ages 18–65; age/BMI/HDL/non-HDL matrix; fasting mmol/L | The matrix is **Spearman**, with rank-based CIs. The identity TC=HDL+non-HDL cannot turn rank correlations into raw Pearson covariance. |
| [McKenna et al., 2025](https://doi.org/10.1136/bmjopen-2024-097140), Figure 1B and Methods | Age/gender/BMI partial TC–HDL value approximately 0.18 in indexed figure | Mixed adolescent/young-adult psychiatric-service cohort, n=751 overall, substantial missingness and pairwise deletion; no adult-only coefficient. Maintext does not explicitly name Pearson. Age-band and missingness inconsistencies are preserved; the exact numerical value was not independently extracted from the source figure. |
| [Tang et al., NHANES 2025](https://doi.org/10.1038/s41598-025-10184-x), Figure 6 | Pearson heatmap includes age, gender, BMI, TC and HDL in 759 US adults with both CHD and T2DM | Complete numeric entries were not recovered; exact correlation weighting/denominator unresolved. Table 1 uses TC mg/dL and HDL mmol/L, which by itself is harmless for Pearson r but does not fix missing matrix values. Disease-selected sample has major transport limits. |
| [CHARLS glycolipid-network study, 2026](https://doi.org/10.1186/s12944-026-02894-6), Methods | Partial Pearson networks among six glycolipid biomarkers in a restricted reference group | Conditions on other biomarkers rather than age/sex/BMI, with selection by lipid/glucose thresholds. Perturbation-network features are different estimands. This is CHARLS, not the excluded CHNS; no records were accessed. |

The inventory JSON records measurement context, uncertainty, selection and cohort overlap for each source. All table subsets and associations from the same paper are dependent evidence. Distinct geographic sampling frames do not constitute a participant-level non-overlap audit.

## Search-only leads and access limitations

A 2012 Cardiovascular Journal of Africa issue exposed a Pearson matrix from menopausal women with TC/HDL/BMI but no age row. The full 33.9 MB issue was rejected by the browser's size limit and not saved; no numerical constraint was extracted. A statistical thesis displayed a complete matrix from a common diabetes teaching dataset, but it was not accepted as an original biomedical sampling/measurement report. Several other hits correlated lipids with a third biomarker or used mixed/rank methods; none furnished the missing compatible matrix. These are search screens, not full-source exclusions.

Publisher BMJ URLs returned 403; PMC web access sometimes returned a challenge. Named papers were retrieved from the Europe PMC full-text service. The Liu supplement came from its public supplementary-files endpoint. The direct PMC DOCX URL returned an HTML challenge and was discarded. No paid service was used.

**Resource account:** 4,048,729 bytes of newly saved original XML, metadata and supplement ZIP (about 3.86 MiB); 21,568 bytes in one discarded direct HTML response. Extracted DOCX/images duplicate ZIP content and are not counted as new transport. Search/browser response bytes are not exposed and are reported separately as unmetered. Source bodies and published tables remain local; only original summaries, metadata and aggregate calculations are eligible for later reviewed synchronization.

The bounded search closes with a negative exact-use finding and one explicitly different exploratory adult source candidate. Additional assumptions or target-specific tuning are not used to convert it into an exact constraint.
