# Evidence-guided virtual biomedical data

**Current manuscript: [v0.8](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_8.md).**

A scientific Agent turns published evidence, a target-population description, optional observations and an intended analysis into useful virtual biomedical data. Complete-cohort generation without individual records is central. The Agent selects scientific structure and parameters; numerical tools sample and inspect the model.

## Paper and results

- [Full manuscript](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_8.md).
- [Story and contributions](biomedical_research/virtual_cohort_system/manuscript/STORY_AND_CONTRIBUTIONS_v07_2026-11-03.md).
- [Figures and captions](biomedical_research/virtual_cohort_system/manuscript/integrated_figures_v07_2026-11-03/FIGURE_PLAN.md).
- [Integrated evidence ledger](biomedical_research/virtual_cohort_system/manuscript/INTEGRATED_EVIDENCE_LEDGER_v07_2026-11-03.md), including failed studies.
- [Method and implementation](biomedical_research/virtual_cohort_system/README.md).

The paper separates three completed settings:

1. **External-evidence development:** CHNS and ENSANUT, 20 Agent plus four statistical constructions, 72 final tables. Added relational evidence lowered five of six focal discrepancies; CHNS BMI worsened.
2. **Target-summary reconstruction:** six Agent constructions in a separate CHNS experiment. Accessible summaries supported closer reconstruction; no additional-stage revision gain was observed.
3. **Published-model reconstruction:** an HRS longitudinal example, one Agent and one reconstructed published-law model, six valid tables. All 16 mixed-model effects and 27 baseline diagnostics are retained, including weak-effect and upper-tail mismatches. No HRS participant records were used.

These are distinct information conditions, not three unseen clinical confirmations or a universal superiority claim. The main-study inputs are curated. Autonomous literature processing, arbitrary-query validity and replacement of clinical measurement are not established.

The [v0.8 review](biomedical_research/virtual_cohort_system/manuscript/REVIEW_v0_8_2026-11-03.md) checks the revised framing and unchanged numerical foundation. The [current Agent-system contribution plan](biomedical_research/virtual_cohort_system/docs/AGENT_SYSTEM_CONTRIBUTION_AND_EVALUATION_2026-11-03.md) prioritizes the complete research-request-to-data workflow. Its [first implemented entry](biomedical_research/virtual_cohort_system/docs/REQUEST_INTAKE_V1.md) prepares task/author packets; two metadata-only demonstrations and 19 new interface tests passed. The library entry does not launch a model. The subsequent [live integration](biomedical_research/virtual_cohort_system/reports/agent_system_live_2026-11-03/RESULTS.md) actually dispatched two scientific Agents, retrieved originals, executed eight tables and delivered six. A age and B glucose relationships agreed descriptively; B glucose-adjusted BMI did not. All source replays were unavailable and both authors retained their initial models. This is an exposed-reference development result. The [earlier acquisition proposal](biomedical_research/virtual_cohort_system/manuscript/TOP_VENUE_RESEARCH_DECISION_2026-11-03.md) remains optional, not a publication prerequisite. Earlier [PLOS/JBI preparation](biomedical_research/virtual_cohort_system/manuscript/VENUE_AND_SUBMISSION_PLAN_v08_2026-11-03.md) remains a fallback; no venue is settled and no submission has occurred.

## Reproduce the aggregate manuscript results

Run from the repository root with an output directory outside the checkout:

```powershell
python biomedical_research/virtual_cohort_system/reproducibility/reproduce_manuscript.py --repo-root . --output ../v07-reproduced
```

The v0.7 input lock remains unchanged; v0.8 retains its numerical tables and figure assets. See [prerequisites and exact scope](biomedical_research/virtual_cohort_system/docs/REPRODUCING_MANUSCRIPT_v07.md). This reconstructs numerical tables and redraws Figures 2-4/S1 from pinned public aggregate inputs; Figure 1 is copied as a schematic. It does not call an LLM, generate participant-like records, fit clinical data or automatically install dependencies. A standard-library-only verification mode is documented separately.

This is a reviewed research export, not a full workspace backup. Participant-level real/generated tables, third-party originals and credentials are excluded. Clinical reruns require dataset permissions and the relevant execution environment.

## Current status

The [experiment-gap review](biomedical_research/virtual_cohort_system/manuscript/KEY_EXPERIMENT_GAPS_v07_2026-11-03.md) identifies only claim-linked optional extensions. The [metadata-only feasibility audit](biomedical_research/virtual_cohort_system/manuscript/EXISTING_REFERENCE_FEASIBILITY_v07_2026-11-03.md) admits no new independent reference and starts no experiment.

Author declarations, article-type selection and publication-layout inspection remain. A supported bounded claim and reproducible draft do not guarantee publication in a particular venue.

Older status updates remain in [repository history](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/bec2041d1816432dd744cf875c649e9ea6142e67/README.md). Consult the [current focus](biomedical_research/virtual_cohort_system/docs/CURRENT_RESEARCH_FOCUS.md) and [exposure registry](biomedical_research/virtual_cohort_system/docs/DATASET_EXPOSURE_REGISTRY.md) for current interpretation.
