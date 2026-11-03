# Independent evaluator for the bounded CHNS R30 statistical supplement

Prepared 2026-11-03. This new evaluator does not modify or import any frozen evaluator, generator or retained experiment. It performs no generation or fitting and does not read original patient rows. No experimental outputs have been evaluated during implementation.

## Invocation and boundary

```text
python independent_evaluate.py --input-dir FINAL_CSV_DIRECTORY --reference-summary REFERENCE_SUMMARY_JSON --historical-results COMPLETE_RESULTS_JSON --output-prefix NEW_REPORT_PREFIX
```

Without a draw closure, the input directory must contain exactly three CSV files. Their basenames must identify seeds `4101`, `4102`, and `4103` exactly once each, for example `final_4101.csv`. Each has exactly 3,000 rows and columns `age,female,bmi,glucose,hba1c`, with optional `row_id`. Subdirectories may hold files in this strict three-CSV mode, but additional CSVs are rejected. Import, `--help`, and `--self-test` do not open study records. Reports are created exclusively; existing outputs are never overwritten.

For executions with failed or unattempted final draws, pass `--draw-closure DRAW_CLOSURE_JSON`. This manifest must contain `results`, exactly one record for each final seed, with `seed`, `run_id`, `status`, `error`, `receipt_sha256`, and `elapsed_seconds`. Successful slots require a nonempty run identifier, a declared 64-digit receipt hash, and exactly `final_<seed>.csv` directly in the input directory. Non-successful slots require no CSV and remain explicit unavailable slots; no placeholder rows are manufactured. Extra/unregistered CSVs, missing success files, duplicate seeds and inconsistent file inventories are rejected. Receipt/time/run fields may be null for unattempted failure records. An all-failed campaign can have no final-output directory. Every declared failure is retained rather than retried by this evaluator.

The report binds the exact closure bytes by SHA256; optional `--draw-closure-sha256 EXPECTED_HASH` also enforces the controller's predeclared digest. Receipt hashes are declarations within that bound closure, not independently reopened receipt content. The release controller must perform that separate receipt verification.

The reference summary and retained historical report have hard-bound SHA256 values. The historical reference is the exposed CHNS 2009 selected sample (`n=6,631`), not population truth. Only the nine final delivery aggregate records for R01–R03 are selected, excluding initial and trial runs. Each historical metric is checked against the bound reference, stored discrepancy and constructor-stage seed summary. No historical generated rows are reopened.

Filename seeds establish declared slots, not proof of RNG execution. Before execution, the parent release and receipts must bind the generator, specification, seeds and final output hashes. The evaluator reports the actual SHA256 and byte count of every new table. Optional `--fit-artifact` adds a metadata file hash only; it does not import parameters or certify the generating law.

## Statistics and validation

- Independent centered pivoted-QR OLS with intercept: E1 BMI adjusted for age/sex; E2 glucose adjusted for age/sex; E3 age adjusted for sex/BMI/glucose. Units match the retained R30 definitions.
- Twenty-five marginal diagnostics: mean, sample SD (`ddof=1`), linear q10, median and linear q90 for five variables.
- Pearson and Spearman (average ties) glucose–HbA1c correlation.
- Finite numeric columns, exact row count, integer age 35–74, binary female, positive BMI/glucose/HbA1c, unique nonempty optional identifiers. No extra biological magnitude cutoff is imposed. Duplicate measurement rows are counted, not automatically rejected.
- Support-invalid tables retain an unavailable final slot. Rank-deficient regressions or constant-variable correlations are unavailable rather than silently repaired. If a metric lacks any final seed, no complete three-seed mean or discrepancy is reported; all seed values remain visible.

JSON and Markdown contain all 30 metrics for the new statistical construction and each retained R01–R03 constructor. Both **mean seed-wise absolute discrepancy** and **absolute discrepancy of the seed mean** are shown and named separately. There is no cross-metric score, winner, significance or equivalence decision. Reference regression intervals are descriptive community-cluster CR1-t intervals, not tolerance margins. Quantile diagnostics have no fabricated intervals.

## Checks and interpretation

`--self-test` uses invented in-memory arrays/CSV text to check known QR coefficients, rank deficiency, linear quantiles, sample SD, tied-rank Spearman, support/nonfinite/row-count handling, incomplete-slot aggregation, and a complete 30-metric calculation with a known fully adjusted age coefficient. A focused closure test verifies that a failed seed needs no CSV, cannot acquire an unregistered CSV, retains unavailable metrics, and cannot produce a survivor-only mean. All seven tests passed on 2026-11-03. A separate aggregate-only shape/binding check passed for all nine historical final records and 30 metrics per record. These checks did not construct or evaluate an experimental virtual cohort.

This is a descriptive, same-summary calibration comparison with historical Agent outputs. Historical search/feedback/effort budgets differ. Finite synthetic tables do not certify finite theoretical moments; the model requires separate mathematical review. Seed dispersion is not source or structural uncertainty. Real-versus-real resampling is outside this bounded unit.
