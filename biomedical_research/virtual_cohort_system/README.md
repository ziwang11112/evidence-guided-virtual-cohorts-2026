# Evidence-guided virtual cohort system

Version 0.5.0 — frozen structural alternatives on a new public-data period, 28 October 2026. M1–M4 reports remain historical snapshots.

See [M5 new-period results](MILESTONE_5_RESULTS.md), [current validation](m5_validation.json), [M4 source-only development results](MILESTONE_4_RESULTS.md), [M3 target results and limitations](MILESTONE_3_RESULTS.md), [historical M2 progress](MILESTONE_2_PROGRESS.md), and the [interactive architecture document](docs/system-explorer/index.html). The HTML retains its labelled M1 snapshot and links to newer progress.

The objective is to let a capable Agent integrate permitted research evidence into reusable virtual data for biomedical analysis. The system supports three task contracts: whole-cohort generation, enrichment with an entirely unmeasured variable, and completion of missing cells. Program generation and direct row submission are both legitimate routes. M1 supplied contracts/checks; M2 added literature access and explicit execution. M3 links enrichment-program execution to source feedback and Agent revision. One TG pilot showed partial improvement and a worsened sex contrast; general superiority remains unestablished. M4 adds median/quantile/Spearman source checks and fixed-seed feedback portfolios, ending in a retention decision without a new target evaluation. M5 freezes three source-informed structural alternatives before a new NHANES 2021–2023 evaluation (n=2,660). All 15 generated tables reproduce the positive age and negative global BMI-curvature directions, including negative raw-scale curvature. BMI effect magnitudes remain too large, interaction signs are unstable, and source mismatches persist. This is temporal robustness within shared assumptions, not proof of source compatibility, ordinary-Agent superiority or general synthetic-data validity.

## Responsibilities

| Layer | Responsibility | Current implementation |
|---|---|---|
| Task owner / custodian | Define visible inputs, permitted evidence, scientific use, budgets and separately reserved analyses | Typed visible task contract; no target evaluator in the builder package |
| Agent skill | Select evidence, interpret study context, choose generator/parameters, explain assumptions and revise | Concise reusable skill supplied; LLM turns still dispatched by the calling environment, not a standalone API launcher |
| Tool harness | Validate contracts, calculate declared source statistics, bind artifacts and retain revisions | Implemented |
| Evidence gateway | Search/fetch/screen literature, enforce real query budgets and register provenance | Task-bound adapter with a fixed bundle session; screened sources appended to the registry |
| Execution environment | Run frozen generation with curated filesystem mounts and no network | WSL/bubblewrap adapter; generator process only, no broad workspace mount and no local fallback; not isolation of the LLM's file/tool access |
| Independent evaluation | Apply locked analyses to generated and real data after freeze | Existing study evaluators remain unchanged; generic adapter is a later milestone |

The harness does not select biological effects, coefficients, distributions, scientific success thresholds or a required number of Agents. Source files are data, not instructions. A registry records approved artifacts; it is not a content filter, authentication system or filesystem sandbox. The supplied literature adapter enforces its task-bound query limits; unrelated LLM tools are not constrained by this adapter.

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

Explicit adapters (only with supplied task permissions and trusted runtime configuration):

```text
python -m cohort_harness.literature --bundle PATH search --query QUERY
python -m cohort_harness.literature --bundle PATH fetch --pmcid PMCID --version N
python -m cohort_harness execute --bundle PATH --candidate NAME --run-id NEW_RUN --seed SEED --runtime CONFIG
python -m cohort_harness verify-execution --bundle PATH --run-id NEW_RUN
python -m cohort_harness source-replay --bundle PATH --candidate NAME --replay-id NEW_ID --seed SEED --runtime CONFIG
python -m cohort_harness verify-source-replay --bundle PATH --replay-id NEW_ID --candidate NAME
```

See [literature access](docs/LITERATURE_ADAPTER.md), [execution](docs/EXECUTION_ADAPTER.md), and [source replay](docs/SOURCE_REPLAY.md). `validate` remains static. Execution requires a frozen candidate, writes a new `executions/NEW_RUN/` directory and preserves failures. Failure to obtain the configured isolated runtime does not permit execution on the host. A successful integrity verification of a failed-run receipt does not change that run's failed status. Resource limits include wall-clock termination and per-process limits; they are not an aggregate cgroup memory guarantee.

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

The output reports the computed statistic, reported statistic, difference, rows used/dropped and artifact hashes. It does **not** invent an acceptance threshold or p-value. Every computed record still states `generation_link_verified: false`: the source-check submission is not automatically linked to a verified execution receipt. The new execution adapter must next be connected to declared source conditions and source-check tables before this link can be certified. Source consistency is not target-population validation.

## Sequential milestones

1. **Contracts and source-statistic tools — this version.** Validate three task modes, explicit prior-only mode, evidence/model links, check artifacts, revisions and provenance. Run invented integration and adversarial contract tests.
2. **Execution and evidence adapters — current development.** Task-bound retrieval and generator-only WSL execution are implemented. Exercise real Agent submissions on invented fixtures; preserve failures and actual usage. A standalone model launcher and isolation of the builder's general tools are not supplied by these adapters.
3. **Source-context generation and revision.** Bind source-population recipes, generator execution and operator outputs. Let the Agent retrieve/re-extract/revise or retain. Make ordinary iteration and source-check feedback selectable policies under comparable budgets.
4. **Fresh scientific confirmation.** Audit public-case eligibility; freeze method and reserved analyses; compare generated-data analytical utility. Keep existing HDL/insulin cases as development evidence. Evaluate uncertainty separately before claiming calibration.

Do not start a large experiment matrix, new training job or compulsory multi-Agent system merely because the contracts pass. The milestone report records what was actually exercised and what remains unimplemented.

## Current source-feedback interfaces

See [source statistic definitions](docs/SOURCE_CHECKS.md) and [fixed-seed source portfolios](docs/SOURCE_PORTFOLIO.md). Blinded builders must receive only task-approved interface/source inputs; this README and milestone reports contain target results and are evaluator/controller material.
