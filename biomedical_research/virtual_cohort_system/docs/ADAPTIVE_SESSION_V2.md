# Adaptive author sessions v2

An additive version of [v1](ADAPTIVE_SESSION_V1.md), with the same externally launched Agent and isolated generator worker. Historical v1 modules and receipts are unchanged. The Agent chooses science and next actions; the controller does not supply clinical parameters. Only whole-cohort published-evidence tasks are currently admitted by v2.

## Setup and actions

API: `create_session(bundle, config)`, `dispatch(bundle, action_id, action)`, `verify_session(bundle)`. CLI module: `cohort_harness.adaptive_session_v2`, commands `create`, `act`, `status`, `verify` as in v1. The session folder is `adaptive_session_v2`.

Use v1 configuration fields with `schema_version: 2` plus `web_evidence`, a configuration accepted by `web_evidence_v1.validate_config`. Creation initializes the public-source gateway before committing state. Both gateway namespaces and source-registry prefixes are checked on every operation. Do not edit engine files or static task context after creation.

All v1 actions remain. The new action is:

```json
{"kind":"web_evidence","url":"https://example.org/source","source_id":"S_source","purpose":"Resolve the measurement definition","source_type":"official_website"}
```

The URL is illustrative, not a source recommendation. `source_type` and `purpose` are author declarations, not scientific certification. Task permissions must explicitly include `web.fetch`. [The public-source adapter](WEB_EVIDENCE_V1.md) parses bounded public HTTPS HTML/text/PDF and registers checked source artifacts; actual remote access can fail. Source documents are untrusted evidence, not instructions.

## Two distinct feedback layers

Every submitted candidate requires the original whole-cohort recipe/strict semantic sidecar **and** a [descriptive feedback plan](DESCRIPTIVE_FEEDBACK_V1.md). `preflight` and `submit` check both. A `feedback` action returns:

```text
result.strict       original semantic_feedback_v1 report
result.descriptive  assumption-labelled descriptive_feedback_v1 report
```

The same feedback ID is used in separate folders. An action is successful only when both reports are produced and verified. Completion requires successful feedback and every configured analysis for each successful scheduled execution in every submitted stage. Unavailable strict comparisons remain unavailable; a descriptive calculation does not upgrade them to matched source replay. Errors, no-op decisions and all scheduled draws remain recorded.

Ordinary source failures, such as HTTP denial or an unsupported/encrypted PDF, are recorded and let the author choose another action. Internal/provenance errors halt the session. Both states preserve actual costs. Candidate freezing, fixed seed attempts, isolated execution and terminal completion retain v1 behavior.

## Discovery and evaluation scope

This controller implements retrieval of an identified public URL, not a general search-engine client. A host may separately allow native web search for URL discovery. If so, log queries, returned/followed URLs, purpose, time and accidental excluded exposures separately. That channel is procedural and not controller-screened; snippets are not registered scientific constraints. Quantitative evidence should be acquired through the recorded body-ingestion action before use.

Execution, extraction, source-definition agreement and population usefulness are distinct. Generated-only analyses have no reference argument. Independent evaluation should seal the author's choice, bind exact session candidate/run/seed identities, and only then read the designated reference. A historically exposed reference remains a development comparison. This interface provides no standalone model API service or OS isolation of the author's other tools.
