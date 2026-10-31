# Source-only whole-cohort calibration adapter

`run_source_calibration.py` is a case-local execution adapter. It reuses
`cohort_harness.calibration._search` and the append-only
`cohort_harness.calibration_budget` ledger. The existing `run_calibration`
entry point is not applicable to this case: it dispatches the older
`source_replay_v2` enrichment route. This adapter instead calls the existing
whole-cohort bridge's prepare, execute and verify functions for every attempt.
No old module is changed.

## Fixed contract

- Exactly two source contexts, each with 6,000 generated rows, and 20 fixed
  `(context_id, check_id)` pairs. The parent development context is never run.
- Fit seed `[19101]` in each source context; at most 40 proposals per frozen
  structure, including the unchanged baseline as trial zero.
- Deterministic bounded coordinate search; only explicitly named finite
  top-level scalar parameters may vary. Generator, sources, assumptions,
  scientific provenance links, context descriptors, model domain, operators and
  all other candidate artifacts remain fixed. Changed scalar derivations gain
  a numerical-trial annotation. An immutable `calibration_trial.json` binds
  the original freeze, plan, release, trial index, values and value origin;
  baseline values are labeled unchanged. Such trials cannot parent a session.
  Each trial is a distinct frozen bundle.
- The selected trial is the earliest feasible minimum fit loss. Its freeze
  hash and every fit-record hash are sealed before replay. Both baseline and
  selected trial replay on `[19111, 19123]`; when identical, replay is reused.
  Baseline replay still occurs if no fit trial is feasible. Replay never alters
  selection. These unused seeds assess simulation stability on the same source
  evidence, not independent biological validation.
- Loss is `sum(weight * ((value - reported_value) / scale)^2) / sum(weight)`.
  Every check has an explicit positive scale, positive weight and Agent-authored
  rationale. No standard error or confidence level is inferred. Any missing,
  noncomputable or nonfinite statistic makes the whole trial infeasible; failed
  executions and all 20 diagnostic rows remain retained.
- Generated programs run only through the bridge's existing, fixed
  WSL/bubblewrap backend. There is no runtime override or host import of
  submitted code. Verification recomputes permitted feedback from retained
  execution outputs; it does not rerun a generator.

## Inputs

The plan deliberately retains the existing calibration plan schema:

```json
{
  "schema_version": 1,
  "parameters": [{"name": "DECLARED_SCALAR", "lower": 0, "upper": 1, "step": 0.1}],
  "constraints": [{"context_id": "SOURCE_CONTEXT", "check_id": "FIXED_CHECK", "scale": 1,
                   "scale_reason": "Agent-authored scientific rationale; all 20 checks required."}],
  "fit_seeds": [19101],
  "replay_seeds": [19111, 19123],
  "optimizer": {"method": "bounded_coordinate_search", "max_trials": 40, "shrink": 0.5,
                "min_step_fraction": 0.001, "target_loss": 0},
  "execution": {"timeout_seconds": 30, "memory_mb": 1024, "output_bytes": 20000000, "log_bytes": 100000},
  "noncomputable": "infeasible"
}
```

This is an illustrative schema, not a scientific plan or authorization. Bounds,
steps, scales, stopping loss and scientific requirements must be authored and
reviewed before release. `target_loss` is an optimizer stop rule, not a universal
scientific acceptance threshold.

The separate criteria object has exactly these keys:

```json
{
  "schema_version": 1,
  "scope": "source_only",
  "parameter_roles": [{"name": "DECLARED_SCALAR", "role": "source_parameter", "rationale": "Scientific role."}],
  "check_weights": [{"context_id": "SOURCE_CONTEXT", "check_id": "FIXED_CHECK", "weight": 1,
                     "weight_reason": "Scientific weight rationale; all 20 checks required."}],
  "scientific_requirements": ["Predeclared substantive requirements for source-only review."]
}
```

Roles are `source_parameter`, `context`, `domain` or `covariance`. The latter
three require exact-name authorization in the separate root release. Role
declarations are review inputs, not automatic semantic certification; a scalar
named or declared benign can still encode a forbidden scientific choice.
Scientific requirements are retained for substantive review and do not change
fit-only selection. The adapter does not certify source adequacy or target
validity. Frozen auxiliary copies of the plan and criteria may remain in the
candidate; they are preserved bytewise in every trial.

## CLI and release gate

From the project root:

```text
python -B work/c3s/method/run_source_calibration.py validate --bundle BUNDLE --candidate initial --plan PLAN.json --criteria CRITERIA.json
python -B work/c3s/method/run_source_calibration.py run --bundle BUNDLE --candidate initial --plan PLAN.json --criteria CRITERIA.json --session s --release ROOT_RELEASE.json
python -B work/c3s/method/run_source_calibration.py verify --bundle BUNDLE --session s
```

`validate` is metadata-only and writes nothing. It returns the exact input
`binding`, worst-case `reservation` and required restricted parameter names.
The root must separately create the existing bundle-global budget using
`calibration_budget.create_budget`, and author the release:

```json
{
  "schema_version": 1,
  "kind": "root_source_calibration_release",
  "decision": "release",
  "session_id": "s",
  "binding": {"COPY": "the complete binding object returned by validate"},
  "authorized_restricted_parameters": [],
  "reason": "Root review and authorization rationale."
}
```

The adapter never creates its own execution release. The binding includes the
task, candidate freeze, plan, criteria, adapter, reused engines and fixed
runtime configuration. The release's content hash also enters the immutable
budget reservation. Hashes are retained-artifact commitments, not signatures
against an administrator rewriting the complete record.

Maximum reservation per structure is **40 trials, 88 context executions and
88 × timeout seconds**. It includes two source executions per fit trial plus
eight executions for baseline and selected replay. Budget records retain
reservation and actual trial/execution counts; unused reservations are never
refunded. Each execution receipt also retains elapsed time and the session
records wall time. No monetary cost estimate is invented.

Use a short session name such as `s` and short bundle paths on Windows. The
artificial test fixture's longest retained file path was measured at 237
characters with its bounded test root. Real candidate filenames should be
checked before release.

## Retention and testing

Sessions are exclusive and nonresumable. A frozen parent may have only one
calibration session in its bundle ledger. Existing destinations are never
overwritten. Unexpected errors retain `failure.json`, all partial artifacts and
the pending, permanently charged reservation; there is no automatic retry,
resume or host fallback. Normal execution failures instead remain trial
receipts with infeasible scores and search continues within its original cap.

`test_source_calibration.py` uses invented metadata and a mocked bridge. The
actual preparation/freeze/verification infrastructure is used, but no generated
table is produced and the inert generator contains an import-failure sentinel.
Mock release records explicitly identify themselves as engineering fixtures;
they are not scientific execution releases.

```text
python -B -m pytest work/c3s/method/test_source_calibration.py -q --basetemp=work/c3s/method/u2 -p no:cacheprovider
```

Choose a new unused `--basetemp` to retain prior artificial test attempts.
Tests cover weighted scoring, all-check requirements, bounded fit transcripts,
selection before replay, no selection changes from replay, baseline replay
reuse, failures, no-feasible-fit handling, interruption, release bindings,
restricted-role authorization, file tampering and prevention of reruns.
