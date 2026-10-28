# Evidence-guided virtual cohort system

Version 0.1.0 — milestone 1, 28 October 2026.

The objective is to let a capable Agent integrate permitted research evidence into reusable virtual data for biomedical analysis. The system supports three task contracts: whole-cohort generation, enrichment with an entirely unmeasured variable, and completion of missing cells. Program generation and direct row submission are both legitimate routes. This milestone implements the interfaces and checks; it does not demonstrate a scientific improvement.

## Responsibilities

| Layer | Responsibility | Milestone 1 status |
|---|---|---|
| Task owner / custodian | Define visible inputs, permitted evidence, scientific use, budgets and separately reserved analyses | Typed visible task contract; no target evaluator in the builder package |
| Agent skill | Select evidence, interpret study context, choose generator/parameters, explain assumptions and revise | Concise reusable skill supplied |
| Tool harness | Validate contracts, calculate declared source statistics, bind artifacts and retain revisions | Implemented |
| Evidence gateway | Search/fetch/screen literature, enforce real query budgets and register provenance | Existing gateway is a reuse candidate; not integrated into this version |
| Execution environment | Run submitted generation in a bounded process with no reference-data access | Not implemented in this milestone; current local Docker daemon was unavailable at inspection |
| Independent evaluation | Apply locked analyses to generated and real data after freeze | Existing study evaluators remain unchanged; generic adapter is a later milestone |

The harness does not select biological effects, coefficients, distributions, scientific success thresholds or a required number of Agents. Source files are data, not instructions. A registry records approved artifacts; it is not a content filter, authentication system or filesystem sandbox. Task query limits are declarations until a real tool adapter enforces them.

## Architecture decisions

- Reuse the established Python approach. Do not move the project to a hosted agent platform merely to change frameworks.
- Start with one capable builder and deterministic tools. A reviewer role does not require a permanent second LLM.
- Keep published evidence, derivations and assumptions distinct. Sources sharing a cohort are recorded as such.
- Code safety screening, source-statistic computation, output preservation and target scientific validity are distinct checks.
- Version candidates rather than overwrite them. Bind actual check artifacts as well as code, model specification and evidence.
- Keep registry history append-only so newly approved evidence can support a later candidate without altering an earlier source record.
- Do not load a hidden reference table into this harness. A clean input package is preparation for isolation, not proof of isolation.
- Ordinary generation, source-check-assisted revision and uncertainty methods must remain separable for later comparisons.

## Local use

Run from this directory. The implementation uses Python, NumPy and pandas; tests use pytest. The inspected development environment is Python 3.12, NumPy 2.4.5, pandas 3.0.3 and pytest 9.0.3. No API key, model training or HPC allocation is needed for these interface tests.

```powershell
python -m cohort_harness demo --destination work/demo
python -m cohort_harness validate --bundle work/demo --candidate initial
python -m cohort_harness source-checks --bundle work/demo --candidate initial
python -m cohort_harness freeze --bundle work/demo --candidate initial
python -m cohort_harness verify --bundle work/demo --candidate initial
python -m pytest -q
```

The destination must be new. The demo contains seven invented rows and stated arithmetic, not real patients, a published source or an Agent's scientific performance. Its deterministic direct-row route tests interfaces only; it is not an endorsed scientific generator. The source engine returns a mean and a regression coefficient and retains content hashes.

On this Windows account the default pytest temporary directory was inaccessible. If needed, use `--basetemp .pytest_runs/NEW_UNIQUE_NAME` with a fresh directory name inside this project. Never point that option at an existing data or source directory, since pytest manages its contents.

For a revision, prepare a new candidate directory and revision JSON with `reason`, `kind` (`retain` or `revise`), `addressed_findings` and `remaining_limitations`. `retain` must preserve the generator/direct rows and model specification. A declared `revise` must change those bytes; such a change is not automatically a numerical or scientific improvement.

```powershell
python -m cohort_harness freeze --bundle work/demo --candidate revised --parent initial --revision work/revision.json
```

The new candidate must retain evidence and check provenance and remain within the revision budget. Source additions must be registered by the trusted gateway/custodian role, not asserted into existence by a builder. Role separation is procedural in this milestone.

## Bundle contract

```text
bundle/
  task.json
  registry.json
  observed.csv                   enrichment/completion only
  sources/                       approved source artifacts
  candidates/<name>/
    generator.py OR generated.csv
    model_spec.json
    evidence.json
    decision.md
    checks.json
    source_checks.json           optional source-statistic plan
    source_tables/              optional submitted simulated-source tables
    source_check_report.json     written by source-checks, once
    freeze.json                 written by freeze, once
```

`demo` emits a complete minimal instance. The authoritative structural rules are in `cohort_harness/contracts.py` and `lifecycle.py`; the Agent interface is in `skills/evidence-cohort-generation/references/harness-interface.md`.

The program ABI is `generate(observed, spec, seed) -> pandas.DataFrame`, called positionally. It must be a top-level synchronous function with exactly three positional parameters, no variadic or keyword-only parameters. `observed` is the permitted input frame (or None for whole-cohort mode), `spec` is the submitted model specification and `seed` is the caller's seed. Parameter names may differ. Use the declared specification for scientific settings; deterministic behavior may be appropriate when justified. No file/network access is part of this interface. Milestone 1 checks syntax and the signature without importing or executing the program; it does not prove that the body respects the interface or is safe to run.

Task variables carry name, kind, unit, role and nullability, with optional bounds/categories. The row identifier is configurable. Enrichment preserves every input column and row order. Completion preserves every measured generated-variable cell as well as all observed cells. Whole-cohort mode has no input table. Identifiers must be unique and outputs finite where numeric. Unsupported fields, unknown source/assumption references and nonfinite parameters are rejected.

An explicit `prior_only` information mode permits empty source/evidence lists and requires model choices to be recorded as assumptions. It must not invent citations to satisfy the published-evidence contract. Such a mode enables a later honest no-retrieval ablation; this version does not launch either arm.

`checks.json` contains `scope` (`fixture_only` or `source_only`), named records with status/detail, and candidate-relative artifact paths/hashes. A hash proves which bytes were submitted, not that a claimed test was correctly executed. The lifecycle binds every regular candidate file, including check records and artifacts, and verifies parent lineage and source commitments. A changed or added candidate file invalidates its previous freeze.

## Source-statistic checks

Implemented declarative operators are arithmetic mean, sample SD (`ddof=1`), Pearson correlation, an OLS coefficient, and event proportion (`1` or `%`). Selection rules and complete-case handling must be explicit. OLS inputs must already be numeric and full rank; no implicit factor encoding, transformations or survey-weight handling is supplied. Unsupported statistics remain evidence records but cannot claim an implemented replay.

Each `source_checks.json` entry includes `id`, `evidence_id`, `status`, `table`, `operator`, `assumption_ids` and `reason`. Status is `computed`, `approximate`, or `not_computable`. A table records its relative `path`, `sha256` and origin (`fixture` or `agent_supplied_simulation`). An operator records `kind`, `unit`, `selection`, `missing_policy` and its statistic-specific fields. See the demo for two complete examples. An approximate check must name existing assumptions. A non-computable entry sets table/operator to null and explains why.

The engine checks statistic kind, unit labels, variable sets and declared adjustment inclusion where representable. A deliberate variable/adjustment mismatch requires an explicit approximation. These checks do not verify that an outcome/exposure was semantically mapped correctly or that the selected rows represent the source population. Publication context still requires substantive review.

The output reports the computed statistic, reported statistic, difference, rows used/dropped and artifact hashes. It does **not** invent an acceptance threshold or p-value. Every computed record states `generation_link_verified: false`: the submitted table has not been independently generated by this harness. A later isolated runner must execute the frozen generator under declared source conditions before a check can certify that link. Source consistency is not target-population validation.

## Sequential milestones

1. **Contracts and source-statistic tools — this version.** Validate three task modes, explicit prior-only mode, evidence/model links, check artifacts, revisions and provenance. Run invented integration and adversarial contract tests.
2. **Bounded execution and evidence gateway.** Integrate existing screened retrieval with task-specific rules and counters. Run frozen Agent-authored code with only required mounts and no custodian data. Preserve outputs, timeouts, failures, seed behavior and real usage counters. Exercise a real Agent turn against a controlled fixture.
3. **Source-context generation and revision.** Bind source-population recipes, generator execution and operator outputs. Let the Agent retrieve/re-extract/revise or retain. Make ordinary iteration and source-check feedback selectable policies under comparable budgets.
4. **Fresh scientific confirmation.** Audit public-case eligibility; freeze method and reserved analyses; compare generated-data analytical utility. Keep existing HDL/insulin cases as development evidence. Evaluate uncertainty separately before claiming calibration.

Do not start a large experiment matrix, new training job or compulsory multi-Agent system merely because the contracts pass. The milestone report records what was actually exercised and what remains unimplemented.
