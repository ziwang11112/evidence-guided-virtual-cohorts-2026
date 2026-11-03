# Mathematical properties of the submitted law

## Law and generator linkage

The specification supplies every scientific constant. `generate(observed,spec,seed)` requires `observed=None`. It creates the eight `design.female_values` by `design.age_bands` cells with `design.per_cell` rows. Within each cell it draws integer age uniformly over the inclusive endpoints. It then makes independent calls to `rng.gamma` or `rng.beta` according to each margin's declared family, using the exact transformations below. These rowwise draws are independent of age and female; the final permutation only changes order. It returns only row_id, age, female, bmi, glucose, hba1c. It does not construct a covariance matrix and claim that matrix is the law.

The probability statements concern the ideal continuous sampling law implemented by these standard RNG calls. The finite machine implementation tests finiteness/open supports and raises on a boundary/nonfinite result; it performs no clipping, redraw-until-favorable procedure or sample-moment normalization. A failed floating-point draw is an execution failure, not support evidence.

## Demographic support and moments

Exactly 375 rows occupy each sex-by-age-band cell, giving exactly 3000 rows and 1500 per sex. Uniform integer age on a band [a,b] has mean (a+b)/2 and variance ((b-a+1)^2-1)/12. A uniformly selected row has equal probability 1/4 for each age band, and independent female F with P(F=1)=1/2. Thus E(A) is the average of the band means and E(A^2) is the average of each band's variance plus squared mean. The retained deterministic algebra calculates these from the spec. Age is bounded by 25 and 79, and F by 0 and 1, so all their moments exist. Rows are not identically distributed before final permutation because quotas are fixed; row selection after permutation gives the stated mixture. Quotas are exact by construction, without promising exact realized integer-age frequencies.

## BMI gamma support and moments

Let m=parameters.bmi.mean and s=parameters.bmi.sd, k=(m/s)^2 and theta=s^2/m. The generator calls Gamma(k,theta). Here k>0 and theta>0, and X has support (0,infinity). For every nonnegative integer r,

E(X^r) = theta^r Gamma(k+r)/Gamma(k).

Consequently E(X)=k theta=m; Var(X)=k theta^2=s^2; E(X^2)=m^2+s^2. Both required moments and all higher positive integer moments are finite. Positivity is guaranteed by the mathematical law, but there is no finite clinical upper bound. The tail is an assumption, not observed support.

## Glucose and HbA1c beta support and moments

For either margin let l=lower, u=upper, L=u-l, p=(m-l)/L and v=(s/L)^2. Define c=p(1-p)/v-1, alpha=pc, beta=(1-p)c. The retained algebra verifies 0<p<1 and 0<v<p(1-p); hence c,alpha,beta are positive and define a proper Beta(alpha,beta) law. The generator returns X=l+L*U for U~Beta(alpha,beta).

E(U)=alpha/(alpha+beta)=p and Var(U)=p(1-p)/(c+1)=v. Therefore E(X)=m, Var(X)=s^2, E(X^2)=m^2+s^2. Glucose is almost surely strictly in (0,126) mg/dL, exactly the numerical eligibility interval; HbA1c is almost surely in (0,100) percent under its disclosed modeling bound. Bounded variables have finite moments of every nonnegative order. The beta law is specified directly for the selected population; no unselected source law, clipping or hidden truncation normalization is being asserted.

## Joint and analytical-use moments

By A_INDEPENDENCE, all distinct biomarker/demographic cross-covariances vanish in the model, and joint second raw moments equal products of marginal means. This is a structural assumption, not evidence that the real associations vanish. Conditional HbA1c expectation is its fixed marginal mean given any of the requested predictors. Each centered/scaled predictor has positive variance: Var(age10)=Var(A)/100, Var(F)=1/4, Var(bmi5)=s_B^2/25 and Var(glucose10)=s_G^2/100. Independence makes their centered population covariance matrix diagonal with positive diagonal, so it is positive definite. Adding an intercept gives a nonsingular population second-moment matrix. This establishes the existence and uniqueness of all three population OLS projections with finite residual second moments.

The Q1 age10 coefficient, Q2 bmi5 coefficient, Q3 bmi5 coefficient, their Q2-Q3 contrast, and the secondary glucose10 coefficient are all zero under this law. Population Q1 residual RMS is s_H=0.3 percentage points. These statements are derived consequences of the assumed law, not target estimates and not fitted source coefficients. Finite-sample coefficients need not be zero. Continuous, nondegenerate biomarker draws and variation in specified demographic strata give sample full rank with probability one under the ideal law; machine/finite-sample failures must still be recorded by the controller. The displayed predictor-moment results are deterministic algebra, not simulation or numerical integration.

All required weighted means, population SDs and quantiles exist: biomarkers have proper CDFs and finite second moments; age/female have finite support. Cell-standardized weights are equal for this quota design. No exponentiation of an unbounded quadratic, explosive mixture or undefined moment is hidden in the model.

## Evidence scope and uncertainty

The six biomarker first/second moments are obtained by explicit construction from selected source means and SDs, under unverified marginal transport and family assumptions. This is not reconstruction of Lifelines or validation against Mexico. Source age/sex margins are intentionally not target constraints because the task fixes another design. Duplicate unit representations are not independent evidence. The admitted non-marginal operation list is empty, so numerical_uptake.json has records=[].

Individual residual variation comes from independent gamma/beta draws. Estimation uncertainty of source means/SDs is not given a probability model. Source overlap, assay/population transport, dependence and shape uncertainty remain unresolved and are not sampled by changing seeds. All requested associations are assumption-dependent; no causal claim or recovery of individual measurements follows from finite moments or structurally valid output.
