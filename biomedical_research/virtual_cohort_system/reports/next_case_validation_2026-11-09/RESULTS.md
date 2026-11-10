# PNS blood-pressure joint-generation validation

New prespecified analysis task in an exposed PNS release; no new-cohort or national-population claim.

Reference eligible N=8352; final tables=15; all attempted stage/seed tables=15.

## Real reference (not known population truth)

| Analysis | Weighted point | Conditional row-resampling interval | Unweighted sensitivity |
|---|---:|---:|---:|
| bmi_sbp | 3.524 | [2.961, 4.119] | 3.435 |
| bmi_dbp | 2.260 | [1.931, 2.585] | 2.114 |
| residual_correlation | 0.717 | [0.700, 0.734] | 0.741 |

The intervals resample rows while retaining their supplied weights; they are not survey-design confidence intervals. BMI slopes are mmHg per5kg/m² adjusted for age and recorded sex; residual correlation is dimensionless.

## All authors and selected draws

| Author | Native disposition | Selected stage | Tables | BMI–SBP median [range] | BMI–DBP median [range] | Residual correlation median [range] |
|---|---|---|---:|---|---|---|
| A01 | completed | candidates/initial | 3 | 3.391 [3.325, 4.133] | 2.997 [2.948, 3.011] | 0.508 [0.479, 0.511] |
| A02 | completed | candidates/initial | 3 | 3.815 [3.612, 4.033] | 3.350 [2.912, 3.691] | 0.644 [0.632, 0.646] |
| A03 | completed | candidates/initial | 3 | 3.980 [3.591, 4.086] | 2.933 [2.886, 2.965] | 0.506 [0.466, 0.509] |
| A04 | completed | candidates/initial | 3 | 3.880 [3.816, 4.276] | 3.053 [3.029, 3.330] | 0.557 [0.524, 0.567] |
| A05 | completed | candidates/initial | 3 | 3.709 [3.081, 3.775] | 3.058 [3.029, 3.232] | 0.526 [0.495, 0.538] |

Three draws share one authored law; five authors share one real reference. Neither rows, seeds nor authors count as independent clinical cohorts.

## Interpretation boundary

Compare effect magnitude and joint dependence together with dispersion, not sign alone or exact numerical matching. All failures, singular outputs and unselected stages remain in the sealed records. The experiment does not define an arbitrary pass threshold or establish superiority/equivalence. A source-feedback revision, if selected, is not automatically a proven improvement against independent clinical data.

Known unresolved assumptions include target demographics and BMI dependence, omitted source adjustment covariates, age/measurement/selection transport, and raw versus conditional dependence. No post-reveal regeneration is permitted.

Figures: `figures/pns_bp_analysis_utility.pdf` and `figures/pns_bp_dispersion.pdf`. Full numerical output: `RESULTS.json`; independent recomputation is reported separately.
