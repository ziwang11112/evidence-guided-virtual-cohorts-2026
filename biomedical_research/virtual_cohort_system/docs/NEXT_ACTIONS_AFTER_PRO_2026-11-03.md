# Next actions after Pro and the user's scope corrections

Status: integrated implementation plan, based on a fresh static capability audit. No new generator, patient analysis, runtime preflight or experiment was executed while preparing this plan. The completed 3 November continuation remains closed. This is the current next-action reference; it consolidates the review, adaptive scope and optional ablation design.

## Decision

Prioritize a working, purpose-aware Agent that delivers useful biomedical data with access to relevant evidence, numerical tools and revision. Research questions are visible. Generators may adapt across requests. Real-reference statistics can be inputs or feedback when declared; agreement with those statistics is then reference consistency, not independent validation. Whole-cohort generation without individual input remains central.

Adopt Pro's evidence-coverage audit, bounded numerical source trials, separation of assumptions from measured evidence, use-specific evaluation and sampling uncertainty. Do not turn the proposed sampling benchmark into a prerequisite for every generation task, require one immutable generator across tasks, or make multiple Agents/training/new datasets mandatory.

## 1. Wire the adaptive scientific turn into existing tools

The capability audit found functioning code interfaces for literature retrieval, candidate execution, source contexts, reviewed HbA1c conversion, feedback and version records. The experiment-specific controller fixes authors, versions, contexts and seeds; it is not a general adaptive Agent session. The next implementation should add a small task/session wrapper around existing components and an externally dispatched scientific Agent turn. It should not rebuild those components or patch the old release.

The new task should expose research purpose, available reference information and ordinary resource limits; allow scoped retrieval, author-side numerical trials, structure/parameter revision and retention; and return actual tool results to the author. Check actual runtime availability at execution time. Preserve concise code/evidence/version records, with complete attempt accounting, rather than requiring a new administrative project for each trial.

Verified static reuse map:

| Capability | Existing path / entry point |
|---|---|
| Task-scoped retrieval and source registration | `cohort_harness/literature.py::run_literature` |
| Program or direct-table execution | `cohort_harness/execution.py::run_candidate`; `python -m cohort_harness execute` |
| Whole-cohort source-context preparation and execution | `work/scaleup_2026-11-01/bridge/context_bridge.py::{prepare,binding_requests,seal,execute,verify}` |
| Strict execution-linked semantic feedback | `cohort_harness/semantic_feedback_v1.py::{preflight,collect_feedback,verify_feedback}` |
| Reviewed qualified OLS/Pearson/Spearman and HbA1c response conversion | `work/evidence_revision_v1_2026-11-02/implementation/qualified_relationships_v1.py::compute_qualified_feedback` |
| Source phase and feedback delivery | `work/evidence_revision_v1_2026-11-02/implementation/revision_controller_v1.py::{open_source_phase,dispatch_sources,source_feedback_packet,record_decision}` |

Keep strict semantic feedback and qualified approximations distinguishable. The newer bridge supports whole-cohort generator programs with declared contexts; it does not automatically support arbitrary direct-table context replay. The legacy calibration adapter remains enrichment-specific. Do not present it as an already working whole-cohort optimizer; first use the available execution and numerical checks, adding only a small missing adapter if needed for an actual chosen construction. These findings concern code interfaces; they are not a new live runtime verification.

## 2. Run one generous-information development request first

Use existing CHNS materials and the current age/sex/BMI/fasting-glucose/HbA1c task. No new cohort acquisition is a prerequisite. Ask for a complete adult virtual cohort suitable for the already stated adjusted BMI, glucose and age analyses. Supply the existing full reference-summary set and external evidence as declared developmental inputs; do not cherry-pick only favorable statistics. No individual observations need enter the whole-cohort generator. This reference-assisted regime is intentionally different from an external-literature-only regime.

Revisit already selected source papers for relevant excluded/omitted evidence, particularly age associations, while retaining their actual adjustment sets and applicability. The Agent chooses a law and parameters; the coordinator does not translate a desired target answer into a mandatory generating coefficient. The Agent may use provided statistics as numerical constraints and can report incompatibility or multiple plausible constructions.

Start with one new scientific construction, retain its initial data, provide numerical feedback, and obtain a revised or retained final version. The task/session implementation must state a small total author/retrieval/trial budget before dispatch, including internal simulations, rather than inheriting or resetting closed budgets. For a stochastic program, three fixed delivery seeds per stage would give at most six delivery tables; working/source trials must be counted separately within the total budget. A direct-row route must not count repeated copies as independent draws.

This is an integration and data-use feasibility pilot, not a new independent CHNS validation or a claim that feedback must improve every result. If the initial output already fits its intended use, retention is legitimate. If performance changes, report gains and losses together. Deliver usable local data, a short evidence/assumption record, actual initial/final analysis summaries and costs.

## 3. Improve evaluation alongside generation

Evaluate fit to given reference distributions and relationships, and the scientific analyses the task requests. Preserve reference sampling uncertainty and conditional generation variation separately. Exact agreement with a real sample is not required; ungrounded tolerances cannot be selected after observing results. A favorable coefficient does not establish tail, prevalence or general joint-distribution utility.

Pro's proposed 2,000-replicate reference-derived sampling diagnostic remains a separate bounded support task using existing data and unchanged old generators. Its independently reviewed formulas provide an ideal-reference noise benchmark, not candidate-specific equivalence. It should not delay wiring the Agent or expand into a general benchmarking project. See `pro_evaluation_review_2026-11-03/REVIEW_SYNTHESIS.md` for qualifications and the implementation checks still needed.

If an existing comparable dataset or an appropriate previously unused portion is available, define its evaluation role before viewing its results. Check population, measurement and selection comparability. Once its results inform revision, describe that exposure. If all available references are used, report developmental consistency and the remaining external-validation gap; do not invent an independent comparator or start a new acquisition campaign automatically.

## 4. Expand only after the adaptive loop actually works

The optional four-cell experiment is: external literature versus explicitly supplied extra real-reference summaries, each at initial delivery and after an additional feedback stage. Its full design is in `INFORMATION_AND_REVISION_ABLATION_DESIGN_2026-11-03.md`. Agent tool access remains ordinary and task-adaptive. Use paired revisions, common evaluation definitions and honest information/compute accounting. Additional information is not algorithm superiority; additional iteration includes extra computation.

For scale planning, three independent constructions per information condition, paired initial/final versions and three delivery seeds would yield 36 delivery slots. This is illustrative, not an execution release, and excludes internal/source trial costs. Repeated or retained outputs do not increase the number of independent scientific constructions. A pilot selected during development should not be silently pooled into a later prospectively defined comparison.

## Decisions that determine whether to continue

- If basic execution, evidence use or provided-reference consistency fails, repair the identified implementation/model issue before scaling.
- If reference consistency improves while unrelated relationships deteriorate, report the trade-off and identify the unsupported joint assumptions.
- If exposed-reference quality is useful but external performance is weak, retain the supported reference-assisted use and state the transport limitation.
- If a component adds no useful data improvement or only overhead, simplify it; a no-op does not invalidate every data-generation use.
- Do not require success on every optional capability or expand cases merely to obtain a favorable result.

The immediate engineering deliverable is the small adaptive task/session connection and one actual initial-to-final data-generation run. The paper's contribution will be judged from the resulting data and scientific analyses, not from the number of control files, Agents or checks.
