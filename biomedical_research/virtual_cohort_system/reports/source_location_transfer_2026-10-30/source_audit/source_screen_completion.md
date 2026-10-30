# M11 source-only screen completion

Verified 36 isolated source generator executions in 24 replay reports; no source execution failures. All eight candidates are frozen/verified. Evidence bytes match across every candidate; generator bytes match within each family. No target tables or evaluator results were read.

| Family | Scenario | Sex | Location offset | Initial median | Calibrated median | IQR | Mean replay age slope |
|---|---|---|---:|---:|---:|---:|---:|
| ha | primary | male | -0.074802 | 5.374802 | 5.300000 | 0.738395 | 0.015335 |
| ha | primary | female | -0.076377 | 5.276377 | 5.200000 | 0.708125 | 0.018963 |
| ha | alt1 | male | -0.079975 | 5.379975 | 5.300000 | 0.756755 | 0.015259 |
| ha | alt1 | female | -0.081766 | 5.281766 | 5.200000 | 0.732834 | 0.018937 |
| ha | alt2 | male | -0.081115 | 5.381115 | 5.300000 | 0.757129 | 0.015294 |
| ha | alt2 | female | -0.082994 | 5.282994 | 5.200000 | 0.733502 | 0.018969 |
| hb | primary | male | -0.083985 | 5.383985 | 5.300000 | 0.735718 | 0.015336 |
| hb | primary | female | -0.084899 | 5.284899 | 5.200000 | 0.773459 | 0.018946 |
| hb | alt1 | male | -0.090415 | 5.390415 | 5.300000 | 0.757676 | 0.015253 |
| hb | alt1 | female | -0.090969 | 5.290969 | 5.200000 | 0.798591 | 0.018899 |
| hb | alt2 | male | -0.093909 | 5.393909 | 5.300000 | 0.759579 | 0.015251 |
| hb | alt2 | female | -0.094050 | 5.294050 | 5.200000 | 0.800135 | 0.018895 |

Maximum absolute calibrated pooled-median discrepancy is 8.88e-16 percentage points. Maximum pooled IQR change is 8.88e-16; maximum per-seed age-slope change is 6.25e-17 percentage points/year.

The source-reference IQR is 0.8 for each sex. Reference age slopes are 0.0153 (men) and 0.0191 (women) percentage points/year. Individual quartile/age discrepancies and every seed remain in source_screen_summary.json. Locations were calibrated to medians; neither IQRs nor slopes were refitted. Exact median agreement is expected from the fixed additive correction and reused source seeds. It provides no independent target validation.

Source plan SHA256: `c88d0bc1cf4d334831139d19dcb6da5769f9e9c626ac482828bc10fc9600f548`

Source support and selection remain approximate: raw baseline n=4420 age bins are used for the n=4402 HbA1c analysis sample; open >=70 compressed to 70-79; pooled BMI used within each sex; dependence and tails assumed. Grossmann moments are unfitted context diagnostics. The initial pooled-age quartiles 40/52/65 differ from Masuch 40/53/64 and were retained.

Controller review: fixed-plan hash guards were added; all candidate plan copies and audit plan hash matched before target phase. New replay reports are verified inside run_source_replay (its return calls verify_source_replay); calibration also verifies initial reports explicitly. An extra source-rank assertion initially treated clipped ties as strict ordering; corrected before any freeze to allow tied values, then all source-X invariants passed. No scientific candidate parameter changed because of that preparation check.
