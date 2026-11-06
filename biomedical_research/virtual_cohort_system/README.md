# Evidence-guided virtual biomedical data

**Current manuscript: [v0.20](manuscript/DRAFT_v0_20.md), 6 November 2026.**

**From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents**

[Reading PDF](manuscript/conference_draft_v20_2026-11-06/paper.pdf) · [Overleaf-ready ZIP](manuscript/conference_draft_v20_2026-11-06/overleaf_v20.zip) · [Method overview](manuscript/paper_figures_v20_2026-11-06/fig1-agent-method.drawio.svg)

How can a researcher analyze paired biomedical measurements when individual records are unavailable? The researcher describes the population, the variables and the intended analyses. The agent uses published summaries to choose a joint model. A numerical worker draws complete virtual records from the agent's program. A measured comparison then shows which intended analyses those records support in the selected target sample.

## Reading the paper

1. [Figure 1](manuscript/paper_figures_v20_2026-11-06/fig1-agent-method.drawio.svg) follows a research request through evidence selection and agent modeling to a table that supports several analyses.
2. [Figure 2](manuscript/paper_figures_v19_2026-11-06/fig3-iron-utility.png) follows two frozen iron-status programs. The same hemoglobin and ferritin columns supply a threshold odds ratio, a joint proportion and a rank correlation. The [results and independent check](reports/iron_breadth_2026-11-05/RESULTS.md) distinguish source replay from comparison with the target survey.
3. Figure 3 examines what additional [external relationship evidence](reports/main_study_freeze_2026-11-03/RESULTS.md) changes. Five of six glycemia coefficient discrepancies decreased and one increased. Supplement S11 follows one constructor's translation of two published projections into a joint regression.
4. Figure 4 takes the question to [glycemia and lipids](reports/evidence_use_cross_task_2026-11-05/RESULTS.md). The [earlier frozen prospective wave](../../reports/scaleup_2026-11-01/production_release/RESULTS.md) reports both prespecified stopping decisions in Figure S5.

[Manuscript history](manuscript/README.md) · [Current research focus](docs/CURRENT_RESEARCH_FOCUS.md) · [Agent implementation](cohort_harness/evidence_use_v1.py) · [Lipid pair diagnostic](manuscript/Q5_LIPID_ORDER_POST_HOC_v19.md) · [Data exposure registry](docs/DATASET_EXPOSURE_REGISTRY.md) · [Archived v0.18 review guide](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/ec07b03ea20745f731a4cd347d44808e9b803686/REVIEW_GUIDE.md).
