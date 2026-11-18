# Stage 1 scientific proposal: revise the two residual scales

Decision: **revise**, subject to independent source-only review. The new supplement supplies dimensional BMI slopes from the same Finnish cohort that supplied the baseline nested R-squared values. Together they support two conditional residual-SD ratios, under stated interpretation and projection assumptions. I propose using those ratios to replace the baseline glucose and HbA1c working residual scales, while retaining the BMI scale and the existing model structure. This is a substantive, assumption-dependent development change; neither source fidelity nor target improvement has been demonstrated.

No candidate has been generated, validated, frozen or executed in this stage. No target rows, old execution results or evaluation results were read. The original E01 files remain unchanged.

## Newly used source information

The primary source is PMC6458679, Additional file 3, continuous-BMI blocks for the general Finnish population (Health 2011 reference, n=653, age 30-64). In Table S2 the BMI coefficient is printed as **0.0125**, p<0.0001, adjusted for binary age (30-44 versus 45-64) and sex. In Table S1 it is **0.0240**, p<0.0001, with the same age/sex indicators and fasting-time adjustment according to the main Methods. Its fasting coefficient and coding are not given. These values were checked against the admitted converted visible text. Main article XML Table 3 confirms R-squared pairs 0.0660/0.1164 for HbA1c and 0.1174/0.1642 for glucose.

The appendix does **not** label either outcome's units, explicitly label the slopes unstandardized, or provide coefficient SEs/CIs. I choose the working interpretation that Table S2 uses HbA1c percent and Table S1 glucose mmol/L, with unstandardized slopes per kg/m2. Intercepts near 5 for HbA1c and 4-6 for glucose, main-text physical BMI definition, and main glucose thresholds support this interpretation; it remains an assumption. Preserve the printed, unit-unlabelled values in evidence. The interpreted glucose slope is 0.0240 × 18.0182 = **0.4324368 mg/dL per kg/m2**; this is a declared conversion of an interpreted value, not a directly printed result. Threshold p-values will not be converted into precision weights, SEs or individual dispersion.

The Finnish analysis is survey-weighted, with binary age, 4-17-hour fasting, complete cases, and exclusions for diagnosed/registered/treated diabetes, HbA1c >=6.5% and glucose >=7 mmol/L. The target is the specified Mexico analytical design, age 25-79, exactly eight equal age-sex cells, continuous age adjustment, recorded 8-12-hour fasting and no reported prior diagnosis, glucose <126 mg/dL, and no HbA1c upper exclusion or verified medication/anemia exclusion. These are different populations, selection rules, conditioning sets and weights. The supplement is part of the same Finnish cohort as the main table, not independent replication.

## Source operators and what their algebra identifies

Let B be BMI. For the source HbA1c operator, Z_H contains an intercept, I(age 30-44), and male (reference female). The reported quantity is the survey-weighted linear-projection coefficient of B in H ~ Z_H + B. For glucose, Z_G additionally contains fasting time with incompletely reported coding, and the operator is the weighted coefficient of B in G ~ Z_G + B. Source coefficients and R-squared must refer to the same sample, weights, outcome and conventional nested-projection R-squared within each outcome. These alignments are plausible from the article but cannot be fully verified without the analysis details.

Under those conditions, r_YB.Z = sign(beta_B) sqrt[(R2_full-R2_base)/(1-R2_base)], and beta_B/r_YB.Z = SD(Y residualized on Z)/SD(B residualized on Z). Applying these identities yields:

| Source-derived quantity | Value | Status |
|---|---:|---|
| r_BG.ZG | 0.23027191091657706 | Same-source conditional projection algebra; reported slope supplies sign |
| r_BH.ZH | 0.23229605270598924 | Same-source conditional projection algebra; reported slope supplies sign |
| s_G.ZG / s_B.ZG | 1.8779398593546361 mg/dL per kg/m2 | Depends on glucose unit interpretation and conversion |
| s_H.ZH / s_B.ZH | 0.05381064316155604 percentage points per kg/m2 | Depends on HbA1c unit interpretation |

These are ratios, **not recovered absolute residual SDs**. Z_H and Z_G differ. The source supplies neither their common residual covariance matrix nor HbA1c dispersion conditional on age, sex, BMI and glucose. It would be incorrect to claim that the appendix reports the new variances below.

## Exact minimal model change

For the target construction, transport both ratios and both partial correlations to a common residual base Z_T = (intercept, continuous age, female). This specifically assumes invariance across binary versus continuous age, omitted/fixed fasting context, source versus target weighting, populations, age range, measurement and selection. It also assumes that the two different source BMI-residual denominators can each be represented by the same target BMI residual scale. This is a substantive unresolved assumption, not an algebraic identity.

Retain the baseline target BMI residual SD **s_B=3.8 kg/m2**. Its source is the Kerman low-FBS subgroup's marginal SD, transported as a residual scale; it is not a Finnish residual SD. Retain baseline r_GH=0.23 as an assumed target age/sex-residual correlation. Its evidence remains Kerman's *raw* Pearson correlation, including some known diabetes cases, so its transport and raw-to-residual interpretation are unverified. No new evidence resolves this joint-covariance closure.

Choose s_G = s_B × (0.0240 × 18.0182)/r_BG = **7.136171465547617 mg/dL**, and s_H = s_B × 0.0125/r_BH = **0.20448044401391294 percentage points**. These replace 12.4 and 0.30612807415479226 respectively. Retain the existing triangular covariance algebra:

```
b_G = r_BG*s_G/s_B
b_H = (s_H/s_B)*(r_BH-r_BG*r_GH)/(1-r_BG^2)
g_H = (s_H/s_G)*(r_GH-r_BG*r_BH)/(1-r_BG^2)
v_G = s_G^2*(1-r_BG^2)
v_H = s_H^2*[1-(r_BH^2+r_GH^2-2*r_BG*r_BH*r_GH)/(1-r_BG^2)]
```

The exact parameter changes are:

| model_spec parameter | Static baseline | Proposed |
|---|---:|---:|
| residual_moments.glucose_sd | 12.4 | 7.136171465547617 |
| residual_moments.hba1c_sd | 0.30612807415479226 | 0.20448044401391294 |
| glucose.bmi_slope | 0.7514136040435673 | 0.4324368 |
| glucose.variance | 145.60685248130525 | 48.2246402839392 |
| hba1c.bmi_slope | 0.015256066586887239 | 0.010190399159585504 |
| hba1c.glucose_slope | 0.004601604141344884 | 0.005340898000388721 |
| hba1c.variance | 0.08557424216967495 | 0.038180384887393407 |

All other scientific constants and distribution families remain as in the admitted baseline. In particular: eight fixed cells; integer uniform age within cells; B=15+30 Beta(6.20467382040628,8.102798478762697), independent of age/sex; scaled-beta glucose on (50,126); gamma HbA1c with constant conditional variance and no upper cap. Independent innovation draws are retained. With A=age, F=female, the proposed means are:

```
m_G = 91.2 + 0.2*(A-43.8) - 5.40546*(F-296/525)
      + 0.4324368*(B-28.01)
m_H = 5.4 + 0.010*(A-52) - 0.08301*(F-0.52)
      + 0.010190399159585504*(B-28.01)
      + 0.005340898000388721*(G-93.07681062857144)
```

For glucose, p=(m_G-50)/76, k=(m_G-50)*(126-m_G)/v_G-1, alpha=p*k, beta=(1-p)*k. For HbA1c, gamma shape=m_H^2/v_H and scale=v_H/m_H. The existing generator can implement this law by specification changes only, plus a distinct candidate identifier prefix if the controller supplies a new bundle.

The old Kerman glucose SD12.4 and NHANES age-50-54 upper-percentile-derived HbA1c scale remain evidence/context, but cease to determine these two scales. Remove the active normal-scale assumption and update provenance accordingly; do not delete the reported mean/quantile evidence. The old r_BG/r_BH numeric values remain, with their signs now supported by source coefficients. No broad new mechanism, interaction, fitted target parameter or additional candidate is proposed.

This choice prioritizes dimensioned BMI slopes plus within-study relative-dispersion information over the baseline's combination of Finnish standardized associations, Kerman glucose dispersion and a normal approximation from an NHANES HbA1c quantile. It does not establish that Finnish relative dispersion transports better. In particular it deliberately narrows both target outcome residual distributions; the complete scheduled diagnostics must expose any resulting trade-offs.

## Consequences for Q1, Q2 and Q3

With the requested transformations and exact equal-cell design, the following are population linear-projection implications of the proposed law, not simulated estimates or target observations:

| Analysis | Static baseline implication | Proposed implication | Interpretation |
|---|---:|---:|---|
| Q1_age10, glucose-adjusted age | 0.10000000 | 0.10000000 percentage points/10 years | Retained NHANES conditional-age transport; supplement does not supply a continuous-age replacement |
| Q2_bmi5, age/sex-adjusted BMI | 0.09356887 | 0.06250000 percentage points/5 kg/m2 | 5*(b_H+g_H*b_G); equals interpreted Finnish slope only through the declared target transport |
| Q3_bmi5, additionally glucose-adjusted BMI | 0.07628033 | 0.050951995797927516 percentage points/5 kg/m2 | 5*b_H; depends on the unverified HbA1c-glucose correlation closure |

The Q2-Q3 difference is an omitted-variable projection identity within the chosen law, not demonstrated causal mediation. Q2 has a more direct dimensional source anchor than before. Q3 is not newly identified by the supplement. Q1's source basis is unchanged. None is validated for Mexico; all remain sensitivity-construction analyses. Three seeds assess simulation variability, not uncertainty in evidence or transport.

## Checks, unresolved matters and source-feedback boundary

Actual checks: source text/table inspection, static generator/spec inspection and constant-only arithmetic in `proposal_constant_calculations.py`, saved in `PROPOSAL_CALCULATIONS.json`. The correlation determinant remains 0.8647193686793377. Over the full predictor support, m_G is 79.45618706057142 to 108.63475106057143, minimum beta variance cap is 1018.2070486682462 > v_G, and m_H is 4.727509255184533 to 6.062139478001639. All beta/gamma parameters are positive. Conditional SDs are 6.944396322499113 mg/dL for glucose and 0.19539801659022388 percentage points for HbA1c. Bounded predictors and positive bounded gamma parameters preserve finite moments; rank is supported by the unchanged varying covariates and nonzero innovations but must still be checked on each executed table.

Unresolved: appendix units and coefficient precision; exact R-squared convention and coefficient/R-squared alignment; differing source adjustment sets; transporting relative scale and partial correlations; Kerman marginal-to-residual BMI SD; raw-to-residual HbA1c-glucose correlation; selection and assay differences; linearity, homoscedasticity and tails. The original sex and age assumptions remain, including Taiwan's age-only sex coefficient used as fully adjusted and Finnish glucose predictive margins used as a conditional sex contrast. The new Finnish appendix sex coefficients differ from those retained choices; this proposal does not reproduce the full Finnish regression equation, its intercepts, its absolute R-squared or all its margins. No uncertainty distribution over parameters is justified.

Any later supplied source-statistic checks must use **semantic_feedback_v1** and preserve the original source operator. Weighted Finnish coefficients/R-squared with binary age and unobserved fasting coding cannot be re-labelled as unweighted continuous-age target regressions. Exact source replay is not proposed: source weights, joint covariates and fasting coding are unavailable. Where the implemented interface cannot represent these, mark them unsupported/non-computable with that reason. Constant identities above are algebra checks only. Existing range-restricted target-versus-source descriptive comparisons remain approximation diagnostics, explicitly not source replay, and may deteriorate for the retired glucose-SD or HbA1c-quantile anchors. No target outcome may be used to change this scientific law after freeze.

The machine-readable proposal records the exact files read and parameter mapping. JSON parsing passed; 16 input files were hashed and all manifest-listed files read matched their admitted hashes, recorded in `PROPOSAL_READ_INTEGRITY.json`. These are format/integrity checks, not harness candidate validation. The evidence-cohort-generation skill and its harness interface guided the source boundary and evidence/assumption separation.

This stage recommends proceeding to independent review of this one proposal. If its relative-scale transport is judged inadmissible, retain the old candidate and stop; the mere successful retrieval of the appendix does not require generation.
