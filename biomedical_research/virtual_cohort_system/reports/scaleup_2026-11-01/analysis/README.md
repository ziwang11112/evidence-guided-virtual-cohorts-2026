# K02 prospective in-memory analysis

This additive module implements arithmetic for the three existing K02 estimands.
It is a **prospective draft**, not scientific admission, an access-control gate,
a case/global freeze, a target evaluation, or a generation runner. It does not
load/save tables, discover files, run a source generator, or return row-level data.

Read `K02_ANALYSIS_SPEC_v0.json` for the fixed definition. Call
`analyze_frame(canonical_dataframe, role="reference")` only on an intentionally
authorized evaluation table, or use `role="generated"` for a generated table.
The mandatory role prevents accidentally reporting synthetic-row uncertainty.
It is a caller declaration, not authentication or an isolation boundary.

Canonical fields are `age, sex, bmi, total_cholesterol, hdl_cholesterol`.
Numeric columns must already have real numeric dtypes; booleans, complex values
and string-encoded numbers fail explicitly. Sex uses literal recorded F/M levels.
Canonical missing values are pandas/NumPy missing values, not unparsed raw NA
strings. Raw column mapping, sentinel decoding, units, file custody and identity
checks belong to a later separately reviewed preparation layer.

The common denominator requires age at least 18, finite numeric fields, F/M or
missing sex (missing excluded), and positive BMI/TC/HDL. The age threshold is an
investigator choice. Excluded-row and overlapping reason counts are explicit.
Additional columns never add restrictions. No trimming, lifestyle, LDL/TG,
disease, fasting, pregnancy or TC>=HDL filter is applied. No real eligibility
count was computed by this implementation work.

OLS uses fixed centered/scaled coordinates `age10=(age-50)/10`,
`bmi5=(BMI-25)/5`, an F indicator and an intercept. This is algebraically
equivalent to raw age/sex/BMI adjustment, and its BMI coefficient is directly
the requested per 5 kg/m² contrast. TC/HDL residual correlation uses the same
common rows and design. SVD supplies a declared numerical rank test.
Constant responses, singular design, too few rows and unresolved numerical
degeneracy remain explicit unavailable records; all three endpoint IDs persist.

Reference slopes can have normal-multiplier HC3 **sensitivity intervals**.
Unknown clustering remains unresolved: these are not design-based population
confidence intervals or validated coverage. The residual correlation has no
interval in v0. Generated tables have no inferential intervals. Zero/numerically
unresolved residual variation gives no HC3 interval and no residual correlation;
an otherwise identifiable finite slope point is retained. Numerical tolerances
protect arithmetic, and are not scientific-adequacy thresholds.

Only explicit reference evaluation emits outcome sample SDs (ddof 1) as
evaluation-only denominators for the separate prospective resolution rule.
No SD, target effect or generated-row precision is supplied to a builder by
this module. No success score, equivalence decision or campaign gate is added.

## Verification

Tests use a 32-row invented balanced factorial with analytically known slopes,
residual correlation and constant-leverage HC3 variance. Additional small
invented cases check per5 scaling, category relabeling invariance, the common
subset, invalid schema/codes, rank/constant/perfect-fit failures, retained
endpoint records, generated-mode inference suppression and input preservation.
No fixture table is written. Run only `test_k02_analysis.py`; older suites and
real/source cases are not part of this unit.

Actual new-suite run on 2 November 2026: **17 passed in 0.58 seconds** using
CPython 3.12.10, NumPy 2.4.5, pandas 3.0.3 and pytest 9.0.3 on Windows. Command:
`python -X utf8 -m pytest test_k02_analysis.py -q -p no:cacheprovider`.
The command wall time was 1.80 seconds. No old tests, real cohort fit, source
generator, file download or quota/admission change occurred.
