# Independent self-check and controller review

Status: PASS for prelaunch checker and controller review. All identified blocking issues were resolved before launch. Review used code and entirely invented software fixtures only. No target reference, raw NHANES files, actual candidate tables or target outcomes were accessed during this review. No engine/controller file was edited by this reviewer.

## Reviewed bytes

- cohort_harness/self_consistency.py: `60f8f8c398104df3c017e96f5d6c659953e6f634a6caa17c5de8711f646e97f7`
- tests/test_self_consistency.py: `67cc1eaf409a3ecd4fa8e6136ccc1a4ae4df4fa5de4179babc28a01340e8249b`
- docs/SELF_CONSISTENCY.md: `7b3526dd19caa458bc6b7a01a532b7f48feea8d789049399c9186ccebe0c448b`
- work/m16_direct_repair_2026-10-30/controller.py, final reviewed version: `aed12872e18a6e64919260471aee2a5c4634d8cef34d018fd251b1c91617aefc`

## Independent numerical work

`independent_self_check.py` constructs a separate six-row invented fixture. It does not import the author's test fixtures or internal checker helpers. Expected values use exact rational arithmetic (Fraction), direct mean/sample-variance/RMSE formulas, linear quantiles, independently constructed average ranks for ties, and exact Gaussian elimination for rank. The public checker entry point then produces the report for comparison.

All 477 arithmetic comparisons passed. Coverage includes overall, marginal and all Cartesian joint groups for location, scale, outcome, residual and standardized residual; empty groups and singleton groups; sample SD with n-1; quantiles; Pearson and tied-rank Spearman; unequal scale guides; strict greater-than tail thresholds; duplicate counts; constant predictors and collinear numeric design. Four of six declared joint groups are populated. The numeric design rank is independently 2. All input hashes remain unchanged. The invented nonzero residual mean remains computed with scientific validity not assessed; no equality-to-zero scientific pass criterion was applied.

Result: `INDEPENDENT_SELF_CHECK.json`. The module author's separate test suite was read but not rerun by this reviewer; the engine author reports 56 passing invented-fixture tests. The independent script is a separate numerical verification, not a claim of biomedical validation.

## Controller review and corrected findings

Initial review found source-check definitions were not yet enforced against the pre-authoring model plan. A subsequent review found that stripping the full table object allowed an auxiliary table to supply source diagnostics. Root corrected both before launch: all six non-table source-check fields must match the committed plan exactly; every computed/approximate table must be generated.csv with its current exact SHA-256 and agent_supplied_simulation origin. Not-computable checks require no table. These corrections preserve the intended chronology and tie both source and self diagnostics to the authored table.

Root also added terminal and intermediate-lineage guards and persistent CLI operational failure receipts. `controller_branch_check.py` verifies eight guard branches using a temporary invented filesystem and explicitly stubbed contract/lifecycle/execution adapters. It rejects changed source definitions, a substituted table, a stale table hash, post-terminal revision, post-terminal editing feedback, revision1 after a final commitment, and bypassing a committed revision1. An injected CLI diagnostic failure leaves a failure receipt. These are branch checks, not a complete controller integration run. Result: `CONTROLLER_BRANCH_CHECK.json`.

Static review confirms: scientific construction and evidence hashes precede the candidate generated.csv; frozen candidates are verified before feedback; original and current model diagnostics are retained for revised tables; parent feedback bytes are copied and hash-bound to the next candidate; retention checks preserve generated data/model/evidence/construction; feedback is outside the frozen candidate; reservation/report creation is exclusive; no target-reference path is read by the controller; no generator is executed in the direct-table feedback route. These are workflow/byte guarantees, not OS isolation or proof that an Agent never drafted values elsewhere.

## Resolved stop-action semantics

Review identified that accepting action=stop as a candidate while mapping it to lifecycle kind=revise would reject an unchanged scientific stop. Root resolved this before launch: stop is excluded from candidate precommit actions with an explicit separate-stop-record message. BUILDER_TASK.md requires stop_record.json to end an unsuccessful construction while preserving a valid initial table, and requires retain for an unchanged submitted final table. An independent temporary-fixture branch check confirms stop is rejected before writing any commitment.

The eight earlier branch checks bind controller c5abf126a49a2c8ec6a6ab99c05bb46493a74918acffc867ca8a12e09d391642. The reviewed follow-up change affects the action gate and its message; the final stop check and this final static read bind `aed12872e18a6e64919260471aee2a5c4634d8cef34d018fd251b1c91617aefc`. Result: CONTROLLER_FINAL_STOP_CHECK.json. No unresolved blocking finding remains.

## Scope limits

This review does not assess source extraction fidelity, scientific model adequacy, literature budgets in actual runs, literal authorship, or the future candidate chronology. Those require the scheduled builder/custody review. Hash and precommit guards do not establish model-unseen data. Target release remains locked and is not authorized by this report.
