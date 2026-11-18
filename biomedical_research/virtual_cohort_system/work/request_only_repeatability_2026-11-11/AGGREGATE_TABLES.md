# Complete repeatability aggregate tables

Every assigned constructor is retained. Group means below average available constructor means, not independent patients; availability is reported explicitly. Ranges span constructors. See the primary figures for individual simulation seeds. These are descriptive developmental comparisons with previously exposed sample references.

Final-table slots: 36 delivered, 0 failed, 0 unavailable / 36 planned. Model calls: 331. Known tariff cost: USD3.9851613; accounted cost: USD3.9851613.

## PNS: every constructor

| Constructor | BMI–SBP | BMI–DBP | Residual SBP–DBP | SBP SD | DBP SD | SBP < DBP fraction |
|---|---:|---:|---:|---:|---:|---:|
| PNS_BASE_R1 | 3.2927 | 2.5948 | 0.6109 | 20.6543 | 11.2822 | 0.0000 |
| PNS_BASE_R2 | 3.7368 | 2.9868 | 0.6160 | 16.2475 | 10.5048 | 0.0000 |
| PNS_BASE_R3 | 4.7221 | 2.7545 | 0.6691 | 16.6879 | 10.2083 | 0.0000 |
| PNS_WORKFLOW_R1 | 5.4061 | 3.6483 | 0.7834 | 18.6987 | 10.8648 | 0.0000 |
| PNS_WORKFLOW_R2 | 5.5969 | 3.7041 | 0.6160 | 18.6492 | 11.0658 | 0.0000 |
| PNS_WORKFLOW_R3 | 3.3622 | 2.4244 | 0.6765 | 16.8372 | 11.2052 | 0.0000 |
| Existing sample reference | 3.5240 | 2.2599 | 0.7172 | 18.1916 | 11.0941 | 0.0000 |

Units in column order: mmHg per 5 kg/m^2; mmHg per 5 kg/m^2; 1; mmHg; mmHg; 1.

Blood-pressure SD uses the saved population-SD convention; lipid SD uses the saved sample-SD convention. Fractions are proportions, not percentages. A reference zero is not asserted unless present in the pinned reference.

## lipids: every constructor

| Constructor | BMI–TC | BMI–HDL | Residual TC–HDL | TC SD | HDL SD | HDL > TC fraction |
|---|---:|---:|---:|---:|---:|---:|
| LIPID_BASE_R1 | 8.8287 | -1.1546 | 0.3308 | 37.8013 | 11.9592 | 0.0000 |
| LIPID_BASE_R2 | 14.6148 | -1.4896 | 0.3590 | 36.6868 | 13.1331 | 0.0000 |
| LIPID_BASE_R3 | 12.3831 | -2.3124 | 0.4233 | 35.7716 | 11.9587 | 0.0000 |
| LIPID_WORKFLOW_R1 | 9.9313 | -1.3482 | 0.1456 | 32.9360 | 11.3752 | 0.0001 |
| LIPID_WORKFLOW_R2 | 13.3370 | -0.0116 | 0.3560 | 42.1900 | 13.1809 | 0.0000 |
| LIPID_WORKFLOW_R3 | 8.8104 | -1.4142 | 0.3193 | 39.2089 | 12.2797 | 0.0000 |
| Existing sample reference | 5.6831 | -4.6230 | 0.5121 | 42.8466 | 20.1756 | unavailable |

Units in column order: mg/dL per 5 kg/m^2; mg/dL per 5 kg/m^2; 1; mg/dL; mg/dL; 1.

Blood-pressure SD uses the saved population-SD convention; lipid SD uses the saved sample-SD convention. Fractions are proportions, not percentages. A reference zero is not asserted unless present in the pinned reference.

## Descriptive policy profiles

| Case | Analysis | Policy | Available authors | Mean | Author range | Reference | Mean absolute difference |
|---|---|---|---:|---:|---|---:|---:|
| PNS | BMI–SBP | ordinary | 3/3 | 3.9172 | 3.2927–4.7221 | 3.5240 | 0.5474 |
| PNS | BMI–SBP | workflow | 3/3 | 4.7884 | 3.3622–5.5969 | 3.5240 | 1.3722 |
| PNS | BMI–DBP | ordinary | 3/3 | 2.7787 | 2.5948–2.9868 | 2.2599 | 0.5187 |
| PNS | BMI–DBP | workflow | 3/3 | 3.2589 | 2.4244–3.7041 | 2.2599 | 0.9990 |
| PNS | Residual SBP–DBP | ordinary | 3/3 | 0.6320 | 0.6109–0.6691 | 0.7172 | 0.0852 |
| PNS | Residual SBP–DBP | workflow | 3/3 | 0.6920 | 0.6160–0.7834 | 0.7172 | 0.0694 |
| PNS | SBP SD | ordinary | 3/3 | 17.8632 | 16.2475–20.6543 | 18.1916 | 1.9702 |
| PNS | SBP SD | workflow | 3/3 | 18.0617 | 16.8372–18.6987 | 18.1916 | 0.7731 |
| PNS | DBP SD | ordinary | 3/3 | 10.6651 | 10.2083–11.2822 | 11.0941 | 0.5544 |
| PNS | DBP SD | workflow | 3/3 | 11.0453 | 10.8648–11.2052 | 11.0941 | 0.1229 |
| PNS | SBP < DBP fraction | ordinary | 3/3 | 0.0000 | 0.0000–0.0000 | 0.0000 | 0.0000 |
| PNS | SBP < DBP fraction | workflow | 3/3 | 0.0000 | 0.0000–0.0000 | 0.0000 | 0.0000 |
| lipids | BMI–TC | ordinary | 3/3 | 11.9422 | 8.8287–14.6148 | 5.6831 | 6.2591 |
| lipids | BMI–TC | workflow | 3/3 | 10.6929 | 8.8104–13.3370 | 5.6831 | 5.0098 |
| lipids | BMI–HDL | ordinary | 3/3 | -1.6522 | -2.3124–-1.1546 | -4.6230 | 2.9708 |
| lipids | BMI–HDL | workflow | 3/3 | -0.9247 | -1.4142–-0.0116 | -4.6230 | 3.6983 |
| lipids | Residual TC–HDL | ordinary | 3/3 | 0.3710 | 0.3308–0.4233 | 0.5121 | 0.1410 |
| lipids | Residual TC–HDL | workflow | 3/3 | 0.2737 | 0.1456–0.3560 | 0.5121 | 0.2384 |
| lipids | TC SD | ordinary | 3/3 | 36.7532 | 35.7716–37.8013 | 42.8466 | 6.0934 |
| lipids | TC SD | workflow | 3/3 | 38.1116 | 32.9360–42.1900 | 42.8466 | 4.7349 |
| lipids | HDL SD | ordinary | 3/3 | 12.3503 | 11.9587–13.1331 | 20.1756 | 7.8252 |
| lipids | HDL SD | workflow | 3/3 | 12.2786 | 11.3752–13.1809 | 20.1756 | 7.8970 |
| lipids | HDL > TC fraction | ordinary | 3/3 | 0.0000 | 0.0000–0.0000 | unavailable | unavailable |
| lipids | HDL > TC fraction | workflow | 3/3 | 0.0000 | 0.0000–0.0001 | unavailable | unavailable |

No cross-analysis composite score, post hoc equivalence tolerance or pooled clinical success rate is defined. Direction agreement alone does not establish analytical usefulness.

## Construction and resources

| Constructor | Terminal status | Selected | Calls | Queries | Downloads | Candidates | Trials | Known USD | Unknown calls |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| PNS_BASE_R1 | finalized | v001 | 21 | 8 | 3 | 1 | 1 | 0.2527286 | 0 |
| PNS_WORKFLOW_R1 | finalized | v001 | 32 | 13 | 4 | 1 | 1 | 0.4122633 | 0 |
| LIPID_WORKFLOW_R1 | finalized | v001 | 26 | 6 | 5 | 1 | 1 | 0.2838656 | 0 |
| LIPID_BASE_R1 | finalized | v001 | 23 | 8 | 3 | 1 | 1 | 0.2011518 | 0 |
| LIPID_BASE_R2 | finalized | v001 | 17 | 5 | 2 | 1 | 1 | 0.1530005 | 0 |
| LIPID_WORKFLOW_R2 | finalized | v001 | 30 | 8 | 4 | 1 | 1 | 0.4337903 | 0 |
| PNS_WORKFLOW_R2 | finalized | v001 | 34 | 16 | 8 | 1 | 1 | 0.4936989 | 0 |
| PNS_BASE_R2 | finalized | v001 | 27 | 12 | 4 | 1 | 1 | 0.2980009 | 0 |
| PNS_WORKFLOW_R3 | finalized | v001 | 39 | 15 | 8 | 1 | 1 | 0.5113226 | 0 |
| PNS_BASE_R3 | finalized | v001 | 28 | 15 | 5 | 1 | 1 | 0.3368245 | 0 |
| LIPID_BASE_R3 | finalized | v001 | 24 | 10 | 2 | 1 | 1 | 0.2353693 | 0 |
| LIPID_WORKFLOW_R3 | finalized | v001 | 30 | 11 | 6 | 1 | 1 | 0.3731450 | 0 |

Candidate/seed counts do not measure independent clinical evidence. A v001 selection is retention of the first submitted program; trial success is not scientific source or target validation.
