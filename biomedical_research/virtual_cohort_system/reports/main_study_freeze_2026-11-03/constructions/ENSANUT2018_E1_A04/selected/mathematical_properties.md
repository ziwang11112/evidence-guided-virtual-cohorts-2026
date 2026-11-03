# Actual probability law and analytic linkage

This document describes the code in generator.py and settings in model_spec.json. The retained analytic_calculation.py independently evaluates formulas using these settings; it does not import the generator or sample individuals. It derives source moments from primitive laws, then calls the admitted source_projection operator. No numerical integration or Monte Carlo is used. analytic_results.json binds the code, specification, evidence, calculation script and operator hashes.

## Design and selection

The target table contains exactly 375 rows in each female=0/1 crossed with age bands 25–39, 40–54, 55–69 and 70–79. Within each cell, age A is discrete uniform on the inclusive integers. Each row has independent latent factors; the fixed demographic counts make rows non-IID in their design variables. The marginal mathematical target law selects each of the eight cells with probability1/8. Random permutation changes row order only. IDs are fictional and unique.

This is a law conditional on the complete stated eligibility and measurement restrictions, not a generative model of the screening process. The model does not assert which anthropometric documentation field is correct, add medication/anemia exclusion or manufacture observable diagnosis/fasting/pregnancy fields. Those restrictions are defining membership assumptions; only age, sex and numeric glucose selection can be verified from the output columns.

## Independent primitives and metabolite laws

Let C take values -1 and +1 with equal probabilities. Independently draw R_B and R_G from affine Beta laws with mean0 and variances14.56 and72. For a residual on [l,u], l<0<u, set

    k = (-l*u)/v - 1
    alpha = (-l)/(u-l) * k
    beta = u/(u-l) * k
    R = l + (u-l) * V,  V ~ Beta(alpha,beta).

Then E(R)=0 and Var(R)=v. Both shape parameters are positive for the specification's supports: BMI residual [-12,30] and glucose residual [-40,31]. The analytic script verifies the formulas and shapes, with no samples. Define

    B = 26.5 + 1.5*C + R_B
    G = 91.8 + 3*C + R_G.

Thus E(B)=26.5, Var(B)=16.81, E(G)=91.8, Var(G)=81 and Cov(B,G)=4.5. This covariance is an explicit completion assumption; neither Jansen nor Pani supplies it. It is nonzero and the resulting correlation is about0.122. A and female F are independent of these primitives. Their lack of association with B/G, and the absence of a sex coefficient below, are assumptions rather than inferred zero facts.

The covariance matrix S of (B,G) is [[16.81,4.5],[4.5,81]], with determinant1341.36>0. This follows from the independent positive-variance residuals, not from merely asserting a desired moment matrix.

## Outcome law and distinct projection constraints

Let b=0.0118924 percentage points/(kg/m^2) and g=0.01163828888888889 percentage points/(mg/dL), the two *separate* age/sex-adjusted Jansen coefficients. Let a=0.01 percentage points/year be the Pani coefficient adjusted for sex, BMI and glucose. We choose a common conditional linear model as an unverified transport/completion assumption:

    H = 5.6 + a*(A-55.5) + theta_B*(B-26.5) + theta_G*(G-91.8) + E.

E is independent and Uniform[-sqrt(3v_E),sqrt(3v_E)]. The two Jansen separate normal equations are

    16.81*theta_B + 4.5*theta_G = 16.81*b
    4.5*theta_B + 81*theta_G = 81*g.

Solving gives theta_B=0.00890935652173913 and theta_G=0.01114332463768116. In particular theta_B is not b, and theta_G is not g. For the selected Lifelines working source law, age is Uniform[55.5-sqrt(3)*9.9,55.5+sqrt(3)*9.9], and F is Bernoulli0.597, independent of the same B/G/E primitives. This law matches only the admitted rounded Table1 age/sex moments; its support and independence are assumptions. Table2's unknown row-specific populations are assumed to share this working law, an unresolved limitation.

Set v_E = 0.3^2 - a^2*9.9^2 - theta^T*S*theta. The retained calculation verifies v_E>0. Accordingly E(H)=5.6 and Var(H)=0.09 under this Lifelines working law. Directly reported percent HbA1c mean/SD are selected; converted IFCC alternatives are not additional constraints.

Residualizing B and G for A,F leaves their centered metabolic values. Therefore the separate population projections are theta_B+theta_G*4.5/16.81=b and theta_G+theta_B*4.5/81=g. These are established from the generator law, not assigned as simultaneous coefficients.

For the qualified Pani slope diagnostic, the separately declared source reference law has A=25+K where K has geometric-failures law P(K=k)=p(1-p)^k, k=0,1,..., p=1/31; F is Bernoulli0.5, independent of the same metabolic and error primitives. Its age mean is55 and variance930. This unbounded reference age support is an analytic device, not a proposed source demographic fit or target age model. It does not silently replace the source >=70 band with70–79. The full regression residual E is orthogonal to (A,F,B,G), so the age population projection is a for this law and for any nondegenerate finite-variance age law satisfying the same conditional structure. The operator evaluates the specified source moments and returns0.01. Original survey weights/IPD are unavailable, so this is not a survey replay.

Pani age-band means are not constrained or checked numerically: their covariate composition, weights and source age distribution are unreported, and the pooled conditional equation/intercept is not a reconstruction of these marginal means. Their SEs are not residual SDs. This limitation is recorded individually for all eight operations.

## Support and finite first/second moments

The target and Lifelines laws use bounded age, binary sex, compact Beta residuals, a bounded common factor and bounded outcome error. No exponentiation, quadratic unbounded term, clipping or rejection occurs. In particular B lies within[13,58] kg/m^2 and G within[48.8,125.8] mg/dL. These are technical model supports, not known population cutoffs. They guarantee positive values and strict G<126 even at their endpoints. The primitive triangle bounds imply target H in[4.2441858554,6.9458926403] percent; these conservative bounds may not be jointly attainable. HbA1c is therefore strictly positive. All first, second and cross moments exist because every target variable is bounded. The source Lifelines conservative H interval is[4.3777128255,6.8823656702].

For the Pani analytic reference, K has finite first and second moments E(K)=(1-p)/p and Var(K)=(1-p)/p^2, because 0<p<1 and geometric sums converge. H is an affine function of K plus bounded terms, so E(|H|) and E(H^2) are finite; Cauchy–Schwarz guarantees all covariance entries. At A>=25 its minimum is at least the target lower bound; its upper support is unbounded. No target rows use this reference age law. F has positive variance in each reference law; A is nondegenerate; S is positive definite; E has positive variance. Thus each population predictor covariance matrix is nonsingular and all requested population linear projections exist. A particular finite table can still have sampling fluctuations; population nonsingularity is not a proof of every finite-sample regression's success.

## Interpretation

Within-law residual variation is distinct from sampling uncertainty of external estimates, uncertainty about unreported dependencies/shapes and uncertainty in population/measurement transport. This candidate uses fixed source point estimates and fixed assumptions. Repeated seed draws do not propagate those other uncertainties or create evidence. Q3 and Q2–Q3 depend directly on the assumed covariance completion. The source coefficients do not identify them, and no causal mediation interpretation is justified. No individual measurement is recovered.
