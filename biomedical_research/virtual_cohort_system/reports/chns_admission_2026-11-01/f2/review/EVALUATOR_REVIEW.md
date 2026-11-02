# Independent F2 evaluator review

Reviewer: `/root/chns_f2_review`. Scope: static scientific computation, information boundaries, runtime interface and release/inventory enforcement. No CHNS participant table, generated table or target result was accessed. No evaluator run, generator run or passed test suite was repeated. This document does not release clinical access.

## Initial disposition: correction required before approval

Reviewed initial evaluator SHA-256 `852c3e4843a971e6e443cf6c31a7aa9c3f7fe41a01b660416b70b294dec64079`, test SHA-256 `b5956a06ea66efdfb91a9f0f09da7e10e8d2f7a02328c3960b48016aad39dfff`, and fixed analysis plan SHA-256 `a2c5f43969c700474a9466416be8503dc0c92b1c78b12a07a6edc6bc88f247b7`.

1. **Reference availability must follow the frozen finite-value policy.** The measurement decision says to use finite released glucose/HbA1c values. The initial `prepare_reference_frames` uses `notna()` and retains infinite glucose/HbA1c into the common denominator, subsequently withholding the entire case. Apply the finite-glycemia availability rule during reference preparation, with explicit nonfinite accounting. Retain finite zero/negative values for the existing interpretation/withholding gate. Generated invalid values must continue to withhold without deleting rows. This is an implementation correction to the existing policy, not a new target-informed exclusion or amendment to frozen scientific documents.
2. **Record the actual SAS decoder version.** The runtime binding includes Python, NumPy, pandas and SciPy but not pyreadstat, which performs the clinical decode. Bind its installed version in the prospective evaluation runtime metadata. A metadata-only reviewer import/signature check found pyreadstat **1.3.7**, whose `read_sas7bdat` accepts `usecols` and `user_missing=False`. No file argument was supplied and no SAS file was opened by this check.

The implementation author was notified through the coordinator before any reference decoding. This initial finding must remain visible when the final resolution is added.

## Scientific and procedural checks that passed static review

- Exact source field/key/wave names match the reviewed plan. Linkage checks precede wave selection; no silent deduplication occurs. Gender mapping, age scope, exact flag-9 handling, finite positive anthropometry and BMI algebra agree. Common complete cases apply to all three analyses, including glucose availability for E1; community availability does not remove participants.
- E1, E2 and E3 are the three fixed raw, unweighted, intercept-including OLS coefficients, with the planned adjustment sets. Minimum n, full rank, residual degrees of freedom and conditioning diagnostics are implemented. No expected sign or target-fitting operation appears.
- Cluster score sums and the sandwich bread yield the specified CR1 correction `G/(G-1)*(n-1)/(n-k)`, with k including the intercept, and t critical values with G-1 degrees of freedom. Invalid community IDs or fewer than 20 groups make the interval unavailable while preserving the full-sample point estimate. There is no IID fallback. Generated rows receive no inferential precision from their artificial row count.
- Finite nonpositive glucose/HbA1c values trigger withholding before scientific calculations. Invalid generated analysis tables are not repaired by row deletion. This conservatively withholds all three shared-denominator analyses and diagnostics; it does not certify physiologic interpretation.
- Means, sample SDs, linear quantiles, Pearson correlation and average-tie Spearman correlation match the planned diagnostics. Comparisons retain signed differences; ratios require a reference interval excluding zero. Interval membership remains descriptive. No global accuracy score or post-result tolerance is introduced.
- All twelve construction/stage/seed slots are retained, including failure and absence. Stable signs require all three valid program outputs. Direct-row reuse receives no independent Monte Carlo credit. No best seed is selected.
- The ordinary evaluation entrypoint first checks F2, protocol, plan, evaluator/runtime, exact independent approval payload and final inventory. It verifies all four stage reservations, candidate freezes, execution receipts and generated-file hashes. Successful outputs cannot be relabelled absent or failed. An exclusive evaluation reservation precedes reference file hashing/decoding; failure consumes that reservation and is recorded rather than automatically retried.
- The all-four-stage gate intentionally blocks an early-stop inventory with a still-runnable stage. Any such case requires a separately reviewed closure; this implementation must not be worked around with invented run receipts. It does not modify the frozen F2 controller.
- Actual clinical reads are confined to the private reader called by the gated orchestrator, after the four approved file hashes are verified. No patient read occurs at module import. The private Python helper is not an operating-system security boundary; approvals and hashes are procedural safeguards against accidental drift, not protection against coherent host rewriting.

## Verification evidence and limits

The implementation note reports **77 invented-only tests passed in 2.12 seconds**. The reviewer inspected the tests, including independent linear-algebra and statsmodels CR1/t comparisons, threshold/failure cases, all-slot accounting, missing-release no-read behavior and unreserved-stage rejection. The reviewer did not rerun that suite. The only reviewer runtime inspection was the pyreadstat installation/version/signature check described above.

This review does not establish reference release quality, missing-reason recovery, nationally representative inference, transport validity, source reproduction or generated scientific usefulness. Extreme unsupported numerical cases may terminate with a recorded evaluation failure rather than yield scientific estimates; no successful output is presumed. Final inventory approval and an exact evaluation-release payload remain separate future steps, followed by independent numerical recomputation.

## Final resolution

**Static implementation disposition: PASS after the two corrections.** Final evaluator SHA-256: `e40f403b13125f5b41f620126a807122bb99796558adda576518fcf50796365a`. Final test SHA-256: `e6d779a6ab5a997caa17f329181f42b563a46c7d4f694e596e4775af3150872d`.

The reviewer verified the corrected reference common-case mask requires finite glucose and HbA1c, counts nonfinite/nonmissing values separately in the linked pre-eligibility sample, and retains finite zero/negative values for the existing gate. Generated frames do not use this reference filter; their invalid values still cause withholding without row deletion. Runtime metadata now obtains pyreadstat's version through `importlib.metadata.version`, without decoding or importing participant data. The fixed protocol, plan and F2 controller are unchanged.

The implementation author reports only affected checks rerun after correction: **17 passed, 70 deselected in 1.80 seconds**. The reviewer inspected these changed tests and did not execute them. The previous 77-pass result remains historical evidence for the previous implementation; this is not a claim that the full expanded 87-case suite was run on the final bytes.

This PASS covers the actual evaluator implementation. **It does not approve an actual evaluation release or final inventory, which were not yet supplied for this review.** No clinical or generated table was read and no primary/recomputation evaluation was started. The initial findings above remain part of the review history.
