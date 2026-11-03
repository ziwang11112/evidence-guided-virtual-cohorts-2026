# Probability law and analytic properties

## The actual generator law

Let A be uniform on the integers 35,...,74, with mean c=54.5 and variance (40^2-1)/12=133.25. Let F be Bernoulli(p), p=2049/3547, independently of A. Set D=(A-c)/10 and C=F-p. The coordinate order is BMI, glucose, HbA1c. Vectors a=(.010,.020,.015), b=(.010,-.010,.005), lambda=(.35,.65,.80), target-scenario mean m=(25,5.2,6.1), and SD s=(3.6,1.4,1) are in model_spec.json. m and s transpose reported MIND marginal scales under the explicit transport assumption; a, b and lambda are assumed. Calling them scenario targets here denotes model normalization, not hidden clinical target values.

For any real vector t in R^3 define the bounded demographic MGF

T(t) = (1/40) sum_{r=35}^{74} sum_{f=0}^{1} p^f (1-p)^(1-f) exp[t' {a(r-c)/10+b(f-p)}].

For each coordinate e_j, set M1_j=T(e_j), M2_j=T(2e_j),

v_j = log[1+(s_j/m_j)^2] - log[M2_j/M1_j^2],
ell_j = log(m_j) - log(M1_j) - v_j/2.

The retained deterministic calculation verifies v_j>0. Independently of A,F, let U and epsilon_1,...,epsilon_3 be independent standard normals. Define

Z_j = sqrt(v_j){lambda_j U + sqrt(1-lambda_j^2) epsilon_j},
X_j = exp[ell_j+a_j D+b_j C+Z_j].

These equations match generator.py directly: its demographic_mgf computes T(k e_j); its log_variances and intercepts compute v and ell; its common/individual arrays implement U and epsilon, followed by one exponentiation. There is no quadratic Gaussian exponent, clipping, truncation, rejection or feedback adjustment. The script analytic_properties.py independently implements these equations without importing generator.py and never samples rows. Its 80 finite-state terms are exact enumeration of the demographic law, not quadrature or generated participants.

## Support and existence of moments

A is integer in [35,74]; F is 0 or 1 with both categories having positive probability. Conditional residual covariance is

K = q q' + diag(v_j(1-lambda_j^2)), where q_j=lambda_j sqrt(v_j).

Because every v_j>0 and |lambda_j|<1, for nonzero w, w'Kw=(w'q)^2+sum_j w_j^2 v_j(1-lambda_j^2)>0. Conditional on any A,F, X has a nonsingular multivariate lognormal distribution with support (0,infinity)^3. Thus BMI is strictly positive and glucose/HbA1c are strictly positive (stronger than their task nonnegativity). No finite physiological upper or lower cap is claimed. Floating-point runtime validation remains the controller's responsibility; this is a mathematical, not a few-seed, argument.

For every finite real vector t, including first and second powers and every product needed below,

E[product_j X_j^t_j] = exp[t'ell + (1/2)t'Kt] T(t).

The Gaussian exponential identity is finite for all finite t because K is finite. T(t) is a finite sum of finite positive terms. Hence all real power moments of the biomarkers exist, including required first/second moments and cross-products. Multiplication by A or F remains integrable because A,F are bounded. There is no assumption that the MGF of the raw lognormal biomarker exists for positive arguments; it is the log-Gaussian MGF used here.

Substitution gives E[X_j]=m_j and E[X_j^2]=m_j^2+s_j^2 exactly: the variance identity follows from exp(v_j)M2_j/M1_j^2=1+(s_j/m_j)^2. Thus the source individual SD is total scenario SD, not the conditional log-residual SD sqrt(v_j). The exact second moments and their numeric values are retained in analytic_properties.json.

## Cross-moments and the requested projections

For j,k, E[X_j X_k] = exp[ell_j+ell_k+(v_j+v_k+2K_jk)/2] T(e_j+e_k). For j=k this includes K_jj=v_j. For B(A,F) equal to A or F,

E[B X_j] = exp[ell_j+v_j/2] (1/40) sum_r sum_f p^f(1-p)^(1-f) B(r,f) exp[a_j(r-c)/10+b_j(f-p)].

Also E[A F]=E[A]p, E[F^2]=p and E[A^2]=(1/40)sum_r r^2. These formulas create the full covariance matrix of (A,F,BMI,glucose,HbA1c); they are not a desired covariance matrix detached from the sampling law.

For each visible analysis with predictor vector W and response H=HbA1c, the intercept-including population OLS slope is Var(W)^(-1)Cov(W,H) and intercept E[H]-beta'E[W]. The script evaluates E1: W=(A,F,BMI), E2: W=(A,F,glucose), and E3: W=(F,BMI,glucose,A), preserving each separate adjustment set. They are exact consequences of this assumed law, not fitted source coefficients or new empirical findings. The reported normal-equation residual and minimum eigenvalues check numerical calculation; analytic formulas establish the meaning.

The predictor covariance matrices are nonsingular. Given any A,F, each included biomarker subset has a positive density on an open set, so an almost surely constant linear combination must have zero coefficients on the biomarkers. Independence and nondegenerate support of A and F then force their coefficients to zero. Thus no nontrivial predictor linear combination has zero variance. The population OLS moments therefore exist uniquely. Finite samples can still have rare missing-category or degenerate designs; no absolute finite-sample rank guarantee is asserted, and actual output checks remain pending. The sample residual variation is not epistemic evidence precision.

## Interpretation and uncertainty

The finite mixture is a target scenario with no diabetes/treatment/pregnancy exclusions, not a reconstruction of any external source selection. Source comparisons are unavailable. Source mean/SD rounding, sample uncertainty, assay differences, transport from 61-80-year-old MIND participants to a 35-74-year selected target, and the chosen composition and dependence remain unresolved. Structural and transport assumptions are fixed in this candidate; multiple seeds vary rows only. No generated regression or synthetic confidence interval recovers individual measurements or establishes target-population validity or clinical causality.
