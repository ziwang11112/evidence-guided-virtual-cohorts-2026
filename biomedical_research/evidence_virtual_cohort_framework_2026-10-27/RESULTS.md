# Expanded development replay and paper-design decision

27 October 2026. **The expanded completion results preserve the reference evidence state for all 18 affected case-by-analysis comparisons. Missing-only also preserves all 18; MICE–PMM preserves 17.** This supports a limited conclusion-preservation use case, not a demonstrated Agent advantage. Whole-cohort generation remains less consistent on unprovided relationships. The method-paper direction is retained, with separate synthesis/completion tracks and independent-case validation required.

## Executed scope

The successful, immutable run is [development_batch/attempt_02](development_batch/attempt_02/README.md). It used the unchanged published-analysis replay functions and existing frozen data:

| Input type | Number of tables | Meaning |
|---|---:|---|
| Original observed reference | 1 | One 75-person, five-visit cohort, with native missingness |
| Artificially masked reference | 3 | Three overlapping masks of the same people |
| Agent completions | 60 | Twenty imputations per mask |
| MICE–PMM completions | 60 | Twenty imputations per mask |
| Whole synthetic cohorts | 20 | Twenty samples from one previously constructed final program |
| **Total** | **144** | **Not 144 independent studies or Agent constructions** |

Each input has 35 outputs: six baseline correlations, 25 time contrasts and four separately labelled proxy associations. The full batch produced **5,040 analysis rows**, with **zero analysis failures and zero pooling failures**, in approximately **117 seconds** on the current local Python runtime. This timing is analysis execution only; it excludes earlier generation and does not measure model-call cost.

In completion, 29 outputs per table use entirely unchanged data. They are preservation controls, not generative successes. Only five PFS time contrasts and the PFS–weight proxy are affected. Thus 3,480 of the 4,200 completion rows are controls; 720 are affected. Twenty draws are combined within each method/mask/affected estimand, yielding 36 pooled records. Whole-cohort samples are not Rubin-pooled and are never concatenated into a larger clinical cohort.

## Completion: conclusion preservation versus numerical recovery

The descriptive evidence-state rule is positive when an interval is above zero, negative when below zero, and uncertain when it includes zero. This is a coarse reporting rule, not an equivalence test or a complete definition of biological truth. The expanded analysis family was selected retrospectively and contains strongly correlated contrasts.

| Method | Evidence-state agreement with observed reference | Smaller effect discrepancy than missing-only |
|---|---:|---:|
| Missing-only | 18/18 | Reference comparison |
| Agent completion | 18/18 | 6/18 |
| MICE–PMM completion | 17/18 | 4/18 |

Agent has smaller absolute effect discrepancies than this MICE reference in 16/18 cells. The two implementations differ in covariate sets and model specification; this is not an isolated causal effect of having an Agent.

The one MICE evidence-state disagreement is the month-12 versus month-3 PFS change in random mask A: the original interval is unresolved, while the imputed analysis has an interval below zero. This is a source-reference discrepancy, not proof of a population false positive.

The original selected findings remain preserved: higher PFS is associated with greater body weight, and PFS decreases from baseline to month 3. The numerical recovery result from the previous report also remains: the PFS-weight coefficient is farther from its observed-data value after either completion method than after missing-only in all three masks. Preserved interpretation and imperfect coefficient recovery can coexist.

## Whole-cohort synthesis: incomplete analytical preservation

The twenty cohorts here were generated previously from target-derived marginal summaries. No new generator or Agent proposal was created in this batch. Source-constrained trajectories and unprovided relationships are reported separately.

Examples from the complete retained family:

| Analysis | Reference comparison across 20 cohorts | Interpretation |
|---|---|---|
| Baseline DD100–DD1000 correlation | Mean absolute r error 0.078; evidence state agrees 20/20 | The related-measure association was reasonably retained in this development example |
| Baseline PFS–DD100 correlation | Mean absolute r error 0.271; evidence state agrees 0/20 | The omitted cross-domain relation was not preserved; the real significance boundary is fragile and is not the sole evidence of discrepancy |
| Go/No-Go baseline-to-month-3 change | Evidence state agrees 5/20 | Uncertainty in paired/longitudinal changes matters even when visit means are constrained |
| PFS-weight exploratory proxy | Evidence state agrees 16/20 | Some analytical utility, with failures retained; not exact original-model replication |

The original PFS–DD100 raw-data p value is approximately .0485, while the article omitted its significance star; prior source audits retained this discrepancy. Therefore the 0/20 classification count should not be treated as a robust binary truth. The sizeable correlation discrepancy and all intervals/estimates remain available for assessment. Likewise 20/20 agreement on supplied mean trends is not an independent discovery.

The practical implication is specific: full synthetic generation must be tested on a complete reserved family, including cross-variable and temporal dependence. The success of mostly observed-data completion cannot substitute for that evaluation.

## Implementation review and retained failure

The first wrapper used pandas' default CSV parser. Existing completion files were serialized with 17 significant digits; default parsing created tiny numerical differences in cells that were unchanged in binary64 under round-trip parsing. Exact preservation checks therefore rejected six completion inputs in the smoke run, leaving 210 failed outputs out of 385. No full run of that version was performed. Its code, freeze and smoke are retained, with the explanation in [STATUS.md](development_batch/STATUS.md).

Attempt 02 uses `float_precision="round_trip"` consistently. It freshly computes all reference and whole-synthetic analyses instead of reusing results obtained with a different parser. Unchanged completion controls are copied only after exact input equality and target-only preservation checks. No original participant values or generator files were repaired or altered.

Seven implementation tests pass. An independent source audit reran all 35 analyses for one Agent and one MICE completion and found exactly matching estimates, SEs, intervals, p values and analysis counts. The source freezes, new implementation freeze and output hashes were verified after execution. A separate final review passed all 44 checks, verified all 5,040 rows and 36 independently reconstructed Rubin calculations, confirmed the stated comparisons, and directly reran one reference contrast. It is recorded in [independent_review](independent_review/VERIFICATION.md). These checks establish consistency of this execution, not clinical or population validity.

## What is ready and what is not

Ready: [method and experiment plan](METHODS_AND_EXPERIMENT_PLAN.md), [paired Agent strategy specification](AGENT_STRATEGIES.md), [manuscript scaffold](MANUSCRIPT_SKELETON.md), broad development evaluator and retained outputs.

Not yet run: the proposed multiple-structure policy, the three-case paired-policy experiment, new confirmation cohorts, autonomous evidence-acquisition comparison, or the research-design utility task. This batch broadens analysis coverage on old outputs; it is not that prospective large experiment.

The next implementation is the common policy/scenario interface and audited case adapters, followed by nine fresh initial lineages across three development studies, two paired policy branches and twenty final cohorts per branch: 360 Agent-generated cohorts plus 60 statistical-reference cohorts. Proceed only after the shared interface and evidence/analysis ledgers are fixed. Two additional candidate study designs have public data routes, but their analysis adapters and prior-exposure audits must be completed before they can serve as confirmation.

Do not promise patient-recruitment savings from these results. The intended near-term benefit is useful research preparation and transparent exploration, measured by reserved-analysis behavior and a concrete planning task. This is a credible method-paper objective with substantial prior art, not yet an established new method advantage or a journal-level result.

Full outputs: [all 5,040 analysis rows](development_batch/attempt_02/results/all_results.csv), [36 affected pooled comparisons](development_batch/attempt_02/results/completion_pooled.csv), [whole-synthetic summaries](development_batch/attempt_02/results/full_synthetic_summary.csv), [execution summary](development_batch/attempt_02/results/summary.json).
