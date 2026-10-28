# Declarative source statistics

Source checks calculate statistics from a declared table. Execution-backed source replay uses the same operators on verified generator output. Neither route validates source-population assumptions or target scientific utility. Definitions below add to schema version 1 without changing existing operator meanings; `correlation` continues to mean Pearson correlation.

Every operator requires `kind`, a nonempty `unit`, `selection` (a list of declared filters), and `missing_policy` (`error` or `complete_cases`). Additional fields must match the chosen kind exactly. Numeric variables must already be numeric, finite and non-boolean. There is no implicit encoding or transformation.

| Kind | Additional operator fields | Supported definition |
|---|---|---|
| `mean` | `column` | Arithmetic mean |
| `sd` | `column` | Sample standard deviation, `ddof=1` |
| `median` | `column`, `method: "linear"` | Linear sample quantile at probability 0.5; average of the two middle values for even sample sizes |
| `quantile` | `column`, `q`, `method: "linear"` | Linear sample quantile at finite probability `0 <= q <= 1` |
| `correlation` | `x`, `y` | Pearson correlation of two distinct numeric variables |
| `spearman_correlation` | `x`, `y` | Pearson correlation of ascending average ranks of two distinct numeric variables; unit must be `"1"` |
| `ols_coefficient` | `outcome`, `predictors`, `term`, `include_intercept` | OLS coefficient with the declared intercept and numeric, full-rank design; residual degrees of freedom required |
| `proportion` | `event` | Fraction or percentage satisfying the declared event; unit `"1"` or `"%"` |

## Quantile definition and evidence

For sorted values `x[0], ..., x[n-1]`, linear interpolation sets `h = (n-1)*q`, `j = floor(h)` and `g = h-j`. The result is `(1-g)*x[j] + g*x[j+1]`, with the final endpoint equal to `x[n-1]`. This is NumPy's explicit `method="linear"` convention (Hyndman–Fan type 7). A singleton has the same quantile for every allowed probability. Empty complete selections are not computable.

For example, `[0,4,8,20]` has lower quartile 3, median 6 and upper quartile 11 under this convention. A published quartile must retain its reported value; these examples do not justify converting other conventions into this one.

Evidence of kind `median` requires `method: "linear"` or `method: "not_reported"`. Evidence of kind `quantile` requires the same `method` field and an explicit finite `q` in `[0,1]`. All ordinary evidence fields remain required. `q` is not permitted on median evidence, and `q`/`method` are not permitted on unrelated evidence kinds. Only mark the evidence method `linear` when supported by the source or its documented derivation; do not infer it merely because the operator implements it.

An operator always declares `method: "linear"`. If the source method is `not_reported`, the check must be `approximate` and name an existing assumption explaining the convention. For replay, that assumption can be at the context or check level. A probability mismatch between evidence and operator is rejected even for an approximate check. Unsupported known conventions can remain `reported_other` evidence with their original `statistic_name` and a `not_computable` source-check entry.

Median operator example:

```json
{"kind": "median", "unit": "y_unit", "selection": [], "missing_policy": "error", "column": "y", "method": "linear"}
```

Upper-quartile operator example (matching evidence must have `kind: "quantile"`, `q: 0.75` and its explicit source method):

```json
{"kind": "quantile", "unit": "y_unit", "selection": [], "missing_policy": "error", "column": "y", "q": 0.75, "method": "linear"}
```

## Spearman definition

`spearman_correlation` evidence is distinct from `correlation`. Its estimate must be finite and within `[-1,1]`, and its unit must be `"1"`. It does not accept a tie-method override. Both variables are ranked after applying selection and any explicitly allowed complete-pair deletion. Equal values receive their average ascending rank. The result is Pearson correlation of these rank vectors; the no-ties rank-difference shortcut is not used. Fewer than two complete pairs, or either constant rank vector, is not computable.

```json
{"kind": "spearman_correlation", "unit": "1", "selection": [], "missing_policy": "error", "x": "x", "y": "y"}
```

This is unadjusted, unweighted sample Spearman correlation. Partial rank correlation, survey weighting, confidence intervals and p-values are not supplied. A Pearson estimate cannot be relabelled as Spearman for checking. Existing variable/adjustment mapping checks still require explicit approximation assumptions for mismatches; they do not establish substantive measurement equivalence.

## Reporting and verification

All operators apply selection before missing-value checks. `error` rejects missing operator values; `complete_cases` drops rows missing any required operator variable and records their count. Nonfinite numeric values are errors rather than missing values. Successful results retain input, selected, used and dropped-row counts. Source checks retain `generation_link_verified: false`; successful verified replay can attach `true` to the same statistics. A mathematically undefined statistic is retained as `not_computable`, including an explanation, without inventing a numeric value or discrepancy.

The tests use hand-calculated invented values for odd/even medians, linear interpolation, tied ranks and missing pairs. Replay tests use a mocked execution backend to check linkage, pre-execution definition rejection and recomputation/tamper detection; they do not establish process isolation or scientific validity.

New replay reports use schema version 2 and bind both `engine_sha256` (replay implementation) and `operator_engine_sha256` (statistic implementation). Replay recipes and ordinary source-check reports remain schema version 1. Version-1 historical replay reports require the recorded M3 code version; current verification rejects them explicitly. Changes to either implementation invalidate current-version replay verification unless its recorded engine version is restored. Historical frozen candidates and reports must not be rewritten to claim current verification.
