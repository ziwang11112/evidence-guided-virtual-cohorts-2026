# Post hoc check of HDL and total cholesterol in the Q5 virtual cohorts

Each lipid construction sampled total cholesterol and HDL cholesterol in mmol/L. We compared both numbers within each previously generated row and counted instances in which HDL exceeded total cholesterol. Both concentrations were finite and positive in every row. Applying the common conversion factor of 38.67 to both columns gives the same ordering in mg/dL. The audit used the stored outputs corresponding to each frozen execution receipt.

| Generator | Seed 9101 | Seed 9102 | Seed 9103 | HDL > total / all pairs |
| --- | ---: | ---: | ---: | ---: |
| L01 | 5 | 12 | 15 | 32 / 9,000 |
| L02 | 2 | 4 | 1 | 7 / 9,000 |
| L03 | 12 | 10 | 8 | 30 / 9,000 |
| Total | 19 | 26 | 24 | 69 / 27,000 (0.256%) |

Each seed supplied 3,000 paired values per generator. The pooled frequency describes these nine synthetic deliveries. The Q5 protocol prespecified scientific associations and dispersion. This later check addresses a different use of the table, whether its paired measurements imply a physically plausible non-HDL concentration. The three generators sample separate positive margins linked by a copula. That construction permits HDL to exceed the total. The published aggregate association results alone cannot determine how much those individual pairs contributed to the discrepancy in residual correlation.

[Q5 protocol](../reports/evidence_use_cross_task_2026-11-05/PROTOCOL.json) · [Q5 results](../reports/evidence_use_cross_task_2026-11-05/RESULTS.md) · [L01 code](../reports/evidence_use_cross_task_2026-11-05/authors/L01/candidates/initial/generator.py) · [L02 code](../reports/evidence_use_cross_task_2026-11-05/authors/L02/candidates/initial/generator.py) · [L03 code](../reports/evidence_use_cross_task_2026-11-05/authors/L03/candidates/initial/generator.py).
