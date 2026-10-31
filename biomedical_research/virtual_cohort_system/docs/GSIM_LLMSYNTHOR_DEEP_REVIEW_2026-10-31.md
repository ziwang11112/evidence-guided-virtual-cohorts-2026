# G-Sim and LLMSynthor: deep reading and a constructive continuation

Date: 2026-10-31. Status: paper, appendix, official-release and data-access audit completed; no numerical reproduction or new cohort experiment performed.

Scope clarification after this review: the user explicitly includes **complete virtual-cohort generation with no individual-level records available**, using published evidence and a target-population specification. The hidden-column experiment discussed below is a pilot/adaptation case, not a restriction on the system. The updated [storyline and scope](PAPER_STORYLINE_AND_DIRECTION_2026-10-31.md) distinguishes evidence-only generation, column augmentation and cell completion. This clarification changes the forward research plan; it does not change the audited predecessor findings or completed experimental results.

## Decision

Both papers should become foundations and comparators for our work. Their existence does not close the research direction. It does change the contribution we must demonstrate: a generic LLM generation/feedback loop, multiple input sources, and downstream use of generated records already exist.

The most useful continuation is to investigate whether a generator can support scientific analyses when its evidence consists of published results computed under different population, measurement and adjustment conditions, while the target biomarker is entirely unobserved. A specific representation and execution mechanism, followed by convincing validation, could make that an extension worth publishing. A new application label or an extra Agent role would not establish it.

The immediate objective is to understand which parts of the predecessors work under our available information. We should not begin by trying to beat every number in their tables or by building a large new system.

## Reading boundary and supporting records

Three parallel reviews examined the methods, implementation and evaluation. The root independently checked key code paths and selected paper results. These are static findings; published numerical results below have not been rerun.

| Work | Primary version | Inspected public implementation |
|---|---|---|
| G-Sim | ICML 2025, PMLR 267; 49-page paper including appendices | `samholt/generative-simulations`, commit `72b5d51a7790b8b2ebc87973ee5e9d21aa818ece` |
| LLMSynthor | *Macro-Aligned Micro-Records Synthesis with Large Language Models*, arXiv v3, 2026-05-31; KDD 2026 DOI | `YihongT/LLMSynthor`, commit `92e443f93c6edecc0fa9ca3045d4204da7d42aa5`; README/images/metadata, no algorithm implementation |

Detailed source locators, tables, code observations and manifests:

- [G-Sim technical review](../reports/neighbor_deep_read_2026-10-31/gsim/GSIM_DEEP_REVIEW.md) and [source manifest](../reports/neighbor_deep_read_2026-10-31/gsim/SOURCE_MANIFEST.json).
- [LLMSynthor technical review](../reports/neighbor_deep_read_2026-10-31/llmsynthor/LLMSYNTHOR_DEEP_REVIEW.md) and [source manifest](../reports/neighbor_deep_read_2026-10-31/llmsynthor/SOURCE_MANIFEST.json).
- [Independent data and evaluation audit](../reports/neighbor_deep_read_2026-10-31/audit/DATA_EVALUATION_AUDIT.md).
- [Independent review of this synthesis](../reports/neighbor_deep_read_2026-10-31/audit/SYNTHESIS_REVIEW.md): passed, with the comparator-scope clarification incorporated below.

Original papers and retrieved third-party source snapshots remain local. Completed M16 artifacts and revealed outcomes were not changed or reused for tuning.

## 1. The actual objects produced by the LLM

| Question | G-Sim | LLMSynthor | Consequence for our design |
|---|---|---|---|
| What does the LLM produce? | Executable simulator structure, stochastic transition logic, parameters and bounds | Compact proposals specifying categories, numerical ranges and record counts | An Agent can control generation through a program or sampling plan |
| What does numerical software do? | Fit parameters, run the proposed simulator, compute diagnostics | Sample records from proposals, aggregate records, calculate frequency discrepancies | Program sampling is compatible with substantive Agent responsibility |
| What is revised? | Simulator code and exposed parameters | Where the next batch of records places probability mass | Structural revision and row-level editing are distinct mechanisms |
| What information drives revision? | Validation metrics and prior candidate history | Target-minus-generated bin/cell frequencies | Feedback must be defined in terms of information actually available to us |
| Does it require multiple Agents? | Inspected path uses one LLM for proposal/reflection plus tools | One proposal/dependency model plus statistical execution | Multi-agent collaboration is optional |
| Is foundation-model training required? | No LLM fine-tuning; SBI trains a separate posterior estimator | No task-specific LLM fine-tuning described | Start with existing models and inspectable tools |

Sources: [G-Sim, §3 and official implementation](https://proceedings.mlr.press/v267/holt25b.html); [LLMSynthor, §3 and Appendices A/C](https://arxiv.org/html/2505.14752v3).

Our M16 literal authorship of 200 values remains a useful feasibility branch. It need not define the whole method. A stronger default may let the Agent choose a reusable conditional distribution or program and let a sampler produce as many virtual records as needed. The contribution must remain visible in those choices and their evidence, rather than being hidden in a fixed analyst-written biological model.

## 2. G-Sim in detail

### Mechanism

The useful decomposition is:

`task/schema → LLM simulator code → numerical parameter fitting → validation diagnostics → LLM reflection and revised code → retain a candidate`.

The released implementation provides a `SimulatorStep` skeleton. The LLM fills the transition function and parameter interface. Evolutionary search or simulation-based inference then calibrates that fixed structure. The reflection receives validation loss, losses for individual state dimensions and fitted parameters. Candidate history is ranked by validation Wasserstein distance.

This gives a meaningful distinction between a wrong parameter value and a wrong structural assumption. A parameter optimizer cannot repair an absent nonlinear dependency unless the structure exposes it; an LLM can propose such a structural change.

### Actual data and feedback

The three main environments are hand-designed stochastic simulators: SIR epidemic dynamics, a supply system and hospital bed occupancy. They are real-world-inspired tasks, not observed COVID or hospital patient cohorts. The default released main-table path uses 100 trajectories per train/validation/test split, with 60 transitions each; the GP branch overrides this to 24 trajectories. A separate 10,000-trajectory sweep setting is not the default main-table sample size.

The most consequential implementation detail is the reference distribution. At each validation state, the SIR and supply evaluators draw 200 next states from both the candidate and the known true simulator; hospital uses 20. The resulting distributional discrepancy is feedback for structural search. Thus the reference offers more information than a finite table of observations, and substantially more than a few published regression coefficients.

This is appropriate for a known-simulator benchmark. It is not a feedback resource available when an unmeasured biomedical variable has no target observations.

The inspected code computes test scores for each candidate, but the feedback and ranking paths inspected use validation scores. We found no basis to assert test-score leakage into those prompts. A stricter implementation for our project should nevertheless keep the final evaluator outside the candidate execution path.

Code evidence: [SIR evaluation at the pinned commit](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/libs/SIR/env.py#L100-L120), [feedback serialization](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/utils/llm_tools.py#L53-L96), [candidate search](https://github.com/samholt/generative-simulations/blob/72b5d51a7790b8b2ebc87973ee5e9d21aa818ece/agents.py#L456-L743).

### Evaluation and results

The paper combines distributional evaluation, prediction errors, known-graph comparisons, intervention demonstrations and a decision-use example. That breadth is worth learning from: the paper asks what an executable simulator enables, beyond fitting a single summary.

Selected Table 2 test Wasserstein means, lower is better, as reported by the authors:

| Method | SIR | Supply | Hospital |
|---|---:|---:|---:|
| One-shot code, no calibration | 1.17 | 2.63 | 102 |
| One-shot code, evolutionary calibration | 0.469 | 9.89 | 103 |
| G-Sim–ES | 0.405 | 1.55 | 101 |
| G-Sim–SBI | 0.351 | 1.22 | 5.24 |

The full review preserves the reported confidence intervals. These values concern different systems and are not a common-unit composite score. They support the value of structured search in those tasks, while also showing that calibration is not uniformly beneficial. In a separate fixed-structure SIR comparison, Table 5 favors ES over SBI on Wasserstein, 0.814 versus 1.29. That is a different experiment, not a contradiction.

Source: [published paper, Table 2 p. 7 and Table 5 p. 47](https://raw.githubusercontent.com/mlresearch/v267/main/assets/holt25b/holt25b.pdf).

### What must be resolved before code reproduction

The public repository is inspectable and useful, but it is not a verified turnkey reproduction of the paper tables:

- Paper settings name O1 and typically five refinement loops; the release selects `o3` and three total generations. Parameter-search settings also differ.
- Fresh unseeded `default_rng()` instances bypass global seeding. Shared dataset realizations across methods are not guaranteed by those seed labels.
- The released SIR SBI path conditions on the first training trajectory and evaluates posterior-mean parameters. It does not pool all training trajectories into that observation or propagate the full posterior through every downstream analysis.
- Some baseline distribution evaluations use different state representations, deterministic repeated predictions and a smaller evaluation subset. Their exact comparability needs repair or explicit qualification.
- In the default SBI path, the flag intended to disable parameter optimization is not checked in the SBI evaluator. The released default should not automatically be called a faithful uncalibrated ZeroShot comparison.

These are release-level observations. Their numerical impact has not been measured here, and they do not invalidate the core idea. We should borrow the decomposition, establish a clean controlled implementation, and avoid relying on an unreproduced large performance gap as a promise for our application.

## 3. LLMSynthor in detail

### Mechanism

LLMSynthor starts with variable descriptions and macro-statistics. The LLM chooses related variable groups, and the procedure uses marginal histograms and selected joint contingency tables as constraints. A deterministic calculation identifies underrepresented cells in the cumulative synthetic data. The LLM proposes configurations and counts for the next batch; continuous values are sampled in proposed intervals, uniformly in the main description. The batch is appended and the cycle repeats.

This is more structured than literal row-by-row generation. The LLM decides which combinations and ranges need more mass; the sampler handles repeated draws. At the described default, there are five proposals per iteration and 100 iterations, using GPT-4.1-nano. Larger or smaller model comparisons are included, but a large reasoning model is not the main requirement of its method.

Important qualifications:

- Inferring which variables belong together is separate from obtaining their numerical joint frequencies.
- Section 3.2 already permits an LLM approximation of missing joint statistics when approximate control is acceptable. We cannot claim that supplying missing relationships is entirely absent from this work.
- The experimental implementation obtains target macros from reference micro-records. Appendix A describes six quantile bins and refinement into eight sub-bins when such records are available. Those extra frequencies are an information resource, not merely extra computation.
- The described update appends records. It cannot remove an overrepresented record; it dilutes overrepresented regions by adding other ones. This differs from filling a fixed cohort while preserving its observed cells.
- The copula analogy motivates separating marginals from dependencies. The paper does not establish a calibrated copula density for unidentified biomedical relationships.

Sources: [§3](https://arxiv.org/html/2505.14752v3#S3), [Appendix A](https://arxiv.org/html/2505.14752v3#A1).

### Data, evaluation and the strength of the evidence

| Case | Actual data / generated size | What it tests | What it does not establish |
|---|---|---|---|
| Tokyo mobility | Open PFLOW plus time/activity information from LLMob; 30,000 generated trips | Mixed-source aggregate alignment, maps and contextual scenario generation | Recovery of measured individual travel or an independently verified concert effect |
| E-commerce | 2,000 reference records from a known six-variable Bayesian network | Marginal/joint fidelity, semantic rules, two-sample classification and rule-derived predictive tasks | Real measured clinical outcomes or recovery from unrelated sparse medical studies |
| ACS population | About 15,000 South Carolina survey households, with variable-length person records | Household plausibility and 16 policy queries across six categories | Demonstrated transport to a new population whose required variable was never measured |

Source: [LLMSynthor, §4](https://arxiv.org/html/2505.14752v3#S4).

Open PFLOW is itself a reconstruction from open information, not a table of actual individual GPS trajectories. ACS is survey microdata. These source types should not be combined under one generic “real patient data” label. See the [original Open PFLOW paper](https://doi.org/10.1016/j.trc.2017.09.016) and [official Census PUMS access](https://www.census.gov/programs-surveys/acs/microdata/access.html).

The e-commerce experiment supplies numerical joint tables over related groups from the generating network. Its good performance on those groups is useful constraint-fitting evidence. The ACS queries provide downstream-use evidence, so it would be wrong to describe this paper as evaluating only marginal similarity. The exact overlap between its input constraints and all 16 queries is not specified sufficiently to label every query independently withheld.

Selected published results:

- E-commerce price Wasserstein: LLMSynthor 12.762 versus TabSyn 114.120; age/gender/category joint JSD: 0.071 versus 0.083 (Tables 1–2).
- ACS household rejection: 13.3% for LLMSynthor versus 57.8% for HMM (Tables 5–6).
- ACS query-category error is lowest for LLMSynthor in five of six categories. Mobility favors NVI, 0.24 versus 0.35; the prose's all-six claim is too strong (Table 5).

These are author-reported values. They demonstrate useful outcomes in the stated settings without implying perfect realism or universal superiority. [Paper Tables 1–6](https://arxiv.org/html/2505.14752v3).

### Reproduction readiness

As checked on 2026-10-31, the linked official repository contains no algorithm implementation, preprocessing scripts or experiment configurations. Branches, tags, releases and the project page did not reveal an alternate official implementation. Its README retains an older title and promises a future release.

We can implement a transparent reconstruction from the paper. We cannot call that an official-code reproduction or claim to recreate the exact published results without the missing task details. [Pinned repository](https://github.com/YihongT/LLMSynthor/tree/92e443f93c6edecc0fa9ca3045d4204da7d42aa5).

Other reproducibility items include the exact ACS year/product and filters, all macro tables and query definitions, e-commerce probability tables and label rules, generation/rejection order, seeds and API budgets. Table 1 distinguishes macro-only, macro-plus-micro and micro-trained baselines, unlike the surrounding blanket statement that all baselines use microdata. We should preserve those information categories in any comparison.

## 4. What these papers teach us about making a convincing paper

Our interpretation of their experimental logic is:

1. Define a concrete unavailable resource and the permitted input that substitutes for it.
2. Give the LLM an explicit generative decision, with a computable consequence.
3. Validate the mechanism in a controlled setting with known ground truth.
4. Demonstrate practical use across more than one type of system or record.
5. Show which component, information source or feedback step accounts for the effect.
6. Include downstream use, remaining errors and resource costs.

This structure is reusable. It does not require copying every baseline, adding a large multi-agent architecture, or inventing a new loss before determining the bottleneck. It does require a method-specific claim backed by experiments.

For our project, constraint fit and useful scientific analysis should be reported separately. A generator that matches every provided group mean can still miss an adjusted age relation or a nonlinear effect. Conversely, imperfect marginal fit does not automatically erase all analytical usefulness. Our completed [M16 report](../MILESTONE_16_RESULTS.md) already contains a concrete mixed repair outcome, but not enough evidence for a general method claim.

## 5. Recommended extension: study-conditioned generation

### The research question

Can a scientific Agent convert incomplete published evidence into a target-compatible data generator when different studies use different populations, measurements and analysis specifications, and can the resulting frozen data support useful target analyses?

The central technical object should be an executable description of what each source result means:

`source population and eligibility → measurement/unit mapping → analysis formula and adjustment set → reported statistic and uncertainty`.

For example, a conditional coefficient from `log(marker) ~ BMI + age + sex` is not interchangeable with an unadjusted BMI/marker correlation or a group-specific arithmetic mean. The system should execute the corresponding analysis in a source-compatible simulated setting and compare the appropriate statistic. It should not pool the numbers merely because they share a biomarker name.

### A minimal implementation design

| Object | Agent responsibility | Deterministic responsibility |
|---|---|---|
| Evidence record | Extract source context, statistic, adjustment set, uncertainty and applicability rationale | Verify units/schema, preserve citation and extraction provenance |
| Generative proposal | Choose conditional factors, distributions, nonlinear forms, measurement mappings and assumptions | Validate the proposal, preserve observed target covariates, execute sampling |
| Source analysis operator | Map the source's analysis to an explicit formula and population definition | Run the formula, calculate discrepancies and sampling error |
| Calibration/revision | Interpret conflicts; revise structure, request a missing constraint, retain or stop | Fit exposed parameters to permitted source evidence; preserve candidate history |
| Scientific-use evaluation | No access to locked target answers during construction | Apply the same prespecified analyses to frozen generated and reference data |

An important unresolved input remains: to reproduce an adjusted source coefficient, the source covariate distribution may be needed. Published summaries might not identify it. We must either obtain adequate source information, state a reconstruction assumption with sensitivity analysis, or treat the constraint as only partially executable. A source operator is not made valid simply by putting a regression formula in JSON.

Study heterogeneity and individual residual variation must also remain distinct. Differences between published means do not directly estimate within-person or within-population variability.

### What could become a contribution

- A reliable transformation from heterogeneous published estimates to executable generation constraints, rather than treating all estimates as statistics of one population.
- A reusable method for keeping observed covariates fixed while generating an entirely unmeasured variable from those constraints.
- Evidence about which scientific analyses remain reliable when the joint distribution is only partially constrained, including explicit limitations or uncertainty where appropriate.

These are contribution candidates, not verified priority claims. Indirect inference, statistical matching, evidence synthesis, transportability and related recent generators must be considered before asserting novelty. G-Sim already discusses aggregate evidence, structural uncertainty and active queries; LLMSynthor already combines sources and permits approximate missing constraints. Our contribution would have to lie in a concrete working mechanism and the evidence supporting it.

## 6. The smallest informative next experiment

This is a proposed next unit, not a launched experiment.

### A. Establish a controlled reference before another biomedical target

Use a small known joint distribution with continuous variables. A separate data constructor creates source populations and a target population. Only selected source summaries and target covariates reach the generator. The target's missing variable and scientific analyses remain reserved for evaluation.

Start with two conditions:

1. **Compatible sources:** shared population and measurement conditions, where ordinary aggregate matching should be adequate.
2. **Heterogeneous sources:** changed population composition or measurement/adjustment definitions, with enough documented information to test whether respecting those conditions matters.

At least one analysis should be directly constrained, one should be unprovided but recoverable under the available evidence, and one should be deliberately weakly identified. An impossible relationship should not be used to manufacture a baseline failure.

### B. Adapt the predecessors explicitly

- A **LLMSynthor-inspired proposal/count branch**, clearly labeled a paper-based reconstruction. For fixed-participant enrichment, preserve IDs and observed values and document how the original append-only operation is adapted.
- A **G-Sim-inspired program/calibration branch**, with source-summary diagnostics replacing simulator-oracle feedback. This is an adaptation, not a claim that the original implementation accepts our evidence unchanged.
- Within the same branch, compare ordinary pooled-summary handling with study-conditioned operators. Keep the evidence packet, model access, revision allowance and evaluation protocol comparable.

The first debugging pass can use one branch. Two branches become valuable once we need to establish that a result is not peculiar to a particular sampling representation. Literal row generation can remain an additional diagnostic branch; it need not carry the principal method claim.

Pooled versus study-conditioned handling is a mechanism ablation. It does not establish an Agent-specific advantage over competent statistical data fusion. If we later make that stronger claim, include a condition-aware statistical generator with the same evidence, or keep the contribution claim at the supported level. An effective ordinary Agent or simple statistical implementation is a useful outcome, not an experiment to suppress.

An optional target-macro reference may show what happens with privileged target marginals/joints, but it must be reported as a different information tier. It is not a fair same-input competitor to an evidence-only system.

### C. Evaluate useful analyses and explain the result

The initial outcome panel should include adjustment-sensitive slopes, a nonlinear relation and a subgroup/interaction analysis. Report direction, magnitude on its own scale, stability across repeats and any stated uncertainty. Preserve distributional and validity checks as diagnostics. Do not collapse all of them into a win count or equate a positive sign with equivalence.

Repeat generation under more than one candidate structure when the evidence permits competing structures. Additional generated rows primarily reduce Monte Carlo error; they do not create new measured evidence. An interval calculated by treating every synthetic row as a newly observed independent participant cannot represent all source and structural uncertainty.

For revision, show both permitted source fit and reserved analysis performance at each frozen stage. This tests whether feedback helps the intended use or only improves its own objective.

### D. Continue/stop decisions

| Observation | Interpretation and next action |
|---|---|
| Both branches work with compatible summaries but fail under known source differences | Investigate how source conditions are represented; this is a concrete bottleneck |
| Study-conditioned treatment improves reserved analyses across repeated, heterogeneous cases | Proceed to fresh public biomedical cases and a larger controlled study |
| Ordinary handling works equally well | Adopt the simpler implementation; do not force a complex system contribution |
| All methods fit source statistics but disagree on weakly identified analyses | Improve evidence coverage or quantify the unsupported conclusions; do not tune against revealed targets |
| Only the privileged target-macro reference works | The limiting resource may be information, not Agent strength or sampling code |
| A repair improves its own feedback but harms unprovided analyses | Record the trade-off; revise the diagnostic mechanism only in development cases |

A small successful run would justify expansion, not a top-conference claim. Publication-grade evidence would need multiple controlled data-generating mechanisms and independent biomedical cases, an explicit information budget, faithful adapted comparators, and a reproducible release.

## 7. Practical decision now

Continue the virtual-data direction. Borrow G-Sim's structure/parameter separation and LLMSynthor's compact proposal execution. Focus the first methodological experiment on converting study-specific evidence into appropriate feedback. Keep scientific analyses of the resulting data central.

The next implementation should be small enough to reveal whether this evidence handling changes the outcome. It should reuse our existing evidence/provenance, frozen-candidate and evaluator infrastructure. No new LLM training, HPC job, large target download, or large-scale benchmark is justified by this review alone.

This document completes the requested deep reading and establishes a constructive path. The detailed reviews retain negative findings, release limitations and exact source locators so subsequent design does not depend on the titles or abstract-level similarity of the papers.
