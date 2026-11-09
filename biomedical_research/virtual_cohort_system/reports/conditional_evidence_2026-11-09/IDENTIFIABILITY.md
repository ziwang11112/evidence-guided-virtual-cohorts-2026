# Identifiability and source admission

Independent methods assessment, 2026-11-09. This document derives the required moment identities without reading any target, generated cohort, fitted candidate, or old result. It does not choose clinical coefficients, signs, or a generator family.

## Requested quantities

Let B be continuous BMI, T measured total cholesterol, H measured HDL cholesterol, A the design columns for age and sex, and C=(A,B). Include an intercept in every projection. The three requested quantities are the B coefficients in the population/sample linear projections T~B+A and H~B+A, and the Pearson correlation of the two residuals from T~C and H~C. Specify the age functional form and sex coding; adding age squared or interactions changes the operator. An OLS projection coefficient is defined even when the conditional mean is nonlinear. It is not automatically a causal effect.

These are measured-data estimands unless an independently supported observation model maps assay results to latent concentrations. Assay measurements cannot silently become error-free latent observations.

## Sufficient compatible summaries

A directly reported coefficient for each exactly specified projection and a directly reported Pearson residual correlation for the exactly specified C are sufficient point summaries for the three uses. Sampling uncertainty, source transfer, and dependence between estimates remain separate requirements.

An alternative sufficient object is one internally compatible covariance matrix for (T,H,B,A). For centered variables, let S be that covariance matrix. The coefficient vector for Y~C is S_CC^{-1} S_CY. Let R=S_YY-S_YC S_CC^{-1} S_CY for Y=(T,H). Then the requested residual correlation is R_TH/sqrt(R_TT R_HH). This requires an identifiable design and positive residual variances. Normality is unnecessary for these projection identities.

A smaller natural covariance object is K, the 3x3 covariance matrix of (T,H,B) after each has been linearly residualized on the *same* A in the *same* analytic population. It gives:

```
beta_T = K_TB / K_BB
beta_H = K_HB / K_BB
rho_TH.C = (K_TH - K_TB*K_HB/K_BB) /
           sqrt((K_TT - K_TB^2/K_BB)*(K_HH - K_HB^2/K_BB))
```

K's six entries are a convenient sufficient set, not a claim of a unique minimum representation. The three requested numbers themselves form the minimal direct point-summary representation. Neither representation identifies a full generative distribution, its marginal shapes, intercepts, interactions, or observation error.

A complete compatible Pearson correlation matrix for (T,H,B,A) suffices for the residual correlation. Recovering an unstandardized BMI coefficient additionally needs the relevant outcome/BMI SD ratio. All SDs and correlations must refer to the same scale, sample/selection, weighting, missing-data treatment, and variable definitions. Pairwise-complete correlations with different underlying samples are not automatically one joint covariance matrix. Check positive semidefiniteness and rounding; do not silently repair the matrix.

Using correlations after adjustment for A alone, all three values r_TH.A, r_TB.A, r_HB.A together identify

```
rho_TH.AB = (r_TH.A - r_TB.A*r_HB.A) /
            sqrt((1-r_TB.A^2)*(1-r_HB.A^2))
beta_Y = r_YB.A * SD(residual(Y~A)) / SD(residual(B~A))
```

Two BMI associations alone leave r_TH.A free and therefore do not identify the TC-HDL residual relation. Marginal outcome SDs are not the residual SDs in the coefficient formula. A reported standardized regression coefficient converts to an unstandardized coefficient using the exact source standardization scales; a partial correlation is a different statistic. Cluster-robust or survey standard errors do not change the stated point projection, but ordinary t-to-partial-r identities do not apply to their robust t statistics.

## What does not supply the requested quantities by itself

| Published information | Admissible source meaning | Missing information for exact requested use |
|---|---|---|
| Coefficient with additional or different covariates | Its own stated adjusted projection | Compatible covariance involving omitted/added covariates, or an explicit transport/model assumption; coefficients cannot simply be relabelled |
| Sex-specific or age-stratified slopes | Within-stratum projections | Pooled joint moments and compatible age design; averaging slopes by sample size generally does not recover a common pooled slope |
| Categorical BMI contrasts or adjusted lipid means | Stated category contrast/standardization | Within-category BMI-outcome information, BMI distributions and adjustment design; category midpoint division assumes a response form |
| Marginal Pearson association | Marginal projection/correlation | Covariance with the requested covariates |
| Marginal Spearman association | Correlation of source-defined ranks | Pearson covariance and covariate adjustment; converting under a copula/distribution assumption is a model-dependent operation |
| Partial correlation adjusted for a different set | Its own partial-correlation operator | Cross-covariances needed to add or remove the missing adjustments |
| Lipid range, diagnostic cutoff, or marginal SD | Range/threshold/marginal spread | Conditional mean and covariance structure |
| Two separate outcome regressions | Two conditional-mean projections | Covariance of their errors/residuals |
| Residual SD from each outcome regression | The two residual scales | Cross-residual covariance; zero correlation cannot be inferred |

Different adjustment sets are not a reason to discard authentic evidence. They are a reason to retain its actual source operator and decline an exact-use label. A model may accommodate several such source constraints without any one coefficient being equal to the requested coefficient.

## Conditional SD is an ambiguous term

The diagonal of the Schur complement above is the variance of a linear-projection residual. Its square root is a *linear residual SD*. It equals a covariate-invariant conditional SD only with suitable conditional-mean and homoskedasticity assumptions. Under heteroskedasticity or a misspecified linear conditional mean, it is not SD(Y|C=c) at each c. A published residual standard error may divide a residual sum of squares by n-p, whereas a covariance calculation divides by n-1 or n; these factors must be reconciled before algebraically combining finite-sample summaries. An SE of a mean or coefficient is not an individual-level residual SD.

## Model-neutral admission criterion

Admit a numerical source item when an independent reader can identify (1) its original provenance and value, (2) the source population and selection, (3) the measured variables, units, transformations and relevant measurement process, and (4) a sufficiently explicit statistic operator. Record weighting, covariates/design, missingness/sample size, uncertainty, and cohort overlap where available; mark unresolved items as unresolved. There must be a reproducible operation that can be applied to a compatible proposed source-data law or source-like sample and compared with the publication. An authentic but ambiguous number may remain in the inventory without becoming an executable constraint.

Assign separate labels:

1. **Exact-source-use:** the source operator matches a requested estimand, including variable scales and design. This does not establish transport to a new population.
2. **Derived-source-use:** the requested operator follows algebraically from compatible source summaries; provide the calculation and assumptions.
3. **Different-source-operator:** a verified, executable, scientifically relevant statistic with a different adjustment set, population/stratum, transform, or statistic family. Preserve its actual label and the gap to each requested use.
4. **Context-only/pending:** useful definition or incomplete/ambiguous evidence without an executable numerical constraint.

Missing uncertainty does not justify treating a point estimate as exact. It may support a transparently provisional sensitivity constraint, with uncertainty unresolved. Do not invent a clinical tolerance, pool overlapping estimates as independent, or select a favorable sign/magnitude. Reporting ambiguity, population transport uncertainty, sampling uncertainty, and model uncertainty are distinct.

Scientific admission and implementation readiness are separate. Defining a source projection does not require recreating every detail of the original estimation software, but uncertainty in imputation, weighting or selection cannot be hidden. A replay on a complete proposed source-data law can compare its projection with an imputation-pooled published estimate only under stated missing-data/estimation assumptions. A per-SD BMI operator must use the declared source-law BMI standardization; that source-law SD needs external support or explicit sensitivity. It is not a per-kg/m2 coefficient. Missing source covariates, weights and selection information must not be supplied by target rows.

This criterion constrains fidelity to source evidence, not the Agent's model class. Any statistically valid model is eligible if it declares its source/measurement/transfer mapping and replays the admitted source operators. It may use non-Gaussian margins, nonlinear means, interactions, mixtures, heteroskedasticity, or other structures. A simpler parametric conversion may be considered, but its assumptions must remain visible and must not be mislabelled as source identification.

## Decision for construction

Let F be the set of source/measurement/transfer models compatible with the admitted evidence and its declared uncertainty. A requested quantity is identified only if its values agree across F; otherwise report an identified/sensitivity range or unresolved variation. Multiple compatible models may remain even after all three requested summaries are directly constrained. Successful source replay establishes consistency with those summaries, not clinical validation or uniqueness.

Admitting at least one different-source-operator can justify a bounded, separately labelled source-replay exploration when its assumptions and unresolved uses are declared. It does not by itself fill all three requested-use gaps. If no executable statistic survives verification, preserve the negative finding and close the branch without another cohort generation. No generation or target comparison is performed in this review.
