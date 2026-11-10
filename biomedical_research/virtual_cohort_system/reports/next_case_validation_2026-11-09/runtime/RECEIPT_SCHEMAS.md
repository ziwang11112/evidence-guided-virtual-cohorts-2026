# Host receipt schemas

These are truthful host records, not signatures or evidence that a tool was called. They must refer to actual author/reviewer dispatches. Unknown metadata is null; do not invent a model snapshot, token count or reviewer identity. The controller rejects self-review, incomplete gates and changed candidate bytes. Root retains access control procedurally.

## Method freeze, host only

Place `METHOD_FREEZE.json` in this runtime directory only after admission/source sufficiency and independent implementation checks. Required fields:

```json
{
  "kind":"pns_bp_method_freeze",
  "status":"approved",
  "reviewed_by":"actual root/review identity",
  "gates":{"case_admission":true,"source_adequacy":true,"implementation_review":true,"method_freeze":true},
  "files":{"project-relative file from cli bindings":"sha256"},
  "source_packet":{"path":"absolute new-case packet directory","files":{"sources/original.pdf":"sha256","skills/SKILL.md":"sha256","input/source_admission.md":"sha256"}},
  "source_registry":[{"source_id":"original-id","path":"sources/original.pdf","sha256":"sha256","origin":"curator","screening":"approved"}],
  "source_families":{"original-study-id":["original-id"]}
}
```

The exact `files` mapping is `cli.py bindings`, including native core, optional replay, wrapper, analysis, evaluator, independent recomputation, visible task and protocol. The packet must be inside the new-case directory; it may contain only `sources/`, `skills/` and `input/` paths. Include vetted interface documentation under `input/` and the authoring skill plus its referenced schema documentation under `skills/`. Files are copied before native session creation; static context cannot later grow. Additional retrieved evidence is appended only through gateway actions.

## Actual author dispatch

```json
{
  "author_id":"A01","agent_id":"actual collaboration ID",
  "fresh_context":true,"fork_turns":"none","model_policy":"inherit",
  "model_metadata":{"requested_model":null,"returned_model":null,"provider":null,"model_snapshot":null,"reasoning_effort":null,"temperature":null,"token_usage":null},
  "prompt_sha256":"sha256 of runtime/AUTHOR_TASK.md",
  "recorded_by":"actual host identity"
}
```

The host actually dispatches the fresh author and supplies this record before `start`; the initial dispatch may instruct the author to wait for its bundle. The author prompt is the runtime `AUTHOR_TASK.md`, based on the root template and appended CLI contract. Model metadata records what the host actually exposes, not a guessed API configuration.

## Independent candidate review

`act --review` for submit accepts exactly these fields:

```json
{
  "kind":"pns_bp_candidate_review","author_id":"A01","candidate":"candidates/initial",
  "reviewer_id":"actual independent reviewer ID","status":"approved",
  "candidate_files":{"model_spec.json":"sha256","evidence.json":"sha256","decision.md":"sha256","checks.json":"sha256","generator.py":"sha256","other required plan file":"sha256"},
  "checks":{"no_reference_access":true,"parameter_provenance":true,"bounded_behavior":true,"schema":true,"feedback_semantics":true,"no_desired_sign_requirement":true},
  "blocking_findings":[],"source_adequacy":true,
  "source_families":{"one original study":["source-id-for-main","source-id-for-supplement"]},
  "source_replay_approved":false
}
```

`candidate_files` is the full recursive candidate inventory excluding only generated `freeze.json`, not this illustrative file list. Each used evidence source ID must occur once in the family mapping, and must already be registered. Reviewers check that multiple reports/documents from one original are grouped correctly; this is not inferred from download count. Set optional replay approval true only after context/measurement/operator review. Revision metadata follows the existing native `submit` schema (`parent` plus the original lifecycle revision object).

## Final author decision and final review

The decision has exactly `author_id`, `final_candidate` (candidate path or null), nonempty `reason`, `source_feedback_used`, `generated_analysis_used`, and nonempty `optional_source_replay_disposition`. The two `*_used` fields must equal `cli.py decision-bindings --author A01`: all successful strict/descriptive feedback and optional source replay reports, and all generated-analysis result receipts. Acknowledging a report does not claim it justified a change. The decision is authored before reference reveal.

The final reviewer receipt has exactly:

```json
{"kind":"pns_bp_final_review","author_id":"A01","reviewer_id":"actual independent ID","decision_sha256":"sha256 of exact decision file","status":"approved","blocking_findings":[],"complete_disposition":true,"no_reference_access":true}
```

## Extra action schemas

```json
{"kind":"source_preflight","candidate":"candidates/initial"}
{"kind":"source_replay","candidate":"candidates/initial","replay_id":"source01","context_id":"author-declared-context","seed":271}
{"kind":"external_search","query":"author-chosen query","tool":"actual tool name"}
```

After an external search permit, the search receipt has exactly `query`, `tool`, `status` (completed/failed/not_executed), `result_urls` (list), `host_tool_call_id`, and `notes`. A completed or failed call must have its actual tool-call ID. Do not perform an additional unrecorded query or source download under one permit.
