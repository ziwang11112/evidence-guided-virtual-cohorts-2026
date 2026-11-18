# Independent generated-table audit

Status: **passed**. All **93 of 93** scheduled endpoint comparisons matched: three primary estimates and 28 existing diagnostics for each of seeds 5301, 5302, and 5303. Primary model ranks also matched. No audit failures or numerical mismatches occurred.

The audit ran once after all three new isolated executions, closure, and completed evaluation. It verified the frozen candidate commitments, execution/receipt/table hashes, closure, and evaluation output binding before reading only the three new generated tables. It repeated binding verification after the calculation. It did not execute a generator, call/import the main provider or analytical engine, read old generated or patient rows, or open the actual cached target-results file. Embedded reference fields in the evaluation report were not used or emitted.

Independent calculations used QR/triangular solution for weighted least squares, equal weight for each of the eight demographic strata, compensated inverse-CDF quantiles, and `math.fsum` moments. Comparison tolerances were fixed beforehand at absolute and relative tolerance 1e-10; quantiles required exact equality. Each table had 3,000 rows with 375 rows per demographic stratum.

| Seed | Matched endpoints | Full/reduced rank | Full-model residual RMS (%) | Conditional BMI RMS (kg/m²) | Conditional glucose RMS (mg/dL) |
| --- | ---: | --- | ---: | ---: | ---: |
| 5301 | 31/31 | 5/4 | 0.1979562320 | 3.653575014 | 6.952642389 |
| 5302 | 31/31 | 5/4 | 0.1983834032 | 3.651636249 | 6.946770822 |
| 5303 | 31/31 | 5/4 | 0.1938540715 | 3.661894966 | 7.045439912 |

Conditional BMI RMS adjusts for age, sex, and glucose; conditional glucose RMS adjusts for age, sex, and BMI. These additional diagnostics describe generated-table conditional variation and were not compared with a new target endpoint. The full weighted design condition numbers were 4.1280, 4.1242, and 4.1632, respectively; singular values and rank cutoffs are retained in the machine-readable results.

Command: `python -B independent_numeric_audit.py`. Exit code: 0. Output summary: `passed`, three matched slots. Detailed endpoint differences, ranks, hashes, and diagnostic values are retained in `independent_audit/RESULTS.json`, with its hash in `independent_audit/COMPLETED.json`. This audit establishes numerical agreement and artifact identity for these outputs; it does not establish source-unit correctness, transport validity, or target-population truth.
