# Evidence-guided virtual biomedical data

**Current working paper [v0.13.1](manuscript/DRAFT_v0_13_1.md), 4 November 2026.**

[Reading PDF](manuscript/conference_draft_v13_1_2026-11-04/paper.pdf) · [Overleaf-ready ZIP](manuscript/conference_draft_v13_1_2026-11-04/overleaf_v13_1.zip) · [Figure package](manuscript/paper_figures_v13_2026-11-04/README.md) · [Experiment-gap checklist](manuscript/KEY_EXPERIMENT_GAPS_v13_1_2026-11-04.md)

The paper evaluates whether a complete virtual cohort can support a researcher’s intended analysis. An Agent uses qualified biomedical evidence, a population description and any available observations to choose a joint law. Numerical tools sample it. We run the intended analysis on the final table and compare the resulting estimates with an appropriate reference.

## Integrated scientific story

The [story/figure plan](reports/manuscript_integration_v13_2026-11-04/STORY_AND_FIGURE_PLAN.md) distinguishes three contributions: implemented evidence-to-cohort construction; inspectable scientific modeling and explicit assumptions; analysis-centered evaluation across different information settings.

| Experiment | Distinct scale | Supported use and boundary |
|---|---|---|
| External-evidence main study | 20 Agent + 4 statistical constructions; 72 final tables | Additional relationships lower five of six mean coefficient discrepancies; CHNS BMI worsens. Exposed references. |
| CHNS target-summary reconstruction | 6 Agents; 18 distinct final tables | The final tables were analyzed for agreement with the supplied regressions and correlations. |
| HRS published-model reconstruction | 2 constructions; 6 valid longitudinal tables | Data support source-model follow-up analysis; source coefficients supplied, no HRS individual data. Weak branch/spread limitations remain. |
| Earlier reviewed open search | 5 reviewed studies; 1 constructor; 3 final tables | Useful selected relations and explicit dependence sensitivity; conditional/distributional differences remain. |
| New unified open-retrieval workflow | 4 constructors; 2 requests; 12 final tables | 12 unique studies, 16 paper uses; all six primary directions retained, mixed magnitudes/ranks/dispersion. Developmental repetition, not fresh clinical confirmation. |

The [complete new batch](reports/core_workflow_replication_2026-11-04/RESULTS.md) records 366 independently reproduced aggregate endpoints, four initial trials and twelve final 3,000-row tables. Its information and author roles differ from the earlier main study, so the new batch is not treated as another comparable arm or a controlled improvement over it. Seeds, generated rows, authors and clinical references are different units.

## Method and implementation

1. Define scientific use, population and allowed information.
2. Preserve source population, measurement, analysis operator, estimate, uncertainty and provenance.
3. Let the Agent choose a generator and declare missing joint/transport assumptions.
4. Execute versioned candidates and supply qualified feedback; record revision or retention.
5. Run scientific analyses and interpret usefulness according to the information supplied.

Different requests may receive different generators. Principal experiments use Agent-authored programs. Historical direct-table and enrichment experiments remain separate; these studies do not establish universal request coverage or clinical-measurement replacement.

Implementation: [generation skill](skills/evidence-cohort-generation/SKILL.md), [execution adapter](docs/EXECUTION_ADAPTER.md), [source replay](docs/SOURCE_REPLAY.md), and [worked implementation trace](reports/paper_figure_revision_v12_2026-11-04/IMPLEMENTATION_TRACE.md). Approximate source comparison does not certify source-population replay, extraction or transport.

## Manuscript, review and reproduction

- [Manuscript navigation](manuscript/README.md), [archived v0.13 content review](reports/manuscript_integration_v13_2026-11-04/INDEPENDENT_DRAFT_REVIEW.md), and [archived v0.13 PDF review](reports/manuscript_integration_v13_2026-11-04/FINAL_PDF_REVIEW.md).
- [New Figure 5](manuscript/paper_figures_v13_2026-11-04/fig5-open-retrieval.svg) and [中文读图说明](manuscript/paper_figures_v13_2026-11-04/FIG5_READING_GUIDE_ZH.md). Three-seed ranges are not confidence intervals; reference intervals are not acceptance margins.
- [Earlier six-endpoint interpretation](reports/paper_figure_revision_v12_2026-11-04/FIG23_READING_GUIDE_ZH.md), [aggregate reproduction entry](docs/REPRODUCING_MANUSCRIPT_v07.md), and [exposure registry](docs/DATASET_EXPOSURE_REGISTRY.md).

The manuscript integrates completed evidence without new generation or clinical fitting. Historical Figures 1–4 are unchanged; former Figure 5 is Figure S1. Old protocols, empirical results and adverse findings are preserved. The generic reading PDF is not an official submission template. Authorship/declarations and venue-specific production remain.

Patient-level real/generated data, third-party full articles/codebooks and credentials remain local. Clinical reruns require lawful access. The [v0.13 public scope](reports/manuscript_integration_v13_2026-11-04/PUBLIC_SCOPE.md) describes that release; aggregate-only plotting is not regeneration of clinical records.

Earlier navigation and additional historical links remain in the [previous README](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/baeaf8cf11be00a6f79df5971ad3279a8c6f5aa3/biomedical_research/virtual_cohort_system/README.md). [Current focus](docs/CURRENT_RESEARCH_FOCUS.md) and the focused gap checklist supersede old pending-work statements.
