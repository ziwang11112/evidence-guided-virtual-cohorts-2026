# Execution-backed source feedback

`cohort_harness.source_replay` runs a frozen enrichment generator under explicitly declared source covariates, then computes the existing declarative source statistics on its verified output. The original task, candidate and model specification stay frozen. This supplies source feedback for a subsequent Agent revision; it does not select a revision or scientific relationship.

## Frozen recipe

Before freezing a generator candidate, add `source_replay.json` and its covariate CSV files inside that candidate. A minimal recipe is:

```json
{
  "schema_version": 1,
  "contexts": [
    {
      "id": "source_1",
      "population": "The declared population and selection for this source",
      "reason": "Why these source covariates represent the reported statistic",
      "assumption_ids": ["A_source_context"],
      "measurement": {
        "mode": "identity",
        "description": "The CSV and generator output use the task variable names and units; explain the source mapping."
      },
      "input": {
        "path": "source_contexts/source_1.csv",
        "sha256": "REPLACE_WITH_CSV_SHA256",
        "origin": "declared_source_covariates"
      },
      "checks": [
        {
          "id": "mean_y",
          "evidence_id": "E_source_mean",
          "status": "approximate",
          "operator": {
            "kind": "mean",
            "unit": "y_unit",
            "selection": [],
            "missing_policy": "error",
            "column": "y"
          },
          "assumption_ids": [],
          "reason": "Compare the generated source-context mean with the extracted source mean."
        }
      ]
    }
  ]
}
```

Every assumption ID must already exist in `model_spec.json`; every evidence ID must exist in `evidence.json`. `computed` requires no context or check assumptions. `approximate` requires at least one assumption in the context or check. A source whose population must be approximated therefore cannot claim an exact check by leaving its check-level assumption list empty.

The covariate CSV must contain exactly the task's identifier and observed columns, in task order. Generated outcome columns are forbidden, even if empty. Values must satisfy the original task types, bounds, categories, nullability and unique-identifier contract. CSV bytes are bounded by the execution output-byte limit, with at most one million source rows and one million characters per physical line or field. Source row count may differ from the target task. The adapter supports enrichment and generator submissions only; direct simulated-output tables cannot obtain this linkage.

Measurement mapping is explicitly identity-only. No transformations, unit conversion, factor encoding, coefficient selection or source-population reconstruction occur in the harness. A builder may prepare source covariates and evidence in task units, retaining the original extracted values, derivations and assumptions in its submission. The declaration and hashes do not independently establish that such preparation is scientifically appropriate or excludes forbidden information; the builder/custodian evidence-access boundary remains procedural.

Checks accept the existing mean, sample SD, Pearson correlation, OLS coefficient and event proportion operators, including explicit selections and missing-value policies. Statistic kind and unit must match the evidence item. Variable/adjustment mismatch requires `approximate` and recorded assumptions. Non-computable estimators retain their explanation; there is no automatic pass threshold.

## API and retained artifacts

```python
from cohort_harness.source_replay import run_source_replay, verify_source_replay

report = run_source_replay(
    bundle, "candidates/initial", "source_feedback_01", seed=17,
    runtime=trusted_runtime, timeout_seconds=30, memory_mb=1024,
    output_bytes=20_000_000, log_bytes=100_000,
)
assert report["status"] == "success"
verify_source_replay(bundle, "source_feedback_01", candidate="candidates/initial")
```

The corresponding CLI commands are `source-replay --bundle PATH --candidate NAME --replay-id ID --seed SEED --runtime CONFIG` and `verify-source-replay --bundle PATH --replay-id ID [--candidate NAME]`. Execution limits have the same flags as `execute`.

Feedback is written outside the frozen candidate:

```text
bundle/source_replays/<replay_id>/
  replay.json
  contexts/<context_id>/bundle/
    task.json
    registry.json
    observed.csv
    sources/...
    candidates/source/...
    executions/replay/...
```

Each child task changes only `population` and `n_rows` from the parent task. Its information exclusions, task mode, column contract and budgets remain identical. The child contains the parent's frozen registry prefix and sources, with exact copies of every frozen candidate artifact. Code and model specification are byte-identical. A child freeze describes this derived execution bundle, not an Agent model revision; an actual Agent revision remains a separate parent-linked candidate subject to the original revision budget. Replay does not perform literature calls or consume query/download budget. All contexts use the caller's recorded seed and resource limits.

The existing WSL/bubblewrap adapter executes the child generator. Only its staged task, covariates, specification, generator, request and worker enter the generator sandbox. A successful verified receipt is required before any check receives `generation_link_verified: true`. The report binds the parent freeze, recipe, code/specification, child artifacts, execution receipt and generated bytes. Verification rechecks all hashes, original parent lineage, child task derivation, registry prefix, same candidate bytes, execution status/limits and recomputes the statistics. Passing an expected `candidate` prevents accidental reuse of another candidate's feedback.

Attempted generator failures retain their execution artifacts and return a failed report with no verified check for that context. Integrity or initial contract errors raise; partial artifacts remain for inspection and cannot be reused under the same replay ID. A numerical discrepancy from the source is a diagnostic and does not change a successful execution into a failed run. Reports are append-only. This implementation requires its recorded source-replay engine version for later verification.

For a revision, the Agent should review the verified source-only report, explain whether to retain or revise, and bind a copy of that report as an auxiliary artifact in the new candidate's `checks.json`. Source replay does not modify the frozen parent or automatically re-fit its parameters. Keep any later held-out evaluation separate from this feedback loop.

## Verification performed

The focused test suite uses invented data and a mocked backend for structural and failure checks; those tests do not establish isolation. It checks preservation, parent/child code and specification identity, actual source row-count use, mean/SD/correlation/OLS calculations, declared assumption requirements, outcome-column/path/hash rejection, failed execution, changed output/specification/input, wrong-candidate feedback, feedback-number tampering, append-only IDs and registry-prefix preservation.

An actual isolated invented smoke run is retained at `work/source-replay-smoke-eab50dd6`. The four-row source context ran through WSL/bubblewrap and passed replay verification, yielding mean 5 and OLS slope approximately 2. Its source mean discrepancy of -2 remained visible diagnostic feedback. This was a trusted interface fixture, not an Agent submission or biomedical validation.

Hash receipts are not signatures against a host user rewriting the full record. Generator-only isolation does not constrain the Agent's other tools. Declared population and measurement equivalence still need substantive review. Source consistency does not establish target-population validity or uncertainty calibration.
