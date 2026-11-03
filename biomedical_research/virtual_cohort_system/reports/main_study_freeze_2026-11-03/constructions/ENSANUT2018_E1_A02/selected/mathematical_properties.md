# Actual law and its moments

The submission models an already selected population. It does not simulate diagnosis, fasting records, pregnancy/lactation, anemia, medication, missingness or measurement-route documentation. Those task conditions identify the intended use; their effect on the transported law is unassessed.

Let U_B, U_G and U_H be independent copies of U=6(T-1/2), T~Beta(4,4). These factors are independent of age A and sex F. The beta variance formula gives E(U)=0, Var(U)=1 and support [-3,3]. The standardization in generator.py is the identical expression sqrt[4(2 alpha+1)](T-1/2), with alpha=4 from the specification.

Use s_B=4.1, s_G=9, rho=0.25. The assignments are:

- B=26.5+s_B U_B.
- G=91.8+s_G[rho U_B+sqrt(1-rho^2) U_G].
- H=5.6+c_A(A-55.5)+c_F F+c_B(B-26.5)+c_G(G-91.8)+s_H U_H.

Here c_A=0.01 and c_F=0. The two remaining conditional coefficients are derived, rather than equated to separate source regression coefficients. Denote the admitted separate Jansen slopes by j_B=0.0118924 and j_G=0.01163828888888889. Because residualizing on independent age and sex leaves B and G centered, the separate BMI projection is c_B+c_G rho s_G/s_B and the separate glucose projection is c_G+c_B rho s_B/s_G. Therefore:

c_B=(j_B-rho s_G j_G/s_B)/(1-rho^2),

c_G=(j_G-rho s_B j_B/s_G)/(1-rho^2).

Their denominator is 0.9375>0. This is a declared dependence scenario: the packet does not identify rho, independence from age/sex, or the fully adjusted BMI effect. In particular Q3 and Q2-Q3 are assumption-dependent.

# Source-context laws and analytic linkage

For Lifelines, define A=55.5+9.9 U_A with an independent standardized Beta(4,4) factor, and F~Bernoulli(0.597) independently. This matches the source age moments but assumes a continuous age shape and technical age support [25.8,85.2]. The reported age/sex margins are treated as applying to both Table2 row-specific sets despite unknown row n. These are substantive source-context assumptions, not recovered source observations. The BMI, glucose and HbA1c assignments above are unchanged.

Set s_H^2=0.3^2-c_A^2(9.9)^2-V_BG, where V_BG=c_B^2 s_B^2+c_G^2 s_G^2+2 c_B c_G rho s_B s_G. The retained calculation checks positivity and records its actual value. Thus Lifelines E(H)=5.6 and Var(H)=0.3^2 under this law. The printed percent mean and SD are selected; the rounded IFCC-derived percent alternatives are not additional independent constraints.

For the separate Pani population law, A=25+Z with Z~Gamma(k=4,scale=7.5), F~Bernoulli(0.5) independently, and the same B/G/H assignments. The age law has E(A)=55 and Var(A)=225. Its upper tail is unbounded; the target age79 limit is never used for the source >=70 band. Its smooth continuous age density and source sex proportion are assumptions. The joint predictor covariance is positive definite: age variance is positive, sex variance is positive, and the B/G block determinant is s_B^2 s_G^2(1-rho^2)>0. Since E(U_H|A,F,B,G)=0, the full population regression of H on A,F,B,G has exactly the declared conditional coefficients, including age 0.01. This verifies the qualified population projection only; actual NHANES survey-weighted estimation cannot be replayed.

The retained analytic script forms the covariance by affine transformation of these independent factors: Cov(X,H)=Cov(X,X)c and Var(H)=c'Cov(X,X)c+s_H^2. It does not supply an arbitrary desired covariance matrix. It independently rederives the coefficients and residual variance and compares them with the exact specification consumed by generator.py. It hashes that code and specification and passes the resulting source moments to the admitted source_projection function. No generator is imported, called or sampled.

For Pani age bands [l,u), the gamma survival function for integer k is S_k(t)=exp(-t) sum_(j=0)^(k-1) t^j/j!. Let t_l=(l-25)/7.5, t_u=(u-25)/7.5 and S_k(infinity)=0. Then P_band=S_k(t_l)-S_k(t_u), and E[A I_band]=25 P_band+7.5 k [S_(k+1)(t_l)-S_(k+1)(t_u)]. Because B and G are independent of A and centered, E[H|band]=5.6+0.01(E[A I_band]/P_band-55.5). The actual script evaluates these finite sums, not quadrature or random draws. The eight discrepancies are compatibility diagnostics. Reported SEs remain estimator uncertainty; the law is not fitted to those means.

# Target law, support and existence

For each of F=0,1 crossed with [25,39], [40,54], [55,69], [70,79], the generator creates exactly 375 records and samples age uniformly over the band's integer years. Thus quota counts and 3000 records hold by construction. Independent beta factors are then assigned to each record. A randomly selected row has an equal eight-cell mixture law. Within-cell ages need not have exactly equal counts.

B lies in [14.2,38.8]. G lies in 91.8 +/- 27(0.25+sqrt(0.9375)), a positive interval with upper endpoint below126. These technical support limits are not learned population cutoffs; the construction will omit wider BMI tails. There is no clipping, rejection or exponentiation in the generator. H has minimum 5.6+0.01(25-55.5)-3[abs(c_B s_B+c_G s_G rho)+abs(c_G s_G sqrt(1-rho^2))+s_H], verified positive. Its maximum uses age79 and the plus sign. Numerical support results are retained in analytic/results.json.

Target A,F,B,G,H are bounded random variables, so their absolute first moments, second moments, all higher polynomial moments and every needed regression cross-moment exist. The fixed-cell cohort is not iid across all rows, but rowwise moments and equal-cell population estimands remain well-defined. Predictor covariance remains nonsingular by independent nondegenerate factors and nonzero within-design age variance. Conditional mean residualization therefore has a well-defined population projection.

The Lifelines law is bounded too. The Pani source law has unbounded gamma age and hence unbounded H above, but gamma has finite moments of every nonnegative integer order, E(Z^r)=7.5^r Gamma(4+r)/Gamma(4). H is affine in Z plus bounded variables. The triangle and Cauchy-Schwarz inequalities establish finite E|H| and E(H^2), and finite cross-moments. Its positive lower bound follows from A>=25. No exponential of an unbounded quadratic, lognormal tail or hidden mixture is present.

# Meaning of uncertainty

U_H and the B/G factors model individual variation. Fixed external coefficients are plug-in estimates, with unavailable Jansen CI levels/SE and Pani slope SE. They are not sampled across seeds. Structural uncertainty in factor family, rho, covariate independence and sex effect is separate from statistical precision. Transport to Mexican adults and task-specific selections is unverified. Additional seeds change fictional residual draws and finite-sample summaries; they do not create clinical evidence, estimate source uncertainty, or recover individual measurements.
