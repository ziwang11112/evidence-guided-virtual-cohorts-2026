# Independent evaluation-controller guard review

**PASS for the bounded static recheck of the prior guard corrections. No remaining code blocker was found in that scope.** This report does not authorize target evaluation and does not certify completed source feedback, final freezes or any concrete evaluation schedule. Those prerequisites remain to be supplied and reviewed before root issues the separate evaluation release.

Reviewed on 2026-10-31. The reviewer read the controller, guard tests, interface, relevant existing harness verification code and nonprivate construction/source-bridge metadata. No controller, generator or engine was imported or executed. No test suite was rerun. No private, raw, reference or generated table was opened or hashed; no candidate scientific files were inspected. Only this new review file was written.

## Prior corrections

- **PASS: direct-row and recursive-parent access boundary.** Before any recursive `lifecycle.verify_candidate` call, `preflight_freezes` checks all listed builders' two stages, their bound freeze hashes, actual program route and absence of the direct `generated.csv` route. Initial candidates require index 0 and no parent; final candidates require index 1 and the exact bound initial parent path/hash. The public task and bundle task hashes agree and the task is whole-cohort. The reused harness therefore follows the inspected program path and refuses an observed table. It validates the program by AST rather than importing it.
- **PASS: successful execution artifact boundary.** `receipt_metadata` requires the exact `SUCCESS_FILES` set and matches it to actual directory entries. It binds and checks every successful artifact except generated CSV bytes in this phase. The generated CSV hash is recorded without opening the table. Staged task/model/program hashes must equal frozen commitments; request seed/limits, fixed runtime, launch command, worker hash, successful process and completed worker report are checked. Failed/timeout receipts return before any output/log traversal.
- **PASS: distinct physical bundles.** The controller checks both distinct bundle names and resolved, case-normalized physical identities. Its path checks reject traversal, Windows devices and symbolic links/junctions. These checks are consistent with the existing harness's path rules.

## Remaining controller checks

- Root authorization requires the evaluation schema, approved root issuer, explicit `effects_authorized: true` and fixed once-only purpose before binding access. The controller then verifies eight fixed document bindings, the full current harness Python-file set, ready preparation receipt/release linkage and reference output hash. This review did not inspect actual reference counts.
- Every listed construction must have exactly initial/final at seeds 18203, 18211 and 18223. Initial and final candidate freeze/lineage verification is complete before target output verification. Retained finals must preserve generator/model/evidence, external task/source commitments and registry snapshot, and reuse the same-seed initial execution receipt/output/status. A retained final cannot spend another draw through this interface.
- The fixed results directory must be absent. It is created exclusively, followed by an attempt receipt, before the first generated-cohort verification. Existing results, including a failed attempt's directory, block another invocation. There is no force, seed override, generation, source-feedback or automatic retry path.
- Existing `execution.verify_execution` is called only after the gate and attempt marker for unique successful runs. Metadata is checked again before the prepared reference is opened. The reference bytes must match the release/preparation receipt. The same bound engine handles reference and generated inputs, with fixed 399 stability attempts and seed 18301 and the separate exact generated cell quotas.
- Failed/timeout slots stay in the complete schedule with null estimates. Identical retained output contents are analyzed once while retaining all stage/seed labels. Every consumed byte commitment is rechecked before exclusive aggregate output writes. Post-attempt failures preserve a failure receipt and are not retried automatically.
- Saved results contain aggregate estimates, stability accounting, schedule statuses and hashes, not participant identifiers, example rows or residual vectors. The controller writes only under `analysis/results` and has no path that sends diagnostics to a builder or resumes a scientific generator. Builder access separation remains procedural in the shared host workspace, consistent with the executor's stated `agent_isolation: not_provided` scope.

## Test evidence and limits

The inspected interface records **13 of 13 guard tests passing in 0.053 seconds**, and its controller/test hashes match the current bytes below. The tests include explicit regression coverage for all-builders program-route/parent preflight and the exact artifact whitelist, generated-byte refusal during successful metadata verification, failure-receipt early return, inert import/help, schedule/retention checks and prior-results refusal. This reviewer inspected those tests but did not execute them or claim an independent end-to-end run.

The reviewed controller is a target-evaluation wrapper, not a complete scientific-process auditor. It binds approved source inputs through each candidate freeze, but **does not itself require or validate the two source-context execution/feedback reports, their seed/budget history or the actual source-only feedback shown to each builder**. `lifecycle.verify_candidate` checks `checks.json` structure and listed artifact hashes; that is not proof that source feedback occurred or that every required report was listed. Likewise, the wrapper can verify the full grid for one or two builders named by root but cannot discover a construction omitted from the root release. These are material procedural limits, not regressions in the two corrected access guards.

Accordingly, before issuing any `EVALUATION_RELEASE.json`, root must independently verify the complete construction set, all required source-context receipts and feedback/decision provenance, any revision/retention budgets and every final freeze, preserving the relevant hashes in its release/audit record. The construction release currently delegates later source execution and explicitly reserves target effects for a separate release. No `EXECUTION_RELEASE.json` or `EVALUATION_RELEASE.json` was present when this review checked the case's top-level metadata. This PASS must not be read as satisfaction of those future scientific release prerequisites.

Hash checks are local consistency controls under the trusted root process. They are not signatures, host access controls or protection against coordinated file/receipt rewriting or hostile concurrent mutation. The inspected implementation does not claim otherwise.

## Reviewed artifact hashes

Paths are relative to R, except `PROJECT/`, which denotes R's parent project's `virtual_cohort_system` directory.

| Artifact | SHA-256 |
|---|---|
| `analysis/run_evaluation.py` | `a792b9380751ef6dcd6419c51e99ede902d5dc9694f2c5b39bfcaa2fae990005` |
| `analysis/test_run_evaluation_guards.py` | `c5168b2218031652123f837f97bf9c79aa087055ba0de64744051784e170f93e` |
| `analysis/EVALUATION_INTERFACE.md` | `a05dff8c94372a4be82e8ecd20472f63b0c544ecd1a69d87731a01712eda378e` |
| `analysis/analytical_engine.py` | `1799c017b60f8fd3a9af409a524d3ebd9e54c81016e52da760aeafaefe03289d` |
| `CONSTRUCTION_RELEASE.json` | `51085460dedde3da4da34f1138aba72574b6a76b571ede90bc003edba653e46e` |
| `method/SOURCE_CONTEXT_SCHEMA.md` | `c84f2d379da351406c534b3c9fc31aaa948614b00ed1cb8a9e69d20ac6e8d1a6` |
| `method/SOURCE_CONTEXT_READINESS.md` | `43454701158c5d20f56f20e549ae3b3c985432fb2f9ba600bf2e055ddf7b48d4` |
| `PROJECT/cohort_harness/lifecycle.py` | `01688ffce3972053bab631c19e1f7a7bb941c53af1a5a658dfff0ecad401fee4` |
| `PROJECT/cohort_harness/execution.py` | `194a471f61e119dae9f8069dc976e070988545eb2e2ccbff84305cc84ddb238d` |
| `PROJECT/cohort_harness/__init__.py` | `403f30f780b1b018edec1cafa6a6a3c882464a15e60fd4bdb76310a2fe5c7c73` |
