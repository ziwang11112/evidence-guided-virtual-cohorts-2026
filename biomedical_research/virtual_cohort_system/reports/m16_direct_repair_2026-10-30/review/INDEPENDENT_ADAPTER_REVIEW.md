# M16 independent adapter and B1 retention review

**Decision: PASS for the reviewed independent adapter, subject to the separate final closure/release audit. This record does not authorize target release.** No hidden target bytes were read, and no real target evaluation or independent target recomputation was run. No prelaunch-bound file or frozen scientific arithmetic was changed.

## Inspected and modified scope

Inspected `independent_target_audit/recompute.py`, `test_recompute.py`, unchanged `frozen_independent.py`, the canonical evaluator/interface README, B1's closed initial/final audit chain and source/self-feedback, and the root-owned `release_target.py`. Edited only the independent wrapper/tests/documentation and reviewer-owned records.

The initial adapter mapped the scientific estimands correctly but lacked exact endpoint/deletion/change coverage checks, aggregate CSV-to-JSON validation, and a complete independent public release gate. Those gaps are now fixed. An invented rank-failure test also exposed a status vocabulary mismatch: independent `failure` versus canonical `rank_deficient`. The adapter now compares explicit success/failure while retaining original statuses, reasons and rank values. Neither arithmetic engine was altered.

## Bound versions

| File | SHA-256 |
|---|---|
| `independent_target_audit/recompute.py` | `c969c2141de94e7d31762ff86dca41a802f7e7deb800b79f7ba499cdb52d1f29` |
| `independent_target_audit/test_recompute.py` | `470e94e9b6743aca80dfb6af5aba15e0bbe174783bcb596df541448a51c7efd7` |
| `independent_target_audit/frozen_independent.py` | `e2cd4b3cc7720c3d2bc42f5e67dae9c67595534091f1fe0631683f16fc1398da` |
| `evaluation_code/evaluator.py` | `a63c3aecf9718ee9be1bd462bd0df3d40765d1228efd158fae69d18deda15483` |
| `evaluation_code/frozen_m15b_estimands.py` | `4181cfbd8ae37df58699558196ca241f2bd60e4d895b9a18de40a42cbaffce12` |
| `review/B1_RETENTION_CHAIN_AUDIT.json` | `f09bb2dba6fe122775bd1bb4600ab95bbe06dc5d7dc9348ea4b1ed7e5fd3038a` |
| Root-owned `release_target.py`, source reviewed after guard fixes | `1688cad973e21ce36f4c5eec42bc2fb28199147e472a81c3720acb8ba9f36c3a` |

## Numerical and release checks

The adapter retains the four global models, four group reverse regressions and 16 descriptive summaries. The independent implementation uses statsmodels QR fitting and separately written summary calculations rather than calling the canonical numerical routines. Complete-case counts, ranks, all available initial/final tables, changed-row counts and all 24 endpoints per stage are compared. Exact record-set validation prevents a missing or duplicated result from passing through a loop unnoticed. Initial/final difference and change records are checked without selecting a favorable stage.

All actual joint stratum/PSU groups are enumerated. Every deletion result, omitted and remaining count, rank, failure count, range and sign-stability field is checked. No prior target's PSU count is imposed. The current reference schema accepts native `WTMEC2YR`; the estimands remain unweighted finite-quota descriptions. Six complete stage records are not described as six independent tables when retention makes bytes identical.

The two canonical CSVs are checked against the documented JSON structure before the reference is read. This catches serialization corruption independently of numerical estimand agreement. Numerical tolerance is relative and absolute `1e-9`; it does not establish scientific accuracy or equivalence. Failure reasons are not forced into identical vocabulary. A disagreement in a nonfinite fit's rank-reporting convention remains a visible audit stop for review.

The public gate verifies the release identity and all seven controller assertions, canonical paths and hashes, prelaunch file/code/reference commitments, native weight-column identity, three builder identities and closure statuses, equal observed bytes and task semantics, registry prefixes, freeze/ancestry/table bindings, and the four preauthoring files with receipt copy/chronology. It rejects a reference binding or hardlink alias before hashing it as a public input. The reference bytes are accessed only after these checks and aggregate integrity checks. This remains procedural control, not sandboxing or cryptographic approval.

## Tests actually run

Final command used the project Python 3.12 interpreter, pytest, `independent_target_audit/test_recompute.py`, and fresh invented-fixture base directory `P/work/m16_independent_adapter_tests_review_d`.

**22 tests passed in 7.29 seconds.** They cover:

- All six table stages and joint-PSU numerical comparison; all changed-row counts.
- Deliberately altered estimates and covariates.
- Missing reference, candidate, change, builder and PSU records; duplicate candidate endpoints.
- CSV scalar corruption and a missing change row.
- Native weight metadata perturbed by many orders of magnitude without changing unweighted estimates.
- Retained identical rows, a failed builder with preserved initial, rank-deficient estimates and null PSU ranges.
- Authorized public gate without reference reads; missing closure assertion, wrong release kind, changed code/precommit, reference aliases and hardlinks; missing explicit execution flag.

The earlier rank-failure fixture failed as expected against the original adapter vocabulary and passed after the explicit schema mapping. All fixtures are artificial; no real reference or generated participant rows were parsed for these tests.

## B1 closed retention chain

`B1_RETENTION_CHAIN_AUDIT.json` records **66 binding/immutability assertions**. Both stages' four scientific files match their own preauthoring receipts and freezes. Evidence, model specification and construction are byte-identical across stages. The final revision plan is intentionally different and records `retain`; it is independently precommitted and frozen. Initial and final generated CSVs are byte-identical, implying zero changed outcomes and one authored table. Bytes were hashed without parsing participant rows.

The 33 source-check recipes preserve the predeclared mappings, including 13 unavailable comparisons. Final source results equal initial source results. The actual initial feedback copies match their hashes, and initial/current, final/current and final/original self reports are byte-identical. Terminal feedback is explicitly marked terminal. The final plan's source-mean differences, reverse slopes, residual BMI association, tail counts and tie counts agree with existing aggregate reports. Those reports remain source/own-guide diagnostics, with scientific validity not assessed.

B1 honestly states that retention did not improve the data. It does not disguise mismatched reverse slopes, unsupported conditional relationships or absence of a calibrated sampling law. Existing structural-preservation assertions are inherited from controller reports; actual row-level recomputation remains for the later authorized independent evaluation.

## Root release-writer interface

Source inspection of the updated `release_target.py` confirms it requires a passing closure record with `target_outcomes_read=false`, seven true assertions, a hash-bound `review/FINAL_RELEASE_AUDIT.md`, and all six initial/final freezes. It rejects private/reference and hardlink-alias audit bindings before hashing them. The reference is copied as metadata from prelaunch; the authorizer does not read reference contents on its normal path. No execution of this writer was performed here.

The writer intentionally requires all three builders to be complete. If a builder closes failed, it needs an explicit writer amendment/review; the canonical evaluator and independent adapter already support retaining a failed builder and its available initial. This review cannot replace the pending closure audit of B2/B3, source exposure, feedback budgets or final hashes.
