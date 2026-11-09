# Host-dispatched adaptive sessions v1

Implemented 9 November 2026 in `cohort_harness/adaptive_session_v1.py`. An externally launched scientific author chooses each next action. The controller actually dispatches literature retrieval, candidate freezing, isolated execution, strict semantic source feedback and host-approved generated-data analyses. It contains no model API client and does not select a scientific model, parameters, evidence query, procedural skill or revision for the author.

This is a new additive controller. Historical modules, sessions, clinical packets and results retain their original behavior. Fixed retrieval, output-route or revision choices in earlier ablation experiments are not restrictions on this controller. The author can retain a justified construction, change structure or parameters, or choose either a program or a directly supplied table under the existing contract.

## Host setup

Use a fresh bundle containing the existing `task.json`, matching `request.json` (schema version, purpose, analyses, task), approved `registry.json` and source files. The initial source packet is admitted by the host before session creation. Unfrozen candidate drafts may already exist. Existing frozen candidates or execution/feedback directories cannot be adopted. Enrichment/completion also require their declared observed input.

Creation also binds existing `AUTHOR_TASK.md`, `SETUP_NOTES.md`, `adapters.json` and every file under `input/` and `skills/`. Their bytes and inventory cannot change during a session. Author notes, draft candidates, gateway state and the append-only source registry use their separate lifecycle; they are not treated as static context. Place all intended fixed scientific context in these admitted namespaces before creation.

The host creates a config of this form; numbers here are resource choices, not scientific parameters:

```json
{
  "schema_version": 1,
  "limits": {"actions": 48, "candidates": 3, "executions": 9, "feedbacks": 9, "analyses": 9},
  "allowed_seeds": [9401, 9402, 9403],
  "runtime": {
    "backend": "wsl_bubblewrap", "distribution": "Ubuntu-24.04",
    "venv_root": "/home/zwang/.cache/evidence-cohort-runtime/m2/venv",
    "bwrap": "/home/zwang/.cache/evidence-cohort-runtime/m2/bubblewrap/usr/bin/bwrap"
  },
  "execution_limits": {"timeout_seconds": 45, "memory_mb": 1536, "output_bytes": 20000000, "log_bytes": 50000},
  "analysis_adapters": {
    "generated": {
      "path": "D:/absolute/reviewed/generated_analysis.py",
      "function": "analyze",
      "sha256": "REPLACE_WITH_ACTUAL_HASH",
      "dependencies": {"D:/absolute/reviewed/dependency.py": "REPLACE_WITH_ACTUAL_HASH"}
    }
  }
}
```

`runtime: null` permits direct-table validation but cannot run a program. Only the existing inspected runtime configuration is accepted; creation validates configuration, not live runtime availability. The host should check its runtime before a scientific session. Do not modify controller/adapter code after creation: their hashes are bound to the session.

Analysis adapters are host-reviewed Python files, identified by absolute path, entrypoint and hash. `dependencies` is optional; list every host-owned transitive source file that needs binding. The interface is `analyze(output_path, task_path, request_path) -> dict`, with JSON-finite output capped at 2 MiB. No target/reference path is supplied. The controller marks these results as generated-output analysis with `reference_role: none`, never source-population replay. An adapter's code and imports are trusted and run on the host; this interface is not a Python sandbox or proof that the code reads no other files.

## Author actions

The Python API is `create_session(bundle, config)`, `dispatch(bundle, action_id, action)` and `verify_session(bundle)`. The CLI accepts action JSON files:

```text
python -m cohort_harness.adaptive_session_v1 create --bundle BUNDLE --config CONFIG_JSON
python -m cohort_harness.adaptive_session_v1 act --bundle BUNDLE --action-id UNIQUE_ID --action ACTION_JSON
python -m cohort_harness.adaptive_session_v1 status --bundle BUNDLE
python -m cohort_harness.adaptive_session_v1 verify --bundle BUNDLE
```

Each row below is an action object. Names may be `initial` or `candidates/initial`. Candidate programs are never imported by the controller.

| Action | JSON fields in addition to `kind` |
|---|---|
| `literature` | `action`: `init`, `search`, `fetch`, `list-supplements` or `fetch-supplement`; the corresponding existing adapter arguments (`query`, `limit`, `cursor`, `pmcid`, `version`, `supplement_id`) |
| `preflight` | `candidate`; strict whole-cohort source-semantics declaration check before submission |
| `submit` | `candidate`; for later versions, `parent` and existing lifecycle `revision` object |
| `execute` | `candidate`, new `run_id`, scheduled `seed` |
| `feedback` | `candidate`, `run_id`, new `feedback_id` |
| `analysis` | `candidate`, `run_id`, allowlisted `adapter`, new `analysis_id` |
| `finish` | `final_candidate`, `reason`; `final_candidate: null` explicitly abandons the session |

For example:

```json
{"kind":"execute","candidate":"initial","run_id":"initial_s9401","seed":9401}
```

Whole-cohort `submit` always calls `semantic_feedback_v1.preflight` before freeze; `feedback` explicitly calls its strict preflight/collector without legacy fallback. Every later candidate extends the latest successfully submitted candidate. The existing lifecycle revision record has `kind` (`retain` or `revise`), `reason`, `addressed_findings` and `remaining_limitations`. A no-op is permitted; do not claim a model change when only records change.

Source feedback remains a **declared-source diagnostic contrast on task-population output**. It is not reconstruction of a different source population, proof of faithful source extraction or target validation. The author must retain source applicability, adjustment, measurement and uncertainty qualifications. No action accepts a target table or numerical target statistics as source replay. Registry additions after creation must arise through dispatched literature actions; original sources and registry prefixes remain bound. These checks do not establish the authenticity of a host-admitted packet against a malicious host.

The controller can freeze and execute enrichment/completion candidates, but v1 does not dispatch a source-feedback adapter for those modes. It reports that limitation rather than routing them to a whole-cohort collector. Additional estimators and source-population replay are not silently implemented by this session layer.

## Accounting, completion and failures

Each accepted action is reserved and charged before adapter dispatch. Failed attempts are not refunded. `preflight` charges an action; `submit` also charges a candidate attempt, even if the candidate contract fails. Literature queries/downloads/HTTP attempts retain the existing task-bound gateway accounting, including metadata fetch costs and failed network attempts. The session binds gateway state and audit bytes after each operation, so outside changes cannot reset usage unnoticed.

The fixed seed list is a schedule. A candidate/seed pair can be attempted once, including failed attempts. IDs cannot be reused. A completed `finish` requires every submitted stage to have attempted every scheduled seed and every successful execution to have strict semantic feedback (whole-cohort mode) plus every configured analysis adapter's report. The chosen final candidate must have a successful output. The author may inspect the first draw, but must preserve the rest of every submitted stage's schedule before successful closure. The author chooses whether a new stage is justified; no structural change is compulsory.

Explicit abandonment remains possible and terminal. Its result includes each stage's attempted, failed and unattempted seeds and available diagnostics. It cannot be reported as a completed scheduled comparison. Infrastructure failures stop the session; external host reports should retain the outstanding schedule. Ordinary network availability failures consume their real budget and return an error the author can respond to. Source rejection, unsupported content and exhausted acquisition allowance are also retained, not treated as successful evidence.

Malformed unfrozen candidates can be corrected after a charged contract error. Integrity failures, changed inputs/engines, missing execution infrastructure, unknown host failures and incomplete writes stop further work. There is no unsandboxed generator fallback, automatic retry, reset, refund or automatic recovery. Failed/timeout receipts are checked against the requested candidate, submitted freeze, seed, limits, complete request and trusted worker/launch identity, not merely against their own internally consistent hashes.

The session directory contains an immutable configuration, an append-only hashed reservation/result event chain, an atomic head checkpoint and separate actual action responses. An exclusive operation lock serializes operations and remains after an interrupted dirty write. Candidate versions remain frozen; execution/feedback/results live outside them. `status` and `verify` check commitments and recorded execution/source-feedback receipts without regenerating a cohort or rerunning the host analysis adapter. Hashes are procedural commitments, not signatures against someone rewriting the whole host record. Only the existing generated-program process has OS isolation; the author and trusted analysis adapters do not.

An action's `status: success` means that the operation completed, not that its scientific criteria passed. Inspect the contained feedback, not-computable checks, differences and analysis results. Source fit, rubric coverage and successful receipts are distinct from useful final scientific analyses.

## Validation

`tests/test_adaptive_session_v1.py` exercises actual invented direct rows through submission, execution validation, strict semantic feedback, host analysis and terminal completion. It also checks real literature dispatch with intercepted HTTP, persistent acquisition usage, meaningful no-op lineage, all-stage seed schedules, failed-attempt accounting, immutability, changed gateway/source/engine/adapter state, terminal refusal and failed-program trusted staging. Program-failure tests use a mocked backend and do not prove OS isolation. Tests contain no clinical data, real network retrieval, paid model call or target evaluation.
