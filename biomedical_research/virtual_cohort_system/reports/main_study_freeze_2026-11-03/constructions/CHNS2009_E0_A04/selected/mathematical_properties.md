# Probability law and moments

Write m_i, s_i and l_i for the three specification means, individual SDs and factor loadings. Let A be discrete uniform on integers 35 through 74, S be Bernoulli(0.5), and F,E_B,E_G,E_H be mutually independent standard normal variables, independent of A and S. Each generator row implements

v_i = log(1 + (s_i/m_i)^2), mu_i = log(m_i) - v_i/2,
Z_i = l_i F + sqrt(1-l_i^2) E_i,
X_i = exp(mu_i + sqrt(v_i) Z_i).

This is the law in generator.py, not a proposed moment matrix disconnected from the program. The generator computes v_i and mu_i from the specification, uses one shared normal draw per row and independent normal residuals, and applies exp without clipping, rejection or outcome-dependent selection. The scientific law has no hidden classes, quadratic normal exponent or fitted constraints. Rows are conditionally IID given the fixed specification; identifiers are deterministic labels.

All m_i,s_i are positive and finite, and all |l_i|<1. Thus Z has correlation matrix R=ll' + diag(1-l_i^2), which is strictly positive definite: for nonzero a, a'Ra=(a'l)^2+sum_i a_i^2(1-l_i^2)>0. Every Z_i is N(0,1). For any finite real exponent vector t,

E[product_i X_i^t_i] = exp(sum_i t_i mu_i + 0.5 sum_ij t_i t_j sqrt(v_i v_j) R_ij) < infinity.

The moment-generating identity for a multivariate normal proves all positive and mixed polynomial moments exist, including first, second and fourth moments needed for least-squares population projections and usual variance calculations. This claim concerns polynomial moments, not existence of the lognormal MGF at positive argument. In particular E[X_i]=m_i, Var(X_i)=s_i^2, E[X_i^2]=m_i^2+s_i^2, and Cov(X_i,X_j)=m_i m_j expm1(sqrt(v_i v_j) l_i l_j) for i not equal to j. Correlations are obtained by dividing by s_i s_j; none is a reported source relationship.

Age has mean (35+74)/2=54.5, variance (40^2-1)/12=133.25 and finite support. Female has mean 0.5, variance 0.25 and support {0,1}. BMI, glucose and HbA1c have mathematical support (0,infinity), meeting the task's strict positive BMI and nonnegative laboratory support; they are actually strictly positive almost surely. No additional range is presented as a known population cutoff. The unbounded upper tails and arbitrarily small positive levels are limitations of the assumed law, not established clinical tails. Normal floating-point generation and exponentiation are approximations to this law. An exponentiation error raises a failure and is never repaired by clipping or selectively redrawing. Runtime success remains for the isolated controller to determine.

Because the continuous joint density is positive on (0,infinity)^3 and age/sex each vary independently, no nontrivial affine combination of the requested population regressors is constant. Their covariance matrices are strictly positive definite and their intercept-including population normal equations have unique solutions. Finite samples could in principle have a degenerate age/sex realization; observed ranks must be checked after authorized execution, not assumed from the population proof.

Independence of age and sex from the continuous block makes the population E1 BMI coefficient Cov(B,H)/Var(B) and E2 glucose coefficient Cov(G,H)/Var(G). The population E3 age coefficient is exactly zero even after conditioning linearly on female, BMI and glucose. The analytic script reports these coefficients solely as consequences of the chosen law, never as targets, fitted clinical values, or source estimates. The selected source moments numerically coincide with the transported law by construction, which cannot verify selection or measurement transport.

Individual variation is encoded by F and the independent E_i. Uncertainty in the source estimates, structural loadings, lognormal tails and population/measurement transport is not represented by those random terms and is not quantified by repeated rows or seeds. No individual clinical measurements are reconstructed.
