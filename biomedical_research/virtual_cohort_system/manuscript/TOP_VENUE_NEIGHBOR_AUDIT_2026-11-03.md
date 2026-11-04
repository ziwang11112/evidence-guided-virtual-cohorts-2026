# Close-neighbor audit for the higher-ambition research route

Prepared 3 November 2026, America/Chicago. Bounded independent review: four papers. This memo reviews possible extensions; it does not amend the frozen experiments or establish that an extension is novel or effective. No experiment, cohort acquisition, patient-data inspection or paid-model call was performed.

## Decision in one paragraph

The biomedical data-generation problem remains worth pursuing. Its harder input conditions are real: published estimates may describe different populations, measurements and adjustment sets, while the requested cohort has no individual construction records. However, general LLM model authorship, aggregate-only synthesis, missing-dependency reasoning, feedback, and flexible generation requests already have close precedents. The most promising additional capability is to make the relationship between a requested analysis and a missing **study-qualified statistical constraint** operational: determine which observed evidence could distinguish plausible joint models, obtain that evidence, interpret it under its actual study conditions, and produce a more useful table. This is a proposed adaptation of established model criticism and experimental-design ideas, not a claim of inventing active acquisition. Its value needs to appear in generated-data analyses, not only an evidence ledger or selector score.

## What the four predecessors actually establish

The entries distinguish a formal capability from the conditions evaluated. Statements below summarize the original papers; the final column is our comparison, not a claim that a predecessor cannot be adapted.

| Work and verified identity | Original method and evaluation | Relevant distinction |
|---|---|---|
| **G-Sim**, ICML 2025, PMLR 267 | LLM-authored simulator structure, numerical calibration and diagnostic-driven structural refinement. Section 2.3 permits fragmented/unpaired sources and domain text. Appendix B.2 explicitly discusses observational equivalence and finer diagnostics. Main experiments use three hand-designed stochastic environments, with distributional/predictive evaluation and scenario-use demonstrations. | Aggregate diagnostics and uncertainty about structure are already in scope. Its inspected experiments do not establish automatic interpretation and acquisition of differently adjusted biomedical literature estimates. This is an untested setting, not proof of inability. [Official record and PDF](https://proceedings.mlr.press/v267/holt25b.html). |
| **LLMSynthor**, KDD 2026, AI for Sciences listing; inspected arXiv v4, 8 June 2026 | The generic aggregate operator is not restricted formally to frequencies. Dependency inference selects informative variable combinations, expands/filters joint targets and can optionally approximate missing joints. LLM proposals specify configurations/counts, followed by numerical sampling and discrepancy feedback. Evaluation includes mixed-source mobility, controlled transactions and household policy queries; contextual event requests also alter synthesis. | “Agent finds missing relationships,” zero-individual-input generation, multiple sources and dynamic requests are insufficient differentiators. The inspected algorithm does not choose a newly observed, study-qualified estimate by query-specific discrimination between alternative laws. [Official listing](https://kdd2026.kdd.org/papers/); [full methods](https://arxiv.org/html/2505.14752v4). |
| **SPADA**, *Doubling Your Data in Minutes: Ultra-fast Tabular Data Generation via LLM-Induced Dependency Graphs*, EMNLP 2025 main proceedings | LLM-generated sparse dependencies guide KDE or conditional-flow sampling. Both routes use original individual data for fitting or conditional retrieval. Main tables assess predictive utility, violations and runtime; additional datasets and ablations appear in appendices. | Agent-selected structure with numerical execution is already a valid published design. This is not an equal-information baseline for an article-only construction unless separately adapted; absence of individual input is a different regime, not demonstrated superiority. [Official record](https://aclanthology.org/2025.emnlp-main.525/); [full paper](https://aclanthology.org/2025.emnlp-main.525.pdf). |
| **SynthIPD**, *training-free synthetic individual patient data generation*, arXiv v2, 24 July 2026; no later venue established here | Published Kaplan–Meier/risk information and subgroup summaries yield survival records with covariates through constrained assignment. Inputs must describe the same population; multivariate categorical reconstruction requires joint-stratum summaries. The paper compares N9741 subgroup analyses with true IPD, pools six myeloma studies and evaluates three simulated survival mechanisms. | Published biomedical evidence to complete analyzable records is already explicit. Our intended setting allows heterogeneous external evidence and less complete joint information. That broader interface also creates assumptions that its narrower reconstruction problem avoids. [Full paper and version](https://arxiv.org/html/2509.16466v2). |

This is not a field-wide priority search. The project already documents statistical precedents, including indirect inference, statistical matching and ML-NMR, in its positioning file. Their existence must remain part of the eventual introduction. ModelSMC is being checked separately by the root reviewer; this memo does not count an uninspected fifth paper or claim that weighted candidate models are new.

## What we can learn from their paper construction

**Our reconstruction of the research argument:** successful papers in this set make a specific computational object or operation visible, explain what it enables, and evaluate that operation and its downstream use. The transferable lesson is not that every paper must train a foundation model or invent a loss. It is that the method should make one defensible promise whose success can be measured in the claimed conditions.

For our project that promise should remain about **generating useful biomedical data**. A user can specify a population and an intended analysis; the method can construct a different generator for another request. We do not need to promise one universal table. Conversely, an ordinary prompt accepting arbitrary variables does not establish scientific coverage. The evidence and joint assumptions must support the particular output being claimed.

The absence of a particular task from these papers' evaluations creates an opportunity for investigation, not automatically a novel algorithm. A carefully demonstrated biomedical capability can still be a substantive contribution. The experiment should show why the chosen operation changes the generated data's usefulness, rather than treating the application label or Agent count as evidence of novelty.

## What our completed work already contributes

These are local artifact findings from `DRAFT_v0_8.md` and `CORE_CONTRIBUTION_POSITIONING_2026-11-03.md`, not predecessor claims.

1. **A real scientific authoring operation exists.** Agents choose joint laws and translate evidence into model parameters. The worked example connects separate age/sex-adjusted BMI and glucose projections to a joint response law, while declaring the residual correlation assumption. This is more substantive than putting fixed biological coefficients behind an Agent interface. The algebra itself is established.
2. **Complete cohorts are produced without individual construction inputs.** The principal two-case study has 20 Agent and four statistical constructions, yielding 72 final tables. The later supplied-summary and longitudinal public-model settings demonstrate additional information regimes, rather than more independent external clinical validations.
3. **Analysis-level usefulness is empirically visible but uneven.** Additional external relations improved five of six designated coefficient discrepancies and worsened CHNS BMI. Supplying accessible target summaries improved reconstruction. The longitudinal example reproduced a strong specified interaction while retaining weaknesses elsewhere.
4. **Current evidence does not isolate the proposed new mechanism.** The main study has no scientific revisions; source-population replay was unavailable. Declared semantic consistency is not evidence that an operator was accurately extracted or transported. Different evidence arms do not isolate an acquisition policy, semantic interpretation, or a particular model-search mechanism.

The supplied-summary and public-model results are valuable reconstruction demonstrations. The external-evidence results reveal the difficult part: completing a joint law and transferring conditions. More random seeds from existing laws would not answer why that part succeeds or fails.

## Extension 1: acquire the missing relation needed for a requested analysis

**Status: proposed; priority candidate for a small discriminating study.** This extends data generation, rather than replacing it with a literature-search benchmark.

### Concrete example

A user requests a complete cohort for a BMI–HbA1c regression adjusted for glucose, age and sex. The admitted articles contain separate BMI and glucose projections and marginal variation. Several joint models can reproduce those inputs while implying different adjusted BMI effects. A residual BMI–glucose association from a suitable source could help distinguish those completions; another HbA1c mean might not. An unadjusted association from a different population is not automatically the same constraint.

The proposed operation is therefore to choose a **statistic with its source population, measurement and adjustment operator**, rather than merely choose a variable pair or a promising paper title.

### Implementable change

Given the same base evidence and research request:

1. The Agent authors materially distinct plausible joint models and exposes their implied requested analyses. Each must meet the admitted constraints to the specified tolerance; merely duplicating a model does not provide structural alternatives.
2. For the available evidence candidates, it predicts what each operator would report under each model in the declared source context. If that context cannot be modeled from allowed information, the limitation is explicit.
3. It selects one observed evidence item expected to resolve uncertainty relevant to the request, within the same retrieval budget available to the comparator. Selection is frozen before its numerical result is revealed.
4. It incorporates the returned estimate with its uncertainty and source conditions, then produces the complete virtual data. The acquired number need not be a target result and must not be silently treated as one.

Candidate disagreement is a diagnostic of the supplied model set, not a calibrated posterior or proof that truth lies in the set. One new estimate need not identify the whole joint law. When it cannot resolve the requested analysis, the result remains a conditional data product with that limitation.

### What would distinguish a useful result from a decorative loop

A small fixed-corpus mechanism study can vary whether an available relationship is actually informative for the requested analysis and whether its population/adjustment conditions match. Include plausible **context twins**: similar variable names but different adjustment sets or population conditions. This tests numerical interpretation rather than keyword selection. A controlled world can establish the mechanism, but is not patient validation.

The principal comparator should be an equally capable ordinary Agent given the same request, base evidence, corpus metadata, tool availability and acquisition/computational budget. It may reason about dependencies and conditions. Do not forbid it from using the very capability the proposed system claims to improve. An all-evidence diagnostic can establish whether the bottleneck is acquiring information or constructing a useful law after information is available; it is not a budget-matched performance baseline.

Success means better **final-table scientific analyses**, while preserving already admitted constraints, across all prespecified tasks and authors. Selected-card accuracy alone is inadequate. Failure cases include identical candidate models, confident use of a mismatched source, an informative estimate that the generator ignores, or improving the requested coefficient by destroying other admitted relationships. Preserve these outcomes.

This candidate goes beyond adding a search box: the proposed decision unit is a query-relevant source operator whose numerical implications are tested before acquisition. Whether that is a worthwhile methodological advance remains an empirical question. Generic active experimental design, model disagreement and missing-evidence identification should not be claimed as inventions.

## Extension 2: source-conditioned reconstruction before target generation

**Status: narrower fallback or enabling component, not a separate large platform.** If evidence selection is unnecessary or unstable, a cleaner hypothesis is that interpreting a statistic in its own study conditions improves generation from heterogeneous studies.

The Agent would construct a joint model plus explicit source observation operations: source eligibility/covariate mix, measurement transformation and statistical adjustment. Each supplied number is compared with its own implied source statistic; the requested target cohort is sampled under the target specification. A target-table statistic is not substituted for a source statistic. Unknown source distributions remain assumptions, rather than being filled from hidden target data.

A controlled comparison should separate effects of interpreting context from effects of extra information or computation. A flattened-statistic ablation is useful for diagnosis but is not a strong predecessor baseline by itself. A capable ordinary Agent or a reasonably adapted simulator-calibration procedure must receive the full source information and be allowed to use it. If both solve the task equally well, the result can still establish a useful application; it would not establish superiority of the extra machinery.

This is an operational extension of established statistical synthesis, not a new principle of integrating aggregate data. It becomes scientifically compelling if it enables useful generation under realistically heterogeneous inputs with less case-specific human model design, and those claims are measured. Until then, describe it as a candidate capability, not an accomplished general evidence compiler.

## Prioritization and stopping point

Prefer one bounded study of Extension 1, using Extension 2 only to the degree required for valid source interpretation. Do not introduce a new model-training program, multi-Agent hierarchy or unrelated benchmark collection. If the ordinary Agent already selects and uses the relevant evidence reliably, simplify the implementation and report that fact. If no permitted evidence can constrain the requested joint analysis, increasing the number of generated rows is not a remedy.

For a higher-ambition submission, the next result should establish an identifiable data-generation capability and its useful operating conditions. It need not show universal superiority over every carefully designed statistical generator. Any paper claim must remain limited to the actual comparisons and information supplied. Venue selection and the decision to execute are left to the root task and user.

## Inspection record

- **G-Sim:** official PMLR publication record freshly checked; full-method reading used the already retained published-text extraction `work/neighbor_deep_read_2026-10-31/gsim/holt25b.txt`, particularly §§2.3, 3, 5–6 and Appendix B.2. The prior implementation audit is dated 31 October; no fresh repository reproduction or universal release-quality claim is made.
- **LLMSynthor:** official KDD listing was directly confirmed through the indexed official page, identifying the AI for Sciences track. The current page rendering did not expose the complete list, so the official-domain search result was used for that specific identity check. Full arXiv v4 §§3.1–3.3, 4.1–4.3 and appendix materials were inspected. DOI recorded in that version: `10.1145/3770855.3818965`. The older local v3/code audit was not silently promoted into a current code audit.
- **SPADA:** official ACL Anthology metadata and published PDF inspected; §§3.1–3.4, §4 and corresponding tables support the input and evaluation distinctions. Runtime claims were not reproduced.
- **SynthIPD:** arXiv v2 methods §§3.1–3.3, particularly same-population and joint-stratum requirements, plus §§4–5 case/simulation analyses inspected. No conference acceptance is inferred from the preprint.

All proposed extensions and comparisons above are our reasoning. None is attributed to the authors as their historical idea-development sequence. No absence or priority claim follows from this four-paper audit.
