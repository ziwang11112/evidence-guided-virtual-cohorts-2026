# Independent evaluator and source-controller review

30 October 2026. **PASS for the reviewed numerical definitions and procedural gate, subject to the controller completing the documented release checks before reference access.** No implementation defect requiring a scientific change was found. This review does not itself authorize or run the real-data evaluation.

## Boundary and files

Read `evaluator.py`, `test_evaluator.py`, the evaluator README, `../controller.py`, the protocol and prelaunch commitment. Read the relevant existing source-check and lifecycle implementation to understand delegated verification. Ran invented-data tests only. Did not open actual observed, generated or reference row tables, raw XPT outcomes, or prior target results.

Reviewed evaluator SHA-256: `4181cfbd8ae37df58699558196ca241f2bd60e4d895b9a18de40a42cbaffce12`.

Reviewed source-controller SHA-256: `a96847853ce5045e3cf7c833909df0ac92a97fdf146240d8d1b3b1fbc95b0b61`.

These files, the test module, protocol and prelaunch commitment were hash-checked before and after independent calculations and were unchanged. Subsequent code changes require review of the affected behavior and new release hashes.

## Numerical verification

The existing invented-data suite passes **24 tests**. The first invocation produced 19 passes and five fixture-setup errors because Windows denied access to the default `pytest-of-ziwan` temporary directory. The affected test bodies did not run. A second invocation using a new task-local temporary directory completed all 24 tests; no scientific code was changed to obtain that result.

Beyond those tests, `independent_calculation.py` constructs a separate explicitly invented 200-row full-factorial fixture with nonzero curvature, sex-specific BMI slope differences, an age effect and independent residual variation. It does not reuse the helper's fixtures. Expected regression results are calculated with exact rational normal equations and Gaussian elimination, independently of the evaluator's NumPy least-squares solver. Additional closed-form coefficients check scale and index interpretation. Means, n-1 SD, medians and Q90 are computed separately using rational arithmetic and direct interpolation. A constant response-shift comparison checks that group location statistics shift while slopes and SD remain invariant.

All **72 independent numerical comparisons** pass with maximum absolute difference **3.8746783559417963e-14**. The comparisons cover the 24 estimands, additional closed-form checks, all four global coefficients across four joint-PSU deletion groups, and all 24 generated-minus-measured differences under the invented shift. Results contain aggregate checks only in `independent_calculation_results.json`.

## Estimand and failure handling

- The four global coefficient definitions match the protocol: BMI per five units, age per ten years, a separate quadratic BMI term and a separate male-by-BMI interaction. The curvature and interaction coefficient indices point to the sixth model column, with no accidental combined-model search.
- The four group regressions use BMI as outcome, urate and raw age as predictors, and include an intercept. Their urate coefficient has `(kg/m²)/(mg/dL)` units. No reciprocal conversion of a reverse regression occurs.
- Group SD uses n-1, and median/Q90 explicitly use linear interpolation at `(n-1)q`. All 24 records remain in the output when a numerical estimand fails.
- Nonfinite numeric cells fail affected estimands without complete-case deletion. Rank-deficient models return failure rather than accepting a minimum-norm coefficient. Empty and singleton groups are retained with appropriate statuses. Structural failures reject invalid identities/categories/schema.
- Reference and candidate use the same estimator functions. Pair validation enforces identical ID order and observed age/BMI/race/sex values, 200 matched rows and 50 per group. Canonical ID ordering stabilizes numerical reductions without permitting unmatched pair order.
- Optional reference identifiers and weights do not enter estimation. This is consistent with the finite quota-cohort protocol, not national survey estimation.

## Reference sensitivity and interpretation

Deletion groups are the joint `(SDMVSTRA, SDMVPSU)` labels, so equal PSU numbers in different strata are not merged. Every deletion's size, rank, estimate and failure is preserved. Min/max use finite successful fits only. The all-deletions sign-stability flag is unavailable if any fit fails; finite-only stability is separately labeled.

The code reports no p-values, clinical CIs, equivalence threshold or composite validity score. The ranges are descriptive sensitivity, not a sampling distribution or model/transport uncertainty interval. Strict floating-point signs can change for coefficients numerically near zero; the README states this, so the flag should not be promoted into a biological decision rule.

## Release gate review

The CLI refuses execution without `--execute`. It then checks the release schema, controller assertions, protocol/evaluator/task/observed hashes, both freeze hashes, full lifecycle verification, direct-table routes, committed generated-table hashes, initial revision index and final ancestry. Only after these checks does it access the reference file to verify its hash and then read its values. Existing tests exercise missing-review rejection, self-hash tampering and the ordering of reference hashing relative to lifecycle verification using invented files and explicitly mocked lifecycle receipts.

The existing lifecycle verifier recursively checks ancestor hashes and rejects cycles, so the evaluator's subsequent ancestry traversal is based on verified receipts. The gate does not infer source validity or reviewer identity from a Boolean. Source-feedback binding, exposure review, preservation review and independent code-review completion remain trusted controller assertions that must correspond to actual work.

The prelaunch commitment already records a private reference SHA-256. **The final release manifest must use that same committed digest and reference path; do not derive a new reference choice after seeing outcomes.** Bind the reviewed evaluator hash before reference evaluation. This audit read the commitment metadata but did not open/hash the actual reference file.

The pure in-memory functions and explicit reader are not access controls. An arbitrary caller can bypass the CLI, and the release file is not a signed capability. A new output directory is required, but the gate is not a global single-use authorization system. These limits are consistent with the documented procedural controller model. The controller remains responsible for the scheduled one-release evaluation and preventing target-informed repair.

## Source-only controller review

`source_feedback` verifies prelaunch input commitments and source-registry prefix, validates/freezes the candidate contract, requires the direct-table route, reserves one of two feedback slots before calculation, and obtains/verifies a direct-row execution receipt with `generator_executed == false`.

Its only scientific calculation is the existing source-check adapter. That adapter binds source-check/evidence/spec/table artifacts, validates operator/evidence types and unit labels, preserves explicit approximation assumptions and reports `generation_link_verified: false`. Paths are confined to candidate-bound files; no private reference path or outcome estimator is used by this controller. No hard-coded urate relationship, target coefficient or numeric repair is present.

The controller does not mechanically prove that each proposed source operator is scientifically comparable to the target-shaped table, or that a selected evidence item was extracted correctly. The promised substantive review must occur before running the check. Its feedback wording correctly states that population differences make these transport diagnostics rather than exact source replay. A structurally valid check and close source fit remain insufficient evidence of target usefulness.

Before the actual release, the controller should retain the final candidate's verified freeze/preservation record and any scheduled direct validation receipt, bind actual feedback artifacts, and confirm the exposure/use interpretation. This review did not inspect a candidate or claim that those steps have already occurred.

## Outcome

The evaluator is numerically consistent with the protocol on independent invented data. The source controller keeps target analysis out of feedback. No real scientific result was produced, and no frozen protocol, candidate, source or historical result was changed by this review.
