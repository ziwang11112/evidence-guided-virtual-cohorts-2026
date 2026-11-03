# Supplied contract guidance

This is a bounded summary of the unchanged `cohort_harness` version-1 contracts, supplied so construction does not require wider workspace reads. The controller validates against the actual implementation. Files use UTF-8 JSON with finite JSON numbers and no duplicate keys.

## Task and fixed evidence

`task.json` is fixed. It supplies schema_version, task_id, mode, population, row_id, n_rows, columns, information_policy and budget. This task is whole_cohort: there are no observed columns or participant input. All declared output columns must appear in exact order, meet bounds/types, and have no nulls. The sole identifier is unique.

`evidence.json` is fixed and already compiled to `{schema_version: 1, sources: [...], items: [...]}`. Do not edit its hashes, facts, IDs, source context, units, uncertainty or applicability. Source artifact references bind only this arm's permitted packet and common NGSP guidance, not a broader source archive. Evidence item IDs are the only legal evidence references in your specification.

Compilation expands each mean/individual-SD group into a mean item and an SD item; each median/quartile group into median, Q1 and Q3 items; each sex-count group into its derived fraction. These dependent summaries do not become independent source studies. The common NGSP relation is one contextual item. A relationship's unconfirmed interval level remains unavailable in the strict CI field and is preserved in its applicability text. No confidence level or estimator SE is inferred.

## model_spec.json

Exactly three top-level keys:

- `parameters`: an object of your finite JSON scientific settings. Nested objects/lists are allowed.
- `assumptions`: a list of objects, each exactly `{"id": "unique_id", "description": "explicit assumption"}`.
- `parameter_provenance`: an object with keys exactly equal to the top-level parameter keys. Each entry is exactly `{"evidence_ids": [...], "assumption_ids": [...], "derivation": "nonempty explanation"}`.

Every parameter must cite at least one valid supplied evidence ID or declared assumption ID. Lists have unique nonempty strings. Assumption IDs are unique. Derivation explains the relation between evidence, assumptions and your value; it is not a claim of recovered target truth. Do not include unsupported schema keys such as version, model_name or citations outside these objects.

## generator.py and decision.md

The generator must declare exactly one top-level synchronous `generate` function with three positional arguments and no variadic or keyword-only arguments. Return a pandas DataFrame from `(observed, spec, seed)`. Static signature acceptance does not execute the body or certify output validity. `decision.md` must be nonempty and should concisely describe scientific choices, evidence use and limitations without private reasoning traces.

## checks.json

Exactly these top-level keys:

`{"scope": "source_only", "records": [...], "artifacts": []}`

Each record has exactly `name`, `status` and `detail`, with unique nonempty names and nonempty details. Status is one of `pass`, `fail`, `not_computable`. Under this five-file, no-generator-run construction assignment, record the relevant numerical checks as `not_computable` and explain that they were not performed because no execution/feedback was supplied. Do not label an unperformed check as passed.

The unchanged lifecycle requires an auxiliary bound result artifact for a recorded pass/fail. Such an artifact would exceed this task's five-file inventory, so the controller performs and records its static validation outside your submission. `artifacts` stays empty. No target-feedback record is permitted.

## Controller commands, not constructor execution permission

After the five files exist, the controller can run from the project root:

`python -m cohort_harness validate --bundle BUNDLE --candidate initial`

`python -m cohort_harness freeze --bundle BUNDLE --candidate initial`

`python -m cohort_harness verify --bundle BUNDLE --candidate initial`

The CLI candidate name is `initial`; the Python API uses `candidates/initial` or its absolute directory. None of these three commands executes a program. Only the separately released isolated execution adapter may run it; no local fallback is authorized.
