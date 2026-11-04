# Evidence-guided virtual biomedical data

**New visual edition:** [Figure gallery](biomedical_research/virtual_cohort_system/manuscript/visual_redesign_v11_2026-11-04/index.html), [reading PDF](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v11_2026-11-04/paper.pdf), [Overleaf bundle](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v11_2026-11-04/overleaf_v11.zip). An expanded Agent framework and integrated result displays, with the same scientific results.

**Current manuscript: [v0.11](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_11.md), 4 November 2026.**

A scientific Agent turns published evidence, a target-population description, optional observations and an intended analysis into useful virtual biomedical data. Complete-cohort generation without participant inputs is central. The Agent chooses scientific structure and parameters; numerical tools sample and inspect the model.

## Paper and results

- [Reading PDF](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v10_2026-11-04/paper.pdf), [Overleaf bundle](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v10_2026-11-04/overleaf_v10.zip), and [v0.10 story/visual design](biomedical_research/virtual_cohort_system/reports/conference_draft_v10_2026-11-04/STORY_AND_VISUAL_DESIGN.md).
- [Independent v0.10 review](biomedical_research/virtual_cohort_system/reports/conference_draft_v10_2026-11-04/INDEPENDENT_DRAFT_REVIEW.md): all main numerical values retained; original compact figures, four evaluation questions.

- [Full manuscript](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_10.md).
- [Current consolidation and rerun decision](biomedical_research/virtual_cohort_system/reports/manuscript_consolidation_2026-11-04/CONSOLIDATION_DECISION.md).
- [Method/version audit](biomedical_research/virtual_cohort_system/reports/manuscript_consolidation_2026-11-04/METHOD_AND_RERUN_AUDIT.md) and [contribution/figure audit](biomedical_research/virtual_cohort_system/reports/manuscript_consolidation_2026-11-04/SUPPORT_AND_FIGURE_AUDIT.md).
- [Figures 1–4 and S1](biomedical_research/virtual_cohort_system/manuscript/integrated_figures_v07_2026-11-03/FIGURE_PLAN.md), [new Figure 5](biomedical_research/virtual_cohort_system/manuscript/integrated_figures_v09_2026-11-04/figure5_agent_scientific_utility.svg), and [real-sample context supplement](biomedical_research/virtual_cohort_system/manuscript/integrated_figures_v09_2026-11-04/supplement_real_real_context.svg).
- [Independent manuscript and figure review](biomedical_research/virtual_cohort_system/reports/manuscript_consolidation_2026-11-04/REVIEW_v09.md).
- [Method and implementation](biomedical_research/virtual_cohort_system/README.md).

The principal experimental settings have distinct information conditions:

1. **External-evidence development:** CHNS and ENSANUT, 20 Agent plus four statistical constructions, 72 final tables. Added relational evidence lowered five of six focal constructor-averaged mean absolute discrepancies; CHNS BMI discrepancy increased.
2. **Target-summary reconstruction:** six Agent constructions in a separate CHNS experiment. Accessible summaries supported closer reconstruction. Additional review produced retention, with no demonstrated revision gain.
3. **Published-model reconstruction:** one Agent and one reconstructed published-law model produced six valid longitudinal tables, each with 11,509 virtual subjects at four visits. Both HbA1c interactions, all 16 mixed-model effects and distributional mismatches are retained. No HRS participant records were used.
4. **Open-search construction:** a search without bibliographic seeds assembled five seriously reviewed original studies. One fresh constructor chose a joint law and delivered three complete 3,000-person tables. Figure 5 shows every non-intercept regression term and a missing-dependence sensitivity; age/sex-adjusted BMI and age analyses had useful agreement, with other conditional and distributional differences remaining.

An additional 100 community-disjoint resplits of the existing CHNS reference contextualize the latest model's discrepancies. All 36 metrics remain available. These are within-sample descriptive comparisons, not new cohorts or equivalence thresholds.

The shared scientific procedure has separately frozen experimental implementations and inputs. Historical enrichment and earlier adverse results remain in the record; six real reference families do not mean six current-version autonomous validations. Actual retrieval and generation are demonstrated in host-dispatched workflows. Arbitrary-query validity, standalone autonomy and replacement of clinical measurement are not claimed.

## Reproduction and access

The existing aggregate reproduction entry point remains unchanged:

```powershell
python biomedical_research/virtual_cohort_system/reproducibility/reproduce_manuscript.py --repo-root . --output ../v07-reproduced
```

It verifies pinned aggregate inputs, reconstructs the original numerical tables, redraws Figures 2–4/S1 and copies Figure 1 as a schematic. See [prerequisites and exact scope](biomedical_research/virtual_cohort_system/docs/REPRODUCING_MANUSCRIPT_v07.md). The [new figure instructions](biomedical_research/virtual_cohort_system/manuscript/integrated_figures_v09_2026-11-04/FIGURE5_CAPTIONS.md) cover the additional aggregate-only renderer. Neither pathway runs an LLM, generates participant-like records or refits clinical data.

This is a reviewed research export. Patient-level real/generated tables, third-party original papers/codebooks and credentials remain local. Clinical reruns require lawful dataset access and the corresponding environment.

## Current status

The manuscript and five main figures are available for scientific review. The audit found no common unresolved error requiring all historical datasets to be regenerated. A future unified cross-case open-retrieval study is conditional on that stronger claim, not a prerequisite for the current paper.

Final article-length editing, authorship/funding/conflict/access/ethics/AI declarations and publication-layout checks remain. No journal is settled and no submission has occurred. See the [current focus](biomedical_research/virtual_cohort_system/docs/CURRENT_RESEARCH_FOCUS.md) and [exposure registry](biomedical_research/virtual_cohort_system/docs/DATASET_EXPOSURE_REGISTRY.md).
