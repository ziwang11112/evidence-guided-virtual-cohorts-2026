# Complete aggregate endpoint appendix

All 31 prespecified endpoints are shown. A/B denote constructions 1/2; each seed column represents a unique 2,000-row fictional table. Initial and final labels have identical values because both constructions retained their generators. This appendix does not treat 12 labels as 12 independent cohorts.

Reference n = 6,931. Reference bands are empirical cluster-resampling stability bands (399/399 valid), not confidence intervals or equivalence bounds. SD uses normalized weights and no degrees-of-freedom correction; source-feedback SD uses the separate sample-SD convention. Quantiles use the inverted empirical CDF. Values are rounded only for display; CSV preserves numeric precision.

## Associational projections and residual spread

| Endpoint (unit) | Reference | Empirical band | A_18203 | A_18211 | A_18223 | B_18203 | B_18211 | B_18223 |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| Q1_age10 (HbA1c pp / 10 years) | 0.075132 | 0.067124–0.082185 | 0.098499 | 0.099857 | 0.095317 | 0.095906 | 0.104439 | 0.101859 |
| Q2_bmi5 (HbA1c pp / 5 kg/m²) | 0.083643 | 0.070373–0.095214 | 0.059041 | 0.058814 | 0.058665 | 0.050316 | 0.057074 | 0.058761 |
| Q3_bmi5 (HbA1c pp / 5 kg/m²) | 0.056638 | 0.043901–0.068006 | 0.024784 | 0.024267 | 0.023721 | 0.016307 | 0.028113 | 0.019165 |
| Q2_minus_Q3_bmi5 (HbA1c pp / 5 kg/m²) | 0.027005 | 0.021969–0.032421 | 0.034256 | 0.034546 | 0.034944 | 0.034009 | 0.028962 | 0.039596 |
| glucose10_age_sex (HbA1c pp / 10 mg/dL) | 0.1142 | 0.099957–0.129289 | 0.115931 | 0.122518 | 0.11885 | 0.104657 | 0.114221 | 0.122667 |
| q1_residual_rms (HbA1c pp) | 0.488478 | 0.445775–0.53377 | 0.259457 | 0.254766 | 0.259764 | 0.257931 | 0.255569 | 0.254496 |

## age: marginal diagnostics

| Endpoint (unit) | Reference | Empirical band | A_18203 | A_18211 | A_18223 | B_18203 | B_18211 | B_18223 |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| age.mean (years) | 53.422346 | 53.336149–53.523577 | 53.863 | 53.9415 | 53.8745 | 53.858 | 53.927 | 53.871 |
| age.sd_population (years) | 16.200778 | 16.108407–16.290199 | 16.452575 | 16.503517 | 16.475641 | 16.576877 | 16.490078 | 16.423805 |
| age.q10 (years) | 31 | 31–31 | 31 | 31 | 30 | 30 | 30 | 30 |
| age.q50 (years) | 54 | 54–54 | 54 | 54 | 54 | 54 | 54 | 54 |
| age.q90 (years) | 75 | 75–75 | 76 | 76 | 76 | 76 | 76 | 76 |

## female: marginal diagnostics

| Endpoint (unit) | Reference | Empirical band | A_18203 | A_18211 | A_18223 | B_18203 | B_18211 | B_18223 |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| female.mean (0/1) | 0.5 | 0.5–0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| female.sd_population (0/1) | 0.5 | 0.5–0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| female.q10 (0/1) | 0 | 0–0 | 0 | 0 | 0 | 0 | 0 | 0 |
| female.q50 (0/1) | 0 | 0–0 | 0 | 0 | 0 | 0 | 0 | 0 |
| female.q90 (0/1) | 1 | 1–1 | 1 | 1 | 1 | 1 | 1 | 1 |

## bmi: marginal diagnostics

| Endpoint (unit) | Reference | Empirical band | A_18203 | A_18211 | A_18223 | B_18203 | B_18211 | B_18223 |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| bmi.mean (kg/m²) | 28.659134 | 28.526947–28.798932 | 26.355136 | 26.344171 | 26.422549 | 26.300856 | 26.206382 | 26.405782 |
| bmi.sd_population (kg/m²) | 5.521096 | 5.321685–5.742809 | 3.979322 | 4.086661 | 4.115826 | 4.209103 | 4.223091 | 4.140351 |
| bmi.q10 (kg/m²) | 22.497028 | 22.285984–22.683145 | 21.405648 | 21.107605 | 21.153909 | 20.857448 | 20.749723 | 21.21548 |
| bmi.q50 (kg/m²) | 28.080808 | 27.9593–28.205587 | 26.312686 | 26.294354 | 26.458748 | 26.333579 | 26.206195 | 26.33563 |
| bmi.q90 (kg/m²) | 35.234505 | 34.944879–35.466667 | 31.414613 | 31.55505 | 31.668284 | 31.55411 | 31.660273 | 31.87805 |

## glucose: marginal diagnostics

| Endpoint (unit) | Reference | Empirical band | A_18203 | A_18211 | A_18223 | B_18203 | B_18211 | B_18223 |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| glucose.mean (mg/dL) | 91.034616 | 90.667237–91.34539 | 91.591016 | 91.554934 | 91.970159 | 91.721224 | 91.433902 | 91.50366 |
| glucose.sd_population (mg/dL) | 11.936805 | 11.65681–12.206605 | 9.17426 | 9.207678 | 9.010978 | 9.188423 | 8.981276 | 9.156225 |
| glucose.q10 (mg/dL) | 77 | 77–78 | 79.702009 | 80.003884 | 80.393994 | 80.23468 | 80.057267 | 79.497747 |
| glucose.q50 (mg/dL) | 90 | 90–91 | 91.746667 | 91.4248 | 92.057853 | 91.647652 | 91.600218 | 91.588463 |
| glucose.q90 (mg/dL) | 107 | 106–107 | 103.138654 | 103.385303 | 103.213795 | 103.487796 | 102.827261 | 103.45312 |

## hba1c: marginal diagnostics

| Endpoint (unit) | Reference | Empirical band | A_18203 | A_18211 | A_18223 | B_18203 | B_18211 | B_18223 |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| hba1c.mean (%) | 5.314143 | 5.300623–5.329148 | 5.391261 | 5.380852 | 5.388742 | 5.424118 | 5.412054 | 5.421233 |
| hba1c.sd_population (%) | 0.527375 | 0.48694–0.568771 | 0.335694 | 0.334912 | 0.33065 | 0.328221 | 0.338045 | 0.338285 |
| hba1c.q10 (%) | 4.8 | 4.8–4.8 | 4.955945 | 4.956146 | 4.968172 | 4.999244 | 4.974979 | 4.989821 |
| hba1c.q50 (%) | 5.3 | 5.3–5.3 | 5.395653 | 5.374422 | 5.392275 | 5.426752 | 5.423926 | 5.426014 |
| hba1c.q90 (%) | 5.8 | 5.8–5.9 | 5.830176 | 5.813366 | 5.823122 | 5.845614 | 5.835585 | 5.85081 |

## All scheduled labels and output identities

Every retained final label reuses the corresponding initial table and is not a new draw.

| Construction | Stage | Seed | Status | Output SHA-256 |
|---|---|---:|---|---|
| construction_1 | initial | 18203 | success | `58ac94563ad91b491bd8301bca9af674ccf6d0b1de054243235f5d25f6b52da5` |
| construction_1 | initial | 18211 | success | `481b010ca94e6983373f4ab7af7be77bb67edc3e3b5be1a8798f76743d3e437e` |
| construction_1 | initial | 18223 | success | `ac2c235e131637d33a589d8a3acc816615b32f6ed284478b61f9643979b52876` |
| construction_1 | final | 18203 | success | `58ac94563ad91b491bd8301bca9af674ccf6d0b1de054243235f5d25f6b52da5` |
| construction_1 | final | 18211 | success | `481b010ca94e6983373f4ab7af7be77bb67edc3e3b5be1a8798f76743d3e437e` |
| construction_1 | final | 18223 | success | `ac2c235e131637d33a589d8a3acc816615b32f6ed284478b61f9643979b52876` |
| construction_2 | initial | 18203 | success | `1a58c27b3715a8340ccf85f49ffb4d77693d0db709223816091d8e95fab07e0d` |
| construction_2 | initial | 18211 | success | `9f85148810cfbdfd3c5cdcdf6a31b74dd0fec900fb72dea7dc2b713b9e2c5629` |
| construction_2 | initial | 18223 | success | `8b821e6757de20f955adeba87de2abdcf7cc15949287bd8b237ef18b0313e917` |
| construction_2 | final | 18203 | success | `1a58c27b3715a8340ccf85f49ffb4d77693d0db709223816091d8e95fab07e0d` |
| construction_2 | final | 18211 | success | `9f85148810cfbdfd3c5cdcdf6a31b74dd0fec900fb72dea7dc2b713b9e2c5629` |
| construction_2 | final | 18223 | success | `8b821e6757de20f955adeba87de2abdcf7cc15949287bd8b237ef18b0313e917` |
