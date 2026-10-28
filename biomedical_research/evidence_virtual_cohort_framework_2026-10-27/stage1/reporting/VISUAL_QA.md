# Scientific figure inspection

All six final PNGs were reopened and visually inspected with `view_image` after rendering on 2026-10-28 UTC. The corresponding PDFs are vector exports from the same Matplotlib figures.

| Figure | Visual checks |
| --- | --- |
| `case_a_reserved_correlations` | Six panels; all lineages/scenarios; real intervals and point estimates visible; literal currency labels and three-decimal limits preserve the small positive PFS–DD100 lower limit; no clipping. |
| `case_b_reserved_correlations` | All six changes; clear shorter endpoint labels; every reference interval visibly includes zero; complete 15-row context inventory in each panel. |
| `case_c_reserved_correlations` | All six changes; clear differences among target, persistent and shared/discordant alternatives; no row or scenario omitted. |
| `case_a_reserved_proxy_associations` | All four exploratory coefficients; separate reference bands; full context inventory; captions qualify proxy analysis and scenario interpretation. |
| `case_b_paired_uncertainty` | Four endpoint panels; log-scale ratios labelled numerically; reference ratio 1; body-mass extremes retained; sample size and real paired correlation shown. |
| `case_c_paired_uncertainty` | Four endpoint panels; 44 versus 43 endpoint-pair denominators displayed; readable ratio axes and all context rows. |

Final ordering is uniform across every PNG, PDF, scenario key and detailed table: ordinary, P1 target (7), P2 alternative (7), P3 alternative (6), repeated for lineages 1–3, followed by the three statistical contexts. A prior draft sorted scenario names; it was regenerated before delivery. No files using that earlier ordering remain among the six named deliverables.

Markers summarize generated-cohort aggregate estimates: dots are individual draws, diamonds medians, and lines min–max. They are never presented as synthetic confidence intervals. Gray bands in relationship plots show the real unadjusted 95% interval. Colors distinguish ordinary/proposed/statistical contexts, with row labels providing a non-color cue.

The reporting script also verifies all 825 display summaries against the frozen evaluator, checks 495 ordinary-versus-each-proposed term rows and validates the P1/P2/P3 allocations. Results are saved in `aggregate_reporting_validation.json`. No participant rows were accessed for reporting.
