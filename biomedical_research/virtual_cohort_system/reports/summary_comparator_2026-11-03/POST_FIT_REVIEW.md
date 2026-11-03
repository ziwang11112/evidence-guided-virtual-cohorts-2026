# Independent post-fit gate

Decision: **PASS**. 142 checks; 0 failures.

FIT SHA256: `9eabdd459aad112d0577a59de11e5013d8076b0eb8a9ee0b7afe35f06b57773a`.

The stored fitted law and released inputs/code were independently checked before final generation. No optimizer, sampler, patient table or quadrature routine was executed.

- Marginal CDFs are normalized and strictly monotone; their actual sampler probabilities are positive. The integer age support is 35–74, continuous supports are positive and bounded, and Bernoulli sex probability is valid. All marginal moments therefore exist under this declared law.
- Mean, SD and quantile constraints were recomputed from CDF masses and exact uniform-cell moments. All fitted standardized marginal equations satisfy the 1e-6 gate. Female SD remains a redundant sample-versus-population diagnostic.
- All three stored covariance matrices are finite, symmetric and positive definite. SVD projection calculations reproduce the separate adjusted coefficients. Analytical Spearman and covariance-derived Pearson checks pass.
- Exactly three glycemic and three covariate starts match the released allocation, with all nfev within limits and counters reconciled. The selected parameters match the declared cost/tie-selection rule.
- Both 128→256 and 256→512 integration comparisons pass their fixed native-unit tolerances. This review recomputes their arithmetic, not independent quadrature integrals.

## Retained residuals at the final 512-node diagnostic

| Quantity | Generated-law minus supplied target |
|---|---:|
| E1 | 7.88581066456e-06 |
| E2 | 0.00051742933328 |
| E3 | 1.03633929431e-05 |
| pearson | 0.000876693289512 |
| spearman | 2.22044604925e-16 |

These are calibration residuals, not performance on unseen outcomes. Passing permits the three fixed final draws; it does not certify biological truth, clinical interchangeability or superiority. No model changes or additional optimization are permitted by this gate.
