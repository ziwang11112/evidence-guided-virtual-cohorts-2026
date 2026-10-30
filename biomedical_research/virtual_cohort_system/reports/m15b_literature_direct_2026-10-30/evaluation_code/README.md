# M15-B1 fixed evaluator

`evaluator.py` defines the 24 estimands in `../PROTOCOL.md` and descriptive joint-PSU deletion sensitivity for the four global reference coefficients. It contains no candidate generator and performs no work on import. Its tests use only explicitly invented algebraic data. No actual target, reference, observed table, generated table, or article was read while implementing these files.

## Data and interpretation

Candidate columns must be exactly `sample_id,race,sex,age,bmi,urate`. The private reference requires those columns plus `SDMVSTRA,SDMVPSU`; optional `SEQN,WTPH2YR` are accepted and ignored. IDs must be unique nonempty strings, race exactly `White/Black`, and sex exactly `male/female`. The benchmark comparison requires identical ID order and observed covariate values, 200 people, and 50 in each race/sex group. Pure table estimators also permit smaller invented fixtures; the executable benchmark never relaxes the quota.

All analyses are unweighted finite-cohort descriptions. No p-values, confidence intervals, national estimates, acceptance thresholds, individual reconstruction scores, or combined quality score are calculated. Initial and final candidates are both reported; no candidate is selected from target results. An identical initial/final table is reported once with both labels and zero changed rows.

Every estimand retains its value (or JSON null), status/reason, units, total `n`, complete-case count for diagnostic purposes, and matrix rank. Numeric missing/nonnumeric/nonfinite values fail affected estimands without dropping rows. A rank-deficient OLS design fails the entire model; no pseudoinverse coefficient is silently accepted. Summary ranks refer to an intercept-only group design (1 when the group is nonempty, otherwise 0); they are explicitly labeled as such, and no summary regression is fitted. The SD uses `ddof=1`; median and Q90 use NumPy's explicit `method="linear"`, equivalent to interpolating at `(n-1)*q`. Fixed sample-ID sorting makes computations independent of input row order while comparison still enforces matching row order between reference and candidate.

Deletion records retain the joint stratum/PSU identifiers, omitted and remaining row counts, ranks, values and failures. Min/max ranges use only finite successful deletions. `all_deletions_sign_stable_with_full` is null if the full fit or any deletion fails; `finite_deletion_sign_stable_with_full` separately reports the finite subset. Both compare strict floating-point signs to the full fit, without a tolerance or equivalence threshold. Very small fitted coefficients can therefore change signs from roundoff. The number of deletion groups and all failures remain visible. These ranges are descriptive sensitivity, never calibrated uncertainty or confidence intervals.

## Pure interfaces

- `evaluate_table(frame, reference=False)` returns 24 estimate dictionaries.
- `validate_pair(reference, candidate)` checks matching identity/covariates/order and the fixed quota.
- `compare_tables(reference, candidate)` returns all 24 measured/generated pairs and differences.
- `reference_sensitivity(reference)` returns the four full fits, deletion details and range/sign summaries.

These functions operate on explicit in-memory inputs and are not a security boundary. `read_analysis_table(path, reference=...)` is an explicit reader for controller use; it must only be called after final release. The CLI enforces the procedural release checks below before its first reference-file access.

## Controller release manifest

The controller writes the manifest only after the final freeze, source-feedback binding review, source/exposure-map review, preservation checks, and independent code review. All hash values below are lowercase full SHA256 digests; placeholders are intentionally invalid. Paths should be absolute, except `candidate`, which must be relative to the bundle. The evaluator self-hash is required. The controller must precommit the private reference hash before evaluation, independently of outcomes.

```json
{
  "schema_version": 1,
  "kind": "m15b_target_evaluation_release",
  "evaluation_authorized": true,
  "bundle_path": "D:/ABSOLUTE/PATH/TO/BUNDLE",
  "protocol_sha256": "FULL_SHA256_OF_PROTOCOL_MD",
  "evaluator_sha256": "FULL_SHA256_OF_EVALUATOR_PY",
  "task_sha256": "FULL_SHA256_OF_BUNDLE_TASK_JSON",
  "observed_sha256": "FULL_SHA256_OF_BUNDLE_OBSERVED_CSV",
  "reference_path": "D:/ABSOLUTE/PRIVATE/REFERENCE.csv",
  "reference_sha256": "PRECOMMITTED_FULL_SHA256_OF_PRIVATE_REFERENCE",
  "initial": {
    "candidate": "candidates/initial",
    "table_sha256": "FULL_SHA256_OF_INITIAL_GENERATED_CSV",
    "freeze_sha256": "FULL_SHA256_OF_INITIAL_FREEZE_JSON"
  },
  "final": {
    "candidate": "candidates/final",
    "table_sha256": "FULL_SHA256_OF_FINAL_GENERATED_CSV",
    "freeze_sha256": "FULL_SHA256_OF_FINAL_FREEZE_JSON"
  },
  "controller_checks": {
    "both_releases_verified": true,
    "source_feedback_binding_verified": true,
    "source_exposure_map_verified": true,
    "preservation_verified": true,
    "independent_code_review_complete": true
  }
}
```

If initial and final are the same frozen candidate, use that candidate in both manifest entries and both explicit CLI paths. The gate verifies the current protocol and evaluator, task/observed commitments, both `freeze.json` hashes, `cohort_harness.lifecycle.verify_candidate` for both candidates, direct-table routes, both generated-table commitments, initial revision index, and final ancestry. Only then does it check the explicit reference path and reference hash. The assertions are trusted controller statements; the gate does not establish reviewer identity, independently prove source review, enforce OS isolation, or cryptographically prove when the reference hash was committed. It performs no generator execution and no source searching.

The CLI has no automatic run mode. The command below is an invocation template only, and must not be executed before release:

```powershell
python evaluator.py --execute --release-manifest RELEASE.json --reference PRIVATE_REFERENCE.csv --initial BUNDLE/candidates/initial/generated.csv --final BUNDLE/candidates/final/generated.csv --output-dir NEW_PRIVATE_RESULTS_DIRECTORY
```

Omitting `--execute` fails before any input file is opened. Existing output directories are refused. Successful output is aggregate-only `evaluation.json` (including complete sensitivity details) and flattened `estimands.csv`. Patient-level tables remain local and are not copied into evaluation outputs.

## Invented-data tests

```powershell
$testScratch = Join-Path 'D:/AIR-014_ECRC_Paper_Clean_2026-08-16' ('.m15b_evaltest_' + [guid]::NewGuid().ToString('N').Substring(0,8))
python -m pytest work/m15b_literature_direct_2026-10-30/evaluation_code/test_evaluator.py -q --basetemp $testScratch
```

Run from `virtual_cohort_system`. The short, fresh scratch path avoids this machine's default pytest-temp permission restriction and legacy Windows path-length limit. Tests cover hand-known forward/reverse coefficients, separate quadratic/interaction recovery, linear quantiles and n-1 SD, missing groups, singleton groups, deficient designs, nonfinite failures, preservation and quota enforcement, permutation invariance, ignored private weights/identifiers, joint PSU deletion counts/ranges/failures, absence of inferential output fields, and pre-execution gate refusal. Gate-order/tamper tests explicitly mock lifecycle verification and use invented placeholder files; they do not claim an integration test of genuine candidate releases. None execute the experiment.
