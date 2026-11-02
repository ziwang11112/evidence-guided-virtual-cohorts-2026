# Actual isolated software-fixture smoke

This directory contains the driver and aggregate records for a source/target
integration test. There are no real biomedical values, patient tables or
production conversion constants in this fixture. Read the [checkpoint](../SOURCE_TARGET_BRIDGE_CHECKPOINT_2026-11-02.md)
and [independent retained-artifact review](INDEPENDENT_LIVE_REVIEW.md).

`run_invented_pair.py prepare <new-local-directory>` writes and freezes a parent,
derives source/target drafts, and emits unsigned binding and unit-map proposals.
It does not execute a generator or create approval decisions. An actual separate
reviewer must inspect these artifacts and supply `context_reviews.json` and
`unit_mapping_approved.json` in that new directory.

`run_invented_pair.py run <same-directory>` checks the approved mapping and its
correspondence to the actual target task before sealing/dispatch. It performs
exactly the declared source (3 rows) and target (6 rows) pair using the existing inspected local
WSL/bubblewrap runtime. There is no host execution fallback, automatic retry or
clinical campaign release. No other platform support is implied.

The driver checks actual lifecycle and feedback outputs, then produces an
in-memory scaled target view with an explicitly invented factor of 2. Its digest
and execution/task binding are retained; the scaled view is not a third
generated table. The two original fixture tables and complete runtime artifacts
stay local. `LIVE_RESULT.json`, `BRIDGE_REPORT.json`, `SMOKE_PLAN.json` and
`UNIT_CONVERSION_RECEIPT.json` are aggregate/metadata records, not clinical
validation or a posterior uncertainty claim.

Actual source geometric mean 2.0 and transformed values were independently
recomputed with different arithmetic, with discrepancy 0.0. No generator was
rerun during that independent verification. The source v1 result remains
unavailable because the declared original statistic is unsupported there; the
supplement reports a descriptive calculation without inventing a strict fit.
