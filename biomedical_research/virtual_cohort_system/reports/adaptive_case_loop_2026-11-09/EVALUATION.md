# Adaptive existing-case evaluation

developmental existing case; every attempted version and planned endpoint retained

| Stage | Analysis | Unit | Generated mean [seed range] | Available / attempted | Existing sample [supplied interval] | Absolute point difference |
|---|---|---|---:|---:|---:|---:|
| candidates/initial | K02-HDL-BMI | mg/dL per 5 kg/m^2 | -1.1898 [-1.4824, -1.0297] | 3 / 3 | -4.6230 [-8.3920, -0.8541] | 3.4332 |
| candidates/initial | K02-TC-BMI | mg/dL per 5 kg/m^2 | 10.6997 [10.1613, 11.1775] | 3 / 3 | 5.6831 [-3.7535, 15.1197] | 5.0166 |
| candidates/initial | K02-LIPID-RESIDUAL | 1 | 0.1383 [0.1229, 0.1658] | 3 / 3 | 0.5121 unavailable | 0.3738 |
| candidates/dependence_sensitivity | K02-HDL-BMI | mg/dL per 5 kg/m^2 | -1.1999 [-1.4770, -1.0310] | 3 / 3 | -4.6230 [-8.3920, -0.8541] | 3.4231 |
| candidates/dependence_sensitivity | K02-TC-BMI | mg/dL per 5 kg/m^2 | 14.7893 [14.2912, 15.2518] | 3 / 3 | 5.6831 [-3.7535, 15.1197] | 9.1062 |
| candidates/dependence_sensitivity | K02-LIPID-RESIDUAL | 1 | 0.1986 [0.1837, 0.2257] | 3 / 3 | 0.5121 unavailable | 0.3135 |

Seed ranges are Monte Carlo variation, not clinical CIs. Reference slope intervals retain their supplied HC3 conditional sensitivity meaning; they are not equivalence margins.

## Initial to final

| Analysis | Final minus initial | Change in distance to sample point estimate (negative = closer) |
|---|---:|---:|
| K02-HDL-BMI | 0.0000 | 0.0000 |
| K02-TC-BMI | 0.0000 | 0.0000 |
| K02-LIPID-RESIDUAL | 0.0000 | 0.0000 |

## Dispersion and coverage

| Stage | Diagnostic | Unit | Mean | Reference | Available / attempted |
|---|---|---|---:|---:|---:|
| candidates/initial | total_cholesterol.sd_sample | mg/dL | 46.1168 | 42.8466 | 3 / 3 |
| candidates/initial | hdl_cholesterol.sd_sample | mg/dL | 14.5611 | 20.1756 | 3 / 3 |
| candidates/initial | total_cholesterol.conditional_rms | mg/dL | 44.1161 | unavailable | 3 / 3 |
| candidates/initial | hdl_cholesterol.conditional_rms | mg/dL | 14.4646 | unavailable | 3 / 3 |

candidates/initial: 3 successful / 3 attempted tables; all 26 planned endpoint records per attempt retained; 0 unavailable endpoint values.

| candidates/dependence_sensitivity | total_cholesterol.sd_sample | mg/dL | 47.1385 | 42.8466 | 3 / 3 |
| candidates/dependence_sensitivity | hdl_cholesterol.sd_sample | mg/dL | 14.5785 | 20.1756 | 3 / 3 |
| candidates/dependence_sensitivity | total_cholesterol.conditional_rms | mg/dL | 44.3587 | unavailable | 3 / 3 |
| candidates/dependence_sensitivity | hdl_cholesterol.conditional_rms | mg/dL | 14.4809 | unavailable | 3 / 3 |

candidates/dependence_sensitivity: 3 successful / 3 attempted tables; all 26 planned endpoint records per attempt retained; 0 unavailable endpoint values.

## Limits

- One adaptive author and an already exposed reference; no new independent clinical confirmation.
- Twenty-one diagnostics have no reference; all remain generated-only.
- No causal attribution of changes to retrieval, skill or feedback; all endpoints retained.
- Repeated direct rows across seeds are one table, not independent draws.
