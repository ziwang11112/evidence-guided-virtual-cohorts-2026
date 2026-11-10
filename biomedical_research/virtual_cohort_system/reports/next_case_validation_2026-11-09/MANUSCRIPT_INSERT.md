# Additional whole-cohort validation: paired blood pressure

## Role in the paper

This experiment adds a new prespecified biomedical request to the tested authoring workflow. It evaluates whole-cohort construction without target individual inputs, rather than enrichment of one missing column. The PNS release was already used for a different outcome; the new blood-pressure estimands were not previously numerically exposed in the audited project record. We therefore describe this as a qualified new-task validation within a previously used data family, not a new independent cohort or a globally blinded experiment.

## Methods paragraph

We specified a joint blood-pressure task before examining its reference estimates. Five fresh scientific Agent contexts received an identical external-evidence packet, target description and analysis request, with no target records, moments or coefficients. The packet contained INTERSALT BMI–blood-pressure coefficients, Beijing older-adult blood-pressure summaries, and contextual measurement information. Each author selected its own stochastic structure and numerical assumptions, underwent independent implementation review, and generated three 3,000-row cohorts with seeds 271, 409 and 557 in the existing isolated worker. Outputs contained age, recorded sex, BMI, systolic blood pressure (SBP) and diastolic blood pressure (DBP), plus a mechanical identifier. Authors could retrieve more evidence and revise once using source feedback; all five chose to retain their initial model. We sealed every author and all fifteen outputs before revealing the three reference analyses. The reference comprised 8,352 eligible PNS laboratory-substudy records, using the supplied laboratory weights. Both blood-pressure regressions adjusted for age and sex; the third analysis correlated the two residuals after adjustment for age, sex and BMI. These are descriptive association projections, not intervention effects. All fixed outputs and analyses were retained.

## Results paragraph

All fifteen tables supported the three prespecified analyses. Across all draws, the BMI–SBP coefficients were 3.081–4.276 mmHg per 5 kg/m², compared with a weighted reference estimate of 3.524. The BMI–DBP coefficients were consistently larger, 2.886–3.691 versus 2.260. Residual SBP–DBP correlations were consistently smaller, 0.466–0.646 versus 0.717. The qualitative discrepancy pattern persisted with the unweighted reference, whose corresponding estimates were 3.435, 2.114 and 0.741. Marginal SD ratios relative to the weighted reference ranged from 0.931 to 1.129 for SBP and 0.896 to 1.076 for DBP; residual SD ratios ranged from 0.833 to 1.058 and 0.880 to 1.034. Generated mean blood pressures were also lower across all draws: SBP 117.90–124.81 versus 125.83 mmHg and DBP 74.65–77.05 versus 78.87 mmHg. Thus the broadly comparable variability and BMI–SBP effects did not establish adequate reconstruction of every association or of the joint distribution.

| Independent author | BMI–SBP, median of three draws | BMI–DBP, median of three draws | Residual correlation, median of three draws |
|---|---:|---:|---:|
| A01 | 3.391 | 2.997 | 0.508 |
| A02 | 3.815 | 3.350 | 0.644 |
| A03 | 3.980 | 2.933 | 0.506 |
| A04 | 3.880 | 3.053 | 0.557 |
| A05 | 3.709 | 3.058 | 0.526 |
| Weighted real reference | 3.524 | 2.260 | 0.717 |

The full draw ranges, all diagnostics, source-check dispositions and unweighted sensitivity are in RESULTS.md/RESULTS.json. Authors are repeated constructions under the same host configuration, and seeds are repeated draws from each law; neither constitutes an independent clinical reference.

## Interpretation paragraph

The experiment provides further evidence that an Agent can construct a usable multivariable data object from incomplete published evidence and an analysis request, while locating its scientific usefulness at the analysis level. In this case, the magnitude of the BMI–SBP relationship was reasonably close to the measured reference, but the BMI–DBP relationship and residual dependence remained mismatched. All authors numerically adopted the same published BMI coefficients under explicit transfer assumptions; their residual dependence, demographic laws and nonlinear age effects remained assumptions. The observed gaps are compatible with source-to-target and model-specification limitations, but this experiment does not identify their separate causal contributions. No model was regenerated after disclosure.

Source feedback was executed but did not certify transport: 108 strict check evaluations remained non-computable, while 75 assumption-labelled descriptive contrasts were calculated. Those are repeated checks, not 183 independent source constraints. There was no additional author retrieval, source-population replay or scientific revision. Accordingly, this experiment supports analysis-specific generation feasibility, not an improvement from feedback, autonomous search, broad calibrated inference or superiority over a competing generator. These distinctions complement the paper's existing comparative evidence rather than replacing it.

## Figure captions

**Paired blood-pressure analysis from fully generated cohorts.** Three panels show BMI–SBP and BMI–DBP regression coefficients (mmHg per 5 kg/m², adjusted for age and recorded sex) and residual SBP–DBP correlation after adjustment for age, sex and BMI. Each row is one independent author; three dots are its fixed-seed draws and connecting lines their range. The dashed line is the weighted reference estimate. Shading shows 2.5th–97.5th percentiles from 500 conditional IID row resamples retaining the original weights; it is not a survey-design confidence interval or a prespecified equivalence margin. Every author and seed is shown.

**Variability accompanying the analysis estimates.** Marginal and residual standard deviations of each generated biomarker are divided by those of the same weighted reference. Circles denote SBP and squares DBP; all three draws per author are displayed. A ratio of one denotes matching dispersion, not statistical or biomedical acceptance. Means and associations must be assessed separately.

## Editorial decision

Retain the shared workflow and add this complete result as a bounded task-extension panel. Do not select A02's correlation and A01's SBP estimate to manufacture a composite best generator. Do not promote the band to a pass criterion or convert same-sign counts into broad validation. This unit is closed to result-guided tuning. A future change requires a separately justified method question and prospective evaluation; no additional dataset or component is triggered by these discrepancies alone.
