# Group 6 independent implementation review

Reviewer: `/root/main_review_g5`. Review is limited to assigned frozen candidates, their task/input/profile/decision and registered sources, plus the permitted skill/interface/schema/lifecycle/controller material. No generator or author script is imported or executed, no participant rows are sampled, no numerical quadrature is used, and no clinical target results or unassigned candidate is inspected. Readiness concerns implementation, source traceability, numerical uptake and mathematical properties; it does not require favorable source or target fit.

## ENSANUT2018_E1_A03 — ready

Candidate: `candidates/initial`; decision: `initial_final`.

- Candidate freeze SHA-256: `f9b271ccd9bcea22826688969a7438c61d41de3d7bd9f461ef1d6fbef019cae1`.
- Decision SHA-256: `87f90f4733821abd9d4593effe8690b6af60f9e69c0f9dcce296c44d642437fd`.
- Retained independent script: `review_ensanut_e1_a03.py`; calculations: `ENSANUT2018_E1_A03_calculations.json`.
- Fresh `lifecycle.verify_candidate(bundle, 'candidates/initial')` and 101 independent checks passed. Frozen candidate and decision files were unchanged.

The code implements the declared standardized beta BMI factor, independent beta glucose residual and independent standardized-uniform HbA1c residual. The affine equations preserve their covariance interpretation. The nested demographic loops guarantee 375 rows in each of eight sex-by-age-band cells, 3000 rows total and 1500 per sex, with integer ages inside inclusive endpoints. The code performs no clipping, rejection or subsequent selection.

Independent enumeration of primitive support corners gives these closure bounds:

| Variable | Lower | Upper |
|---|---:|---:|
| BMI | 19.1656970338 | 44.8357574155 |
| Glucose, mg/dL | 67.7724370617 | 123.0724231854 |
| Target HbA1c, % | 4.5419062467 | 6.7189274502 |

The bounds satisfy task positivity and glucose <126 with clear margins. They are disclosed model supports, not measured clinical limits. Target and Lifelines laws are bounded, so their moments exist. The Pani source law has an uncapped `70 + geometric-failures(p=0.1)` upper age band. It has finite polynomial moments; HbA1c is affine in age plus bounded variables and stays positive. Its remote, biologically implausible age tail remains an explicit approximation. The source context does not silently inherit the target's age-79 limit.

Independent 2×2 algebra derives joint coefficients `(0.004646330742428303, 0.011003290354090355)` from the two separate Jansen projections and assumed BMI/glucose correlation 0.30. The coefficients are not copied as two jointly adjusted slopes. Correct NGSP and glucose predictor conversions use no affine offset. The residual variance `0.06889732901983824` is positive and reproduces the selected Jansen total HbA1c variance after explained variance is removed.

Direct covariance identities from the actual affine equations reproduce every retained mean, covariance and second moment for target design, Lifelines and Pani. Independent Cholesky population projections reproduce Jansen BMI `0.0118924`, Jansen glucose `0.01163828888888889` and Pani fully adjusted age `0.01` in their separately declared source contexts. Positive primitive variances and the nonzero HbA1c residual establish full population rank. Constraint agreement is imposed under assumptions and is not independent validation.

All eight Pani conditional-mean numerators, denominators and age moments were independently checked. The raw discrepancies remain:

| Source age band | Calculated HbA1c | Reported | Difference |
|---|---:|---:|---:|
| 25–39 | 5.365 | 5.20 | +0.165 |
| 40–44 | 5.465 | 5.28 | +0.185 |
| 45–49 | 5.515 | 5.37 | +0.145 |
| 50–54 | 5.565 | 5.40 | +0.165 |
| 55–59 | 5.615 | 5.44 | +0.175 |
| 60–64 | 5.665 | 5.46 | +0.205 |
| 65–69 | 5.715 | 5.50 | +0.215 |
| ≥70 | 5.835 | 5.51 | +0.325 |

These discrepancies are retained scientific limitations. They were not converted to fit scores or assessed against the reported survey SEs. Equal source band probabilities, within-band age laws, cross-cohort intercept transfer, covariate independence and survey simplification are explicit assumptions. Unweighted source counts do not become population weights.

All 30 evidence and normalization records agree with the registered scoped extracts. All 11 operation records are complete: three model constraints and eight analytic checks, with correct source/evidence IDs, preserved uncertainty, overlap, selection and measurement caveats, and reachable parameter/result pointers. All 29 quantitative target-as-source comparisons remain unavailable with correct semantic hashes; NGSP is contextual guidance. Duplicate unit representations are not independent evidence, source SEs are not individual SDs, and unknown CI confidence levels are not turned into precision weights.

This review leaves transport, dependence completion, source selection and assay differences unresolved. Exact source reconstruction, complex-survey replay and target validity are not established. No final-stage action was taken; runtime table validity and finite-sample rank remain for the isolated controller.

## CHNS2009_E1_A04 — ready

Candidate: `candidates/initial`; decision: `initial_final`.

- Candidate freeze SHA-256: `c3f35238a177d3017614b52bb15770f9fb0949d3ef45f06cde0c3e20490a663b`.
- Decision SHA-256: `2ae088987068c566c48c9523f89888c758570f97d2b76d40005edf39b1d5ef68`.
- Retained independent script: `review_chns_e1_a04.py`; calculations: `CHNS2009_E1_A04_calculations.json`.
- Fresh `lifecycle.verify_candidate(bundle, 'candidates/initial')` and 99 independent checks passed. Frozen candidate and decision files were unchanged.

The code implements independent bounded uniform factors, independent target age/sex, and an independent centered Bernoulli glycemic class. It generates the specified 3000 rows and six columns, with integer ages 35–74 and unique synthetic identifiers. This task has no exact demographic quotas. Class probabilities and shifts are disclosed scenario choices; they are not diabetes prevalence estimates or clinical exclusions.

The generator subtracts the class contribution when deriving within-class glucose variance, and subtracts all explained contributions when deriving HbA1c residual variance. The extra HbA1c class coefficient is `kH-betaG*kG`, so substitution gives a total class shift of `kH` exactly once. Independent direct covariance identities and endpoint evaluation through the sequential B/G/H equations reproduce every retained context result. Target within-class glucose variance is approximately `0.52`; HbA1c residual variance is `0.6826240740379911`. Centering preserves means and the resulting total SDs are the specified MIND-derived scenario anchors.

Independent 2×2 inversion gives the shared joint percent-scale coefficients BMI `0.005872569756097562` and glucose `0.197450432`. They derive from the two separate Jansen source projections only after assuming residual correlation 0.25 and nuisance independence. The two source projection coefficients are not inserted as joint coefficients. NGSP conversion adds the offset to the source mean only and scales SDs/slopes by the multiplier; native IFCC covariance is recovered exactly once by the qualified operator.

| Source operation | Independent value | Reported point | Use |
|---|---:|---:|---|
| Jansen BMI, native IFCC per kg/m² | 0.13 | 0.13 | Imposed constraint |
| Jansen FPG, native IFCC per mmol/L | 2.2899999999999996 | 2.29 | Imposed constraint |
| Bao Pearson | 0.6824284695170836 | 0.619 | Analytic check |
| MIND Spearman | Unavailable | 0.529 | Context only |

The Bao raw discrepancy `+0.06342846951708359` is retained. Its separate source context uses declared approximate scales and class assumptions, not exact median/IQR matching. No CI-membership criterion, source precision weighting or favorable-fit requirement was applied. MIND lacks a declared post-imputation source rank law and tie mechanism; contextual use correctly declines numerical uptake. No Pearson substitution or target-correlation assignment occurs.

Primitive-corner extrema independently reproduce target closure bounds:

| Variable | Lower | Upper |
|---|---:|---:|
| BMI | 18.7646170928 | 31.2353829072 |
| Glucose, mmol/L | 3.2784114378 | 10.3215885622 |
| HbA1c, % | 4.0417352370 | 9.6029250393 |

All source contexts also have positive measurement support, and the selected Jansen FPG upper bound is below 7 mmol/L. These bounds follow from the chosen bounded law and are not physiological limits. Every factor and finite mixture branch is bounded; therefore all required absolute moments exist. The independent age/sex directions and successive nonzero U/V/E loadings give positive-definite population covariance; Cholesky verification passed for each context. Independent OLS solutions reproduce target-law implications E1 `0.015760314991354718`, E2 `0.3849415907588688`, E3 `0.005`. The age coefficient is explicitly assumed and not newly inferred.

All 36 evidence records preserve the admitted packet. Registered hashes, marginal and relationship mappings, operation-record hashes, locators, analytic bindings and uptake artifact pointers agree. All four non-marginal operations are fully accounted for, including the contextual MIND record. Source selections, nominal specimen/assay transfer, same-cohort overlap and unavailable estimator uncertainty remain explicit. All quantitative target-as-source comparisons remain unavailable with bound semantic records.

Readiness does not establish target validity, clinical tail adequacy, individual recovery, uncertainty calibration or exact source reconstruction. Latent class assumptions, nuisance effects, composition and population/assay transfer remain unresolved. The reviewer generated no participant rows, imported no candidate/author script and performed no final-stage actions; realized finite-sample rank and table validity remain for isolated execution.
