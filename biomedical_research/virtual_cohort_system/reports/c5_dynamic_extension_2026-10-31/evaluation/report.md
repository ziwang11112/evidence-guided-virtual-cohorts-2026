# C5 artificial dynamic-variable-extension evaluation

This evaluates one invented, fully specified Gaussian example. It is an implementation and mechanism sanity check, not biomedical validation, a new conditional-probability theory, or method superiority.

All nine scheduled outputs were committed and their hashes verified before analytical answers and tables were read. All declared endpoints are retained. Monte Carlo discrepancies are descriptive; no clinical or numerical closeness threshold was invented.

Structural checks passed for all tables: **True**.
Exact parsed original-cell preservation for all extensions: **True**.

## Analytical references

| Endpoint | Population answer |
|---|---:|
| A1_slope_x1 | 0.75 |
| A1_intercept | -16 |
| A2_slope_x1 | -1.362591432 |
| A2_slope_x2 | 0.9278996865 |
| A2_intercept | 62.84639498 |
| A3_residual_variance | 42.8338558 |
| A3_residual_sd | 6.544757887 |

## Prespecified per-run endpoint estimates

| Run | Endpoint | Estimate | Reference | Signed deviation |
|---|---|---:|---:|---:|
| parent_r1 | A1_slope_x1 | 0.75459892 | 0.75 | 0.00459892 |
| parent_r1 | A1_intercept | -16.220817 | -16 | -0.220817 |
| parent_r2 | A1_slope_x1 | 0.72568747 | 0.75 | -0.0243125 |
| parent_r2 | A1_intercept | -15.592279 | -16 | 0.407721 |
| parent_r3 | A1_slope_x1 | 0.77714466 | 0.75 | 0.0271447 |
| parent_r3 | A1_intercept | -16.08414 | -16 | -0.0841399 |
| joint_r1 | A1_slope_x1 | 0.78348544 | 0.75 | 0.0334854 |
| joint_r1 | A1_intercept | -16.495719 | -16 | -0.495719 |
| joint_r1 | A2_intercept | 63.281671 | 62.846395 | 0.435276 |
| joint_r1 | A2_slope_x1 | -1.3943572 | -1.3625914 | -0.0317658 |
| joint_r1 | A2_slope_x2 | 0.93563582 | 0.92789969 | 0.00773613 |
| joint_r1 | A3_residual_variance | 43.528214 | 42.833856 | 0.694358 |
| joint_r1 | A3_residual_sd | 6.5975915 | 6.5447579 | 0.0528336 |
| joint_r2 | A1_slope_x1 | 0.70236653 | 0.75 | -0.0476335 |
| joint_r2 | A1_intercept | -15.378493 | -16 | 0.621507 |
| joint_r2 | A2_intercept | 64.235417 | 62.846395 | 1.38902 |
| joint_r2 | A2_slope_x1 | -1.4563294 | -1.3625914 | -0.093738 |
| joint_r2 | A2_slope_x2 | 0.92113222 | 0.92789969 | -0.00676746 |
| joint_r2 | A3_residual_variance | 41.179448 | 42.833856 | -1.65441 |
| joint_r2 | A3_residual_sd | 6.4171214 | 6.5447579 | -0.127636 |
| joint_r3 | A1_slope_x1 | 0.78944162 | 0.75 | 0.0394416 |
| joint_r3 | A1_intercept | -16.43432 | -16 | -0.43432 |
| joint_r3 | A2_intercept | 62.894533 | 62.846395 | 0.048138 |
| joint_r3 | A2_slope_x1 | -1.3290416 | -1.3625914 | 0.0335498 |
| joint_r3 | A2_slope_x2 | 0.98936545 | 0.92789969 | 0.0614658 |
| joint_r3 | A3_residual_variance | 42.618472 | 42.833856 | -0.215384 |
| joint_r3 | A3_residual_sd | 6.5282824 | 6.5447579 | -0.0164755 |
| extended_r1 | A1_slope_x1 | 0.75459892 | 0.75 | 0.00459892 |
| extended_r1 | A1_intercept | -16.220817 | -16 | -0.220817 |
| extended_r1 | A2_intercept | 61.294554 | 62.846395 | -1.55184 |
| extended_r1 | A2_slope_x1 | -1.2620057 | -1.3625914 | 0.100586 |
| extended_r1 | A2_slope_x2 | 0.88440757 | 0.92789969 | -0.0434921 |
| extended_r1 | A3_residual_variance | 44.960321 | 42.833856 | 2.12647 |
| extended_r1 | A3_residual_sd | 6.7052458 | 6.5447579 | 0.160488 |
| extended_r2 | A1_slope_x1 | 0.72568747 | 0.75 | -0.0243125 |
| extended_r2 | A1_intercept | -15.592279 | -16 | 0.407721 |
| extended_r2 | A2_intercept | 62.314396 | 62.846395 | -0.531999 |
| extended_r2 | A2_slope_x1 | -1.3600511 | -1.3625914 | 0.00254028 |
| extended_r2 | A2_slope_x2 | 0.86295275 | 0.92789969 | -0.0649469 |
| extended_r2 | A3_residual_variance | 42.701288 | 42.833856 | -0.132568 |
| extended_r2 | A3_residual_sd | 6.5346223 | 6.5447579 | -0.0101356 |
| extended_r3 | A1_slope_x1 | 0.77714466 | 0.75 | 0.0271447 |
| extended_r3 | A1_intercept | -16.08414 | -16 | -0.0841399 |
| extended_r3 | A2_intercept | 62.399222 | 62.846395 | -0.447173 |
| extended_r3 | A2_slope_x1 | -1.3225212 | -1.3625914 | 0.0400703 |
| extended_r3 | A2_slope_x2 | 0.926483 | 0.92789969 | -0.00141668 |
| extended_r3 | A3_residual_variance | 44.355964 | 42.833856 | 1.52211 |
| extended_r3 | A3_residual_sd | 6.6600273 | 6.5447579 | 0.115269 |

## Old-cell preservation

| Extension | Parent | Parsed cells exact | Printed tokens exact | Maximum absolute x1/x2 difference |
|---|---|---|---|---:|
| extended_r1 | parent_r1 | True | True | 0.0 |
| extended_r2 | parent_r2 | True | True | 0.0 |
| extended_r3 | parent_r3 | True | True | 0.0 |

## Interpretation and complete diagnostics

Each extension shares every old variable and row with its parent. Joint draws are separate draws; matching replicate numbers are only bookkeeping. The three seeds per arm are Monte Carlo draws from one specified model and source construction, not independent scientific evidence. A single fresh author supplies the three programs, so differences cannot establish an author or algorithm effect.

The accompanying evaluation.json records all source moments, correlations, quantiles, conditional residual checks, per-arm means, between-seed sample SDs, ranges, deviations, and every prespecified joint-minus-extension endpoint difference. Failed structure or analysis is retained explicitly. No output is rejected for a numerical result and no source or generator is revised from these results.

A successful result supports reuse and compatible variable extension for this artificial fixture only. It does not establish transport to real populations, real unmeasured-variable recovery, calibration under uncertain evidence, causal validity, or a general advantage over one-shot generation.
