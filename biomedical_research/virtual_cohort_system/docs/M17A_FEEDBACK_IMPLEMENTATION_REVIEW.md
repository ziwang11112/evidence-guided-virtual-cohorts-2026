# M17-A whole-cohort feedback: independent implementation review

Date: 2026-10-31. Decision: **PASS for the bounded artificial-data execution described in the M17-A plan.** No blocking implementation defect was identified in this review.

This review inspected the new collector/verifier, fixture preparation code, focused tests, interface documentation and the existing candidate/execution/statistic functions they call. It did not edit implementation files, execute a generator, rerun the test suite, read patient data or inspect closed target outcomes. Actual isolated execution and independent arithmetic on its output are separate checks for the controller.

## Reviewed files and hashes

SHA-256 hashes bind the reviewed versions:

| File | SHA-256 |
|---|---|
| `cohort_harness/whole_cohort_feedback.py` | `9fa53322c642307160ac5e588fcabf64f2e8c84e1c67eb02eacdfde3d2ca3605` |
| `tests/test_whole_cohort_feedback.py` | `3081f82d3112fd8b2ff5c3c6b239ec78612fd8e509d4ffc3f83dcf218bffb216` |
| `examples/m17a_whole_cohort.py` | `909467e57dc5d27d1b3317e09f48898d6c60106642cae10cf713bd55bbc3509b` |
| `docs/WHOLE_COHORT_FEEDBACK.md` | `0d1dd830ecd3cf9e1221f9d501839884b63e0a1f00788b4c393ca95793faa65c` |

## Boundary findings

| Question | Reviewed behavior | Finding |
|---|---|---|
| Is the feedback tied to the requested candidate? | `_compute` verifies the candidate and execution, requires the execution candidate path and route to match, and requires success | Pass |
| Can a caller substitute an arbitrary table? | The only table path is the verified run's `output/generated.csv`; the interface has no comparison-CSV argument | Pass |
| Does whole-cohort mode use observed participant input? | Existing freeze verification rejects `observed.csv` and observed-column roles; the collector rechecks mode and absence of the canonical observed file | Pass within the declared bundle contract |
| Is the recipe frozen? | Candidate verification binds the complete candidate file set, including `whole_cohort_feedback.json`; later recipe changes invalidate verification | Pass |
| Are statistics and evidence aligned? | The shared metadata validator checks evidence IDs, kind/unit, variable/adjustment relationships and explicit approximation assumptions; the statistical engine validates operator fields | Pass with the existing declared-approximation semantics |
| Are unavailable checks retained? | Declared `not_computable` checks retain their reason; runtime `NotComputable` results retain the original declared status and a computation reason | Pass |
| Can feedback overwrite the candidate or an earlier report? | New reports are written outside the candidate, and existing feedback IDs are rejected | Pass |
| Does verification check more than a success flag? | It recomputes statistics from verified execution output, compares complete report content, checks hashes and code/runtime identities, and rejects extra feedback files | Pass |
| Are direct output and code execution distinguished? | The report retains the execution route and execution flag; Agent authorship remains unverified and scientific validity unassessed | Pass |
| Are commands accurately documented? | New `collect`/`verify` parser and documented core `validate`/`freeze` commands match their arguments | Pass |

The direct-route tests check known arithmetic independently of the collection result: mean, sample SD and an adjusted regression coefficient. The mocked program test checks no-observed staging, but cannot establish physical isolation. The implementation's scope labels and documentation preserve that distinction.

## Test evidence and review limits

The implementation agent reports **33 focused tests passed in 5.35 seconds**. The initial run had 32 passes and one failure in an error-message expectation; the implementation had correctly rejected the extra operator field. The expectation was corrected before the reported passing run. This reviewer inspected the test code but did not independently execute those tests.

The inspected suite covers wrong mode, added observed input, observed-column roles, wrong candidate, failed execution, malformed metadata, undefined statistics, report/output/recipe tampering, path/ID rejection, no overwrite and CLI success round trips. The CLI error branch catches the relevant validation and filesystem exceptions and returns status 2 with a JSON error. A separate error-path assertion would be a useful small addition if that interface changes later, but it is not a blocker for the present bounded fixture.

## Scientific and operational scope

- A verified output link establishes which retained execution table was analyzed. It does not establish source-population equivalence, measurement equivalence or scientific usefulness.
- The new recipe names the actual executed population and supports identity measurement only. It does not recreate several study populations or implement cross-study transport.
- The canonical no-observed-table rule cannot semantically certify that every admitted source document lacks individual records. A real evidence-only study still needs an input-packet review.
- Verification assumes retained artifacts and the stated code/runtime environment. Hashes are not signatures against an actor who can rewrite the entire record, and the creation timestamp is not externally attested.
- The fixture's supplied program and coefficients are invented engineering code, not an Agent's scientific construction. It generates two continuous variables (`x`, `y`) and a binary `group` variable.
- No actual WSL/bubblewrap result or new biological performance is claimed by this review. The controller should inspect that run's status and independently recompute its five reported statistics before reporting execution success.

The only minor documentation issue noted during review was the plan's phrase “two-variable population,” while the prepared fixture has two continuous variables plus a group indicator. This was reported to the root for clarification and does not change the implemented task.
