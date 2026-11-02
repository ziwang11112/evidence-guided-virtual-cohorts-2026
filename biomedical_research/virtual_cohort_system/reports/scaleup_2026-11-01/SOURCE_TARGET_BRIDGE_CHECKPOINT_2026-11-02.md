# Source/target execution connected and tested in the isolated runtime

2 November 2026. The user asked to implement the approved design, connect source and target generation, review the implementation carefully and avoid manually prescribing biomedical relationships. This checkpoint implements that bounded connection. **It runs two invented software-fixture executions, not a new biomedical experiment.**

## What is now connected

The new [bridge](bridge/README.md) takes a frozen scientific candidate containing source and target contexts, derives context-specific tasks and the explicit active-context selector, requests independent review of the derived bindings, seals the child candidates, and executes the finite declared schedule through the existing WSL/bubblewrap adapter.

Actual source and target executions use the same generator bytes and the same full scientific specification apart from `active_context`. Shared parameters and allowed context-varying inputs must be declared. The bridge does not insert means, slopes, residual scales, expected signs or correlations. These remain decisions of the clinical constructing Agent when a real case is released.

Sources use `semantic_feedback_v1` explicitly, with the existing supplemental collector only when declared. Target execution can have no source feedback. The source evidence remains unchanged; unavailable strict calculations and descriptive/assumption-defined diagnostics remain separate. Fixed trial IDs, seeds and row counts debit attempts before dispatch. Re-preparation cannot reset this retained parent's budget, and failed/interrupted work cannot be silently retried. Global campaign budgets remain the campaign controller's responsibility.

The separate [unit adapter](bridge_units/README.md) converts an explicitly reviewed target-analysis view while preserving rows, identifiers and other columns. It checks declared analytes, direction and unit mapping, changes numeric values and records content commitments. It does not fit a biomedical relationship. The actual smoke caller verifies the execution and task before using this pure component.

## Actual live integration result

The [reusable smoke driver](bridge_smoke/run_invented_pair.py) prepared an invented frozen parent and unsigned review requests. A separate reviewer inspected and approved the actual source, target, supplement and invented unit-map commitments before execution. The live path used the inspected runtime, not the mocked process boundary used in unit tests.

| Check | Actual result |
|---|---|
| Source execution | 3 invented rows, seed 101, one attempted run, successful; recorded execution time 0.671 s |
| Target execution | 6 invented rows, seed 103, one attempted run, successful; recorded execution time 0.578 s |
| Scientific construction linkage | Identical code and common specification, with declared shared toy scale 1.0; only active context changes |
| Context selection | Different fixed row counts make a wrong selector observable through the output contract |
| Source feedback | Original geometric mean remains unavailable in strict v1; the supplemental descriptive geometric mean is 2.0; no strict discrepancy or proxy difference is invented |
| Target feedback | None, as declared; no real target effects used |
| Unit view | Explicit invented factor 2 changes the target values as expected and preserves identifiers; the input contract is checked against the verified target task |
| Attempts / biomedical count | Two isolated software runs; zero new clinical constructions, zero new patient-reference evaluations |

The reported execution times are receipt-level runtime durations. They exclude Agent work, review, preparation and overall task wall time, and are not an end-to-end research-cost claim. Exact aggregate records are in [LIVE_RESULT.json](bridge_smoke/LIVE_RESULT.json), [BRIDGE_REPORT.json](bridge_smoke/BRIDGE_REPORT.json) and [UNIT_CONVERSION_RECEIPT.json](bridge_smoke/UNIT_CONVERSION_RECEIPT.json). Full fixture execution directories remain local; no patient or generated row-level table is exported.

## Independent review and corrections

The [independent component review](bridge/INDEPENDENT_REVIEW.md) found and resolved source-ID attribution, normalized reviewer identity, consumed-versus-successful status, and retention of partial/error artifacts. Reporting now separates any verified pair, all planned generation links, and all successful diagnostic trials. The completed ledger binds retained artifacts, including failures.

Bridge tests cover 37 distinct cases and were independently reproduced with the process/runtime boundary mocked, while using real lifecycle and semantic/supplemental checks. The unit adapter's final suite has 56 distinct invented-array cases; independent review separately checked the earlier 54-case suite and six affected review checks after a fix. Repeated reviewer/author runs are not counted as additional distinct tests. [Bridge test accounting](bridge/TEST_RESULTS.json) records earlier runs and the implementation correction; the component review records the independent setup-only failure before its successful invocation.

A separate read-only review of the smoke driver required the unit input schema to match the actual target task before either execution. That fix was made before preparation, along with driver and unit-code commitments. Independent verification of the final retained live outputs is recorded in [the live review](bridge_smoke/INDEPENDENT_LIVE_REVIEW.md); it does not rerun generators.

## Scope and remaining scientific work

- The connection proves retained mechanical execution linkage. It does not prove that arbitrary model code obeys its declared science, that evidence transfers correctly, that the Agent is the author, or that a host cannot rewrite all artifacts coherently.
- All contexts currently generate in the same canonical units, selected for the supported source-native feedback path. The downstream unit view does not provide general mixed-unit source feedback, assay harmonization, nonlinear transforms or derived non-HDL feedback.
- No production clinical unit factor was activated. The smoke uses explicitly invented units and values. A real lipid conversion needs its documented mapping in the clinical contract; unit conversion alone does not reconcile specimen or assay differences.
- The new bridge does not launch an LLM, guarantee beneficial revision, or release the full campaign. Actual clinical evidence/context contracts, finite per-case source schedules, statistical references, reference preparation and evaluation wiring still need completion.
- New-phase clinical case admission remains zero. The candidate screen is unchanged at 3/6 families and 3/12 originals. K02 remains qualified but not released, with disclosed prior study context and unresolved independent-validation counting.

The next scientific step is to instantiate this working connection with the admitted Agent-visible evidence and source/target assumptions, finish the corresponding statistical reference and evaluation contract, and meet the existing global case freeze before clinical construction. No revealed target is reopened, no quota is enlarged, and the CHNS scheduler remains paused.

The [implementation scope](../../docs/SOURCE_TARGET_BRIDGE_IMPLEMENTATION_SCOPE_2026-11-02.md) and [design v1](../../docs/METHOD_AND_EXPERIMENT_DESIGN_v1_2026-11-02.md) remain the guide. Old frozen harness modules, historical generators, the original campaign plan and prior source packets were not modified.
