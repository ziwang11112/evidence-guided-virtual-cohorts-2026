# Evidence-guided virtual biomedical data

**Current manuscript: [v0.14](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_14.md), 5 November 2026.**

**Evidence-Guided Agents for Analyzable Virtual Biomedical Cohorts**

[Reading PDF](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v14_2026-11-05/paper.pdf) · [Overleaf-ready ZIP](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v14_2026-11-05/overleaf_v14.zip) · [Figures](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v14_2026-11-05/README.md) · [Draft checklist](biomedical_research/virtual_cohort_system/manuscript/KEY_EXPERIMENT_GAPS_v14_2026-11-05.md)

A scientific Agent turns published biomedical evidence, a population description, optional observations and intended analyses into a joint generating model and virtual data. Whole-cohort generation without individual construction records is central. The Agent chooses substantive structure and numerical evidence use; deterministic tools sample, inspect and analyze the result. Different research requests can receive different models.

## Completed scientific story

The paper combines an external-evidence information contrast, supplied-summary reconstruction, a published longitudinal model, repeated open retrieval, and a new glycemic/lipid cross-task study. These settings have different inputs and references and retain separate denominators. The contribution is an inspectable evidence-to-data workflow and demonstrated analysis-specific uses, not a new statistical family or universal superiority claim.

The [new cross-task experiment](biomedical_research/virtual_cohort_system/reports/evidence_use_cross_task_2026-11-05/RESULTS.md) contains six fresh Agent constructions, two requests and 18 final tables of 3,000 fictional rows. All 54 primary point directions agreed with the corresponding sample estimates, but effect magnitudes, residual dependence and dispersion differed. The TC slope reference interval crosses zero. All 513 aggregate outputs were independently recomputed; 324 matched cached references and 189 were generated-only diagnostics. These references were already exposed in development.

All six authors retained their initial laws. The 132 source checks were unavailable under their declared definitions, so numerical source-replay or feedback-driven improvement is not established. The data support transparent, assumption-dependent relationship exploration and analysis-workflow inspection; quantitative replacement of a measured target cohort remains unsupported. All six constructions and unfavorable results remain visible.

## Read, inspect and reproduce

- [Manuscript history and reviews](biomedical_research/virtual_cohort_system/manuscript/README.md)
- [Story and figure roles](biomedical_research/virtual_cohort_system/reports/manuscript_integration_v14_2026-11-05/STORY_AND_FIGURE_PLAN.md)
- [New Figure 6: scientific analyses](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v14_2026-11-05/fig6-cross-task.svg) and [Figure 7: dispersion](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v14_2026-11-05/fig7-dispersion.svg)
- [Evidence-use implementation](biomedical_research/virtual_cohort_system/cohort_harness/evidence_use_v1.py) and [design](biomedical_research/virtual_cohort_system/docs/EVIDENCE_USE_V1.md)
- [Portable aggregate plotting](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v14_2026-11-05/render_cross_task_aggregates.py): both new PNGs were reproduced pixel-for-pixel without participant or generated-row access.
- [Exposure registry](biomedical_research/virtual_cohort_system/docs/DATASET_EXPOSURE_REGISTRY.md) and [public release scope](biomedical_research/virtual_cohort_system/reports/manuscript_integration_v14_2026-11-05/PUBLIC_SCOPE.md)

The 16-page generic reading copy contains seven main figures, one supplementary figure, three main tables, four supplementary tables and 28 references. Scientific author review, venue/length selection and author declarations remain. The ZIP is a local LaTeX package, not an uploaded Overleaf project or a submission.

Patient-level real/generated tables, third-party originals/codebooks and credentials remain local. Public plotting is portable; the historical construction controllers retain documented local layout/runtime/source-access requirements. This release did not rerun a generator, read participant rows, refit a clinical reference or retune an exposed target. [Current focus](biomedical_research/virtual_cohort_system/docs/CURRENT_RESEARCH_FOCUS.md).
