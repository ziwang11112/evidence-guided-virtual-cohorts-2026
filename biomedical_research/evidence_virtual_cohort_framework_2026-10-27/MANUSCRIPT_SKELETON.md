# Evidence-Guided Virtual Cohorts for Biomedical Analysis and Study Planning

Working manuscript scaffold, 27 October 2026. This is not a completed paper. Prospective experiments below have not been run. Do not fill result placeholders with expected improvements.

## Abstract scaffold

**Problem.** Researchers often have access to published statistics and partial records before they have a complete cohort suitable for their planned analyses. Virtual data could help prepare analytical workflows and examine design assumptions, but realistic marginal distributions alone do not establish scientific utility.

**Approach.** We propose an evidence-guided Agent workflow that constructs executable cohort generators, records study and measurement applicability, separates observed constraints from unidentified dependence, and reports the sensitivity of planned analyses across an examined, prespecified set of evidence-compatible scenarios. This finite set is not exhaustive. Whole-cohort synthesis and partial-record completion are evaluated separately.

**Evaluation.** The planned evaluation replays prespecified analyses on real and generated cohorts, reserves relationships not supplied to the Agent, retains uncertain findings, and evaluates one research-design decision. Comparisons use the same available information and distinguish independent Agent constructions from repeated samples of a generator.

**Current development evidence.** In an exposed 75-person longitudinal completion pilot, two selected qualitative findings were retained in all three masks. The statistical comparator and missing-only analysis also retained those findings. Agent completion did not improve primary coefficient recovery over missing-only. Earlier whole-cohort pilots showed incomplete preservation of unprovided dependence. These motivate broader evaluation; they are not confirmation of the proposed policy.

**Confirmation results.** [Insert only after frozen independent-case experiments and the research-use evaluation.]

## Introduction argument

1. Research preparation often precedes complete data access. Explain concrete use: analysis debugging, plausible-scenario exploration and deciding which measurement to collect.
2. Existing synthetic data and Agent systems already provide orchestration, aggregate-to-record generation and scientific-utility evaluation. Cite G-Sim, SynthCraft, LLMSynthor, DALL-M, MeLD and longitudinal analysis replay rather than claiming the broad category is new.
3. The remaining tested question is whether limited, heterogeneous evidence can support *unprovided* biomedical analyses and useful decisions, and whether the system exposes ambiguity instead of hiding it in a single plausible table.
4. State contributions only at the level supported by results: shared workflow, evidence-regime benchmark, a tested construction/revision mechanism, and a measured use case.

## Methods to write now

- Cohort selection and exposure registry; exact patient/visit/analysis denominators.
- Evidence extraction, study-native operators, population and measurement mappings, overlapping source cohorts.
- Information regimes: target-summary reconstruction, cross-study generation and observed-data completion.
- Ordinary and proposed Agent policies; model/prompt/version logging; fixed budgets and permitted feedback.
- Scenario construction, source checks and qualification of sensitivity ranges.
- Numerical generation, preservation contracts, independent implementation audit and output freeze.
- Prespecified claim families and identical real/synthetic analysis code.
- Direction, practical magnitude and uncertainty-state reporting; copied-control exclusion.
- Correct distinction between multiple imputations and repeated fully synthetic cohorts.
- Comparator information parity, failure retention and study-level statistical units.
- Independent confirmation and research-design utility; limitations of reference resampling.

## Results order

1. Data accessibility and ability to reproduce the reference analyses, including discrepancies in published annotations.
2. Whole-cohort performance on reconstruction and reserved analyses, separated.
3. Completion utility on analyses that actually use generated cells.
4. Variation across independent builders, random samples and studies.
5. Mechanism ablations and failures under conflicting/missing evidence.
6. Utility for the prespecified research-design decision.

Existing Ross results belong in development evidence or a clearly labelled initial experiment. A large number of output rows cannot make that study an independent confirmation.

## Discussion points to retain regardless of outcome

- Scientific-conclusion preservation does not require exact record recovery.
- Matching sign/significance alone can conceal an exaggerated effect or underestimated uncertainty.
- Marginals do not identify paired or cross-time dependence; more virtual rows do not supply missing evidence.
- An unresolved empirical association is not a known null.
- Partial completion of mostly real data does not establish full synthesis performance.
- Agent-authored statistical programs and directly authored records have different costs and failure modes; neither is automatically superior.
- Source-conditioned fidelity and target-population transport require separate evaluation.
- A successful software/audit pipeline and a superior scientific method are distinct achievements.
- Virtual-data outputs support research rehearsal within demonstrated limits; original empirical confirmation remains necessary for new clinical claims.

## Result-dependent conclusion templates

**If the proposed policy improves reserved analyses and decisions across cases:** describe the specific regimes, effect sizes, tradeoffs and remaining failures; avoid a universal reliability claim.

**If it preserves analyses but does not outperform adequate alternatives:** frame a validated workflow/resource contribution, with an honest assessment of when the Agent saves preparation effort.

**If performance remains inconsistent:** report the benchmark and failure structure, narrow the supported uses, and do not label the scenario policy a validated solution.

Sources and execution plan: [Methods and experiment plan](METHODS_AND_EXPERIMENT_PLAN.md). Results are linked only after execution and independent audit.
