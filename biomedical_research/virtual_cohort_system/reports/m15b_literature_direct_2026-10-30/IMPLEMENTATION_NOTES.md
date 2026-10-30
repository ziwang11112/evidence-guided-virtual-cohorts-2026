# Implementation notes

M15-B1, 30 October 2026. These are interface/operation observations, not target results.

- The existing source-check documentation listed operators without the full native recipe envelope. The builder correctly paused rather than inventing an interface. The controller supplied the schema and explicitly permitted reading `cohort_harness/source_checks.py` for packaging. `docs/SOURCE_CHECKS.md` now documents the existing envelope; no harness behavior or scientific rule changed.
- One controller validation command supplied `candidates/initial` to a CLI argument that accepts the simple name `initial`. It failed before validation/execution with `Use a simple candidate name`. The corrected command passed, reporting the direct-row route and `generator_executed: false`. No data changed.
- The gateway's conservative study-alias filter rejected an independent Ferrara article because its discussion cites NHANES; its original cohort was verified before explicit controller admission. An unsupported DOCX supplement was acquired at its already-discovered original URL. Both attempts count against the existing case budget. Raw originals remain local and full exposure is recorded.

The interface fixes do not establish analytical accuracy or turn assumption-derived age/curvature choices into observed evidence.
