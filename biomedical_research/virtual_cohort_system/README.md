# Evidence-guided virtual biomedical data

**Scientific-use development, 9 November 2026.** An Agent evaluated a baseline and an optional component-coherence repair using execution-bound feedback. The [complete before/after report](reports/analysis_use_rubric_v2_2026-11-09/RESULTS.md) retains all scientific analyses, source gaps, setup failures and independent audits. This is a controlled development check, not new clinical validation or an overall quality claim.

## From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents

The scientific agent turns published evidence and a study request into a probability model and sampling program. The host coordinates the evidence and review budget, a numerical worker generates the records, and a separate evaluator compares the requested analyses with a measured reference.

**Executed adaptive loop, 9 November 2026.** The new [controller](docs/ADAPTIVE_SESSION_V1.md) dispatches Agent-selected retrieval, construction, isolated execution, checks and revision. In one [existing-case run](reports/adaptive_case_loop_2026-11-09/RESULTS.md), a fresh Agent completed 28 actions and six generated tables across a primary and a dependence-sensitivity model. All requested analyses were computed and independently reproduced. The author retained its primary model before reference evaluation; source-transfer uncertainty remains, and this run does not demonstrate an overall quality gain from revision. Full-text sources and individual tables stay local.

**Expanded methods draft v0.25, 8 November 2026.** [Read the paper (PDF)](manuscript/methods_draft_v25_2026-11-08/paper.pdf) · [Read the manuscript and supplement](manuscript/DRAFT_v0_25.md) · [Open the Overleaf project](manuscript/methods_draft_v25_2026-11-08/overleaf_v25.zip).

This revision completes the statistical comparator results, makes dispersion and complete-case limitations explicit, and adds verified related work. A separate [controlled diagnostic](reports/review_revision_2026-11-08/controlled_joint_moments/RESULTS.md) found that ordinary agents already recovered the joint law from compatible summaries; an additional consistency instruction showed no gain. Its twelve artificial deliveries are six unique tables, not new biomedical cohorts.

**Existing-case diagnosis, 8 November.** The [scientific-use report](reports/analysis_use_diagnosis_2026-11-08/READOUT.md) and [24-analysis map](reports/analysis_use_diagnosis_2026-11-08/USE_MAP.csv) distinguish usable reconstructions and partial external agreement from unvalidated uses. Independent mathematical checks separate historical software defects from current evidence and modeling gaps. Using all eight available age profiles does not provide a simple dispersion repair. This unit generated no new clinical tables; it guides specific evidence needs rather than retuning disclosed targets.

| What would you like to inspect? | Where to look |
| --- | --- |
| How does the system run? | Figure 1 maps the [agent action and feedback loop](manuscript/paper_figures_v24_2026-11-06/fig1-agent-loop.drawio.svg), showing the author, executable program, source checks, retain-or-revise choice and sealed tables. The Methods follow an actual source-only revision and a retained law. [Editable architecture](manuscript/paper_figures_v24_2026-11-06/fig1-agent-loop.drawio) · [Implementation references](manuscript/paper_figures_v24_2026-11-06/README.md). |
| What does a researcher receive? | Figure 2 illustrates an [iron-status request](manuscript/paper_figures_v20_2026-11-06/fig1-agent-method.drawio.svg). A synthetic participant has a row containing both hemoglobin and ferritin. Several analyses use these same pairs. |
| What do modeling choices change? | Figure 3 compares the two models' predictions and the measured estimates in the [sealed iron study](reports/iron_breadth_2026-11-05/RESULTS.md). |
| When do additional published associations help? | Figure 4 compares six adjusted regressions in the [glycemia evidence contrast](reports/main_study_freeze_2026-11-03/RESULTS.md). Supplement S11 describes the regression calculation chosen by one constructor. |
| Which results extend to other requests? | Figure 5 reports the [glycemia and lipid tests](reports/evidence_use_cross_task_2026-11-05/RESULTS.md). Figure S5 and Table S7 report the earlier prospective wave and its stopping rule. |

[Manuscript history](manuscript/README.md) · [Sampling worker](cohort_harness/execution.py) · [Declared-statistic checks](cohort_harness/semantic_feedback_v1.py) · [Current research focus](docs/CURRENT_RESEARCH_FOCUS.md) · [Lipid pair diagnostic](manuscript/Q5_LIPID_ORDER_POST_HOC_v19.md) · [Archived v0.18 review guide](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/ec07b03ea20745f731a4cd347d44808e9b803686/REVIEW_GUIDE.md) · [Dataset exposure registry](docs/DATASET_EXPOSURE_REGISTRY.md).
