# Proposed next unit: improve evidence-constrained data generation

31 October 2026. Status: proposal in response to the user's question about the next step and thematic alignment. No new experimental cycle, generator execution, target acquisition or automation has been started.

## Unchanged research theme

Published biomedical evidence, a target-population specification and optional observations are translated by a scientific Agent and statistical tools into reusable virtual individual-level tables. Full-cohort generation with zero individual inputs remains central; unmeasured-variable augmentation and missing-cell completion remain additional use cases. Actual downstream analyses determine demonstrated utility.

The output remains a dataset, its executable generation recipe and evidence/assumption record. Analysis-use boundaries are validation results, not a replacement research topic. A normal scientific Agent is a valid implementation. A claim of superiority over another Agent is not required to test data-generation feasibility.

## What the completed case does and does not establish

Cycle 2 executed source-conditioned replay and independent target evaluation. It included algebraic parameter derivation, not merely unaudited code generation. However, it did not demonstrate beneficial feedback-driven numerical fitting, a scientific structure revision, autonomous evidence-gap retrieval, or robustness across model families. Both independently authored constructions used the same linear Gaussian family and assumed residual correlation 0.30, then retained their models.

The observed failures are incomplete source age-profile reproduction, quantitative age/BMI transfer discrepancies and narrow generated dispersion. The experiment did not isolate whether missing evidence, population/measurement mismatch, parameter estimation or functional form caused them. A source-fit improvement alone cannot establish improved transfer.

## First unit: bounded source-side fitting and revision

Use the already audited source evidence in a new source-only development task, with no ENSANUT target context, target effects or target table supplied to the builder. Preserve all old frozen candidates and results. This unit is an implementation/mechanism test, not another validation on the exposed target.

1. **Agent proposes the scientific construction.** Start with a transparent low-complexity candidate. Permit at most one genuinely different source-defensible alternative when a documented source discrepancy motivates it. For example, source age-band evidence may motivate a low-complexity nonlinear age response; it does not prove that nonlinear aging caused the previous failure. Agent-authored model choices and parameter provenance must be explicit.
2. **A numerical tool fits declared source-supported parameters.** Before fitting, freeze the model, permitted parameter set/bounds, source observation operators, loss/scaling choices, scientific source requirements and numerical budget. Reproduce each source statistic in its own population, units and adjustment set. Do not splice separate regression coefficients into a full conditional equation. No target statistic enters fitting.
3. **Unknown structure stays visible.** Unreported source covariance, source-population composition and transport assumptions must not be unconstrained optimizer knobs used to force agreement. Retain a small explicit set of defensible scenarios where information does not identify a unique value. Scenario ranges are not automatically posterior intervals.
4. **Source discrepancies trigger specific actions.** Recheck extraction/units/operators first, then distinguish parameter mismatch from structure limitations or insufficient information. Allow one bounded evidence-gap request when a particular missing statistic would change the construction or distinguish candidates. Retrieval asks for that statistic and population definition, not the preferred answer or effect direction. Admit new evidence before use; preserve failed searches and conflicting studies.
5. **Check completed candidates using unused source-simulation seeds.** Report every fixed source check before and after fitting, with any tradeoff or remaining contradiction. These checks test Monte Carlo stability on the same source evidence, not independent clinical replication. Retention remains permissible; no scientific improvement claim follows from a no-op.

Provisional caps for planning: one scientific author, at most two scientific structures, at most 40 numerical objective evaluations per structure, two unused source-check seeds, and one evidence-gap request covering at most three additional primary studies. These caps require a concrete implementation specification before execution; they are not an active protocol. Existing source replay and isolation should be reused. No new training, paid API or HPC is proposed.

## Source-side decision

Before running, define meaningful source requirements using each statistic's actual uncertainty and scientific role. Do not infer a confidence level or standard error that a source does not report. No universal low-loss threshold or post hoc tolerance is supplied here.

Proceed to new-target validation only if a candidate can produce valid data and satisfy the justified source requirements jointly, with stable unused-seed checks and explicit unresolved assumptions. A numerical improvement that substantially worsens another key constraint is reported as a tradeoff. If no candidate is compatible, report the conflict and missing evidence and stop this unit; do not add unrestricted study offsets or silently remove adverse evidence.

## Subsequent real-data test

Only after the source-side unit is informative, admit one fresh external target using metadata and predeclared eligibility/measurement criteria before viewing its effects. The target must have a defensible relationship to the source populations; source-to-target compatibility is not guaranteed by calibration.

For the full-cohort mode, the Agent receives published evidence and a population description, with no target individual rows. Freeze the generator, any retained scenarios, source inputs and a small analysis plan before unveiling target results. Include a primary scientific relationship, a useful analysis not directly fitted, and distribution/residual diagnostics. Assess direction, scientifically relevant magnitude and variability, with appropriate reference uncertainty. Individual values need not match real participants, and neither a finite sample mean nor a synthetic large sample is population truth.

If claiming that fitting, retrieval or a structure change improves quality, isolate that change with an appropriate same-information comparison or ablation. For a feasibility claim alone, the central test remains whether the generated table supports the intended analyses against an independent real reference. Do not turn the experiment into a mandatory Agent leaderboard.

## Deliverables and novelty boundary

Deliver the working source-calibration/revision path, all candidate recipes and checks, generated source-development tables kept local, and a continue/stop decision for independent whole-cohort validation. A later successful real case would deliver a virtual cohort with a tested analytical-use scope.

LLM structural proposals combined with numerical parameter calibration already appear in [G-Sim, ICML 2025](https://proceedings.mlr.press/v267/holt25b.html). That division of work is a useful implementation reference, not a novelty claim. Our candidate contribution remains translating heterogeneous published study-level evidence into generators for scientifically useful virtual data under missing individual-level information. Its novelty and general utility still need evidence.

## Continuity

The completed [ENSANUT report](../reports/autonomous_research_cycle2_2026-10-31/results_report/REPORT.md), [closeout](../reports/autonomous_research_cycle2_2026-10-31/CYCLE_CLOSEOUT.md), frozen generators and revealed reference remain unchanged. That reference is closed to tuning and fresh-confirmation claims. The existing second-cycle automation remains paused.
