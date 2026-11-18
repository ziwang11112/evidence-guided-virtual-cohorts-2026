# Independent numerical recomputation

Status: **pass**. 649 checks; 0 failures.

All 25 bound tables were parsed independently under the fixed common-case rules. 
The Schur complement of the centered covariance matrix supplies age/sex-adjusted correlations; 
the production OLS residualization function was neither imported nor called.

25/25 tables computed; 75 planned pair slots retained. 
150 r/r² values were compared with both JSON and CSV. Maximum absolute difference: 1.33e-15.

All bound hashes remained unchanged. No API, new generation, new target fit, or participant-row export occurred.

| Table | n | BMI–TC r | BMI–HDL r | TC–HDL r |
|---|---:|---:|---:|---:|
| REAL | 396 | 0.070079 | -0.116594 | 0.498273 |
| LIPID_BASE_R1_54001 | 2972 | 0.165114 | -0.099360 | 0.304459 |
| LIPID_BASE_R1_54003 | 2969 | 0.220268 | -0.047969 | 0.327252 |
| LIPID_BASE_R1_54007 | 2961 | 0.169241 | -0.078830 | 0.301961 |
| LIPID_BASE_R2_54001 | 3000 | 0.300961 | -0.105360 | 0.294663 |
| LIPID_BASE_R2_54003 | 3000 | 0.344405 | -0.060234 | 0.346645 |
| LIPID_BASE_R2_54007 | 3000 | 0.296467 | -0.100281 | 0.294100 |
| LIPID_BASE_R3_54001 | 3000 | 0.245742 | -0.179448 | 0.356573 |
| LIPID_BASE_R3_54003 | 3000 | 0.288163 | -0.126789 | 0.371440 |
| LIPID_BASE_R3_54007 | 3000 | 0.278202 | -0.136250 | 0.361972 |
| LIPID_WORKFLOW_R1_54001 | 3000 | 0.198057 | -0.114511 | 0.122597 |
| LIPID_WORKFLOW_R1_54003 | 3000 | 0.224595 | -0.056355 | 0.116943 |
| LIPID_WORKFLOW_R1_54007 | 3000 | 0.261883 | -0.093919 | 0.123840 |
| LIPID_WORKFLOW_R2_54001 | 3000 | 0.233592 | 0.001770 | 0.334111 |
| LIPID_WORKFLOW_R2_54003 | 3000 | 0.228566 | -0.007938 | 0.360438 |
| LIPID_WORKFLOW_R2_54007 | 3000 | 0.248373 | 0.004756 | 0.342962 |
| LIPID_WORKFLOW_R3_54001 | 3000 | 0.210018 | -0.109922 | 0.303353 |
| LIPID_WORKFLOW_R3_54003 | 3000 | 0.185095 | -0.116987 | 0.273608 |
| LIPID_WORKFLOW_R3_54007 | 3000 | 0.251777 | -0.099805 | 0.282445 |
| R04_GENERIC_54001 | 3000 | 0.292306 | -0.105360 | 0.297039 |
| R04_GENERIC_54003 | 3000 | 0.334343 | -0.060234 | 0.348802 |
| R04_GENERIC_54007 | 3000 | 0.287117 | -0.100281 | 0.296419 |
| R04_STRUCTURED_54001 | 3000 | 0.273564 | -0.101717 | 0.311434 |
| R04_STRUCTURED_54003 | 3000 | 0.321210 | -0.072527 | 0.341181 |
| R04_STRUCTURED_54007 | 3000 | 0.272957 | -0.095380 | 0.294492 |

These are developmental, method-guided partial reanalysis results, not original-code reproduction, 
equivalence certification, or independent population confirmation. Seed differences are conditional simulation variation.
