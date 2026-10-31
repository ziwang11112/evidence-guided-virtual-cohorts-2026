# Source-context bridge readiness

2026-10-31. **Mechanically ready for root review; no clinical use performed.** Implementation is confined to this `method` directory. Existing harness code, historical reports/verifiers and `STATE` were not edited. No target/private/results contents were read. Source-context scientific adequacy remains a separate substantive decision.

## Implemented contract

`run_source_contexts.py` creates separately frozen whole-cohort child bundles and uses existing execution/feedback APIs. The complete parent specification is preserved in every child except `parameters.active_context`. Canonical JSON comparison distinguishes booleans, integers and floating-point representations. All scientific values, all context definitions, parameter provenance and assumptions remain fixed. Each child task must match its predeclared descriptor; only population, row count and numeric supports may differ from the parent, inside the declared common domain.

`SOURCE_CONTEXT_SCHEMA.md` documents exact inputs and APIs. The parent must contain a frozen `source_context_plan.json` and each source's preauthored task/feedback recipe. Preparation binds the parent freeze, generator, complete specification, normalized shared specification, source registry prefix, child freezes and implementation hashes. Completed reports verify execution identity/limits and recompute each child's existing whole-cohort feedback. No host import/execution of the candidate generator, local backend fallback, coefficient selection, fitting, measurement conversion or source-row reconstruction is implemented.

Two safeguards identified during independent static review were incorporated before testing: reject undeclared context directories even under execution-like paths, and use canonical comparisons for exact specification/task/registry identity. The statistical-preflight module is also included in the implementation hash bindings. The reviewer found no remaining blocking issue; that was static review, not additional execution evidence.

## Actual checks

| Retained attempt | Outcome | Runtime | Explanation |
|---|---|---:|---|
| `test_runs/run01` | 1 passed, 41 failed | 1.87 s pytest time | Fixture paths exceeded legacy Windows path limits before preparation completed. No generated table was created. All files/logs remain. |
| `test_runs/run02`, fixtures `u02` | 42 passed | 7.10 s pytest time | Compact hashed temporary directory names resolved the filesystem issue. |
| `test_runs/run03`, fixtures `u03` | **43 passed** | **7.47 s pytest time** | Added a test proving that re-freezing a changed child scientific parameter cannot evade the shared-construction audit. |
| Artificial isolated smoke, `p01` → `s01` | **2/2 successful and freshly reverified** | **4.142261 s** total execution/verification wall time | Existing inspected Ubuntu-24.04 WSL/bubblewrap runtime; seed 17401. |

The focused suite checks valid independent supports, exact specification preservation, malformed/unknown/case-colliding selectors, task/descriptor/policy mismatches, domain bounds, metadata/operator rejection, parent/child/artifact tampering, re-frozen scientific changes, no-observed input, append-only destinations, forbidden host backend, failed runtime retention and report tampering. Unit tests generate no individual tables. The runtime-failure tests leave empty output placeholders and false linkage flags, with no fallback launch.

The first attempt and subsequent tests are retained rather than cleaned up. The project directory is not a Git checkout, so no Git-based change assertion is made. The recorded implementation/source hashes and this agent's restricted writes document the scope.

## Isolated artificial smoke

The trusted preparation-only `prepare_artificial_source_contexts.py` writes a fictional arithmetic-sequence program as inert text. It creates neither rows nor execution results. The program is first imported inside the existing isolated worker. It is an engineering fixture, not an Agent-authored biomedical model or scientific result.

| Context | Generated rows | Declared and computed mean | Difference | Execution receipt elapsed |
|---|---:|---:|---:|---:|
| `source_a` | 4 | 11.5 fictional units | 0 | 2.610 s |
| `source_b` | 6 | 22.5 fictional units | 0 | 0.625 s |

Exactly **two nonempty `generated.csv` files** exist under this method directory, both under `s01/contexts/.../executions/source/output/`. The parent public-design fixture was not executed. No `input/observed.csv` was staged. Both retained worker probes report `/mnt` absent, `/home` absent, and an empty network route table; network interface enumeration is unavailable because `/sys` is not mounted. These are generator-process observations, not Agent-wide isolation evidence.

`SMOKE_SUMMARY.json` records measured timings/checks. `s01/report.json`, per-context execution receipts and feedback reports retain the executable linkage. A separate fresh Python process successfully ran `verify_source_contexts` after execution. `IMPLEMENTATION_RECEIPT.json` binds the reviewed code, unit logs/XML, schema, readiness note, artificial parent freeze, smoke preparation/report and summary. `implementation_v1/` preserves the exact case-local implementation used by the smoke; do not rewrite its receipts if later code changes.

## Use and limits

API sequence from a trusted controller with the project on its import path:

```python
prepare_source_contexts(parent_bundle, "initial", new_destination, seed,
                        runtime=trusted_runtime)
verify_preparation(parent_bundle, new_destination, candidate="initial")
execute_source_contexts(parent_bundle, new_destination, candidate="initial")
verify_source_contexts(parent_bundle, new_destination, candidate="initial")
```

Keep Windows destination paths short enough for the existing filesystem/runtime; the bridge intentionally does not alter global long-path settings. Source IDs and auxiliary paths should be concise. A failed or partially started destination is retained and cannot be reused; prepare a fresh destination for any authorized retry. Invalid execution receipts may prevent final outer report creation and never gain successful linkage.

The bridge verifies mechanical shared construction, not whether the program uses the selected context scientifically correctly. Aggregate-only inputs still need substantive review: nested specification JSON and admitted evidence cannot be certified free of individual records by hashes. Population eligibility, missing adjustment variables, measurement equivalence, survey estimands, source uncertainty and transportability remain Agent/reviewer responsibilities. Ordinary Agent work remains valid; no forced benchmark comparison or ablation was added.
