# Conditional-structure diagnosis of the closed live A/B study

Date: 2026-11-04. Scope: original analytic review of the frozen specifications/programs and previously saved aggregate evaluation. This note does not revise a candidate, rerun evaluation, fit a model, simulate a cohort, or inspect real/generated individual rows. Only the elementary arithmetic explicitly identified below was calculated. The evidence-cohort-generation skill supplied the distinction between reported evidence, structural assumptions, and unsupported inference; its generation/replay workflow was not invoked.

## Finding

B's three saved adjusted BMI point estimates are negative although its explicit BMI pathways into the HbA1c mean, glucose mean, and elevated-component probability are positive. This is mathematically possible and is not, by itself, evidence of a coding bug or an internal contradiction. The requested coefficient belongs to a joint-distribution linear projection after glucose, age, and sex adjustment. It does not equal a BMI multiplier in the generator. A static calculation below shows that the frozen B structure already permits a negative conditional BMI relationship in a precisely defined subproblem. It does **not** identify which component caused the observed full-model discrepancy.

The saved results establish a descriptive mismatch with the exposed development reference. They do not establish an implementation defect, an independently validated failure rate, or a repair direction that can be inferred from the reference sign.

## Artifacts and saved observations

Reviewed inputs were `evcLive01/{A,B}/task.json` and each `candidates/initial/{generator.py,model_spec.json,decision.md}`, together with `work/agent_system_live_2026-11-03/{SOURCE_AND_MODEL_AUDIT.md,evaluation/REPORT.json,evaluation/SUMMARY.json}`. The bundle root is `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcLive01`; the work root is `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work`. Original papers were not newly reread; source-fidelity statements here rely on the existing source audit. No reference/generated CSV, execution output table, or other row-level data was opened. No generator was imported or executed. No literature search, source replay, parameter intervention, or new experiment was performed.

The saved B results concern `hba1c ~ 1 + bmi + glucose + age + female`:

| Saved delivery | BMI coefficient, HbA1c percentage points per kg/m² | Saved conditional HC3 interval | Marginal Pearson BMI–HbA1c |
|---|---:|---:|---:|
| 7301 | -0.009491669 | [-0.017374652, -0.001608686] | 0.135088922 |
| 7302 | -0.000984996 | [-0.009179087, 0.007209094] | 0.125922289 |
| 7303 | -0.002646883 | [-0.011209133, 0.005915366] | 0.123590559 |

The exposed reference coefficient is +0.022464221, with saved community-cluster CR1-t interval [0.015259513, 0.029668930]. Two of the three generated BMI intervals include zero; negative point estimates should not be paraphrased as three determinate negative interval findings. The three draws condition on one fixed specification and are not three clinical studies. Final slots alias the retained initial tables. The report records independent QR recomputation agreement, including B coefficient/interval maximum absolute differences below 1.8e-14. This supports faithful numerical calculation of the saved regressions; it does not establish scientific adequacy of the generator.

## What determines the adjusted sign

Let X denote BMI, G glucose, Y HbA1c, and Z the intercept, age, and female indicator. Use the same linear adjustment actually requested, not conditioning on exact age/sex cells. Write x, g, and y for residuals after their linear projections onto Z. With a nonsingular design, the Frisch–Waugh–Lovell identity is

\[
\beta_X = \frac{\operatorname{Cov}(x,y)\operatorname{Var}(g)-\operatorname{Cov}(x,g)\operatorname{Cov}(g,y)}{\operatorname{Var}(x)\operatorname{Var}(g)-\operatorname{Cov}(x,g)^2}.
\]

The denominator is positive when x and g are not collinear. The sign is therefore the sign of the numerator. Equivalently, if r is the residual of X after projection onto all of Z and G, then `beta_X = Cov(r,Y)/Var(r)`. These identities apply to the sample OLS calculation as well as to the population linear projection when the relevant second moments exist. The preceding source audit established those moment conditions for the ideal final laws.

Even when the age/sex-adjusted BMI–HbA1c covariance is positive, the coefficient becomes negative if

\[
\operatorname{Cov}(x,g)\operatorname{Cov}(g,y) > \operatorname{Cov}(x,y)\operatorname{Var}(g).
\]

Positive marginal BMI–HbA1c correlation alone does not supply any of these three residual covariances. A positive structural mean derivative is also not this partial covariance. The adjustment set, BMI–glucose dependence, shared outcome variation, mixture composition, and the linear projection of nonlinear relationships all enter the coefficient. This is an associational statement; it does not assign causal meaning to the generator's factorization or to adjusting for glucose.

## A precise compatibility check inside frozen B

B generates a latent component D whose logit increases by 0.10 per BMI unit. At fixed D, age, and sex, both continuous means increase with BMI through

`f_H(X) = 1 + 0.002(X - 24.5)` and `f_G(X) = 1 + 0.012(X - 24.5)`.

The component conditional means are 5.55/7.4 for HbA1c and 5.0/7.4 for glucose. Glucose and HbA1c also share a normal residual, with component correlations 0.50/0.65. Thus, before conditioning on glucose, both the positive multipliers and the rising probability of the higher-mean component can increase mean HbA1c with BMI. This observation does not determine what remains at fixed glucose.

An exact calculation can isolate that distinction without sampling. Let G0 denote glucose before the independent meal increment and before output rounding. Within fixed D, age, and sex, the frozen equations have the form

\[
\log G_0=\mu_G(X)+s_G U, \qquad
\log H=\mu_H(X)+s_H\{\rho U+\sqrt{1-\rho^2}V\},
\]

where U and V are independent standard normals, `s = sqrt(log(1 + (SD/mean)^2))`, and the X dependence in each location is `log f(X)`. Conditioning on G0 fixes U as a function of X. Consequently

\[
\frac{\partial \log E[H\mid G_0,X,age,female,D]}{\partial X}
=\frac{0.002}{f_H(X)}-\rho\frac{s_H}{s_G}\frac{0.012}{f_G(X)}.
\]

The conditional residual variance is constant within that component, so this derivative describes the log of the conditional arithmetic mean as well as the conditional mean of log H. At the centering BMI 24.5, elementary substitution of frozen constants gives:

| Component | s_H | s_G | rho × s_H/s_G | Conditional log-mean derivative |
|---|---:|---:|---:|---:|
| Lower | 0.071978742 | 0.129455721 | 0.278005256 | -0.001336063 |
| Elevated | 0.200665619 | 0.316249725 | 0.412435623 | -0.002949227 |

Holding pre-meal glucose fixed offsets the explicit positive BMI contribution to glucose by a lower value of the shared residual. Because that residual also increases HbA1c, the resulting conditional derivative can be negative despite the positive direct HbA1c multiplier. These are derivatives of a conditional subproblem, **not** fitted HbA1c percentage-point slopes and not estimates of the reported OLS coefficient.

The evaluated B analysis uses G = G0 + meal, hides D, applies linear age/sex adjustment, and receives four-decimal outputs. Marginalizing D changes conditional component weights; the independent meal term changes the glucose measurement/dependence; heteroscedastic lognormal scales and nonlinear covariate effects enter the overall projection. Therefore this calculation proves compatibility, not a decomposition or causal attribution of the full observed sign. In particular, it does not show that the meal term, copula correlation, mixture, tail repair, or any one parameter is the culprit. No component intervention was performed.

## Why A is not B with glucose omitted

A uses a different joint law. Before its gamma residual draw its conditional mean is

`E[Y | X,Z,D] = constant + 0.012 X + 0.008 age - 0.03 female + 1.9 D`.

Its BMI conditional mean is `constant + 0.025 age - 0.6 female + 1.2 D`, with conditional SD 3.5. Let d be the residual of D after linear projection on Z, and write `X = its conditional mean + u`. The frozen construction has `E[u | Z,D] = 0`. It follows at the population-law level that

\[
\beta_{X,A}=0.012+1.9\frac{1.2\operatorname{Var}(d)}{1.44\operatorname{Var}(d)+12.25}.
\]

Thus A's chosen ideal structure itself yields a positive BMI population projection, larger than 0.012 when residual component variation is present. A positive saved coefficient is consistent with these assumptions; it does not validate them. Finite sample coefficients can vary.

Generated A and B differ in BMI generation, mixture membership, HbA1c distribution, coefficients, and residual structure. Comparing their coefficients is **not** a nested-regression experiment on the same synthetic cohort, even when seeds and the initial age/sex draws match. It cannot measure the effect of adding glucose to B's analysis.

The saved reference A and B fits do use the same documented complete-case sample. A limited algebraic inference is possible there: the omitted-variable identity gives the BMI coefficient in the reference projection `G ~ 1 + BMI + age + female` as

`(0.05494608227224503 - 0.022464221350644194) / 0.3929088614167606 = 0.08267021722156362`.

This is arithmetic on saved nested coefficients, not a new fit. It illustrates why the reference coefficient changes after adding glucose. It provides no corresponding decomposition for generated B and must not become a model-tuning target.

## What the saved report cannot resolve

REPORT.json saves marginal SDs, two B marginal association pairs (BMI–HbA1c and glucose–HbA1c), fitted coefficients/intervals, and design rank/condition number. It does not save BMI–glucose covariance, the full cross-covariances of BMI/glucose/HbA1c with age and sex, age–sex covariance, the residualized Gram matrix, or the reduced HbA1c-on-BMI/age/sex fit on each B table. A large condition number from an unstandardized design is not itself a diagnosis of the sign or of meaningful collinearity.

The saved coefficient gives the final partial-covariance ratio and its sign. The reported marginal quantities and coefficients do not uniquely reveal all FWL numerator terms or their separate magnitudes. In particular, a missing marginal BMI–glucose correlation alone would still leave the age/sex adjustment dependencies unresolved. A normal-equations identity constrains these missing moments but does not uniquely recover their full matrix.

The report also lacks component-resolved moments, pre-meal versus post-meal aggregate dependence, and parameter interventions. Even a complete FWL decomposition would explain how the observed projection balances covariance terms; it would not uniquely attribute an error to one generative mechanism. The three fixed-specification draws cannot distinguish all structural explanations or quantify source/transport uncertainty.

## Evidence gap, structure choice, and evaluation mismatch

| Layer | What the closed artifacts support | What they do not support |
|---|---|---|
| Evidence gap | The prior source audit found no material transcription defect, but the admitted means, SDs, marginal correlations, and predictor-list abstract do not identify either requested adjusted regression or the required joint law. All proposed source-semantic checks remained unavailable. | Unknown conditional dependence is not evidence of zero dependence; a known positive marginal relationship does not identify the adjusted sign. |
| Structure choice | Authors selected latent mixtures, covariate pathways, distributions, composition, and—in B—copula and meal assumptions. The final code is consistent with these principal choices and admits the negative conditional relationship derived above. | Mathematical coherence and disclosure do not make those laws empirically identified; a negative adjusted coefficient does not by itself demonstrate incorrect implementation. |
| Evaluation mismatch | The saved B adjusted BMI points have the opposite sign from the exposed development reference; A's BMI magnitude is also lower than its reference. | This does not identify a responsible parameter, authorize tuning to the reference, establish population truth, or constitute independent confirmation. |

## Minimal improvement before adding modules

The immediate improvement is a short **analysis-specific structure review**, not a mandatory source-plus-target simulation pipeline. For each requested adjusted coefficient, record the exact estimand and adjustment set, distinguish structural mean parameters from projection coefficients, write the relevant FWL dependence, and mark which needed relationships are evidence-supported, assumed, or unassessed. A stated expectation of a positive adjusted sign must have a valid structural or evidential basis; otherwise it should be an unresolved question rather than an acceptance criterion. This note supplies that review for the closed B result.

For a future authorized aggregate diagnostic, the smallest useful addition is the five quantities `Var(x), Var(g), Cov(x,g), Cov(x,y), Cov(g,y)` after the **same** intercept/age/female residualization, plus sample size, units, design definition, and a check that the FWL ratio reproduces the saved coefficient. A residualized three-variable covariance matrix is a convenient equivalent. Alternatively, the complete centered covariance matrix for BMI, glucose, age, female, and HbA1c preserves enough information for the projection. This would expose the arithmetic reason for the sign without exporting individual rows or generating any new cohort. It is a proposed improvement only; none was calculated from rows and the old evaluator/report was not changed here.

If mechanism attribution later matters, specify a discriminating structural question and authorize an appropriate intervention separately; do not guess a culprit from these aggregates. If the needed source joint distribution is unreported, label a replay as unavailable or explicitly assumption-dependent. Inventing a source population merely to obtain a passing check would not fill that evidence gap. No replay, target-sign constraint, new module, or parameter revision is necessary to accept the present diagnosis.
