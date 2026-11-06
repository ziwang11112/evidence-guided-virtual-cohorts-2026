# Evidence-guided virtual biomedical data

## From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents

The scientific agent turns published evidence and a study request into a probability model and sampling program. The host coordinates the evidence and review budget, a numerical worker generates the records, and a separate evaluator compares the requested analyses with a measured reference.

**Current edition v0.21, 6 November 2026.** [Read the paper (PDF)](manuscript/conference_draft_v21_2026-11-06/paper.pdf) · [Read the manuscript and supplement](manuscript/DRAFT_v0_21.md) · [Open the Overleaf project](manuscript/conference_draft_v21_2026-11-06/overleaf_v21.zip).

| What would you like to inspect? | Where to look |
| --- | --- |
| How does the system run? | Figure 1 maps the [system architecture](manuscript/paper_figures_v21_2026-11-06/fig1-system-architecture.drawio.svg), including the agent's artifacts, source checks, final sampling and the separate target evaluation. [Editable architecture](manuscript/paper_figures_v21_2026-11-06/fig1-system-architecture.drawio) · [Implementation references](manuscript/paper_figures_v21_2026-11-06/README.md). |
| What does a researcher receive? | Figure 2 illustrates an [iron-status request](manuscript/paper_figures_v20_2026-11-06/fig1-agent-method.drawio.svg). A synthetic participant has a row containing both hemoglobin and ferritin. Several analyses use these same pairs. |
| What do modeling choices change? | Figure 3 compares the two models' predictions and the measured estimates in the [sealed iron study](reports/iron_breadth_2026-11-05/RESULTS.md). |
| When do additional published associations help? | Figure 4 compares six adjusted regressions in the [glycemia evidence contrast](reports/main_study_freeze_2026-11-03/RESULTS.md). Supplement S11 describes the regression calculation chosen by one constructor. |
| Which results extend to other requests? | Figure 5 reports the [glycemia and lipid tests](reports/evidence_use_cross_task_2026-11-05/RESULTS.md). Figure S5 and Table S7 report the earlier prospective wave and its stopping rule. |

[Manuscript history](manuscript/README.md) · [Sampling worker](cohort_harness/execution.py) · [Declared-statistic checks](cohort_harness/semantic_feedback_v1.py) · [Current research focus](docs/CURRENT_RESEARCH_FOCUS.md) · [Lipid pair diagnostic](manuscript/Q5_LIPID_ORDER_POST_HOC_v19.md) · [Archived v0.18 review guide](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/ec07b03ea20745f731a4cd347d44808e9b803686/REVIEW_GUIDE.md) · [Dataset exposure registry](docs/DATASET_EXPOSURE_REGISTRY.md).
