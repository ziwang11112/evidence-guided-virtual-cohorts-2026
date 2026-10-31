# Independent M17-B recomputation

`recompute_m17b.py` is independent of the custodian's array-based numerical evaluator. It uses statsmodels formula fits, HC3 covariance, and patsy prediction contrasts for the eight locked effects. It records all six distribution summaries, both Pearson correlations, all eight quota counts, generated-minus-reference differences, stage realization ranges, and paired final-minus-initial effects. It separately counts scheduled stage tables, unique paths, and unique content hashes.

The script never imports or runs a candidate. Real-table audit requires the root release manifest's exact authorization string plus the pre-release endpoint-exposure hash. The auditor must also receive root's explicit instruction before invoking this mode. The current state is pre-release readiness only.

Before release, record a snapshot of the finished artifacts using the `snapshot` command. `--file` can be repeated for initial/final frozen files; `--directory` also freezes directory membership and should be used only once that directory is complete. Snapshot only permitted source/candidate/protocol files, never the private reference. An initial static-review snapshot is already supplied. A separate final snapshot should include final candidate code/specification, decision/feedback records, source packet, and protocol after root declares them complete. The snapshot itself should be bound into the root's release record if practical.

Example command shape, with absolute paths supplied by root:

```text
python recompute_m17b.py snapshot --output PRE_RELEASE_SNAPSHOT.json --directory FINISHED_CANDIDATE_DIRECTORY --file PROTOCOL
python recompute_m17b.py audit --release TARGET_RELEASE.json --reported-results custodian/results/evaluation.json --artifact-snapshot PRE_RELEASE_SNAPSHOT.json --output-dir NEW_AUDIT_RESULTS_DIRECTORY
```

Every release-bound input and every snapshot artifact is checked before and after calculation. An existing output directory is rejected. All eight endpoint fields and diagnostics in `evaluation.json` are compared at relative tolerance 1e-8 and absolute tolerance 1e-10. Failed endpoint calculations are recorded rather than silently omitted. A result marked `review_required` retains discrepancies and scheduling failures; it is not a scientific success threshold. For normal runs, table validation enforces integer ages 20–79 from the task contract as well as the protocol's eight quotas and value domains.

The `self-check` mode uses only an invented arithmetic fixture, verifies known formula/contrast results, and never reads a source or real table. It passed under Python 3.12 with numpy 2.4.5, pandas 3.0.3, patsy 1.0.3 and statsmodels 0.15.0 after correcting the formula-metadata compatibility issue documented in the initial review.
