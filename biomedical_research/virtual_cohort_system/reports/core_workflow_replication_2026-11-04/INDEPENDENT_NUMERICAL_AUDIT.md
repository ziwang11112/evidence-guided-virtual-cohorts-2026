# Independent numerical and accounting audit

2026-11-04. **PASS.** The separately implemented audit reproduces all **366/366** final endpoints across all **12/12** planned slots. There are zero numerical mismatches, zero unavailable endpoints in this completed corrected evaluation, and zero inventory/accounting issues.

The actual run first passed the frozen all-author closure gate, then verified evaluation_v2/EVALUATION_COMPLETED.json and both bound output hashes. The reviewed correction manifest and all its bindings were also checked. The closure gate and completed-output hashes passed again after calculation. Two earlier mock-only boundary checks established that blocked closure and missing corrected completion each prevent any result/table read. A separate agent statically checked the independent formulas and gates before the actual run.

## Numerical results

| Case | Planned endpoint comparisons | Maximum absolute difference, all endpoints | Maximum absolute difference, three main endpoints |
|---|---:|---:|---:|
| CHNS2009 | 180 | 3.552713678800501e-15 | 9.783840404509192e-16 |
| ENSANUT2018 | 186 | 4.263256414560601e-14 | 3.069766663088558e-14 |

The tolerance was fixed before inspecting generated outputs: absolute difference at most 1e-10 + 1e-9 times the larger absolute value. All ENSANUT inverse-CDF quantiles additionally matched exactly as observed values. Every endpoint's generated evaluation value, independent value, difference, tolerance, units and status is retained in evaluation_v2/independent_numerical_audit/RESULTS.json. These tolerances assess floating-point agreement, not biomedical accuracy or equivalence.

Regression coefficients were recomputed by SciPy pivoted QR with the declared SVD rank convention, without calling the original providers or analytical engines. ENSANUT's exact 375-person allocation in each of eight cells makes all row weights equal, so the independent ordinary fit equals the declared WLS projection. RMS and marginal moments used independent sums. CHNS uses sample SD, linear quantiles, SciPy Pearson and average-rank Spearman; ENSANUT uses population SD and the first observed value whose original-row cumulative mass reaches the normalized probability, using independent compensated summation. The CSV reader uses Python's round-trip float conversion, consistent with the frozen transport convention.

## Inventory and preservation

| Author | Query credits | Original downloads | Frozen candidates | Trial / final attempts | Decision |
|---|---:|---:|---:|---:|---|
| C01 | 6 | 4 | 1 | 1 / 3 | retain |
| C02 | 6 | 4 | 1 | 1 / 3 | retain |
| E01 | 7 | 4 | 1 | 1 / 3 | retain |
| E02 | 5 | 4 | 1 | 1 / 3 | retain |

All 16 charged physical attempts are retained, with 12 distinct final table hashes. All final CSVs have 3,000 finite rows and distinct nonempty row identifiers; task bounds and exact ENSANUT cells pass. Source IDs/usage, acquisition commitments, freeze/decision inventories, required initial trials, decision-before-final order, selected candidates, output routes, seed roles, error/status accounting, CSV/JSON endpoint coverage, cost-record identities and generated-only summary counts/means/ranges agree. No author used a revision.

The original evaluator and original evaluation remain preserved. V1 rejected finite NumPy float64 quantiles at an exact Python-type check and consequently marked all CHNS endpoint payloads unavailable. This was corrected additively by the independently approved evaluator_v2 scalar acceptance/serialization change. No model, scientific parameter, seed, generated table, estimator or reference changed. The numerical audit explicitly binds that correction and does not recast the v1 attempt as successful.

No generator was executed by this audit, no participant/reference file was opened, and no reference value was used in the independent calculations. Completed evaluation files contain reference fields, but the audit ignores them. It checks existing aggregate comparison-availability labels only when reproducing generated-summary inclusion. The frozen runner is reused solely for commitment/closure verification; all scientific numerical calculations are separate.

This pass establishes numerical and accounting consistency. It does not establish clinical validity, successful source transport, usefulness for every intended analysis, independent scientific structures, or superiority over another method.

## Bound artifacts

- independent_numerical_audit.py: bac3ee6ad9e68dbe273d75da4a414165e83bf51b270af19feb04f6e36ebd2f84
- evaluation_v2/independent_numerical_audit/RESULTS.json: 3c6262e1e5dff180d950aa2e884a98b195308159fcff848e46331796bd95042a
- evaluation_v2/independent_numerical_audit/AUDIT_COMPLETED.json: 060abe9283d5f598313f1c9fff47ea308cc355dfc4bc86ef3c61a29541504ef3
- EVALUATOR_V2_CORRECTION.json: 4965fbe9bc15c4f18122f5ac393a1d52cb3f892448adb66f5466fa0ef2b24f9d
- CONTROL.json, unchanged: ae31ee07eddabcd592d8cde0a2bcc5326f108a5d2073de83f96ef2e9d2aa3503

Runtime: NumPy 2.4.5, SciPy 1.17.1. No further execution or extension is needed for this numerical audit.
