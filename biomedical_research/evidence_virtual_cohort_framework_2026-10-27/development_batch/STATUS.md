# Completed batch and preserved failed smoke

The successful batch is in **`attempt_02/results/`**. It completed 144 datasets × 35 outcomes = **5,040 analysis records**, plus **36 Rubin-pooled completion outcomes**, with zero analysis or pooling failures. Runtime was 116.73 seconds. The 31 paper-replay outcomes and four exploratory proxies remain explicitly separated in every result record.

The root-level `run_batch.py`, configuration, tests, README, freeze and `smoke/` are preserved **attempt 01**. Its smoke exposed a CSV-parsing defect: the default pandas reader parsed unchanged source and 17-digit completion decimals inconsistently. All six tested completion datasets failed preservation, retaining 210 unavailable output records. No attempt-01 full batch was run. Do not use that implementation for another analysis.

Attempt 02 uses round-trip parsing for every source/reference/completion CSV and freshly recomputes all 35 reference and full-synthetic analyses through the original hash-frozen analysis functions. It does not reuse numerical results produced with the first parser. Seven artificial-fixture tests passed, including an explicit 17-digit decimal regression fixture. Its smoke produced 385 valid records across 11 datasets before the full batch ran. Neither the source records nor any generator or original analysis code was edited, and no generator was executed.

Across the full 120-completion inventory, 3,480 outputs are unchanged preservation controls and 720 can respond to PFS completion. Only the six affected outcomes within each of six completion arms are pooled. The 20 full-synthetic cohorts remain distinct Monte Carlo draws. Those draws, overlapping masks and related analyses are not independent clinical validation units. All results are retrospective development evidence.

An independent reviewer recomputed all 35 outcomes for one Agent and one statistical-reference completion using the frozen functions. Estimates, SEs, interval bounds, p-values and person/row counts matched exactly, including all copied controls. Source, implementation and smoke hashes remained unchanged. After the full batch, its output manifest was verified and both attempts' source/implementation freezes still passed verification.

Main outputs:

- `attempt_02/results/summary.json`: counts, failures, computation provenance, runtime and interpretation limits.
- `attempt_02/results/all_results.csv`: all 5,040 aggregate analysis records, including estimates, intervals, reference values, magnitude errors and uncertainty states.
- `attempt_02/results/completion_pooled.csv`: 36 affected pooled outcomes with missing-only comparisons.
- `attempt_02/results/full_synthetic_summary.csv`: all 35 per-outcome Monte Carlo summaries, with 20 draws retained in each denominator.
- `attempt_02/freeze.json`: complete pre-execution commitment; `attempt_02/results/output_manifest.json`: output hashes.

These tables contain analysis-level summaries, not patient rows. `uncertain` means an interval includes zero; it does not establish a true null or equivalence. Source-marginal-constrained trajectories, unprovided baseline relationships and exploratory proxy associations require separate interpretation.
