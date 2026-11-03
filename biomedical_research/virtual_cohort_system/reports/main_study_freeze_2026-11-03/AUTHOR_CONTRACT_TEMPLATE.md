# Main-study scientific author contract

This is a task-specific, evidence-guided whole-cohort construction. You choose the scientific model, parameters and documented transport/completion assumptions. The purpose is usable virtual biomedical data for the visible analytical requests. No particular sign, effect size, distribution family or favorable result is required. A transparent decline or unsuccessful construction remains a result.

The dispatcher supplies one session directory, its `bundle/task.json`, `profile.json`, admitted evidence and scoped source summaries, source-operation descriptions, and the following interface documents. Read only those approved inputs and your own outputs. Do not read sibling conditions, other authors, coordinator case cards, old experiments, patient records, target statistics, result reports, or repository-wide summaries. This is a procedural information boundary; your general tools are not host-isolated. No new browsing or downloads are allocated to this already curated main comparison.

Use the installed `evidence-cohort-generation` skill and its harness interface. Scientific code executes only through the supplied isolated controller; do not run the generator, sample rows, or make local Monte Carlo/calibration draws yourself. Deterministic analytic calculations are allowed with their actual scripts, inputs and outputs retained. Do not substitute numerical quadrature or large random draws without declaring how they were computed. Two exploratory table attempts are shared across the entire construction. Failed execution consumes a slot. Three final seeds are fixed before authoring. The coordinator's controller performs those executions; creating a new folder or candidate does not renew the budget.

## Deliver a scientific candidate

Write `bundle/candidates/initial/` with `generator.py`, `model_spec.json`, `evidence.json`, `decision.md`, `checks.json`, `whole_cohort_feedback.json`, and `source_semantics_v1.json`. Use exactly the allowed scientific variables, units, selection and generation design in the task. `generate(observed, spec, seed)` returns a DataFrame and receives `observed=None`. Put all scientific constants in the specification with evidence/assumption provenance. Any technical or scientific support limits must be disclosed rather than presented as known population cutoffs.

Source-population replay is not supplied in this allocation. Target-table feedback must mark source comparisons unavailable. The versioned semantic interface checks declared meanings; it does not turn a target table into a source-population reconstruction. The supplied analytic projection functions may evaluate a law's separately specified source-context moments. Those moments must actually follow from your model, with population/selection, units, conditioning and remaining assumptions stated. A matrix of desired moments without a demonstrated relation to the generator is not evidence of numerical uptake.

Include `numerical_uptake.json` as `{"records": [...]}`, one record for every admitted non-marginal operation, with:

- `operation_id` and source/evidence IDs;
- `use`: `model_constraint`, `analytic_check`, `context_only`, or `declined`;
- actual parameter/constraint/analytic artifact paths for numerical uses;
- the source-context population/selection and measurement assumptions;
- source uncertainty treatment and cross-source overlap;
- what the input identifies and what your construction assumes;
- a reason when an operation is contextual, unavailable or declined.

E0 has no non-marginal records; its empty list is valid. E1 is not compelled to accept incompatible evidence. A literature citation alone is not numerical uptake. Separate adjusted regressions are separate population projections, not interchangeable coefficients of a single combined equation. Unsupported cross-covariances are not zero facts. Multiple unit representations of one reported statistic are one piece of evidence.

Include `mathematical_properties.md`: establish that variables and the required model moments exist under your actual probability law, including any exponentiation, unbounded quadratic term, mixture or clipping. Finite output on a few seeds does not establish finite population moments. Distinguish residual variation, uncertain external estimates, structural uncertainty and population transport. Do not claim individual measurements are recovered.

## Optional feedback and final decision

You may request at most two total exploratory executions through the coordinator, using seeds 5201 and 5202, and see your own generated diagnostics. These are not clinical target answers. You may use the remaining allowance to revise after a concrete finding, or retain if no supported change is warranted. Preserve the initial candidate unchanged after its freeze. Keep any revised candidate separately and bind the actual feedback used. Do not report a retained model as an improvement.

At conclusion write `decision.json` outside the candidate:

```json
{"author_id":"assigned id","candidate":"candidates/initial","action":"initial_final","reason":"concise scientific stopping rationale"}
```

Allowed actions are `initial_final`, `retain`, and `revise`. An independent reviewer checks the committed code/specification, source uptake and mathematical properties. Readiness does not require a favorable source fit or anticipated target outcome. Once the final configuration is selected, no scientific changes or exploratory trials are allowed. The controller then attempts all three fixed final seeds 5101, 5102 and 5103. Failures and unavailable statistics remain in the record. All cases and conditions close before common target-reference evaluation.

No private reasoning trace is requested. Deliver the model, evidence/assumptions, executable calculation artifacts, actual check records and a concise decision rationale.
