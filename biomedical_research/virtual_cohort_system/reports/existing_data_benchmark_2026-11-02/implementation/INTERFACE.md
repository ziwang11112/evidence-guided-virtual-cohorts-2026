# Single-stage constructor interface

Read this file, `AGENT_PROMPT.md`, `contracts_guidance.md`, your bundle's `task.json`, `sources/evidence_packet.json`, `sources/NGSP_UNITS.md` and `input/compiled_evidence.json`. The evidence packet is the approved original arm packet. The compiled evidence is its mechanical harness representation plus common unit guidance. Native source variable names and units remain native; the target task defines its own output columns. Do not treat differently named plasma/serum measurements as interchangeable.

The task is whole-cohort synthesis without participant input. Produce exactly 3,000 rows with columns, order, types and bounds from the task. `female=1` denotes the documented female category and `female=0` the documented male category. Source gender coding must be handled under the qualifications in the supplied packet. The target glucose is the released central-serum field under the stated analytical population, not source fasting plasma by definition. Task bounds are representation requirements, not observed population moments.

## Allowed artifacts and information

Your constructor read allowlist, relative to this bundle, is:

- `task.json`
- `sources/evidence_packet.json`
- `sources/NGSP_UNITS.md`
- `input/compiled_evidence.json`
- `input/INTERFACE.md`
- `input/AGENT_PROMPT.md`
- `input/contracts_guidance.md`
- Your own `candidates/initial/` submission files.

Do not read registry/controller manifests, other bundles, wider workspace documents, old code/candidates/results, target data, original source bodies or external sources. DOIs and the unit-guidance URL are attribution, not permission to retrieve. The procedural information boundary does not prove absence of general prior knowledge. No new source search or download is permitted.

There is one scientific stage, `initial`, with no scientific revision or source-feedback round. The bounded technical correction policy below applies before freeze. The controller will execute this one frozen program with seeds **1701, 1702 and 1703**. Do not create another model or seed-dependent scientific settings. Different random draws from the same declared law are permitted. Do not run the generator, produce a table, perform a pilot/sweep or access real/generated rows during construction. The controller owns all executions and their attempt accounting.

## Exactly five submitted files

Use only `candidates/initial/` for your submission:

1. `evidence.json`: already supplied as a fixed exact copy of `input/compiled_evidence.json`; do not edit, replace or subset it.
2. `model_spec.json`: your scientific parameters, assumptions and parameter provenance under the supplied schema.
3. `generator.py`: your actual self-contained program.
4. `decision.md`: concise model choices, evidence use, transport assumptions, unsupported analytical uses, implementation limitations and reason for stopping after this submission.
5. `checks.json`: truthful numerical-check status under the schema below.

Do not add auxiliary files, generated CSVs, source-check recipes, output logs, alternate models or a freeze receipt. The controller adds its own receipts outside your five-artifact submission step. All scientific parameters must be documented in the specification; do not hide a second set in code. Engineering constants such as column names are not empirical facts.

## Program interface

Define one top-level synchronous function with exactly three positional arguments:

`generate(observed, spec, seed)`

It receives `observed=None`, the complete submitted model specification, and one prescribed integer seed. Return a pandas DataFrame, not a file. The exact task output order is `row_id, age, female, bmi, glucose, hba1c`. IDs are unique nonempty strings. Age is an integer in 35-74; female is integer 0/1; BMI is strictly positive; glucose and HbA1c are finite and nonnegative. No missing cells are allowed. Exactly 3,000 rows must be returned. Bounds enforce task validity; they are not permission to infer or copy empirical target ranges.

Use the seed for all random draws. Use `spec['parameters']` for declared scientific settings and declare your handling of support/truncation if needed. The same model and parameters must be used for every seed. Do not import files, inspect paths/environment, access network/processes, print sensitive state or read the task/source files from inside the generator. The function must work from the supplied spec alone.

The trusted runtime provides standard Python numerical facilities plus numpy 2.4.5, pandas 3.0.3 and scipy 1.16.3. It allows 180 seconds, 1,024 MiB memory, a 2 MB output bound and bounded logs per run. These are engineering limits, not invitations to run calibration simulations. Avoid undeclared packages and runtime installation.

## Specification and checks

See `contracts_guidance.md` for exact required keys. Every top-level parameter must have provenance referencing supplied evidence IDs or declared assumption IDs. Individual SDs, estimator SEs, quartiles, regression coefficients and correlations retain distinct meanings. Native source facts may inform your modelling choices, but no target signs, slopes or success values are prescribed.

Exactly five artifacts leave no auxiliary check-result file. Therefore this submission's `checks.json` must record numerical checks as **not_computable/not performed**, with an empty artifacts list. For example, use a source-only record whose detail states that no generated source table or target feedback was provided and no numerical source diagnostic was executed. Do not claim a pass/fail for an unperformed calculation. The controller will perform static contract/signature validation and record it separately; such validation is not numerical or scientific confirmation.

A valid submission is not an executed or scientifically validated generator. The controller reviews and freezes before isolated execution. A failed runtime must never trigger your own local fallback. No source-context generation or numerical feedback collector is supplied in this single-stage task.

## Pre-freeze technical correction policy

An initial submission may receive at most two interface-only correction returns before freeze. Permitted findings are schema errors, syntax/signature errors, prohibited I/O, provenance-reference inconsistency or an unused required field. No scientific statistic, random draw, source-feedback value, desired relationship or parameter recommendation may be returned. The author may perform metadata-only validation of permitted files, but must not execute the generator or inspect target information. Preserve every submitted version and the review log outside the bundle under controller custody. These corrections are not scientific revisions or additional models. Once frozen, every prescribed execution failure consumes its slot; no replacement run or model is permitted.
