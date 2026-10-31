# C3: source-constrained whole-cohort generation

Completed scientific execution, 31 October 2026. This is a bounded source-only development experiment. It does not reopen ENSANUT or any previously revealed clinical target. The overall research remains evidence-guided virtual data for scientific analysis, including whole-cohort generation with no individual input.

## What was built and tested

A fresh scientific Agent received the admitted literature evidence and source-population descriptions, without target records, target effects or previous candidate answers. It authored two complete stochastic generators, their scientific assumptions, five adjustable scalar parameters, parameter ranges, discrepancy scales and acceptance criteria before any C3 generation. The two candidates were frozen and independently reviewed.

The models generate age, sex, BMI, fasting glucose and HbA1c together. Both use the same source evidence, source covariate distributions and independence assumptions. Their difference is the age-response structure: an additive linear age effect versus a prespecified sensitivity structure with a smaller age increment after 60. The latter is an assumption motivated by the published marginal profile; it is not an established conditional biological mechanism.

The Agent authored the scientific model. A deterministic bounded optimizer subsequently fitted its declared parameters, and the frozen Python generator produced the rows inside the existing isolated executor. This unit did **not** test direct row-by-row LLM output, a new Agent revision loop, or superiority to an ordinary Agent. The source-only calibration adapter extends existing project calibration to complete-cohort source replay; calibration itself is not a new methodological contribution.

Two source contexts replayed all 20 specified published statistics: distributions, age-stratum means and the exact reported regression projections. Each generated source table has 6,000 fictional observations. Separate source anchors retain their correct meanings: the Lifelines overall HbA1c mean and the Pani 55–59 mean are different statistical objects. Unknown target-population location is not filled from a previously seen target.

## Fixed protocol and actual execution

- Each structure had a maximum of 40 parameter trials. Both stopped after 37 at the prespecified minimum step, selecting trial 26 on fitting seed 19101.
- Baseline and selected parameters were then replayed on unused seeds 19111 and 19123. These seeds were not used for parameter selection or subsequent modification.
- Total: 74 scalar trials, 164 isolated source-table executions, zero infeasible trials and zero failed executions. Sixteen of those tables are the baseline/selected unused-seed outputs; the remaining tables belong to fitting. They are simulation draws, not independent clinical cohorts.
- No target download, clinical evaluation, additional source search, model training, HPC job, paid API or new scheduler was started.
- The adapter passed 22 focused tests. An independent audit recomputed all 20 source statistics for baseline and selected models at the three fixed seeds: 240 statistic entries from 24 already-existing tables. It used independent mean, sample-SD, proportion and OLS code, not the production statistic engine.
- Exact paired IDs and all age/sex/BMI/glucose values were unchanged by calibration. The changes are confined to the declared HbA1c-law parameters.

Each source-generation/replay session recorded about 192 seconds before final integrity verification. Timeout reservations are not CPU time or monetary cost; peak memory, CPU consumption and total human/Agent work were not measured.

## Results

Lower values below mean a lower prespecified weighted mean squared source discrepancy. These numbers are not clinical accuracy, a likelihood or uncertainty coverage.

| Structure | Fitting seed: initial → fitted | Unused seed 19111 | Unused seed 19123 |
|---|---:|---:|---:|
| Linear | 0.670013 → 0.370687 | 0.669428 → 0.360010 | 0.699142 → 0.414309 |
| Alternative age structure | 0.230385 → 0.215629 | 0.173461 → 0.205038 | 0.236617 → 0.259953 |

**Linear: reproducible loss reduction, incomplete source compatibility.** Its aggregate improvement persists on both unused seeds. However, the ≥70 HbA1c mean remains 0.10661 and 0.10675 percentage points above the reported source value, outside the prespecified ±0.10 engineering interval. One unused-seed age slope is 0.00799098, narrowly below the 0.008 lower limit. That near-boundary failure is reported literally; it is not evidence of a clinically meaningful discontinuity or a major biological error.

**Alternative: fitting did not yield a robust improvement.** Loss decreased on the fitting seed but increased on both unused seeds. Its initial version passed all 20 numerical source criteria on both unused seeds. The fitted version failed the age-slope criterion on both: 0.007390 and 0.007265 versus the admitted source estimate 0.010 and the authored interval [0.008, 0.012]. Its worst age-stratum mean discrepancy improved from about 0.0645–0.0648 to 0.0516–0.0522. This is a concrete tradeoff: better profile matching can accompany a worse projected association.

Both structures, initial versions, selected versions and every failure remain reported. The alternative does not satisfy the complete prespecified structural-preference rule because it introduces an additional failed age-slope requirement. No structure is promoted to a new target on the basis of this replay.

## What this changes in the research plan

The mechanism works operationally: an Agent-defined complete-cohort generator can be frozen, fitted against study-specific statistical operators, and independently audited without individual source or target data. But the tested objective can prefer a parameter change that damages an analysis the virtual data should support. A single aggregate score is therefore insufficient evidence that generated data became more scientifically useful.

This result supports a next **design** question: how should a generator revision be accepted when the intended scientific analyses disagree about its quality? A bounded future comparison could preregister analysis-specific compatibility requirements and evaluate an acceptance rule alongside aggregate-loss selection, with multiple fitting draws and untouched evaluation draws. The acceptance criteria must come from the intended use and the source uncertainty; they must not be chosen to rescue the failed C3 model. Multiple fitting seeds and different acceptance rules are untested proposals, not demonstrated fixes. C3 outputs are now exposed development material.

Before claiming reusable scientific analysis or target-population validity, a separate fresh case must establish appropriate source-to-target mapping and evaluate both source-constrained and unprovided analyses. Source-fit success alone is insufficient. A future target's baseline location, covariate dependence and transport assumptions still need defensible inputs; they cannot be recovered by borrowing an old target's revealed outcomes.

This unit is closed without further fitting. Existing models and all historical clinical targets remain frozen. No new target, additional structure or alternative scheduler is automatically started.

## Limits that remain visible

The source statistics are estimates, not known population truths. Discrepancy scales and numeric limits were declared engineering conventions rather than clinical equivalence margins or calibrated confidence intervals. Pani age means and Jansen separately adjusted regressions do not identify the full joint distribution. Covariate independence, finite age supports, the residual distribution, survey representation, assay comparability and cross-study transport remain assumptions. Pani/Liu overlap is not independent replication. Neither whole-population validity nor individual measurement recovery follows from generating more rows.

## Inspectable artifacts

- [Frozen protocol](../reports/c3s/PROTOCOL.md), [preexecution adjudication](../reports/c3s/PREEXECUTION_ADJUDICATION.md) and [independent preexecution review](../reports/c3s/review/PREEXECUTION_REVIEW.md).
- [Independent result report](../reports/c3s/analysis/audit_v1/REPORT.md), [all 20 checks across the inspected outputs](../reports/c3s/analysis/audit_v1/all20_checks.csv) and [all numerical failures](../reports/c3s/analysis/audit_v1/all_numeric_criterion_failures.csv).
- [Loss and replay figure](../reports/c3s/analysis/audit_v1/loss_and_trajectory.png) and [per-check figure](../reports/c3s/analysis/audit_v1/all_twenty_checks.png).
- [Agent-authored initial models and criteria](../reports/c3s/linear/candidates/initial/decision.md), [alternative model](../reports/c3s/alternative/candidates/initial/decision.md), and [adapter documentation](../reports/c3s/method/README.md).

The curated private repository contains code, evidence summaries, commitments and aggregate analyses. All fictional individual-row tables remain local. Repository copies use `reports/c3s/` rather than `work/c3s/`; the export mapping and exclusions are explicit.
