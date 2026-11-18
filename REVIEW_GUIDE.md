# Reviewer guide

**From Fragmented Evidence to Analyzable Biomedical Cohorts with Scientific Agents**. KDD working manuscript v0.34, 18 November 2026.

1. Read the [manuscript and supplement](biomedical_research/virtual_cohort_system/manuscript/kdd_draft_v34_2026-11-18/paper.pdf).
2. Open the [experiment and result index](biomedical_research/virtual_cohort_system/PUBLIC_RESEARCH_INDEX.md) to locate the protocol, aggregate data, model programs and failures for each study.
3. Follow the [original-paper audit](biomedical_research/virtual_cohort_system/work/original_paper_capability_2026-11-17/SOURCE_MODEL_AUDIT.md) from a reported statistic to a modeling decision and its downstream estimate.
4. Check the [matched-size comparison](biomedical_research/virtual_cohort_system/work/matched_size_utility_2026-11-17/RESULTS.md) and the [figure and table verification](biomedical_research/virtual_cohort_system/work/manuscript_integration_v34_2026-11-18/QA.json).

## Replay the published numerical results

From the repository root, run this command in a Python environment with NumPy, pandas, SciPy, Matplotlib and PyMuPDF. The release check was tested with Python 3.12.10 and package versions 2.4.5, 3.0.3, 1.17.1, 3.10.9 and 1.26.7, respectively.

```sh
python -B biomedical_research/virtual_cohort_system/reproducibility/check_v34.py
```

The command exercises both original-paper analysis routes on an in-memory fixture and checks the primary result figures, Tables 1, S7 and S8 against the published aggregates. It also prints a descriptive comparison of anchor-study statistics with the six requested analyses and a breakdown of the nine lifestyle contrasts by signed difference, estimator spread and mean absolute difference. For blood pressure the source coefficients have a different adjustment set. For iron status the threshold counts leave the continuous rank correlation undetermined.

This replay uses published research outputs and runs offline. A new Agent construction would require model access and source texts. Independent re-estimation of measured outcomes would require access to the original cohort records.

[Archived v0.18 reviewer guide](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/9b8920d87c3ad4cfda9e05da91e40d4570b4ae34/REVIEW_GUIDE.md)
