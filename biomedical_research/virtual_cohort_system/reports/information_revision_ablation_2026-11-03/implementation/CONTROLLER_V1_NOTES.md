# Information × revision controller v1

This is a new controller for the prospective six-construction study. It does not replace or edit the closed adaptive-reference pilot or any frozen harness module. Its scientific route is an author-written stochastic program, executed only through the existing isolated execution adapter.

## Profile and provider contract

Use `initialize(root, bundle, profile, evaluator, author_id=actual_author_id, dependencies=...)`. The external coordinator actually creates and contacts that author; `dispatch` and `handback` record those acts rather than performing them.

Required profile fields are `information_condition` (`L` or `R`), `required_diagnostic_ids`, and `required_analysis_ids`. The provider is called as `evaluate(bundle, candidate, run_id, profile_path)` and returns `diagnostics` and `analyses`, each with exactly the required ID coverage. `analysis_definitions`, if provided as a profile path, is snapshotted and hash-bound. Additional imported provider dependencies must be supplied to `initialize` for equivalent binding.

For L, `reference_summary` is prohibited, not merely ignored. The controller projects analysis output to generated-statistic fields `id`, `value`, and optional `status`, `unit`, `n`, `rank`; reference points, intervals, discrepancies, ratios, conclusion labels, free-form provider metadata and paths are omitted. Values must be finite numbers or null. Status must be `ok`, `success`, `computed`, `unavailable`, or `not_computable`. Counts/ranks must be nonnegative integers or null. The L provider must also avoid reading a reference independently; projection is defense in depth and is not a filesystem security boundary. The full retained analysis output key is `analysis_feedback`.

Both arms retain the same generated-only quality block: nonpositive `glucose` and `hba1c` counts, and `duplicate_measurement_rows`. These are strictly nonnegative integer primitives (booleans, strings, floats, mappings and negative values fail validation). Additional quality keys are omitted for both arms, preventing free-form nested metadata from leaking through the L allowlist. A supplied top-level generated sample size `n` is also retained for both arms and must be a nonnegative integer.

R requires `reference_summary`, which is snapshotted and bound. It retains the provider's declared-reference comparison fields. This is reference consistency, not independent validation or recovery of a known population truth.

Both conditions explicitly call `semantic_feedback_v1.preflight`, `collect_feedback`, and `verify_feedback`. `numeric_semantic_evidence_ids` defaults to an empty list. A main-task table cannot obtain a numerical source comparison unless that evidence ID is explicitly allowed; L requires this list to be empty. The permitted R use is an already supplied reference whose population/operator has been reviewed, not an automatic assertion that the target is a source-study population. External evidence and its uncertainty can still appear as approved source records with `calculation: null` and unavailable status.

## Actual boundaries

This version has **no source-context adaptation interface**. An alternate bundle or a trial labeled `source_context` is rejected before reservation/execution. The same policy applies to all six constructions. A new adapter would need prospective source-population contracts, identity units or reviewed measurement mappings, frozen-parent linkage, identical code and explicit specification changes; a context string alone cannot establish this. Accordingly the study may describe revision using allowed-information diagnostics, not quantitative external-source population replay.

Per session: one author, two author phases, at most one revision/retention decision, up to two initial trials, three initial deliveries, up to two revision trials, three final deliveries. Delivery seeds are 4101, 4102 and 4103; each delivery has 3,000 rows; trials have at most 3,000. Maximum attempts are ten, and failure consumes its attempt. There is no local fallback, automatic retry of a used delivery seed, or additional author. The study coordinator enforces the six-session/sixty-table total separately. Retrieval counts are inherited from each bound task (the planned task has two queries and one document).

Initial trial seeds are 4201 and 4202; revision trial seeds are 4301 and 4302. A different trial seed or repeated seed within the same phase is rejected before an attempt is reserved. A failed attempt still uses its seed and slot.

Trial executions must precede that phase's delivery. Initial feedback closes initial execution; final feedback closes final execution. Revision dispatch requires actual initial-feedback handback to the same author. Retention and revision both bind that initial feedback hash. Feedback checks code/task hashes, candidate freezes, execution receipts, generated-table hashes, and recomputed analysis values.

The common final evaluator is deliberately outside this controller's author-feedback API. The coordinator must wait until all six final versions are closed before invoking that evaluator. This module by itself does not enforce that global reveal gate, certify source extraction/applicability, provide host-adversary tamper resistance, or guarantee researcher/author isolation.

## Focused verification

`test_information_session_v1.py` uses mocked execution only: its output is a test marker, never a synthetic scientific cohort. Nine version-specific checks passed: L reference-sentinel removal, R comparison preservation, rejection of an L reference profile, the new seed/ten-attempt contract with phase closure and same-author feedback hashes, three mutation cases, rejection of target-as-source replay, and failure charging without fallback. No prior closed-controller tests were rerun.

The first invocation could not create fixtures in the pre-existing inaccessible system pytest directory; it yielded nine setup errors before test execution. A fresh explicit workspace test directory resolved the environment issue. The successful command was:

```powershell
& 'C:/Users/ziwan/AppData/Local/Programs/Python/Python312/python.exe' -m pytest work/information_revision_ablation_2026-11-03/implementation/test_information_session_v1.py -q --tb=short --basetemp 'D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcIA_controller_qa_v1'
```

Do not reuse that `--basetemp` path without inspection: pytest may clear an existing base directory. Keep the existing QA artifacts, or choose a new unused directory for newly justified tests. No scientific author was dispatched or data generated by this verification.

Following independent review, generated-quality parity and fixed trial seeds were implemented before any session initialization. A focused follow-up selected twelve affected/new cases (five unaffected cases were deselected): quality parity with nested reference sentinels, six invalid quality-count types, phase-specific seed and duplicate rejection, plus existing L/R filtering, budget/closure and failed-adapter cases. All twelve passed in 2.21 seconds using a new unused `evcIA_controller_qa_v2` directory. No old frozen-pilot tests were run.
