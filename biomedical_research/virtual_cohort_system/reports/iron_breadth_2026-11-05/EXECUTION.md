# Iron generator execution

Run from this directory with Python. `iron_runner.py` passes the agent-authored module, unchanged and bound to its SHA-256, to the WSL Ubuntu 24.04 worker used by the cohort harness. The small bridge passes `n`, `numpy.random.default_rng(seed)` and a context string to `generate(n, rng, context)`. Use `zhu_source` for Zhu's source population and `target` for the requested target population. The ordered DataFrame columns are `hb_g_dl` and `ferritin_ug_l`. Both must be positive and finite.

```powershell
python iron_runner.py --generator PATH --sha256 HEX --author A --stage initial --mode source
python iron_runner.py --generator FINAL_PATH --sha256 FINAL_HEX --author A --stage final --mode target
```

The source call draws 100,000 rows using seed 4101. A revised final program can receive one source replay using that same seed and `--stage final --mode source`. When retained unchanged, its initial replay applies. After the study coordinator releases final construction, the target call draws 5,000 rows per seed (5101, 5102, 5103). An attempt directory can be created only once. Retain failure receipts. The coordinator owns scientific review, source feedback delivery, final authorization and the cross-author closure.

The worker and mount rules come from `cohort_harness.execution` and `cohort_harness/_worker.py`. Bubblewrap isolates the generator process from the network and host workspace, supplies read-only staged files, and bounds time, memory and output. Each run preserves its worker, author, bridge, seed, input hashes, runtime version hashes, execution status and generated file hash. The compact adapter has separate receipts for this pilot. It uses the operator, unit and variable-role checks from `semantic_feedback_v1` for band-level geometric means and deficiency fractions. Raw threshold joint cells and their crude odds ratio are arithmetic derivatives on the same source frame. It does not implement the historical six-author trial controller or its full signed-off semantic manifests.

Generated files remain local under `private_runs/A|B/initial|final/source_4101|target_SEED/output/generated.csv`. Source feedback is `source_diagnostics.json` in the source run directory. Its Table III groups correspond to Hb below 10, 10 to below 12, or at least 12 g/dL. Its cell order is both low, Hb low only, ferritin low only, neither low. Empty groups have undefined conditional statistics. The Cuba study's corrected-ferritin OR is contextual and does not enter this raw-ferritin check.

Run `python -m pytest -q test_iron_runner.py` for the six-row artificial worker and numeric-domain checks. The fixture verifies the strict cutoffs, geometric mean, cross-product OR, file protocol and mounted namespace. The standalone source adapter holds no numerical target references.
