# Direct-table self-consistency diagnostics, version 1

`cohort_harness.self_consistency` compares an Agent-authored enrichment table with an Agent-declared conditional construction. It is a deterministic checker, not a generator or a scientific model. It contains no biological coefficients, fits no model, calls no model API, executes no submitted code, changes no input, and emits no row-level table or residual vector.

This interface supports task-schema version 1 **enrichment** tasks only. Whole-cohort and completion tasks are explicitly rejected. One generated numeric outcome is selected per report; every column in the complete table is still checked against the task contract.

## Command and output

From the project root, using the configured Python environment:

```text
python -m cohort_harness.self_consistency --task TASK.json --observed observed.csv --generated generated.csv --spec candidates/NAME/audit/construction.json --output NEW_REPORT.json
```

All five arguments are mandatory. The report parent directory must exist. The output is created exclusively; an existing file is never overwritten. Successful calculation returns exit code 0 and a compact receipt on stdout. Rejected input returns exit code 2 with an error on stderr and no new diagnostic report. The Python entry point is:

```python
from cohort_harness.self_consistency import run_self_consistency
report = run_self_consistency(task_path, observed_path, generated_path, spec_path, output_path)
```

`validate_self_consistency_spec(task, spec)` validates an already parsed task and construction without reading tables. `run_self_consistency` additionally performs strict JSON/CSV parsing, preservation checks and realized-expression checks.

The controller should commit `audit/construction.json` **before rows are authored** and retain that separate commitment. The checker binds the bytes presented to it; it cannot establish chronology, authorship, independence or compliance with a prior commitment. It reports `authorship_or_prior_commitment: "not_verified"`. A controller can compare the report's specification hash with its earlier commitment. Store feedback outside a frozen candidate and preserve earlier reports when revising.

## Construction schema

Every object is strict: unknown or missing fields are rejected. The required fields are:

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1`; a Boolean is not a version |
| `interpretation` | `conditional_moments` or `working_guides` |
| `outcome` | A task-declared generated numeric or integer column |
| `numeric_predictors` | Unique observed numeric/integer column names; may be empty |
| `group_by` | Unique observed categorical column names; may be empty; at most 4,096 combinations of declared categories |
| `conditional_mean` | A supported expression |

The sole optional field is `conditional_sd`, also a supported expression. If supplied, it must evaluate to a finite, strictly positive value for every row. Omission means no SD or standardized-residual claim, not a default SD.

Under `conditional_moments`, `conditional_mean` asserts the conditional expected value E[Y|X]; `conditional_sd`, if supplied, asserts SD[Y|X]. Neither field denotes a regression standard error, a coefficient uncertainty, or a confidence interval. Under `working_guides`, those same fields designate a location guide and optional positive scale guide without asserting conditional population moments. The report echoes the interpretation and distinguishes those quantities in summary names. In both cases `residual` means the arithmetic difference Y minus the declared location; the word alone does not establish a probabilistic error model.

The scientific Agent chooses the expressions, coefficients, interpretation and supporting rationale. Evidence provenance and assumptions remain in the candidate's evidence/model/decision artifacts; this compact construction file does not replace them. There are no biological defaults or automatic choices of signs, groups, units, transformations or residual distributions. A construction must use units consistent with the outcome; the checker does not perform dimensional analysis.

### Expression grammar

| Expression | Calculation |
| --- | --- |
| `{"const": 2.5}` | Finite numeric constant; Booleans rejected |
| `{"column": "x"}` | A column listed in `numeric_predictors` |
| `{"lookup": {"column": "group", "values": [{"key": "a", "value": 0}, {"key": "b", "value": 3}]}}` | Constant lookup using an observed categorical column |
| `{"op": "add", "args": [EXPR, EXPR]}` | Addition |
| `{"op": "sub", "args": [EXPR, EXPR]}` | First minus second |
| `{"op": "mul", "args": [EXPR, EXPR]}` | Multiplication |
| `{"op": "div", "args": [EXPR, EXPR]}` | First divided by second |
| `{"op": "min", "args": [EXPR, EXPR]}` | Elementwise minimum |
| `{"op": "max", "args": [EXPR, EXPR]}` | Elementwise maximum |
| `{"op": "pow", "base": EXPR, "exponent": 2}` | Power with a finite constant exponent in [-8, 8] |

All six binary operators require exactly two operands. Nested expressions support centering, interactions and group-dependent locations/scales. The combined mean/SD expression budget is 1,024 nodes and maximum depth 32. Expressions are interpreted through a fixed operator dispatch, without `eval`, `exec`, imports, callbacks or formula strings. Division by zero, nonreal powers, overflow or missing realized values reject the calculation. Computation uses NumPy real floating-point arithmetic; this is not symbolic or arbitrary-precision algebra.

A lookup must include each task-declared category exactly once, even if a category has no observations. Values are finite numeric constants, not further expressions. There is no implicit reference group or fallback value. Keys retain their JSON string/numeric type; a string `"1"` differs from number `1`. The categorical column must have role `observed`; lookup membership in `group_by` is not required. Column expressions require declared observed numeric predictors. Identifiers and generated outcomes cannot be predictors, groups or lookup inputs.

### Entirely invented arithmetic example

Suppose a task declares identifier `key`, observed numeric `x` and `w`, observed categorical `group` with categories `["a", "b", "c"]`, and generated numeric `y`. These variable names, values and coefficients describe software fixtures, not a biological model.

```json
{
  "schema_version": 1,
  "interpretation": "conditional_moments",
  "outcome": "y",
  "numeric_predictors": ["x", "w"],
  "group_by": ["group"],
  "conditional_mean": {
    "op": "add",
    "args": [
      {
        "op": "add",
        "args": [
          {"const": 10},
          {"op": "mul", "args": [{"const": 2}, {"column": "x"}]}
        ]
      },
      {
        "lookup": {
          "column": "group",
          "values": [
            {"key": "a", "value": 0},
            {"key": "b", "value": 3},
            {"key": "c", "value": -3}
          ]
        }
      }
    ]
  },
  "conditional_sd": {"const": 2}
}
```

For invented inputs `x = [0, 1, 2, 3]`, `w = [0, 2, 4, 6]`, `group = [a, a, b, b]`, the location vector is `[10, 12, 17, 19]`. An authored outcome vector `[11, 10, 20, 19]` has deviations `[1, -2, 3, 0]`, mean 0.5, sample SD sqrt(13/3), and RMSE sqrt(3.5). Standardized deviations have mean 0.25. These nonzero sample means do not produce a failed check. The numeric predictor design is rank deficient because `w = 2*x`. The report itself does not reproduce those row vectors.

## Table representation and preservation

The existing `contracts.validate_output` task checks apply: exact column order, row count, types, bounds, categories, unique nonmissing identifiers, original row order, and unchanged observed values. Additionally, every identifier/observed CSV cell must be **identical after CSV decoding** between input and authored output. Changing an observed numeric cell from `1` to `1.0` is rejected even though the values compare numerically equal. Copy observed cell text without reformatting it. CSV quoting and line-ending differences alone do not alter decoded cell text; the file hash nevertheless binds the actual bytes.

CSV input is UTF-8 (an optional BOM is accepted), with a header and exactly the task's row count. Ragged rows and unexpected columns are rejected. The observed table contains all and only nongenerated task columns; the authored table contains every task column. Strings such as `NA` are literal strings rather than automatically inferred missing values. An empty CSV cell represents missingness only when the column permits it. Empty nonnullable strings and blank category labels are unsupported. Numeric underflow to zero and nonfinite numeric input are rejected. Categorical CSV tokens must equal the textual form of a declared category; colliding textual category representations are rejected.

Missing values are unsupported in declared numeric diagnostics, declared groups and realized lookup inputs. Other observed columns can retain task-permitted missing values. The checker never substitutes or imputes inputs.

## Reading the report

The report contains SHA-256 hashes and byte counts for the exact task, observed table, authored table and construction bytes that were parsed. It also records hashes of this checker and its imported contract module plus Python, NumPy and pandas versions. Hashes provide byte linkage rather than evidence-quality or execution-environment attestation. No timestamp or output-path-dependent payload is added, so unchanged inputs and implementation/runtime produce the same report bytes.

Diagnostics include:

- Overall and per-declared-category counts, finite status, arithmetic mean, sample SD using n-1, RMSE from zero, and linear-interpolated quantiles at 0, .01, .05, .5, .95, .99 and 1 for outcome, location, deviation and optional scale/standardized deviation. `groups` contains marginal summaries for each `group_by` column. `joint_groups` additionally contains every combination in the Cartesian product of task-declared categories, along with declared/observed/empty group counts. Empty combinations remain explicit. With no `group_by` columns the joint status is `not_requested` and those counts are zero. Joint deviations can remain substantial when marginal deviations cancel.
- Pearson and Spearman correlations of deviations with every declared numeric predictor, and analogous standardized correlations when a scale is supplied. Spearman uses average ranks for ties. No p-values or fitted slopes are produced.
- Rank of the intercept plus the centered/scaled declared numeric predictors, its SVD tolerance, constant-predictor names, and `full_column_rank` or `rank_deficient` status. This describes that numeric design, not all nonlinear expressions or categorical contrasts in the construction.
- Outcome duplicate counts and largest multiplicity; counts of absolute standardized deviations strictly greater than 1, 2 and 3 when applicable. Tail counts imply no normal-distribution reference.

Sample SD is null for fewer than two values; an unrepresentable SD is null with `numeric_overflow`. Empty declared categories remain visible with `empty_group`. Correlations are null with explicit status for too few values, constant vectors or numerically unresolved variation. These diagnostic statuses do not constitute rejection of an otherwise valid table. Aggregate summaries can describe a group containing only one row; the interface promises no row-level output, not a privacy transformation.

`status: "computed"` means the supported calculation completed. `table_contract: "valid"` concerns representation and preservation. `scientific_validity: "not_assessed"` always remains explicit. The report has no scientific pass/fail threshold and no instruction to force residual means or correlations to zero. It cannot establish a realistic joint distribution, valid conditional moments, transportability, causal effects, authorship or independent target performance. A direct table can agree with its own declared guide while remaining scientifically inadequate.

`tests/test_self_consistency.py` exercises known invented arithmetic, safe-expression boundaries, preservation, undefined diagnostics, determinism, hash binding and exclusive report creation. No prior candidate results or biomedical raw data are needed to run these tests.
