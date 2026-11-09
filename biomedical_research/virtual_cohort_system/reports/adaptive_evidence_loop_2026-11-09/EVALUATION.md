# Adaptive existing-case evaluation

developmental existing case; every attempted version and planned endpoint retained

| Stage | Analysis | Unit | Generated mean [seed range] | Available / attempted | Existing sample [supplied interval] | Absolute point difference |
|---|---|---|---:|---:|---:|---:|
| candidates/initial | K02-HDL-BMI | mg/dL per 5 kg/m^2 | -0.9882 [-1.3418, -0.7175] | 3 / 3 | -4.6230 [-8.3920, -0.8541] | 3.6348 |
| candidates/initial | K02-TC-BMI | mg/dL per 5 kg/m^2 | 8.1278 [7.3291, 8.7267] | 3 / 3 | 5.6831 [-3.7535, 15.1197] | 2.4447 |
| candidates/initial | K02-LIPID-RESIDUAL | 1 | 0.1517 [0.1287, 0.1655] | 3 / 3 | 0.5121 unavailable | 0.3604 |

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
| candidates/initial | total_cholesterol.sd_sample | mg/dL | 31.5290 | 42.8466 | 3 / 3 |
| candidates/initial | hdl_cholesterol.sd_sample | mg/dL | 17.8231 | 20.1756 | 3 / 3 |
| candidates/initial | total_cholesterol.conditional_rms | mg/dL | 30.0550 | unavailable | 3 / 3 |
| candidates/initial | hdl_cholesterol.conditional_rms | mg/dL | 17.6443 | unavailable | 3 / 3 |

All attempted tables and 26 endpoint records per attempt retained.

## Limits

- One adaptive author and an already exposed reference; no new independent clinical confirmation.
- Twenty-one diagnostics have no reference; all remain generated-only.
- No causal attribution of changes to retrieval, skill or feedback; all endpoints retained.
- Repeated direct rows across seeds are one table, not independent draws.
