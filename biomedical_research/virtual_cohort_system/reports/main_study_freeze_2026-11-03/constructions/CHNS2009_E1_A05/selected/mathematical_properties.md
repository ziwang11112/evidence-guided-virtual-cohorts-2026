# Probability law, moment existence and source calculations

This document describes the submitted code, not recovered participant measurements. `analytic/calculate.py` reads the specification and performs closed-form calculations; it never imports `generator.py`, produces rows, samples latent variables, runs Monte Carlo, or performs numerical quadrature. Its source covariance matrices are consequences of the laws below, not independently chosen desired moments.

## Target law and support

For each of 3,000 independent virtual rows, let Z=(Z_age,Z_B,Z_G,Z_H) be centered multivariate normal with correlation R=`parameters.target_law.latent_correlation`. The generator takes independent standard normals and multiplies them by the transpose of the Cholesky factor of this matrix. All marginal scientific constants are in the specification.

Age is 35+floor(40 Phi(Z_age)), so it is integer uniform on 35,...,74. The code assigns floating-point CDF rounding to exactly 1 to the last bin; this is an endpoint arithmetic guard, not truncation of a latent scientific law. Female is an independent Bernoulli variable with the Bao female probability. Independence and transported sex composition are assumptions.

For each biomarker X_j, X_j=exp(a_j+s_j Z_j). Set v_j=log(1+SD_j^2/m_j^2), s_j=sqrt(v_j), a_j=log(m_j)-v_j/2. The selected target scenario uses MIND arithmetic mean/individual SD pairs for BMI, serum glucose and HbA1c, under explicit population/measurement transport. This gives strictly positive values and no upper support limit. No diabetes, pregnancy, treatment or source selection rule is used to discard or clip target rows.

The latent biomarker correlations are obtained from assumed or source-derived rank correlations. BMI-glucose rank 0.25 is an unsupported completion assumption. BMI-H rank is derived under the Jansen source assumptions below. Glucose-H rank uses the MIND source point. Age's latent correlations 0.10,0.10,0.15 are author assumptions. None is a reported conditional age coefficient. The matrix is checked positive definite in `analytic/source_results.json`.

## Finite first and second moments

For any finite real t, the normal moment generating function gives E[exp(tZ)]=exp(t^2/2). Thus E[X_j^k]=exp(k a_j+k^2 s_j^2/2) is finite for k=1,2 (indeed every finite real k). In particular E[X_j]=m_j and E[X_j^2]=m_j^2+SD_j^2. Correlated products obey E[X_i X_j]=m_i m_j exp(s_i s_j R_ij), hence every biomarker covariance exists. Age and female are bounded, and Cauchy-Schwarz bounds all their cross-moments with biomarkers. Age has mean 54.5 and variance 133.25; Bernoulli variance is p(1-p). There is no exponentiated quadratic term, mixture with an infinite-moment component, hidden rejection step or scientific clipping.

The mathematical law is finite almost surely. Finite machine arithmetic is a separate implementation issue: the generator raises on nonfinite or nonpositive biomarker output instead of dropping or replacing rows. No execution claim is made from this proof.

Positive definiteness gives nonzero conditional Gaussian innovation variance for every latent coordinate. The biomarkers have a joint density positive on the positive orthant. Each age bin has positive probability, and both female groups have positive probability. Therefore there is no deterministic affine dependence among the requested OLS predictors and the population intercept-including design second-moment matrices are nonsingular. A particular finite sample still needs the controller's rank and numerical checks; population rank is not a claim that all possible finite samples have both sex categories.

## Why the Gaussian rank formula applies to this law

The law explicitly assumes Gaussian dependence; no Gaussian-copula identity is inferred from source ordinary moments. Strictly increasing continuous marginal transforms imply F_X(X)=Phi(Z_X) and F_Y(Y)=Phi(Z_Y). For two standard normals of correlation rho, population Spearman is 12 E[Phi(Z_X) Phi(Z_Y)]-3.

Introduce independent standard normals V and W, also independent of (Z_X,Z_Y). The expectation is P(V<=Z_X,W<=Z_Y). The differences (Z_X-V,Z_Y-W) have variances 2 and correlation rho/2. A centered bivariate normal with correlation c has positive-orthant probability 1/4+asin(c)/(2 pi): the probability is 1/4 at c=0 and differentiating its Gaussian integral gives derivative 1/(2 pi sqrt(1-c^2)), whose integral is asin(c)/(2 pi). Consequently the rank functional is 6/pi asin(rho/2), and rho=2 sin(pi r_s/6) installs a rank constraint in this explicitly assumed family.

For affine uniform margins, standardizing each margin is the same as standardizing Phi(Z), so raw Pearson correlation also equals this rank functional. For lognormal margins, raw Pearson is instead [exp(s_i s_j rho)-1]/sqrt([exp(s_i^2)-1][exp(s_j^2)-1]). They are not interchanged. These are population identities; original imputed values, finite-sample ranks, ties and unknown sample weighting are not reconstructed. `analytic/mind_rank.json` is a law-specific derivation submitted for review; no independent review is claimed by the author and the supplied ordinary-moment operator is not called for Spearman.

## Directly selected Jansen scenario and separate projections

The Jansen source scenario has its own population, measurements and marginal laws. It is conditional on the published eligibility, not the target law and not an unselected parent subsequently mislabeled. Missing anemia/prior-diagnosis variables prevent reconstruction of selection probabilities; eligible membership is assumed. Source age is uniform on 55.5 +/- sqrt(3)*9.9, approximately 38.35 to 72.65; these assumed source supports are unrelated to the target age bounds. BMI is uniform with mean 26.5 and SD 4.1. FPG is uniform with mean 5.1 and SD 0.5, whose entire support is below 7 mmol/L. Native IFCC HbA1c is uniform with mean 38 and SD 3. Its percent representation is 0.09148*IFCC+2.152. The source supports are convenient moment-matching assumptions, not population cutoffs.

The same Gaussian biomarker copula submatrix used by the actual generator is used here. Source age and female are independent of biomarkers and each other. These are explicit unreported cross-covariance assumptions; the source's nuisance coefficients are not reported as zero. Female probability is derived from the reported male count fraction and female=1 is a declared code, not a claim about the original coding.

For independent nuisance covariates, the coefficient of BMI in the separate intercept-including regression HbA1c_IFCC~age+female+BMI is Cov(BMI,H_IFCC)/Var(BMI). With uniform margins it equals r_BH*(3/4.1). Choose r_BH=0.13*(4.1/3)=0.1776666667, then convert it to the latent rho using the rank identity. This establishes exactly the law-to-moment link for the BMI operation. The target transports that rank dependence under an explicit assumption; it does not insert 0.13 or its percent conversion as a target regression coefficient.

Separately, the glucose projection HbA1c_IFCC~age+female+FPG equals r_GH*(3/0.5). Keeping the MIND-derived common rank r_GH=0.529 yields 3.174 mmol/mol per mmol/L, compared with the reported Jansen 2.29: raw discrepancy +0.884. This mismatch is retained. Neither separate regression slope is treated as a simultaneous structural coefficient in a joint BMI-plus-glucose equation. The source BMI-glucose covariance is generated by its explicitly assumed rank 0.25 and does not alter the separate focal projection when source age/sex are independent.

`analytic/jansen_moments.json` calculates Cov(X_i,X_j)=SD_i SD_j * (6/pi asin(R_ij/2)) from these uniform laws, adds the independent Bernoulli covariance, and passes the resulting means/covariance to the supplied source operation. That operation converts the response covariance by the NGSP multiplier only, so the source coefficients retain native IFCC units.

## Bao Pearson and MIND rank scenarios

Bao's source pair is directly conditional on its own eligibility: Shanghai communities with previously diagnosed diabetes and specified medical conditions excluded, screen-detected diabetes retained. The age-20 boundary, exact pair count and original processing remain unresolved. Each source pair margin is lognormal with a=log(reported median), s=log(Q3/Q1)/(2 Phi^-1(.75)). Three rounded quantiles need not lie on one lognormal law, so the computed quartile discrepancies are explicitly retained. Neither the source marginal model nor the target is said to reproduce the original measurements.

This Bao pair uses the same latent glucose-H correlation as the target/MIND copula. Its own lognormal source means/covariance follow from the exponential moment formula above, and the supplied Pearson operation computes its population correlation. The raw discrepancy from 0.619 is retained without precision weighting or modification of the target law.

The MIND source pair is directly conditional on its selected 61-80-year rural cohort, including known diabetes. Its lognormal FSG/HbA1c margins use the reported source means and individual SDs. The continuous Gaussian rank proof gives 0.529 under the installed copula parameter. This is fitted source agreement, not independent validation. Source imputation/ties, prior-year BMI assessment and laboratory timing are not reproduced. The target carries this pair dependence and its marginal moments by declared transport, which remains unvalidated over a broader age range and different analytical selection/measurement setting.

All source scenarios use finite uniforms, Bernoulli variables or linear-normal exponentials, so their first/second moments exist by the same arguments. They share actual generator transformations and the biomarker dependence matrix, but source-context parameters are explicitly separate. No source rows are generated. Every target-table/source-statistic comparison in the feedback sidecars is unavailable.

## Interpretation and uncertainty

Latent innovations describe individual virtual variation conditional on fixed scenario parameters. Unknown external-estimate uncertainty, unknown joint structure, and population/assay transport uncertainty are separate and are not quantified by repeating rows or seeds. Jansen's printed intervals have unknown confidence level and are never converted to SEs, residual SDs, equivalence tolerances, or weights. Records within each cohort share participants; no pooled independent-evidence score is formed.

E1 and E2 are source-analogous target analyses only. E3 is not identified by the two source slopes or the rank correlations and depends on the assumed target age correlations, margins and covariances. Changing those assumptions would change E3 even while leaving every fitted source constraint intact. Female independence algebraically implies zero population female projection coefficients; that is an assumption-dependent feature, not empirical evidence. No individual recovery, clinical causal effect, community-sampling inference, or publication readiness is established.
