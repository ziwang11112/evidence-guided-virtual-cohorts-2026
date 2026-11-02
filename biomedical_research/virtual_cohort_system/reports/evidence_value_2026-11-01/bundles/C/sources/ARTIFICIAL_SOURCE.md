# Artificial population-statistic note

Invented fixture only. This is not a paper, dataset release or clinical result.

Artificial source with Pr(g=1)=0.5; no exclusions or missingness.

## S1: exact univariate and pairwise functionals

E_G_MEAN: 0.5; Section S1: g population mean

E_G_SD: 0.5; Section S1: g population SD

E_X_MEAN: 0; Section S1: x population mean

E_X_SD: 1; Section S1: x population SD

E_Y_MEAN: 0.69999999999999996; Section S1: y population mean

E_Y_SD: 1.1146748404803977; Section S1: y population SD

E_COV_G_X: 0; Section S1: population covariance g,x

E_COV_G_Y: 0.14999999999999999; Section S1: population covariance g,y

E_COV_X_Y: 0.14999999999999999; Section S1: population covariance x,y

No normal, Gaussian-copula, residual-distribution or independence family is reported by S1.

## S2: group-conditional population analysis

Within each g, E[y|x,g] is linear with the stated intercept/slope, and Var(y|x,g) is the square of the stated residual SD for every x. This reports conditional first and second moments, not a distribution for the errors or x. The within-group x mean and population SD are stated separately. Population OLS includes an intercept, uses x as the sole predictor, and has no weighting, other adjustment, selection or missing-data processing. Residual SD is sqrt(E[(y-intercept-slope*x)^2|g]), not a standard error.

E_G0_X_MEAN: 0; Section S2: g=0 x mean

E_G0_X_SD: 1; Section S2: g=0 x SD

E_G0_Y_INTERCEPT: 0.40000000000000002; Section S2: g=0 y~1+x intercept

E_G0_Y_SLOPE: -0.54999999999999993; Section S2: g=0 y~1+x x coefficient

E_G0_RESIDUAL_SD: 0.80000000000000004; Section S2: g=0 y~1+x residual SD

E_G1_X_MEAN: 0; Section S2: g=1 x mean

E_G1_X_SD: 1; Section S2: g=1 x SD

E_G1_Y_INTERCEPT: 1; Section S2: g=1 y~1+x intercept

E_G1_Y_SLOPE: 0.84999999999999998; Section S2: g=1 y~1+x x coefficient

E_G1_RESIDUAL_SD: 0.80000000000000004; Section S2: g=1 y~1+x residual SD
