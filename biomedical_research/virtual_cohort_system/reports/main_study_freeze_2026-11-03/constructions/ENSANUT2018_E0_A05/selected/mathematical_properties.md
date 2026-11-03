# Law and moment existence

The cohort contains 375 independent fictional rows within each of the eight fixed female-by-age-band cells; only the final row order is shuffled. A uniformly selected row has female F equally likely 0 or 1 and, independently, age chosen from an equal mixture of discrete uniform laws on 25–39, 40–54, 55–69 and 70–79. Let m and v be the mixture's exact mean and variance. Define A=(age-m)/sqrt(v), S=2F-1. Thus E(A)=E(S)=0, Var(A)=Var(S)=1 and Cov(A,S)=0. The finite quotas create a sampling design; they do not change these single-row mixture moments or imply that the whole cohort is iid.

Independently of age/sex and each other, draw X_B, X_G, X_H from Beta(k,k), where k=3. A beta density with positive shape parameters is a proper finite probability law on (0,1). E(X)=1/2 and Var(X)=1/[4(2k+1)]. Define U=sqrt(4(2k+1)) (X-1/2). Each U has mean zero, variance one and support contained in [-sqrt(7),sqrt(7)]. The factor vector Z=(A,S,U_B,U_G,U_H) therefore has mean zero and identity covariance under this explicitly assumed independence structure.

Write b_A=.12, b_S=.10, g_A=.18, g_S=-.05, g_B=.30, h_A=.22, h_S=-.06, h_B=.20 and h_G=.50. Let r_B=sqrt(1-b_A²-b_S²), r_G=sqrt(1-g_A²-g_S²-g_B²), r_H=sqrt(1-h_A²-h_S²-h_B²-h_G²). All radicands are positive. The submitted generator implements exactly:

* B=26.5+4.1(b_A A+b_S S+r_B U_B).
* G=91.8+9(g_A A+g_S S+g_B U_B+r_G U_G).
* H=5.6+.3(h_A A+h_S S+h_B U_B+h_G U_G+r_H U_H).

The constants, loadings and beta shape reside in model_spec.json with evidence or assumption provenance. No hard-coded scientific effect occurs only in the generator. BMI B is kg/m², glucose G mg/dL and HbA1c H percent. This law is directly conditional on the task selection; it is not a full population law filtered by unobserved diagnosis or measurement variables.

## Support and finite moments

All components of Z are bounded, and each output is affine in Z. The exact extremal interval calculation is retained in analytic_calculation.py and analytic_results.json. It verifies BMI>0, glucose>0, glucose<126, HbA1c>0, integer age 25–79, and female in {0,1}, with substantial numerical margins. Endpoints are closure bounds, not claims that continuous residual endpoints occur with positive probability. These ranges are model-imposed support restrictions; they are not empirical or clinical population cutoffs. They suppress tails absent from the admitted evidence.

For any affine output Y=m_Y+l_Y Z, bounded Z yields a finite deterministic M with |Y|≤M, so E|Y|≤M and E(Y²)≤M². By the same argument every polynomial moment and every pairwise product is finite; Cauchy–Schwarz also establishes E|Y_iY_j|<infinity. There is no exponentiation, unbounded quadratic, clipping, rejection or hidden mixture tail. Means and covariance are exactly E(Y)=m_Y and Cov(Y)=L Lᵀ, where L is the lower triangular loading matrix retained in analytic_results.json. Its diagonal is (sqrt(v), .5, 4.1 r_B, 9 r_G, .3 r_H), all nonzero. Consequently the joint covariance is positive definite and each requested predictor covariance is invertible. All required population least-squares projections and residual second moments exist uniquely. This is a proof about the law, not inference from finite output seeds.

## Law-linked calculations

The retained deterministic script derives the age mean/variance from the finite age bands, builds L from the submitted specification, and calculates raw means, covariance and second-moment matrices, support intervals, both HbA1c projections and the secondary glucose10 projection by linear algebra. It never imports the generator and never draws random values or enumerates synthetic rows. It uses no numerical quadrature. These calculations are consequences of the assumed task law, not a free-standing matrix of desired moments and not source-context replay.

The projection algebra is also explicit. Residualizing B on A,S gives 4.1 r_B U_B; therefore Q2_bmi5=5(.3/4.1)h_B/r_B. Conditioning on glucose as well gives q_G=h_G/r_G, q_B=(h_B-q_G g_B)/r_B and q_A=h_A-q_G g_A-q_B b_A. Hence Q3_bmi5=5(.3/4.1)q_B and Q1_age10=10(.3/sqrt(v))q_A. The full-model residual is .3 r_H U_H, with RMS .3 r_H. Q2-Q3 is the difference of those descriptive coefficients. Matrix and substitution calculations are cross-checked in the retained result.

## Interpretation and limits

The transferred BMI, glucose and HbA1c marginal means/SDs follow algebraically under the equal-cell target-design law. They are selected source anchors under an explicit transport assumption, not observed Mexican target values. The Jansen source's reported age and sex distribution are not imposed on the task design. No source population has been reconstructed and all target-table source comparisons remain unavailable. Duplicate IFCC/percent representations are not fitted twice. The dependence loadings, symmetric beta shapes, independence of residual factors, absence of interactions and conditional selection model are assumptions. E0 does not identify Q1, Q2 or Q3.

Residual variation is individual synthetic variation under a fixed law. External estimate uncertainty is unreported and is not replaced by residual SD or sample size. Structural and population-transport uncertainty remain unquantified; repeated seeds cannot resolve them. This table does not recover individual measurements, show causal effects, establish medication/anemia exclusions, or establish clinical validity or national representativeness.
