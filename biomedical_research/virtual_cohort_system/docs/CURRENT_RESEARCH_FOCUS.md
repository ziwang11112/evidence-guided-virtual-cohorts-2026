# Current focus — from published evidence to analyzable biomedical cohorts

Updated 6 November 2026. [Manuscript v0.20](../manuscript/DRAFT_v0_20.md) · [Reading PDF](../manuscript/conference_draft_v20_2026-11-06/paper.pdf) · [LaTeX ZIP](../manuscript/conference_draft_v20_2026-11-06/overleaf_v20.zip).

The [method overview](../manuscript/paper_figures_v20_2026-11-06/fig1-agent-method.drawio.svg) follows a researcher who needs paired measurements through the published evidence, the agent's modeling decisions and the virtual table delivered to the researcher. Researchers can run multiple prespecified analyses on that table and compare them with measurements available under a separate evaluation protocol.

Figure 2 starts with [iron status](../reports/iron_breadth_2026-11-05/RESULTS.md). Source constraints and agent assumptions produce two different target laws. Three analyses of the same continuous columns show where their predictions diverge. Figure 3 evaluates how [additional evidence](../reports/main_study_freeze_2026-11-03/RESULTS.md) changes target regression estimates. The [cross-task results](../reports/evidence_use_cross_task_2026-11-05/RESULTS.md) distinguish agreement in sign from agreement in conditional dependence. Supplement S11 explains the case-specific derivation behind a glycemia generator.

## Prospective evidence

The earlier HAALSI evaluation froze the target analyses before disclosure. Across five agent constructions and three draws per construction, both glucose main effects agreed with the sample in point direction, while eight of 15 draws agreed on the interaction. Three of five constructions passed the primary criterion. Four were required, and the margin also admitted three zero effects. In Turkana, none of five passed. The existing [frozen record](../../../reports/scaleup_2026-11-01/production_release/RESULTS.md) supports this limited conclusion for the earlier workflow. The November 5 interface reused the same Turkana measurements.

## Decision and next step

The [KDD comparison decision](KDD_LLMSYNTHOR_COMPARISON_PRIORITY.md) separates a scientific biomedical comparator from methodological neighbors G-Sim and LLMSynthor. The [optional adaptation protocol](../reports/kdd_neighbor_design_2026-11-05/PROTOCOL.md) is not scheduled. A published model refit or another published paper's headline score is not evidence of transport to a new cohort.

Review the completed prospective and developmental results separately. A claim that the later evidence-use interface transports to a new population requires an independently admitted target selected before outcome disclosure. The [local admission review](../reports/manuscript_v17_2026-11-05/FRESH_TARGET_REVIEW.md) found zero such cases ready for evaluation. The earlier stop decision stands. [Exposure registry](DATASET_EXPOSURE_REGISTRY.md) · [Claim-specific gaps](../manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md).
