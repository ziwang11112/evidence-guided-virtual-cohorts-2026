# Mathematical properties of the submitted law

All component latent correlation matrices were positive definite in the actual source fitting; their minimum eigenvalues are [0.6005470253580362, 0.37974199937744874, 0.4530887708206647]. The fit reports retain all source constraints and integration-order checks. A local constrained entropy solution is not a certified global optimum.

Biomarkers are positive lognormal, shifted positive lognormal or explicitly bounded truncated-lognormal transforms of finite-dimensional Gaussian variables. All polynomial moments of ordinary/shifted lognormal variables exist; the truncated glucose margins have bounded support. Jansen percent HbA1c equals 2.152 plus a positive lognormal term, preserving positivity after conversion back to native IFCC. There is no exponentiation of an unbounded lognormal predictor. Finite mixtures preserve finite polynomial moments.

CHNS age is a bounded integer quantile transform on 35-74, with binary sex and a fixed finite source-donor mixture. ENSANUT has eight exact age/sex cells. Within each integer-age CDF mass, latent age is a truncated Gaussian; conditional biomarker latent variables are Gaussian. Their finite mixture therefore has finite exponential-linear moments. The sampler does not exponentiate a quadratic or otherwise add an unreviewed tail law.

Separate source age/selection laws determine the source moment constraints. Target age/sex rules do not replace source composition in those constraints. Source means/SDs do not identify the full joint population. Independent sex, latent Gaussian dependence, uniform age approximations and donor transport are explicit assumptions. MIND Spearman uses a continuous smoothed copula law, not reconstruction of original mean-filling/ties.

Generated rows have not yet been sampled. Floating-point endpoint/overflow/support failures remain possible and fail an execution without clipping, repairs or redraws. Mathematical moment existence does not establish biological realism, target usefulness, calibrated uncertainty or patient-specific measurements.
