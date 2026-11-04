# Independent numerical review

Status: **pass_initial_pending_final_closure**.

Scope: four prespecified initial generated tables (trial 7400; deliveries 7401–7403), 3,000 rows each. No generator was executed, and no patient file or historical target reference was opened. Final author closure and reference comparison remain pending.

Regression coefficients and HC3 covariance were independently recomputed using QR decomposition. 95% intervals use the Student-t critical value with n − p residual degrees of freedom. An additional statsmodels OLS/HC3 check was performed. Marginal SD uses n − 1; quantiles use linear interpolation; Pearson and tie-aware Spearman correlations were recomputed with SciPy.

| Seed | Stage | Artifact checks | Diagnostic checks | Statsmodels checks | Largest diagnostic absolute difference |
|---:|---|---|---|---|---:|
| 7400 | initial_trial | pass | pass (89 numeric) | pass | 5.33e-15 |
| 7401 | initial_delivery | pass | pass (89 numeric) | pass | 8.44e-15 |
| 7402 | initial_delivery | pass | pass (89 numeric) | pass | 4.44e-15 |
| 7403 | initial_delivery | pass | pass (89 numeric) | pass | 2.22e-15 |

All declared output quality flags were recomputed. Checks additionally cover identifier uniqueness, missing cells, integer age/sex values, column order and row count. Every recorded execution-file hash, candidate/input binding, prescribed seed, session result, feedback hash and diagnostic hash was verified. The harness verifier was invoked only in verification mode.

| Seed | Analysis | BMI slope | HC3 95% interval |
|---:|---|---:|---|
| 7400 | primary | 0.012538169 | [0.001767711, 0.023308627] |
| 7400 | descriptive_secondary | 0.042763626 | [0.030514981, 0.055012270] |
| 7401 | primary | 0.018107000 | [0.006213495, 0.030000504] |
| 7401 | descriptive_secondary | 0.051758392 | [0.039154455, 0.064362329] |
| 7402 | primary | 0.003803464 | [-0.007993795, 0.015600723] |
| 7402 | descriptive_secondary | 0.042167633 | [0.029771297, 0.054563968] |
| 7403 | primary | 0.007869772 | [-0.003585366, 0.019324910] |
| 7403 | descriptive_secondary | 0.044723381 | [0.031783702, 0.057663060] |

The JSON companion retains every coefficient, standard error, interval, covariance element, marginal summary, all ten pairwise Pearson/Spearman relationships, quality flag and check outcome. These are conditional summaries of the synthetic draws, not evidence of target validity or uncertainty about sources, model structure, transport or patients.
