# Case-local evaluation interface

2026-10-31. **Implementation and guard tests only; no evaluation release created and no actual evaluation invoked.** No reference CSV or actual generated cohort was opened. Existing analytical_engine.py, its tests, readiness document, and frozen logs are unchanged. The controller adds no statistical estimator: all coefficients, descriptive summaries, and 399-attempt empirical stability bands come from the bound analytical engine.

Files: `run_evaluation.py`, `test_run_evaluation_guards.py`, and this interface. The controller is inert on import. `--help` exits before case access, harness imports, runtime operations, or analysis. There are no generation, source-feedback, rerun, force, seed-override, or output-directory options.

## Future root-issued release

After every final candidate is frozen and every scheduled execution has a preserved receipt, root may create `R/EVALUATION_RELEASE.json`. This document is not that release. All paths below use forward slashes and are relative to R unless explicitly described as project-relative. Root must list the complete planned set of one or two constructions; the controller checks every listed construction's initial/final × three-seed grid and cannot discover an omitted construction from an unrelated directory.

Required top-level fields:

```json
{
  "schema": "ensanut_evaluation_release_v1",
  "release_id": "ROOT-ASSIGNED-UNIQUE-ID",
  "issuer": "root",
  "status": "approved",
  "effects_authorized": true,
  "purpose": "fixed_target_evaluation_once",
  "bindings": {},
  "harness_files": {},
  "reference": {"path": "custodian/private/reference_v2.csv", "sha256": "ROOT-VERIFIED-HASH"},
  "builders": [],
  "schedule": []
}
```

The empty objects/lists and placeholder hash deliberately make this example non-executable. Root fills all fields only for a concrete, verified schedule.

`bindings` must contain exactly the following eight keys, each with `{ "path": "...", "sha256": "64 lowercase hex digits" }`:

| Binding key | Required path |
|---|---|
| protocol | PROTOCOL_v2.md |
| task | public_v2/task.json |
| source_panel | public_v2/SOURCE_PANEL_SPEC.json |
| analysis_engine | analysis/analytical_engine.py |
| evaluation_controller | analysis/run_evaluation.py |
| preparation_receipt | custodian/PREPARATION_RECEIPT_v2.json |
| preparation_release | PREPARATION_RELEASE_v2.json |
| preparation_script | custodian/prepare_reference_v2.py |

`harness_files` maps every current `.py` source beneath `P/cohort_harness/`, including nested vendor Python sources, to its SHA-256. Its keys are project-relative, such as `cohort_harness/lifecycle.py`. The controller requires the exact current source set and hashes before importing the existing verification APIs. No runtime launch or subprocess execution is used by the controller.

The preparation receipt must use schema `ensanut_preparation_receipt_v2`, report `readiness.ready=true`, bind the supplied preparation release, and bind the same current protocol, engine, and preparation implementation. Its output entry `outputs["private/reference_v2.csv"].sha256` must equal `reference.sha256`; that receipt key is relative to custodian, while the evaluation-release reference path includes `custodian/`. Only the prepared seven-column reference is eligible for loading; the raw source/linked/audit files are not controller inputs.

The preparation receipt's metadata was inspected to confirm this interface. Observed receipt SHA-256: `7b233adcdabb86f9863bfd42b332ba3ffb65b01c528f1fc931cb4ade4d3c1758`. No receipt counts or reference rows were inspected for implementation choices.

Each `builders` entry has these fields:

```json
{
  "id": "construction_1",
  "bundle": "ROOT-CHOSEN-BUNDLE-PATH",
  "initial_candidate": "candidates/initial",
  "initial_freeze_sha256": "ROOT-VERIFIED-HASH",
  "final_candidate": "candidates/final",
  "final_freeze_sha256": "ROOT-VERIFIED-HASH"
}
```

Bundles must be distinct, including their resolved Windows identity. Each bundle's task must be byte-identical to the public task. Both stages must be frozen program candidates: actual `generator.py` present, actual direct `generated.csv` route absent, initial index 0 with no parent, final index 1 with the exact initial candidate/receipt path/hash as parent. These route/lineage checks happen for all builders before recursive `lifecycle.verify_candidate` is allowed to read candidate state. The existing API then verifies the source registry prefix, committed source/task bytes, evidence, specification, program ABI, check artifacts, and candidate files without executing the program.

Each `schedule` entry has these fields:

```json
{
  "builder": "construction_1",
  "stage": "initial",
  "seed": 18203,
  "stage_candidate": "candidates/initial",
  "execution_candidate": "candidates/initial",
  "run_id": "target-initial-18203",
  "receipt_sha256": "ROOT-VERIFIED-HASH",
  "status": "success",
  "output_sha256": "ROOT-VERIFIED-HASH",
  "retained_from": null
}
```

For every builder the complete schedule is initial and final at seeds **18203, 18211, 18223**, exactly once per stage/seed. No extra or missing slot is accepted. `receipt_sha256` binds `<bundle>/executions/<run_id>/execution.json`; `output_sha256` binds its `output/generated.csv`. The controller derives the relevant execution freeze hash from the builder's bound stage and never asks an old receipt to claim a different final freeze.

For a retained final, `stage_candidate` names the new final freeze, `execution_candidate` remains the initial candidate, and `retained_from` is `{ "stage": "initial", "seed": SAME_SEED }`. The final freeze must declare `revision.kind="retain"`; generator, model specification, evidence, external task/source commitments, and registry snapshot must remain identical. The same-seed initial/final slots must share the exact run ID, receipt hash, output hash, and status. Changed-model finals must declare revision and use their own matching final execution. A retention cannot spend new draws.

For a preserved unsuccessful execution, `status` is `failed` or `timeout` and `output_sha256` is null. Its root-bound receipt must still identify the correct program candidate, freeze, seed, scope, and status. No failed or timeout output or log is opened. Every failed slot remains in the JSON and in all 31 CSV endpoint rows with null values; it is not dropped or retried. A missing/malformed freeze or integrity mismatch rejects the gate rather than being relabelled a scientific failure.

## Read boundary and one-attempt behavior

1. Verify the root authorization, all fixed document/tool hashes, preparation receipt, complete schedule, every initial/final program freeze, retention identity, and every execution receipt's metadata. Successful runs must have the exact executor artifact set, staged task/model/program commitments, matching request/seed, approved runtime/launch identity, current worker hash, successful process, and completed worker report with 2,000 rows and the task's columns. The generated CSV is not opened in this phase.
2. Create the new fixed directory `analysis/results` exclusively and write `EVALUATION_ATTEMPT.json`. Any existing directory, including one left by a failed attempt, prevents another invocation.
3. Call existing `execution.verify_execution` only on the unique successful runs. This is the first point at which generated outputs may be opened. It performs no generation. Recheck the whole metadata gate, then load only the hash-bound prepared reference. Preserve lab cluster identifiers as strings. Confirm reference floors and execute the unchanged engine with exactly 399 attempts and seed 18301.
4. Evaluate every verified scheduled generated output using the same engine, additionally requiring exactly 2,000 rows and exactly 250 per age/sex cell. Invalid scientific values, quotas, or singular designs reject the whole generated table and remain reported as failed slots. Retained output contents are computed once and reused while every stage/seed label remains present.
5. Recheck all consumed input hashes before exclusively writing aggregates. Preserve any post-attempt exception in `EVALUATION_FAILURE.json`; no automatic retry or cleanup occurs.

No patient identifiers, examples, row-level reference data, or residual vectors are exported. No synthetic p-values, causal claims, equivalence decisions, source feedback, or tuning are added. Hash receipts establish local byte consistency and root's procedural authorization; they are not cryptographic signatures against coordinated host-side rewriting.

Future invocation, only after the explicit root release: `python -B analysis/run_evaluation.py`. The entry point derives this case from its own verified location; there is no CLI path override.

## Saved aggregates

All writes are under the previously absent `analysis/results/`:

- `EVALUATION_ATTEMPT.json`: release hash, start time, and scheduled slot count.
- `aggregate.json`: reference estimates, empirical stability bands and attempted/valid/failure information, each scheduled slot's result/status and reuse link, complete input hashes, and software versions. It separately counts scheduled slots, unique successful execution runs, distinct output contents, successful analytical slots, and failed slots. Bootstrap replicate-level estimates are omitted; aggregate bands and failure accounting are retained.
- `all_endpoints.csv`: every reference and scheduled generated endpoint, with builder, stage, seed, status, estimate, reference stability limits, and output hash. There are 31 fixed endpoints per slot. Retained initial/final labels are both present and share their output hash.
- `EVALUATION_COMPLETED.json`: completion time and hashes of both aggregate products; or `EVALUATION_FAILURE.json` if the attempt stops.

## Actual verification and current readiness

`python -B -m unittest test_run_evaluation_guards` passed **13/13 tests in 0.053 seconds** on the final code. All fixtures are temporary metadata or opaque placeholder bytes, never real or artificial cohort tables. Tests cover authorization-before-access, schedule completeness/seeds/budget, failure output prohibition, path/hash checks, retained scientific/source identity, actual program-route and exact parent preflight, no extra execution artifacts, successful metadata verification without generated-byte access, failed-receipt early return, inert import/help, and prevention of repeat attempts. No full evaluation or statistical calculation was executed.

A separate read-only audit identified two pre-gate access risks in the reused APIs (direct-row/recursive-parent verification and an unconstrained artifact list). Both were corrected with explicit route/lineage preflight and an exact successful-artifact whitelist, with guard regression coverage. It also prompted comparison of resolved case-normalized bundle identities. The auditor did not invoke this controller or write/change files. A further delegated recheck was unavailable because the agent thread limit was reached; no final independent PASS beyond these inspected corrections is claimed.

Controller SHA-256: `a792b9380751ef6dcd6419c51e99ede902d5dc9694f2c5b39bfcaa2fae990005`.

Guard-test SHA-256: `c5168b2218031652123f837f97bf9c79aa087055ba0de64744051784e170f93e`.

Unchanged analytical-engine SHA-256: `1799c017b60f8fd3a9af409a524d3ebd9e54c81016e52da760aeafaefe03289d`.

The wrapper is ready for root review and future hash-bound schedule population. Actual effect computation remains gated on the separate root-issued evaluation release; no target result is claimed here.
