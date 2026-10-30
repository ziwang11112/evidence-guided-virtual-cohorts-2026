# Evaluator implementation checks — 2026-10-30

Scope: evaluator implementation and invented-data tests only. No actual target/reference/observed/generated table or source article was opened. No actual experiment was run. Existing harness files were read for the lifecycle API but not modified. The fixed protocol was read before implementation.

Final result: **24 passed in 0.70 seconds** under Python 3.12.10, NumPy 2.4.5, pandas 3.0.3, pytest 9.0.3. Both Python files also passed `python -m py_compile`.

The meaningful numerical checks use invented algebraic cohorts and hand-known expected answers. Coverage includes forward and reverse coefficients, separately specified curvature and interaction models, sample SD and linear quantiles, retained missing-group and rank/nonfinite failures, quota and identity preservation, numerical permutation invariance, ignored weights/private identifiers, joint rather than marginal PSU deletion, deletion sample counts and failure reporting, and no inferential result fields. Gate tests verify refusal without `--execute`, refusal before file hashes when controller review flags are absent, self-hash tamper refusal, and reference-hash access only after both candidate checks. The gate-order tests mock lifecycle verification explicitly; genuine frozen-bundle integration remains part of the controller's final release audit.

Retained technical failure history:

1. Initial test invocation: 19 passed, 3 fixture-setup errors. Windows denied access to pytest's existing default `%TEMP%/pytest-of-ziwan` directory. No estimator assertion failed.
2. Added two release-order/tamper tests, used a fresh scratch directory under `evaluation_code`: 22 passed, 2 fixture-setup failures because nested test paths exceeded Windows' legacy path length. No estimator assertion failed.
3. Used a short, fresh workspace-root scratch directory: all 24 tests passed. The README records the reproducible command and environment workaround.

Implementation SHA256 at handoff:

- `evaluator.py`: `4181cfbd8ae37df58699558196ca241f2bd60e4d895b9a18de40a42cbaffce12`
- `test_evaluator.py`: `c1bb3c1f9f2138e24ce4cfa948bc1fe2b72dddf40f6e4ac2399410afd1352de4`

The evaluator self-hash is mandatory in the controller release manifest. If the independent review changes the implementation, recompute the hash and rerun appropriate tests before writing the final release manifest. Manifest assertions are procedural controller statements, not authenticated proof of review or OS-enforced isolation.

Temporary-fixture cleanup was rejected by automatic approval review as “blocked by policy”; no deletion occurred. Exclude `evaluation_code/invented_test_tmp_bf30cbcb326a482cba05f5bfcb035134/`, `evaluation_code/__pycache__/`, and the workspace-root `.m15b_evaltest_fe23fc21/` from any code synchronization. These temporary fixtures are invented, and their names/content do not describe real released candidate bundles.
