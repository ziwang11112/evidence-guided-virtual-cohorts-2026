# Reviewer guide

**Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?** KDD Research working manuscript v0.36, 19 November 2026.

1. Read the [manuscript and supplement](biomedical_research/virtual_cohort_system/manuscript/kdd_draft_v36_2026-11-19/paper.pdf).
2. Open the [experiment and result index](biomedical_research/virtual_cohort_system/PUBLIC_RESEARCH_INDEX.md) to locate the protocol, aggregate data, model programs and failures for each study.
3. Follow the [original-paper audit](biomedical_research/virtual_cohort_system/work/original_paper_capability_2026-11-17/SOURCE_MODEL_AUDIT.md) from a reported statistic to a modeling decision and its downstream estimate.
4. Check the [matched-size comparison](biomedical_research/virtual_cohort_system/work/matched_size_utility_2026-11-17/RESULTS.md) and the [figure and table verification](biomedical_research/virtual_cohort_system/work/manuscript_integration_v34_2026-11-18/QA.json).

5. Inspect the [prospective freeze and external comparison](biomedical_research/virtual_cohort_system/work/prospective_bp_freetown_2026-11-18/RESULTS.md) and the [deposited-field audit](biomedical_research/virtual_cohort_system/work/prospective_bp_freetown_2026-11-18/REFERENCE_AUDIT.json).

[Original-paper iron experiment and measured survey](biomedical_research/virtual_cohort_system/work/original_paper_iron_sensitivity_2026-11-19/RESULTS.md) · [Checks before opening the reference](biomedical_research/virtual_cohort_system/work/original_paper_iron_sensitivity_2026-11-19/SCIENTIFIC_RESULTS.json)

## Replay the published numerical results

From the repository root, run these commands in a Python environment with NumPy, pandas, SciPy, Matplotlib and PyMuPDF. The release check was tested with Python 3.12.10 and package versions 2.4.5, 3.0.3, 1.17.1, 3.10.9 and 1.26.7, respectively.

```sh
python -B biomedical_research/virtual_cohort_system/reproducibility/check_v34.py
python -B biomedical_research/virtual_cohort_system/reproducibility/check_v35.py
python -B biomedical_research/virtual_cohort_system/work/prospective_bp_freetown_2026-11-18/replay_public.py
```

The first command exercises both original-paper analysis routes on an in-memory fixture and checks the primary result figures, Tables 1, S7 and S8 against the published aggregates. It also prints a descriptive comparison of anchor-study statistics with the six requested analyses and a breakdown of the nine lifestyle contrasts by signed difference, estimator spread and mean absolute difference. For blood pressure the source coefficients have a different adjustment set. For iron status the threshold counts leave the continuous rank correlation undetermined.

The second command checks the three tables typeset in v0.35. The third replays the prospective freeze, model calculations and finite-draw decision. This replay uses published research outputs and runs offline. A new Agent construction would require model access and source texts. Independent re-estimation of measured outcomes would require access to the original cohort records.

[Archived v0.18 reviewer guide](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/9b8920d87c3ad4cfda9e05da91e40d4570b4ae34/REVIEW_GUIDE.md)
