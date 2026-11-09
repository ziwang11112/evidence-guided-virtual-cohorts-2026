# Independent aggregate result review: PASS_AGGREGATE_REPORTING

All 18 scheduled draws succeeded and retain complete endpoint sets: **54 primary estimates plus 459 diagnostics = 513 scalars**. Coverage is three primary analyses plus 28 diagnostics per glycemia draw, and three plus 23 per lipid draw. The inspected independent recomputation agrees on **513/513** values; the largest absolute difference is **7.82 × 10⁻¹⁴**. Its tolerance checks floating-point arithmetic, not clinical equivalence.

Receipt/file hashes, all seed identities, seal/closure/evaluation ordering, endpoint units, all comparison arithmetic, 171 construction summaries, and Markdown/JSON consistency were independently checked. The report retains **189 unavailable reference comparisons** for 21 lipid diagnostics across nine draws. The implementation review remains unchanged.

## Primary results

Values below are means across the three scheduled seeds of each authored law. A = installed skill; B = A plus task rubric; C = B plus reusable procedures. Exact seed ranges and supplied uncertainty remain in the bound evaluation and review JSON.

| Endpoint | Unit | Reused reference | A mean | B mean | C mean |
|---|---|---:|---:|---:|---:|
| Q1_age10 | percentage points / 10 years | 0.0751324 | 0.101451 | 0.0980937 | 0.0959441 |
| Q2_bmi5 | percentage points / 5 kg/m² | 0.0836428 | 0.0562014 | 0.0616312 | 0.06045 |
| Q3_bmi5 | percentage points / 5 kg/m² | 0.0566375 | 0.0292355 | 0.044905 | 0.0357213 |
| K02-HDL-BMI | mg/dL per 5 kg/m^2 | -4.623 | -2.43131 | -2.16664 | -2.19569 |
| K02-TC-BMI | mg/dL per 5 kg/m^2 | 5.68311 | 11.2159 | 9.7649 | 10.7028 |
| K02-LIPID-RESIDUAL | 1 | 0.51207 | 0.125103 | 0.135491 | 0.135948 |

For these specific constructions, glycemia B/C show smaller mean absolute discrepancies than A on each primary endpoint, with no consistent C-over-B pattern. Lipid discrepancies vary by endpoint. Every lipid construction produces residual correlation near 0.13 versus the reused reference near 0.51. These are descriptive observations, not causal effects of instructions or evidence of general skill superiority.

## Uncertainty and limits

- Glycemia bands are endpoint-specific **399-attempt empirical cluster-resampling stability bands**, not national confidence intervals or acceptance margins.
- Lipid slope intervals are **HC3 normal assumption-conditional sensitivity intervals**, not design-based confidence intervals. The TC-BMI interval includes zero. Residual correlation has no supplied interval.
- Generated-data inferential intervals remain unavailable. The three-seed ranges describe draws from one law and are not confidence intervals or independent-author replication.
- References were previously exposed and reused. One author per arm/case, unequal unmeasured token use, and assumption-dependent transfer limit interpretation. No fresh clinical confirmation or overall quality score follows from this arithmetic pass.
- Source-use/process quality is reviewed separately. No real patient files, original reference files or authored models were opened here, and no regeneration or target refit occurred.

Exact reviewed files are bound in [INDEPENDENT_RESULT_REVIEW.json](INDEPENDENT_RESULT_REVIEW.json). The review covers [EVALUATION.json](EVALUATION.json), [EVALUATION.md](EVALUATION.md), completion/closure records, [independent_recompute.py](independent_recompute.py), and [RECOMPUTATION.json](RECOMPUTATION.json).
