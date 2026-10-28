# Independent post-run audit

Status: PASS for numerical and provenance verification only; this is not a scientific success score. No generator, evaluator, analysis specification, or rule was changed.

Recomputed 164 weighted fits and 328 endpoints for the real outcome and 40 scheduled generated dataset files. The 40 files occupy distinct paths/slots and have 25 distinct SHA-256 contents; they represent four Agent constructions, not 40 independent cohorts or Agents. All 12,918 numeric aggregate scalars agree within absolute tolerance 1e-09 plus relative tolerance 1e-10. 0 failed checks.

Maximum absolute discrepancy: 6.46594e-13; coefficients: 6.46594e-13; covariance entries: 2.19824e-14.

The independent implementation uses weighted QR with raw weights and triangular solves for PSU influence totals. It does not import the frozen evaluator. Full-spine PSU groups are retained and centered within strata; all model ranks and residual degrees of freedom match the official results.

Design: 9,813 full-spine records, 4,885 domain records, 15 full/domain strata and 30 full/domain PSUs. Model residual df: A=14, B=12, C=11, D=11.

All 189 release commitments, 40 unique output paths/slots, nested candidate/review/execution commitments, the survey packet manifest, and gateway audit prefixes were independently verified. Every scheduled file retains exactly one row per observed key and exactly preserves BMI, age and sex. Only aggregate data, comparison errors and file hashes are exported.

Initial/final outputs are byte-identical for ordinary_2, gap_1 and gap_2 for every paired seed. All five ordinary_1 output pairs differ. These are three no-op output revisions and one changed construction; documentation activity alone is not numerical improvement.

All official fit, distribution, endpoint-draw, summary and initial/final change outputs were checked, including the four later custodian CSV tables and aggregate report. The root report also passes its aggregate, manifest and interpretation checks: all eight endpoints are retained, zero-overlapping real intervals remain unresolved, five draws are not five independent Agents, and significance matching is not a universal success criterion. No composite winner is calculated.

## Limits

- This audit verifies the committed artifacts and current outputs, not an OS-enforced blinding boundary or absence of pretrained exposure.
- Same-seed reproducibility assertions were provenance-checked; frozen generator execution was not repeated by this auditor.
- This numerical audit does not establish appropriateness of external evidence choices, transport validity, causality, individual outcome recovery, or workflow superiority.
- In this dataset every full-spine PSU contains target members; retention of empty-domain PSUs is independently implemented, but this released dataset does not itself exercise a zero-member PSU case.
- Synthetic survey intervals remain conditional on generated outcomes and are not calibrated uncertainty about the hidden true feature.
