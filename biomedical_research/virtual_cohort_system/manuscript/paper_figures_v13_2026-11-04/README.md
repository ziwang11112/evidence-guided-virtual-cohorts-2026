# v0.13 scientific figure package

Five main figures and one supplementary figure support the integrated manuscript. The blue/purple/coral palette and native scientific units are retained.

| Figure | Scientific role | Production identity |
|---|---|---|
| 1 | Worked Agent evidence-to-model implementation | Original schematic, copied unchanged from v0.12 |
| 2 | All six main-study E0/E1 analyses | Original aggregate plot, copied unchanged |
| 3 | Supplied-summary joint reconstruction | Original aggregate plot, copied unchanged |
| 4 | Longitudinal source-model reconstruction | Original aggregate plot, copied unchanged |
| 5 | Four open-retrieval constructions across two requests | Newly drawn from frozen aggregate results; all 36 primary values |
| S1 | Earlier open-search analysis and dependence sensitivity | Former Figure 5, copied unchanged |

The [new Figure 5](fig5-open-retrieval.svg), [caption](CAPTION_FIG5.md), [中文读图说明](FIG5_READING_GUIDE_ZH.md), [seed values](FIG5_SEED_VALUES.csv) and [numerical bindings](FIG5_NUMERIC_BINDINGS.json) retain all authors, seeds, units and reference definitions. Means/ranges describe draws from fixed laws, not structural uncertainty. Previously exposed sample references are not population ground truth; neither reference interval is an acceptance margin.

Historical drawing/plotting sources remain in the [v0.12 package](../paper_figures_v12_2026-11-04/README.md). [Reuse hashes](../../reports/manuscript_integration_v13_2026-11-04/FIGURE_REUSE_MANIFEST.json) establish that those fifteen SVG/PNG/PDF exports are unchanged.

The new [plot builder](render_open_retrieval.py) uses aggregate inputs only. Its default paths refer to the original local experiment layout; public repositories store that layout under reports, so reproduce with the original work/ directory layout or point the script's BATCH constant to the corresponding reports/ directory in a separate reproduction copy; the archived reviewed builder has no path-option CLI. It does not invoke an Agent, generate tables or refit patient data. Exact inputs and output hashes are in the binding file. The complete [experimental report](../../reports/core_workflow_replication_2026-11-04/RESULTS.md) retains all 330 diagnostic values beyond the 36 primary values shown.

Independent checks: [new figure review](../../reports/manuscript_integration_v13_2026-11-04/NEW_FIGURE_REVIEW_NOTES.md), [draft numerical/claim review](../../reports/manuscript_integration_v13_2026-11-04/INDEPENDENT_DRAFT_REVIEW.md), and [final PDF layout review](../../reports/manuscript_integration_v13_2026-11-04/FINAL_PDF_REVIEW.md). A layout check at the current full-width size does not certify arbitrary journal-column reduction.
