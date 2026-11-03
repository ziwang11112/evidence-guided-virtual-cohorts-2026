# Actual law and mathematical properties

This is a finite-support associational probability law for fictional individuals. It does not recover individual measurements. The source-context moment calculations use the same conditional equations and parameter values as `generator.py`; they replace only the explicitly declared demographic law. They are approximate source populations, not source-row replay. `analytic_calculations.py` is retained and was executed without importing the generator. `analytic_results.json` binds the generator, specification, evidence and calculation script by SHA256.

## Design and latent law

The output has eight deterministic strata, each with375 rows: female0/1 crossed with ages25-39,40-54,55-69,70-79. Age is drawn uniformly over the integers in each stratum. All continuous latent draws are independent across rows and components, conditional on this fixed allocation. A randomly selected output position therefore has the equal-stratum mixture distribution, with female probability0.5 independent of its age band and age. Fixed quotas mean the table is a stratified collection, not an unconditionally iid national sample.

Let U1,U2,U3 be mutually independent Beta(3,3), independent of age A and female F, and put Zj=(2Uj-1)sqrt(7). The beta density is proper because its positive parameters have finite beta normalizer. E(U)=1/2 and Var(U)=1/[4(2*3+1)]=1/28. Thus E(Zj)=0, Var(Zj)=1, support is[-sqrt(7),sqrt(7)], and every absolute moment exists. Independent zero cross-covariances are a completion assumption, not reported evidence.

## Conditional equations and coefficient identification

Use centers a0=55.5, f0=0.597, b0=26.5, g0=91.8 and h0=5.6. In the equations below all numeric values are read from `model_spec.json`; rounded values shown here are explanatory only.

    B = b0 + aB(A-a0) + dB(F-f0) + sB Z1
    G = g0 + aG(A-a0) + dG(F-f0)
        + sG[rho Z1 + sqrt(1-rho^2) Z2]
    H = h0 + bA(A-a0) + bF(F-f0)
        + bB(B-b0) + bG(G-g0) + sH Z3

The assumed aB=0.04, dB=0.4, aG=0.12, dG=-2 and rho=0.30 are not source-identified. The Jansen source-completion law takes A continuous uniform with mean55.5 and SD9.9, F Bernoulli(0.597), independent. Matching its BMI and glucose variances gives

    sB^2 = 4.1^2 - aB^2*9.9^2 - dB^2*0.597*0.403 > 0
    sG^2 = 9.0^2 - aG^2*9.9^2 - dG^2*0.597*0.403 > 0.

These give sB=4.076112049490298 and sG=8.867146778981388. Conditional on age and sex, Cov(B,G)=rho*sB*sG is nonzero. Frisch-Waugh residualization therefore gives two *separate* source projections:

    tB = bB + bG*rho*sG/sB
    tG = bG + bB*rho*sB/sG.

The admitted tB=0.13*0.09148=0.0118924 and tG=2.29*0.09148/18=0.01163828888888889 lead to

    bB = [tB-rho*sG/sB*tG]/(1-rho^2) = 0.004722025662320084
    bG = [tG-rho*sB/sG*tB]/(1-rho^2) = 0.0109870927539898.

Thus neither Jansen separate projection was simply substituted as a coefficient in the joint response. The denominator is0.91>0. The conditional age coefficient bA=0.01 adopts the Pani adjusted age projection; bF=0 is an explicit unreported direct-sex-effect assumption. For any demographic/covariate law with finite nonsingular predictor covariance and independent mean-zero Z3, the joint population age coefficient is bA. This is a model implication, not evidence that cross-population transfer is valid.

Let kA=bA+bB*aB+bG*aG and kF=bF+bB*dB+bG*dG. Under the Jansen law,

    Var(H) = kA^2 Var(A) + kF^2 Var(F)
             + (bB*sB+bG*rho*sG)^2
             + (bG*sG*sqrt(1-rho^2))^2 + sH^2.

Setting this to the chosen reported percent SD0.3 squared yields sH=0.2567830729720274 with strictly positive remaining variance. This is residual individual variation, not uncertainty in literature estimates. The alternative IFCC-derived HbA1c mean5.62824 and SD0.27444 are rounding-related representations and were not added as extra constraints.

## Law-derived moments and source operations

Writing W=(A-EA,F-EF,Z1,Z2,Z3), the output vector is mu+LW. The retained calculation expands the equations above into L, then computes covariance as

    Sigma = L diag(Var(A),pF(1-pF),1,1,1) L^T.

It does not posit a desired covariance matrix. L and all its underlying parameters are recorded, so each covariance follows from the actual conditional law. L is lower triangular with diagonal(1,1,sB,sG*sqrt(1-rho^2),sH), all positive. Both source age variances and sex variances are positive. Hence full covariance and each regression predictor covariance are positive definite; linear projection coefficients uniquely exist. The admitted `source_projection` operator evaluates each Jansen adjustment set separately and the Pani adjustment set separately. Values are0.011892400000000003,0.01163828888888889 and0.009999999999999998, respectively. They match fitted constraints to floating-point precision, not independent validation.

The separate Pani source-completion law takes A discrete uniform25,...,84, F Bernoulli(0.5), independent, with the same conditional equations. The source does not identify this age law, sex balance, uniform population weights, or upper age84. In particular its reported >=70 group has no admitted upper bound; our70-84 group is an explicitly limited approximation, not a silent substitution of the task's upper age79. The real survey and its older tail remain unreconstructed.

For each band I, E(H|I)=h0+kA[E(A|I)-a0]+kF[0.5-f0]. The finite integer-uniform mean is(low+high)/2, band probability is its number of ages divided by60, and E(H I)=Pr(I)*E(H|I). These are exact finite-law formulas, not quadrature or generated rows. All eight operations have retained numerator, denominator, mean, source SE and raw discrepancy. Discrepancies range from+0.1315259757 to+0.3393559228 percentage points. They were not optimized away or treated as target evidence. The original band SEs remain uncertainty of survey estimates, not individual SDs.

## Support and finite first/second moments

Every source and target age law has finite support, F is binary, and each Z has finite support. All outputs are affine functions of those bounded variables. There is no exponentiation, unbounded quadratic, clipping, rejection, rescaling to sampled margins, or seed-dependent parameter fitting. The age-mixture distribution is finite, and affine images preserve boundedness. Therefore E|X| and E(X^2), as well as all cross-moments required by the projections, exist for every modeled variable in all three contexts.

The retained deterministic calculation evaluates32 rectangular-support vertices per context. These vertices are algebraic support extrema, not simulated cohort rows. Bounds for the task are:

| Variable | Lower bound | Upper bound |
|---|---:|---:|
| BMI kg/m^2 |14.256821201014867|38.38557879898514|
| Glucose mg/dL |57.91625377015442|125.23174622984558|
| HbA1c % |4.187408191132845|6.935937046565505|

Bounds include endpoints as a conservative closed support. BMI and HbA1c are strictly positive, and glucose is strictly below126 with a margin far larger than floating-point rounding. Source Lifelines glucose upper bound is124.46942258923741; source Pani upper bound is125.83174622984558. Thus source and target glucose selection is supported without post hoc truncation. These supports are artifacts of the chosen bounded law, not known clinical or population cutoffs; extreme obesity and glycemic tails are not represented. Complete selection metadata such as fasting and anthropometry are membership premises because the task permits no additional fields.

## Distinct uncertainties and limits

Individual dispersion comes from the beta latent draws and demographics. Sampling variation across seeds describes fictional table realizations. External coefficient uncertainty is not propagated: Jansen interval levels/SEs and Pani age-slope SE are unavailable. Structural uncertainty includes rho, linearity, residual shape, zero direct sex effect and bounded support. Population transport includes ancestry, source recruitment, serum/plasma measurement, assays, fasting, anemia/medication differences and target exclusions. These are not assigned unsupported probabilities or pooled with source precision. No causal effects, target validity, national prevalence or recovered personal measurements are claimed.
