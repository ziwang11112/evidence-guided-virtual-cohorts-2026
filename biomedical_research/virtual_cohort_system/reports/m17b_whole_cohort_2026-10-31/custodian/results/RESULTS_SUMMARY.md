# M17-B custody evaluation: locked result

31 October 2026. The locked evaluator ran once after the explicit root final-output release. All 12 scheduled initial/final entries completed; none failed. These entries represent six unique generated tables from two constructions and three fixed analytical seeds. Both constructions retained their models, so the initial and final entries reuse exactly the same table for each seed and give identical results. They are not 12 independent tables or 12 experiments.

Every reference and generated table has 320 rows and exactly 40 rows in each of the eight prescribed sex-by-age cells. No target resampling, model change, target-feedback iteration, or analysis omission occurred.

## All eight locked endpoints

Ranges below span the three scheduled analytical realizations of each construction. They are realization ranges, not confidence or calibrated model-uncertainty intervals. Reference intervals use normal HC3 standard errors for the selected sample and specified regression; they are not NHANES complex-survey intervals.

| Endpoint | Reference estimate | Reference HC3 SE | Reference 95% interval | B1 realization range | B2 realization range |
|---|---:|---:|---|---|---|
| Adjusted BMI, mg/dL per 5 kg/m² | 0.2722 | 0.0461 | [0.1819, 0.3625] | [0.3083, 0.4684] | [0.2561, 0.3266] |
| Adjusted age, mg/dL per decade | 0.1485 | 0.0403 | [0.0694, 0.2275] | [0.1430, 0.2098] | [0.1613, 0.1799] |
| Adjusted female−male contrast, mg/dL | -1.2817 | 0.1368 | [-1.5498, -1.0136] | [-1.5712, -1.3330] | [-1.4950, -1.2288] |
| BMI curvature contrast, mg/dL | -0.0391 | 0.0447 | [-0.1267, 0.0485] | [-0.1962, -0.1044] | [-0.0168, 0.0068] |
| Female−male BMI slope difference | -0.0004 | 0.1011 | [-0.1985, 0.1977] | [-0.1899, 0.1179] | [-0.0712, 0.0823] |
| Male BMI slope | 0.2724 | 0.0841 | [0.1077, 0.4372] | [0.2397, 0.5836] | [0.2515, 0.3392] |
| Female BMI slope | 0.2721 | 0.0558 | [0.1627, 0.3815] | [0.3576, 0.3938] | [0.2588, 0.3631] |
| Reverse urate slope, kg/m² per mg/dL | 1.5277 | 0.3470 | [0.8475, 2.2078] | [1.3031, 1.8735] | [0.9768, 1.3951] |

| Endpoint | B1 generated−reference difference range | B2 generated−reference difference range |
|---|---|---|
| Adjusted BMI, mg/dL per 5 kg/m² | [0.0361, 0.1963] | [-0.0161, 0.0545] |
| Adjusted age, mg/dL per decade | [-0.0055, 0.0613] | [0.0128, 0.0314] |
| Adjusted female−male contrast, mg/dL | [-0.2895, -0.0514] | [-0.2133, 0.0529] |
| BMI curvature contrast, mg/dL | [-0.1571, -0.0653] | [0.0223, 0.0459] |
| Female−male BMI slope difference | [-0.1895, 0.1183] | [-0.0708, 0.0827] |
| Male BMI slope | [-0.0328, 0.3112] | [-0.0209, 0.0667] |
| Female BMI slope | [0.0855, 0.1217] | [-0.0132, 0.0910] |
| Reverse urate slope, kg/m² per mg/dL | [-0.2246, 0.3458] | [-0.5508, -0.1326] |

The positive adjusted BMI and age directions, negative adjusted sex contrast, positive sex-specific BMI slopes, and positive reverse association occur in all six unique generated tables and the reference. B1 has a systematically larger adjusted BMI estimate than the reference; B2 is closer for this quantity across these three draws. B2 systematically understates the reverse-association magnitude. Curvature and interaction reference intervals span zero, so their point signs do not establish reliable directions. No composite success threshold is inferred.

## Supporting diagnostics

Each range uses only the three final-stage entries for that builder, avoiding duplicate initial/final counts. SD uses ddof=1; quantiles use linear interpolation. Full precision and every per-table value are retained in evaluation.json.

| Variable / group / statistic | Reference | B1 range | B2 range |
|---|---:|---|---|
| bmi / overall / mean | 29.1824 | [27.1370, 27.7796] | [27.2684, 27.7188] |
| bmi / overall / sd | 6.6908 | [5.7540, 6.2309] | [5.7181, 6.0016] |
| bmi / overall / p10 | 21.7620 | [19.5046, 20.6452] | [20.7299, 20.9818] |
| bmi / overall / p50 | 28.0750 | [26.3925, 27.1013] | [26.3123, 26.9955] |
| bmi / overall / p90 | 37.7320 | [34.9876, 36.6323] | [35.1022, 35.4336] |
| urate / overall / mean | 5.5809 | [5.4148, 5.5067] | [5.4083, 5.4695] |
| urate / overall / sd | 1.4269 | [1.5078, 1.5571] | [1.4475, 1.5673] |
| urate / overall / p10 | 3.7000 | [3.5019, 3.6850] | [3.5111, 3.6503] |
| urate / overall / p50 | 5.6000 | [5.2433, 5.4042] | [5.2052, 5.3672] |
| urate / overall / p90 | 7.4000 | [7.2482, 7.4484] | [7.3323, 7.5635] |
| bmi / male / mean | 28.7544 | [27.1714, 27.9170] | [27.3206, 28.2239] |
| bmi / male / sd | 5.0463 | [5.1160, 5.6559] | [5.2040, 5.3989] |
| bmi / male / p10 | 22.5070 | [21.1362, 21.1879] | [20.9763, 21.8392] |
| bmi / male / p50 | 28.2600 | [26.8100, 27.6430] | [26.4182, 27.8740] |
| bmi / male / p90 | 35.9040 | [33.6811, 35.4052] | [34.3854, 34.8293] |
| urate / male / mean | 6.1937 | [6.1178, 6.2858] | [6.0561, 6.2369] |
| urate / male / sd | 1.2247 | [1.3221, 1.3971] | [1.2772, 1.3973] |
| urate / male / p10 | 4.7000 | [4.5059, 4.7524] | [4.5034, 4.6560] |
| urate / male / p50 | 6.1000 | [5.9003, 6.1147] | [5.8497, 6.0489] |
| urate / male / p90 | 7.7100 | [7.9017, 8.1514] | [7.7414, 8.2527] |
| bmi / female / mean | 29.6104 | [26.8146, 27.8682] | [27.2137, 27.6010] |
| bmi / female / sd | 7.9989 | [6.3443, 6.7302] | [6.0370, 6.6836] |
| bmi / female / p10 | 21.2830 | [19.0729, 20.1034] | [19.5720, 20.9818] |
| bmi / female / p50 | 27.6350 | [25.4564, 27.1342] | [26.0098, 26.3385] |
| bmi / female / p90 | 39.8000 | [35.3762, 37.4407] | [35.3528, 36.2223] |
| urate / female / mean | 4.9681 | [4.6860, 4.7276] | [4.7021, 4.8244] |
| urate / female / sd | 1.3526 | [1.2169, 1.3765] | [1.2618, 1.4639] |
| urate / female / p10 | 3.4000 | [3.0957, 3.3100] | [3.0798, 3.2618] |
| urate / female / p50 | 4.9000 | [4.4233, 4.6339] | [4.4719, 4.6248] |
| urate / female / p90 | 6.4100 | [6.4005, 6.5582] | [6.4108, 6.8600] |
| Pearson age__bmi | 0.0459 | [-0.1093, 0.0393] | [-0.1828, -0.0246] |
| Pearson bmi__urate | 0.2347 | [0.2180, 0.3562] | [0.2032, 0.2467] |

All six generated tables understate overall mean BMI and female mean BMI and SD. All six also understate mean urate overall; sex-specific mean differences and dispersion are retained above rather than reduced to a single fidelity score.

## Scope and closure

This is one temporal validation case within the NHANES survey family, using an explicitly standardized quota cohort. The results do not estimate national prevalence, establish equivalence or biological transport, demonstrate calibrated uncertainty, or show feedback-driven improvement. Endpoint exposure was classified before unblinding in ENDPOINT_EXPOSURE.md; source-supplied and assumption-encoded relationships remain transfer/assumption tests rather than independent discoveries.

The target is now exposed and closed to further tuning or fresh-confirmation reuse. Preserve the mixed results. Any next scientific test requires a separate protocol and an unopened reference; this custody evaluation starts no new task.

## Machine-readable record

- evaluation.json: all reference and generated fits, HC3 intervals, quotas, diagnostics, and empty failure list.
- comparisons.csv: 96 scheduled endpoint records (12 stage entries × 8 endpoints); only 48 correspond to unique generated-table endpoint combinations.
- realization_ranges.csv: 32 builder/stage/endpoint records; initial and final ranges are identical under retention.
- post_evaluation_integrity.json: input bindings, unique-table counts, and output hashes.
