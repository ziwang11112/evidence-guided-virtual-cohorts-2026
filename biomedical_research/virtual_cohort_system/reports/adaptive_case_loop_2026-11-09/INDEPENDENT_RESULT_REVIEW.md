# Independent adaptive result review: PASS_AGGREGATE_REPORTING

All six scheduled 3,000-row outputs are retained and analyzable. Independent postclosure recomputation agrees on **156/156 values**: 18 primary estimates and 138 diagnostics. Maximum absolute difference is **5.15 × 10⁻¹⁴**. Hashes bind the closure, all generated outputs, evaluation, final narrative and PNG/PDF plots. This is an arithmetic/reporting pass, not a clinical-validity score.

## All three requested analyses

| Endpoint | Unit | Retained initial mean | Unselected sensitivity mean | Reused sample reference |
|---|---|---:|---:|---:|
| K02-HDL-BMI | mg/dL per 5 kg/m² | -1.1898 | -1.1999 | -4.6230 |
| K02-TC-BMI | mg/dL per 5 kg/m² | 10.6997 | 14.7893 | 5.6831 |
| K02-LIPID-RESIDUAL | 1 | 0.1383 | 0.1986 | 0.5121 |

The retained primary has a less negative HDL slope, higher TC slope and lower residual correlation than the sample point estimates. The sensitivity moves residual correlation closer while moving the TC slope farther away; it remains unselected. **The author selected initial before reference evaluation, so initial-to-selected-final changes are zero.** No favorable alternative or seed was substituted.

## Coverage and interpretation

- All three analyses and 23 diagnostics appear for every output. Thirty values have matching frozen references; 126 diagnostic values remain generated-only. No execution or generated-endpoint failure occurred.
- Six source-feedback receipts contain 34 not-computable checks each: **204 unavailable instances and zero computable formal source comparisons**. They are neither passed source-calibration checks nor clinical endpoint failures. They are separate from the 156 computed output statistics.
- Reference slope intervals retain their HC3 normal assumption-conditional sensitivity meaning. The TC interval includes zero; residual correlation has no supplied interval. Being inside a supplied slope interval does not demonstrate equivalence. Seed ranges are simulation variation, not clinical confidence intervals.
- The final narrative and figure identify the retained primary and unselected sensitivity, show all three analyses and exact units, and avoid an overall gain or causal skill-superiority claim. One author and reused exposed aggregates provide no fresh clinical confirmation.
- No original reference JSON or real patient file was opened. Existing generated rows were read only after closure; no author program was imported, no rows regenerated and no target refit performed. Source-transfer validity remains a separate audit.

The generated EVALUATION.md retains a cosmetic table interruption in its second-stage dispersion block; the final RESULTS.md supplies a correctly structured table with both stages. No numbers are omitted.

Exact artifact and output hashes, recomputation results and all primary estimates/intervals are recorded in [INDEPENDENT_RESULT_REVIEW.json](INDEPENDENT_RESULT_REVIEW.json).
