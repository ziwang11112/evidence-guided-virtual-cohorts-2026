# F2 controller implementation and invocation

1 November 2026. Implemented integration, pending independent code review and a real F2 release. The existing `f2` directory is the future execution bundle; this work did not issue a release, approve a real candidate, run a biomedical generator or inspect clinical values. Only this controller directory and the new controller test file were authored.

The controller exposes `freeze_stage`, `run_stage` and `revision_feedback`, with the corresponding CLI below. It calls existing lifecycle/execution APIs, then **semantic_feedback_v1 preflight/collect/verify explicitly**, followed only by an approved optional conditional-feedback path. No legacy collector fallback, source replay, model authoring, calibration run or target evaluator is added. The legacy helper is consulted only to inventory implementation hashes used by strict v1.

## Fixed schedule and outputs

- Constructions `C1`, `C2`; stages `initial`, `revised`; seeds `1701`, `1702`, `1703`. Candidates are exactly `candidates/C1_initial`, etc. Execution/feedback IDs are exactly `C1_initial_s1701`, etc. There are at most 12 target-table slots.
- Task: whole-cohort, 3,000 rows, no observed columns/file; generated columns in order `age`, `female`, `bmi`, `glucose`, `hba1c`, plus the task identifier. Task budget allows one revision. Scientific units/support are bound by the reviewed task and fixed feedback semantics.
- Every execution is limited to 180 seconds, 1,024 MiB, 20,000,000 output bytes and 100,000 log bytes. The trusted runtime can be supplied through the existing execution adapter; no unsandboxed execution alternative is introduced.
- Before running the first seed, an exclusive stage request reserves all three slots. Ordinary failed runs and feedback errors remain in the complete round. No slot retry, new seed or replacement candidate is created. A process interruption leaves a non-resumable partial stage; it cannot be rerun or unlock a revision.
- A direct-row candidate uses the existing copy/validation route. Its three receipts reuse the same frozen table and explicitly receive **no independent resampling/Monte Carlo credit**. This is not represented as three stochastic draws.

Artifacts are written under `f2_controller/<construction>_<stage>/`, outside frozen candidates: freeze request/receipt binding, run reservation, per-seed attempt/result files, and one complete `feedback_round.json`. The round includes all three full strict/conditional reports or failure records. There is no averaging objective, ranking or target performance. A revised candidate must contain an exact byte copy named `revision_feedback.json`; it is independently reviewed and frozen along with the revised model. Its lifecycle parent is its own initial candidate. Failed initial seeds remain visible in a revision round; incomplete rounds cannot be used.

## Exact release contract

`F2_RELEASE.json` belongs inside the bundle. It must have exactly these fields:

```text
schema_version: 1
status: "released"
task_sha256: SHA256(task.json)
evidence_sha256: SHA256(the fixed candidate evidence.json)
controller_sha256: SHA256(chns_f2_controller.py)
engine_sha256: controller.engine_hashes()
protocol: {path: "PROTOCOL.md", sha256: ...}
analysis_plan: {path: "analysis_plan.json", sha256: ...}
builder_brief: {path: "BUILDER_BRIEF.md", sha256: ...}
feedback_policy: {path: "evidence/FEEDBACK_POLICY.json", sha256: ...}
schedule: {constructions: ["C1","C2"], stages: ["initial","revised"],
           seeds: [1701,1702,1703], max_target_tables: 12}
limits: {timeout_seconds: 180, memory_mb: 1024,
         output_bytes: 20000000, log_bytes: 100000}
independent_review: {path: "review/F2_RELEASE_REVIEW.json", sha256: ...}
```

All referenced paths are safe relative paths inside the bundle. The review JSON has exactly `schema_version:1`, `decision:"approved"`, nonempty `reviewer_id`, `coordinator_id`, `reviewed_utc`, `reason`, `independent:true`, and `approved_release`. The last field is the entire release object **excluding** its `independent_review` reference, avoiding a circular hash. Reviewer/coordinator IDs must differ. The controller does not create this approval. The reference evaluator's future code is not required for this study release; the prospective analysis-plan bytes are bound now, with evaluator validation/evaluation release remaining a separate gate.

`FEEDBACK_POLICY.json` has exactly `schema_version:1`, `strict_recipe_sha256`, `strict_semantics_sha256`, `required_assumptions` (full `{id,description}` records) and `conditional_interpretations` (null, or the exact permitted interpretation objects). Each candidate must preserve the released evidence and strict recipe/sidecar bytes and the required assumption descriptions. Selected conditional objects must equal approved policy objects exactly; the existing conditional module separately verifies the candidate-specific plan and independent interpretation approval. No template materializer is added: the reviewed packet supplies fixed templates, and the constructor supplies only permitted model/approval bindings.

## Independent candidate gate

Before `freeze-stage`, a new candidate must contain `candidate_review.json` with exactly:

```text
schema_version: 1; decision: "approved"; independent: true
reviewer_id; builder_id; reviewed_utc; reason
release_sha256: SHA256(F2_RELEASE.json)
candidate_files: {each candidate-relative artifact path: SHA256(bytes), ...}
declined_interpretations: [{id: permitted interpretation ID, reason: ...}, ...]
```

The file map includes every candidate artifact except `candidate_review.json`, the controller-authored `f2_stage_binding.json`, and lifecycle's `freeze.json`. The latter is already excluded by `lifecycle._files`. Reviewer and builder IDs must differ. With conditional feedback, builder identity must also match its approval plan. Every permitted proxy is either included unchanged or explicitly declined; no omitted proxy disappears silently. A decline can avoid the optional conditional API, while the fixed strict unavailable rows remain. The controller then adds its release/stage binding to the **new, unfrozen** candidate and calls ordinary lifecycle freeze. It never edits a frozen candidate.

## Invocation after release and candidate review

From the project root, substitute the actual bundle path for `BUNDLE`:

```powershell
python work/chns_admission_2026-11-01/f2/controller/chns_f2_controller.py freeze-stage --bundle BUNDLE --construction C1 --stage initial
python work/chns_admission_2026-11-01/f2/controller/chns_f2_controller.py run-stage --bundle BUNDLE --construction C1 --stage initial --runtime-json TRUSTED_RUNTIME_JSON
python work/chns_admission_2026-11-01/f2/controller/chns_f2_controller.py revision-feedback --bundle BUNDLE --construction C1
```

Return that entire verified round to C1 in one revision turn. If a revised/retained candidate is selected, copy the round bytes to its `revision_feedback.json`, complete independent candidate/interpretation review, then use `freeze-stage ... --stage revised --revision-json REVISION_JSON` and `run-stage ... --stage revised`. The revision JSON uses the existing lifecycle fields `kind` (`retain` or `revise`), `reason`, `addressed_findings`, `remaining_limitations`. Repeat the fixed schedule separately for C2. No real invocation has occurred in this work.

Protocol/evaluator files are custodian material, not builder inputs. Builder access uses the reviewed allowlist and procedural fresh-context separation. Neither this controller nor its hashes create host-level Agent isolation; existing WSL/bubblewrap isolates only actual generator processes. Approval identities/source truth are declarations checked procedurally, not cryptographically authenticated signatures. Deleting or coherently rewriting host records can defeat hash commitments.

## New checks and limits of verification

Only `tests/test_chns_f2_controller.py` was run. The first 10 checks passed; after actual hardening of round-summary, attempt and reservation verification and an additional summary-tampering check, **11 passed in 1.14 seconds**. These tests use invented metadata and mocked lifecycle/execution/feedback calls, not clinical rows or executable biomedical generators. They cover release gating, fixed routing/limits, failed-slot retention, twelve-slot/revision boundaries, immutable candidate/template meaning, declared proxy decline, direct-table replication disclosure, interruption/no retry and round tampering.

No old passed suite was rerun. Mock routing establishes the selected API calls and controller bookkeeping, not a new isolation test, a fully materialized real-candidate check or scientific utility. The real source templates, candidate-specific approvals, F2 release and later one-time reference evaluation remain pending their own independent gates.
