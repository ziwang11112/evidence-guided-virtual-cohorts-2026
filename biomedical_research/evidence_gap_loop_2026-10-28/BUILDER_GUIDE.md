# Common construction contract

Read this document, your assigned policy file, the three descriptive JSON/Markdown files and observed.csv in `shared/`, `runner_contract.json`, your own run folder, and approved artifacts in your own literature session only. Do not inspect `custodian/`, `review/`, other runs, old experiments, results, source downloads, or original participant IDs. You may execute the provided literature CLI; do not use other web/search/download tools. Scope instructions are procedural controls, not a claim of OS-enforced isolation.

## Scientific task

Preserve each observed `row_id,bmi,age,sex` and generate an entirely unmeasured `hdl` column in mg/dL for the described target population. Produce useful virtual data for biomedical association analyses, including questions not answered explicitly by your input evidence. No expected sign, coefficient, correlation, shape, subgroup pattern or residual variance is supplied by the coordinator.

Choose the scientific structure and all parameters yourself. You may use applicable primary research, explicit transformations and clearly documented assumptions. Do not use individual source datasets or target outcome data. All NHANES-derived evidence from ANY cycle is excluded; the target cohort name is disclosed only to define population/measurement and exclusions. The gateway screens before displaying content, including article references; record access limitations and never bypass a rejection.

Both workflows can identify problems, search for additional evidence, consider competing structures, revise and retain a justified no-op. Use your best scientific judgment. This is not a competition to produce a desired known effect.

## Tools and budget

Python: `python`.

Run from the experiment root with your assigned absolute `RUN` directory:

```
python -B tools/literature_gateway.py --session RUN/literature --config tools/gateway_config.json search --query "..." --limit 10
python -B tools/literature_gateway.py --session RUN/literature --config tools/gateway_config.json fetch --pmcid PMC...
python -B tools/literature_gateway.py --session RUN/literature --config tools/gateway_config.json list-supplements --pmcid PMC...
python -B tools/literature_gateway.py --session RUN/literature --config tools/gateway_config.json fetch-supplement --pmcid PMC... --supplement-id RETURNED_ID
```

There are at most 12 search queries and 12 document download attempts **in total across initial construction and revision**, plus the gateway's bounded metadata requests. Follow the returned usage counters. Reserve some budget when a concrete follow-up may be useful. There is no required paper count. Both arms receive the same tools and maximum budget. Unsupported supplement formats return a categorical error; do not treat missing tables as zero effects.

Build an initial candidate in the first assigned turn. An independent reviewer will then supply source/code/scientific findings, without target feedback. You have one revision turn with the remaining budget. Both initial and final versions will be retained. Do not open a final version before that review. No model training or API credentials are needed.

Gateway returns artifact `{session_relative_path, sha256, bytes}`. In your ledger, use `{path: "literature/" + session_relative_path, sha256: returned_sha}` relative to your run. Only artifacts genuinely registered by the gateway are accepted. Keep source records traceable to main text or supplement; if using an abstract-only quantity, mark that limitation explicitly and do not invent unavailable tables.

## Required initial files

Write only inside your own run folder:

- `initial/generator.py`: `generate(observed: pandas.DataFrame, evidence: dict, seed: int) -> pandas.DataFrame`.
- `initial/model_spec.json`: all scientific parameter values and their provenance.
- `initial/evidence.json`: typed source/evidence records below.
- `initial/decision.md`: concise scientific choices, transformations, source applicability, assumptions, unresolved questions, supported/unsupported uses and search stopping reason. These are auditable decisions, not private reasoning traces.
- `initial/artificial_checks.json`: numerical/source-only checks and invented-input tests that you actually ran; label their scope. No true target outcome tests.
- Additional policy-specific files if required by your assigned policy.

Generator returns exactly `row_id,bmi,age,sex,hdl` in the input row order, preserving observed values. HDL must be finite and positive. Include conditional stochastic variability with a local seed-controlled RNG. A deterministic point-prediction table is not this generation task. Do not force a desired p-value or generated-sample correlation.

Allowed dependencies are NumPy, Pandas, SciPy, math, statistics and typing. No file/network/subprocess access, dynamic execution, import tricks, input mutation, or global RNG mutation. The specification is passed as the `evidence` argument. Keep scientific numerical constants in `parameters` where practical; all remaining numerical modeling choices must be explained. Pure mathematical/indexing constants are not biological evidence.

You may inspect observed predictor distributions, but do not look for hidden answers or outcome-derived variables. Test implementation on invented inputs before submission. The controller will produce the official repeated cohorts after freeze and review. Do not manually tune to particular generated draws.

### Evidence schema

Top level: `sources` and `evidence`, both nonempty lists.

Each source requires:
`id`, `identifier` (PMCID/DOI), `population`, `measurement`, `cohort_overlap`, `approved_artifacts` (list of path/hash objects).

Each evidence item requires:
`id`, `source_id`, `locator`, `estimand`, `variables`, `adjustment`, `reported`, `uncertainty`, `applicability`, `model_use`, `bridge_assumptions`.

Keep unknown information explicitly unknown. Means, correlations, adjusted slopes, standardized effects, odds ratios, standard errors and standard deviations are different quantities. A source can be contextual/non-numerical. Two sources from the same cohort are not independent confirmations. Do not apply LLM confidence as a numerical precision weight.

### Model specification schema

`parameters`: a nonempty dictionary of your selected parameters, including grouped/nested values if useful.

`assumptions`: a list of objects with `id` and `description`.

`parameter_provenance`: exactly the same keys as `parameters`; each entry is an object with:

```
{
  "evidence_ids": ["actual evidence record IDs, or empty when purely assumed"],
  "assumption_ids": ["actual assumption IDs, or empty when not needed"],
  "derivation": "Exact reported estimate or transformation and its conditions"
}
```

At least one evidence/assumption reference per parameter is required. All IDs must resolve. Additional fields for equations, measurement, uncertainty, family, alternatives and applicability are welcome. Declaring an assumption is not evidence that it is true.

## Revision turn

After receiving the review, decide whether new evidence, extraction repair, structure revision, parameter revision, sensitivity analysis or a justified no-op is warranted. Use only permitted evidence and the review. Do not infer hidden answers from the coordinator's wording.

Write a new `final/` directory with generator, model_spec, evidence, decision and actual artificial checks. Preserve every initial file and gateway history. Add `final/revision.json`:

```
{
  "generator_or_spec_changed": true,
  "reason": "Concrete reason; use false above for an exact generator/spec no-op",
  "findings_addressed": [],
  "remaining_limitations": []
}
```

File hashes determine whether generator/spec changed; mere prose updates are not numerical improvement. Report substantive retrieval/model decisions and remaining uncertainties. You will not receive target evaluation until all constructions are complete and frozen.

Your assigned workflow is one member of a small pilot. Do not inspect or emulate other constructions. Do not claim that repeated draws are independent models, that larger synthetic sample size supplies new clinical evidence, or that a source-compatible model is already validated in the target population.
