# Evidence-guided virtual biomedical data

**Current manuscript: [v0.18](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_18.md), 6 November 2026.**

**From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents**

[Reading PDF](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v18_2026-11-06/paper.pdf) · [Overleaf-ready ZIP](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v18_2026-11-06/overleaf_v18.zip) · [Iron-status figure](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v18_2026-11-06/fig3-iron-utility.png)

Researchers may need to analyze paired biomarkers when no individual records are available. The agent qualifies the published measurements and relationships, writes a joint probability model, and identifies the assumptions under which complete records can be generated. The resulting tables can be analyzed with ordinary statistical software.

## Which scientific analyses can those rows support?

1. **What changes when more is known?** In [CHNS and ENSANUT](biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/RESULTS.md), adding external relationship evidence reduced mean absolute discrepancy for five of six designated regression coefficients. The CHNS BMI effect became less accurate.
2. **What can be learned from one table?** In the [iron study](biomedical_research/virtual_cohort_system/reports/iron_breadth_2026-11-05/RESULTS.md), two generators each matched a published source odds ratio. Both understated the NHANES target association. One came closer on the co-occurrence of low values; the other on continuous rank correlation.
3. **Does that pattern travel?** In the [glycemia and lipids study](biomedical_research/virtual_cohort_system/reports/evidence_use_cross_task_2026-11-05/RESULTS.md), point directions agreed across the six analyses; adjusted lipid dependence was too weak. In the [earlier prospective wave](reports/scaleup_2026-11-01/production_release/RESULTS.md), neither case passed its prespecified overall rule.

The [HRS longitudinal comparison](biomedical_research/virtual_cohort_system/reports/hrs_public_example_2026-11-03/RESULTS.md) and [supplied-summary experiment](biomedical_research/virtual_cohort_system/reports/information_revision_ablation_2026-11-03/RESULTS.md) establish what can be reconstructed when more information is given. [Manuscript and figure guide](biomedical_research/virtual_cohort_system/manuscript/README.md) · [Agent implementation](biomedical_research/virtual_cohort_system/cohort_harness/evidence_use_v1.py).

[Current focus](biomedical_research/virtual_cohort_system/docs/CURRENT_RESEARCH_FOCUS.md) · [Claim-specific experiment gaps](biomedical_research/virtual_cohort_system/manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md) · [Exposure registry](biomedical_research/virtual_cohort_system/docs/DATASET_EXPOSURE_REGISTRY.md). Real and simulated individual records remain local. The LaTeX package is a review draft, not a conference submission.
