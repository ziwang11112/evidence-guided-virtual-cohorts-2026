# Final model decision: ordinary_1

The conditional lognormal generator retains the initial Taiwan Biobank sex-by-BMI mean anchors, age-centering construction and source-derived variability proxy. The numerical revision replaces its longitudinal percentage tail with a cross-sectional additive obesity slope. No target outcome or generated target cohort was inspected to select this change.

## Review F1: directly relevant cross-sectional tail evidence

Two additional gateway searches identified L2020 (PMC7644056), a study of 1,214 Italian overweight/obesity clinic patients. Its main Table 2 gives an HDL-on-BMI coefficient of -0.42 mg/dL per BMI unit (95% CI -0.53 to -0.32), adjusted for age and sex. More specifically, the published author response embedded in the approved JATS contains Table rev2 for patients with BMI>30: coefficient -0.33 (95% CI -0.47 to -0.20), with the same adjustment. This is a separate subgroup analysis in the publication correspondence, not a main-text coefficient, a downloaded DOCX table, or an independent second cohort. All numbers were read from the gateway-approved complete article text/XML; no external supplement or individual data was accessed.

The final model uses -0.33 as the right derivative of the conditional arithmetic HDL mean at BMI30.5, common to men and women. Let m0 be the sex- and age-specific mean at that anchor. Beyond it, m=m0*exp(-0.33*(BMI-30.5)/m0). This retains a positive mean and preserves the source slope locally. It does NOT reproduce a fitted source linear model across the entire range: exponential curvature is assumed. The initial sex-specific longitudinal percentage slopes remain only a comparator, not final parameters. This removes the change-from-within-person-to-between-person bridge while leaving transport and curve-shape bridges unresolved.

L2020 is selected and not target matched. It excludes medications, diabetes and several diseases, is from Italy, and includes ages as young as14. Table1 reports BMI25-64.60; target predictor support extends beyond that. Several Table1/prose age, sex-count and BMI-range entries differ slightly. No numerical correction is invented; no model parameter uses those discrepant summaries. The subgroup n is unavailable. Its slope confidence interval is sampling uncertainty within the source, not a bound on target transport. Flat-tail, original longitudinal-tail, source-CI slope and linear-tail alternatives are evaluated on invented inputs only.

## Review F2: retained anchor and age assumptions

The original G2019 (PMC6627528) Table2 sex-by-BMI means are category averages, not exact-BMI conditional means. Knots17,21.25,25.5,30.5 are assumed representatives; only the two closed-bin knots are midpoints of published boundaries. The source has no registered supplements (gateway list-supplements returned an empty list), and no retrieved evidence identifies within-bin BMI distributions or joint sex-by-age-by-BMI cells. Its Table3 age effects also adjust for lifestyle, WHR and body fat, unlike the generated model.

The current means and modest common age pattern are retained because no available replacement identifies the missing joint information more directly. Final checks vary representative BMI values and remove age effects; these reveal sensitivity, not identify a preferred alternative. The source-age centering identity is an algebraic identity at assumed representatives only. It does not demonstrate reproduction of actual source within-bin distributions. No conditional age/sex interaction is inferred from pooled margins, and a printed overlap in source age-bin boundaries remains disclosed.

## Review F3: variability and measurement

G2019 SEM*sqrt(n) correctly recovers approximate individual SD under the usual independent-mean formula. The resulting SD remains a broad-cell marginal SD, not a residual SD conditional on exact BMI, age and sex. The final model retains it as an explicit variability proxy; lognormal shape, source-derived CV with age and the extreme BMI tail, and independent participant residuals remain assumptions. Repeated random draws quantify Monte Carlo variation under the fixed scenario, not source or transport uncertainty.

L2020's overall HDL48.35+/-12.47 mg/dL is a mixed-sex, mixed-predictor mean and SD. It is not substituted for conditional spread. That study used overnight-fasting plasma lipids measured by automated colorimetry (Hitachi/Boehringer Mannheim); this does not establish calibration to the target direct-serum Roche method. G2019's exact HDL assay remains unspecified in its retrieved maintext. Final checks include SD multipliers0.75/1.25 and a matched-mean/matched-variance gamma alternative. These are deliberately illustrative model choices with no evidence-based uncertainty coverage.

## Preserved evidence cautions and scientific scope

H2019 (PMC6566419) overlaps G2019's parent cohort and contains inconsistent SEM and BMI count labels; it is qualitative context only. K2017 (PMC5627541) concerns HDL function as well as concentration; CEC coefficients, heritability and repeat correlations are not used as HDL residual variance. D2019 remains abstract-only longitudinal context. Neither the added Italian source nor the original sources establish US target calibration or individual HDL recovery.

The virtual column can support transparent scenario analyses conditional on BMI, age and sex. Relations not directly estimated by the evidence arise from chosen model structure. It cannot establish clinical risk, causal weight-change/aging effects, associations with unobserved covariates, or increased clinical information from larger synthetic sample size. Supported implementation claims and unresolved scientific gaps are distinct.

## Retrieval, tests and preservation

Revision used two queries and two download attempts: a potentially useful ARIC fulltext was rejected by the gateway and was not bypassed; L2020 was accepted. The G2019 supplement listing was empty. Total use is8/12 queries and7/12 downloads, leaving4 queries and5 downloads unused. Retrieval stops because the new source directly reduces F1's estimand gap, while no supplied joint summaries or residual measures warrant further numerical changes. No attempt was made to retrieve original/source individual datasets.

All initial files are preserved. final/artificial_checks.json records actual source-arithmetic, provenance, invented-input distribution, interface and sensitivity checks, reproducible with run_final_checks.py. These are implementation/source checks only. No target accuracy or improvement claim is made. final/revision.json records the substantive change and unresolved limitations.
