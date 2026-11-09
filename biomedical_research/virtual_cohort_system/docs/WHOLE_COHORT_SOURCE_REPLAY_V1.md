# Whole-cohort source replay v1

This additive adapter executes a frozen program in a separately declared source
population. It uses the existing WSL/bubblewrap execution backend without any
local fallback. Legacy modules and frozen bundles are unchanged. It never reads
parent execution output, target-reference rows, or requested target-use results.

## Builder interface

Before freezing, put `whole_cohort_source_replay_v1.json` and each referenced
recipe/semantics JSON inside the candidate. The exact schema is:

```json
{
  "schema_version": 1,
  "budget": {"max_evaluations": 24, "max_rows_per_evaluation": 10000},
  "schedule": [
    {"replay_id": "initial_source_main_19701", "candidate": "candidates/initial",
     "context_id": "source_main", "seed": 19701, "n_rows": 10000}
  ],
  "contexts": [
    {
      "id": "source_main",
      "population": "Builder-declared source law, selection and limitations",
      "n_rows": 10000,
      "columns": ["REPLACE WITH FULL v1 COLUMN OBJECTS"],
      "reason": "Scientific justification for this source projection",
      "assumption_ids": ["A_source_law", "A_standardization"],
      "recipe": {"path": "source_contexts/main_feedback.json", "sha256": "64 lowercase hex characters"},
      "semantics": {"path": "source_contexts/main_semantics.json", "sha256": "64 lowercase hex characters"},
      "predictor_checks": [
        {"kind": "zscore", "column": "bmi", "raw_column": "raw_bmi",
         "selection": [],
         "reference": {"mode": "sample", "selection": [], "ddof": 1},
         "assumption_ids": ["A_standardization"],
         "reason": "Declared source-sample standardization convention, not certified as the paper convention"}
      ],
      "assumed_diagnostics": [
        {"check_id": "source_slope", "assumption_ids": ["A_standardization"],
         "reason": "Explicit descriptive source-law projection under this convention"}
      ]
    }
  ]
}
```

The example is a schema illustration, not a scientific model. No clinical
parameter values are supplied by the adapter. `columns` uses the existing full
task column schema, with the same row identifier as the parent; all other
columns have role `generated`. Source columns may include nuisance variables
absent from the target task, and may have different supports or units. Such
differences need the builder's separately frozen source-to-target mapping.

Every schedule entry has exactly the five shown fields. IDs are portable names;
candidate is `candidates/name`. Include all planned stages/seeds in the initial
schedule and retain identical `schedule` and `budget` in any revision. Optional
scheduled contexts can remain undeclared and unused; a requested context must
exist and its row count must equal its scheduled row count. Schedule length
cannot exceed the budget. The controller must bind these limits to the approved
external protocol: this generic adapter cannot determine the user's budget from
an arbitrary builder-authored number. It counts reservations across all
candidates in the same bundle; new bundles are not a budget-reset mechanism.

## Exact same generator and specification

The child changes only task `population`, `n_rows`, and `columns`. Task identity,
mode, row identifier, information policy, and task budget remain unchanged.
`generator.py`, `model_spec.json`, `evidence.json`, `decision.md`, admitted source
files and the parent's frozen registry prefix are copied byte-for-byte and
verified. Source evidence is not rewritten to manufacture operator compatibility.
The child has its own adapter-authored `checks.json`, parent binding, and freeze.
Parent artifacts, including a target-only feedback recipe, remain untouched.

The existing worker invokes `generate(observed, spec, seed)` with `observed=None`.
The generator may read the read-only `/input/task.json` in that isolated process
to obtain the current population, row count and output schema, for example:

```python
import json
from pathlib import Path

def generate(observed, spec, seed):
    task = json.loads(Path("/input/task.json").read_text())
    # Choose the declared source/target law using task and the unchanged spec.
    # Return exactly task["n_rows"] rows and the task's ordered columns.
```

The source sidecar is compiler metadata and is not mounted in the worker. Put
all scientific sampling conventions and source/target parameters in the same
frozen specification. Context selection based on the declared population or
column schema must be explicit in that generator and specification. No host
code executes the generator or injects coefficients.

## Strict recipes and assumption-dependent projections

Each referenced recipe has the existing `whole_cohort_feedback.json` schema;
its population equals the source context population. Its assumption IDs include
all context and predictor convention assumptions. Each referenced semantic
sidecar has the existing `source_semantics_v1.json` schema, binding the unchanged
`evidence.json` hash and the exact per-context recipe hash. These files are copied
unchanged to their canonical names in the child. Use `semantic_feedback_v1`
definitions faithfully; weighting or standardization that is unresolved remains
unavailable in the strict result. A standardization assumption must not be
relabelled as a verified identity measurement mapping just to obtain a strict
numeric value.

The strict engine always preflights the complete recipe before execution and
collects feedback after successful, verified output and predictor checks. A
structural semantic error rejects the operation; there is no legacy fallback.
The strict report is retained under the source child. `matched_declared` means
agreement among submitted definitions, not exact source-population recovery.

`assumed_diagnostics` is an explicit parallel lane. Each entry references a
non-null operator in the strict recipe whose declared status is `approximate`.
It requires at least one known assumption. After the strict report is produced,
the unchanged existing `source_checks.apply_operator` evaluates that very same
operator on the verified source output. OLS is supported, as are its other
existing operators; no substituted adjustment, selection, transform, or estimator
is introduced. The label is always `assumption_dependent_source_projection`,
including when strict semantics are unavailable. Raw point differences and the
reported source uncertainty are retained descriptively, with no acceptance
score, no CI-overlap equivalence claim, and no residual-SD interpretation.
Unsupported/undefined calculations remain unavailable rather than zero error.
The source operator itself must be `specified`; an unsupported or unreported
estimand cannot enter this lane. Every declared source analysis variable unit
must equal its generated task column unit, with the existing dimensional
coefficient check. `nonidentity` therefore does not authorize an implicit
outcome conversion or comparison of differently scaled numeric columns.
For `nonidentity` or unresolved transforms, this adapter's assumed lane supports
only OLS whose coefficient term is an explicitly checked zscore predictor.
Other transformation families need a separately implemented and reviewed mapping.
The parallel estimator is unweighted. It does not implement weighted regression
or establish equivalence with a known weighted source analysis. Any claimed
equivalence needs a separately reviewed scientific argument; otherwise that
published estimator remains unavailable, and any unweighted projection must be
labelled as an assumption-dependent comparison with a different sampling rule.

## Standardized numeric predictors

The generator emits both a raw column and its precomputed standardized numeric
predictor. The standardized column has unit `1`; original evidence variable
names can be retained for that source-only standardized column while the raw
column has a distinct name. Every `predictor_checks` entry verifies the formula
on the generated table before either numerical diagnostic lane proceeds.
`selection` selects rows to check; `reference.selection` selects source rows from
which mean and SD are computed. `ddof` is explicitly 0 or 1. Different
stratum-specific definitions can be declared as separate checks. Empty
selections, insufficient reference rows, zero SD, nonfinite values and false
identities fail closed. Tolerance is fixed at `rtol=atol=1e-9`, solely for a
numerical identity, not source fit. Reference mean and SD are recorded.
Every row selected by a source operator using a declared standardized column
must be covered by that column's identity checks; checking a convenient subset
cannot validate a regression on additional unchecked rows.

An alternative reference is
`{"mode":"model_parameters","mean_parameter":"KEY","sd_parameter":"KEY"}`.
Those keys must identify finite scalar parameters in the unchanged model
specification, with positive SD and the existing parameter provenance. Their
clinical meaning and transfer assumptions still need review. The adapter never
reads target rows to estimate these values and never computes them from a target
output. No other predictor transformation is implicitly performed.

## API and receipts

```text
python -m cohort_harness.whole_cohort_source_replay_v1 preflight --bundle B --candidate initial
python -m cohort_harness freeze --bundle B --candidate initial
python -m cohort_harness.whole_cohort_source_replay_v1 run --bundle B --candidate initial --replay-id initial_source_main_19701 --context-id source_main --seed 19701
python -m cohort_harness.whole_cohort_source_replay_v1 verify --bundle B --candidate initial --replay-id initial_source_main_19701
```

Python entrypoints are `preflight(bundle, candidate)`,
`run_source_replay(bundle, candidate, replay_id, context_id, seed, *, runtime=None,
timeout_seconds=30, memory_mb=1024, output_bytes=20000000, log_bytes=100000)`, and
`verify_source_replay(bundle, replay_id, *, candidate=None)`.

Each attempt lives under `whole_cohort_source_replays_v1/<replay_id>/`. An
exclusive admission lock serializes reservations. `request.json` reserves one
scheduled evaluation before child construction or execution. Failed and
interrupted reservations count and cannot be overwritten/retried under the
same ID. A stale lock or malformed interrupted reservation fails closed for
controller inspection. Source feedback is never written inside the parent
candidate. Verification checks parent freeze, exact child task/code/spec/evidence,
source registry/artifacts, per-context recipes, execution provenance, file hashes,
predictor identities, strict feedback, and the separate assumed calculations.
Failed execution receipts remain failures with no successful generation claim.

This ledger does not observe optimizer-internal calls or analytic objective
evaluations. The controller must separately enforce and audit those budgets;
one source execution is not proof that only one objective evaluation occurred.
Rows and seeds are numerical evaluations, never independent clinical studies.
