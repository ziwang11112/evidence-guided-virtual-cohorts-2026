# Building the task rubric

A rubric specifies what the output needs to do and how it will be assessed. A skill supplies procedures for doing and checking it. The rubric should change with the research request; the procedure library should be reusable. Existing provenance or parameter-reference schemas are useful inputs, not evidence that a scientific criterion has been met.

## Select relevant criteria

| Criterion family | Task-specific question | Evidence of completion |
|---|---|---|
| Requested data and analysis | Are the requested variables, units, preserved observations and analysis definitions represented? | Actual schema and preservation checks; the requested estimator runs or a precise missing prerequisite is documented |
| Adopted source relationships | Does the construction preserve the exact adopted statistic in its stated source context? | Recomputed matching estimator or explicit derivation, with original conditioning, measurement, selection and uncertainty |
| Variation needed for the use | Is dispersion, subgroup heterogeneity or residual variation adequate for the specific analysis? | Relevant distributional or variance checks; source-supported scale separated from a shape/transfer assumption |
| Joint structure needed for the use | Does the joint law support the required adjusted relationship, interaction, repeated measures or threshold combination? | The actual requested analysis on the output and, where possible, model-implied quantities or valid source replay |
| Sensitivity and permitted claims | Does the conclusion depend on an unmeasured or unreported quantity? | A specific dependency and its consequence; justified sensitivity results if authorized and feasible |

These are a menu, not five mandatory scores. Split a criterion when its analyses require different evidence. Do not reward unrelated analyses, agent counts, verbose reasoning or model complexity. A clinical threshold is a task input requiring justification, not a universal property of a rubric.

## Criterion record

Record the following in the task's requested format, or a concise table if no schema is supplied:

- `id`, `analysis`: the scientific use and exact estimator/contrast.
- `basis`: user requirement, permitted source with locator, algebraic consequence or explicit assumption.
- `reference_role`: task invariant, source reconstruction, supplied-reference calibration, external-reference evaluation, or no numerical reference.
- `check`: calculation, input population/measurement and necessary tool.
- `comparison`: measure and any justified tolerance/uncertainty rule established before output inspection; otherwise descriptive only.
- `finding`: actual result and artifact; distinguish computed results from planned checks.
- `assessment`: demonstrated for the stated scope, contradicted, unresolved, or not applicable with reason.
- `next_action`: action tied to the finding and the requested use.

Keep coverage and correctness separate: 10 declarations with no executable evidence are not 10 passed numerical checks. A justified missing-evidence finding can be correct reasoning while the corresponding data-use criterion remains unresolved. Do not aggregate these states into an invented 0–100 biomedical-validity score.

## Scope and reference handling

Correct reproduction of a source statistic is useful even when the target reference is absent. It does not establish transfer. A provided real-data statistic may be used when the task permits it; label the comparison as calibration. A reference retained for independent evaluation must stay out of construction and revision. Lack of independent reference does not forbid generating explicitly assumption-dependent data for exploration.

Check scientific plausibility under the modeled measurement: latent quantities and noisy recorded values may require different constraints. Do not impose an intuitive bound without deciding which variable is represented. Record overlap between source studies before interpreting apparent agreement or uncertainty.

## Example of different requests

For an adjusted exposure–biomarker regression, record the adjustment set, coefficient scale, design and relevant residual variation. For a prevalence calculation, prioritize the threshold definition and probability mass around it; exact participant-level values need not be recovered. For power planning, variance, dependence, sampling design and uncertainty require substantially stronger support than agreement in the sign of a mean relationship. The same virtual table may have different support for these three uses.
