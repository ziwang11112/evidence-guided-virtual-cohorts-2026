# Whole-cohort source-context review

2026-10-31. Read-only implementation review; the only file written is this note. No generator was run, no scientific model or coefficient was supplied, and no target/private/results contents were read. Review covers the public harness modules, documentation, artificial examples, and test definitions. It does not assess whether any particular Lifelines/NHANES paper is admissible or sufficient.

## Decision for this cycle

**GO with existing execution and feedback interfaces plus explicitly frozen source-context specifications, if the Agent can defend the source populations from admitted aggregate evidence. No core harness change is necessary.** Use separately frozen whole-cohort bundles for each declared source population. Execute the same Agent-authored program in each bundle; compute statistics using the existing `whole_cohort_feedback` collector on that bundle's verified output. This makes each feedback report refer to the population actually generated.

The smallest defensible claim is “the same frozen scientific construction, instantiated under explicitly declared source contexts.” It is not “byte-identical complete model specifications” if a context block changes. Preserve that distinction in reporting. A short cross-bundle manifest/audit should establish the shared construction and exact allowed context differences; existing individual execution receipts alone do not establish it.

**NO-GO for calling the present target-population feedback a reconstruction of an independent source population. NO-GO for passing source individual covariates or silently adapting enrichment replay to this task.** If source-context construction is unsupported, retain the source check as approximate or not computable, with the substantive reason. Do not delay the ordinary Agent case to build a generic framework. The ordinary Agent route remains valid, and this review imposes no benchmark ablation.

## What the code actually supports

| Existing component | Relevant behavior | Consequence |
|---|---|---|
| `cohort_harness/whole_cohort_feedback.py:43,77` | Recipe population must equal task population; reads only a successful verified whole-cohort output; identity measurement only | Already suitable for a source-population bundle, but does not construct or certify that population |
| `cohort_harness/source_replay.py:93,132` | Enrichment only; requires covariate CSV; copies candidate bytes to a child | Cannot serve this aggregate-only whole-cohort case |
| `cohort_harness/source_replay_v2.py:111` and `source_context.py:52` | Independent supports, but still enrichment and source-frame inputs | Useful design precedent for separate supports, not a directly reusable whole-cohort adapter |
| `cohort_harness/_worker.py:39,47` | Calls `generate(None, specification, seed)` for whole cohort | All context inputs must be available through the frozen specification, or an explicitly authored read of the staged task |
| `cohort_harness/execution.py:226` | Stages task, specification, program, request, worker; no arbitrary auxiliary candidate file staging | Adding a standalone `context.json` does not make it visible to the program |
| `cohort_harness/lifecycle.py:116,225` | Freezes all candidate artifacts; verifies whole-cohort mode has no observed input | Auxiliary context plans can be committed before execution without editing core contracts |
| `cohort_harness/whole_cohort_feedback.py:36` | Receipt binds collector and contracts/execution/lifecycle/source_checks/source_replay implementation hashes | Editing these old modules can invalidate historical feedback verification; avoid it |

The artificial `examples/m17a_whole_cohort.py` already demonstrates the needed ABI, whole-cohort task, aggregate evidence, model parameter provenance and frozen feedback recipe. It is a mechanical example, not a biomedical construction to reuse. `examples/prepare_m17b.py` demonstrates aggregate-only preparation and admission, not separate source reconstruction.

## Recommended minimal contract

The Agent writes a single `generator.py` and a complete context-aware scientific specification. The controller does not invent distributions, adjust slopes, replace residual variances, choose outcome thresholds, or reconstruct age/sex/BMI rows. The same program must generate all five scientific variables—age, sex, BMI, FPG and HbA1c—from the permitted aggregate evidence and declared assumptions in each context. Source input is a specification, never a patient table.

Prefer ordinary specification wrappers using the existing ABI:

- A shared scientific block contains the structural model, globally fixed parameters, algorithms, transformations, dependence assumptions and any declared context-response rule. The Agent authors it. It is identical across all context wrappers for a candidate revision.
- A context block contains a stable context identifier, generated row count, population definition, eligibility definition, and the admitted aggregate distribution descriptors or conditioning values the Agent's model actually needs. Every varying field is explicitly allowlisted before feedback. Its scientific meaning and evidence/provenance are declared.
- `parameter_provenance` remains complete under the existing `validate_spec` contract: one entry per top-level parameter. Nested objects are supported, but their nested scientific contents still need traceable explanations. Do not use the flexibility of nested JSON to hide unreviewed coefficients or patient records.
- Every complete per-context `model_spec.json`, `task.json` and `whole_cohort_feedback.json` is frozen before the first feedback-producing execution. The full generator file is byte-identical. Compare the shared scientific block with a specified canonical JSON encoding, and bind the entire wrapper file separately. Include shared provenance and assumptions in the identity projection, not merely numerical parameters.

Different outcome-generating coefficients hidden in a context block would defeat the intended shared-construction claim. If an Agent explicitly proposes source-varying effects, these need a predeclared common rule and evidential basis; report that weaker/shared-rule claim honestly. They cannot be introduced by controller repair after seeing discrepancies. Context-specific age/sex/BMI distributions are legitimate population inputs only when justified as such; their full joint distribution is generally not identified by marginal summaries.

A practical sequence is:

1. Before freeze, the Agent supplies the common program, common scientific definition, all context wrappers, source evidence mappings, assumptions and diagnostic definitions. The target task stays limited to its public design; reserved Mexico ENSANUT information is not a source context or permitted evidence.
2. Bind a `source_context_plan.json` and exact authored context task/specification/recipe artifacts inside the primary candidate. This is an auxiliary declared plan, not a new accepted harness schema. It can be frozen by the current lifecycle.
3. Mechanically prepare one whole-cohort source bundle per context in a fresh controller output directory. Copy the generator, admitted evidence and source artifacts, and the exact preauthored context task/specification/recipe. Preserve the information exclusions and budget accounting. Freeze each bundle. This is a derived execution bundle, not an extra scientific revision.
4. Record an outer manifest binding the parent freeze, plan, generator, shared-science projection, complete context artifacts and child freezes. Independently compare the exact declared fields, rather than accepting an arbitrary “same model” Boolean. It is acceptable to perform these few checks in a case-local controller script this cycle.
5. Use only `execution.run_candidate`/the existing execute CLI. Require successful verified generator execution. Call `whole_cohort_feedback.collect_feedback` and `verify_feedback` with the specific child candidate/run. Preserve unsuccessful runs and their errors. Use new IDs for retries.
6. Assemble source-only diagnostics that retain each context, source estimate, uncertainty, calculation, discrepancy and assumptions. Any Agent revision is a new primary parent-linked candidate within the original revision budget, binding the actual feedback used. Freeze its complete source-context definitions again.

The outer manifest must explicitly say that cross-bundle construction identity is checked by the new case audit, while child execution/output linkage is checked by the existing harness. Existing feedback does not automatically verify a relationship between two independent bundles. Hashes remain relative commitments, not authorship proof or protection against a host rewriting a whole record.

## Other implementation options

| Option | Exact implementation files if adopted | Approximate work | Recommendation |
|---|---|---|---|
| Existing APIs plus case-local wrappers/audit | New `work/autonomous_research_cycle2_2026-10-31/method/run_source_contexts.py`; new focused `.../method/test_source_contexts.py`; the Agent's candidate `source_context_plan.json` and `source_contexts/<id>/{task.json,model_spec.json,whole_cohort_feedback.json}` | About 150–250 lines of mechanical orchestration/identity checks and 100–180 lines of focused tests; no existing harness file changes | Preferred if needed this cycle; per-case data files are authored inputs, not new infrastructure |
| Exact generator **and complete specification** identity using staged task selection | Same case-local runner/audit; Agent writes program that explicitly reads `/input/task.json`, selects an already-frozen context from a complete common specification, and rejects unknown selectors | Similar orchestration; fewer spec differences, extra program dependency on the sandbox task path | Technically possible because task is staged, but less clean than the ABI wrapper. Select via an unambiguous frozen task identifier with exact mapping; do not infer population semantics from prose. The controller supplies no science |
| New reusable whole-cohort source adapter | New `cohort_harness/whole_cohort_source_contexts.py`; new `tests/test_whole_cohort_source_contexts.py`; new `examples/prepare_whole_cohort_source_contexts.py`; new `docs/WHOLE_COHORT_SOURCE_CONTEXTS.md` | Roughly 250–400 implementation lines plus 200–350 test/example lines, including strict plan validation, derivation, receipt/reverification, failures and append-only paths | Defer until more than one case needs it. Use a dedicated `python -m ...` entry point, avoiding edits to `__main__.py` and all hash-bound old modules |

These are estimates, not implementation commitments. The case-local route can be even smaller when all bundles are prepared directly by the Agent, but it still needs explicit cross-bundle identity verification. A generic adapter should reuse existing public lifecycle/execution/feedback functions, not copy or modify statistical algorithms. It should not retrofit whole-cohort branches into `source_replay`, `source_replay_v2`, `source_context`, `_worker`, or `whole_cohort_feedback`. Historical verifiers and their documented version requirements remain unchanged.

Direct-row submissions remain a supported ordinary whole-cohort route. Separate Agent-authored tables can have source diagnostics, but cannot establish that the same scientific program was run across contexts; do not force an execution claim onto that route.

## Source, target and computational eligibility

Keep three notions separate: the source paper's eligible population; the public target design; and the computational support over which the common model is claimed to work. Source and target supports may differ or even be disjoint. Do not truncate a source population to target ages or BMI bounds merely to pass the target contract. Conversely, widening a source task does not establish scientific transportability.

For separate bundles, author the correct source task column supports. Preserve ordered variable names, types, units, roles and nullability unless a deliberate new construction is being declared. Record source and target support differences and require both within the declared computational domain. The existing whole-cohort task validator enforces each bundle's support; it does **not** enforce this cross-context domain relation. A case audit may compare declarations without executing Agent code. Do not call `compile_source_task` with a dummy source frame: it intentionally rejects whole-cohort mode.

Eligibility is more than numeric bounds. For each check, define age limits, sex coding, recruitment setting, fasting requirement, diabetes/medication/pregnancy exclusions, complete-case population, and measurement definition wherever the admitted paper reports them. Five generated variables cannot implement selection on an absent medication or diagnosis variable. A source-specific conditional population can be represented only if the Agent actually defines and justifies it; assigning a population label or treating a glucose threshold as equivalent to clinical diagnosis/medication exclusion is insufficient. If required selection is unavailable, label the approximation with its specific assumption or retain `not_computable`.

Likewise, define FPG specimen/units and HbA1c scale/measurement assumptions explicitly. The collector performs no conversion, factor encoding or measurement harmonization. Any conversion must be Agent-authored upstream, evidence-backed, frozen and described; the feedback operators then work on the final common units. Missing-value and selection rules must match the reported estimand as closely as permitted.

Simulation row count is a declared Monte Carlo design choice, not automatically the source paper's sample size. Use a fixed seed/run schedule chosen before feedback. If repeated source draws are needed, retain each receipt and report Monte Carlo variability separately from published sampling uncertainty, model uncertainty and transport uncertainty. Do not let a larger simulated sample suggest increased precision of the evidence. Nothing in this review requires a new repeated-run benchmark.

## What statistics can honestly be compared

The existing engine supports unweighted mean, sample SD, linear median/quantile, Pearson correlation, average-tie Spearman correlation, numeric full-rank OLS coefficients and simple event proportions, with declared AND selections and missing policies. Use the actual source statistic kind, variables, adjustment set, units and quantile convention. Preserve all original estimates and uncertainty.

Source-population reconstruction from aggregates nearly always adds assumptions, so the resulting source checks should normally be `approximate`. A numerical operator being exactly computable does not erase a population reconstruction or measurement approximation. `computed` requires no context/check assumptions under the current metadata contract. Empty selections, constant correlations and rank-deficient regressions remain `not_computable` rather than receiving invented numbers.

Survey weighting, survey variance, logistic effects, partial rank correlations, transformed regressions and adjustments involving absent variables are not supplied by these operators. A reported NHANES weighted population mean might be compared approximately with a draw from a declared population distribution, but that does not reproduce the paper's survey estimator or its design-based variance. Explain that estimand assumption; do not silently relabel the published result as an unweighted sample statistic. Unsupported analyses stay visible as `not_computable` unless a separately reviewed Agent-authored analysis is explicitly within the task.

Differences remain diagnostic, not an automatic pooled loss or acceptance threshold. Passing source checks does not prove validity for the reserved target cohort, identify an otherwise underdetermined joint distribution, or calibrate uncertainty.

## Necessary verification, proportional to the chosen route

For case-local orchestration, new tests should address the new relationship between bundles, not reimplement all existing operator tests:

- Two artificial aggregate contexts with different row counts/supports run through the same program/shared-science projection and retain the correct population in each feedback; preparation and execution stage no observed or individual source table.
- Changed generator, shared scientific values/provenance, unapproved wrapper fields, mismatched task/specification context, and a feedback report from the wrong child/run are rejected. All context definitions are bound before any accepted feedback.
- Invalid whole-cohort columns, an observed file, out-of-domain declared support, missing context provenance, excluded source declarations, unsafe/reused paths and altered child receipts fail closed. Source support differing from target support is accepted when explicitly declared inside the common computational domain.
- A backend failure is retained and cannot produce successful source linkage; no host import, execution or fallback of Agent code occurs. One actual small invented WSL/bubblewrap smoke is needed before claiming the new orchestration works with isolation. Mocked tests alone cannot establish this.
- Retained parent/context files are unchanged; existing freeze/execution/feedback verification still succeeds. Use existing operator tests for numerical definitions and one hand-calculated artificial source statistic for the new wiring.

For a reusable adapter, additionally test full report recomputation, appended/removed files, engine/version changes, failed partial contexts, invalid plan schemas and historical verifier separation. No new tests or runtime claims are made by this review; only code and documentation were inspected.

The unavoidable substantive gate is source adequacy: the Agent must explain how admitted aggregate evidence supports each context's distribution and selection. A general adapter cannot supply that missing science. Proceed with the actual case using existing interfaces whenever that explanation is sufficient, and keep unsupported source diagnostics explicit when it is not.
