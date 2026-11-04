# Evidence-guided virtual biomedical data

**Latest completed experiment:** [Open-evidence workflow replication](biomedical_research/virtual_cohort_system/reports/core_workflow_replication_2026-11-04/RESULTS.md), 4 November 2026. Four fresh scientific authors selected their own external studies and constructed whole cohorts for two existing population requests. Twelve final tables (36,000 virtual rows) supported all six prespecified association directions; effect magnitudes, rank structure and dispersion remained mixed. All 366 numerical endpoints passed independent recalculation. All authors retained their initial model; no revision gain is claimed. This is developmental replication on exposed references, not fresh clinical validation. [Result figure](biomedical_research/virtual_cohort_system/reports/core_workflow_replication_2026-11-04/display/primary_analyses.png) · [Public release scope](biomedical_research/virtual_cohort_system/reports/core_workflow_replication_2026-11-04/PUBLIC_SCOPE.md). This new experiment awaits a separate manuscript integration; the v0.12 paper below is unchanged.

**Current manuscript: [v0.12](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_12.md), 4 November 2026.**

[Reading PDF](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v12_2026-11-04/paper.pdf) · [Overleaf bundle](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v12_2026-11-04/overleaf_v12.zip) · [Figures and reproduction](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v12_2026-11-04/README.md) · [中文读图说明](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v12_2026-11-04/READING_GUIDE_ZH.md)

A scientific Agent turns published evidence, a target-population description, optional observations and an intended analysis into useful virtual biomedical data. Complete-cohort generation without participant inputs is central. The Agent chooses scientific structure and parameters; numerical tools sample and inspect the model.

The current revision uses native-unit result plots and an implementation-grounded method diagram. It changes figure presentation, captions and explanation, while preserving the scientific body, numerical tables and experiments. It adds no generated cohort, clinical fit or independent validation.

## Paper and interpretation

- [Implementation trace](biomedical_research/virtual_cohort_system/reports/paper_figure_revision_v12_2026-11-04/IMPLEMENTATION_TRACE.md): actual request, evidence record, numerical conversion, generator interface, source feedback and retention decision.
- [Independent figure and guide review](biomedical_research/virtual_cohort_system/reports/paper_figure_revision_v12_2026-11-04/FIGURES_AND_GUIDE_REVIEW.md) and [final PDF review](biomedical_research/virtual_cohort_system/reports/paper_figure_revision_v12_2026-11-04/FINAL_PDF_REVIEW.md).
- [Six-endpoint reading guide](biomedical_research/virtual_cohort_system/reports/paper_figure_revision_v12_2026-11-04/FIG23_READING_GUIDE_ZH.md): the precise meaning of five improved discrepancies, the CHNS BMI deterioration, remaining conditional mismatches and different uncertainty sources.
- Primary-paper result-page readings: [G-Sim and SPADA](biomedical_research/virtual_cohort_system/reports/paper_figure_revision_v12_2026-11-04/GSIM_SPADA_RESULT_READING.md), [LLMSynthor](biomedical_research/virtual_cohort_system/reports/paper_figure_revision_v12_2026-11-04/LLMSYNTHOR_FIGURES_AND_RESULT_READING.md).
- [Method and implementation](biomedical_research/virtual_cohort_system/README.md), [current focus](biomedical_research/virtual_cohort_system/docs/CURRENT_RESEARCH_FOCUS.md), [consolidation and rerun decision](biomedical_research/virtual_cohort_system/reports/manuscript_consolidation_2026-11-04/CONSOLIDATION_DECISION.md), and [method/version audit](biomedical_research/virtual_cohort_system/reports/manuscript_consolidation_2026-11-04/METHOD_AND_RERUN_AUDIT.md).

The principal experimental settings retain distinct information conditions:

1. **External-evidence development.** CHNS and ENSANUT, 20 Agent plus four statistical constructions and 72 final tables. Relational evidence lowered five of six constructor-averaged mean absolute coefficient discrepancies; CHNS BMI discrepancy increased. Improvement does not mean that every resulting relation is accurate.
2. **Target-summary reconstruction.** Six Agent constructions in a separate CHNS experiment. Accessible summaries supported closer reconstruction across regressions and correlations. Additional review produced retention, with no demonstrated revision gain.
3. **Published-model reconstruction.** One Agent and one reconstructed published law produced six valid longitudinal tables, each with 11,509 virtual subjects at four visits. Both HbA1c interactions, all 16 mixed-model effects, distributional mismatches and three invalid initial comparator attempts remain recorded. No HRS participant records were used.
4. **Open-search construction.** A search without bibliographic seeds assembled five seriously reviewed original studies. One fresh constructor authored a joint law and delivered three complete 3,000-person tables. The complete seven-term display and missing-dependence sensitivity retain useful secondary BMI/age agreement together with conditional and distributional mismatches.

An additional 100 community-disjoint resplits of the existing CHNS sample contextualize the latest generated tables. All 36 metrics remain available in the [real-sample context supplement](biomedical_research/virtual_cohort_system/manuscript/integrated_figures_v09_2026-11-04/supplement_real_real_context.svg). These are within-sample descriptive comparisons, not new cohorts or equivalence thresholds.

The shared scientific procedure has separately frozen implementations and information packets. Historical enrichment, direct-output experiments and adverse results remain in the record. Virtual rows, seed draws, authored models and clinical reference families are different units. Arbitrary-request validity, standalone autonomy and replacement of clinical measurement are not claimed.

## Reproduction and access

The [v0.12 figure package](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v12_2026-11-04/README.md) contains original scripts, native-value bindings and captions. The editable method diagram is embedded in its exports; its builder regenerates the source. The reading PDF is a generic two-column copy, and the ZIP is an editable LaTeX package rather than an official conference template.

The existing aggregate reproduction entry point remains unchanged:

```powershell
python biomedical_research/virtual_cohort_system/reproducibility/reproduce_manuscript.py --repo-root . --output ../v07-reproduced
```

It verifies pinned aggregate inputs, reconstructs earlier numerical tables, redraws Figures 2–4/S1 and copies Figure 1 as a schematic. See [prerequisites and exact historical scope](biomedical_research/virtual_cohort_system/docs/REPRODUCING_MANUSCRIPT_v07.md). These aggregate-only workflows do not run an LLM, generate participant-like records or refit clinical data.

This repository is a reviewed research export. Patient-level real/generated tables, third-party original papers/codebooks, credentials, model contexts and temporary render images remain local. Clinical reruns require lawful dataset access and the appropriate environment. The [v0.12 public scope](biomedical_research/virtual_cohort_system/reports/paper_figure_revision_v12_2026-11-04/PUBLIC_SCOPE.md) defines the exact release boundary.

## History and next work

- [v0.11](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_11.md) and its [historical gallery](biomedical_research/virtual_cohort_system/manuscript/visual_redesign_v11_2026-11-04/index.html) preserve the preceding visual edition.
- [v0.10](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_10.md), its [reading PDF](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v10_2026-11-04/paper.pdf), [Overleaf bundle](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v10_2026-11-04/overleaf_v10.zip), [story design](biomedical_research/virtual_cohort_system/reports/conference_draft_v10_2026-11-04/STORY_AND_VISUAL_DESIGN.md) and [independent review](biomedical_research/virtual_cohort_system/reports/conference_draft_v10_2026-11-04/INDEPENDENT_DRAFT_REVIEW.md) preserve the narrative checkpoint.
- [v0.9](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_9.md), [original figure plan](biomedical_research/virtual_cohort_system/manuscript/integrated_figures_v07_2026-11-03/FIGURE_PLAN.md), [historical outcomes](biomedical_research/virtual_cohort_system/manuscript/SUPPLEMENT_HISTORICAL_RESULTS_v05.md) and [exposure registry](biomedical_research/virtual_cohort_system/docs/DATASET_EXPOSURE_REGISTRY.md) retain the extended empirical record.

The manuscript is available for scientific author review. A future unified cross-case open-retrieval study is conditional on that stronger claim, not an automatically added requirement for this draft. Venue-specific formatting, article-length editing, authorship/funding/conflict/access/ethics/AI declarations and software/data-release terms remain to be finalized. No venue is settled and no submission has occurred.
