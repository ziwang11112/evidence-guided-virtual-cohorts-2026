# Evidence-guided virtual biomedical data

## From Published Evidence to Analyzable Biomedical Cohorts with Scientific Agents

Can researchers run useful biomedical analyses when the required individual records are unavailable? A scientific agent interprets statistics from published studies, chooses a joint model for the requested population, and writes a generator that produces complete records. The experiments compare analyses of these records with measured sample estimates.

**Read the [paper (PDF)](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v19_2026-11-06/paper.pdf) or [paper (plain text)](biomedical_research/virtual_cohort_system/manuscript/DRAFT_v0_19.md).** The current manuscript is v0.19, dated 6 November 2026. Table 1 identifies who supplies each scientific decision. Figure 3 follows two agent-authored transfer choices from a published four-cell table to three analyses of continuous virtual records.

| Scientific question | Where to look |
| --- | --- |
| How does a statistic in a paper become a numerical dependency in an agent-authored generator? | Table 1, Figure 1 and the [worked derivation](biomedical_research/virtual_cohort_system/manuscript/SUPPLEMENT_SOURCE_AND_ASSUMPTIONS_v05.md) |
| Which adjusted regressions improve when relationship evidence is added? | Figure 2 and the [CHNS / ENSANUT results](biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/RESULTS.md) |
| What happens when researchers use one virtual iron-status cohort for three different analyses? | The [Figure 3 reproduction materials](biomedical_research/virtual_cohort_system/manuscript/paper_figures_v19_2026-11-06/README.md), and the [iron-status evidence, models and results](biomedical_research/virtual_cohort_system/reports/iron_breadth_2026-11-05/RESULTS.md) |
| Which results carry across biomarkers or hold when exact target results are withheld until after generation? | Figure 4 and the [glycemia / lipids results](biomedical_research/virtual_cohort_system/reports/evidence_use_cross_task_2026-11-05/RESULTS.md), then Figure S5 and the [earlier prospective wave](reports/scaleup_2026-11-01/production_release/RESULTS.md) |

The [archived v0.18 review guide](REVIEW_GUIDE.md) distinguishes source reconstruction, developmental evaluation and the earlier prospective tests. It links the source materials, scientific generator code, aggregate endpoints, and what a reader can reproduce from this repository. Real and generated participant records remain local.

[Post hoc lipid ordering check](biomedical_research/virtual_cohort_system/manuscript/Q5_LIPID_ORDER_POST_HOC_v19.md) · [Overleaf project](biomedical_research/virtual_cohort_system/manuscript/conference_draft_v19_2026-11-06/overleaf_v19.zip) · [Manuscript versions and figures](biomedical_research/virtual_cohort_system/manuscript/README.md) · [Project index](biomedical_research/virtual_cohort_system/README.md) · [Dataset exposure registry](biomedical_research/virtual_cohort_system/docs/DATASET_EXPOSURE_REGISTRY.md)
