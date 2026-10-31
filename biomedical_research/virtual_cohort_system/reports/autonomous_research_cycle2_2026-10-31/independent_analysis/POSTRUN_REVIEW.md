# Independent postrun verification and interpretation review

2026-10-31. The unchanged, prewritten independent checker was executed exactly once after root authorization. Authorization SHA-256: `1e22974f9772c37e62dd162b649ae1db9017c819fb388488390f88f6d6d5fd89`. Checker SHA-256: `bf197b898e56d41fa6a83604e2456d30667ebad0a102a234a0a2e480e550b418`. Measured command runtime: **12.405 seconds**. No source/raw tables, failed execution outputs, or execution logs were opened; no regeneration, estimator change, production modification, or retry occurred. The target is revealed and closed to tuning.

**Arithmetic result: match, zero discrepancies.** The reference and all six distinct successful generated outputs were independently recomputed, with every one of the 12 scheduled stage labels preserved. Both final constructions retained their same-seed initial outputs. There were zero failed analytical slots. All 31 fixed estimands and the JSON/CSV results agreed, including exact rational-mass point quantiles. The comparison CSV contains 403 endpoint rows (31 reference plus 12 times 31 generated labels), including 195 exact point-quantile comparisons; retained labels are duplicates of evidence, not additional generated cohorts.

The independent cluster resampling reproduced 399 attempted and 399 valid replicates at seed 18301, with zero empty-cell or singular-design failures. All 31 stability bands and the valid/failure attempt accounting matched. The reference contained 6,931 eligible participants in 317 represented lab strata and 2,450 eligible PSUs, including 36 singleton strata. These are counts of the finite analytical reference and its resampling frame.

The largest absolute point-estimate difference was `5.684341886080802e-14` for construction 2, seed 18223, glucose mean. The largest stability-bound difference was the same magnitude for the lower glucose-mean endpoint. Both are within the predeclared numerical comparison rule. Exact point-quantile mismatch count was zero. Replicate estimates were computed internally but not exported; production does not publish them for direct replicate-by-replicate numerical comparison.

Aggregate labeling is consistent with the protocol: the reference is called a finite empirical age/sex-standardized analytical population; bands are explicitly empirical cluster-resampling stability bands without confidence-coverage or national-design inference claims; and Q2 minus Q3 is labeled descriptive and noncausal. The schedule retains all stage and seed identities and distinguishes 12 labels from six unique outputs. The 50% female mean is imposed by the standard; it cannot count as evidence that a generator learned the target distribution. The female median of 0 follows the prespecified inverse-CDF boundary convention.

The following table summarizes the five coefficient quantities. All values are HbA1c percentage points. Q1 is per 10 years of age; Q2, Q3, and their difference are per 5 kg/m2 BMI; the secondary glucose projection is per 10 mg/dL glucose. Construction ranges are the three scheduled seeds, with retained finals identical to their initial outputs. They are Monte Carlo seed ranges, not uncertainty intervals.

| Quantity | Finite-reference estimate | Empirical reference stability band | Construction 1 seed range | Construction 2 seed range |
|---|---:|---:|---:|---:|
| Q1 adjusted age | 0.07513 | 0.06712–0.08219 | 0.09532–0.09986 | 0.09591–0.10444 |
| Q2 BMI without glucose | 0.08364 | 0.07037–0.09521 | 0.05867–0.05904 | 0.05032–0.05876 |
| Q3 BMI with glucose | 0.05664 | 0.04390–0.06801 | 0.02372–0.02478 | 0.01631–0.02811 |
| Q2 minus Q3 | 0.02701 | 0.02197–0.03242 | 0.03426–0.03494 | 0.02896–0.03960 |
| Secondary glucose | 0.11420 | 0.09996–0.12929 | 0.11593–0.12252 | 0.10466–0.12267 |

Both constructions recover positive directions for these fixed projections, but neither reproduces their joint magnitude pattern. Every generated Q1 estimate exceeds the reference stability band's upper endpoint, while every generated Q2 and Q3 estimate falls below its lower endpoint. The additional Q3 conditional analysis therefore exposes a substantial magnitude discrepancy even though its direction is positive. Q2 minus Q3 is positive in every seed, but this is descriptive coefficient change and supplies no causal mediation result. All construction-1 changes and two construction-2 changes exceed the reference band's upper endpoint; the remaining construction-2 change lies within it.

The secondary glucose estimates are numerically close to the reference and fall within its empirical stability band. This is a limited descriptive transfer finding. Band inclusion is not an equivalence rule, and this single agreement does not validate the whole cohort. Marginal diagnostics also show differences: generated mean BMI is approximately 26.21–26.42 kg/m2 versus reference 28.66; generated BMI SD is 3.98–4.22 versus 5.52; glucose SD is 8.98–9.21 mg/dL versus 11.94; and HbA1c SD is 0.328–0.338 percentage points versus 0.527. HbA1c means are approximately 5.381–5.424% versus reference 5.314%.

These results establish successful execution and numerical consistency of the prespecified analytical workflow, alongside incomplete target transfer. They do not establish clinical substitution, national representativeness, causal identification, biological significance from synthetic sample size, method superiority, or calibrated model uncertainty. Q1 and Q2 are source-indexed transfer checks; Q3 evaluates joint conditional structure that was not directly supplied as a calibration target. No source reproduction claim was independently adjudicated here because source reports were outside this audit's access scope. Retention provides no evidence of post-feedback improvement, and the exposed target cannot become a tuning input for a new-confirmation claim.

Saved audit products and SHA-256:

- `postrun_results/comparison.json`: `e9c848f975e6ffe44a26ab9b54ee13e269f81b02fa0bed88e27c6101fe166649`
- `postrun_results/endpoint_comparison.csv`: `3883b17b039935cff3b360138100ed779eaba65aab179b8d4072980d2546ec76`
- `postrun_results/COMPLETED.json`: `6825971ad1a2c3c726cffcc38a070884460faeaea801d86132ac583376537c41`

The numerical report and its completion receipt remain unchanged. This separate review adds interpretation using aggregate results only and does not rerun any patient-level or generated-table analysis.
