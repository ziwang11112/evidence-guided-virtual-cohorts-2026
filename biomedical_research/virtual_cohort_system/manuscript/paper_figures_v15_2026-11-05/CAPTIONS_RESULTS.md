# Caption-ready notes for v15 results figures

These captions describe the rendered v15 panel order. They preserve the original experimental definitions and uncertainty types. Abbreviations: pp, percentage points; TC, total cholesterol; HDL, high-density lipoprotein cholesterol.

## Figure 2: native-unit evidence comparison

**Relational evidence changes the fidelity of generated analyses across six endpoints.** Panels show CHNS (a-c) and ENSANUT (d-f) HbA1c coefficients in native units. The adjustments are age and sex for CHNS BMI (a) and glucose (b); sex, BMI and glucose for CHNS age (c) and ENSANUT age (d); age and sex for ENSANUT BMI (e); and age, sex and glucose for ENSANUT BMI (f). The displayed increments are 1 kg/m² BMI, 1 mmol/L glucose and 1 year age for CHNS, and 10 years age or 5 kg/m² BMI for ENSANUT. E0 supplies basic/marginal evidence; E1 adds relational evidence. Each Agent arm contains five independently authored generators, ordered A01-A05 within the group; each statistical arm contains one prescribed generator. Dots show all three final seeds, open diamonds their means, and thin segments their within-generator min-max ranges. Matching author identifiers do not pair E0 and E1. Dashed lines are selected-sample reference estimates; gray bands retain the CHNS 95% community-cluster CR1-t intervals or ENSANUT empirical cluster-resampling stability bands. Reference bands and seed ranges have different meanings and do not define equivalence. All 24 constructions, 72 distinct final tables and 216 coefficient estimates are retained; references were previously exposed during development.

Optional quantitative sentence, unchanged from v12: E1 reduced the arm's mean absolute reference discrepancy by 82.0% for CHNS glucose, 33.3% for CHNS age, 61.4% for ENSANUT age, 58.3% for ENSANUT BMI and 47.4% for glucose-adjusted ENSANUT BMI; CHNS BMI discrepancy increased by 54.8%. These descriptive contrasts average across three seeds within each author and then across five authors; they are not a pooled score or a claim that every E1 construction improved.

## Figure 3: two scientific requests

**Generated analyses across HbA1c and lipid requests.** The left column shows ENSANUT HbA1c coefficients: age per 10 years, adjusted for sex, BMI and glucose (a); BMI per 5 kg/m², adjusted for age and sex (c); and BMI per 5 kg/m², additionally adjusted for glucose (e). The right column shows Turkana lipid analyses: HDL (b) and total cholesterol (d) coefficients per 5 kg/m² BMI, both adjusted for age and sex; and TC-HDL residual Pearson correlation after adjusting for age, sex and BMI (f). All three constructors per request and three final seeds per constructor are shown, giving six constructors, 18 distinct final tables and 54 primary estimates. Circles show individual seed estimates, open diamonds their means, and thin segments their within-constructor min-max ranges. Dark diamonds and dashed lines mark the exposed sample reference. Gray bands show empirical cluster-resampling stability for the three HbA1c coefficients and HC3 assumption-conditional sensitivity for the two lipid coefficients. The TC interval crosses zero; no reference interval is available for residual correlation. These bands are not acceptance margins. Seed ranges describe sampling variation under fixed constructions, not uncertainty about model structure or clinical replication.

Panel map for LaTeX/cross-reference checks: (a) `Q1_age10`; (b) `K02-HDL-BMI`; (c) `Q2_bmi5`; (d) `K02-TC-BMI`; (e) `Q3_bmi5`; (f) `K02-LIPID-RESIDUAL`.

## Figure 4: supplied-summary reconstruction

**Joint reconstruction of supplied scientific summaries.** Panels show CHNS HbA1c coefficients for BMI adjusted for age and sex (a), glucose adjusted for age and sex (b), and age adjusted for sex, BMI and glucose (c), followed by glucose-HbA1c Pearson (d) and Spearman (e) correlations. Purple L01-L03 constructions use external literature; blue R01-R03 constructions additionally receive 30 target summaries and metadata. Each constructor's three final seed estimates is shown, with open diamonds for means and thin min-max segments. These are independently authored generators, not paired versions. Dashed lines are reference summaries, explicitly available as inputs to R. Gray bands show the available 95% community-cluster CR1-t intervals for regression references; no correlation interval is supplied. All six constructors, 18 distinct final tables, 30 constructor means and 90 seed statistics are retained. Initial and final outputs were identical and are displayed once. Closer R agreement tests reconstruction of supplied information, not prediction of hidden reference summaries.

## Figure S3: marginal and conditional dispersion

**Dispersion of final generated tables.** The four panels show ENSANUT HbA1c population-form marginal SD (a), HbA1c full-model residual RMS (b), Turkana TC sample SD (c), and Turkana HDL sample SD (d), all in their native units. All six constructors and three final seeds per constructor are retained, yielding 36 diagnostic values from the same 18 final tables. Circles show seeds, open diamonds their means, and thin segments their min-max ranges; dark diamonds and dashed lines mark exposed sample references. Gray bands for HbA1c represent empirical cluster-resampling stability; lipid SD reference intervals are unavailable. Agreement on a scientific coefficient does not imply agreement on marginal or conditional spread. Seed ranges do not quantify uncertainty about structural choices.

## Unchanged numerical coverage

| Figure | Endpoints | Constructor means | Seed statistics | Final tables |
|---|---:|---:|---:|---:|
| 2 | 6 | 72 | 216 | 72 |
| 3 | 6 | 18 | 54 | 18 |
| 4 | 5 | 30 | 90 | 18 |
| S3 | 4 | 12 | 36 | 18 |

The cross-task primary and dispersion displays reuse the same 18 tables. Counts are not additive across figures. No patient tables were read, no experiment was run, and no scientific model was fitted for this presentation revision.
