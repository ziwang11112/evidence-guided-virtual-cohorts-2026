# Law, moments, and source linkage

Write B=body mass index, G=fasting glucose in mg/dL, H=HbA1c percentage points, A=age in years and F=female0/1. For X~Beta(p,q), set Z=(X-p/(p+q))/sqrt[pq/((p+q)^2(p+q+1))]. The beta integral gives E[X]=p/(p+q) and E[X^2]=p(p+1)/((p+q)(p+q+1)), hence E[Z]=0 and Var(Z)=1. Its support is bounded by subtracting its mean from0 and1 and dividing by its positive SD.

Independently draw U from standardized Beta(2,5) and V,W from standardized Beta(3,3), independent also of (A,F). Set sB=4.1, sG=9 and rho=0.25. The probability law implemented by `_standardized_beta` and `_conditional_outcomes` in generator.py is

    B = 26.5 + sB U
    G = 91.8 + sG(rho U + sqrt(1-rho^2)V)
    H = 5.6 + a(A-55.5) + b(B-26.5) + g(G-91.8) + rW.

There is no clipping, rejection, exponentiation, quadratic term, or seed selection. Scientific parameters are stored in model_spec.json. Sex is generated but has no direct outcome term, an explicit unverified completion assumption. The conditional equations are identical in the target and both declared analytic source scenarios; only the law of A,F differs.

Target: each of eight assigned cells contains exactly375 independent conditional rows. F is fixed within cell, and A is discrete-uniform over the corresponding task integer-year interval. This is a stratified design; an equal-probability row mixture has sex probability1/2 and four equally likely age bands. A row mixture is used only for interpreting moments, never as an empirical source reconstruction.

Lifelines analytic scenario: A is uniform on 55.5 +/- sqrt(3)*9.9; F is independent Bernoulli0.597. This age law is a bounded approximation with E[A]=55.5, Var(A)=9.9^2, rather than the target quotas. Pani analytic scenario: A=25+T with T~Gamma(shape4,scale7.5); F is independent Bernoulli0.5. Thus E[A]=55 and Var(A)=225; Pani age has no upper bound. Both are assumed laws of already selected source participants, not observed people. The Pani gamma is used only for a qualified adjusted projection, not survey-weight recovery or ageband-mean fitting. Source-specific recruitment, ancestry, fasting, assay and missingness remain unverified transport details.

For either scenario E[B]=26.5, E[G]=91.8, Var(B)=sB^2, Var(G)=sG^2, and Cov(B,G)=rho*sB*sG. Independence makes Cov(A,B)=Cov(A,G)=Cov(F,B)=Cov(F,G)=Cov(A,F)=0. These zero covariances come from the stated assumed law, not from the publications. Let vA=Var(A), vF=pF(1-pF). Define X=(A,F,B,G), its block diagonal covariance S with entries vA,vF and the B/G block just derived, and c=(a,0,b,g). Then

    E[H] = 5.6 + a(E[A]-55.5)
    Cov(X,H) = S c
    Var(H) = c' S c + r^2.

This follows by substituting the generator's affine equation and using E[W]=0, Var(W)=1 and independence, not by inventing a desired covariance matrix. The full five-variable covariance is the covariance of the explicit affine transformation of independent latent variables. analytic_check.py independently reconstructs these formulas and reports the actual helper projection results, matrix eigenvalues, support bounds, and generator/spec hashes. It never imports the generator or samples rows.

The two Jansen Table2 regressions are separate projections. After adjusting age and female, their coefficients are

    kB = Cov(B,H)/Var(B) = b + g*rho*sG/sB
    kG = Cov(G,H)/Var(G) = g + b*rho*sB/sG.

With kB=0.13*0.09148=0.0118924 and kG=2.29*0.09148/18=0.01163828888888889, solve

    b = (kB-kG*rho*sG/sB)/(1-rho^2)
    g = (kG-kB*rho*sB/sG)/(1-rho^2).

Because |rho|<1, the source B/G covariance block is positive definite. It is legitimate to fit both source projections only conditional on the additional assumed rho and compatible Table1/Table2 populations. Their slopes do not identify rho or the glucose-conditioned BMI coefficient b. Pani's full adjusted age coefficient is a=0.01 because S is nonsingular and Cov(X,H)=Sc. This is an assumption-qualified population projection, not exact complex-survey regression replay. It would not establish transport even if arithmetic agreement were perfect.

The Jansen percent SD is used once: r^2=0.3^2-[a^2*9.9^2+b^2*sB^2+g^2*sG^2+2bg*rho*sB*sG]. The retained deterministic result verifies r^2>0; this is individual residual variance, not an estimator SE. For any scenario the covariance matrix is positive definite because the independent latent components A,F,U,V,W each have positive variance and the affine transform is nonsingular (sB,sG,sqrt(1-rho^2),r are positive). Full-rank sample regressions are almost sure for the continuous covariates conditional on adequate age variation; finite samples can still fail and must be retained honestly.

Support and moments: U lies in[-sqrt(16/5),sqrt(20)], V,W in[-sqrt(7),sqrt(7)]. (The U lower bound squared is16/5 and upper bound squared is20, obtained directly from Beta(2,5) standardization.) Substitute these endpoints in B,G. The resulting lower bounds are positive and G's upper bound is below126; analytic_results.json reports the numerical margins. Since a,b,g are positive in this specification, the lower H bound is obtained at minimum A,U,V,W. This is positive even for A=25, covering the target and Pani law, and also positive for the Lifelines minimum. Endpoint bounds are mathematical model support, not physiological cutoffs. H is bounded in the target and Lifelines; in Pani only its positive linear A term is unbounded above. Gamma has E[T^k]=7.5^k Gamma(4+k)/Gamma(4) for k>=0, hence finite first and second moments. Therefore every requested variable, covariance and OLS population projection has finite moments. No reliance on finite sampled values is needed.

Uncertainty: rW represents individual residual dispersion at fixed parameters. The source point estimates are uncertain, but missing SE/CI levels do not define their sampling distributions. Pani mean SEs are not individual SDs and are not multiplied by sqrt(n). Jansen rows share a cohort; converted units are not independent observations. Structural alternatives, distribution support, unknown source covariances and target transport remain separate uncertainties that multiple generator seeds cannot resolve. The eight Pani ageband operations are explicitly context_only; no conditional integral or fitted ageband moment is asserted for them.
