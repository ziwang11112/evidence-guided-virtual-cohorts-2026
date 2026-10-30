# Recorded scientific Agent review

M12-C connects an externally launched scientific Agent, verified numerical source calibration, a recorded decision and a formal development candidate. The current calling environment launches the LLM. `scientific_loop.py` does not contain a model API client, perform literature retrieval or isolate the Agent's general tools.

## Responsibility and information flow

The scientific Agent chooses a generator and explains its assumptions from admitted evidence. The controller checks contracts, freezes the candidate and invokes the bounded numerical tool. The same Agent then receives the complete source diagnostics and chooses retention, revision, stopping or a specific evidence request. A favorable decision does not automatically certify scientific correctness.

M12-C's real LLM demonstration uses two invented study summaries and covariate populations. There is no supplied generator formula or target outcome. Initial construction is recorded separately with the prompt, original-input manifest, Agent response and pre-freeze candidate hashes. Post-calibration review is handled by the new module. This is a functional handoff across real LLM and statistical tools, not a benchmark of model quality.

## API and persistent state

Create the one fixed per-bundle controller with:

```python
create_loop(bundle, {"max_actions": 3, "max_promotions": 1})
request_review(bundle, action_id, "candidates/initial", calibration_session_id,
               exact_prompt, actor_description)
# The caller now launches the actual LLM using the recorded request.
record_decision(bundle, action_id, decision)
promote(bundle, action_id, "source_reviewed")  # only eligible retain_structure
verify_loop(bundle)
```

The decision has exactly `choice`, `rationale`, `evidence_ids`, `addressed_constraints` and `remaining_limits`. Choices are `retain_structure`, `revise_structure`, `stop` and `request_evidence`. References must resolve to the frozen evidence and calibration constraint IDs. Recording validates references and integrity; it cannot prove that the prose's scientific reasoning is correct.

Requests bind the original freeze, the source-calibration plan, result and selection, plus a manifest of the permitted source/candidate inputs. They are recorded before external dispatch. A response is bound to its request. The scientific-loop directory stores a task- and engine-bound configuration and an append-only event chain with a head checkpoint. Only one request or promotion can be pending. Existing IDs/configurations cannot reset the allowance, and a stop decision terminates this loop.

The action allowance counts recorded post-calibration review requests. It does not count initial construction, every LLM tool invocation or tokens. Numerical sessions/executions have their separate bundle-global calibration ledger. Promotion reservations count sibling promotions as well as enforcing the existing candidate lineage depth. These are local procedural/run controls, not protection against an administrator creating a different bundle.

## Candidate promotion

Promotion requires a `retain_structure` decision, an available feasible selected trial and feasible separately seeded source replay. It reserves a promotion before writing files. It copies the selected trial's generator and model specification byte-for-byte into the canonical `candidates/<name>` layout, binds the actual source feedback, and records a calibration-provenance sidecar and Agent decision.

The result is a **source-checked development candidate**, not a target release. A feasible score that missed the declared source-fit threshold remains explicitly failed in `checks.json`. Feasible replay means all statistics could be computed; it does not imply the replay score meets any scientific threshold. A target release still needs an admitted case, complete frozen output/analysis schedule and reserved real-outcome evaluation.

`retain_structure` describes the scientific decision. The v1 lifecycle's `retain`/`revise` flag describes program/specification bytes. Calibrated provenance changes the specification bytes even when every numerical parameter is unchanged, so this promotion normally has v1 kind `revise`. Reports must not reinterpret that flag as a new model or performance improvement.

Verification recalculates calibration, checks exact selected program/specification bytes, parent lineage, decision-derived revision annotations, feedback hashes and promotion artifacts. A failed/interrupted promotion remains reserved and blocks further work; automatic recovery is unsupported. Existing promotion sidecar namespaces cannot be overwritten by another promotion—prepare a new scientific submission when advancing beyond this slice.

## Implemented and remaining branches

The retain-and-promote path has both tests and a real LLM source-only demonstration. Revision/evidence-request/stop decisions can be recorded and validated; only stop currently changes the controller's terminal state. Automatic retrieval, autonomous structural editing and post-edit re-evaluation are not implemented by this adapter. Such work must be explicitly orchestrated, provenance-bound and budgeted before being claimed as an autonomous capability.

Do not measure progress by how often the Agent changes a model. A source-informed retention can be appropriate. Scientific usefulness is determined later by the analyses supported by generated data, including analyses not used in calibration and their behaviour against reserved real measurements.
