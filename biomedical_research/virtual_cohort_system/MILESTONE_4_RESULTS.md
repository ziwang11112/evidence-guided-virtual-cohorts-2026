# Broader source feedback and a justified retention decision

28 October 2026 · v0.4.0 · Source-only development extension, with no new target evaluation.

## Main result

The framework can now check published medians, quartiles and Spearman correlations, review every source diagnostic across a fixed seed schedule, and retain an existing generator when the evidence does not justify a change. A real-source development run completed with 34 checks, two source contexts, three fixed seeds and initial/final stages. The Agent chose **retain**. All 102 paired check values were unchanged, and all six paired source-output files were byte-identical.

This improves the available feedback and its audit trail. It does **not** demonstrate improved generated-data performance, a superior revision policy, or a new clinical finding.

## What remains promising from M3

In the earlier locked TG evaluation, the generated data preserved the positive adjusted age association and negative BMI quadratic log-TG curvature in all five draws, both before and after revision. The user's intended utility is scientific analysis of generated data, so these conclusion-preservation results remain central.

The exact scope matters. The age endpoint is a pooled adjusted association, not validation of each sex-specific age curve. The curvature endpoint is a full-domain quadratic projection on **log TG**, not a directly estimated local bend or proof of a threshold at BMI 35. A positive linear arithmetic mean can itself produce negative curvature after log transformation. The generator's further curvature choices were assumptions. Source feedback preserved these qualitative conclusions; it did not newly create them.

M3 remains one construction and one cohort. Repeated residual draws are not additional independent clinical validations. Its results and code hashes are preserved in their historical report and Git commit.

## Implemented changes

1. **Faithful source estimators.** Explicit median/quantile operators use linear interpolation; unknown published interpolation methods require a named approximation. Spearman uses average tied ranks and remains distinct from Pearson. Wrong quantile probabilities, unsupported conventions and invalid inputs are rejected or retained as not computable.
2. **Fixed-seed source portfolios.** The new module verifies every scheduled replay, retains undefined checks, rejects missing/failed schedules, and reports each statistic's variation and paired discrepancy changes in its own units. It does not optimize a combined score. Comparisons require unchanged evidence, source recipes and source-interpretation assumption descriptions.
3. **Implementation binding.** Replay report schema 2 binds both replay and operator code. Historical schema-1 reports require their original M3 code version; they are not relabelled as current verification.
4. **Builder/evaluator document boundary.** The generation skill no longer directs builders to the project README, which can contain target results. Source API documentation and evaluator-only analysis design are separate. Project and installed skill references match and both pass skill validation.

The harness contains no biological direction, TG coefficient, preferred curve or automatic scientific success threshold. The Agent still chooses the model and the retain/revise decision.

## Development design

This experiment inherited the M3 final model. Its initial generator and scientific parameters were unchanged. The Agent rechecked the approved original-paper extracts and upgraded five previously unreplayed WHS evidence items without changing their reported values: median, lower/upper quartiles, and two rank correlations. The 29 existing source definitions and all source covariate bytes stayed fixed. A non-generative assumption explicitly records the unreported quantile convention.

The protocol was committed before execution. Seeds 75101, 75102 and 75103 were used at both stages. Each stage executed the same frozen generator/specification in both source contexts through the existing WSL/bubblewrap adapter. No target outputs were regenerated and no target evaluator was run. There was one new Agent review, one permitted revision transition, and **zero scientific parameter changes**.

The two source contexts approximate the [Healthy Twin Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC6911291.1/) and [Women's Health Study](https://jamanetwork.com/journals/jama/fullarticle/208018). Their simulated covariate rows are numerical integration inputs, not newly collected participants. All checks remain approximate because the papers do not identify the full source joint distribution and transfer conditions.

## What the additional feedback showed

These are initial values; final values are identical after retention. Ranges are across three fixed residual draws, not confidence intervals.

| WHS source statistic | Published | Generated mean across draws | Draw range |
|---|---:|---:|---:|
| TG median, mg/dL | 115 | 113.97 | 113.28–115.03 |
| TG lower quartile, mg/dL | 81 | 78.75 | 78.25–79.09 |
| TG upper quartile, mg/dL | 169 | 165.56 | 165.15–166.19 |
| TG–BMI Spearman | 0.33 | 0.3362 | 0.3304–0.3425 |
| TG–age Spearman | 0.18 | 0.2107 | 0.2043–0.2222 |

The Agent identified a conflict rather than treating every discrepancy as a tuning target. Weakening the female age response might reduce the WHS rank correlation, but the other source's generated age-50–59 TG mean was already low: 120.02–122.15 versus 127.8 mg/dL. Its age-30–39 mean already lay around the reported 80.7. Raising levels to improve quartiles would create other source trade-offs. Those proposed consequences were qualitative model diagnoses, not additional executed candidate comparisons.

With unreported joint age–BMI dependence, cohort selection and source reporting ambiguity, the Agent did not find a uniquely justified conditional change. It retained the model and bound all received feedback. This is a defensible example of retention, not proof that no better generator exists or that this decision beats ordinary review.

## Review and boundaries

- Full software suite: **258 passed, one skipped** because Windows denied the symlink fixture. Tests cover estimators, definition mismatches, linkage, tampering, schedule checks and preserving source trade-offs. Separate real isolated executions establish that the implemented path actually ran.
- Six source replays executed successfully, comprising 12 context executions and 204 computed checks. The 102 initial/final paired check changes were all zero. Six paired source-output hashes matched exactly.
- The builder's skill-directed README read incidentally exposed a qualitative historical target-summary sentence. The builder disclosed it and did not read linked results or numerical target outcomes. The interface was corrected after this observation. This run must remain labelled source-only development, not a clean new blinded target experiment.
- Source evidence was curator-provided; autonomous retrieval was not tested. Outer Agent tools remain procedurally restricted, not OS-isolated. Hash receipts bind retained artifacts on a trusted host; they are not adversarial signatures.
- Generator seeds vary residuals only in this submitted model. The generic portfolio API does not assume that every generator behaves this way. Neither these ranges nor repeated rows account for source, structural or transport uncertainty.
- The source contexts assume unreported joint covariates; repeated diagnostic agreement cannot establish population equivalence. No clinical-measurement replacement, causal effect or publication readiness is established.

## Next discriminating experiment

Preserve the current scientific-use goal and change the experiment rather than tune this exposed target. Before opening a fresh target dataset, let the Agent freeze a small set of source-compatible structural alternatives and state which relationships are supplied, assumed or unassessed. Apply the same reserved age, curvature and nuisance-relation analyses to every candidate. Report whether the scientific conclusions survive model choices, alongside effect magnitude and uncertainty limitations.

For curvature, distinguish response-scale and log-scale analyses so a transformation-induced shape is not mistaken for new biology. Keep model alternatives in the Agent's submissions rather than hand-coded biological defaults in the harness. A fresh cohort or collection period must be checked for overlap and evidence contamination before it can serve as confirmation. The concrete evaluator guidance is in [ANALYTICAL_VALIDATION_DESIGN.md](docs/ANALYTICAL_VALIDATION_DESIGN.md); this document is excluded from blinded builder inputs.

## Artifacts

- [Full source diagnostics](reports/source_portfolio_2026-10-28/source_diagnostics.csv)
- [Agent retention decision](reports/source_portfolio_2026-10-28/candidates/final/decision.md)
- [Portfolio and paired comparisons](reports/source_portfolio_2026-10-28/comparison.json)
- [Inspection boundary](reports/source_portfolio_2026-10-28/README.md)
- [Current validation](m4_validation.json)
- [Earlier target results, unchanged](MILESTONE_3_RESULTS.md)
