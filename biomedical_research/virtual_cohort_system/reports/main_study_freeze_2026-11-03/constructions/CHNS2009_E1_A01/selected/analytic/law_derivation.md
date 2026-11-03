# Declared law and its exact moments

This derivation defines selected-population scenarios, not reconstructed source participants. No simulated rows, numerical quadrature or target observations are used. The generator applies the same equations below using `parameters.target`; the analytic calculation substitutes the separately declared source settings. It does not invoke the generator or provide a source execution adapter.

Let A be age, F be binary female membership, a=A-mA and f=F-pF. Let UB, UG and UH be mutually independent Uniform(-sqrt(3),sqrt(3)) variables. They each have mean zero and variance one. Let D be Bernoulli(pD) and Z standard normal, independent of all other primitives. Define T=mT exp(sT Z-sT^2/2), Q=D T. The named source settings and the target settings are in model_spec.json. Independence and each source support are explicit assumptions, not reported empirical facts.

For each context define b=sB UB and g=sG[r UB+sqrt(1-r^2) UG]. The shared structural family is:

```
BMI = mB + aB*a + fB*f + b
G   = mG + aG*a + fG*f + g + Q
H   = mH + aH*a + fH*f + thetaB*b + thetaG*g + k*Q + sH*UH
```

G is native source FPG for Jansen and Bao; it is central-serum glucose in the target. H is native IFCC HbA1c for Jansen and percent for Bao and target. Cross-context use of the residual response mechanism is an unvalidated transport assumption, not a specimen conversion. Target and Bao use thetaB and thetaG multiplied by 0.09148. The 2.152 offset is relevant only to levels; target/Bao levels are separately assumed rather than transported from Jansen.

For every context, E(Q)=pD*mT and Var(Q)=pD*mT^2 exp(sT^2)-(pD*mT)^2. Jansen pD=0, so Q=0. The exact mean vector is (mA,pF,mB,mG+E(Q),mH+k E(Q)). The six independent centered primitives are (a,f,UB,UG,UH,Q-E(Q)), with diagonal covariance (Var(A),pF(1-pF),1,1,1,Var(Q)). The rows of the loading matrix L are:

```
age:    (1,  0,  0,                   0,                      0,  0)
female: (0,  1,  0,                   0,                      0,  0)
BMI:    (aB, fB, sB,                  0,                      0,  0)
G:      (aG, fG, sG*r,                sG*sqrt(1-r^2),         0,  1)
H:      (aH, fH, thetaB*sB+thetaG*sG*r,thetaG*sG*sqrt(1-r^2), sH,k)
```

Therefore covariance is exactly L diag(v) L'. This is an analytic identity for the stated law, not an arbitrary covariance matrix supplied to the source arithmetic utility. `derive_moments.py` constructs L and v from the same scientific settings used by the generator and retains both along with the resulting moments. It separately checks positivity/support and calls the supplied arithmetic utility only after this derivation.

## Jansen selected law and separate projections

The source law is defined directly conditional on the reported eligibility: selected unrelated western-European adults without self-reported diabetes, anemia or missing required values. It models the already selected population; no claim is made about how conditioning acted on an unselected parent. Source age is continuous uniform with mean 55.5 and SD 9.9, not target age 35..74. Female probability is 1-1176/2921, preserving category membership despite unresolved original numeric coding. BMI and FPG residual SDs subtract the explicitly assumed age/female variance contributions from reported total variances. Source FPG support is analytically below 7, so the declared selected law satisfies the diabetes threshold without post hoc clipping or deletion. Other eligibility properties are fixed context attributes; their distributions and selection probabilities are not reconstructed.

Since a and f are independent of b,g and Q=0, residualization on the span of intercept, age and female gives precisely b and g. The two separate population OLS slopes are:

```
HbA1c ~ 1+age+female+BMI:  cB = thetaB + thetaG*r*sG/sB
HbA1c ~ 1+age+female+FPG:  cG = thetaG + thetaB*r*sB/sG
```

The reported cB=0.13 and cG=2.29 constrain separate projections. Setting r=0.25 is an additional covariance assumption. Solving the above two equations gives thetaB=(cB-r*sG/sB*cG)/(1-r^2) and thetaG=(cG-r*sB/sG*cB)/(1-r^2). Neither structural coefficient is simply pasted from a source regression. Changing the unreported residual covariance changes these structural coefficients. Source HbA1c residual variance is 3^2 minus its age/female variance and the full variance of thetaB*b+thetaG*g, including their covariance. The retained script confirms it is positive.

These equal-weight, intercept-including, no-interaction functionals are qualified scenarios. Exact original row membership, weights, intercept convention and source estimator uncertainty remain unavailable. Equality to their fixed source points is imposed by this construction, hence not independent validation.

## Bao selected law and Pearson diagnostic

The Bao law is separately conditional on its reported exclusions, including no previously diagnosed diabetes but allowing screen-detected high glycemia. Its continuous age support is (20.01,80.01), an assumption separate from target support and avoiding the unresolved age-20 boundary. Its latent excess component is labelled screen-detected heterogeneity, not known diabetes. Neither source eligibility probabilities nor exact participants are recovered. The source sex count fraction is used directly; reported medians are chosen baseline anchors. They are not claims that the full generated law has the same quantiles. The 4% class, all residual scales and covariances are explicit assumptions.

The exact law covariance above yields Pearson Cov(G,H)/sqrt(Var(G)Var(H)). That calculation is compared descriptively with 0.619. The law is not fitted to that correlation, and a discrepancy does not supply a pooled penalty or target correction. All original imputation/weighting uncertainty remains unresolved.

## Additional target use

The target age and female effects are chosen separately. With vB=sB^2, vG=sG^2+Var(Q), cBG=r*sB*sG, dB=thetaB*sB^2+thetaG*cBG and dG=thetaB*cBG+thetaG*sG^2+k*Var(Q), the model's fully adjusted residual slopes are the solution of [[vB,cBG],[cBG,vG]] beta=(dB,dG). Its fully adjusted age coefficient is aH-betaB*aB-betaG*aG. This is algebraically determined by the chosen law; it is not an empirically identified age effect or a newly inferred target answer. Separate target projections likewise follow from this covariance. No target-reference statistic has been used.
