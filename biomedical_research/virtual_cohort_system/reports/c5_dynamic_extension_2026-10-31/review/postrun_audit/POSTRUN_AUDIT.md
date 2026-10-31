# C5 independent actual-output audit

**PASS.** All planned numerical analyses and diagnostics were independently recomputed from the nine actual local output CSVs. No discrepancy requiring correction was found. No generator or evaluator code was executed/imported for the independent statistical calculations, and no scientific run was repeated.

## What was verified

- Nine scheduled successful isolated generator executions, each with 2,000 fictional rows; nine unique file contents. Six are final three-variable tables and three are their two-variable parent draws.
- All 48 endpoint estimates: old-pair slope/intercept on all nine tables, and new adjusted slopes/intercept plus residual variance/SD on the six full tables. All 210 accompanying diagnostic estimates were also recomputed, including means, sample SD/covariance, correlations, linear-interpolated quantiles, and population-conditional residual checks.
- 1,213 numerical fields (estimates, analytic references, signed/absolute deviations, summaries and comparisons) matched the primary evaluation within arithmetic tolerance. Maximum absolute discrepancy: 4.263256414560601e-14. The independent implementation uses Python csv/math/statistics and explicit centered covariance formulas; it does not reuse the evaluator's estimation functions.
- 649 structural/integrity checks passed, covering exact output schema/count, finite values, IDs, old-cell preservation, provenance, current code/plan, actual receipts and aggregates. Ten original source/custody/evaluator artifact hashes were additionally verified after release; the evaluation's embedded analytic reference equals its originally committed file.
- All three extensions preserve parent IDs/order and all x1/x2 values exactly. Parsed numeric differences are zero; lexical old CSV cells also match. Parent/extension A1 slope and intercept are exactly identical under the independent arithmetic.
- Each child's six scientific files match the precommitted extension template byte for byte. Native verification confirms the frozen candidates, execution receipts and preservation reports. Synthetic parent input provenance remains explicitly synthetic.
- The three non-generation requests are reuse, new_population and clarify. Each has a verified routing record, no child bundle and zero generated tables.
- The native scientific namespaces contain exactly the nine planned receipts, with no reruns or failed attempts. Audit fixture executions under the separate pre-execution review directory are not counted as scientific runs.
- The execution-start record pins the current run plan; plan/source/scientific bindings remain unchanged. Recorded chronology places final-output commitment before reveal authorization and evaluation. This is auditable procedural chronology, not cryptographic proof of every possible tool access.
- All eight explicitly snapshotted historical anchors are unchanged. The historical manifest does not claim to cover every byte of every past experiment.

## Main numerical results

Values below are means over the three fixed synthetic draws per route, not independent clinical replications.

| Analysis | Constructed population | One-shot joint | Conditional extension |
|---|---:|---:|---:|
| Old x2-on-x1 slope | 0.750000 | 0.758431 | 0.752477 |
| x3 adjusted x1 coefficient | -1.362591 | -1.393243 | -1.314859 |
| x3 adjusted x2 coefficient | 0.927900 | 0.948711 | 0.891281 |
| Conditional residual variance | 42.833856 | 42.442044 | 44.005858 |

The extension's old-pair result exactly equals that of its preserved parent. Finite draws do not equal exact population summaries; all residual deviations and per-seed values remain in INDEPENDENT_RESULTS.json. No post-hoc tolerance, algorithm winner, equivalence claim or confidence-coverage claim is introduced.

## Observed execution cost

The nine native execution receipts record 8.048 seconds in total. The recorded controller-start to final-manifest interval is 9.982882 seconds. These are local elapsed-time measurements, not CPU time, total research time, model token cost or human effort. CPU usage, peak memory, full Agent/human effort and monetary cost were not metered. The fixed runtime reports Python 3.12.3, NumPy 2.4.5 and pandas 3.0.3.

## Scientific interpretation and retained limitations

The actual outputs and prior structural review support a functioning conditional-extension implementation for this fully specified artificial Gaussian example. The system appended stochastic x3 while preserving the original synthetic records and supported every planned calculation. This does not show that it inferred a missing real-world relationship from incomplete publications, transported between real populations, improved over another Agent, or saved patient measurement costs.

Complete source moments already determine the analytic answers. One scientific author with an algebra helper produced related routes; three seeds are Monte Carlo draws, not independent method authors or patient cohorts. Root's early final-source intake and the author's incidental Phase 2 historical-summary exposure remain disclosed. No conclusion of complete role blindness is warranted. The known initial marginal and final conditional law are compatible by construction; real evidence admission and unknown-dependency handling remain separate next steps.

The unit can close without extra seeds, revised parameters or further artificial tasks. This audit does not itself satisfy the fresh real-case readiness gate.

## Audit artifacts

- POSTRUN_AUDIT.json: verdict, accounting, measured elapsed times and output/evaluation bindings.
- AUDIT_CHECKS.json: all structural checks and numerical comparison fields.
- INDEPENDENT_RESULTS.json: recomputed analyses, complete summaries and all declared between-route contrasts.
- CUSTODY_INTEGRITY_CHECKS.json: post-reveal checks of all ten originally committed artifacts.
- recompute.py: independent recomputation source; no candidate/evaluator import or generator calls.
