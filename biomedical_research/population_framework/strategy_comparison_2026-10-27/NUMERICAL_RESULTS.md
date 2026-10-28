# Frozen framework-policy comparison: numerical results

All candidates were committed before this evaluation. These are exposed historical development cohorts; the check split is not fresh external confirmation.

TV and response-probability errors are on a 0–1 scale; lower is better. Weight quantile error is percentage points; waist quantile error is cm. Quantile MAE below is only a descriptive mean across the three prespecified quantiles and required strata; it was not a selection objective. Correlation error is absolute r difference.

## Historical check

| Case | Policy | Stage | Joint TV | Weight response error | Waist response error | Weight Q MAE | Waist Q MAE | Correlation error |
|---|---|---|---:|---:|---:|---:|---:|---:|
| fit_han | ordinary | initial | 0.0862 | 0.0862 | 0.0212 | 1.7997 | 1.1701 | 0.0006 |
| fit_han | ordinary | updated | 0.0646 | 0.0646 | 0.0204 | 0.3165 | 1.5999 | 0.1746 |
| fit_han | structured | initial | 0.0554 | 0.0507 | 0.0178 | 1.9149 | 1.0058 | 0.1682 |
| fit_han | structured | updated | 0.0775 | 0.0775 | 0.0175 | 0.4122 | 1.6425 | 0.1764 |
| exercise | ordinary | initial | 0.4418 | 0.4295 | 0.2648 | 3.9508 | 3.6431 | 0.2040 |
| exercise | ordinary | updated | 0.1499 | 0.0405 | 0.0725 | 1.2013 | 0.7968 | 0.2983 |
| exercise | structured | initial | 0.4917 | 0.4590 | 0.3014 | 4.2694 | 4.0838 | 0.7738 |
| exercise | structured | updated | 0.2382 | 0.0352 | 0.0865 | 1.2138 | 0.8799 | 0.5640 |

## Historical development

| Case | Policy | Stage | Joint TV | Weight response error | Waist response error | Weight Q MAE | Waist Q MAE | Correlation error |
|---|---|---|---:|---:|---:|---:|---:|---:|
| fit_han | ordinary | initial | 0.0868 | 0.0773 | 0.0619 | 1.6082 | 2.0828 | 0.0639 |
| fit_han | ordinary | updated | 0.0775 | 0.0735 | 0.0203 | 1.1526 | 0.6872 | 0.1113 |
| fit_han | structured | initial | 0.0906 | 0.0418 | 0.0585 | 1.7235 | 1.3906 | 0.1049 |
| fit_han | structured | updated | 0.0891 | 0.0864 | 0.0233 | 1.2123 | 0.7298 | 0.1131 |
| exercise | ordinary | initial | 0.3847 | 0.3847 | 0.1477 | 3.7166 | 3.1344 | 0.2466 |
| exercise | ordinary | updated | 0.1605 | 0.0326 | 0.1524 | 0.8761 | 1.6049 | 0.3410 |
| exercise | structured | initial | 0.4142 | 0.4142 | 0.1842 | 4.0352 | 3.4977 | 0.8164 |
| exercise | structured | updated | 0.2145 | 0.0232 | 0.1494 | 0.8122 | 1.5399 | 0.6066 |

## Paired check-participant bootstrap contrasts

Negative favors structured. Intervals condition on these fixed generators and do not include Agent, source-study or transport uncertainty.

| Case | Final structured − ordinary | 95% percentile interval | Difference in update changes | 95% percentile interval |
|---|---:|---|---:|---|
| fit_han | 0.0128 | [-0.0029, 0.0128] | 0.0437 | [-0.0222, 0.0554] |
| exercise | 0.0883 | [0.0131, 0.1055] | 0.0384 | [-0.0304, 0.0502] |
| equal_case_mean | 0.0506 | [0.0100, 0.0565] | 0.0411 | [-0.0088, 0.0435] |

## Final check strata and joint probabilities

Cell order: neither, weight only, waist only, both. Response definitions are weight change ≤ −5% and waist change ≤ −5 cm; these are analytic thresholds.

| Case | Policy | Stratum | Real N | Real probabilities | Generated probabilities | TV |
|---|---|---|---:|---|---|---:|
| fit_han | ordinary | female_pooled | 107 | 0.4393, 0.0935, 0.1869, 0.2804 | 0.4060, 0.1472, 0.1556, 0.2913 | 0.0646 |
| fit_han | structured | female_pooled | 107 | 0.4393, 0.0935, 0.1869, 0.2804 | 0.3943, 0.1559, 0.1544, 0.2954 | 0.0775 |
| exercise | ordinary | LVLI | 18 | 0.5000, 0.2222, 0.0000, 0.2778 | 0.3691, 0.1914, 0.1412, 0.2983 | 0.1617 |
| exercise | ordinary | HVLI | 16 | 0.2500, 0.0625, 0.0000, 0.6875 | 0.1976, 0.1707, 0.1316, 0.5001 | 0.2397 |
| exercise | ordinary | HVHI | 15 | 0.2667, 0.1333, 0.1333, 0.4667 | 0.2265, 0.1735, 0.1413, 0.4586 | 0.0482 |
| exercise | structured | LVLI | 18 | 0.5000, 0.2222, 0.0000, 0.2778 | 0.2987, 0.2453, 0.1964, 0.2596 | 0.2195 |
| exercise | structured | HVLI | 16 | 0.2500, 0.0625, 0.0000, 0.6875 | 0.1656, 0.2215, 0.1792, 0.4337 | 0.3382 |
| exercise | structured | HVHI | 15 | 0.2667, 0.1333, 0.1333, 0.4667 | 0.1886, 0.2183, 0.2054, 0.3877 | 0.1570 |

## Execution status

| Run | Status |
|---|---|
| fit_han/ordinary/initial | checks_passed |
| fit_han/ordinary/updated | checks_passed |
| fit_han/structured/initial | checks_passed |
| fit_han/structured/updated | checks_passed |
| exercise/ordinary/initial | checks_passed |
| exercise/ordinary/updated | checks_passed |
| exercise/structured/initial | checks_passed |
| exercise/structured/updated | checks_passed |

Full per-stratum quantiles, slopes, intercepts, residual SDs, both seed summaries, probabilities and provenance are in [metrics.json](evaluation/metrics.json). Every prespecified case/policy/stage is retained.

The two methods share evidence, submission count, target sampling N/seeds and execution code. Exact tokens and internal compute were not matched. One independent builder per case/policy cannot estimate Agent variability. This compares two generating-Agent procedures, not generation against a no-record Agent or classical estimation.
