# ENSANUT 2018 main-study binding

Prepared 3 November 2026. **Execution remains disabled pending independent release.** This is a new developmental reuse of a previously evaluated reference, not a new untouched clinical validation.

The primary task is whole-cohort synthesis: generate age, female, BMI, fasting serum glucose and HbA1c without individual inputs. The new 3,000-row allocation is exactly 375 rows in each of eight age/sex cells. The population, positive-value restrictions, glucose below 126 mg/dL, original anthropometry and fasting/diagnosis restrictions, and equal-cell standard follow the pinned old protocol. The changed row count does not alter the estimand.

## Input packages

- `E0.json`: 17 records containing Lifelines marginal summaries, their duplicate original/converted representations, and measurement-unit guidance.
- `E1.json`: the same 17 records plus 13 records representing two Jansen adjusted projections in original/converted units, the Pani adjusted age coefficient, and eight age-band means. These are 11 additional distinct statistical quantities, not 13 independent observations.
- Per-arm normalization files retain reported/derived roles, uncertainty labels, duplicate groups and printed Jansen interval bounds with unknown confidence level. Pani SEs remain SEs.
- Per-arm registries point only to scoped authored source extracts. **Do not provide the earlier complete human summaries or packet to E0:** those files include relational and quarantined numeric prose outside E0's information condition. Complete article retrieval is not open in this comparison. Existing published-literature knowledge in the base model is not erased; the contrast concerns supplied evidence.
- `case_card.json` is coordinator/reviewer material. The author receives only its arm's allowlisted input files, public task and analysis definitions. Prior private-reference paths and historical controller files are not author inputs.

The old packet's preparation labels remain historical in normalized metadata. Its later root admission receipt is hash-bound in the case card; they are not interpreted as new or missing source admission. Liu's contextual univariate equation and quarantined Jansen Table 3 numbers are omitted from both arms. No new original paper, download, patient row or target result was read.

## Numerical evidence path

`source_operators.py::source_projection` computes a source-population linear projection from a supplied finite moment vector/covariance matrix. Jansen's BMI and glucose regressions remain separate models adjusted for age and sex. Pani's age regression additionally adjusts BMI and glucose.

The helper performs numerical checks and the projection calculation. It does **not** certify that the supplied moments were derived from the submitted generator. A numerical-uptake claim therefore requires retained analytic derivation, explicit source-context assumptions and independent candidate review linking that derivation to the frozen program. In particular:

- A copied source coefficient in a JSON field is not numerical model uptake.
- Target demographic quotas and target-table statistics are not source-population replay.
- Jansen's row-specific sample size and source joint distribution remain uncertain.
- Pani's survey weighting cannot be recovered from published unweighted counts. Its age band >=70 has no admitted upper limit; the target limit of 79 cannot silently truncate it.
- Source plasma to target serum, ancestry, selection, anemia and assay differences remain transfer assumptions.

The new session uses deterministic analytic calculations and at most two target trials; this binding does not launch a new source-row replay mechanism. Age-band integrals may be calculated by an author with a declared source law or marked unavailable. No extra simulation is promised to make every source check computable.

## Exact analyses and generated-only feedback

`generated_feedback.py::evaluate_generated` reads only the current verified generated output and task/profile. It uses the hash-pinned existing `analysis/analytical_engine.py::analyze_cohort` and never reads a real reference. The three primary outputs are:

1. `Q1_age10`: age coefficient in HbA1c ~ age10 + female + BMI5 + glucose10.
2. `Q2_bmi5`: BMI coefficient in HbA1c ~ age10 + female + BMI5.
3. `Q3_bmi5`: BMI coefficient in the full Q1 model.

Q1 and Q2 test target transfer of source-indexed relations supplied in E1. Q3's exact conditional relation is not supplied or algebraically identified by the packet. The additional Q2-minus-Q3 diagnostic is an algebraic contrast of those outputs, not independent evidence or mediation. All endpoints use equal 1/8 demographic-cell weighting. Glucose stays in mg/dL; it must not be confused with CHNS mmol/L.

The case retains all weighted distribution diagnostics and the source-indexed glucose projection. Reference uncertainty is the old 399-attempt cluster stability procedure, not a national confidence interval or automatic acceptance band. Final clinical comparison occurs only after all campaign constructions close.

## Verification and remaining release work

Seven new tests passed: five deterministic moment tests (partial-covariance identity, source context, predictor unit scaling and invalid moments) and two generated-feedback tests (hand-built factorial identities, invalid inputs/quotas). They use artificial arrays without random sampling. They establish arithmetic/interface behavior, not biomedical validity. Historical passed test suites and clinical experiments were not rerun.

The prepared profiles bind two total exploratory attempts (5201, 5202) and three final seeds (5101, 5102, 5103), following the root main-session specification. They do not enable execution. Independent review of the case information split, analytic helper, generated-only provider and global comparator/evaluator release is still required. No root STATE or old frozen artifact was modified.
