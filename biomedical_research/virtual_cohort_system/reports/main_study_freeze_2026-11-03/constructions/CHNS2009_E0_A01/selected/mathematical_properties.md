# Probability law and its mathematical properties

The actual law implemented by `generator.py` is the product of five marginals. Let A be uniform on the 40 integers 35 through 74, F be Bernoulli with p=2049/3547, and let independent standard-normal innovations Z_B, Z_G, Z_H be independent of A and F. For each positive variable X in BMI, glucose, HbA1c, define

`v_X = log(1 + (s_X / m_X)^2)`;
`mu_X = log(m_X) - v_X/2`;
`X = exp(mu_X + sqrt(v_X) Z_X)`.

The specification supplies (m,s)=(25,3.6), (5.2,1.4), and (6.1,1.0), with units kg/m^2, mmol/L serum glucose, and HbA1c percent. These are source mean/individual-SD settings transported by assumption. They are not target estimates. `analytical_audit.py` retains a deterministic formula calculation and `analytical_results.json` records its numerical values; neither executes or imports the generator or creates rows.

## Existence, support and first two moments

Age and female have finite support. E[A]=(35+74)/2=54.5 and Var(A)=(40^2-1)/12=133.25 year^2; E[F]=p and Var(F)=p(1-p)>0. For every real finite r, the normal moment-generating identity gives `E[X^r]=exp(r*mu_X+r^2*v_X/2)`, which is finite. In particular E[X]=m_X and E[X^2]=m_X^2+s_X^2, so Var(X)=s_X^2. All required first and second moments exist. Products needed for cross-moments are finite by Cauchy-Schwarz, or directly by independence. All fourth moments also exist.

Each lognormal has support (0,infinity), so BMI, glucose and HbA1c are strictly positive under the mathematical law. Age satisfies the task exactly, and female is 0 or 1. There is no unbounded quadratic term in an exponent, mixture, clipping, truncation, source-selection exclusion or hidden clinical cutoff. Lognormal tails are unsupported structural assumptions, not inferred population tails. Extremely unusual values can occur. Finite mathematical moments do not guarantee every floating-point evaluation is representable; the code raises an error on nonfinite or nonpositive continuous output and performs no adaptive replacement.

## The exact scientific uses

With an intercept, each requested population least-squares projection is defined because its predictor covariance matrix is diagonal with strictly positive diagonal entries, and all cross-moments exist. Mutual independence implies Cov(HbA1c,age)=Cov(HbA1c,female)=Cov(HbA1c,BMI)=Cov(HbA1c,glucose)=0. Therefore E1 (BMI term adjusted for age and female), E2 (glucose term adjusted for age and female), and E3 (age term adjusted for female, BMI and glucose) are exactly zero in the population law. The intercept for each is 6.1 percent. This is an algebraic consequence of A_INDEPENDENCE, not a newly inferred result, published null effect, or target calibration. Pearson and Spearman glucose/HbA1c correlations are likewise zero in the ideal population law by independence; finite samples fluctuate.

The generated design is not guaranteed full rank for every finite random sample: a Bernoulli sample can theoretically be constant, and discrete age can theoretically fail to vary. Continuous nondegenerate predictors yield full rank almost surely conditional on a nondegenerate discrete design. Runtime diagnostics must retain a failed or unavailable fit without resampling. The generator does not build community identifiers, cluster sampling, or reference confidence intervals. Synthetic IID precision is not clinical or community-cluster inference.

## What remains uncertain

Within-person-column residual dispersion is the modeled individual variation s_X; it is not external-estimate uncertainty. All parameters are fixed across seeds. The packet supplies no estimator SE for these marginal anchors, so no estimator precision or prior distribution is invented. Population transport, the lognormal family, age composition, and independence are structural assumptions not integrated over by these seeds. Repeated seeds measure draw-to-draw variation of this fixed law only. Three final tables are not three independent biomedical studies. No individual measurement is recovered, and no causal or clinical association is established.

## Source context and overlap

All numerically used margins come from the same MIND-China analysis; their sampling dependence is unknown and they are not independent confirmations. MIND age margins are not transplanted because the source age range differs. Jansen, Bao and NGSP are contextual records only. No cross-source pooling, meta-analysis, weighting, population reconstruction or separate source analytic fit is claimed. Matching first two moments to chosen anchor numbers by formula is a feature of parameterization, not an execution-backed source check.
