# Actual probability law and finite moments

All scientific settings occur in `model_spec.json`. `generator.py` implements the following target law with 3,000 independent rows. Write q=0.20 and r=2 sin(pi*0.529/6). For independent standard normals U,V,W, set Z_G=U, Z_B=qU+sqrt(1-q²)V and Z_H=rU+sqrt(1-r²)W. The resulting correlation matrix in B,G,H order is [[1,q,qr],[q,1,r],[qr,r,1]], with determinant (1-q²)(1-r²)>0. The BMI-HbA1c residual independence is assumed; it is not an unreported zero treated as fact.

For each biomarker, given positive chosen arithmetic mean m and SD s, put sigma²=log(1+s²/m²), mu=log(m)-sigma²/2, and X=exp(mu+sigma Z). The target means and SDs are transported from the stated MIND marginals. Age is independent uniform over integers 35,...,74; female is independent Bernoulli(0.5). IDs are artificial deterministic unique strings. There are no observed inputs, participant records, hidden group labels, row exclusion, clipping, mixture, nonlinear exponentiated quadratic term, or empirical rank transforms.

For any finite power vector k, the biomarker raw moment is

    E[product X_i^k_i] = exp(k' mu + k' Sigma k / 2),

where Sigma=diag(sigma) R diag(sigma). Thus all positive integer moments exist, including E[X], E[X²], every cross-second moment, and fourth moments required for usual unweighted OLS asymptotics under this IID law. The statement follows from the normal moment-generating function, not finite sample output. Specifically E[X_i]=m_i, Var(X_i)=s_i² and Cov(X_i,X_j)=m_i m_j (exp(Sigma_ij)-1). Each biochemical variable has support (0,infinity): positive BMI/glucose/HbA1c satisfy task lower supports. There is no assumed clinical upper cutoff. Such unbounded tails may be scientifically inadequate; finite moments do not validate the tail model. The target age mean is 54.5 and variance (40²-1)/12; Bernoulli mean/variance are 0.5/0.25. These are assumed mathematical consequences, not target observations.

The continuous biomarker joint density has full support on the positive orthant and nonzero residual innovations. Its covariance is positive definite because no nonconstant linear combination can be constant on that support. Age/female are independent, each has positive variance, so all requested population OLS predictor covariance matrices are nonsingular. A finite random cohort can in principle have only one sex category or other rank failure; the controller must retain failures rather than regenerate. The population E3 age coefficient is exactly zero, because age is independent of every other variable. This is fixed by assumption and is not newly inferred from the two Jansen regressions. Conditional on glucose, log-BMI/log-HbA1c innovations are independent; this also imposes the absence of a direct BMI dependence. A raw linear regression is a projection of this law, not an equation with the published source coefficients inserted.

The implementation uses finite-precision normal draws and exponentiation. Mathematical support/finite-moment proofs describe the ideal law. The generator explicitly fails on floating-point overflow, underflow to zero or nonfinite values; it neither replaces nor clips such rows. No guarantee of execution has been inferred from these analytic calculations.

# MIND rank constraint: law-specific proof

The separate source scenario conditions on MIND's eligible age-61-80 rural follow-up, free of dementia/functional disability and including known diabetes. Its FSG and HbA1c positive margins use the source-specific reported arithmetic moments. The pair uses the same latent r as the generator. It is explicitly a continuous approximation to a processed source dataset with incompletely documented mean imputation and ties, not a reproduction of source rows or assay harmonization.

For continuous lognormal X,Y, their population CDF values are Phi(Z_G),Phi(Z_H). Let A,B be independent standard normals, also independent of the pair. Then E[Phi(Z_G)Phi(Z_H)]=P(Z_G-A>=0,Z_H-B>=0). The two differences have variances 2 and covariance r, hence correlation r/2. For a centered normal pair with correlation c, its positive-quadrant probability is 1/4+asin(c)/(2*pi): one obtains this by writing the pair as a rotation of an isotropic normal vector; its uniformly distributed angle places the positive wedge at angle pi/2+asin(c). Therefore Spearman rho_S=12 E[F_X(X)F_Y(Y)]-3=(6/pi)asin(r/2). The specification inverts this identity, giving 0.529 algebraically. No Gaussian-copula shortcut is asserted without this law and proof. No ordinary covariance matrix alone was used to identify rank association. Exact agreement is imposed, not an independent validation. Equal weights and continuous no-tie population ranks are assumptions; empirical tie preprocessing remains unknown.

# Jansen source law and selection-linked moments

Jansen is a separate diagnostic scenario, not the target. The same latent-factor structure is used for BMI, plasma FPG and **native IFCC HbA1c**, with source-specific lognormal parent means/SDs. Age is an independent continuous uniform with mean55.5 and SD9.9 (support mean +/- sqrt(3) SD, not target-truncated); female is independent with probability 1-1176/2921. Other reported eligibility restrictions are represented as already applied, with unobserved selection effects assumed absent. The parent biomarker moments are set to the reported selected moments as an acknowledged approximation; this does not claim the selected law reproduces them exactly.

Then apply the explicit source condition FPG<7.0. If L=log(X) is multivariate normal, a=(log(7)-mu_G)/sigma_G, and k is any finite vector, completion of the square gives

    E[exp(k'L) | L_G<log(7)]
      = exp(k'mu + k'Sigma k/2)
        * Phi(a - (Sigma_G,* k)/sigma_G) / Phi(a).

The denominator is strictly positive; the numerator is finite. The conditional source moments of every finite order therefore exist. The actual post-selection first and second moments, not unselected or target moments, are supplied to `source_operations.evaluate`. Age/gender remain independent because the selection involves FPG only. The two separate intercept-including source OLS projections have predictor sets (age,gender,BMI) and (age,gender,FPG), respectively; the supplied function computes each covariance projection on its proper set. No combined regression is substituted. Their calculated values can disagree with the published 0.13 and 2.29. Both discrepancies are retained. Source anemia, diabetes history, missing processing, family preference and true model rows remain incompletely known, so this is neither exact source reconstruction nor a strict replay.

Native IFCC avoids treating transformed and original slopes as different pieces of evidence. If represented in NGSP units, X_percent=0.09148 X_IFCC+2.152; a covariance or slope receives only the multiplier, and a level also receives the offset. This affine representation is not a plasma-to-serum adjustment or an assay equivalence claim.

# Bao source law and analytic Pearson check

The Bao pair law is directly specified conditional on its eligible analyzed Shanghai adults, excluding known diabetes but retaining screen-detected diabetes. It uses log-locations log(reported medians) and log-SDs log(Q3/Q1)/(2 Phi^-1(.75)). Because the printed median/quartiles are not perfectly log-symmetric and the source interpolation rule is unknown, the model need not match both endpoints. The actual endpoint discrepancies are retained. Only the pair is needed for the unadjusted Pearson functional; unmodeled demographics are not silently substituted with target demographics.

For log-SDs a,b and latent correlation r, Pearson(X,Y)=[exp(rab)-1]/sqrt((exp(a²)-1)(exp(b²)-1)). `analytic_checks.py` derives the equivalent source first/second moments and sends them to the supplied operation. It reports the raw discrepancy from 0.619 with no fitting, CI membership rule, or pooled score. This pair law uses Bao-specific margins, not MIND or target moments. Its shared r is a transport hypothesis that may be incompatible with the reported source correlation.

# Reproducibility, uncertainty and scope

`analytic_checks.py` imports only the supplied source arithmetic, never the generator. It uses closed-form expressions, standard normal CDF via `math.erfc`, deterministic inverse CDF, and small linear systems. No random draws, simulated rows, quadrature, optimization or generator execution occur. `analytic_results.json` retains input/script/generator byte hashes, actual contexts, all calculated moments, and source discrepancies. Static ABI/contract validation has separate receipts; neither validates execution or science.

The normal innovations express individual residual variation conditional on fixed scenario parameters. Unknown source estimator uncertainty has not been converted from individual SDs or from unconfirmed-level Jansen intervals. No cross-source precision pooling occurs. The two Jansen estimates share a cohort; MIND rank and MIND marginal evidence share a cohort; Bao's pair/marginal evidence share another cohort. These are not independent confirmations. Source-estimation uncertainty, family/shape choice, selection, unreported cross-covariances and population transport are separate unresolved uncertainties. Synthetic seeds are not new clinical evidence, and no individual measurements are recovered.
