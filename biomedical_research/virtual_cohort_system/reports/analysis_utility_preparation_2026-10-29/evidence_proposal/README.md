# Source-only packets awaiting independent admission

Prepared 2026-10-29 for fasting insulin from age/sex/BMI/fasting glucose and HbA1c from age/sex/BMI. NHANES and Brazil PNS were excluded from **both** packets. No target rows, target results, custodian artifacts, candidate outputs or generator execution were used. These files do not grant evidence approval.

The extraction uses the source/item fields in `cohort_harness/contracts.py`. The two JSON files are evidence proposals rather than submitted, approved candidate bundles. Artifact paths are relative to this evidence directory. `candidate_packet.json` records limitations, screening and retrieval provenance. `build_source_packets.py` only serializes manually checked literature statistics; it is not a scientific generator.

## Insulin packet

`fasting_insulin_evidence.json` has three primary evidence contexts and one optional reference anchor:

- Framingham: selected healthy community participants, with both cross-sectional and longitudinal standardized log-insulin associations. The cross-sectional age and male-sex estimates are weak; they must not be substituted by the stronger longitudinal estimates. Waist is the adiposity predictor, not BMI. Exact assay details and raw log-scale SDs are not available in the main article.
- Guishan, Taiwan: n=321 older adults without diabetes, insulin mean 7.10 and SD 4.14 microU/mL, raw insulin–glucose Pearson r=0.38, and joint descriptions grouped by insulin tertiles. The insulin-tertile BMI summaries are not a regression of insulin on BMI.
- MACAD: n=470 Mexican-American adults from CAD-enriched families. Insulin medians/IQR widths are 11.3/8.1 for men and 12.0/7.4 for women, microIU/mL. Univariate R for log-insulin/log-BMI is 0.56 overall, 0.60 in men and 0.54 in women. The full GEE includes insulin sensitivity, clearance and waist, absent from the task.
- DASA Rio de Janeiro: independent Brazilian laboratory records, **not PNS**. Optional selected-healthy reference values; central 95% insulin limits 2.52–13.14 microU/mL. These apply after BMI, glycemia, medication and outlier selection, not to an unrestricted adult population.

No source identifies a complete conditional distribution of insulin given exactly age, sex, BMI and fasting glucose. Missing pieces include predictor covariance, intercept/log-scale normalization, residual distribution and diabetes/treatment effects. Do not invent a waist-from-BMI map, treat unknown relationships as independent, replace raw insulin with log-insulin, or use IQR width as SD. No insulin unit conversions were performed.

## HbA1c packet

`hba1c_evidence.json` separates three contexts:

- SHIP-0 and SHIP-Trend are independent population cohorts from the same German region. Whole-population sex-specific medians/quartiles and BMI-adjusted age slopes are distinct from the combined selected-healthy age/sex reference limits. The whole samples include known diabetes; the healthy reference group excludes diabetes, obesity and other conditions. The Table 3 values disagree with the abstract/results text for some upper reference limits. The packet preserves Table 3 values and flags the conflict; independent review must decide whether to admit them. Linear age coefficients are included only for whole-sample strata without a spline term.
- Hoorn 1989 and Hoorn 2006 provide separate cross-sectional samples without **known** diabetes, including screen-detected diabetes. HbA1c is 5.4% with SD 0.7% and 0.4% respectively. Adjusted BMI coefficients are negative after accounting for glucose, waist/hip and lifestyle. These conditional effects must not be used as coefficients for an age/sex/BMI-only model. The different sign and conditioning are retained.
- DIRECT-DETECT is optional prospective structure evidence: complete published sex-specific equations predict HbA1c about six years later and need waist, medication, smoking and parental diabetes history. They are not a direct model for contemporaneous HbA1c with the task's three covariates. Hoorn participants overlap the 2020 Hoorn source. Its other cohorts (KORA, Inter99, METSIM) add population contexts; they do not make the pooled equation four independent replications.

The HbA1c packet does not identify a general-population diabetic/nondiabetic mixture conditional on age/sex/BMI. Known diabetes, treatment, anemia, renal function and related factors are absent. The relatively low explained variance of non-glycemic source models reinforces the need for residual variability; neither a complete residual law nor age/sex/BMI-only variance is reported. No source HbA1c unit conversions were performed.

## Provenance and local retention

Seven primary full texts were retrieved and verified as saved XML or HTML, with SHA-256 recorded. Numeric values were read from these saved full texts, not accepted from search snippets. Thirteen search queries were used; the bounded search then stopped. Unretrieved or excluded leads are retained in `source_screen.csv`. Formal harness validation and independent source admission were not performed by this extraction agent.

Full texts and their generated text extracts are under `sources/`, excluded by this directory's `.gitignore`. Keep those local; do not publish whole papers to GitHub. The manifest hashes identify the exact retrieved bytes, not study validity. Some primary articles discuss NHANES in their literature reviews; only their own non-excluded cohort results were extracted.
