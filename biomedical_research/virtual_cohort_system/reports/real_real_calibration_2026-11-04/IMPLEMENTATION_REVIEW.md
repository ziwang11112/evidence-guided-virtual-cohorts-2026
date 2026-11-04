# Independent implementation review

Date: 2026-11-04. Decision: **APPROVED FOR FREEZE at the hashes below.** No unresolved blocking implementation defect was found after correction of the partition-exhaustion audit path. This approval concerns conformance to the descriptive protocol, not the validity of any as-yet-uncomputed numerical result or an equivalence claim.

## Scope and reviewed versions

This reviewer inspected the new source, invented-fixture tests, protocol, design review and implementation notes, plus the historical selection module as source text to verify the specific helper called and the contents of its returned quality summary. The reviewer did not read patient values or generated table rows, import or execute the historical runner, run historical tests, execute the file-backed new evaluation, or change implementation files. This review stage writes only this file.

| Artifact | SHA-256 reviewed |
|---|---|
| `calibration.py` | `b84b4c69de5910a48b8ff21373077b25f452ccea8e65681ebcf5243de3d6c1be` |
| `test_calibration.py` | `ac84cbaf337446eb7cc7bfb25ce5ff6f318db5a7c85e71496c02d991b883ab45` |
| `PROTOCOL.json` | `25464431dffbdf5a8bfc6f9345955b27bcd2f3c61c2ae149ed115ac64d05833a` |
| `DESIGN_REVIEW.md` | `411d5ddd816e1a2a03bf6a4c434d7e83264ed6b3e34329971b6378c35d5deefb` |

The source and test hashes were independently read from disk after the author's correction and matched the author's final candidate hashes. Any subsequent code change requires a new review binding before execution.

## Findings resolved before approval

The initial implementation accumulated each rejected partition's pool counts but discarded them when all permitted attempts were exhausted. That would have made the stated all-attempt audit incomplete on the failure path.

The corrected `SamplingExhaustedError` carries only the failed seed, attempt numbers, per-side pool counts, acceptance flags, reason, fixed sample size and no-replacement/no-relaxation flags. The file-backed `run` catches this specific error, exclusively writes `FAILURE.json` with protocol/freeze/receipt provenance and the aggregate audit, then re-raises it. No successful report is published, no substitute seed is selected and no clinical values or membership lists are included. The invented exhaustion test now checks the complete two-attempt audit in its impossible toy fixture. This resolves the finding without changing the sampling or metric calculations.

## Protocol conformance

### Sampling and sample identity

The file-backed entrypoint is fixed to the 100 seeds 8400–8499, 6,631 reference rows, 218 communities, 3,000 selected rows per side and at most 1,000 partition attempts per seed. `verify_inputs` rejects a protocol differing from those constants. Nondefault helper arguments exist for small invented fixtures; `run` does not expose them.

Community labels are factorized with sorted order. A fresh PCG64 generator for each seed permutes the community positions, assigns 109 to R1 and 109 to R2, and accepts solely when both pools contain at least 3,000 rows. No clinical variable, coefficient, correlation or discrepancy is used for acceptance. The same stream samples R1 followed by R2 without replacement, then sorts selected row positions. Explicit overlap checks cover both rows and communities. Assigned and represented community counts, per-side pool/sample counts, attempts and domain-separated hashes are retained.

The historical `prepare_reference_frames` helper checks linkage keys and merge cardinality, constructs the original BMI/age/sex/common-complete-case frame, and returns no patient identifiers. Both regressions operate on the same sampled frame. The reference's row/community counts and numeric schema are checked before analysis; the sampling helper also rejects missing/invalid community assignments. The code does not enlarge A by admitting rows with missing glucose.

### Complete metrics and discrepancy arithmetic

The fixed ordered metric inventory has 36 unique keys: all 9 OLS coefficients, 20 continuous marginal summaries, female proportion and 6 pairwise correlations. The two models include their intercepts and exactly the declared predictors. OLS uses `numpy.linalg.lstsq(rcond=None)` without weights. SD uses `ddof=1`; marginal and discrepancy quantiles use linear interpolation; Spearman uses average ranks for ties. All three requested variable pairs are present.

Each existing G table is summarized once and remains fixed across all splits. Every split retains R1 and R2 metrics, signed/absolute R1−R2 differences, signed/absolute G−R2 differences separately for each G seed, and `(abs(G−R1)+abs(G−R2))/2`. The same R2 is used within each requested paired comparison. The symmetric quantity is not presented as correcting dependence.

Summary output is limited to q10, median and q90 in native units plus scheduled/available/unavailable counts. No ratios, percentile ranks, win/exceedance rates, p-values, confidence intervals, thresholds or success counts are calculated. The human-readable results should continue the design's emphasis on the seven nonintercept coefficients while retaining all nine coefficients; the core output already preserves all nine.

### Unavailable values and failed inputs

Rank-deficient models retain all coefficient keys as null with a model-specific reason; `lstsq` numerical failure also becomes null. Constant-variable or nonfinite correlations become null with reasons. A nonfinite scalar summary or discrepancy is represented as null rather than an invalid JSON number. Affected metrics propagate to the corresponding discrepancy; unaffected metrics remain available. Every scheduled split remains in a successful report, and no metric failure triggers resampling.

Per-metric quantiles use only available values and always expose the missing denominator. An entirely unavailable metric has null quantiles and explicit counts. This is a transparent availability policy, not imputation. Raw nonfinite/nonnumeric data, malformed generated schema/IDs, changed input hashes and sampling-frame integrity errors halt the run rather than filtering or repairing rows. Partition exhaustion now retains its aggregate failure audit and stops.

## Read gate, historical boundaries and output inspection

The reviewed module has no data reads or writes at import. Through the supported file-backed `run` path, the ordering is: verify protocol and frozen code/review bindings; verify historical anchors, four source hashes and three generated-table hashes; exclusively create `READ_RECEIPT.json`; decode; evaluate; rehash all bound input files and code; exclusively create `REPORT.json`. Hashing file bytes before the receipt does not decode clinical or generated values. An existing report or receipt prevents automatic rerun/overwrite. The receipt records the pre-decode bindings.

The only call into the frozen historical evaluation module is `prepare_reference_frames(frames, plan)`. The new implementation does not call `evaluate_released`, either later historical evaluation runner, any generator, a candidate execution API or a download mechanism. The historical module import suppresses bytecode writes, restores the temporary import state, and does not run its campaign. Its returned `quality` object contains aggregate linkage/missingness/cleaning counts only.

Generated headers must be unique and exactly match `person_id` plus the five analysis variables; IDs must be complete/unique and are removed before summary. A report contains aggregate metrics, counts, input paths/hashes and selection hashes. The ephemeral positional arrays in `SampleSplit` are never serialized; neither patient IDs, community labels, membership arrays nor generated rows are inserted into report or failure objects. The command-line success printout contains only report path/hash and split/metric counts. These are procedural/code boundaries, not an OS isolation or anonymization guarantee.

The implementation records NumPy/Pandas/Python/Pyreadstat versions and preserves the protocol's limitations on finite-frame dependence, clustering, repeated use of one sample, fixed G draws and development-reference exposure. No statement in the executable report turns the descriptive comparison into independent-cohort validation.

## Verification evidence and remaining execution check

The author reported that all six invented in-memory tests passed after the correction (0.694 seconds). This reviewer inspected those tests; the reviewer did not claim a separate test execution. They cover reproducible/disjoint sampling, count-only rejection and exhaustion, all nine coefficients against an exact orthogonal construction, tied Spearman ranks, the complete 100-by-36 report, discrepancy arithmetic, explicit null retention without resampling, zero differences, and invalid numeric input rejection. The source inspection separately covered the file-backed gate and output paths, which those tests do not exercise against real files.

The next authorized step is root-controlled freeze and one file-backed execution, followed by the separately assigned independent numerical recomputation. That later check must verify actual split membership hashes, all metrics/discrepancies/summaries, unavailable counts and frozen-input invariance without changing the generator or selecting favorable outputs. This review does not substitute for that check and does not claim that it has already passed.
