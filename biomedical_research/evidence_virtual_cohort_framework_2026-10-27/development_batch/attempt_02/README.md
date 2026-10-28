# Retrospective development analysis expansion

This batch processes 144 existing local input datasets: one observed-data reference, three missing-only cases, 120 completions (20 draws × two methods × three masks), and the 20 unique final cohorts from `obesity_paper_replay_2026-10-27`. Initial/final duplicates are excluded. The separate generation-routes project has a single final program cohort and is outside this fixed batch.

Every dataset has 35 records: the frozen paper module's six baseline Pearson correlations, 25 categorical-visit REML contrasts, and four separately identified exploratory standardized pooled associations. The proxy models are not exact reproductions of the publication's incompletely specified coefficients. Previously observed results and this expanded query family are development evidence, never confirmation.

Only follow-up PFS values were artificially masked. Therefore 29 of 35 outputs per completion are exact preservation controls: six baseline correlations, 20 non-PFS time contrasts and three non-PFS pooled associations. They are copied only after exact equality checks on all columns used by those functions, including the full baseline rows. The six affected outputs are computed using the unchanged frozen functions. The shared completion validator independently requires exact preservation of every non-target cell and native missing value. No patient rows are emitted by this batch.

Every CSV is read with `float_precision="round_trip"`, preserving decimal-to-binary conversion consistently across original and 17-digit completion files. All 35 reference and full-synthetic analyses are freshly computed through the unchanged frozen functions. The original source freezes, nested initial/final generation locks, all 120 completion hashes, reference and code hashes are checked before data loads and again before writing results. Original paper output hashes are verified for provenance; their numerical results are not reused. `freeze.json` commits this script, tests, configuration, README, source files and complete dataset registry before smoke/full execution. No generator is loaded, rerun or revised.

This is attempt 02. Attempt 01 remains immutable in the parent directory, including its code, freeze and failed smoke. Its default pandas reader parsed unchanged decimal values inconsistently between source and completion exports; all six smoke completion datasets failed preservation (210 unavailable output rows), and no full batch ran. The correction changes CSV parsing and recomputes the reference/full-synthetic analyses instead of reusing a cache made with the default parser. It does not change any source data, generator, selected outcome, statistical formula or seed.

Twenty completions are Rubin-pooled separately within each method, case and affected outcome (36 pooled results). A failed draw leaves the entire pooled outcome unavailable; failures are retained in the denominator. The approximation does not certify proper multiple imputation or population coverage. No Rubin pooling is applied to full synthetic cohorts. Their 20 draws remain distinct and any min/max range is descriptive Monte Carlo variability. Baseline relationships without provided covariance, source-marginal-constrained trajectories and exploratory proxies have separate labels; agreement on constrained trajectories is not evidence of recovering unprovided dependence.

Each result retains the estimate, SE, interval, status, reference values, signed/absolute error, error in reference-SE units, SE ratio, and interval classification. `positive` and `negative` require intervals strictly on one side of zero; `uncertain` includes zero and does not establish a true null, equivalence or absence of association. The exact available reference is the source's observed-data analysis with native missingness and sampling uncertainty. No inferential CI is computed over correlated outcomes, masks or simulation draws. Normal-Wald mixed-model intervals do not promise exact agreement with the publication's unspecified SAS denominator degrees of freedom.

Commands from this directory with local Python 3.12:

```powershell
python -B -m unittest -v test_batch
python -B run_batch.py freeze
python -B run_batch.py smoke
python -B run_batch.py run
python -B run_batch.py verify
```

Freeze and output creation are exclusive. Do not overwrite an executed batch. Smoke retains the reference, all three missing-only cases, first completion of each of six arms and one synthetic cohort (11 × 35 = 385 records). Full execution retains all 144 × 35 = 5,040 records; 3,480 completion records are unchanged controls and 720 are affected outputs. Tests use only artificial fixtures. `results/summary.json` reports actual counts, failures, elapsed time and limitations; `all_results.csv` contains aggregate analysis outputs, `completion_pooled.csv` the 36 affected pooled outputs, and `full_synthetic_summary.csv` per-outcome descriptive summaries with all 20 draws in each denominator.
