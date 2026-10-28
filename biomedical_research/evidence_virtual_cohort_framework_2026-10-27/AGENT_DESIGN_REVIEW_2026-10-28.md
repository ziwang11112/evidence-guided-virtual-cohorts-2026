# Designing an Agent that turns research evidence into useful virtual cohorts

28 October 2026. Prospective design review. No new generation, model fitting, or target evaluation was performed for this document. The completed insulin pilot and its freezes remain unchanged. Proposed components below are not claims of implemented capability.

## 1. The decision

Keep the objective: **use available observations and applicable external studies to generate richer virtual datasets that support useful biomedical analyses**. Whole-cohort generation, adding entirely unmeasured variables, and missing-cell completion remain distinct use cases. Exact reconstruction of individuals is not the objective.

The next design should improve **how the Agent turns a consequential evidence gap into a retrieval or modeling action**. It should not merely increase the number of agents, provide a more flexible regression, or document more limitations. The delivered object remains generated data, accompanied by a reproducible generator and an account of which analyses have support.

For variable enrichment, the modeling target is a conditional distribution:

`p(new variables | observed variables, target population, measurement conditions)`.

The observed columns remain fixed. Their joint distribution is supplied by the cohort; the new conditional relationships must come from external evidence, applicable individual data if available, and explicit assumptions. LLM knowledge can suggest hypotheses and search terms, but is not a substitute for a traceable numerical source.

We will keep the existing Python workflow. No training of an LLM, new agent framework, HPC deployment, or agent swarm is necessary for the next discriminating experiment.

## 2. What the implemented pilot actually teaches

The clean builder independently retrieved six primary studies, selected three for numerical use, and authored an executable conditional lognormal generator. It chose the transformations, model structure and parameters. This was meaningful Agent participation, rather than a coordinator supplying the biological formula. However, it was program generation followed by numerical sampling, not direct LLM output of every insulin value.

The pilot retained the broad positive BMI association. Its fixed structure did not recover the reserved curvature or sex-dependent slope pattern. That is more informative than a small difference in a coefficient: some scientifically relevant relationships were missing. One construction and its twenty residual draws cannot establish either the method's general validity or a benefit over another method.

| Actual decision | Why it matters | Required change in decision process |
|---|---|---|
| An insulin ratio between two BMI groups became an individual log-linear slope. | Group composition and within-group variation are not identified by two means; an adjusted individual relationship does not follow automatically. | Record a bridge assumption, search for individual conditional evidence, and test whether alternative relationships fit the same source summaries. |
| Marginal age-bin insulin and BMI medians became paired conditional anchors. | Marginal medians need not describe the same person or a conditional median. | Treat these as marginal constraints unless a justified source-population model connects them to the conditional model. |
| Marginal subgroup spread became conditional residual noise. | Spread due to BMI, other covariates and selection was assigned to individual residual variation. | Separate marginal, conditional and between-study variation; seek residual or joint information where it matters. |
| No need for separate sex reference intervals helped justify zero conditional terms. | A reference-interval partition decision is not evidence of no adjusted effect or interaction. | Keep absence of evidence separate from evidence of negligible effects. A zero-term fallback may be explicit, but must not be advertised as an established biological absence. |
| Search stopped after six of twelve permitted substantive queries. | The stopping rationale was that a tractable simulator could be constructed. A known lead to adjusted supplementary tables remained unresolved. | Stop on adequate information for intended uses, a documented search/access limit, or lack of promising leads, rather than a paper-count target. |
| Source/code review approved an explicitly limited simulator. | Extraction and arithmetic can be correct while analytical adequacy remains unestablished. | Add a scientific challenge with actions, alongside implementation verification. |

The source gateway deliberately did not retrieve supplements. It accepted all six requested main texts; four search-level exclusions were not examined. We cannot infer that rejected sources contained the missing answers, or that further retrieval would necessarily succeed. A real capability gap was the inability to follow an already identified supplementary-table lead through the approved interface.

These observations come from [the initial decision](../insulin_feature_enrichment_2026-10-27/agent_clean/INITIAL_DECISION.md), [the search log](../insulin_feature_enrichment_2026-10-27/agent_clean/SEARCH_LOG.md), [the model specification](../insulin_feature_enrichment_2026-10-27/agent_clean/initial/model_spec.json), [the source/code review](../insulin_feature_enrichment_2026-10-27/review/INITIAL_SOURCE_CODE_REVIEW.md), and [the completed results](../insulin_feature_enrichment_2026-10-27/RESULTS.md).

**Diagnosis:** the important unsupported transformations were often disclosed correctly, but disclosure did not change the next action. This is an evidence-to-decision weakness. It is not evidence that the implementation was fraudulent, that coding failed, or that a larger model alone would solve the problem.

## 3. What should be intelligent, and what should be deterministic

| Component | Responsibility | What it must not silently decide |
|---|---|---|
| Accountable builder Agent | Identify missing relationships; select evidence; propose structures; request analyses; revise the generator and its scientific claims. | Read final target answers, invent numerical citations, or select a successful draw after evaluation. |
| Literature tools, optionally an evidence worker | Search, retrieve main texts and supplements, extract source-linked evidence, identify cohort reuse and incompatible estimands. | Treat a paper's conclusion as an executable coefficient without its model and context. |
| Scientific challenger | Find consequential assumptions; construct or describe evidence-compatible alternatives; specify the evidence or analysis that would distinguish them. | Supply hidden reference answers or require a familiar biological pattern merely because it seems plausible. |
| Numerical engine and implementation checks | Fit authorized source constraints, simulate, calculate diagnostics, preserve observed cells, validate units and interfaces. | Choose case-specific biological slopes or modify data to make a desired result significant. |
| Independent evaluator | After freezing, run reserved analyses and compare scientific interpretations with the reference. | Feed final-test findings back into the same construction and still call it a held-out test. |

The builder can also perform retrieval. A separate challenger is useful because it has a different assignment, not because another copy of the same model becomes independent scientific evidence. The evaluator is outside the generation loop. More agents are an optional engineering choice, not the proposed contribution.

The LLM's distinctive work is semantic and adaptive: recognizing that two reported quantities answer different questions, finding the right table, resolving measurement definitions, choosing which missing fact matters next, and proposing a suitable generator. The numerical engine supplies reproducible mathematics. No LLM weight update is required; source-based parameter calibration is different from LLM training.

## 4. Define the intended use before searching

Create a short task contract containing:

- Target population, eligibility, time point, measurement scale and requested new variables.
- Which cells are observed, derived or synthetic; which original information must be preserved.
- Broad intended analysis classes, such as adjusted associations, trends across exposure range, subgroup comparisons, or longitudinal changes if the design supports them.
- Available evidence and allowed development feedback, with final evaluation kept separate.
- Retrieval, construction, execution and review budgets.

The contract does not specify the desired effect direction or hidden test result. A generic coverage map applies across outcomes: location, dependence, shape, modifiers, conditional variation, tails, selection, measurement and transport. Each entry can be relevant, irrelevant, partly supported, unresolved or an explicit assumption. Not every task needs every component; longitudinal behavior should not be manufactured for a cross-sectional task.

The Agent should ask, for example, “Do these data constrain the individual relationship after the intended adjustment?” rather than “Have I found six insulin papers?” This policy must be applied to new outcomes without an insulin-specific checklist of the already revealed failures.

## 5. Turn papers into typed evidence, not a bag of numbers

An evidence record should preserve:

| Field | Purpose |
|---|---|
| Source identifier, version/hash and exact table/section | Verify extraction and distinguish article from supplement. |
| Cohort identity, overlap and repeated publications | Avoid counting the same participants as independent evidence. |
| Population, eligibility, setting and follow-up/time point | Decide whether evidence is applicable and what selection it reflects. |
| Variables, units, assay, specimen, fasting and censoring/rounding | Prevent measurement mismatch disguised as biological differences. |
| Estimand and original analysis formula | Distinguish means, medians, correlations, adjusted slopes, standardized effects and odds ratios. |
| Adjustment set, transformations and reference categories | Determine what the estimate conditions on. |
| Estimate, precision, sample size, dependence among reported quantities | Avoid treating SE as SD or several correlated tables as independent constraints. |
| Applicability and permitted use | Mark a direct constraint, an assumption-dependent bridge, contextual evidence, or unusable evidence. |
| Missing information and next retrieval lead | Make unresolved uncertainty actionable. |

The schema is a bookkeeping contract, not a claim that every field is known. Unknown fields remain unknown. An LLM's subjective confidence is not a sampling variance and must not be converted into a precision weight.

A reported adjusted coefficient may constrain a compatible model under its original adjustment and population. It is not universally transportable. Qualitative evidence can guide a candidate's structure or sensitivity questions; it must not silently create a precise coefficient.

## 6. Compare evidence in each study's own setting

For study `j`, the conceptual forward calculation is:

```
source population and selection
    -> candidate individual model
    -> source measurement process
    -> the study's original analysis
    -> predicted reported statistic
```

Compare that statistic with the reported estimate and its uncertainty. Only then generate under the target population and target measurement definition. Do not require the target cohort simultaneously to have the marginal mean of every source population.

This is the useful connection to [ML-NMR](https://pmc.ncbi.nlm.nih.gov/articles/PMC7362893/): individual models are integrated over the covariate distributions of the aggregate-data studies. The statistical idea predates LLM agents; matching simulated summaries is not, by itself, a new loss function.

Three implementation levels are appropriate:

1. **Direct compatible constraint:** a source provides a usable coefficient, uncertainty and model definition. Apply it only with the necessary model/transport assumptions recorded.
2. **Executable source operator:** sufficient source population information permits simulation or integration and reproduction of the reported analysis. Calibrate candidate parameters using these source constraints.
3. **Incomplete source context:** missing joint covariate distributions, adjustment definitions or assay calibration prevent an adequate operator. Retrieve the missing information, use a stated approximation with sensitivity, or retain the source as context. Do not invent a complete source population and call the resulting match exact.

Begin with a small set of supported operators, such as grouped means, simple regression summaries and reported correlations. Adding a new operator requires verifying its statistical meaning. Calibration must account for repeated/cohort-overlapping estimates and available covariance information; when these are missing, restrict the constraint set or report a sensitivity analysis rather than multiplying independent-looking likelihoods.

Every source check must be labeled directly computable, computable under explicit assumptions, or currently unevaluable. Do not score a candidate against an unevaluable statistic. An assumption-dependent fit is not independent validation. Calibration fits permitted source constraints, never protected target outcomes; incompatible constraints should be exposed rather than forced to match exactly.

Separate three levels of variation: individual residual variability; systematic population or study differences; measurement differences. An unexplained source discrepancy should not automatically increase every target person's random noise. Conversely, a hierarchy with arbitrary study offsets can fit everything while explaining nothing. Unconstrained offsets are not a substitute for information, and any random-effects model needs enough independent studies to support its estimation.

## 7. The actual generation and revision loop

### 7.1 Choose a generator with a common joint interpretation

The Agent proposes a model suited to the evidence and task. Eligible families may include conditional parametric models, mixtures justified by documented populations, copula-based models when dependence information exists, or other executable probabilistic models. A dependency graph expresses a factorization; it is not automatically a causal graph.

For several new columns, individually plausible regressions must form a coherent joint model. For example, a covariance matrix must be valid, conditional sampling order must be defined, and generated mediators must not be inconsistently treated as observed covariates. Added complexity needs a reason. Neither a universally linear default nor a compulsory nonlinear model is adequate.

Every consequential choice links to evidence or an assumption. The controller fixes interfaces and permissions; the Agent decides the biological dependence structure. This is how the Agent participates in the central generation problem rather than merely writing a report around a hard-coded equation.

### 7.2 Require an actionable scientific challenge

The challenger should identify the highest-impact unresolved assumption and, where feasible, exhibit a different model that remains compatible with the same source evidence but changes an intended analysis. It then asks what obtainable evidence would distinguish the alternatives.

A simple mathematical warning illustrates the issue: knowing a conditional mean at two values of an exposure does not determine the curve between them. Many functions pass through two points. Group means provide different, generally weaker information; passing a curve through group-average points does not reproduce those group means. For real source summaries, alternative models must be checked with the appropriate source operator.

This is a focused challenge, not a requirement to construct three arbitrary scenarios for every case. Alternatives are sensitivity hypotheses unless justified probabilities are available. Their agreement is not proof that all plausible models agree.

Each challenge names the affected analysis, the source constraints both alternatives satisfy, the consequential difference and a feasible discriminating retrieval or analysis action. Predeclare a review-round limit as well as tool/compute budgets. Start with one focused challenge; do not enumerate alternatives indefinitely. If no discriminator is available, record the ambiguity without automatically selecting the more complicated model.

### 7.3 Route each problem to a concrete action

| Finding | Action | What counts as resolution |
|---|---|---|
| Wrong unit, SE/SD extraction, model transformation or source locator | Repair extraction/code; rerun affected source checks. | The specified quantity is reproduced correctly. |
| Marginal evidence being used as a conditional relationship | Seek joint/adjusted evidence or a usable source-population distribution. | A justified mapping, or an explicit unresolved bridge with its consequences assessed. |
| Known relevant supplement unavailable | Request a screened supplement through the tool interface. | An approved artifact with source identity, or a documented access limitation. |
| Source estimates disagree | Examine populations, assays, selection, adjustment and cohort overlap before pooling. | A supported explanation/model or an unresolved conflict; not convenient source deletion. |
| Different compatible structures change an intended conclusion | Search specifically for distinguishing evidence; examine supported alternatives. | Better constrained structure, or a clearly conditional analytical interpretation. |
| A source-calibrated candidate fails an unused source check | Examine transport and structure; then revise if justified. | Improved source-level predictive compatibility, without claiming target validation. |
| No promising evidence remains within budget | Stop retrieval and release the qualified generator or declare a requested analysis unsupported. | A transparent endpoint; not an invented relationship or endless searching. |

Search priority should use explicit reasons: relevance to an intended analysis, evidence insufficiency, plausible impact on interpretation and a concrete retrievable lead. Start with a simple ranked queue. Do not introduce an unvalidated numerical “value of information” score with fabricated probabilities.

Stop conditions are: relevant information is adequate for the stated limited uses; the fixed budget is exhausted; or targeted attempts establish saturation/access limits with no promising lead. A paper-count target is not the stopping criterion. Evidence adequacy here is a reasoned decision to be evaluated, not a formal guarantee of identification.

### 7.4 Persist changes and retain justified no-ops

Each decision records the issue, supporting evidence, attempted action, model difference, remaining assumption and affected analyses. A reviewer comment must either produce a justified action or receive an explicit explanation of why no change is supported. Documentation-only changes remain documentation-only; they must not be counted as scientific improvement.

Illustrative decision record, with no biological parameter supplied:

```json
{
  "issue_id": "GAP-014",
  "affected_component": "conditional_exposure_response",
  "evidence_status": "marginal_group_summary_only",
  "consequence": "multiple_relationships_may_fit_available_evidence",
  "next_action": "retrieve_adjusted_supplement",
  "source_ids": ["SOURCE-2"],
  "permitted_feedback": "approved_source_evidence",
  "resolution": null,
  "model_change": null
}
```

Conceptual controller logic:

```
contract = freeze_task_and_budget()
evidence = acquire_initial_evidence(contract)
while budget_remains:
    candidate = builder.propose_or_revise(contract, evidence, prior_diagnostics)
    source_checks = numerical_engine.check(candidate, evidence)
    challenge = scientific_reviewer.challenge(candidate, evidence, source_checks)
    action = builder.choose_action(challenge, remaining_budget)
    record(action, reasons, affected_components)
    if action is retrieve: evidence += screened_retrieval(action)
    elif action is repair_or_revise: prior_diagnostics = approved_diagnostics
    elif action is release_or_stop: break
freeze(candidate, evidence, decisions, generated_outputs)
independent_evaluator.run_reserved_analyses()
```

This is a design specification, not implemented pseudocode claimed as a working controller.

## 8. Keep both generation routes, with honest descriptions

**Agent-authored program:** the Agent selects and writes the statistical generator; the runtime draws records. This route is scalable and makes parameter provenance, source reproduction and repeated generation inspectable. A local RNG controls numerical sampling. It should be the first route for mechanism analysis because its changes can be traced.

**Direct record generation:** the LLM emits values or records using the same evidence and task contract. It remains a valid separate experiment. Give it a consistent cohort-level specification and preserve observed values. Check cross-batch behavior, repeated-value artifacts, conditional variation and dependency coherence. Store exact outputs, prompts, model/version and execution metadata; a requested seed does not make an external LLM API deterministic. It must not silently switch to a numerical generator while being reported as direct generation.

Both routes require downstream analysis checks. Neither is automatically more realistic. A later matched-budget comparison can ask whether direct generation uses qualitative context productively; it is not necessary to cross every route with every review configuration in the first pilot.

## 9. Data usefulness and uncertainty are analysis-specific

The output includes synthetic datasets, generator/version, evidence ledger, decision history and a compact analysis-support report. Use a **matrix of separate fields**, rather than one global “valid” label:

- Was the relationship supplied, implied by the input, or genuinely reserved?
- Does the source apply to the intended population and measurement?
- Does its interpretation depend on an unresolved assumption?
- Has that analysis been checked against independent observations, and with what result?

A new variable without target truth can still support research rehearsal, sensitivity analysis and planning of future measurements. Its new correlations are hypotheses to test. Agreement with input evidence shows successful translation; agreement on genuinely reserved analyses supplies stronger evidence of utility. This preserves the broad generation idea without advertising every additional column as a recovered observation.

Distinguish residual sampling variation, source/parameter uncertainty, and structural/transport uncertainty. Repeating one fixed generator estimates only the first. Propagate parameter uncertainty where the source and model support it; otherwise expose justified sensitivity ranges rather than invented calibrated probabilities. Avoid turning a finite set of alternatives into a confidence interval by labeling it one.

Compare scientific direction, shape, adjustment and subgroup interpretation where relevant. Exact estimates need not match. Practical differences should be judged using independently justified criteria, with estimates and uncertainty shown. Matching significance or matching two inconclusive results is not a universal success criterion. More generated rows do not add independent empirical evidence or prove recruitment costs have been replaced.

## 10. Minimum implementation changes

Build these in a **new versioned directory**. Preserve the frozen insulin experiment.

| Existing component | Next small extension | Acceptance check |
|---|---|---|
| `literature_gateway.py` | Screened supplement retrieval, cohort provenance and an explicit missing-artifact response. | Approved supplement provenance is recorded; prohibited target material never reaches the builder through the interface. Unsupported formats fail clearly. |
| `EVIDENCE_LEDGER.json` | Typed estimand/measurement records and links from model components to records or assumptions. | A marginal mean cannot be silently serialized as an adjusted slope; missing covariance/context remains explicit. |
| `model_spec.json` and Agent decision file | Generic component/assumption map, gap queue and versioned action records. | A consequential unresolved gap leads to an action or justified stop, not only a footnote. |
| Source/code review | Add a separate scientific-challenge artifact. | Challenge identifies a possible conclusion change and a discriminating observation, rather than generic requests for complexity. |
| `run_generation.py` | Reuse preservation/RNG/interface checks; generalize the variable schema in the new version. | No insulin-specific scientific constants are in the reusable controller. |
| Evaluator and freeze machinery | Reuse independently verified numerical logic; keep new reference access outside construction. | All scheduled constructions and draws are frozen before final results are computed. |

The previous fresh-context/read-scope instructions are useful procedural isolation, but all subagents in this desktop environment share filesystem access. They are **not an operating-system security boundary**. For the next confirmatory run, provide the generation Agent a restricted tool broker that serves only staged allowed files, or use a separately controlled execution environment with enforced file access; verify access logs and disclose remaining pretraining/source-overlap limits. Merely copying allowed files to another directory does not restrict access to the originals. Do not claim perfect blinding from a prompt alone.

The supplement extension needs content screening before display or agent access, including extracted tables and captions. It should follow source-linked attachments rather than arbitrary browsing. Begin with a few supported formats and request an explicit supported retrieval alternative when parsing fails; do not silently use partial tables. This improves retrieval capacity while preserving the experimental exclusions.

Do not initially add a web interface, many model providers, an agent-memory database, RL-based search policy, a universal source simulator, or a hundred baselines. The first deliverable is a small decision loop whose actions are observable and testable.

## 11. A bounded test of whether the design helps

### Development checks

Use artificial evidence cards to check the policy on generic problems: SE versus SD, marginal versus conditional effects, two summaries that do not determine a curve, common reference intervals that do not identify adjusted absence, and source assay/population mismatch. These are controller checks, not biomedical performance results. Include well-supported cases so the policy must also generate useful data rather than always defer.

The exposed insulin case can help debug the software and explanation. It is not a new independent test. Do not add its observed curvature or interaction to the next generator by hand.

### Fresh empirical pilot

1. A custodian selects and locks a fresh eligible cohort or a previously unexamined outcome, with source independence and overlap documented. A different NHANES cycle alone does not guarantee full independence. Use target predictors and population metadata only during construction.
2. Compare a **capable ordinary workflow** with the same workflow plus the explicit gap-to-action policy and scientific challenge. Both receive the same neutral starting packet, model version, allowed tools, information access, model-family freedom, comparable total construction/search/review budget and feedback policy. The ordinary Agent is allowed to identify gaps, review and revise; it is not deliberately crippled. An extra challenger must consume the proposed arm's total budget rather than provide free additional compute.
3. Plan two or three independent Agent constructions per workflow, with several fixed numerical draws per construction. These are pilot defaults to be frozen before execution, not a power calculation. Use actual execution/token/query costs, not just equal maximum query counts.
4. Lock a small set of scientifically meaningful analysis classes and their interpretation rules before outcomes are revealed. Include supplied-relation consistency checks and genuinely reserved questions. Do not invent universal clinical effect-size cutoffs merely to create a pass score.
5. Freeze generated outputs and support claims. Run the same locked analysis set on **every** construction and on the real reference, regardless of the Agent's support labels. The primary report concerns analytical agreement and disagreement of the generated data across that full set. Separately evaluate correct support claims, incorrect confident claims, unresolved/qualified claims, usable-analysis coverage and costs. Do not drop difficult analyses because the Agent declined to endorse them, collapse all uncertainty into “wrong,” or declare victory by refusing every useful analysis.
6. Inspect whether the policy caused **better generated analytical results**, and which concrete retrieval/model revisions produced them. A longer report with unchanged data is not an improvement in generation quality. Cost savings or a useful reduction in unsupported claims can be reported separately if demonstrated.

Different retrieval outcomes are an intended part of the policy comparison, not automatically a confound. If a gain appears, a small secondary replay with the same evidence bundle can separate improved retrieval from improved evidence-to-model use. Tool improvements such as supplement access must be available to both arms; otherwise their benefit would be mistaken for the new decision policy's benefit.

A first cohort tests feasibility, not general reliability. Broader confirmation should subsequently cover different populations, variables and evidence structures. Expand only if the mechanism produces consequential useful decisions and credible analytical gains. Stop or simplify if it mainly produces caveats, overhead, arbitrary flexibility, or gains restricted to relationships already supplied.

A previously unexamined outcome is preferable for this first policy test: a new insulin cohort would still evaluate a workflow designed after observing insulin-specific failure modes. If insulin remains the first deployment, declare that development history and reserve another outcome/population for confirmation. Two or three builds do not establish statistical superiority; the purpose is to decide whether the mechanism merits expansion.

## 12. What related work establishes, and what remains to test

| Primary work | Useful precedent | Boundary for this project |
|---|---|---|
| [G-Sim, ICML 2025](https://proceedings.mlr.press/v267/holt25b.html) | LLM proposes simulator structure; numerical methods calibrate parameters; diagnostics guide revision. | This structure/calibration loop is established. Our open problem concerns heterogeneous published evidence and useful target-population analyses. |
| [SPADA, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.525/) | LLM-induced dependency structure coupled to statistical generation. | Its conditional distributions are learned from row-level training data. It does not supply an unknown column's conditional distribution from papers alone. |
| [DALL-M, Computers in Biology and Medicine, 2025](https://doi.org/10.1016/j.compbiomed.2025.110022) | Contextual clinical feature augmentation and domain-informed generation. | Feature augmentation is not new by itself. Its retrieval uses known lesion context; downstream improvement does not independently establish the truth of every generated feature. |
| [ML-NMR, JRSS A, 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7362893/) | Relates individual-level models to aggregate evidence in each study population. | Requires statistical/transport assumptions; it is not automatic recovery of an arbitrary joint distribution from incomplete summaries. |

The prospective contribution is therefore testable: **can an Agent identify which missing or incompatible evidence threatens intended analyses, acquire more useful constraints, and revise a coherent generator so that richer synthetic data support better reserved scientific conclusions?**

RAG, multiple agents, code generation, synthetic feature addition and source-matching objectives alone do not establish novelty. This review is a bounded design comparison, not an exhaustive novelty search. A paper would need demonstrated analytical value, informative failures and an ablation showing what the decision mechanism contributes.

## 13. Recommended immediate sequence

1. Implement typed evidence, the gap/action record, screened supplement support and the scientific challenge in a new small version.
2. Audit the generic evidence-to-model traps with artificial examples and verify that supported tasks still proceed to generation.
3. Freeze a matched-budget ordinary-Agent comparison on a fresh protected case.
4. Evaluate the generated data through reserved scientific analyses; expand only if the new decisions improve practical usefulness.

The central change is operational: **an assumption that could change the scientific conclusion must affect what the Agent does next.** It should prompt targeted evidence acquisition, a justified model change, a useful sensitivity analysis or an honest limit on an analysis. It should not disappear into a footnote while the same generator is released unchanged as broadly validated.
