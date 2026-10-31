# Independent aggregate-only case interpretation

**Decision: simplify the claim; stop work on this exposed reference; continue only with a new, prospectively blinded validation study.** This case demonstrates a working evidence-to-cohort workflow and consistent association directions. It does not establish quantitatively reliable transfer of the prespecified age or BMI analyses, recovery of an unreported joint distribution, or a generally reusable substitute for measured cohorts.

Reviewed on 2026-10-31 using the protocol, admission, initial scientific review, source diagnostic reports, production aggregate endpoints and independent postrun aggregate audit. No participant/generated rows were read, and no model, fit or simulation was run or changed. The independent numerical audit reports MATCH with zero mismatches. This supports computational correctness under the fixed estimators, not scientific validity.

## What the fixed analyses show

All slopes below are HbA1c percentage points per stated increment. A/B are the two constructions. Their entries are **derived descriptive arithmetic means across their three prespecified seeds, with the observed seed range**; they are not pooled clinical estimates or uncertainty intervals. Finals retain the initials unchanged.

| Endpoint | Finite reference [empirical stability band] | A mean [seed range] | B mean [seed range] |
|---|---:|---:|---:|
| Q1: age, per 10 years; sex/BMI/glucose adjusted | 0.07513 [0.06712, 0.08219] | 0.09789 [0.09532, 0.09986] | 0.10073 [0.09591, 0.10444] |
| Q2: BMI, per 5 kg/m²; age/sex adjusted | 0.08364 [0.07037, 0.09521] | 0.05884 [0.05867, 0.05904] | 0.05538 [0.05032, 0.05876] |
| Q3: BMI, per 5 kg/m²; age/sex/glucose adjusted | 0.05664 [0.04390, 0.06801] | 0.02426 [0.02372, 0.02478] | 0.02119 [0.01631, 0.02811] |
| Q2 − Q3: coefficient change on glucose adjustment | 0.02701 [0.02197, 0.03242] | 0.03458 [0.03426, 0.03494] | 0.03419 [0.02896, 0.03960] |
| Glucose, per 10 mg/dL; age/sex adjusted | 0.11420 [0.09996, 0.12929] | 0.11910 [0.11593, 0.12252] | 0.11385 [0.10466, 0.12267] |

Directions agree for all four primary quantities across all six unique outputs. Magnitudes do not: every Q1 exceeds its reference stability band, and every Q2 and Q3 lies below its band. Mean Q1 is approximately 30%/34% higher, Q2 30%/34% lower, and Q3 57%/63% lower for A/B. These descriptive discrepancies are substantial relative to the reference values; no post hoc equivalence threshold or statistical rejection rule is introduced. The glucose diagnostic is much closer, but its band overlap establishes neither equivalence nor broad transport success.

Q3 is a useful prespecified, not-directly-calibrated check: its positive direction survives glucose adjustment in both generated and measured data. Its small generated magnitude is a failure of quantitative agreement here. It is not an independently discovered relationship: the source projections and the assumed joint law already constrain it. Q2 − Q3 shows attenuation in this case, without evidence of causal mediation. Relative attenuation, calculated as the ratio of the descriptive means, is about 59%/62% in A/B versus 32% in the reference. A's absolute coefficient change exceeds the reference band in all seeds; B's does in two of three. The remaining B seed is within the band, which is not evidence of equivalence.

**The Q3 error cannot be assigned solely to unknown covariance.** Let Δ = Q2 − Q3. The identity Q3 = Q2 − Δ gives reference-minus-generated Q3 shortfall = Q2 shortfall + generated-minus-reference Δ excess. Applied to the seed means:

| Descriptive decomposition, percentage points per 5 kg/m² | A | B |
|---|---:|---:|
| Q2 shortfall | 0.024803 | 0.028259 |
| Δ excess | 0.007577 | 0.007184 |
| Q3 shortfall | 0.032380 | 0.035443 |

Thus about 77%/80% of the arithmetic Q3 shortfall is already present in Q2; only 23%/20% is the added excess coefficient change. These are an accounting identity, **not causal shares** of error. Covariance can affect both quantities, and selection, transport, measurement and model shape can also matter. No intervention on an assumption was evaluated, so neither covariance nor any competing explanation is isolated. The stronger claim that Q2 transported and only the additional adjustment failed is contradicted by these results.

The distribution diagnostics also limit reuse: mean BMI is 26.37/26.30 versus 28.66 kg/m², mean HbA1c is 5.387/5.419 versus 5.314%, and Q1 residual RMS is 0.258/0.256 versus 0.488 percentage points. Matching some associations or a glucose mean does not recover the observed dispersion or multivariable analytical behavior.

## Source fidelity, dependence and evidence limits

Both source reconstructions reproduce several supplied marginals and projections approximately. Lifelines BMI slopes are 0.01053/0.01215 versus supplied 0.0118924 per kg/m²; Pani age slopes are 0.009918/0.009649 versus 0.010 per year. Yet Pani's ≥70 HbA1c mean is 5.633/5.657 versus 5.51%. Agreement with selected calibration quantities coexists with source age-pattern mismatch. The source feedback is neither uniformly exact nor a validation of transfer to ENSANUT. Source reconstruction, selection differences, plasma-to-serum comparability and target transport remain distinct issues.

A/B share a conditional Gaussian family, linear HbA1c law and residual BMI/glucose correlation 0.30. Their close coefficients therefore provide little structural robustness evidence. Independent authoring is not independent clinical replication. Pani/Liu also overlap in NHANES. Three seeds per construction assess only finite-generation variability conditional on fixed assumptions, not parameter/model/transport uncertainty or three independent clinical cohorts. Both finals were retained: 12 scheduled analytical slots contain six unique outputs, and there is no observed iterative improvement attributable to source feedback.

The reference comprises 6,931 selected observations standardized to eight equally weighted age/sex cells, not the Mexican national population. All 399 cluster-resampling attempts were valid, but their bands describe stability of this finite reference under the specified perturbation scheme. They do not establish population truth, resolve selection/measurement error, or supply national design-based confidence coverage.

## Minimum next study and decision rule

Preserve this case as a transparent feasibility and quantitative-transfer limitation result. Do not tune the exposed ENSANUT reference or recast a revised fit to it as confirmation. Stop claims of reliable unseen conditional inference or iterative benefit from this experiment.

The minimum useful continuation is one genuinely unexposed external dataset family with a frozen measurement/eligibility definition and the same separation of evidence-only builders from the evaluator. Before revealing its results, freeze (1) a simple direct aggregate/projection-transport baseline, (2) genuinely distinct, source-defensible dependence/functional-form alternatives and their uncertainty handling, and (3) scientifically justified magnitude tolerances for Q2, Q3, Δ and distribution/residual diagnostics. Preserve every model and seed; test the non-calibrated projection alongside its source-indexed predecessor so errors cannot be reassigned after exposure. This is a proposal for a new protocol, not authorization for additional work in this closed case.

Continuation is justified only as a falsifiable test of whether joint generation adds analytical value beyond the simpler baseline while meeting those prospective tolerances. If it again supplies only directions while missing prespecified magnitudes, simplify the application to assumption-conditioned scenario generation and stop the claim of reliable quantitative cohort transport. One successful new case would be limited external evidence, not general validity, superiority across methods, or a publication guarantee.
