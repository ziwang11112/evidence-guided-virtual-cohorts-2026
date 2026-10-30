# Source-only M11 location audit

The evidence supports a useful, assumption-labelled calibration experiment, but does not identify a unique source conditional intercept. The paired comparison should hold the evidence, source covariate table, age/BMI effects, residual law and random seeds fixed. Change only the sex-specific additive location using the source marginal-median operator described below. Improved agreement with fitted source medians is mechanical; independent source diagnostics and the custodian's target analysis determine what else changed.

The original extraction audit read only the assigned ha/f and hb/final evidence, model specification, generator text and replay recipe, plus source packets and primary publications. It did not read participant covariates/outcomes, target reference tables, M10 result estimates or project history. At that audit's completion no generator had been executed or candidate created. The subsequent controller-authorized construction and source-only replay are recorded separately in `source_screen_completion.md` and `source_screen_summary.json`; biomedical generation uses the supplied isolated adapter only. The compact extraction, hashes and original read ledger are in `source_evidence_packet.json`.

## Statistical definitions and source context

[Masuch et al. 2019](https://link.springer.com/article/10.1186/s12902-019-0338-7), Table 1, provides the unweighted analyzed SHIP-Trend cohort's age median 53 (quartiles 40,64) years and BMI median 27.5 (24.5,31.0) kg/m². Results paragraph Par20 supplies HbA1c medians 5.3% in men and 5.2% in women, with respective quartiles (5.0,5.8) and (4.8,5.6). These are marginal quantiles, not conditional locations. Table 2's whole-cohort age coefficients are BMI-adjusted linear-regression mean slopes: 0.153 (SE0.011) and 0.191 (SE0.011) percentage points per decade, men and women respectively. Both whole SHIP-Trend strata have no fitted spline term. Using these slopes as shifts of a conditional median additionally assumes an additive location family with covariate-invariant residual law.

The source uses Bio-Rad Diamat HPLC and includes diabetes and medication use in its whole cohort. Its n4402 analysis excludes pregnancy and missing HbA1c from the n4420 baseline cohort. Its selected healthy n987 subset and pooled healthy reference intervals are different estimands and should not calibrate these whole-population generators. Published quartile interpolation conventions and sampling uncertainty are unspecified. HbA1c and source covariate quartiles are rounded.

[Völzke et al. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4390827/), Table 1, gives raw baseline counts by sex and age bin:

| Age bin | Men | Women |
|---|---:|---:|
| 20–29 | 190 | 194 |
| 30–39 | 309 | 388 |
| 40–49 | 414 | 465 |
| 50–59 | 456 | 475 |
| 60–69 | 408 | 435 |
| ≥70 | 368 | 318 |
| Total | 2145 | 2275 |

Those counts identify sex-specific coarse age distributions in the n4420 baseline, not the exact n4402 HbA1c sample. The age/BMI values of the 18 excluded people are not reported. The final age bin has no upper limit in this table. Masuch describes sampling ages 20–79; baseline examinations can include older attained ages. Treating the last bin as 70–79 therefore imposes a disclosed task-support truncation/compression, not a recovered source maximum.

Völzke Table 2's male/female BMI medians 27.8/27.0 are weighted with poststratification and inverse participation weights. Its parentheses are confidence intervals, not quartiles. They should not replace Masuch's unweighted BMI distribution or provide residual/BMI spread. Figure 2 displays sex BMI distributions and Figure 3 age-specific obesity, but no numeric raw age–BMI correlation was recovered in this bounded audit.

A context cross-check is [Großmann et al. 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10855893/), Table 1's explicit whole-baseline column: age mean51.96/SD15.46, BMI mean28.12/SD5.23 with seven missing BMI values. Its n203 study subset is a separate column. These are pooled moments and the same cohort, not independent evidence. They are recorded for review but are not required for the primary calibration pair and should not enter it without controller admission.

## What the existing two scientific families imply

Both inherited families set sex locations to the published marginal medians at age49.5 and BMI27. Their age effects are 0.0153 and 0.0191 per year. Their conditional-reference interpretation is expressly assumed. Neither original artificial source-X recipe represents the actual published age distribution.

Family ha retains BMI effect `0.18*tanh((BMI−27)/7.5)`, residual `scale_s*(exp(0.4*Z)−1)` with scales1.2/1.05, and bounds3–20. Family hb retains BMI effect `0.02*(BMI−27)`, residual `0.95*(exp(0.5*Z)−1)`, and no clipping. BMI effects, residual shape/scale and transport remain inherited assumptions; this experiment does not identify or refit them.

A median-zero residual does not make the marginal median equal the location after covariate mixing. In particular, the median of a sum generally is not the sum of its medians. Changing only the reference age to the source median, or subtracting effects at median age/BMI, fails to account for this convolution. Replacing a median with an arithmetic-mean formula would change estimands.

## Fixed source-X proposal

Use reported sex/age-bin counts, with equal probability across integer ages within each decade. For the primary context, map the open ≥70 bin to70–79 to stay inside the inherited age support; label this as an approximation. Report the resulting pooled age quartiles against Masuch53(40,64), and retain discrepancies instead of adjusting bins until they match. Midpoint-based age means under this assumption are derived values52.365 in men and51.195 in women, not reported source means.

Use the same pooled BMI marginal within each sex because raw sex-specific quartiles are unknown. A transparent quantile model matching all three reported BMI quartiles is:

`Q_B(u) = 27.5 + s_side*Phi_inverse(u)`

where `s_left=(27.5−24.5)/0.67448975` and `s_right=(31−27.5)/0.67448975`. Bound it at15–50 kg/m², inherited numerical source support rather than a published minimum/maximum. The distribution is an asymmetric normal-quantile approximation, not an estimated parametric truth. It reproduces the three quartile anchors while avoiding any inference of independence from non-reporting.

Freeze three source scenarios before calibration or target evaluation:

1. **Primary:** published age-bin marginals; pooled BMI quantile law above; age and BMI independent within sex.
2. **Dependence sensitivity:** identical marginals, Gaussian-copula latent correlation+0.35 within sex. This is an explicitly chosen moderate positive association, not an extracted estimate. Keeping the marginals fixed isolates dependence sensitivity.
3. **Tail sensitivity:** the same+0.35 copula, but a positive right-tailed quantile law `Q_B(u)=27.5*exp(t_side*Phi_inverse(u))`, with `t_left=log(27.5/24.5)/0.67448975` and `t_right=log(31/27.5)/0.67448975`, again bounded15–50. Quartile anchors stay fixed. Comparing this with scenario2 isolates the consequence of a different tail form.

These three scenarios are a bounded sensitivity set, not draws from a posterior or a validated uncertainty interval. They do not cover all feasible joint distributions. The optional top-bin70–84 variant is scientifically useful but requires the controller to admit an enlarged source age domain; do not silently violate task support. If it cannot be admitted, record that older-source-age sensitivity was not run.

An approximately44,200-row context (ten times the baseline counts) allows exact reported age-bin proportions and integer within-bin balancing. Freeze covariates and any source-context construction seed before fitting locations. The same context is used for both members of each pair. Source-X replication improves numerical integration only; it does not increase clinical evidence. If memory/runtime require fewer rows, state the deterministic rounding deviations.

## Generic additive-location calibration

For each family and sex, retain the original age/BMI functions and residual law. Define `T_s = beta_s*(A−49.5)+g(B)+R_s`. Let the reported marginal source median be `m_s`. Set the calibrated location to `c_s = m_s − median_source(T_s)`. Equivalently, solve the monotone scalar equation `E_source[F_Rs(m_s−c_s−beta_s*(A−49.5)−g(B))]=0.5` for each sex.

For the inherited shifted-lognormal residual, `F_R(r)=0` if `r<=−scale`, otherwise `Phi(log(1+r/scale)/sigma)`. This makes deterministic CDF integration/bisection mathematically possible, but the controller's fixed M11 contract requires calibration from actual frozen source executions. Use that execution-backed operation below; do not substitute local generator execution or use the analytic alternative to bypass the adapter. The operation has one scalar degree of freedom per sex; no BMI/age/residual parameters or signs are changed.

For each scenario, execute the frozen initial candidate with the identical source covariate table and all three prespecified source seeds94101,94102,94103. Pool the verified generated HbA1c rows across these three seeds within each sex. Compute the pooled type-7 median `q_s` (not the average of three medians), and set `c_s_new=c_s_initial+m_s−q_s`. Retain source execution/output hashes, all three seeds, the selection and estimator, the computed median and signed offset, and the resulting location. Freeze a new specification with only those location values changed, then replay it. The source outcomes used here belong to an invented published-source context, never the target. All source seeds contribute equally; no best seed is selected. Use the predeclared table only and keep the original scientific generator bytes identical.

For ha, the target medians5.3/5.2 are strictly inside the3–20 output bounds, so clipping does not change the CDF equation at the median. It can change tail or regression diagnostics. Pure location shifts leave within-sex coefficients and IQRs invariant before clipping; ha clipping can break exact invariance, and its nonlinear BMI term plus age–BMI dependence can change the OLS coefficient under the replay's linear BMI adjustment. Such findings should be reported rather than tuned away.

The controller's fixed bounded comparison is one initial plus three scenario-calibrated specifications per inherited family. Label scenario1 the primary and scenarios2/3 sensitivity alternatives; retain all of them. Use target seeds93101,93102,93103 only under custodian evaluation, giving24 target tables across two families and four specifications. The source scientist neither reads those tables nor selects among versions using their utility. Do not select a scenario, offset or candidate using target utility, a desired sign, or a source residual seed.

The initial and revised arms must receive identical admitted evidence and replay contexts; otherwise changing source evidence/context and location simultaneously makes the intervention ambiguous. Median agreement is a fitted source check. Hold out IQRs and BMI-adjusted age coefficients as descriptive trade-off checks; they are not independent publications or target validation.

## Remaining limits

Sex-specific raw BMI laws, within-bin ages, age–BMI dependence, conditional residual heterogeneity and source conditional intercepts remain unidentified. The count/HbA1c subset mismatch is small in row count but its exact effect is unknown. Evidence rounding makes calibration to many decimal places numerical convenience only. Cross-sectional source age slopes do not establish individual aging effects or causal effects. Population, assay, treatment and calendar-time transport to the intended target remain unassessed by source calibration.

Stop the design search here: there is enough source information to define a reviewable bounded experiment, and more selected-subset papers would add mismatched estimands rather than identify the missing joint law.
