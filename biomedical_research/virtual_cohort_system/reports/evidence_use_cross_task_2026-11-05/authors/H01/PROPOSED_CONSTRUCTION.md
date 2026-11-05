# H01 proposed whole-cohort construction

This is a complete prospective law, awaiting controller scientific review. It was selected without target observations or desired analysis values. Implementation will use the program route and actual specification values; no generator or candidate exists yet.

## Population and design

Exactly 3,000 fictional adults: 375 in each crossing of female=0/1 and age bands 25–39, 40–54, 55–69, 70–79. Within a cell, integer age is discrete uniform across its inclusive range. Row identifiers will be unique synthetic strings. Equal-cell WLS is ordinary equal-row-weight regression because all eight cells have exactly 375 rows. The cohort represents the task's already selected population (no prior reported diagnosis, glucose<126, recorded fast/anthropometric availability), not a national prevalence sample. Unrepresented diagnosis, fasting-duration, anemia/medication and anthropometric-documentation fields are not fabricated or claimed independently verified.

Let A=age, F=female, B=BMI in kg/m², G=fasting serum glucose in mg/dL and H=HbA1c in percentage points. All innovations below are mutually independent conditional on the stated parents; their independence is an assumption rather than an absence-of-report inference.

## Full law and numerical choices

1. **BMI**: B = 12 + 53 U, U~Beta(6.853607923773584, 15.834788076226413), independent of A and F. The exact chosen mean is 28.01 and SD is 5.00 kg/m². Mean uses the Pani NHANES summary as a location anchor; SD, bounded-beta shape/support and age/sex independence are author assumptions. The bounds 12 and 65 constrain the virtual population to a broad severe-underweight to severe-obesity range and exclude more extreme cases; they are not empirical target cutoffs or post-hoc clipping. Pani's flat age-category BMI pattern motivates testing an age-flat law but does not establish independence or sex equality.
2. **Glucose**: conditional normal kernel with location

   mG = 94.0 + 0.18(A-50) - 4.4496(F-0.5) + 0.432(B-28.01),

   kernel SD=10.0 mg/dL, conditioned on 0<G<126. Draw G from this truncated distribution with A,F,B fixed; do not resample A/B/F when glucose is rejected. The construction is a conditional law inside the already selected target population, not an asserted prediagnosis selection mechanism. Location94 and SD10 are assumptions informed only by the reported roughly 90–100 mg/dL locations and marginal scales in admitted sources. Age0.18 mg/dL/year is an assumed smooth representation of Pani's approximate 8-mg/dL age rise; no exact source age slope is claimed. BMI0.432 and female-4.4496 are converted Finnish S1 slopes used as kernel parameters, with explicit fasting/selection/continuous-age/population transport assumptions.
3. **HbA1c**: define gamma = 0.23*0.73/12.4 = **0.013540322580645161 points/(mg/dL)**. This is a Kerman **marginal** covariance-derived scale, adopted as a **conditional** coefficient by assumption, not by statistical identification. Then

   betaB = 0.0125 - gamma*0.432 = **0.006650580645161291 points/(kg/m²)**,

   betaF = 0.023 - gamma*(-4.4496) = **0.08324901935483871 points**,

   mH = 5.45 + 0.010(A-50) + betaF(F-0.5) + betaB(B-28.01) + gamma(G-94).

   H = mH + R - 1.05, where R~Gamma(shape=9, scale=0.11666666666666667). Thus E(R)=1.05, SD(R)=0.35, and the HbA1c conditional mean is exactly mH. The residual SD0.35 and skew/shape are explicit assumptions; marginal source SDs, SEs, correlations or confidence bounds are not substituted for this conditional SD. HbA1c is not truncated at 6.5 because the target permits high HbA1c despite low fasting glucose. Intercept5.45 is a chosen location near source middle-age 5.4–5.5% values, not a fitted Mexican mean. The age0.010 slope is the transported Pani NHANES adjusted relationship. betaB and betaF are **cross-source model decompositions**: they assume the unadjusted-for-glucose Finnish BMI/sex coefficients and the chosen glucose kernel can approximately coexist with gamma. Their numerical arithmetic does not identify a biological direct effect.

The residual gamma distribution was selected to allow moderate right skew with finite moments and a positive H lower bound; it is not evidence of a specific erythrocyte process. No interactions, latent postload-glycemia factor, medication/anemia mixture or measurement error model is included. Those omissions are explicit unassessed structure, not proven absence. No term is tuned to significance or favourable random seeds.

## Finite moments, limits and transformations

A,F,B,G are bounded. R has finite moments of every positive integer order; H is a bounded affine term plus R and therefore also has all such moments finite (and an mgf in a neighbourhood of zero). The conservative global HbA1c lower bound from the declared supports is approximately **2.7291%**, so no HbA1c positivity repair/clipping is necessary. The gamma upper tail is unbounded; extraordinarily high theoretical HbA1c remains a model limitation. No claim that the full physiologic tail is established is made.

Glucose uses proper rejection or inverse-CDF truncation, never winsorization. Rounding of glucose/HbA1c will not be added merely to look like instrument precision, because that would alter equations and introduce artificial ties. Requested regressions use age10=(A-50)/10, bmi5=(B-25)/5 and glucose10=(G-100)/10; changing a centering constant does not change slopes. Positive scale conversions preserve percentage-point interpretation; H=5.5 means 5.5%, not a proportion0.055.

## Analysis-specific evidence use and assumptions

| Analysis | Proposed evidence-use choice and parameter | What remains assumed |
|---|---|---|
| Q1_age10: H~1+age10+female+bmi5+glucose10 | `relationship`: E_PANI_AGE -> age coefficient0.010/year; `dispersion`: residual0.35 via declared assumption | US-to-Mexico transport; plasma-to-serum measurement bridge; no identical fasting/documentation filter; source-survey versus equal-cell estimand stability; linear age over25–79; residual independence/structure |
| Q2_bmi5: H~1+age10+female+bmi5 | `relationship`: E_FIN_BMI -> nominal reduced BMI0.0125 and its decomposition through betaB/gamma/glucose BMI0.432; relevant glucose/dispersion nuisance parameters linked | Finnish HbA1c/medication selection can be ignored for the transferred slope; binary-to-continuous age adjustment; extension outside30–64; conditional covariance bridge; truncation changes the nominal source regression slightly |
| Q3_bmi5: H~1+age10+female+bmi5+glucose10 | `relationship` with evidence **and explicit assumptions**: betaB=0.0125-gamma*0.432; E_FIN_BMI/E_FIN_G_BMI/E_KERMAN_COV. `check_only`: E_HOORN_CONTEXT | No matching source Q3 coefficient exists. The cross-source decomposition and conditional use of marginal gamma identify this *constructed model*, not the target. Hoorn negative quartile contrasts do not license a negative continuous target slope or rebut this model at the same adjustment set |

In the eventual schema, each link's population/measurement/selection/conditioning/adjustment/scale mismatch will have explicit bridge assumptions shared with unresolved gaps and parameter provenance. Dispersion will be labelled assumption-only where appropriate. Check-only sources will have no numerical parameter paths. No precision-weighted pooling, LLM confidence weighting, or implication that repeated seeds are new evidence is proposed.

## Deterministic implications already checked

Retained `analytic_calculations.py` integrates the declared distribution with Gauss–Jacobi BMI quadrature and exact discrete age/sex summation; it neither samples random numbers nor creates person-level tables. 128 and 256 nodes agree to numerical precision. These are **model implications**, not target observations or source-validation results:

* Glucose's actual projection on A,F,B after truncation has BMI slope **0.42468973**, age0.17752915 and female-4.38537494; the BMI kernel0.432 was not silently called the final projection.
* Q1_age10 model expectation **0.10000000** percentage points/10 years.
* Q2_bmi5 model expectation **0.06200508** percentage points/5 kg/m², slightly below the nominal transported0.0625 due to glucose truncation. No adjustment is proposed to force equality.
* Q3_bmi5 model expectation **0.03325290** percentage points/5 kg/m². This is a prediction of the assumed decomposition, not a directly reported source relation.
* Model mean/SD: glucose94.6393/10.7832 mg/dL, HbA1c5.4974/0.43143%. Marginal G–H Pearson r≈0.43716. This differs from Kerman r0.23 and HbA1c SD0.73 because the Kerman marginal scale was repurposed under a conditional bridge and different population/design. The mismatch is not hidden or described as a matched correlation.

## Later implementation/check plan, subject to review

After controller review, create exactly the required `candidates/initial` program/specification/evidence/decision/check artifacts plus analysis-evidence, whole-cohort feedback, source-semantics and evidence-use sidecars. Record actual static/schema checks; source review/calculation records will be bound auxiliary artifacts. Root alone will freeze/execute the assigned trial and final draws through the supplied adapter. No local random draws, direct-row submission, scenario draws, or generator fallback execution will be used.

Checks should distinguish (a) design/schema validity and finite-moment arithmetic, (b) model-implied requested regressions and source-context mismatch, and (c) unsupported source checks. Exact Hoorn adjusted regressions are not computable with absent waist/hip/2hPG/lifestyle data. Pani weighted age-specific quantiles and Finland predictive margins are not independent validation of this selected equal-cell population. Any generated-only feedback will be inspected with its declared estimand and exclusions; a correction will require a concrete extraction, implementation or qualified source discrepancy, not a favourable target sign. Query budget is exhausted; no further source query is planned.

The output supports inspection of one explicit, evidence-informed hypothetical law. Q1 is relationship-supported with transport assumptions; Q2 is materially assumption-dependent; Q3 is a decomposition-dependent analysis with no directly matched source coefficient. It does not establish causal effects, nationally representative prevalence, target accuracy, measurement savings, or publication readiness.
