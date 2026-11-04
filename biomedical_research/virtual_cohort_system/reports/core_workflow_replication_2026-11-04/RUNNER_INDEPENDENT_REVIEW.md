# Independent runner review and bounded corrections

Date: 2026-11-04. Scope: the new four-author runner, its focused tests, generated-only provider routes and semantic-feedback entrypoints. No candidate generator, biomedical row table, target report or reference evaluation was executed/read. The reviewer was authorized to fix concrete runner defects during this review; the root controller will independently inspect those edits before any scientific freeze.

**Result: the bounded runner control review passes after the corrections below.** This is not a source/model review or full evaluator/numerical audit. No actual author session or `CONTROL.json` was created by this review. At the final inspection, the real batch `CONTROL.json` did not yet exist. Candidate execution still requires the root's diff/evaluator review and each candidate's independent source, finite-moment and specification/code review.

## Defects found and corrected

1. **Direct-row contract mismatch.** The runner rejected `generated.csv`, although the author contract and lifecycle permit either a program or directly authored rows. Removed the extra rejection. Freeze/result records now retain the route. Successful execution records retain `generator_executed` and a seed role. Direct rows use `fixed_table_validation_slot`: the three scheduled delivery slots validate/copy the same fixed authored table, not three independent draws. Program inputs use `program_sampling_input_independence_not_certified`; an accepted seed is not itself proof that the program uses independent randomness. The evaluator/report must carry this distinction and report unique table hashes. Direct-row validation attempts still consume the unchanged attempt budget.

2. **Incomplete control commitment.** Added `RUNTIME_PREFLIGHT.json`, `evaluator.py` and `ENDPOINT_CONTRACT.json` as mandatory `control_files` inputs before `CONTROL.json` can be created. Existing protocol, harness, screened literature gateway, profiles, providers and declared import dependencies remain included. A missing required file now prevents initialization; later changes invalidate the control commitment.

3. **Unverifiable receipt prevented terminal closure.** Previously `_run` bound an execution receipt, then verification could fail; subsequent session verification repeatedly rejected that receipt, including when attempting terminal abandonment. The corrected path retains the receipt's exact hash as `unverified_receipt`, records the exact verification exception and the adapter's originally reported status/error, and sets verified `receipt` and valid `table` to null. Session verification checks the preserved untrusted receipt's bytes without reclassifying it as a valid execution. The charged slot cannot be retried, but terminal failure and global closure remain possible. No unverified output contributes a valid analysis table.

4. **Required trial stages could be skipped.** Final decisions now require an initial trial attempt with resolved result; if a revised candidate was frozen, its revision trial must likewise resolve before either the original or revised candidate can be selected. Successful trials require bound feedback. Zero trials can end only in terminal abandonment, not a completed workflow. One initial family, at most one direct revision, and three final attempts only after final selection remain enforced.

## Other inspected controls

- Acquisition is committed when the first freeze operation initializes the session, before the candidate freeze is attempted. The manifest covers existing bundle root files and the complete `sources`, `gateway` and `input` trees. Later gateway/source changes fail verification; working drafts outside those frozen inputs may continue. Because initialization precedes pre-freeze validation, even a failed first freeze call closes acquisition. The controller should call it only after source/proposal review is complete; it must not retry acquisition to repair an already initialized session.
- Attempts are reserved before execution, failures remain charged, execution directories must belong to reservations, and each author has at most five attempts. Frozen candidates, decisions, reviews, feedback, verified receipts and valid tables are hash-bound. Every author must terminally close before the batch gate opens, including terminal failures without rows. Global physical attempts cannot exceed twenty; twelve final slots remain scheduled even if some never produce deliverables.
- `semantic_feedback_v1.preflight` and `collect_feedback` are invoked explicitly, without legacy collection fallback. The semantic layer binds every check to its evidence locator, units, operator, adjustment/selection definition and uncertainty role. Computable scalar discrepancies are raw, qualified comparisons on generated target-population rows; unavailable definitions remain unavailable. Neither scalar agreement nor semantic matching establishes authentic extraction, transport validity or source-population replay. Those source judgments remain with the independent source review.
- A source-feedback or generated-statistics failure is recorded separately and does not discard a previously verified successful table. The decision must bind every actual trial-feedback report, including error reports.
- Static inspection confirmed that CHNS generated statistics call the pinned analysis implementation with `reference=False`; ENSANUT uses its fixed engine and exact eight-cell quota gate. The new wrapper calls these generated-only functions, bypassing only obsolete E0/E1 profile labels. The runner itself has no target reader or model launcher. Information separation remains procedural rather than OS isolation of Agent tools.

## Verification performed

Ran the ten existing mocked controller tests plus eight focused regression cases: **18 passed**, on the final runner bytes listed below. The new cases exercise direct-row accounting; invalid-receipt preservation, non-retry and terminal/global closure; later mutation of an untrusted receipt; mandatory initial/revision trials; and runtime/evaluator/endpoint control changes. Fixtures use mocked execution and empty byte artifacts only; no scientific rows or candidate code are produced/executed.

Two earlier invocations stopped during pytest temporary-directory setup (Windows default-temp permission, then a missing custom base parent). No test body ran in those invocations. A unique short directory within the workspace resolved the setup issue. The final run completed in 3.47 seconds. These are software-control checks, not empirical or clinical replications.

## Reviewed identities

| Artifact | SHA-256 |
|---|---|
| `runner.py` | `1930d9ae4d7c8ced8dfd5c0b139e5ad70c7ba28d0cbdbbcd5db629109c906dee` |
| `test_runner.py` | `bcfb5d03b29217b07cb3d29cdd8f809778d1cf64afd7fb9ddc8f9f94925a96b7` |
| `test_runner_independent_review.py` | `debfd8978ce3083b703879a8562ddc6e1ea039a87a78be56eab4e2182a1349b0` |
| `PROTOCOL.json` | `9f2589e1e5b51218d50d55698f300a412b45b159de2ed0ff9a1937d3efd08206` |
| `RUNTIME_PREFLIGHT.json` | `9512cf236757184bb746a35b54cd88e10596f9e274ebb7fa88a8b85c7bd5a2e3` |
| `semantic_feedback_v1.py` | `9599e57e1e77f43fd34c249c420e1ef37da755abc13530a6f1a25a215b3393b7` |

The evaluator and endpoint contract were also observed and required as control inputs: `evaluator.py` hash `098d7049a05b420b7ae798901fcc7ec344367fb8b0ddd11bc8f2665f778f1096`; `ENDPOINT_CONTRACT.json` hash `b35b3a681b716eeb258ed56234e5ad694a01e30ceb3243fb9f7b7bfa6f73fdbf`. Those are review-time metadata snapshots, not approval of their full implementation. The root owns any remaining evaluator changes and review before creating `CONTROL.json`. No target file was opened to obtain these identities.
