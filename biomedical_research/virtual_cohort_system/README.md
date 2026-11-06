# Evidence-guided virtual biomedical data

**Current manuscript: [v0.16](manuscript/DRAFT_v0_16.md), 5 November 2026.**

**From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents**

[Reading PDF](manuscript/conference_draft_v16_2026-11-05/paper.pdf) · [Overleaf-ready ZIP](manuscript/conference_draft_v16_2026-11-05/overleaf_v16.zip) · [HRS comparison figure](manuscript/paper_figures_v16_2026-11-05/fig2-hrs-comparison.svg)

A scientific agent uses published evidence, a population description, optional observations and intended analyses to specify a joint model and generate virtual data. The main studies ask the agent to generate an entire population without individual construction records. Its model can change with the requested scientific use.

## What do the generated data support?

1. **Start with a model both methods know.** In the [HRS longitudinal comparison](reports/hrs_public_example_2026-11-03/RESULTS.md), both laws preserved the negative interaction below 6.5% HbA1c. Above that knot the agent and reconstructed published law gave opposite point signs; five of six intervals included zero. This is reconstruction from supplied model information.
2. **Then use external studies that leave parts of the model open.** In [glycemic and lipid requests](reports/evidence_use_cross_task_2026-11-05/RESULTS.md), all six requested quantities agreed in point direction with sample references across 18 tables. An adjusted glycemic effect was reproduced closely by one construction. Residual lipid correlations were systematically weaker (construction means 0.108–0.141; sample reference 0.512).
3. **Test what the relational evidence contributes.** In the [CHNS and ENSANUT information comparison](reports/main_study_freeze_2026-11-03/RESULTS.md), richer evidence reduced mean absolute discrepancy in five of six designated regressions; CHNS BMI became less accurate. The separate [supplied-summary experiment](reports/information_revision_ablation_2026-11-03/RESULTS.md) evaluates reconstruction of available target summaries.

The references are sample estimates, not known population effects. The external cases use previously exposed references and do not establish prospective transfer, individual-level measurement recovery or an overall advantage over statistical generators.

## Reading and reproducing the work

The manuscript contains four main figures and four supplementary figures. The new HRS figure uses reviewed aggregate results; no data-generation or clinical fitting step was repeated for v0.16. The [agent method](manuscript/DRAFT_v0_16.md#3-agent-controlled-evidence-to-cohort-construction), [implementation](cohort_harness/evidence_use_v1.py), [comparator rationale](docs/KDD_LLMSYNTHOR_COMPARISON_PRIORITY.md) and [draft history](manuscript/README.md) provide entry points.

[Current focus](docs/CURRENT_RESEARCH_FOCUS.md) · [Claim-specific experiment gaps](manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md) · [Exposure registry](docs/DATASET_EXPOSURE_REGISTRY.md). Real and simulated individual records remain local. The LaTeX package is a review draft, not a conference submission.
