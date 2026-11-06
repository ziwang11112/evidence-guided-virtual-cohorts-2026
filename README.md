# Evidence-guided virtual biomedical data

**Current manuscript: [v0.17](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_17.md), 5 November 2026.**

**From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents**

[Reading PDF](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v17_2026-11-05/paper.pdf) · [Overleaf-ready ZIP](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v17_2026-11-05/overleaf_v17.zip) · [HRS comparison figure](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v16_2026-11-05/fig2-hrs-comparison.svg)

A scientific agent uses published evidence, a population description, optional observations and intended analyses to specify a joint model and generate virtual data. The main studies ask the agent to generate an entire population without individual construction records. Its model can change with the requested scientific use.

## What do the generated data support?

1. **Start with a model both methods know.** In the [HRS longitudinal comparison](biomedical_research/virtual_cohort_system/reports/hrs_public_example_2026-11-03/RESULTS.md), both laws preserved the negative interaction below 6.5% HbA1c. Above that knot the agent and reconstructed published law gave opposite point signs; five of six intervals included zero. This is reconstruction from supplied model information.
2. **Then use external studies that leave parts of the model open.** In [glycemic and lipid requests](biomedical_research/virtual_cohort_system/reports/evidence_use_cross_task_2026-11-05/RESULTS.md), all six requested quantities agreed in point direction with sample references across 18 tables. An adjusted glycemic effect was reproduced closely by one construction. Residual lipid correlations were systematically weaker (construction means 0.108–0.141; sample reference 0.512).
3. **Test what the relational evidence contributes.** In the [CHNS and ENSANUT information comparison](biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/RESULTS.md), richer evidence reduced mean absolute discrepancy in five of six designated regressions; CHNS BMI became less accurate. The separate [supplied-summary experiment](biomedical_research/virtual_cohort_system/reports/information_revision_ablation_2026-11-03/RESULTS.md) evaluates reconstruction of available target summaries.

4. **Examine a prediction fixed before disclosure.** In the earlier [prospective evaluation](reports/scaleup_2026-11-01/production_release/RESULTS.md), all 15 HAALSI agent draws reproduced the positive glucose associations with BMI and age, and eight recovered the sex difference in BMI slopes. Three of five constructions met the primary criterion, below the four required. All three zero-effect predictions also fell inside the margin. The later Turkana request reused the same measured sample.

## Reading and reproducing the work

The manuscript contains four main figures and five supplementary figures. [Figure S5](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v17_2026-11-05/figS5-prospective-wave.svg) and Table S7 include the six prospectively fixed analyses. The [admission review](biomedical_research/virtual_cohort_system/reports/manuscript_v17_2026-11-05/FRESH_TARGET_REVIEW.md) records which targets were withheld at the time of each experiment. The [agent method](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_17.md#3-agent-controlled-evidence-to-cohort-construction), [implementation](biomedical_research/virtual_cohort_system/cohort_harness/evidence_use_v1.py), [comparator rationale](biomedical_research/virtual_cohort_system/docs/KDD_LLMSYNTHOR_COMPARISON_PRIORITY.md) and [draft history](biomedical_research/virtual_cohort_system/manuscript/README.md) provide entry points.

[Current focus](biomedical_research/virtual_cohort_system/docs/CURRENT_RESEARCH_FOCUS.md) · [Claim-specific experiment gaps](biomedical_research/virtual_cohort_system/manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md) · [Exposure registry](biomedical_research/virtual_cohort_system/docs/DATASET_EXPOSURE_REGISTRY.md). Real and simulated individual records remain local. The LaTeX package is a review draft, not a conference submission.
