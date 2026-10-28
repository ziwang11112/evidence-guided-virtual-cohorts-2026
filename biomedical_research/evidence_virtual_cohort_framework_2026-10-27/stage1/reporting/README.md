# Stage 1 aggregate reporting

The primary narrative is [../RESULTS.md](../RESULTS.md). This directory contains a reproducible presentation of the frozen, completed aggregate evaluation. It contains no participant-level reference data or synthetic cohort rows.

Run `python biomedical_research/evidence_virtual_cohort_framework_2026-10-27/stage1/reporting/build_report.py` from the workspace root. Required packages are NumPy, pandas and Matplotlib; exact versions are recorded in `reporting_manifest.json`. The script first requires the final evaluator manifest and verifies all aggregate-evaluation hashes. It writes only this reporting directory and `../RESULTS.md`.

The six figures are standard scientific plots, each in PNG and vector PDF:

- `case_a_reserved_correlations`: all six Ross baseline correlations.
- `case_b_reserved_correlations`: all six Travers change correlations.
- `case_c_reserved_correlations`: all six He change correlations.
- `case_a_reserved_proxy_associations`: all four Ross exploratory proxy associations.
- `case_b_paired_uncertainty`: all four Travers paired change SD / SE ratios.
- `case_c_paired_uncertainty`: all four He paired change SD / SE ratios.

Every figure shows the three common-parent lineages and each retained scenario. The three fixed statistical contexts remain distinct. P1 is the proposed target anchor, P2 and P3 are the alternatives in frozen allocation order; exact names are in `tables/scenario_key.csv`. A dot is one generated cohort's aggregate estimate. Diamonds and connecting lines summarize the median and min–max of those estimates, not a confidence interval. Correlation/proxy reference bands are real unadjusted 95% intervals. The figures were visually inspected after rendering; the evidence record is `VISUAL_QA.md`.

`ALL_TERM_COMPARISONS.md` preserves all 55 registered terms across all three ordinary/proposed lineage pairs. `STATISTICAL_REFERENCE_RESULTS.md` preserves all three statistical contexts. CSV tables retain the full 825 term-by-scenario summaries and the 495 ordinary-versus-each-proposed term comparisons, along with all state counts, reference results, paired uncertainty, scenario disagreement and fit warnings. Raw errors in different endpoint units are never averaged together. Family counts are explicitly descriptive correlated term-by-draw outcomes.

This reporting pass is post hoc presentation of the fixed metrics. It changes no generator, frozen protocol, analysis definition or evaluation result. It does not select a scenario, pool models, add a superiority test, establish interval coverage, or create independent confirmation from development cases.
