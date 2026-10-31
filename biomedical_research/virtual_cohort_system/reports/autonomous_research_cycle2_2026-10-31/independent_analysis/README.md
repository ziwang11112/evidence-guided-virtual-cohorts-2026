# Independent postrun arithmetic checker

Prepared 2026-10-31 while construction revisions and target results remained sealed. Only `PROTOCOL_v2.md`, `analysis/analytical_engine.py`, `analysis/run_evaluation.py`, and `analysis/EVALUATION_INTERFACE.md` were read as specifications. No actual cohort, builder directory, source report, preparation receipt, or evaluation result was opened during preparation. No production file was modified.

`check_postrun.py` is inert on import. Running without arguments or with `--help` prints help only. Its `--self-check` mode exercises hand-computable abstract vectors and a linear equation; it does not generate a biomedical cohort. The algebra checks passed. No actual-data evaluation has been performed by this checker.

Arithmetic is independently implemented: group-wise `math.fsum` means and population moments; QR and triangular solve for square-root-weighted regression, with the prescribed SVD rank threshold; group-wise residual RMS; exact integer-mass balanced quantiles using the LCM of the eight cell counts; and manually interpolated sorted order statistics for stability endpoints. The production engine is never imported or executed. Cluster/PSU first-appearance order, singleton handling, NumPy default RNG, seed 18301, and 399 attempted replicates reproduce the public sampling contract. Failed replicates receive no replacements.

Point quantiles require exact agreement with the mathematical balanced inverse CDF. This is deliberately independent of the production engine's compensated binary-weight summation, and can identify discrepancies at exact mass boundaries. Other numerical comparisons use the predeclared `1e-10` absolute plus `1e-10` relative computational tolerance (`math.isclose`); these are not scientific equivalence margins. Published aggregate bands can be compared, but production replicate-level estimates are not available for individual replicate comparisons.

## Separate root authorization required

After the fixed evaluation finishes, root must create the previously absent `independent_analysis/POSTRUN_AUTHORIZATION.json` with this structure and actual verified SHA-256 values:

```json
{
  "schema": "ensanut_independent_postrun_authorization_v1",
  "issuer": "root",
  "status": "approved",
  "purpose": "independent_fixed_postrun_audit",
  "reference_and_scheduled_output_access_authorized": true,
  "bindings": {
    "release": {"path": "EVALUATION_RELEASE.json", "sha256": "ROOT-VERIFIED-HASH"},
    "completion": {"path": "analysis/results/EVALUATION_COMPLETED.json", "sha256": "ROOT-VERIFIED-HASH"},
    "aggregate": {"path": "analysis/results/aggregate.json", "sha256": "ROOT-VERIFIED-HASH"},
    "endpoints": {"path": "analysis/results/all_endpoints.csv", "sha256": "ROOT-VERIFIED-HASH"},
    "checker": {"path": "independent_analysis/check_postrun.py", "sha256": "ROOT-VERIFIED-HASH"}
  }
}
```

The placeholders above are intentionally non-executable. This README grants no access. All paths are fixed to this known case directory, except builder bundle/run paths discovered exclusively from the hash-bound evaluation release. No caller path, seed, output-directory, resampling-count, or retry override exists. Symlinks, junctions, traversal and Windows path aliases are rejected. No harness, execution, source-audit or production analysis API is called.

Authorized future invocation:

```text
python -B independent_analysis/check_postrun.py --run-postrun
```

The checker validates the complete initial/final by three-seed grid and retention links. It binds every execution receipt, and reads only the successful generated outputs and the fixed prepared seven-column reference. It recomputes each distinct successful output content once, retaining every scheduled label and the execution/analytical failures. It checks all 31 reference and generated estimands, all 31 stability bands, replicate counts and failure/valid attempt identities, cohort/cell counts, JSON/CSV consistency, and scheduled/unique/failed counts. Existing production files are read only; all consumed hashes are rechecked before writing.

The new fixed `independent_analysis/postrun_results/` directory is created exclusively for one attempt. `comparison.json` and `endpoint_comparison.csv` contain aggregates and numerical differences only; `ATTEMPT.json` and `COMPLETED.json` bind the audit, or `FAILURE.json` records a fixed failure code. There are no participant rows, identifiers, residual vectors, replicate estimates, execution logs, downloads or network calls. An existing audit output directory prevents a repeat; no cleanup or automatic retry is provided.

This checks arithmetic and published aggregate consistency. Root's bound evaluation release remains responsible for complete construction admission, frozen scientific lineage, executor verification, and preparation provenance. No failed/timeout output or log is opened.

Preparation verification: abstract algebra, inert import, unsafe path rejection, an in-memory missing-authorization gate, and `--help` all passed. The gate test returned only an empty invented authorization object and asserted that no subsequent content read occurred. Neither an authorization file nor an audit result directory was created.

Checker SHA-256: `bf197b898e56d41fa6a83604e2456d30667ebad0a102a234a0a2e480e550b418`.
