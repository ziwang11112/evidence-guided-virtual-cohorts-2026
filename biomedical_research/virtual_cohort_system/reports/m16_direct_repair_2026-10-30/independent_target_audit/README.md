# M16 independent post-release audit

`recompute.py` adapts the independently authored, frozen M15-B arithmetic to M16's three initial/final construction pairs. It does not import the canonical evaluator or execute the frozen module's old CLI. The frozen arithmetic is unchanged and pinned to SHA-256 `e2cd4b3cc7720c3d2bc42f5e67dae9c67595534091f1fe0631683f16fc1398da`; the original M15-B copy is also checked.

This is a second computation of an already authorized evaluation, not another development target or a source of feedback for builders. It requires the canonical evaluation output and its matching release manifest. It never creates or repairs outcomes.

## Invocation after authorized canonical evaluation

From the run directory, with an unused audit output path:

```powershell
python independent_target_audit/recompute.py --execute --release private/evaluation_release.json --results results/evaluation.json --output independent_target_audit/actual_results.json
```

The invocation is illustrative. This review did not run it on real data.

Without `--execute` the wrapper reads no inputs. Existing output is rejected before inputs are read. Before reference bytes, an independent procedural gate checks the release kind, seven required controller assertions, code and prelaunch bindings, native reference commitment, all scheduled builder identities and closure states, common observed hashes/task semantics, source registry seed prefixes, candidate ancestry/freeze commitments and all four preauthoring scientific files. Reference paths and hardlink aliases cannot be hashed as public bindings. These checks are procedural integrity controls, not operating-system isolation or proof of reviewer identity.

Both aggregate CSVs beside `evaluation.json` must exactly match independently flattened JSON values, headers, row counts, and order. This is a serialization-integrity check separate from the independent numerical calculations.

## Numerical interface

- Four global coefficients, four within-race/sex BMI-on-urate coefficients, and 16 group descriptive statistics: exactly 24 endpoints.
- Every available initial/final stage is retained, including identical retained tables. Missing or duplicate stage/endpoint/change records fail the audit. Failed builders remain represented; an available initial is not discarded.
- Observed identity, order and covariates are checked independently. Numeric changed-urate counts are compared for each complete pair.
- All reference joint `(stratum, PSU)` deletions and the four global deletion summaries are checked, including omitted/remaining counts, ranks, failures, ranges and sign-stability metadata. A PSU number reused in another stratum remains a separate group.
- `WTMEC2YR` is native private reference metadata. It is not a weight in these unweighted quota-sample estimands. The frozen old reference-file loader is never used; the M16 wrapper checks the native schema itself.
- Numeric agreement uses both relative and absolute tolerance `1e-9`. This is computational agreement, not biological equivalence. Change-direction labels are checked against the canonical numeric change; tiny equivalent floating-point differences between independent solvers are not reinterpreted as an improvement.
- The independent engine records `failure` plus a reason, while the canonical engine has typed failures. The adapter preserves both originals, compares success/failure status, and separately compares value, sample counts and rank. Rank-deficient/null cases are explicitly tested. A nonfinite case with different rank-reporting behavior may stop for manual review rather than silently normalize that discrepancy.

## Invented tests

`test_recompute.py`: **22 passed in 7.29 seconds** in the final review run. Coverage includes all six stages; changed estimates/covariates; missing/duplicate records; CSV corruption and missing rows; unweighted native metadata; joint PSU grouping; retained and failed builders; rank-deficient/null fits; and release failures before any reference read, including direct aliases and hardlinks. All fixtures are invented; no private target or real generated cohort is used in these tests.

The public gate depends on trusted closure/source-review assertions and immutable hash records. The review does not establish the truth of the scientific model, usefulness of generated data, or permission to release an unfinished experiment.
