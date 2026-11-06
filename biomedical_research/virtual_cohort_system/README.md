# Evidence-guided virtual biomedical data

**Current manuscript: [v0.19](manuscript/DRAFT_v0_19.md), 6 November 2026.**

**From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents**

[Reading PDF](manuscript/conference_draft_v19_2026-11-06/paper.pdf) · [Overleaf-ready ZIP](manuscript/conference_draft_v19_2026-11-06/overleaf_v19.zip) · [Iron-status figure](manuscript/paper_figures_v19_2026-11-06/fig3-iron-utility.png)

Researchers may need to analyze paired biomarkers when no individual records are available. The researcher specifies the target population, eligible evidence and intended analyses. A scientific agent writes the joint sampling program and identifies the source statistic or assumption supporting each choice. A numerical worker calls the program with a row count and random seed. Table 1 follows these decisions for hemoglobin and ferritin, and Figure 3 traces their consequences through to three scientific analyses.

## Which scientific analyses can those rows support?

1. **What changes when more is known?** In [CHNS and ENSANUT](reports/main_study_freeze_2026-11-03/RESULTS.md), adding external relationship evidence reduced mean absolute discrepancy for five of six designated regression coefficients. The CHNS BMI effect became less accurate.
2. **What can be learned from one table?** In the [iron study](reports/iron_breadth_2026-11-05/RESULTS.md), two generators each matched a published source odds ratio. Both understated the NHANES target association. One came closer on the co-occurrence of low values; the other on continuous rank correlation.
3. **Does that pattern travel?** In the [glycemia and lipids study](reports/evidence_use_cross_task_2026-11-05/RESULTS.md), point directions agreed across the six analyses; adjusted lipid dependence was too weak. In the [earlier prospective wave](../../reports/scaleup_2026-11-01/production_release/RESULTS.md), neither case passed its prespecified overall rule.

The [HRS longitudinal comparison](reports/hrs_public_example_2026-11-03/RESULTS.md) and [supplied-summary experiment](reports/information_revision_ablation_2026-11-03/RESULTS.md) establish what can be reconstructed when more information is given. [Manuscript and figure guide](manuscript/README.md) · [Post hoc physical-consistency check](manuscript/Q5_LIPID_ORDER_POST_HOC_v19.md) · [Agent implementation](cohort_harness/evidence_use_v1.py) · [Fixed v0.18 review guide](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/ec07b03ea20745f731a4cd347d44808e9b803686/REVIEW_GUIDE.md).

[Current focus](docs/CURRENT_RESEARCH_FOCUS.md) · [Claim-specific experiment gaps](manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md) · [Exposure registry](docs/DATASET_EXPOSURE_REGISTRY.md). Real and simulated individual records remain local. The LaTeX package is a review draft, not a conference submission.
