# Evidence-guided virtual biomedical data

**Current paper edition:** [Reading PDF](manuscript/conference_draft_v12_2026-11-04/paper.pdf), [Overleaf bundle](manuscript/conference_draft_v12_2026-11-04/overleaf_v12.zip), [figure guide](manuscript/paper_figures_v12_2026-11-04/README.md), and [中文读图说明](manuscript/paper_figures_v12_2026-11-04/READING_GUIDE_ZH.md). Native-unit result figures and an implementation-grounded method diagram; unchanged scientific body, tables and experiments.

**Current manuscript: [v0.12](manuscript/DRAFT_v0_12.md), 4 November 2026.**

A scientific Agent turns qualified biomedical evidence, a population description, optional observations and a requested analysis into virtual data. The Agent chooses the joint model and parameters; numerical tools sample and inspect it. Complete-cohort generation without participant inputs is central.

## Paper and evidence

- [Current build notes](manuscript/conference_draft_v12_2026-11-04/README.md), [independent figure/guide review](reports/paper_figure_revision_v12_2026-11-04/FIGURES_AND_GUIDE_REVIEW.md), [final PDF review](reports/paper_figure_revision_v12_2026-11-04/FINAL_PDF_REVIEW.md), and [implementation trace](reports/paper_figure_revision_v12_2026-11-04/IMPLEMENTATION_TRACE.md).
- [Six-endpoint numerical interpretation](reports/paper_figure_revision_v12_2026-11-04/FIG23_READING_GUIDE_ZH.md), [G-Sim/SPADA result-page reading](reports/paper_figure_revision_v12_2026-11-04/GSIM_SPADA_RESULT_READING.md), and [LLMSynthor result-page reading](reports/paper_figure_revision_v12_2026-11-04/LLMSYNTHOR_FIGURES_AND_RESULT_READING.md). “Five of six improved” concerns mean absolute coefficient discrepancy; CHNS BMI worsens and other residual mismatches remain visible.
- Historical editions: [v0.11](manuscript/DRAFT_v0_11.md) and its [gallery](manuscript/visual_redesign_v11_2026-11-04/index.html); [v0.10 reading PDF](manuscript/conference_draft_v10_2026-11-04/paper.pdf), [Overleaf bundle](manuscript/conference_draft_v10_2026-11-04/overleaf_v10.zip), and [story/visual design](reports/conference_draft_v10_2026-11-04/STORY_AND_VISUAL_DESIGN.md).
- [Independent v0.10 review](reports/conference_draft_v10_2026-11-04/INDEPENDENT_DRAFT_REVIEW.md). The main text retains four evaluation questions, five figures and three tables; [v0.9](manuscript/DRAFT_v0_9.md) retains extended details. Presentation revisions add no experiment.

- [v0.10 narrative checkpoint](manuscript/DRAFT_v0_10.md), [consolidation and rerun decision](reports/manuscript_consolidation_2026-11-04/CONSOLIDATION_DECISION.md), and [claim/figure audit](reports/manuscript_consolidation_2026-11-04/SUPPORT_AND_FIGURE_AUDIT.md).
- [Four main figures and Figure S1](manuscript/integrated_figures_v07_2026-11-03/FIGURE_PLAN.md), with [captions](manuscript/integrated_figures_v07_2026-11-03/CAPTIONS.md).
- [New Figure 5](manuscript/integrated_figures_v09_2026-11-04/figure5_agent_scientific_utility.svg) joins the completed open-search construction to all seven regression terms and its pre-generation joint-dependence sensitivity. [Real-sample variation context](manuscript/integrated_figures_v09_2026-11-04/supplement_real_real_context.svg) remains a separate supplement.
- [Aggregate reproduction guide](docs/REPRODUCING_MANUSCRIPT_v07.md).
- [Current focus](docs/CURRENT_RESEARCH_FOCUS.md), [focused experiment gaps](manuscript/KEY_EXPERIMENT_GAPS_v07_2026-11-03.md), and [existing-reference feasibility audit](manuscript/EXISTING_REFERENCE_FEASIBILITY_v07_2026-11-03.md).

- [Current system contribution and evaluation plan](docs/AGENT_SYSTEM_CONTRIBUTION_AND_EVALUATION_2026-11-03.md): complete Agent data generation is primary; evidence-selection scoring is optional.
- [Implemented request intake](docs/REQUEST_INTAKE_V1.md): two request-only demonstrations and 19 passing interface tests. This entry prepares tasks; it does not yet launch the scientific Agent or generate data.
- [Completed live Agent integration](reports/agent_system_live_2026-11-03/RESULTS.md): actual retrieval, two Agent-authored whole-cohort models, eight executions and six delivered tables. Host-dispatched Agents use the intake and tools; partial analytical utility, unavailable source replays and both retention decisions are reported.
- [Earlier top-venue assessment and optional acquisition proposal](manuscript/TOP_VENUE_RESEARCH_DECISION_2026-11-03.md).
- [v0.8 independent writing review](manuscript/REVIEW_v0_8_2026-11-03.md), [earlier fallback venue preparation](manuscript/VENUE_AND_SUBMISSION_PLAN_v08_2026-11-03.md), and [provisional submission text](manuscript/SUBMISSION_TEXT_v08_2026-11-03.md). PLOS is not the settled destination.

## Completed experiments

| Setting | Executed work | Interpretation |
|---|---|---|
| External evidence: CHNS and ENSANUT | 20 Agent and four statistical constructions; 72 final 3,000-row tables; six focal regression endpoints | Added relationship evidence lowered five discrepancies and increased CHNS BMI discrepancy. Exposed developmental references. |
| Target-summary access: separate CHNS L/R | Six Agent constructions; 42 executions, 24 distinct tables overall and 18 distinct delivery tables | Closer reconstruction of several supplied summaries. Initial/final deliveries identical; no additional-stage revision gain. |
| Published longitudinal model: HRS | One Agent and one reconstructed published-law model; six valid tables, each 11,509 virtual subjects at four visits; nine physical generations include three invalid initial comparator attempts | Native longitudinal analysis and source-model reconstruction. Weak upper-threshold interaction and upper-HbA1c spread remain imperfect. No HRS participant records used. |
| Live request-to-data integration | Two fresh-context authors; actual source retrieval; eight 3,000-row executions, including six distinct delivery tables | A age and B glucose relationships have useful agreement; B glucose-adjusted BMI does not. All source replays unavailable, both initial candidates retained. Existing CHNS development reference. |
| Open search to reviewed-evidence construction | Five seriously reviewed original studies; one fresh scientific constructor; one trial and three final 3,000-person tables | Complete joint model and task-specific analysis with useful secondary BMI/age agreement, remaining conditional/distributional differences and explicit unreported-dependence sensitivity. All final outputs retained; no controlled retrieval or revision-gain claim. |
| Real-sample interpretation context | 100 community-disjoint resplits of the existing CHNS sample; all 36 metrics; the same three frozen generated tables | Descriptive variation context for each analysis; no new cohort, generation or equivalence cutoff. |

These are separate information settings. Virtual rows, seed draws, authors and clinical references are different units. The evidence ledger retains historical enrichment/direct-output uses and failed studies. Revealed targets remain closed to tuning and renewed confirmation.

## Method and implementation

1. Define the scientific use, population and allowed information.
2. Preserve study population, measurement, operator, estimate, uncertainty and provenance.
3. Let the Agent choose the generator and declare joint/transfer assumptions.
4. Execute versioned candidates and supply permitted source feedback; record revision or retention.
5. Apply the scientific analyses and interpret agreement according to the information supplied.

Different requests may receive different generators. Multiple Agents, model training and universal superiority over a customized statistical generator are not requirements. Principal experiments use curated evidence and Agent-authored programs. Historical direct table authorship is reported separately; general autonomous extraction and missing-cell completion are not established by these principal studies.

Implementation references: [generation skill](skills/evidence-cohort-generation/SKILL.md), [execution adapter](docs/EXECUTION_ADAPTER.md), and [source replay](docs/SOURCE_REPLAY.md). Individual records identify their actual interface versions. Source-statistic consistency does not certify extraction, transport or analytical usefulness.

## Reproduction and access

The [current figure package](manuscript/paper_figures_v12_2026-11-04/README.md) supplies original drawing/plotting scripts, exact native-value bindings and caption definitions. It redraws existing aggregates only. The editable diagram is embedded in its SVG/PNG/PDF exports and regenerated by its builder; no standalone diagram source or patient-level file is included in the new release.

The [public reproduction entry point](docs/REPRODUCING_MANUSCRIPT_v07.md) verifies pinned aggregate inputs, reconstructs numerical tables, redraws Figures 2-4/S1 and copies Figure 1 as a schematic. It does not run an LLM, generate participant-like records or refit clinical data.

Participant-level real/generated files, third-party full articles/codebooks and credentials are excluded from the public export. Clinical reruns require lawful dataset access and the case-specific environment. Repository availability does not replace those conditions.

## Status and history

The empirical versions and earlier drafts remain unchanged. v0.9 adds the completed open-search, reviewed construction and real-sample context results while retaining the previous four tables and figures. The [method/version audit](reports/manuscript_consolidation_2026-11-04/METHOD_AND_RERUN_AUDIT.md) finds no shared unresolved error requiring wholesale regeneration. Current work consolidates published aggregate outputs and writing; a new unified cross-case open-retrieval experiment is needed only for that stronger prospective claim. Author/funding/access/ethics/AI-use declarations, article-type selection and publication-layout inspection remain.

Earlier implementation/progress notes remain in the [previous README](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/bec2041d1816432dd744cf875c649e9ea6142e67/biomedical_research/virtual_cohort_system/README.md). They describe their original dates. Frozen protocols, adverse results and disclosure history remain in the [exposure registry](docs/DATASET_EXPOSURE_REGISTRY.md) and linked records.
