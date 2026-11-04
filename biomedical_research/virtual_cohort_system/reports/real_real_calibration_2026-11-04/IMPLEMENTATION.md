# Implementation scope

`calibration.py` imports without reading data or writing files. The pure helpers
are `sample_disjoint_communities`, `summarize_metrics` and `build_report`.
`summarize_metrics(frame, errors=...)` returns the fixed 36-key mapping; an optional
dictionary receives per-metric unavailable reasons. `build_report` preserves
those reasons alongside every metric mapping and every scheduled split.

The only file-backed entrypoint is
`run(protocol_path, freeze_path)`. It validates the protocol/freeze, both code
hashes, design review hash, historical anchors, four source-file hashes and three
generated-table hashes before exclusively creating `READ_RECEIPT.json` in this
directory. It then decodes the original four SAS files with their approved
column lists and calls only the old pure `prepare_reference_frames` function.
It never calls either old evaluation runner or creates an old receipt. The
reference must contain exactly 6,631 selected people and 218 communities.

The generated CSV schema is exactly `person_id` plus the five analysis variables;
headers and IDs must be unique, IDs must be complete, and the original numeric,
binary-sex, age and positive-measurement scope is checked without filtering.
IDs are discarded before any summary. All inputs and frozen code are rehashed
after evaluation before `REPORT.json` is exclusively created. Existing receipts
or reports are never overwritten. Exhausting the fixed partition-attempt budget
raises `SamplingExhaustedError` with aggregate attempt counts; `run` exclusively
writes `FAILURE.json` with that audit and the failed seed before stopping. A
failed run leaves its receipt and requires
explicit review rather than an automatic retry.

For each seed 8400 through 8499, a fresh PCG64 stream permutes codes of sorted
community labels. The first 109 and remaining 109 define disjoint pools. A
partition is rejected only when either pool has fewer than 3,000 rows. Every
attempt's pool sizes and decision are retained. After acceptance, the same
stream samples R1 then R2 without replacement; selected row positions are
sorted. Both assigned and actually sampled community counts are reported.
Index fingerprints hash the ASCII domain, a NUL byte, and sorted little-endian
uint64 positions. Domains are `real_real:rows:v1` and
`real_real:communities:v1`; no membership arrays or identifiers are serialized.

All 36 metrics and all 100 splits remain in the report. Regressions use
`numpy.linalg.lstsq(..., rcond=None)`. Correlations use centered inner products;
Spearman uses average ranks for ties. Marginal SD uses ddof=1 and quantiles use
linear interpolation. Rank-deficient/nonfinite statistics become null with a
reason; the selected split is retained and unaffected metrics remain available.
Raw schema and value-integrity violations fail the run.

The report includes R1 and R2 metrics; fixed G metrics computed once per table;
signed/absolute R1-R2 and G-R2 discrepancies; and supplemental symmetric
absolute G discrepancy `(abs(G-R1)+abs(G-R2))/2`. Every discrepancy summary is
q10, median and q90 in original units, with scheduled/available/unavailable
counts. No ratio, percentile rank, exceedance rate, p-value, CI or threshold is
computed. Null values are omitted only from their own summary's quantile
calculation, with the omission count always reported.

The six unit tests use only invented in-memory fixtures. They check deterministic
disjoint sampling and hashes, size-only rejection/exhaustion, all nine regression
coefficients against an exact orthogonal construction, average-rank Spearman,
the full 100-by-36 report and discrepancy arithmetic, unavailable metric
retention without resampling, zero differences and invalid-input rejection.

Command (does not execute the file-backed entrypoint):

```powershell
& 'C:/Users/ziwan/AppData/Local/Programs/Python/Python312/python.exe' -B -m unittest -v test_calibration.py
```

Formal execution is reserved for the root task after freeze and code review.
