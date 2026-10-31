# Independent admission design critique

2026-10-31. Read-only methodological review of the autonomous-cycle protocol, M17-B reference interpretation and whole-cohort feedback specification. No patient files, new papers, target results or generator runs were inspected. NAGALA is a provisional candidate; the statements below are admission requirements, not verified claims about its metadata.

## Target and admission

Use one baseline record per eligible participant and define the target as the released, processed adult health-exam cohort under its documented exclusions. It does not automatically represent all Japanese adults, all clinic attendees or the original enrolled cohort. Record recruitment, dates, measurements, units, exclusions, processing, missingness and access terms before admission. If essential provenance cannot be resolved, defer admission rather than infer it from observed distributions.

Builders receive external published aggregates, eligibility metadata and a variable dictionary, with no individual source or reference records. Record overlap at study-family level. Statistics from the reference study supplied to builders would make corresponding checks source-consistency checks; they would not independently validate transport. Choose variables and analyses before target-result access, according to availability and evidence, never observed agreement.

## Three feasible primary estimands

Conditional on metadata confirming age, sex, BMI, fasting glucose, triglycerides and HDL cholesterol, freeze these baseline descriptive associations:

1. **BMI–glucose association:** the BMI coefficient in the additive linear projection of fasting glucose on BMI, age and sex, reported in verified glucose units per kg/m².
2. **Triglyceride–HDL association:** the log-triglyceride coefficient in the linear projection of HDL cholesterol on natural-log triglycerides, BMI, age and sex. Require positive triglycerides; define handling of invalid measurements prospectively.
3. **Sex modification of BMI–triglyceride association:** the BMI-by-sex coefficient in the projection of natural-log triglycerides on BMI, age, sex and BMI-by-sex. Freeze sex coding and explicitly identify the contrast.

These ask about glycemic association, lipid coupling and subgroup heterogeneity. They are statistical projections within the selected cohort, not causal effects. Freeze transformations, adjustment sets, inclusion/missingness rules and estimator definitions; supply no desired signs or magnitudes. The third estimand is especially vulnerable to weak external constraint. Label each endpoint source-constrained, unprovided or weakly identified after evidence review. If required variables or adequate evidence are unavailable, revise the protocol before target access or defer the case.

Published fully adjusted coefficients are not interchangeable with these projections. Omitted smoking, alcohol, medication or other covariates can change a coefficient even without transport failure. A source check must reproduce its actual adjustment set and population or explicitly remain approximate/noncomputable. Do not synthesize an absent covariate merely to claim an exact match.

## Eligibility and uncertainty

If eligibility excludes elevated glucose or another generated biomarker, generation must represent the distribution conditional on that restriction. Generating an unrestricted population and filtering afterward changes the whole joint distribution. Direct conditional generation or a declared parent-population selection model is acceptable; arbitrary clipping is not an equivalent selection model. Report exclusion violations and any prespecified rejection mechanism. Relationships within a restricted glucose range cannot validate unrestricted metabolic relationships. Unavailable eligibility variables require an explicit conditional-population assumption.

For the finite released cohort, reference coefficients are fixed descriptive statistics once the analysis is fixed. To describe uncertainty for a hypothetical population of similarly selected attendees, report HC3 intervals under independent-participant assumptions; use participant/cluster resampling only when the documented design justifies it. Neither approach corrects selection, measurement error, undocumented processing or transport to national populations. State this inferential scope beside the intervals.

For each frozen output, report the reference estimate, generated estimate and generated-minus-reference discrepancy. Keep seed variation separate from evidence, parameter and structural uncertainty. Generated row counts cannot increase measured information. Without defensible prospective usefulness margins, report discrepancies and uncertainty without declaring equivalence from shared signs, interval overlap or nonsignificant tests. Prespecify a few relevant diagnostics: eligibility violations, missingness, biomarker tails and covariate support.

## Verification and optional mechanism test

An independent checker should recompute all three estimates from identical frozen outputs and verify units, exclusions and file bindings. Agreement establishes arithmetic reproducibility, not biological correctness; shared assumptions and source dependence remain unresolved.

Add a controlled source-condition ablation only if admission exposes a concrete ambiguity about pooling differently selected studies that could change the generator. Include compatible and heterogeneous conditions, paired handling variants, identical evidence/budgets and a frozen small schedule. It can isolate selection-handling behavior; it cannot establish real biomedical transport. Otherwise omit it and spend the bounded cycle on the independently reserved observational reference.
