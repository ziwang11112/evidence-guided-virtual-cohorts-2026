# Source-only review: retain structure

Retain selected trial **t0008** as a provisional development candidate, with its limitations and adverse trade-offs. Do not spend the remaining scientific session on a structural expansion unsupported by these two sources. No frozen file was edited and no generator was imported or executed during this review.

The controller completed 9 feasible numerical trials and 40 isolated executions. Selection used fit seeds 13101/13102 before replay seeds 23101/23102. I read the locked plan, result, selection, selected generator/specification and all four selected-trial source replay reports. Their report hashes match the recorded result bindings; all 18 checks in each report are computed and generation-linked. This review uses supplied verified feedback, rather than independently rerunning the entire verifier.

Selected parameters are `bridge_male` 0.50→0.75, `bridge_female` 0.50→0.25, `residual_sd_male` 4.31→4.81 pp, and `residual_sd_female` 4.31→3.81 pp. Published equation coefficients, conditional family, source rows, covariate assumptions and measurement mapping remain unchanged. Fit loss decreased **0.695051→0.623795 (10.25%)**. The stop was `max_trials`; `fit_threshold_not_met` means the exact zero target was not reached, not failed clinical equivalence. The selected replay loss is **0.706431**. There is no baseline result at the replay seeds, so comparing this number with the initial fit loss would confound parameter changes with seeds.

All 18 source constraints are shown below. Mean values summarize the two fit seeds; replay gives the two fresh values as a range. The final column compares **mean(abs(draw − reported))**, in the statistic's units, on common fit seeds. It is not abs(mean(draw) − reported). Body-fat mean/SD and intercept are in percent or percentage points; BMI, age, sex and inverse-BMI coefficients retain the exact units and adjustment sets in evidence.json and the original source estimator. T denotes Thai DEVELOPMENT and G the full Gallagher composition.

| Constraint | Reported | Initial fit mean | Selected fit mean | Selected replay range | Fit mean absolute error, initial→selected |
|---|---:|---:|---:|---:|---:|
| T: men_mean | 14.1 | 16.5906 | 15.3163 | 15.2725–15.3511 | 2.49055→1.21631 (improved) |
| T: men_sd | 6.5 | 6.28929 | 6.69745 | 6.65992–6.68709 | 0.21071→0.19745 (improved) |
| T: men_bmi_r | 0.72 | 0.705806 | 0.675099 | 0.671629–0.685628 | 0.0141943→0.0449013 (worsened) |
| T: women_mean | 31.8 | 32.2904 | 32.5238 | 32.4559–32.5381 | 0.490351→0.723844 (worsened) |
| T: women_sd | 8.4 | 9.2341 | 9.58658 | 9.63424–9.70092 | 0.834099→1.18658 (worsened) |
| T: women_bmi_r | 0.77 | 0.876161 | 0.903577 | 0.904373–0.906225 | 0.106161→0.133577 (worsened) |
| T: coef_intercept | -10.672 | -14.898 | -17.1507 | -17.603–-17.4974 | 4.22603→6.47865 (worsened) |
| T: coef_bmi | 1.648 | 1.8911 | 2.0092 | 2.02521–2.02942 | 0.243104→0.361199 (worsened) |
| T: coef_age | 0.065 | 0.0441316 | 0.0375618 | 0.0356032–0.0371546 | 0.0208684→0.0274382 (worsened) |
| T: coef_male | -15.3 | -12.9205 | -14.2426 | -14.2761–-14.107 | 2.37949→1.05743 (improved) |
| G: coef_intercept | 76 | 72.1296 | 74.1766 | 74.1601–74.2487 | 3.87044→1.82344 (improved) |
| G: coef_inv_bmi | -1097.8 | -1015.5 | -1034.94 | -1040.05–-1034.32 | 82.2951→62.8619 (improved) |
| G: coef_male | -20.6 | -17.7353 | -19.5267 | -19.9917–-18.3607 | 2.86471→1.07335 (improved) |
| G: coef_age | 0.053 | 0.0664651 | 0.0513046 | 0.0524149–0.0546951 | 0.0134651→0.00169542 (improved) |
| G: coef_asian_inv_bmi | 95 | 67.052 | 57.1105 | 55.0391–62.229 | 27.948→37.8895 (worsened) |
| G: coef_asian_age | -0.044 | -0.0461473 | -0.0450536 | -0.0541312–-0.0439456 | 0.00275239→0.00218928 (improved) |
| G: coef_male_inv_bmi | 154 | 67.3526 | 72.0508 | 43.9447–82.0497 | 86.6474→81.9492 (improved) |
| G: coef_male_age | 0.034 | 0.0330892 | 0.0476966 | 0.0457066–0.050616 | 0.00392337→0.0136966 (worsened) |

There are **9 improved and 9 worsened constraints** by mean absolute draw error: only 3 of 10 Thai checks improve, versus 6 of 8 Gallagher checks. The Thai context's mean scaled squared error worsens **0.621390→0.702771**; Gallagher improves **0.787127→0.525076**. These are correlated diagnostics under fixed engineering scales, not independent evidence or a likelihood. The replay context scores are 0.754642 and 0.646167 respectively.

The clearest gains are the Thai male mean and male coefficient, plus Gallagher intercept, inverse-BMI, sex and age terms. The slight Thai male SD improvement accompanies a worse male BMI correlation. Thai female mean, SD and BMI correlation all worsen. The pooled Thai intercept, BMI slope and age slope also worsen. Gallagher Asian inverse-BMI and male-age interactions worsen; male inverse-BMI improves slightly but remains far below154 on both fresh draws. The lower fitted female residual SD does not establish smaller biological residual variation: it participates in a compromise with mean curvature and reconstructed BMI tails, while the resulting female SD and correlation remain too large.

Sign cancellation matters even though both improvement-count definitions happen to yield9 here. For Gallagher Asian-age, fit mean absolute draw error is **0.002752→0.002189**, whereas absolute error of the seed mean is **0.002147→0.001054**. Initial Gallagher male-age has mean absolute draw error **0.003923**, but seed-mean absolute error only **0.000911**; selected error is **0.013697** by either definition. On fresh replay the Gallagher age error is **0.001140** by mean absolute draw error versus **0.000555** by seed-mean absolute error. Per-seed values and both definitions are retained in review_metrics.json.

Persistent Thai female and Gallagher interaction discrepancies exceed the observed between-seed fluctuations and expose an inadequate simultaneous source fit under this construction. They may reflect source conflict, the shared Thai/Japanese indicator, cross-device transport, mean misspecification, or unreported source covariate distributions. Their causes cannot be uniquely separated here. The corrected Thai BMI threshold distribution is compatible with published margins, but its broad female lower tail, within-threshold shape, allocation and age/BMI copula remain assumptions; inverse-BMI projections depend on them. A source or device identifier would violate the allowed scientific input set, and additional flexible interactions would be assumptions rather than recovered evidence. Retention therefore preserves an inspectable, imperfect candidate; it does not endorse source adequacy or prove that no useful model exists.

For `asian=0`, both bridge adjustments vanish. Thus the selected non-Asian conditional mean function is exactly the initial one; the fitted sex-specific dispersion changes. A later frozen, prespecified evaluation against independently reserved real measurements can assess this candidate's errors and downstream analytical performance in that particular target domain. It cannot be replaced by these source checks, by the invented qualification grid, or by repeated simulation seeds. No current target benefit, individual recovery, causal validity, general uncertainty calibration or measurement savings is established. If later target results are used to choose another model, a new independent evaluation would be required for that changed model.

Decision and traceability: review_decision.json contains exactly the requested five fields and references all18 existing context/check identifiers and existing evidence IDs. review_metrics.py records the permitted-report arithmetic; review_metrics.json retains all seed values, both error definitions, context scores and source report hashes. Source evidence anchors remain Thai Table1, Table2 and Results/Table4; Gallagher p696 DXA Equation1; and the full-cohort Thai BMI-threshold paragraph following Table1. No additional evidence retrieval occurred.
