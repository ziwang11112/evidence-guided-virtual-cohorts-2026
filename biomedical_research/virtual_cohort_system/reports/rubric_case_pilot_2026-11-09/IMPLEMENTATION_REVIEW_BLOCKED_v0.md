# Implementation review: BLOCK

This review covers trusted execution and aggregate evaluation for `rubric_case_pilot_2026-11-09`. It does not approve the scientific content of unseen authored models. Exact controller/protocol and dependency hashes are bound in `IMPLEMENTATION_REVIEW.json`.

## Blocking findings

1. **IR-01 — Infrastructure failures do not stop the batch.** `runner.py:253–306,310–326` catches unavailable-runtime or launch failures as failed draws and continues remaining seeds, then removes the operation lock. `test_runner.py:98–110,153–162` explicitly endorses this behavior. The evaluation specification requires infrastructure defects to halt. Retain the first receipt and consumed slot, then halt under an audit lock when generator entry is false or unknown; confirmed author-code/schema failures remain counted outcomes.
2. **IR-02 — Integrity failures can be treated as model failures.** `runner.py:292–306,329–370` absorbs staged-input/output-inventory failures, hashes the resulting files, and skips success-only staged/launch checks for failed receipts. Integrity/audit/hash violations must halt regardless of generator entry, retaining the receipt and audit state.

Fix classification and add focused mock tests before execution. No new clinical attempts, post-submission repairs, or retries are authorized by this review.

## Checks satisfied by the inspected implementation

All-six sealing, exact input inventories, AST-only author validation, the native WSL/bubblewrap worker, fixed seed slots, create-only artifacts, immutable closure, and reference-after-closure gates are present. H and L transformations, estimands, eligibility handling, and diagnostic conventions match their trusted providers and endpoint contract. The evaluator retains all scheduled endpoints and failures, reports availability denominators, preserves supplied uncertainty semantics, and does not invent reference values, intervals, pass thresholds, or overall quality scores.

The 10 runner and 7 evaluator passing checks were reported by the parent. Their source was reviewed; tests were not repeated. No models, numerical real-reference payloads, generated clinical rows, or prior candidate outcomes were read. No sampling occurred and no implementation or frozen input was changed.
