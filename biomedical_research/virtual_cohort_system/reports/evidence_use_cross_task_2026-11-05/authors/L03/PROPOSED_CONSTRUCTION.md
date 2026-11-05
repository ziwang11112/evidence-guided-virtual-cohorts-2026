# L03 proposed joint law (source review phase only)

The output would contain 3,000 iid rows with unique string IDs and exactly `age`, `sex`, `bmi`, `total_cholesterol`, `hdl_cholesterol` after `id`. Lipids remain in mmol/L. The single proposed construction is an evidence-informed rural external-population scenario; target demographic/lifestyle proportions are unavailable. All three requested analytical uses are **partial / assumption-dependent**, not directly reported or validated target estimands.

## Sex and age

Let F be Bernoulli(0.5), mapped to literal F/M. The balanced probability is an explicit scenario parameter, not a source or target estimate. No source health exclusion is applied as a target filter.

Given sex, draw an independent uniform U on (0,1). Age quantile knots at probabilities 0, .25, .50, .75 are [18,24,33,46] for M and [18,25,34,48] for F. For the first three intervals, interpolate linearly. For U>.75, put v=4(U−.75) and age=q75+(90−q75)*(1−sqrt(1−v)). This keeps age in [18,90] and makes the upper-quarter density decrease linearly toward 90. The three interior quartiles come from rural Malawi; interpolation, continuous-age convention and cap90 are assumptions. The target minimum18 is prescribed. No rounded quartile is asserted as an exact source-population value.

Assume (BMI,TC,HDL) is independent of age conditional on sex. This is a deliberate simplifying scenario because the admitted evidence does not identify age dependence; absence of reported coefficients is not evidence of independence. Its consequence is that age adjustment does not alter population lipid–BMI projections after sex adjustment, and the model may miss age-related confounding or nonlinearity.

## Biomarker law and numerical parameters

Variable order is B=BMI, T=TC, H=HDL. Draw Z~N3(0,R), independent of F and U. Define X_j=exp(a_j+d_j*F+s_j*Z_j). Normal log variables give positive outputs and all polynomial moments finite without clipping. This does not exponentiate a heavy-tailed distribution or a raw lognormal covariate. No TC≥HDL selection is imposed; independently measured outcomes can occasionally reverse. Such events are a model limitation to inspect, not an extra eligibility rule.

Arithmetic mean/SD anchors (m_j,t_j) are B=(21.63,3.61), T=(3.23,.92), H=(1.14,.38). Sex geometric ratios r_j are 23.2/21.5, 3.9/3.6, 1.10/1.05. Let p=.5, A1_j=(1−p)+p*r_j, A2_j=(1−p)+p*r_j². Then:

```
d_j = log(r_j)
s_j² = log((1+t_j²/m_j²) * A1_j²/A2_j)
a_j = log(m_j) − log(A1_j) − s_j²/2
```

These equations decompose source marginal dispersion rather than misusing it as conditional noise. They set model pooled arithmetic moments to the stated anchors and sex geometric ratios to r_j. They do not force source absolute geometric means or pretend the combined studies identify a single population. Constant within-sex log variance is an explicit distributional assumption. All calculated s_j² are positive.

| Variable | a, male log location | d, female log shift | s, within-sex log SD | Implied arithmetic mean M / F |
|---|---:|---:|---:|---:|
| BMI | 3.022293525028255 | .076099343538647 | .161333995244347 | 20.8073825503 / 22.4526174497 |
| TC | 1.093457046927361 | .080042707673536 | .276416699158892 | 3.1008 / 3.3592 |
| HDL | .055087850509920 | .046520015634893 | .323758905626672 | 1.1134883721 / 1.1665116279 |

The assumed within-sex Spearman matrix is the rural Ashanti marginal matrix:

```
S = [[1, .212, −.100], [.212, 1, .106], [−.100, .106, 1]]
R_ij = 2*sin(pi*S_ij/6) for i != j, and R_ii=1
R = [[1, .221550248421557, −.104671912485888],
     [.221550248421557, 1, .110945960049958],
     [−.104671912485888, .110945960049958, 1]]
```

The conversion is exact only under the assumed continuous Gaussian copula. R is the correlation of latent normal variables, **not** raw BMI/lipid Pearson correlation. Its determinant is .922504578908393 and its 2×2 principal minors are positive. A Cholesky factor therefore exists. Applying an unadjusted rural source rank matrix within sex is a separate, strong transport/conditioning assumption. The pooled output rank matrix will generally differ because of sex shifts; this is disclosed rather than repaired by pretending pooled equals conditional.

## Relationship to all requested analyses

For sex f let M_jf=exp(a_j+d_j*f+s_j²/2). Define within-sex covariance C_ij(f)=M_if*M_jf*(exp(R_ij*s_i*s_j)−1), and Cbar=(1−p)C(0)+pC(1). The age/sex-adjusted population OLS coefficients per one BMI are beta_T=Cbar_BT/Cbar_BB and beta_H=Cbar_BH/Cbar_BB. A common slope is a weighted projection across the two sex strata, not a reported mechanistic or causal parameter.

The residual covariance is Cbar_TH−Cbar_BT*Cbar_BH/Cbar_BB. Residual variances are Cbar_TT−Cbar_BT²/Cbar_BB and Cbar_HH−Cbar_BH²/Cbar_BB. Dividing by their geometric mean derives the requested Pearson residual correlation. This is a functional of the entire assumed law, not Spearman and not its latent R_TH entry.

Retained deterministic algebra, without generated rows, implies approximately:

| Intended use | Evidence components and model-implied value | What remains assumed |
|---|---|---|
| K02-HDL-BMI | BMI/HDL marginal moments + geometric sex ratios + Spearman B–H; 5*38.67*beta_H = −2.1058321416 mg/dL per 5 kg/m² | Copula, shape, pooled-to-within-sex rank bridge, no within-sex age dependence, selection/assay/population transport, operational unweighted law |
| K02-TC-BMI | BMI/TC moments + geometric sex ratios + Spearman B–T; 5*38.67*beta_T = 10.8721684821 mg/dL per 5 kg/m² | The same bridges; no imported univariate log slope |
| K02-LIPID-RESIDUAL | All three marginal scales and rank pairs + geometric sex ratios; residual Pearson approximately .13223196035 | Full joint law, all conditioning/adjustment bridges; source TC–HDL Spearman .106 is not a direct constraint on this statistic |

These values are algebraic implications for checking implementation after approval, not requested signs, target estimates, observed outcomes, source-reported adjusted coefficients or acceptance criteria. No target record or estimate was accessed. Row seeds will vary sampling error without adding evidence or modelling source/transport uncertainty.

## Evidence use, feedback and stopping

Planned model parameters explicitly bind the selected source moments, geometric ratios and rank matrix plus assumptions to all three analyses. Age/sex composition is a scenario decision. Proposed assumption IDs are A_population, A_selection, A_measurement, A_unweighted_operational, A_marginal_dispersion, A_equal_logvariance, A_sex_ratio_transfer, A_rank_to_conditional, A_gaussian_copula, A_age_independence, A_age_quantile_shape, A_balanced_sex. Every nonmatching/unknown context comparison will retain its own gap and relevant shared bridge IDs; no gap becomes resolved by choosing a number.

All actual source weighting remains not_reported in semantic bindings. Core source-feedback comparisons that require known weights will remain not_computable even where a generated-only mean/SD/rank diagnostic can be calculated. Geometric summaries are unsupported by the core operator and remain not_computable. Age quantile convention is unreported. No unavailable source statistic is silently replaced by an arithmetic mean, Pearson correlation, different adjustment or a different population.

After approval, prepare only the allowed program candidate and its mandatory sidecars, then let the controller validate/freeze/execute the fixed trial. The generator will read numerical settings from model_spec. Initial checks can bind this source review and the actual deterministic algebra; they cannot claim row validity or execution. Any later one permitted revision must respond to a concrete source/definition/implementation finding; retain the model if feedback supplies none. Source match cannot upgrade target validity. No original acquisition, local random rows or generator execution has occurred.
