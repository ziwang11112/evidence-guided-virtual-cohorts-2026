# Probability law, existence, support and identifiability

This document defines the submitted law, not an empirical description of CHNS.
`model_spec.json` holds all scientific constants. `analytic_source_checks.py`
performs only exact formula evaluation, finite-dimensional matrix arithmetic
and static AST inspection. It imports the assigned pure source-operation helper,
never `generator.py`. It uses no simulation, quadrature or optimization.

## Actual target law and implementation

Write A for age and F for female membership. A is discrete uniform on the task
integers 35 through 74; F is Bernoulli(p). Define a=A-E[A] and f=F-p. Independently,
T is Gamma(k_B, scale 1), U_B=(T-k_B)/sqrt(k_B), and U_G,U_H are independent
Uniform(-sqrt(3),sqrt(3)). Their means are zero and variances one. J is
Bernoulli(q), W is Gamma(k,theta), and L=J W, all independent of these variables.
The letters correspond to values in `target_context` and `shared_structure`:

```
B = b0 + bA*a + bF*f + sB*U_B
G = g0 + gA*a + gF*f + sG*(rho*U_B + sqrt(1-rho^2)*U_G) + L
H = h0 + hA*a + hF*f + betaB*(B-b0) + betaG*(G-g0) + delta*L + sH*U_H
```

The program implements these equations directly in task units. B is BMI, G is
central-serum glucose in the target interpretation and H is HbA1c percent.
Identifiers have no scientific role. There is no exponentiation of a normal or
quadratic predictor, no clipping, and no retrospective exclusion of rows.
The mixture is a mathematical metabolic component, not diagnosed diabetes or
an estimated disease prevalence. All six independent latent variables are
sampled per row, giving independent rows. This does not reproduce a community
survey design or a known age/sex composition.

## Finite moments and strict support

Age and sex are bounded. Each uniform is bounded. For Gamma(k,theta) with the
positive finite parameters specified here,

```
E[W^r] = theta^r Gamma(k+r)/Gamma(k),  r >= 0.
E[L] = q*k*theta
E[L^2] = q*k*(k+1)*theta^2
Var(L) = E[L^2] - E[L]^2.
```

Thus all integer moments of T, U_B and L exist, including first and second
moments. B,G,H are finite affine sums of these variables, so each has finite
first and second population moments; in fact every nonnegative integer moment
exists. Cauchy-Schwarz establishes finite cross moments. Unbounded upper support
does not imply divergent moments. Scientific parameters are fixed, so no
parameter mixing distribution with an unexamined moment is introduced.

The target lower bound for U_B is -sqrt(k_B)=-2. All loadings of U_B and L into
B,G,H are positive. Linear endpoint arithmetic gives valid conservative lower
bounds B>=15.595 kg/m^2, G>=4.044220509655423 mmol/L and
H>=4.484363513522538 percent. Gamma endpoints are limiting support points; the
actual draws exceed them with probability one. Their upper supports are
unbounded. These lower limits are an acknowledged modelling restriction and
exclude some physiologically possible low values; they are not population or
clinical cutoffs. A lies in 35..74 and F is 0 or 1. Each scientific column is
therefore strictly positive where required. Floating-point numerical behavior
still needs the controller's execution checks; these are population-law proofs,
not claims that every software operation has already been run.

## Exact covariance from the law

Expand the above equations about their population means using independent
components Z=(a,f,U_B,U_G,U_H,L-E[L]). If M contains their coefficients, then

```
E[B]=b0; E[G]=g0+E[L]; E[H]=h0+(betaG+delta)*E[L]
Cov(A,F,B,G,H)=M diag(Var(A),p(1-p),1,1,1,Var(L)) M^T.
```

The retained analytic output includes M, its independent-component variances,
means, covariance, support calculations and eigenvalues for every context.
This derivation ties the moments to the actual affine equations rather than a
matrix of desired correlations. Positive age and sex variances, sB>0,
sG*sqrt(1-rho^2)>0 and sH>0 ensure the five-variable covariance is positive
definite: even when L is identically zero, its first five independent columns
are triangular with nonzero diagonal. Every required population OLS projection
therefore exists and is unique. Finite-sample designs can still be exceptional;
the controller must check each table without changing or dropping its rows.

## Jansen post-selection source scenario

The source law uses the same affine equations with its separately specified
source values and L=0. Its U_B is standardized uniform, whereas the target U_B
is standardized gamma. This contextual tail assumption is declared explicitly;
both innovations have the same first two moments, allowing the common moment
derivation without assuming equal source/target distributions.

Source age is continuous uniform with mean 55.5 and SD 9.9, which implies an
assumed support approximately 38.353 to 72.647 years. These endpoints are not
reported source bounds and are not the target bounds. Female probability is
1-1176/2921. The law is declared after self-reported-diabetes, anemia and
missingness exclusions; those unobserved selection variables are not simulated.
Its glucose upper support is below 7 mmol/L, as verified by exact endpoint
arithmetic, so the declared distribution satisfies that measured source
eligibility rule. It does not claim to reconstruct the source regression rows.

For BMI and glucose, source residual variances equal the reported marginal
variance minus the age and female contributions, using the assumed independence
of A and F. This gives sB=4.088052159157856 and sG=0.49732613822309013.
With rho=0.30, let tB=0.09148*0.13 and tG=0.09148*2.29. Residualizing against
age and sex gives

```
tB = betaB + betaG*rho*sG/sB
tG = betaG + betaB*rho*sB/sG
betaB = (tB-tG*rho*sG/sB)/(1-rho^2)
betaG = (tG-tB*rho*sB/sG)/(1-rho^2).
```

The result is betaB=0.0046668871459520965 percent/(kg/m^2) and
betaG=0.1979805681743806 percent/(mmol/L). These are joint-law coefficients
obtained from two separate projections plus an assumed covariance, rather than
the two printed focal coefficients assigned to one equation. The assumed direct
age and female loadings are not recovered Jansen nuisance coefficients.

The source HbA1c mean is 0.09148*38+2.152. Its residual variance is
(0.09148*3)^2 minus the variance of the other affine response terms, giving
sH=0.2495722819775183. It is strictly positive. The source operation receives
these NGSP moments and divides HbA1c cross covariances by 0.09148 to evaluate
each native IFCC projection separately. It recovers 0.13 and 2.29 within
floating arithmetic because they are constraints. This is a consistency check,
not independent fit validation, source reconstruction or transport validation.

## Bao post-selection source scenario

This is a distinct source law, with the source female count fraction and an age
quantile function linearly interpolating the five specified probability/age
knots. The three inner knots are reported source quartiles/median; the outer
knots are assumptions. The function represents adults over 20 after the stated
source health/prior-diabetes/questionnaire exclusions. It does not narrow source
ages to the target 35..74. Its mean and second moment are the exact integrals of
each linear quantile segment: on a segment of probability width w and endpoint
ages x,y, contributions are w(x+y)/2 and w(x^2+xy+y^2)/3.

The same affine structural equations use source-specific BMI/glucose scales,
ordinary locations, female fraction and q=0.06. Source U_B is uniform. The
ordinary symmetric BMI and FPG residual scales use IQR/sqrt(3), the explicit
uniform identity. No claim is made that this matches all source marginal
quantiles after covariate effects and the upper component are added. HbA1c
residual SD, metabolic component size and extra HbA1c loading are assumptions.
The native plasma/percent Pearson operation yields 0.6168579820914971 against
the reported 0.619, a raw difference of -0.00214201790850288. No scalar fitting
or optimization was performed to obtain this result. This single descriptive
comparison is highly sensitive to unreported tails and residual choices; close
agreement does not validate those choices or transport to the target.

## Unidentified quantities and analytical uses

MIND's Spearman 0.529 remains contextual. No MIND rank distribution, mean-filled
variable pattern or tie reconstruction has been declared. A moment-only Pearson
calculation cannot stand in for this source statistic. All four relationship
operations have numerical-uptake records; this operation is explicitly not a
numerical constraint.

The target E1, E2 and E3 coefficients are algebraic consequences of the selected
law, available in `analytic_results.json`, not target truths. In particular,
although L is independent of age marginally, conditioning on glucose can make
L and age associated. E3 therefore need not equal the assumed direct age loading
0.003. With c=rho*sG/sB and v=Var(L), residualizing L against age, sex, BMI and
glucose gives gamma=v/[v+sG^2*(1-rho^2)]; the age coefficient is
`hA-delta*gamma*(gA-c*bA)`. The coefficient is fixed by completion assumptions,
not identified by Jansen's two focal slopes or Bao's correlation. The script's
full covariance projection independently records this implication.

Jansen both slopes and margins share one cohort; Bao correlation and margins
share another; MIND rank and margins share another. Cross-study participant
overlap is not audited in the packet. The NGSP relation and transformed numbers
are one deterministic representation, not additional clinical evidence. No
source CI/SE precision, uniform equivalence threshold, pooled loss or likelihood
is manufactured. Unknown external estimation uncertainty, structural uncertainty
and assay/population transport are not captured by repeated seeds. Synthetic
rows support inspection of this specified scenario, not causal conclusions,
individual measurement recovery, synthetic clinical p-values or validated
measurement replacement.
