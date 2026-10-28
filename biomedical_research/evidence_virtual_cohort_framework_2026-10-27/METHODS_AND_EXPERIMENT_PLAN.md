# Evidence-guided virtual cohorts for biomedical research rehearsal

27 October 2026. Working method-paper plan following the user's decision to evaluate scientific conclusion preservation and practical research use, rather than demand exact reproduction of every value. This document separates implemented machinery, retrospective development results and proposed experiments. It does not preregister already inspected data.

**Execution update:** Stage 0 and the bounded three-case Stage 1 are complete. Stage 1 generated all 420 scheduled cohorts and produced all 7,700 analysis records under `stage1_v3`; see [results](stage1/RESULTS.md) and [decision](stage1/DECISION.md). The scenario policy is implemented, but it did not show consistent reserved-analysis improvement. Stage 2 expansion and Stage 3 study-planning claims remain conditional and unrun. The design below is retained to distinguish the intended paper from the evidence actually obtained.

## 1. Intended contribution and use

**Research question:** Can an Agent turn limited study evidence and, when available, partial individual records into reusable virtual cohorts that support credible *unprovided* analyses, and indicate when the evidence cannot support a research decision?

The intended users want to prepare analysis code, compare measurement or follow-up plans, examine plausible heterogeneity, and decide what real information to collect next. The deliverable is a generator, virtual tables, provenance and an analysis-specific evidence/uncertainty report. Reproducing an observed association is useful; it is not new evidence that the association is true. Virtual rows do not increase the number of observed patients.

Three levels of contribution must be kept distinct:

1. **Usable research software:** valid tables, reproducible programs, source traceability and runnable analysis examples. This is an engineering deliverable already partly implemented.
2. **A validated method:** a shared construction/revision policy preserves reserved analyses across studies and helps a specified research decision, with appropriate comparisons. This is the paper's proposed contribution, not an achieved result.
3. **New biological or clinical discoveries:** require independent empirical support; not the current paper's promised output.

Working title: **Evidence-Guided Virtual Cohorts for Biomedical Analysis and Study Planning**. Keep this neutral title until independent results justify stronger words such as reliable, calibrated or improved.

## 2. What the existing evidence establishes

| Experiment | Supported observation | Boundary |
|---|---|---|
| Ross 75-person longitudinal PFS completion | Both selected qualitative conclusions survive in three masks; Agent cell prediction and coefficient recovery outperform this MICE reference | Missing-only also preserves those conclusions; primary coefficient recovery does not improve over missing-only; only 54 PFS cells per mask are filled |
| Ross whole-cohort generation, 20 seeds | Several supplied trends and the relation between two discounting measures are preserved | Several unprovided cross-domain dependencies are not; one builder and one exposed cohort |
| Direct records versus program generation | Both routes run; improving marginal matching can worsen unprovided change relationships | One lineage per route, with target-derived summaries; not a stable method ranking |
| Adult 12-person and pediatric 44-completer paired pilots | Published paired analyses can be replayed on generated records | Paired variance distortion and a synthetic significant pediatric TG result occur; marginal agreement is insufficient |
| Earlier shared revision policy and evidence acquisition | Shared execution, evidence trace and audit work | Neither a consistent superiority of structured revision nor reliable cross-study transfer has been shown |

Keep all of these records. The new definition of intended usefulness does not erase the earlier coefficient-recovery or revision-policy results.

## 3. Nearest work and the actual novelty question

These are primary-source checks, not a systematic review or proof of originality.

| Prior | Existing contribution that we must acknowledge | What remains to test here |
|---|---|---|
| [G-Sim, ICML 2025](https://proceedings.mlr.press/v267/holt25b.html) | LLM simulator construction/refinement with numerical calibration and diagnostic feedback | Real-cohort analytical validity under study-level, population-specific evidence |
| [SynthCraft, PLOS Digital Health 2026](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001290) | Agent orchestration of synthetic biomedical data tools and evaluation | Evidence-limited inputs and reserved scientific analyses, beyond workflow automation |
| [SPADA, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.525/) | LLM dependency structures coupled to statistical conditional generators | Study/measurement applicability and uncertainty of unobserved relationships |
| [LLMSynthor, KDD 2026 author manuscript](https://arxiv.org/html/2505.14752v4) | Aggregate statistics to micro-records using LLM priors and iterative discrepancies | Biomedical inference and decision consequences, rather than aggregate-to-record generation itself |
| [DALL-M, 2025](https://doi.org/10.1016/j.compbiomed.2025.110022) | Contextual clinical feature augmentation/completion using retrieval and LLMs | Distributions of completions, uncertainty and held-out estimands |
| [MeLD, Nature Communications 2026](https://www.nature.com/articles/s41467-026-74492-0) | Longitudinal synthetic health records evaluated on time-to-event patterns and risk-factor associations | Evidence-conditioned synthesis without a full target training cohort; this work already evaluates scientific relationships |
| [Task Exchangeability, 2026 preprint](https://arxiv.org/abs/2606.13629) | Calibration of real–synthetic discrepancies across tasks under explicit assumptions | Whether biomedical tasks satisfy useful assumptions; no coverage guarantee is borrowed without checking them |
| [EmulatRx, Nature Communications 2026](https://www.nature.com/articles/s41467-026-74501-2) | Agentic real-world-data trial emulation/design | Virtual-cohort-driven decisions under sparse evidence, rather than general Agent trial planning |

Earlier [longitudinal nutrition synthesis work](https://arxiv.org/abs/2305.07685) explicitly evaluated reproduction of published analyses. Consequently, neither preserving scientific results nor calling the output a virtual cohort is by itself novel. The [CDC synthetic linked-data verification service](https://www.cdc.gov/nchs/linked-data/synthetic/index.html) also provides a concrete precedent for using synthetic data with subsequent real-data verification. The practical use is credible; the research contribution needs to be demonstrated.

## 4. Two task tracks, with explicit evidence regimes

### A. Whole-cohort synthesis — main paper track

Input: target population definition, variable dictionary, study design and allowed evidence. No target participant rows. Output: new virtual participants and a reusable generator.

- **A0, target-summary reconstruction:** target means/counts/SDs may be supplied. Label their reproduction as reconstruction. Existing Ross experiments belong here.
- **A1, cross-study transfer:** only external source evidence plus prespecified target descriptors/baseline information. Target outcome statistics and target associations remain reserved. This supports the stronger evidence-to-target claim if successful.
- **A2, additional joint evidence:** add a fixed packet containing independently verified joint/paired or conditional evidence. Compare with A0/A1 under a common budget. Evidence does not become transferable merely because it mentions the same variables.

### B. Partial-record completion — complementary track

Input: incomplete observed rows, exact artificial-mask keys, dictionary and the same allowed external evidence. Output: multiple completed datasets preserving all non-target cells. Current PFS completion is an implementation example.

Keep artificial missingness separate from native missingness. Retrospective completion may use later visits; forecasting must not. Record which information is available for each task. Neither track implies reconstruction of an individual's true unobserved medical facts.

Do not average track A and B scores into one headline. Neural generators trained on target rows are informative only in a separate target-data-available regime; they are not matched-information baselines for A1.

## 5. Shared system: existing components and proposed extension

Reuse `../population_framework/runner.py`, its staged evidence delivery and generic observers. Reuse the masked-completion input-preservation contracts and the pinned paper-analysis functions. Do not replace existing results or build another case-specific engine.

| Component | Responsibility | Current status |
|---|---|---|
| Study/evidence adapter | Population, selection, measurement, units, observation operator, estimate/uncertainty, source location and cohort overlap | Existing case adapters; extraction remains curator-assisted |
| Modeling Agent | Select dependence/trajectory/missingness model and generate executable code or literal records | Implemented in prior pilots; keep actual decisions and rejected options |
| Numerical executor | Run submitted programs, enforce schema and evidence contracts, retain all outcomes | Implemented; context isolation is procedural, not an adversarial security sandbox |
| Source-only reviewer | Check evidence extraction, formula/code consistency and allowed-source discrepancies | Implemented; reviewer agreement is not statistical validation |
| Evidence-compatible scenario policy | Retain distinct plausible joint structures where evidence does not identify one; qualify analysis sensitivity | Implemented and tested in Stage 1; sensitivity demonstrated, consistent accuracy gain not established |
| Reserved evaluator | Same real/synthetic analysis, study-level reporting, independent audit | Existing selected analyses; broader development batch implemented separately here |
| Research-use report | Explain supported, assumption-sensitive and unvalidated analysis uses | Stage 1 analytical report implemented; decision utility and calibrated uncertainty remain untested |

### Proposed mechanism to test

Replace forced selection of one plausible joint structure with a small set of evidence-compatible structures. The Agent must connect each scenario to a specific unresolved quantity, such as paired covariance, a measurement mapping or transport heterogeneity. Sampling variation within one model is not a different structural scenario.

1. Identify dependencies required by a declared class of analyses, without seeing reserved results.
2. Separate evidence-supported values from weakly constrained assumptions and incompatible sources.
3. Construct at most three substantively different joint-model scenarios where needed; a justified single model remains allowed.
4. Check each scenario against the same allowed observations in its native population/measurement context.
5. Return generated tables plus how planned analyses vary across scenarios. Until calibrated, call this a **sensitivity range**, not a confidence interval.
6. Optionally request the missing evidence that most distinguishes scenarios. Acquisition decisions cannot use reserved target error.

This is a candidate mechanism, not a claim that ensembles, sensitivity analysis or active evidence acquisition are new. It must demonstrate an identifiable analytical or workflow benefit relative to ordinary same-budget construction/revision: for example fewer overconfident conclusions, a more useful request for new evidence, or less measured preparation effort at comparable analytical quality. No time-saving claim is made without timing a specified task. If ranges become so broad that no decision is possible, report that cost rather than counting abstention as success.

Any statement of robustness means stability across the **examined, prespecified scenario set**. Three scenarios cannot cover every evidence-compatible joint distribution. Freeze scenario inclusion, exclusion and source-compatibility rules using allowed evidence only, before target evaluation. Report imperfect fits and unresolved source conflicts rather than silently excluding an inconvenient scenario.

### Bounded construction and revision

For the first prospective comparison, each fresh builder gets one initial submission and at most two source-only review rounds. Numerical interface repair is logged separately. Retain every stage and use the final scheduled valid submission under a rule fixed before testing; never choose a seed or stage by target performance. Source evidence is fixed for the main comparison. Autonomous retrieval is a later ablation with the same query budget for both policies and an exclusion list for target-source overlap.

The ordinary policy and proposed policy branch from the same initial construction and get the same source packet, model access, submission limits, and numerical calibration budget. Allow ordinary policy to use multiple candidates too; otherwise gains could merely reflect more search. For full synthesis, the twenty final outputs are a total budget per branch: three retained scenarios receive a fixed 7/7/6 allocation, not twenty outputs each. Preserve scenario labels and show disagreements rather than averaging them away. Record actual latency and model/token metadata when available. Current session subagents do not expose all provider settings: unavailable values remain unavailable, and these runs cannot support precise model-cost comparisons.

## 6. Evaluation by scientific question

Every analysis has a ledger entry *before* a new confirmation run: study, population, variables, estimand, formula, transformation, missingness handling, multiplicity family, evidence availability, and interpretation. A known paper statement and a successfully reproduced reference estimate are separate fields.

Use two distinct fields so unknown relationships do not disappear from the evaluation denominator:

- **Validation role:** `given/reconstruction` when the tested quantity, or inputs mathematically determining it, were supplied; `reserved` when the target relationship was not supplied; `copied_control` when all relevant analysis inputs remained unchanged. Copied controls detect corruption and are excluded from generative-success denominators.
- **Evidence support:** external support with documented transport assumptions, weak constraints, or unidentified. A reserved relationship can also be unidentified; keep it in the reserved family and report the limitation.

The user-facing table shows the original scientific statement, real-data estimate/interval, synthetic estimate/interval or repeated-cohort distribution, direction/magnitude/evidence-state agreement, and interpretation. Exact decimal agreement is not required. Main comparisons fix the same target person count, visit design and declared missingness conditions across methods, and report actual analysis denominators. Larger virtual sample sizes are reserved for the separate planning experiment.

### Main reporting dimensions

1. **Direction and scientific interpretation:** reversal, preserved direction, or unresolved. For a result with a wide real-data interval, a tiny signed point estimate is not treated as a known biological direction.
2. **Magnitude:** effect estimates in the original units and any domain-justified practical category. Do not invent a universal 10% or 20% equivalence margin. If no defensible margin exists, report differences without a binary equivalence claim.
3. **Uncertainty:** distinguish positive, negative and interval-overlaps-null *evidence states*. A nonsignificant reference is not proof of no effect. Track newly confident synthetic findings where the reference is unresolved, but call them unsupported-evidence discrepancies, not population false positives.
4. **Repeated-generation stability:** preserve each builder and sampling seed. Report scenario/build sensitivity and the usable-analysis fraction at each uncertainty policy.
5. **Known-truth diagnostics:** semi-synthetic/controlled environments with explicit nulls permit actual false-positive and coverage assessment. These are additional diagnostic environments, not invented clinical evidence.
6. **Practical utility:** analysis execution success, validity of a measurement/sample-size choice, and preparation time/error reduction where measured. Do not equate successful execution with valid inference.

Analyses are correlated within people and studies. Compare methods within cases, then report case-level results and equal-study summaries. Generated rows, analytic terms and random seeds are not independent studies. With only a few studies, show all cases rather than claiming precise field-wide superiority.

For track B, use multiple-imputation combination rules only under the disclosed modeling assumptions. Within-model imputations and alternative structural scenarios are different: do not Rubin-pool incompatible scenarios as if they were draws from a justified single posterior. Keep each model's MI analysis separate, with a matched, explicitly budgeted number of imputations; report between-model sensitivity separately. For track A, independently simulated full cohorts remain separate Monte Carlo samples; applying Rubin's missing-data rules or pooling their rows as more real patients is invalid without a distinct justified inferential model.

## 7. Comparators and ablations

Do not start with a large arbitrary model zoo. The first comparison has three arms:

| Track | Ordinary statistical reference | Ordinary Agent | Proposed Agent policy |
|---|---|---|---|
| A | Study-design-compatible maximum-entropy/copula/conditional simulator using the same evidence and transparent dependence sensitivity | Same Agent access and candidate/revision budget | Evidence-compatible structures plus analysis-sensitivity report |
| B | MICE-PMM; add substantive-model-compatible or suitable longitudinal imputation when the actual analysis requires it | Ordinary conditional-generation policy | Same proposed policy with observed-cell preservation |

For each case, select one suitable statistical reference by a recorded rule based on the measurement/design audit, before reserved results are inspected. Freeze its evidence mapping, dependence assumptions, sensitivity range and output budget. Do not select the reference family by its target performance. Missing-only is an additional track-B reference. It is not a substitute for a generation comparator in track A. Keep direct record authoring as a small separate arm until repeated-construction feasibility/cost is measured. The paper does not need a no-record Agent as its central opponent; that comparison is only relevant for a claimed advantage on a decision that does not require records.

The main comparison already includes ordinary same-budget revision. The first additional ablation should isolate one mechanism, initially removal of genuinely applicable joint evidence in a case where it exists. Further scenario-removal and corrupted/mismatched-evidence checks follow only if the main comparison warrants expansion. The point is to identify what helps, not maximize the number of plots.

## 8. Cases and exposure registry

| Case | Available data/design | Role now |
|---|---|---|
| Ross et al. 2020, [paper](https://doi.org/10.1371/journal.pone.0243530) | Local verified public workbook; 75 adults, five visits | Exposed development; whole synthesis and completion |
| Travers et al. 2024, [deposit](https://researchdata.bath.ac.uk/1350/) | Local public paired data; 12 men, short dietary restriction | Exposed development; unit/paired-variance fixture, not adequate standalone validation |
| He et al. 2026, [paper](https://doi.org/10.1371/journal.pone.0357145) | Local public data; 100 baseline children, 44 intervention completers; endpoint-specific pairs | Exposed development; paired analysis and unsupported-positive discrepancy |
| Occupational activity/adiposity, [paper](https://doi.org/10.1371/journal.pone.0154935) | Local workbook; reported 692 whole-day and 671 work/non-work records; headers inspected | Candidate confirmation after exposure/codebook audit; compositional time-budget relations and adjusted models |
| ETIP, [paper](https://doi.org/10.1371/journal.pmed.1002079) | Public S1 SAV link verified; 91 randomized; follow-up/endpoint denominators vary | Candidate confirmation, download/parser/model audit still needed; mixed continuous/binary trial outcomes |
| NAGALA/DIETFITS and prior exercise cases | Already analyzed in prior work | May be development/stress cases; never relabel as untouched because the wrapper changes |

The 692- and 671-record occupational sheets overlap, not two independent cohorts. Public article conclusions are visible to the coordinator. Before confirmation, audit past file access and freeze analyses independently of method performance; fresh builder contexts receive a redacted packet. Public-model pretraining exposure cannot be ruled out. If prior target analyses are discovered, retain the case as development and recruit another confirmation case.

Adult-to-child transfer is an optional stress case after within-population utility is established, not an assumed valid default. NHANES can support a larger additional case only with survey-design-aware estimands and the correct examination/fasting subsample weights. [NCHS guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/SampleDesign.aspx) makes simple iid treatment inappropriate for population inference.

## 9. Staged execution budget

These are operational budgets, not a statistical power calculation or a promise of sufficient studies for a high-impact journal.

**Stage 0 — now:** broad retrospective development replay of 144 existing input datasets: one reference, three masks, 120 completed datasets and 20 unique fully synthetic cohorts. Up to 35 analysis outputs each = 5,040 records. There is one underlying Ross study and no new Agent construction. Of 35 completion outputs, 29 are copied controls; only five PFS time contrasts and the PFS-weight proxy are sensitive to completion. Separate the 31 paper-replay outputs from four proxy associations. Preserve failures and all denominators.

**Stage 1 — framework feasibility:** three development cases, three fresh initial builder contexts per case, and two revision-policy branches from each initial construction. Each branch produces twenty final generated cohorts. That is nine initial lineages, eighteen paired policy branches and 360 virtual cohorts, plus 60 fixed statistical-reference cohorts, if all cases pass adapter audits. The branches are paired comparisons, not eighteen independent starting constructions. This measures between-builder versus within-program variation. First verify the completion-specific reporting interface on the frozen Ross outputs; the pediatric completion extension comes later, with its own explicit builder/mask budget. Any new completion builder sees only one masked view, without full-target summaries or target-paper findings; the frozen generic method is executed on other masks by the custodian. Evaluate multiple structural completion scenarios only after a separate matched budget and combination protocol are fixed. Do not start this expansion until the shared scenario-policy and evaluator interfaces pass review.

**Stage 2 — independent-case comparison:** target five eligible studies overall, with at least two cases unused for policy selection. Run five fresh initial lineages per study, two paired revision-policy branches per lineage, and twenty final cohorts per branch. This produces 25 initial lineages, 50 branches and 1,000 cohorts; a fixed statistical arm adds 100 cohorts. The three reused development studies remain labelled development; only the two newly reserved studies provide confirmation of the selected policy. Completion and retrieval ablations are additional, separately enumerated. Five studies still limit generalization; sample counts are not a substitute for distinct study designs.

**Stage 3 — research-use demonstration:** select one decision task prospectively, initially sample size/measurement scheduling for a recoverable longitudinal or paired analysis. Generate the recommendation from allowed evidence. Assess it in a separate real-reference resampling environment with participant-level resampling and in known-truth simulation. This tests conditional operating characteristics, not actual future clinical trial power. Keep effect-size assumptions fixed; do not choose the assumed treatment benefit from the target test result. Compare recommended design regret and sensitivity, not simply whether a synthetic p value is below .05. A later prospective investigator-use study would be stronger evidence of saved effort.

### Advance and stop rules

- Stop execution on source-unit, key/pairing, inclusion-rule or hidden-answer leakage defects; repair transparently before a new run.
- If improvement occurs only on supplied summaries or copied controls, retain software usefulness but do not advance a reserved-analysis superiority claim.
- If more than one evidence-compatible model gives different scientific interpretations, report ambiguity and evaluate whether a bounded evidence request resolves it; do not force a desired result.
- Expand a policy only when benefits recur across development cases/builders and uncertainty remains decision-useful. Inspect per-case failures and the same-budget comparator; no universal invented pass percentage is imposed.
- If there is no independent analytic or decision advantage after the bounded prospective comparison, narrow to a reproducible benchmark/resource or park the new-policy claim. Do not add more agents or rows merely to manufacture a larger study.

## 10. Paper structure and writing readiness

The manuscript can be drafted now at the level of Introduction, system description, evidence regimes and evaluation Methods. Results text must distinguish the development observations already obtained from unrun confirmation experiments.

Suggested figures:

1. Evidence-to-generator-to-analysis workflow, with information boundaries and source applicability.
2. Study/evidence coverage, showing reconstruction, reserved queries and copied controls separately.
3. Real versus virtual effect/interval plots for the complete prespecified claim families, including unresolved findings.
4. Across-study/builder stability and comparison with same-information methods.
5. Mechanism ablations: evidence, scenarios and ordinary revision; benefits and added ambiguity/cost.
6. One research-design decision evaluated in an independent reference environment.

Tables: cohort/exposure registry; closest-work comparison; model/evidence budgets; per-study findings and failures. Supplemental materials retain source extraction, all analysis definitions, all generations, run identities, hashes and negative results. Share patient-level source files only as permitted; synthetic records are labelled synthetic and not automatically described as privacy-preserving.

Journal choice follows the achieved contribution. The current work does not justify predicting acceptance at Nature Communications. Broad independent validation plus a substantive method and demonstrated research use would support aiming at a stronger methods/digital-health venue; a useful, well-audited resource has a different publication case. We will choose a venue after the independent-case and use-task results, not use the journal target to set success rules.

## 11. Concrete next handoff

1. Finish and audit the broad development batch in `development_batch/`; use it to specify failure classes, not select favorable conclusions.
2. Freeze the claim ledger and evidence-regime contract for each next case before any new builder runs.
3. Implement the proposed scenario/revision policy as a shared strategy on the existing runner; retain the ordinary policy under the same resource limits.
4. Audit occupational/ETIP access, units, denominators and exact analysis recoverability; register prior exposure.
5. Execute Stage 1, inspect all cases, then decide whether Stage 2 is warranted. No local LLM training or HPC is required for this first round; profile actual program runtime and model-call cost before purchasing capacity.
