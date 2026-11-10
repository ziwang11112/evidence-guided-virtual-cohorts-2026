# Independent PNS BP results review

**PASS: independent numerical and selection recomputation.**

Results SHA256: `8cf31512061de7bdd76450bcf164398db7934a7228b30cddcfb591b017f7fbec`.
Batch SHA256: `1f3f8137ad282a4844f5c27ff1219fd5827164e720fafc1c71d417bbb27f3acd`.

Independently selected 8,352 of 8,952 rows from the fixed eight workbook fields; all sequential exclusion counts, pregnancy handling and retained duplicate counts match.
Recomputed weighted/unweighted reference and all 15 sealed outputs using the frozen pure-Python FWL oracle: 306 numerical comparisons; maximum absolute difference 1.82e-12. All 45 focal comparison records and 60 dispersion ratios agree within 1.43e-13.
No generator executed, evaluator rerun, patient table persisted, or sealed/frozen file modified.

| Analysis | Weighted reference | Unweighted reference | Generated range, all 15 |
|---|---:|---:|---:|
| BMI–SBP, mmHg per5 kg/m² | 3.523995 | 3.435308 | 3.081446–4.275566 |
| BMI–DBP, mmHg per5 kg/m² | 2.259946 | 2.113805 | 2.886276–3.690607 |
| Adjusted residual BP correlation | 0.717184 | 0.741448 | 0.465841–0.646204 |

The SBP association is in a similar numerical range to the reference across constructions. DBP associations are systematically higher, while residual correlations are systematically lower. These are descriptive observations, not post-hoc pass/fail thresholds or claims of population bias.

A04/A05 final records independently checked: both kept the initial candidate and all three seeds, bound all six feedback and three analysis reports, and acknowledged mismatched descriptive source statistics. No target-based revision occurred.

## Interpretation limits

- PASS concerns reproduction and implementation integrity, not a data-quality pass for five authors. No preregistered quality threshold or equivalence/superiority test exists.
- All 15 outputs retained initial models. This case demonstrates no improvement from revision or additional retrieval, and no exact source-population replay.
- Reference is a weighted selected analytical sample, not known population truth. PNS is an already exposed study family; this is a qualified new BP task.
- Reference intervals are conditional IID row-bootstrap stability with row/weight pairs resampled. They ignore complex survey strata/PSU design, missingness, selection and source/transport uncertainty; not national confidence intervals.
- The 500 reference bootstrap values were not recomputed on patient data in this audit; their frozen algorithm and quantiles were independently tested on invented fixtures before release. This audit rechecks settings, counts and interpretation.
- Three stochastic seeds and five model authors are not 15 independent clinical studies. Their spread is not calibrated epistemic or transport uncertainty.
- Matching association signs alone is not sufficient for all scientific uses. Differences in effect size and residual dependence remain visible and must not be hidden by an all-pass label.
