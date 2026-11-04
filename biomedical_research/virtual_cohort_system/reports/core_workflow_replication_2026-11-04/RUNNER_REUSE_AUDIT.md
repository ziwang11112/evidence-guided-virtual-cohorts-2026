# Runner reuse audit for the proposed core-workflow batch

Date: 2026-11-04. Scope: implementation feasibility only. No new author was dispatched, no generator or evaluator was run, no table was generated, no patient record or target aggregate was read, and no old frozen artifact was modified. The existing reference-bindings metadata was read; it contains paths/hashes/endpoint routes, not target effect values. No scientific family or parameter is recommended here.

## Conclusion

A new shared adapter is feasible using existing mechanics, but neither existing runner is directly suitable. The smallest coherent implementation is a **new copy/adaptation of the main-study session lifecycle**, which already has two trials and three post-decision finals, combined with the evidence-to-generation runner's explicit original/direct-revision family and execution-inventory controls. Reuse the two case-specific generated-only providers and fixed estimator definitions. Do not retarget or edit a frozen runner, bundle, session, or release.

The new allocation is four fresh scientific authors, two per case, at most five physical attempts each: **at most 20 physical attempts and exactly 12 scheduled final slots**, retaining unavailable/failed slots. Final seeds are generated only after that author's immutable selection decision; retention still requires three new final executions. There is no pre-decision delivery or retention alias.

## Exact reusable paths

Project root used below is `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system`.

| Component | Existing path relative to project root | Reuse |
|---|---|---|
| Best lifecycle basis | `work/main_study_freeze_2026-11-03/implementation/main_session_v1.py` | Append-only hash-chain events, reserve-before-execute, two trials, decision gate, three final slots, abandoned constructions, campaign closure |
| Original/direct-revision and inventory checks | `work/evidence_to_generation_2026-11-04/run_session.py` | `family`, `bind_family`, `inventory`, revision parent/freeze commitments; retain successful output identity when feedback fails |
| Postclosure binding pattern | `work/evidence_to_generation_2026-11-04/evaluation/evaluate_build.py` | Exact reservation/result/receipt/output/decision bindings before reference reads; not its B-only endpoint calculations |
| Multi-case aggregate evaluator basis | `work/main_study_freeze_2026-11-03/implementation/evaluate_main.py` | Global closure before reference loading; every scheduled slot including failure; case-specific units |
| Reference routes, no effect values | `work/main_study_freeze_2026-11-03/implementation/reference_bindings.json` | Existing endpoint locations and aggregate hashes; keep coordinator-only |
| CHNS task | `work/main_study_freeze_2026-11-03/cases/CHNS2009/task.json` | Preserve scientific task schema in a new task copy |
| ENSANUT task | `work/main_study_freeze_2026-11-03/cases/ENSANUT2018/task.json` | Preserve scientific task schema in a new task copy |
| CHNS generated-only provider | `work/main_study_freeze_2026-11-03/cases/CHNS2009/generated_provider.py` | `evaluate_generated` and `generated_statistics` |
| ENSANUT generated-only provider | `work/main_study_freeze_2026-11-03/cases/ENSANUT2018/generated_feedback.py` | Same interface, with exact eight-cell gate |
| CHNS fixed estimator dependency | `work/chns_admission_2026-11-01/f2/evaluation/chns_f2_evaluation.py`; `work/chns_admission_2026-11-01/f2/analysis_plan.json` | Only `analyze(..., reference=False)`; do not call the module's clinical reader/evaluation entrypoint |
| ENSANUT pure estimator dependency | `work/autonomous_research_cycle2_2026-10-31/analysis/analytical_engine.py` | `validate_cohort`, cell counts, `analyze_cohort`; preserve pinned bytes |
| Reusable harness | `cohort_harness/execution.py`, `lifecycle.py`, `contracts.py`, `semantic_feedback_v1.py`, `source_checks.py`, `literature.py`, `_vendor/literature_gateway.py` | Existing execution, contracts, immutable candidates, source semantics, retrieval |
| Interface documentation | `docs/SEMANTIC_FEEDBACK_V1.md`, `docs/EXECUTION_ADAPTER.md`, `docs/LITERATURE_ADAPTER.md` | Existing implemented capability boundaries |
| Existing procedural example | `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcBuild01/task.json`, `adapters.json`, `AUTHOR_TASK.md`, `RUN_RULES.json` | Bundle shape only; not a new author template or an authorized retrieval session |

`evcBuild01` has zero query/download budget and no allowed literature actions. Its task uses `person_id` and different unit labels/order. Its candidates, retained decisions, execution state, and run rules must not be transplanted into a fresh author session. The scientific contents of its candidates were not inspected for this audit.

## Essential new-adapter changes and blockers

1. **Allocation and identities.** Replace fixed 24-author/120-attempt main-study checks with an explicit four-author manifest, two CHNS and two ENSANUT, 20-attempt maximum. Use independent fresh external dispatch identifiers. The controller does not launch an LLM or establish fresh context itself. Replace misleading E0/E1 comparative-arm assumptions with the actual unified workflow condition. Both existing providers validate E0/E1 labels; new wrappers must either adapt that procedural validation explicitly or maintain a clearly documented compatibility field without claiming an E0-versus-E1 experiment.

2. **Retrieval must work throughout the allowed author phase.** Main `initialize` requires exactly zero query/download budgets and snapshots every bundle file, including `registry.json`. A legitimate literature fetch appends to that registry, so current `Session.verify` then fails. A new adapter must accept the prospectively bounded nonzero author budgets and literal allowed actions, bind immutable task/session configuration, and verify the registry append-only prefix rather than require the original whole-file digest. Preserve and bind new source artifacts and the final retrieval audit at closure. Bind the gateway implementation under `_vendor/` as a dependency; the existing top-level `cohort_harness/*.py` glob does not cover it. Never reset/move a gateway session to replenish a budget.

3. **One family, at most one feedback revision.** Main `Session.freeze` calls `freeze_candidate` without a parent and does not cap independent candidates. A task's `revisions: 1` limits a lineage, not the number of unrelated initial candidates. Add one initial-family commitment, one optional direct child with parent receipt/revision record, and explicit matching retain/revise decision. Bind actual reviewed feedback and source/usage records into that decision or the new candidate's checks. Borrow these family checks from `run_session.py`; do not borrow its schedule.

4. **Keep the two-trial/three-final schedule.** Main `close_science` already precedes all final attempts and `deliver` reserves only unused final slots. The B runner instead requires initial trial plus three initial deliveries before revision, permits eight attempts, and aliases retained initial deliveries. Those behaviors conflict with this batch and must be absent. Add execution-directory inventory reconciliation from the B runner so any unreserved directory is rejected. All row-producing attempts count, including failed runs and any attempted source/context draw; there is no extra mechanism or source-replay allocation.

5. **Feedback and closure.** Main `trial_feedback` restricts feedback to trials but does not explicitly reject invocation after `science_closed`; add that boundary. Preserve a successful execution/verified table even if semantic feedback or the provider fails, recording those failures separately. Close all four authors, including abandoned ones, before loading either reference aggregate. Closure must bind decision, family, events, feedback, retrieval audit, executions and successful tables. No subsequent author revision is permitted.

6. **Evaluator dimensions and summaries.** Main evaluator hard-codes 72 slots, 24 constructions, five authors per E0/E1 arm and an E1-minus-E0 comparison. Change only the new copy to four constructions/twelve final slots and per-author, within-case summaries. Preserve all null slots and no-retry behavior. Reuse case endpoint bindings; do not use B's `comparison_core.py` schema against main-study endpoint payloads. No pooled cross-case score or arm advantage is identified by this allocation.

7. **Target metadata separation.** Use a new materializer instead of running old `prepare_sessions.py`, which hard-codes E0/E1 packets, 24 sessions, and `evcMS`. Author bundles should contain their assigned task, allowed source artifacts and interfaces, own candidates and generated-only feedback. Keep existing results, target bindings and old candidate science out of author context. Procedural instructions are not OS isolation.

## Schema, key and cell-weight compatibility

| Item | CHNS2009 main-study task | ENSANUT2018 main-study task | Consequence |
|---|---|---|---|
| Exact output columns/order | `row_id,age,female,bmi,glucose,hba1c` | Same | Do not reuse `evcBuild01`'s `person_id` or its different column order |
| Units | year; 1; kg/m^2; mmol/L; % | year; 1; kg/m^2; mg/dL; % | Exact declared unit strings matter in semantic preflight; no silent conversion |
| Task age range | 35–74 | 25–79 | B diagnostic code hard-codes 35–74 and is unsuitable for ENSANUT |
| Scientific output gates | Positive BMI; task permits zero glucose/HbA1c but scientific provider withholds affected analyses for nonpositive glycemia | All three continuous measurements positive; glucose below 126 mg/dL | Contract-valid output does not guarantee analyzable output |
| Composition | No supplied age/sex composition | Exactly 375 in each female 0/1 × 25–39, 40–54, 55–69, 70–79 cell | Generic column validation does not enforce the textual quota; preserve the provider's explicit eight-cell check |
| Estimator/diagnostics | Fixed E1/E2/E3 OLS routes, sample SD and linear quantiles | Equal-stratum WLS, population SD, inverse-CDF weighted quantiles, Q1/Q2/Q3 scaled terms | Do not homogenize to B's HC3/linear-quantile outputs |

ENSANUT weights are `1/(8*n_h)`, giving each cell mass 1/8. When each generated cell contains 375 rows, row weights are equal, but the frozen estimator and quantile conventions still must remain unchanged. Reference cell counts need not be equal. Do not add a synthetic survey-weight or cluster column: neither is in the task schema, and no national-representative interpretation follows. ENSANUT endpoint units include per-ten-year and per-five-BMI-unit effects; these are evaluator definitions, not automatic permitted source-semantic conversions.

## semantic_feedback_v1 and source-operator limits

The reusable interface is `cohort_harness.semantic_feedback_v1`, with no fallback to `whole_cohort_feedback` collection. Its preflight requires `whole_cohort_feedback.json` and a frozen `source_semantics_v1.json` sidecar binding exact evidence/recipe hashes and every check ID, evidence ID and locator. Meaning, outcome/term/adjustment, selection/denominator, units, source n and uncertainty role must be explicitly represented. Sidecar agreement alone does not establish correct extraction.

Implemented operators are mean, sample SD, median/quantile with linear interpolation, Pearson, Spearman, non-intercept unstandardized per-unit OLS coefficients, and proportions. Computation requires known unweighted identity semantics. Weighted/unknown weights and nonidentity/unknown transforms are unavailable. There is no automatic mmol/L–mg/dL conversion, percent/IFCC conversion, standardized-to-unstandardized effect conversion, per-ten/per-five rescaling, survey estimator, or ENSANUT inverse-CDF weighted-quantile source operator. Unsupported definitions remain unavailable; changing labels to pass is invalid.

The B runner allows matched approximate checks on generated target-population rows. That is not independent source-population reconstruction. The main-study controller is stricter: it requires every source check to be unavailable and returns only generated-table diagnostics, with separately reviewed analytic source calculations. Preserve that distinction in the new protocol. Open retrieval can supply new evidence, but it does not create a general source replay engine.

Existing analytic helpers are narrowly bound:
- ENSANUT `cases/ENSANUT2018/source_operators.py` handles three named source-context projection operations using caller-declared finite means/covariances. It neither verifies linkage to the generator nor reconstructs a complex-survey estimator.
- CHNS `cases/CHNS2009/source_operations.py` accepts named Jansen/Pearson operations and explicitly qualified equal-weight source moments; it rejects ordinary-moment Spearman recovery. Its declared affine HbA1c mapping is specific to that helper, not an added semantic-v1 transform capability.

New retrieved statistics outside these bound operation IDs need a separately reviewed analytic definition or an unavailable record. No new sampling-based source table should be created outside the five-attempt author budget.

## Current command shapes; none executed in this audit

Run from the project root, with a **new** bundle whose task already permits the actions and budgets:

```text
python -m cohort_harness.literature --bundle NEW_BUNDLE init
python -m cohort_harness.literature --bundle NEW_BUNDLE search --query "AUTHOR_QUERY" --limit 10
python -m cohort_harness.literature --bundle NEW_BUNDLE fetch --pmcid PMCID --version VERSION
python -m cohort_harness.literature --bundle NEW_BUNDLE list-supplements --pmcid PMCID
python -m cohort_harness.literature --bundle NEW_BUNDLE fetch-supplement --pmcid PMCID --supplement-id ID
python -m cohort_harness validate --bundle NEW_BUNDLE --candidate initial
python -m cohort_harness.semantic_feedback_v1 preflight --bundle NEW_BUNDLE --candidate candidates/initial
python -m cohort_harness verify --bundle NEW_BUNDLE --candidate initial
python -m cohort_harness verify-execution --bundle NEW_BUNDLE --run-id RUN_ID
python -m cohort_harness.semantic_feedback_v1 verify --bundle NEW_BUNDLE --candidate candidates/initial --run-id RUN_ID --feedback-id FEEDBACK_ID
```

The main session has a Python API, not a CLI. A new adapter can preserve this orchestration shape:

```python
initialize(new_author_root, profile, provider, author_id=author_id, dependencies=bound_dependencies)
s = Session(new_author_root)
s.activate(new_batch_release)
s.dispatch(actual_fresh_external_author_id)
s.freeze("candidates/initial")
s.trial("candidates/initial", scheduled_trial_seed)
s.trial_feedback(actual_run_id)
# Optional one direct revision and at most one remaining trial, within two total.
s.close_science(selected_candidate, author_decision, independent_review)
s.deliver()  # Three fresh final attempts after selection, including retain.
# Only after all four sessions close: aggregate evaluator.
```

The optional revised `freeze` needs the new parent/revision arguments; the existing main API does not have them. Direct `python -m cohort_harness execute ...` is an implementation backend, not the author entrypoint: bypassing the new reservation ledger would defeat budget enforcement. Existing lifecycle CLI shapes for controller use are `freeze --candidate revised --parent initial --revision FILE` and `execute --bundle ... --candidate ... --run-id ... --seed ... --runtime CONFIG`; execution must remain inside the charged wrapper.

## Runtime and retrieval limits; verification still needed before execution

Only the configured Ubuntu-24.04 WSL/bubblewrap runtime is accepted. Paths are hard-coded to `/home/zwang/.cache/evidence-cohort-runtime/m2/venv` and `/home/zwang/.cache/evidence-cohort-runtime/m2/bubblewrap/usr/bin/bwrap`. The adapter requires a local Windows drive path, not UNC. The existing `work/evidence_to_generation_2026-11-04/RUNTIME_PREFLIGHT.json` records Python 3.12.3, NumPy 2.4.5, pandas 3.0.3 and five runtime-file hashes; it is historical evidence, not a new readiness check.

Execution defaults are 30 seconds, 1024 MiB, 20 MB output and 100 KB logs; the B wrapper explicitly uses 1536 MiB. Freeze a single trusted batch resource policy before any attempt. The runtime mounts only generator/task/spec/worker and allowed observations (none here), not arbitrary candidate auxiliary files or sources. Confirm author dependencies fit the installed runtime without executing their generator locally. No failed or missing backend fallback is authorized. Resource limits are per-process plus wall timeout, not cgroup-wide aggregate resource isolation.

Literature access is the supplied screened PMC-oriented gateway, not unrestricted web/PDF retrieval. It supports the implemented XML/text/HTML/table/supplement paths, has 16 MiB response caps, 30-second requests, search pages up to ten records, and a one-million-cell table parser cap. Required metadata lookup on fetch can consume query budget; failed/rejected attempts remain charged; source versions require explicit selection. One fixed session per bundle spans construction and revision. “Open retrieval” should therefore mean open author-selected queries within this adapter's finite limits. Other retrieval routes are unavailable unless separately admitted and logged.

No new network/runtime preflight or mock test was run for this audit. Before launch, the new adapter still requires targeted no-row tests for allocation/caps, lineage, append-only retrieval, post-decision final gating, failed-slot accounting, feedback failure preservation, exact ENSANUT cell rejection, and all-four closure before reference bytes. Those are implementation checks, not scientific validation. The old tests and reviewed frozen code are reusable patterns, not proof that the new adapter already works.

