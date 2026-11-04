# Independent runner and evaluator implementation review

Date: 2026-11-04. Decision: no materially blocking implementation finding remains in the reviewed, hash-bound controller. This does not approve a scientific candidate or certify a successful execution; those gates remain separate.

Reviewed code: run_session.py; evaluation/generated_diagnostics.py, comparison_core.py and evaluate_build.py; relevant permitted execution/lifecycle/semantic-feedback interfaces; the controller's targeted routing tests and reports; RUNTIME_PREFLIGHT.json; IMPLEMENTATION_NOTES.md; and CONTROL_MANIFEST.json. No target-reference report, historical result values, patient data or generator was read or executed for this review. No network requests were made.

## Corrections verified

The initial implementation could lose a successful generated table when downstream source feedback or generated-only diagnostics threw an exception. The corrected runner binds a verified output first and records feedback/diagnostic failures separately. The evaluator uses execution success and verified table binding, so such a failure no longer drops that scheduled draw.

The initial closure recorded candidate names without committing all delivery artifacts. The corrected closure binds initial/final freeze hashes, the final decision, all session JSON records (including reservations, results, family bindings and aliases), existing execution receipts, successful delivery tables and the control manifest. The gate recomputes these bindings before reading the pinned aggregate reference. Existing execution receipts, including failed ones, are checked against the reserved candidate and seed.

The original independent numerical check could raise when HC3 intervals were unavailable in a full-rank, high-leverage design. Both numerical paths now retain coefficients and explicitly mark unavailable interval checks. The targeted analytical fixture covers that edge. The accounting also distinguishes physical delivery attempts from successfully verified unique delivery tables, avoiding an inflated table count for failures or retained aliases.

## Budget, ordering and lineage

The controller permits one original family and at most one direct revision. Reservations occur before execution, failures consume their slot, existing reservations cannot be retried, a lock prevents concurrent controller operations, and unbudgeted execution directories are rejected. The maximum is eight physical attempts. No local execution fallback is present.

The initial trial is mandatory at seed 7400. All three initial deliveries use 7401, 7402 and 7403. As explicitly clarified by the root controller and recorded in IMPLEMENTATION_NOTES.md, revision_trial=[7410] denotes the allowed optional revision-trial seed; it is not a compulsory execution. Every revised final delivery still requires all three delivery seeds. Retention aliases all three initial delivery slots and performs no new generation. This clarification leaves the protocol hash unchanged.

Only semantic_feedback_v1 is called; there is no legacy feedback fallback. Its declared-statistic checks do not reconstruct a source population or establish transport. Generated-only diagnostics import no generator and read no reference. Actual feedback binding to an author revision/retain decision remains a candidate/closure audit item; the runner alone does not certify that scientific decision.

The evaluator requires explicit author closure, matching final decision/family, complete delivery slots, intact execution/output commitments and the closure artifact bindings before opening the pinned reference aggregate. It has no patient-data decoder or reference fitting route. All initial/final delivery slots, failures, coefficient terms and declared analyses remain represented; no favorable seed selection, pooled success score or equivalence threshold is implemented.

## Statistical calculation review

The production calculation uses OLS with an intercept and HC3 covariance `X+ diag((e/(1-h))^2) (X+)'`, followed by t intervals with n-k degrees of freedom. The independent calculation uses reduced QR and its corresponding HC3 score formula. Both are appropriate numerical implementations of the stated conditional synthetic-draw interval. These intervals do not represent source, model or transport uncertainty.

The primary and secondary adjustment sets are distinct and correct. Marginal SD uses ddof=1; the stated sample quantiles use linear interpolation. Pearson and Spearman calculations are checked separately, with rank-based recomputation for the latter. Seed ranges and sample SDs summarize fixed-model Monte Carlo variation and remain separate from reference intervals. The comparison preserves raw differences and signs without interpreting agreement as validation.

## Verification evidence and commitments

Independently recalculated file hashes match all four controller files and all nine mechanics files in CONTROL_MANIFEST.json. Both targeted-test report hashes also match. Manifest SHA-256: `9c45570c89b4afb0387d546f946b4984acb581f8a5e3028dbad9142e555669d9`.

- run_session.py: `181098dd30ac2bcc0d791b8d569cac1995201d4d03f5cc500552a4f919215614`
- generated_diagnostics.py: `77a806f77a384b4e22fd4e413e11e49fd1169c4c70320b029526c70929017bc3`
- comparison_core.py: `1e799112f472ec4848b7bd03403308274332b561501095aecf5043328f281330`
- evaluate_build.py: `8882ebd9d7cbd252a2c3cd0d1d93a77cc30dd65483b53ceb68ddd235fb0a583f`

The inspected CONTROLLER_MOCK_CHECKS.181098dd30ac.json records 15 passing routing/budget/error/closure checks. ANALYSIS_ROUTING_CHECKS.json records both analysis routes, independent formula checks and the unavailable-interval case using 160 in-memory analytical fixture rows, zero clinical rows and zero scientific candidate executions. This reviewer inspected those tests/results and code but did not rerun them or broaden testing. The earlier mock report is preserved as pre-correction evidence.

RUNTIME_PREFLIGHT.json records Python 3.12.3, NumPy 2.4.5, pandas 3.0.3 and hashes of five named runtime files. It is a narrow existing-runtime inspection, not a full dependency-tree certificate or proof that a candidate ran. Actual execution receipts and runtime bindings must be inspected after execution. Hash commitments are procedural integrity records, not signatures or OS isolation of the author/reviewer tools.
