# Independent audit v3 parsing repair

V3 changes only committed generated-CSV float parsing to `float_precision="round_trip"`, through `read_generated_output`, plus its own v3 commitment path/key and identifying text. `V3_EXACT_DIFF.patch` retains the complete exact diff. No regression, weighting, rank, quantile, failure-classification or summary arithmetic changed. An AST fixture confirms every arithmetic/report helper other than the audit dispatch is identical to v2.

The primary providers read CSVs through the harness round-trip parser. V2's default pandas parser could lose one ULP before exact quantile comparison. The new invented fixture serializes the binary float immediately above 0.3 as `0.30000000000000004`: default parsing loses one ULP in the tested environment, while round-trip parsing preserves the exact float. The inverse-CDF selected value must match exactly; no tolerance or adjacent-order-statistic allowance is added.

Only `python -B -m unittest test_recompute_v3_parsing -v` was run: **2 tests passed**. V2's **12 tests were not rerun**; their retained results remain inherited evidence for unchanged arithmetic. New test evidence is in `TEST_RESULTS_V3.json`. Original audit/v2 code, commitments, tests and test records are hash-verified unchanged; review artifacts were not modified. Primary evaluator/providers/generators/release remain untouched.

No clinical-reference artifacts or retained generated outputs were read, no campaign evaluation/comparison was run, and no scientific protocol changed. External independent delta review is required before comparison.

V3 code SHA256: `d225b591b6c3d3f6e54ff9b0fc41f9437b6bfdd8f18f367d52a79db85538e8b4`. The post-test commitment is `CODE_COMMIT_V3.json`.
