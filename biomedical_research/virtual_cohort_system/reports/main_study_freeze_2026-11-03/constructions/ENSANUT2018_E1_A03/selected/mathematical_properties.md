# Probability law and analytic linkage

Write A=age in years, F=female, B=BMI in kg/m^2, G=glucose in mg/dL and H=HbA1c in percentage points. For X~Beta(a,b), define standardization U=(X-a/(a+b))/sqrt(ab/((a+b)^2(a+b+1))). The primitive factors are independent U from Beta(2,5), V from Beta(2,2), W uniform on [-sqrt(3),sqrt(3)], with zero mean and unit variance. They are independent of A,F. This independence is an explicit completion assumption.

The actual generator implements exactly:

    B = muB + sB U
    G = muG + sG (rho U + sqrt(1-rho^2) V)
    H = h0 + bA (A-a0) + bF F + bB (B-muB) + bG (G-muG) + sE W.

All scientific parameter values and provenance are in model_spec.json. rho=0.30 and bF=0 are unmeasured assumptions. The generator does not clip, exponentiate, reject or condition sampled observations. It is a direct law for the task-selected population. Clinical selection beyond the emitted columns is a population-membership assumption; absence of diagnosis or measurement errors is not empirically verified by fictional data.

The target contains exactly 375 rows per prescribed sex by age-band cell. Ages are independent discrete uniforms within their allocated cells. Rows have independent residual factors and ages within their fixed cells; they are not one iid national sample. The displayed target-law moments correspond to a uniformly selected row from the balanced design. F and A are independent in that design, with F Bernoulli(0.5). All moments are finite because target A,F,U,V,W are bounded. The support bounds in analytic_results.json follow directly by summing endpoint extrema of the independent factors; they establish B>0, 0<G<126, H>0 without relying on a few finite simulation seeds. The additional narrower supports are modeling choices, not clinical cutoffs. No generated table was used in their calculation.

# Separate projections and first/second moments

The covariance of B,G is Sigma_BG=[[sB^2,rho sB sG],[rho sB sG,sG^2]]. Its determinant is sB^2 sG^2(1-rho^2)>0. Because B,G are independent of A,F, the two Jansen age/sex-adjusted projections require Cov(B,H)=mB sB^2 and Cov(G,H)=mG sG^2. The joint conditional coefficients therefore solve Sigma_BG * (bB,bG)' = (mB sB^2,mG sG^2)'. They are not the two reported projections copied into one equation. The fully adjusted Pani age projection equals bA because the conditional residual has mean zero given all predictors. This equality is transported as an explicit assumption; it is not a causal conclusion.

For each declared source law, let Z=(A-EA,F-EF,U,V,W). Its independent primitive covariance is diagonal. The retained script constructs the loading matrix L from the exact equations above, derives Cov(A,F,B,G,H)=L Cov(Z) L', and derives E[H]=h0+bA(E[A]-a0)+bF E[F]. Every variable's second raw moment is Var(X)+E[X]^2. No desired covariance matrix is directly inserted. Positive sE and nonsingular source predictors make the five-variable covariance positive definite. The analytic source projection operator then uses those derived moments. Its success verifies arithmetic, not the truth of the assumed source distributions or transfer.

The selected Lifelines context has age=55.5+9.9*standardized Beta(2,2), female Bernoulli(0.597), and the same B,G,H equation. Its age shape/support and independence are assumptions; the admitted mean, SD and sex proportion supply only those marginal moments. The residual variance is calculated as 0.3^2-bA^2*9.9^2-beta' Sigma_BG beta, which the retained script verifies is positive. Thus the source HbA1c mean and SD are exactly5.6 and0.3 in the chosen percent representation. Table1 applicability to Table2's unresolved rows is explicitly assumed.

The selected Pani context uses assumed equal masses for the eight reported age bands. Finite bands have integer-uniform age. The open band has A=70+K with P(K=k)=p(1-p)^k, k>=0 and p=0.1. Its mean is70+(1-p)/p and variance(1-p)/p^2. The age support has no upper cutoff; age79 is not transplanted from the target. This unbounded mathematical tail is a source-context approximation, including biologically implausible remote ages, not a claim about human lifespan. Its moments of every finite order exist because the geometric tail decays exponentially. H is affine in A plus bounded factors, so its first and second moments, and the linear-projection moments, also exist. H remains positive because bA>0 and A>=25 with bounded negative residual contribution. No exponentiation or unbounded quadratic term appears.

For each Pani age band, independence gives E[H I_band]/P(band)=h0+bA(E[A|band]-a0)+bF P(F=1). The script retains the actual numerator and denominator and raw discrepancies. The eight source means are diagnostics of this assumed extension, not fitted target age means. Their lack of agreement is preserved. Equal source band masses are not estimated from the published unweighted counts; the original survey law is unavailable.

# Uncertainty and limitations

The residual W represents individual heterogeneity conditional on the assumed predictors. Source sampling uncertainty is separate: Pani SEs describe estimated means, Jansen's printed confidence bounds lack an admitted confidence level, and no SE is imputed from them. The fixed parameter set does not propagate these uncertainties, unknown BMI/glucose dependence, population transport, assay changes or structural alternatives. Those omissions cannot be remedied by generating more rows or seeds. Converted and directly reported unit representations are not independent evidence. These fictional records recover no individual measurements and establish neither causal effects nor target-population validity.
