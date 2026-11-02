# Independent numerical recomputation prepared before reference access

Author/reviewer: `/root/chns_f2_review`. This is a verification implementation of the already fixed analysis, not a new scientific analysis or generator. No CHNS participant file, actual generated table or target result was opened while preparing it. No reference-data hashes were recomputed. No clinical evaluation or recomputation has run.

## Fixed artifacts

| Artifact | SHA-256 |
| --- | --- |
| `chns_f2_recompute.py` | `be03a4c63ce577ba93bd37600cddda528a738917e33829b0d0c950c936ea652a` |
| Reviewed primary evaluator | `e40f403b13125f5b41f620126a807122bb99796558adda576518fcf50796365a` |
| Frozen analysis plan | `a2c5f43969c700474a9466416be8503dc0c92b1c78b12a07a6edc6bc88f247b7` |
| Final evaluator review note | `c15044efb993245a83f2d497fb33f1c8eb450b26ab667a1e5326b42a99323692` |

Installed metadata: Python 3.12.10, NumPy 2.4.5, pandas 3.0.3, SciPy 1.17.1, statsmodels 0.15.0, pyreadstat 1.3.7. These versions are bound again at actual recomputation authorization. No decoder file argument was used in preparing this note.

## Independence and scope

The script independently reads the four approved source files and columns with the hash-bound decoder, checks all-wave key validity/uniqueness, and prepares linkage by indexed intersections rather than the primary evaluator's merges. It independently applies age/gender scope, exact flag-9 handling, the algebraic BMI definition, finite glycemia availability and the common complete-case denominator. Finite zero/negative glycemia is not recoded; it retains the prescribed withholding gate. Invalid generated tables are not repaired by deletion.

It uses **statsmodels OLS and `get_robustcov_results(cov_type="cluster", use_correction=True, df_correction=True, use_t=True)`**, independently of the primary evaluator's own least-squares/sandwich implementation. Grouping failures preserve points and remove only intervals. Generated rows receive no artificial inferential precision. Diagnostics use pandas quantiles/sample SDs and SciPy Pearson/Spearman functions. All three estimates, diagnostics, quality counts, twelve slot outcomes, comparison fields and stage summaries are compared with the completed primary report. Failures and absent slots remain visible.

The fixed comparison tolerance (`rtol=1e-8`, `atol=1e-10`) concerns numerical agreement between implementations; it is not a biological success threshold, an equivalence margin or permission to change scientific results.

Shared dependencies remain explicit: the same frozen scientific definitions and SAS decoder are used. The primary evaluator is imported **only to run `_evaluation_gate` for final metadata/read-permission checks**. None of its data-preparation, estimation, diagnostics or comparison helpers is called. This is independent numerical/processing verification, not an independent source of biological evidence or an independently developed decoder.

## Read gate and eventual use

The script is not run automatically. It requires an explicit coordinator authorization after the real final inventory is reviewed, the primary evaluation is released and a primary `REPORT.json` exists. The file `F2/INDEPENDENT_RECOMPUTATION_RELEASE.json` must contain exactly:

```json
{
  "schema_version": 1,
  "status": "authorized",
  "reason": "Explicit coordinator authorization after completed released primary evaluation",
  "script_sha256": "be03a4c63ce577ba93bd37600cddda528a738917e33829b0d0c950c936ea652a",
  "evaluation_release_sha256": "<hash of actual EVALUATION_RELEASE.json>",
  "primary_report_sha256": "<hash of completed evaluation_results/REPORT.json>",
  "runtime_versions": {
    "python": "3.12.10",
    "numpy": "2.4.5",
    "pandas": "3.0.3",
    "scipy": "1.17.1",
    "statsmodels": "0.15.0",
    "pyreadstat": "1.3.7"
  }
}
```

This example is documentation, not an authorization file. No actual authorization was written by the reviewer. The orchestrator then verifies the primary final gate and all immutable artifacts, exclusively reserves `independent_results/`, and only then verifies/decodes source files and reads successful generated tables. Reports contain aggregates only. A failed reservation produces `FAILURE.json` and is not automatically retried. Any disagreement is preserved for review rather than repaired by rerunning generation or editing the primary report.

After explicit go-ahead, the coordinator may run the script with `--bundle <F2 absolute path> --reference-dir <approved local source directory>`. These arguments are deliberately not filled with an executable data path here. Patient-level and generated data remain local. No primary report, frozen receipt or F2 controller is modified.

## New verification actually performed

Only this new script's `--self-check` was executed, once. It passed in about 2.1 seconds using one fabricated 120-row in-memory fixture, with deliberately shuffled input order and three prespecified availability exclusions. It checked indexed linkage, flag-9/native-missing/infinite-value handling, agreement of all three OLS coefficients and CR1/t results with separately calculated closed-form quantities, and nonpositive-value withholding without row deletion. No study metadata path, source file or generated output was read by this self-check. No artificial patient table was exported, no scientific mechanism experiment was conducted, and no already passed test suite was repeated.

Actual primary evaluation, independent recomputation, complete real slot inventory and scientific utility remain unassessed by this implementation note.
