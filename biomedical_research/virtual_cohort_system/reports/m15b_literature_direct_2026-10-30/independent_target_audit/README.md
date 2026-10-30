# Independent M15-B numerical and dataflow audit

Prepared from `../PROTOCOL.md` and `../evaluation_code/README.md` only. The original evaluator implementation was not consulted or imported while implementing the formulas. No actual observed, reference, or candidate rows were read during preparation. This is an independent recomputation of fixed analyses, not an experiment, generator, revision, candidate selector, or another independent cohort.

`audit.py` implements all 24 fixed estimands using statsmodels formula OLS with an explicit full-rank check and QR fit. It uses standard-library arithmetic mean, sample SD and median, and independently implements Q90 interpolation at `(n-1)*0.9`. Each estimate retains its sample count, complete-case count, matrix rank, units, value or null, and failure status. Missing or nonfinite values are not silently dropped. The four global reference coefficients have complete joint `(SDMVSTRA,SDMVPSU)` deletion records, ranges, sign stability, omitted group counts and rank failure counts. Strict signs have no tolerance; tiny coefficients can change signs from roundoff.

The benchmark comparison checks the exact ID sequence, race/sex values, exact decimal age/BMI values, 200-row quota and 50 rows per group against the observed table. It reports the number of rows whose urate value changed between initial and final and separately records formatting-only differences. Identical initial/final values are one unique candidate table carrying both labels. Estimates and their differences remain descriptive finite-cohort results. No p-values, confidence intervals, scientific acceptance thresholds, or quality score are produced.

The executable gate requires an explicit `--execute-after-controller-release` flag and the controller release manifest documented by the original evaluator README. Before parsing any cohort CSV, it verifies the protocol, released evaluator, task, observed table, both freezes, both generated tables, and reference SHA256 commitments. The reference is hashed only after all nonreference commitments verify. The gate does not import or reuse evaluator or lifecycle functions. Lifecycle/source review remains a required controller assertion, and hashes do not establish reviewer identity, chronology of commitment, or OS isolation. A new private output directory is required. Outputs contain aggregate results and no individual rows.

`compare_canonical_released_output` compares independently computed estimates and PSU details against an explicitly mapped released aggregate. If the released evaluator uses a different JSON field layout, its output must first be mapped transparently to the documented canonical fields; that small schema adapter can be added after authorization without consulting numerical implementation. All 24 keys and all deletions must be retained. The comparison reports numerical differences without a scientific pass/fail threshold.

Execution template only; do not run before the root controller explicitly authorizes the final freeze and evaluation release:

```powershell
python audit.py --execute-after-controller-release --release-manifest RELEASE.json --output-dir NEW_PRIVATE_AUDIT_DIRECTORY
```

After the controller supplies the released aggregate, add `--canonical-released-output CANONICAL_RELEASED_AGGREGATE.json` as appropriate. Expected bundle filenames are `task.json`, `observed.csv`, and each candidate's `freeze.json` and `generated.csv`; the release manifest supplies the candidate paths and private reference path. Verify these filenames against the actual authorized manifest before execution.

Invented-only verification, from `virtual_cohort_system`:

```powershell
python -m pytest work/m15b_literature_direct_2026-10-30/independent_target_audit/test_audit.py -q -p no:cacheprovider
```

Preparation verification: 14 tests passed. The tests cover known forward, reverse, curvature and interaction coefficients, stdlib summaries, explicit quantiles, nonfinite/empty/singleton failures, rank failures, six joint PSU groups and failed deletions, exact preservation and row order, actual changed-row count, identical-candidate counting, aggregate-comparison differences, order invariance, ignored private columns, quota enforcement, inferential-field absence, and refusal before opening inputs when the execution flag is absent. These are implementation checks on invented data, not released-candidate checks or scientific validation.

Status at preparation handoff: implementation ready; actual analysis remains unexecuted and awaits explicit root authorization.

Post-release status: the root controller subsequently explicitly authorized the audit against release manifest SHA256 `1205dfdcf9ebe8333e5b0b13c663f0d7b3e4e633fab2ad551c01db693f2b5d4b`. `map_released_output.py` transparently mapped the released aggregate fields and verified the JSON/CSV export. The independent audit then executed once, successfully. `summarize_audit.py` reads only saved aggregate outputs and writes aggregate checks and the report; it performs no row reads or fits. See `AUDIT_REPORT.md` and `released_audit_results/audit_checks.json`. The original numerical evaluator implementation was never read or imported, and the independent estimand implementation was not changed after seeing released results.
