# New-case runtime contract

This directory adds a procedural wrapper around the unchanged `cohort_harness/adaptive_session_v2.py` dated 9 November 2026. It is not the older adaptive-reference-pilot v2 file. The wrapper has no model API client. Actual fresh `collaboration.spawn_agent(..., fork_turns="none")` authors inherit the active host model; the host records dispatch IDs and available metadata, using null for unavailable model/snapshot/token fields. Hashes are integrity commitments, not authenticated signatures or Agent-wide filesystem isolation.

No clinical generation is authorized by these files alone. `start` requires `runtime/METHOD_FREEZE.json` with all four gates approved and current code, source-packet and protocol bindings. The root host owns this receipt. The reference evaluator must call `controller.verify_batch_seal()` before reading reference values for analysis/comparison; the earlier frozen custodian counts-only readiness read is separate. It receives the selected output paths/hashes and all five author outcomes. Reference paths never enter author configuration, research requests, source feedback or generated-analysis adapters.

## Host commands

Run from the project root with its existing Python environment. Set `$cli` to `work/next_case_validation_2026-11-09/runtime/cli.py`.

```powershell
python -B $cli bindings
python -B $cli start --author A01 --dispatch-record dispatch-A01.json
python -B $cli act --author A01 --id search01 --action search01.json
python -B $cli act --author A01 --id submit01 --action submit01.json --review review-initial.json
python -B $cli decision-bindings --author A01
python -B $cli select-seal --author A01 --decision final-decision.json --review final-review.json
python -B $cli batch-seal
python -B $cli verify-batch
```

`start` creates a fresh `sessions/A01` bundle. No existing session/candidate is adopted. `act` dispatches an actual native action, or one of the explicitly described extra lanes below. `select-seal` performs the native finish operation and hashes the full retained author bundle. A failure/abandonment has a null final candidate and remains one of the five slots. All successful outputs of a chosen candidate are selected; authors cannot pick a seed. All attempted seed slots and failures remain in the seal. The maximum is 30 attempted target-like executions, with at most 15 successful selected tables. Source-replay executions are separate.

An interrupted native action or hash-integrity failure may prevent verification and therefore blocks batch reveal. Do not delete/reset/retry it. A versioned, independently reviewed recovery decision is required; this wrapper does not silently manufacture a failed seal for unverifiable artifacts. A clean native `halted` state with intact receipts may be sealed as failure.

## Author interface and ABI

The scientific columns are `age,female,bmi,sbp,dbp`. The unchanged harness additionally requires the mechanical unique `row_id`; CSV order is `row_id,age,female,bmi,sbp,dbp`, exactly 3,000 complete rows. Age is 20–79 and female is 0/1. Other output bounds are not silently introduced. Dictionary eligibility and transport are described in the visible task. The host supplies the requested regressions, never their answers or a generator law.

Program ABI is `generate(observed, spec, seed)`, with `observed=None`. Only the original WSL/bubblewrap execution adapter may call it. A direct-table route remains allowed and is replayed as a fixed table; repeating it does not create stochastic uncertainty. `request.json` contains schema_version, task, purpose and analyses, as required by native v2. The sole generated-analysis adapter is `analysis_tools.analyze(output_path, task_path, request_path)`: it has no reference input and returns all three requested estimates and diagnostics. Adapter results are shown to the author.

Authors submit the original candidate contract plus strict `semantic_feedback_v1` and descriptive plans. Native `preflight` and `submit` validate both. A successful native `feedback` action collects both lanes; exact/non-computable semantic statuses are preserved. A descriptive target-context contrast never becomes exact source replay. Before submission, an independent review receipt binds every candidate file and checks provenance, schema, bounded mathematics, feedback definitions and no reference access. It cannot impose desired signs or numerical results. Before a second candidate is submitted, all three initial seeds must have been attempted and every successful one must have both feedback and generated analysis. There is at most one revision, and all stages remain visible.

## Retrieval and budgets

`literature` actions permit search, fetch, list-supplements and fetch-supplement through the existing gateway; `web_evidence` permits screened public HTTPS documents through the existing web adapter. Source-free rounds are normal. Two documents from one original study remain one scientific-source family; the independent review maps every used source ID to its original. Document-download counts and scientific-source counts are distinct.

There are at most 12 combined query requests (gateway metadata lookups also spend query allowance), 10 combined new downloads and 50 MiB of new original-document response bodies per author. Search/metadata responses and derived text copies are not original-source bytes; supplied curated packet copies are fixed inputs and do not count as new author downloads. The wrapper reads the gateway download HTTP audit and web response-byte state. Since the unchanged literature gateway lacks a cumulative-byte limiter, each new literature fetch reserves its 16 MiB response ceiling plus one sentinel byte; a web action reserves its 8 MiB ceiling plus one. Actual recorded bytes replace that reservation; unknown-size failed responses are charged conservatively. Retrieval can stop early when the remaining budget is smaller than a response ceiling. There is no automatic retry/refund after a failed attempt.

Native web discovery is permitted only with an external-search permit issued **before** the actual host search. Its action is `{"kind":"external_search","query":"...","tool":"actual host search tool name"}`. Then the host performs exactly that single query and uses `search-receipt --author A01 --id search01 --receipt ...` to record the actual tool-call ID, status and URLs. Each permit spends one of the same 12 queries even if the call fails or is not executed. No search snippets may become quantitative evidence; full documents must be ingested through the approved adapters. Direct unlogged browsing/downloads are outside the admitted method. This external-tool restriction is procedural, not enforced by an OS sandbox.

Optional whole-cohort source replay uses `source_preflight` and `source_replay` extra actions. Its candidate plan is reviewed before submit, with at most six total source executions per author and at most 10,000 rows per context. The frozen schedule and same generator/spec are checked by unchanged `whole_cohort_source_replay_v1`. Plan/seeds/context IDs are authored and frozen before use; target-task seeds are not reused by implication. No source replay is required when the necessary population/operator cannot be defended. An unsupported context remains unavailable, with an explanation in the final decision.

## Verification status

Only new wrapper wiring and analysis fixtures may be tested before the gate. No clean clinical replay, new isolated scientific execution or authoring session is implied. Existing core tests are not rerun. The earlier readiness note records read-only WSL/runtime availability; original isolation is neither weakened nor re-certified by this wrapper. All actual clinical executions remain pending admission and method freeze.
