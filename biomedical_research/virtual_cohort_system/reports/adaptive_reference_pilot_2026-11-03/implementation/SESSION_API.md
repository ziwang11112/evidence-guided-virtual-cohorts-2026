# Adaptive session API

`adaptive_session.py` wraps the existing lifecycle, isolated WSL execution, and
`semantic_feedback_v1` engines. It imports no candidate program on the host.
Scientific structure and parameters come from the externally dispatched author.
The current reference evaluator is supplied separately; no old task IDs or old
controllers are embedded in this wrapper.

From the harness directory, use `python <implementation>/adaptive_session.py`.
Every command requires `--root D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcAR`.

1. `init --bundle <root>/b --profile <unit>/profile.json --evaluator <implementation>/reference_evaluation.py --author-id /root/adaptive_scientific_author` creates a new session. It infers coverage from `required_diagnostic_ids` and `required_analysis_ids`. Profile budgets must equal the session and task budgets. Add `--dependency <file>` for additional immutable implementation/input snapshots.
2. `probe` records a read-only runtime inspection. Actual executions inspect the runtime again. Unavailable WSL execution never falls back to local Python.
3. After the actual external dispatch, `dispatch --phase initial --external-task-id /root/adaptive_scientific_author` records it. The real dispatch is the coordinator's action, not a subprocess or API call hidden in this module.
4. `freeze --candidate <name> --stage trial|initial|final` invokes semantic preflight, lifecycle validation and exclusive freeze. Candidates contain `generator.py`, `model_spec.json`, `evidence.json`, `decision.md`, `checks.json`, `whole_cohort_feedback.json` and `source_semantics_v1.json`, plus bound supporting files. The coordinator's `attach_feedback.py` supplies the reference checks before freezing. `checks.scope=source_only` is legacy representation here: CHNS is a declared developmental input source, not external-only validation.
5. Optional `trial --candidate <name> --seed <integer> --phase initial|revision` uses the same isolated adapter and consumes one of that phase's two slots. `--bundle <fresh-bundle-under-root> --context <label>` supports chosen source-context trials under the same accounting. This pilot caps every trial at 3,000 rows. `trial-feedback --run-id <run>` returns the retained numerical result without consuming a scientific review round.
6. `deliver --stage initial` attempts exactly seeds 3101, 3102 and 3103, 3,000 rows each. All attempts count, including failures. A subsequent invocation can process only previously unattempted slots. There are no hidden retries or substituted seeds.
7. `feedback --stage initial` writes execution-linked aggregate feedback. The injected evaluator must implement `evaluate(bundle, candidate, run_id, profile)` and return complete `diagnostics` and `analyses` lists or ID-keyed objects. Successful outputs are bound to receipts, output bytes, freeze receipts, semantic reports, profile and actual implementation snapshots. Failed attempts remain visible with unavailable statistics. All 27 diagnostics and all 3 analyses are required for this profile.
8. Actually send that file to the same author, then record `handback --stage initial --external-task-id /root/adaptive_scientific_author`. Record `dispatch --phase revision --external-task-id /root/adaptive_scientific_author` when the same author resumes. `decision --decision-json <file>` records the author's one retention/revision choice; its fields are `reason`, `kind` (`retain` or `revise`), `addressed_findings` and `remaining_limitations`.
9. Optional revision trials share the remaining phase budget. Freeze the final candidate, then `deliver --stage final`, `feedback --stage final` and `verify` complete the loop. Final freeze binds the initial freeze as its parent. Retention still receives the same delivery seeds; identical retained outputs are not independent scientific constructions.

`status` reports actual attempt/review/dispatch counts. `retrieval --retrieval-kind query|document --artifact-or-query <description> --outcome <result>` records the actual author retrieval against task limits; the coordinator must record every attempted query/document, including failures. Static reads of the supplied package are not new retrieval requests.

Each operation writes an exclusive event with a previous-file hash. Attempt events
precede execution; failures and unresolved interrupted attempts therefore retain
their budget charge. Frozen candidate files stay in their own candidate directory.
The wrapper refuses mutation outside the new root and refuses initialization over
old freezes/receipts. Hashes detect stale/mutated artifacts; they are not signatures
against a host user rewriting the entire record. An interrupted operation lock is
preserved for inspection rather than automatically rerunning a reserved attempt.

The evaluator reads synthetic output plus approved aggregate reference inputs.
Reference sampling intervals remain separate from variation over the three
conditional generation draws. Exposed-reference agreement is developmental
consistency, not independent validation or an equivalence claim.

Controller validation: 10 focused tests passed. All execution and semantic calls
in these tests are mocked and no scientific rows are generated. The live read-only
runtime probe succeeded with Python 3.12.3, NumPy 2.4.5 and pandas 3.0.3.
