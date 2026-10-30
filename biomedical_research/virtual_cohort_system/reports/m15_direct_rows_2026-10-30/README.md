# M15-A direct Agent-authored rows: source-only audit packet

This packet records one fresh Agent's literal authorship of 128 fictional rows from 20 supplied summaries in Yun et al. (2021), DOI 10.1038/s41366-021-00810-9, Table 2 Adult cohort. After one numerical feedback pass, the Agent retained its table unchanged. Initial and final are two frozen versions of one unique table.

Supplied moments had 1.10% mean absolute relative discrepancy; all four withheld same-source urate SDs were too small, averaging 29.53% relative error. This demonstrates a direct-table submission and feedback/retention path. It establishes neither a repair benefit nor independent biomedical or clinical validation. Exploratory regressions and quartiles describe the authored joint structure and have no empirical correctness labels.

## Contents

- `PROTOCOL.md`, `precommit.json` and the reviews preserve the information boundary, original commitments and independent findings.
- `aggregate.json`, `source_feedback.json` and `postrun_audit_numbers.json` contain aggregate summaries, validation metadata and artifact hashes.
- `source_excerpt.md`, `initial_model_spec.json`, the two decision files and `revision.json` document the screened evidence, declared assumptions and retain decision.
- `controller.py` and `independent_recompute.py` are verbatim audit code. They require the original local `work/m15a_direct_rows_2026-10-30` layout and its retained inputs; this selected archive is not a standalone executable evaluation package.
- `manifest.json` binds every packet file except itself and records each copied file's original local path.

Generated row CSVs, original source XML/full papers, private row-level inputs and local state remain outside this packet. References to their paths and hashes preserve provenance without distributing their bytes. No row table, evaluator, generator, calibration or scientific test was run during export. See [the milestone report](../../MILESTONE_15A_RESULTS.md) for the reviewed interpretation and limits.
