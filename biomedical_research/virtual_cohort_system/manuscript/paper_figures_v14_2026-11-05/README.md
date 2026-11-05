# Figures for manuscript v0.14

Figures 1–5 and S1 are byte-preserved from the preceding edition. Figures 6–7 are byte-preserved from the independently reviewed cross-task study; all six constructors and final seeds are shown. No clinical data or generated rows were read to prepare this package.

- [Figure 6: analysis results](fig6-cross-task.svg): association effects and residual dependence, in native units, compared with existing sample references.
- [Figure 7: dispersion](fig7-dispersion.svg): marginal and residual spread; agreement on one coefficient does not establish a complete distributional match.
- [Portable aggregate-only plotting source](render_cross_task_aggregates.py) and [aggregate results](../../reports/evidence_use_cross_task_2026-11-05/evaluation/RESULTS.json).
- [New study interpretation](../../reports/evidence_use_cross_task_2026-11-05/RESULTS_ZH.md).
- [Preserved earlier figure package](../paper_figures_v13_2026-11-04/README.md).

Seed ranges represent Monte Carlo variation under fixed models. Reference bands retain their original uncertainty meaning; they are not equivalence thresholds. The TC reference slope interval crosses zero. These studies reuse exposed references and do not establish fresh clinical confirmation.

Run `python render_cross_task_aggregates.py --results /path/to/RESULTS.json --out /path/to/new-output-directory` with Python and matplotlib. It checks the reviewed aggregate hash and reproduces both PNG figures pixel-for-pixel. The historical experiment reporting driver additionally requires its local harness/bundles and is not the portable plotting entry.
