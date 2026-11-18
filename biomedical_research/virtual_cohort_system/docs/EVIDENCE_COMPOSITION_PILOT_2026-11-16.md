# Completed evidence-composition pilot

On 16 November 2026, the user authorized wiring the shared evaluator to isolated execution, freezing the design and completing 24 small experiments. The unit is now complete.

Two artificial task families (covariate adjustment and repeated measurements) each used four information conditions and three independent GPT author contexts. Every author chose its own scientific law and parameters. A frozen generic schema connected the existing API client to the existing WSL/bubblewrap execution backend. There were 24 API calls, no revisions/retries, and three fixed draws of 3,000 people per author. No real patient dataset was used.

| Identified primary relation with both evidence records | Mathematical value | Range of generated author means | Mean absolute error across nine draws |
|---|---:|---:|---:|
| Covariate-adjusted X–Y residual correlation | .21875 | .2211–.2230 | .00731 |
| Correlation of within-person changes | -.60000 | -.6013–-.5991 | .01492 |

The positive/positive-to-negative repeated-measure example is useful: the source correlations .8 and .52 constrain different components. All three complete-evidence authors combined them to generate the correct negative change association, rather than inserting either source correlation directly into that analysis.

All 90 identified primary/secondary estimates satisfied fixed numerical tolerances, as did 738 source diagnostics. All 72 requested-estimand identification labels were correct for the supplied task definitions. Incomplete evidence admits alternative completions, so those arms are not scored as wrong simply because their chosen scenarios differ from the complete-evidence world.

All 24 programs and 72 executions were audited. A separate covariance-based route recomputed all 216 analyses (maximum discrepancy 1.17e-15). The 72 output files contain 57 unique numeric tables excluding person IDs; neither seeds nor duplicated tables are independent authors. All programs use nondegenerate Gaussian laws and have finite moments. This is a small controlled result, not clinical transport validation or workflow-superiority evidence.

Requested/returned model: `gpt-6.1-sol`, high reasoning, default service. Returned-usage tariff estimate: **$0.6540764**, below the frozen $6 cap. Full requests, outputs, exact inputs, program seals, usage and execution receipts are local.

The audit also confirms why analysis-use labels must follow assumption dependencies: a DERIVED parameter may still depend on an ASSUMED parent. The pilot's analysis labels correctly preserve that distinction; origin tags alone would not suffice.

The next decision is source admission for one existing biomedical analysis that needs a joint/conditional constraint. No automatic new dataset/model expansion, exposed-target tuning, manuscript rewrite or expired automation restart follows from this unit.

- [Full results](../work/evidence_composition_pilot_2026-11-16/RESULTS.md)
- [Protocol](../work/evidence_composition_pilot_2026-11-16/PROTOCOL.md)
- [Freeze and exact file bindings](../work/evidence_composition_pilot_2026-11-16/FREEZE.json)
- [Implementation review and decision](../work/evidence_composition_pilot_2026-11-16/IMPLEMENTATION_REVIEW.md)
- [Figure](../work/evidence_composition_pilot_2026-11-16/analysis/evidence_composition.png)
- [Complete author-level analysis table](../work/evidence_composition_pilot_2026-11-16/analysis/constructor_analyses.csv)
- [Code and integrity audit](../work/evidence_composition_pilot_2026-11-16/analysis/CODE_AND_INTEGRITY_AUDIT.json)

This document is an original aggregate summary. Raw model calls, generated rows and local work artifacts have not been publicly synchronized in this unit.
