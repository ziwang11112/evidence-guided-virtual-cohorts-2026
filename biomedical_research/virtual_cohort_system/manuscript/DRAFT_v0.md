# Evidence-guided generation of virtual biomedical data for reusable scientific analyses

Working manuscript, 31 October 2026. This is a provisional problem-and-method draft, not a submission-ready article. The core reference profile has completed its independent implementation review; a new prospective real-case evaluation has not begun. Bracketed completion tasks are intentional. No historical pilot is relabelled as confirmation of the consolidated version.

## Abstract — provisional

Biomedical analyses can require measurements that are unavailable as individual records, absent from an existing cohort, or missing for some participants. Published studies may contain relevant distributional and associative evidence, but those results apply under different population, measurement and analytical conditions. We investigate whether a scientific Agent can translate such evidence into a documented stochastic generator and produce virtual data that support a declared set of scientific analyses. The method separates evidence extraction and assumptions, Agent-authored scientific construction, deterministic execution and source diagnostics, bounded revision or retention, and independent evaluation of a frozen virtual release. Complete-cohort generation with no individual inputs is a central setting; unmeasured-variable enrichment and missing-cell completion are distinct optional settings. Development studies show selected analytical feasibility alongside discrepancies in effect magnitudes and distributions. An artificial extension pilot verifies preservation of existing records and source-consistent conditional generation; it does not establish biological transport or algorithmic superiority. [Complete this abstract only after the prospective core-version case and its full claim ledger are locked.]

## Introduction

The immediate practical problem is a gap between the measurements a research question requires and the individual data available to the researcher. In one setting, no participant table is accessible, although related studies report aggregate results. In another, a cohort has measured some covariates but omitted a relevant biomarker. These settings motivate virtual data that can be inspected and analyzed using familiar statistical tools. The intended output is a reusable analytical dataset, rather than a single answer to a specific regression query.

Published evidence does not generally determine a unique joint distribution. A mean in one population, an adjusted coefficient in another, and a subgroup contrast under a different measurement definition cannot be treated as interchangeable constraints. Matching selected source statistics may leave other dependencies unresolved. A virtual biomarker value also should not be interpreted as recovery of a particular participant's true measurement. The central question is therefore which scientific analyses a generator can support under its evidence and transfer assumptions, rather than whether it can emit a large table of plausible-looking rows.

We study an Agent-assisted procedure for constructing those generators. The Agent selects a scientific representation and records the basis of its parameters; deterministic tools execute the construction and calculate source diagnostics. The same frozen virtual release is subsequently evaluated across prespecified analyses. This separates source agreement, transfer to an independent target, and reuse for analyses not directly calibrated. It also permits an explicit negative or unresolved result when the available evidence does not justify the required joint structure.

[Related-work section to be finalized against the existing G-Sim/LLMSynthor implementation audit and the broader statistical literature. A generic generate–check–revise loop, conditional sampling, natural-language input and multiple Agents are not claimed as novel. The final contribution statement must specify the information regime, study-condition representation, actual implemented capability and empirical evidence.]

## Research questions and intended claims

1. Can the procedure turn admitted study-level evidence and a population specification into an executable generator with inspectable scientific assumptions?
2. Can one frozen generated dataset support the declared scientific analyses in an independently measured reference population, including analyses not directly fitted?
3. When additional applicable evidence or a source-feedback revision is used, which analytical conclusions improve, remain unchanged or deteriorate?

The first question includes implementation feasibility. The second requires prospective real-reference evaluation. The third requires a contrast matched to the information and budget being compared; it is not answered by a retention event or by lower source discrepancy alone. No component-superiority claim follows from the current artificial integrations.

## Methods

### Task and information regimes

Each task declares the population, intended estimand, variables, units, permitted observations, source restrictions and analytical uses. In complete-cohort generation, the generator receives no individual records. In enrichment, existing columns are preserved and new variables are generated conditionally. In completion, measured cells remain fixed and only eligible missing cells are generated. Results for these regimes are reported separately because their available information differs.

For a real validation case, measured reference outcomes remain outside the builder's permitted inputs and feedback. Any target aggregates or demographic descriptions supplied to the builder are explicitly listed. Source publications that use the same participants or target cohort require an overlap decision and cannot be described simultaneously as independent external evidence. The available data and source metadata determine case admission before target-effect inspection.

### Evidence and scientific construction

Evidence items retain the original locator, population and selection, measurement definitions, statistic and adjustment set, value and reported uncertainty. Shared cohorts are tracked. Model parameters cite reported values, derivations or named assumptions; unreported dependencies remain unresolved unless an assumption is declared.

One scientific Agent constructs the initial generator and a concise rationale. The program route implements `generate(observed, spec, seed)` and returns a typed table. The coordinator supplies the task and execution controls, while the Agent chooses the stochastic family, dependence structure and parameters. A direct-table route exists as a separate implementation option; it is not exercised by the consolidated reference replay. The Agent's general tools are subject to procedural input restrictions, while generated code executes in the configured isolated runtime.

### Source feedback and bounded revision

Candidate validation and explicit statistic-recipe review precede freezing. Feedback is calculated from verified successful outputs and retains all scheduled computable and non-computable checks. The Agent may revise, retain, seek permitted evidence or stop within the case budget. Actual feedback is copied and hash-bound into the subsequent candidate, while the parent remains intact. Retention is a valid decision and is reported without implying improvement.

The current whole-cohort feedback adapter calculates identity-measurement operators on the existing generated table. It does not automatically regenerate every source study's population or convert measurements. Differences in source applicability are therefore declared as approximations or unresolved checks. Enrichment source replay can execute a frozen generator under supplied, frozen covariate-only source contexts. Any additional case-specific source or target adapter must be separately described and bound.

### Analytical usefulness and uncertainty

The primary evaluation compares the same prespecified analyses applied to virtual and real-reference data. Relevant outputs may include association direction, adjusted effect scale, subgroup contrast or nonlinear shape, with diagnostic checks needed for interpretation. No universal numerical tolerance is assumed. Practical agreement rules, where defensible, are fixed for the scientific use before reference disclosure; otherwise discrepancies and uncertainty are reported without asserting equivalence.

Repeated draws characterize simulation variation. They do not create additional measured source information. Individual residual variation, source-estimate uncertainty, alternative scientific structures and population transport uncertainty are distinguished. Sensitivity scenarios do not automatically form calibrated probability intervals. A finite measured reference is itself an estimate or a defined finite-cohort quantity, not an unquestioned population truth.

### Reproducibility

The method and case protocols bind source artifacts, task and Agent instructions, scientific candidates, code, runtime records, feedback and revisions. Actual execution counts, unique output identities, retained outputs, failures and unavailable runtime metadata are reported. Raw and generated individual tables remain local under the current project-sharing policy; reviewed code, permitted source definitions and scalar summaries are available in the private development repository. A public release plan remains to be specified.

## Results — development evidence, not core-version confirmation

The current result record includes real-reference development pilots with preserved selected associations and mismatched magnitudes or distributions. Earlier versions used different configurations and must not be pooled into confirmation of the consolidated method. Their complete records, including source-fit improvements that did not transfer and unsupported component gains, will populate a development-results appendix.

The C5 artificial pilot evaluated complete joint generation and later conditional extension under the same fully specified Gaussian evidence. Nine fixed 2,000-row executions produced three parent tables and six final three-variable tables. All three extensions preserved the 6,000 original rows and their prior analyses exactly. An independent audit recomputed 48 endpoint estimates and 210 diagnostics. The result establishes compatibility of these implementations in that specified example; the analytical answers were implied by the supplied evidence, and no superiority over joint generation was established.

The core v0 reference integration connected an Agent-authored complete-cohort program, actual isolated execution, six verified source diagnostics and one feedback-bound retention decision. It used an admitted artificial source reporting three within-stratum mean/individual-SD pairs. The Agent chose a Gamma construction and retained it after reviewing the source discrepancies. Two scheduled same-seed executions yielded one unique 768-row table. Independent recomputation of all six statistics at both stages agreed within 4.44e-16; source, code, feedback and parent lineage remained intact. This establishes the reference profile's implementation linkage. It does not establish numerical repair efficacy, broader source-population replay or biomedical accuracy.

[Prospective core-version real case: not yet admitted or evaluated. Report every planned analysis, source-supported versus assumption-dependent structure, reference uncertainty, failures and unresolved outcomes. Do not fill this section with expected or selected favorable results.]

## Discussion — claims to retain and questions to resolve

The practical contribution under investigation is making distributed evidence usable as analytical data with inspectable assumptions. The present implementation demonstrates how scientific choices, data generation, source diagnostics and retention/revision can be recorded separately. Whether this procedure provides useful target-population analyses depends on the applicability and informativeness of the source evidence and requires independent evaluation.

Dynamic requests can help reuse a release or extend it with another variable, but an interface cannot supply an absent scientific relationship. Likewise, increasing the number of rows can improve numerical precision while leaving source and transport uncertainty unchanged. Claims of replacing clinical measurements, reducing recruitment expenditure, calibrated uncertainty or universal generation of arbitrary variables require separate evidence and are outside the initial scope.

The next result should distinguish an implementation limitation from insufficient evidence and from a failure of population transport. A source-consistent model whose downstream analysis fails is informative about the assumed joint structure; it must remain in the result record. Conversely, a successful narrow use does not establish general fidelity across all variables, populations and analyses.

## Planned displays and evidence links

- Figure 1: actual evidence-to-generator procedure, with whole-cohort, enrichment and completion information regimes distinguished.
- Figure 2: all prespecified real-case analyses on the same frozen release, with reference uncertainty and unresolved findings.
- Figure 3: an evidence/revision contrast only if tested, showing initial and final source and target outcomes together.
- Supplement: complete evidence/assumption ledger, development failures, source overlap, actual run identities and implementation audits.

Working records: [core specification](../reports/core_v0_2026-10-31/CORE_METHOD_V0.md), [integration plan](../reports/core_v0_2026-10-31/INTEGRATION_PLAN.md), [draft-readiness gates](../docs/DRAFT_READINESS_CHECKLIST_2026-10-31.md), [C5 results](../reports/c5_dynamic_extension_2026-10-31/RESULTS.md), and [prior-work/storyline analysis](../docs/PAPER_STORYLINE_AND_DIRECTION_2026-10-31.md).
