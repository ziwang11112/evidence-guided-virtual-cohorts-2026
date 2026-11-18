# Independent numerical audit and scientific-use interpretation

PASS: 5846 checks, 4690 numerical comparisons, maximum absolute difference 8.52e-13. All seven dataset slots and189 contrast slots agree with independent CSV parsing and statsmodels QR fits. All checked input hashes are unchanged.

The real reference has1189 BMI,400 TC and405 HDL observations after the fixed selection; nine records are excluded by age<=18. All six virtual tables have1226 complete observations per outcome. The reference is developmental and uncertain; it is not a known population truth.

| Trait / contrast | Real estimate [95% model CI] | A1 mean [seed min,max] | A2 mean [seed min,max] |
|---|---:|---:|---:|
| bmi / rural_minus_pastoralist | 0.086 [-0.061,0.232] | 0.047 [0.031,0.072] | 0.063 [-0.052,0.152] |
| bmi / urban_minus_pastoralist | 0.666 [0.484,0.848] | 0.746 [0.673,0.817] | 0.779 [0.684,0.844] |
| bmi / urban_minus_rural | 0.580 [0.434,0.726] | 0.699 [0.600,0.786] | 0.715 [0.657,0.753] |
| total_cholesterol / rural_minus_pastoralist | 0.222 [-0.009,0.452] | 0.032 [0.010,0.045] | 0.026 [-0.021,0.057] |
| total_cholesterol / urban_minus_pastoralist | 0.475 [0.104,0.846] | 0.451 [0.410,0.500] | 0.496 [0.426,0.558] |
| total_cholesterol / urban_minus_rural | 0.253 [-0.077,0.584] | 0.420 [0.366,0.460] | 0.470 [0.447,0.501] |
| hdl_cholesterol / rural_minus_pastoralist | 0.220 [-0.003,0.443] | -0.053 [-0.127,0.001] | -0.062 [-0.099,-0.022] |
| hdl_cholesterol / urban_minus_pastoralist | 0.087 [-0.271,0.444] | -0.007 [-0.127,0.118] | -0.031 [-0.075,0.020] |
| hdl_cholesterol / urban_minus_rural | -0.133 [-0.452,0.186] | 0.046 [-0.014,0.152] | 0.031 [0.024,0.042] |

Effects above use each dataset/trait's own pooled sample SD. Real intervals are classical OLS model intervals, whereas virtual ranges show three draws from one fixed law; these are different quantities. All raw-unit coefficients and189 pooled/sex-specific results are retained in the JSON.

## Interpretation

- The urban BMI and TC increases are preserved as broad scientific patterns by both constructions. This is consistent with information explicitly present in the source; it is useful reconstruction, not an unseen discovery or independent transport demonstration.
- Agreement is contrast-specific. In particular the generated urban–rural TC contrast is larger on the standardized scale than the present real-reference estimate, while the rural–pastoralist TC contrast is smaller. Do not describe all three lifestyle contrasts as equally recovered.
- HDL changes are weak and seed-sensitive in the virtual cohorts. The real point estimates differ from the virtual ones, but the model intervals must remain visible; nonsignificance does not establish zero or equivalence.
- A1 seed64001 selects the sex-specific HDL branch (nominal LRT p=0.0245688); none of the three real-reference interaction tests select it. All other virtual interaction tests are above0.05. This is one observed analysis-path discrepancy, not proof of a new subgroup mechanism.
- Standardized matching can conceal raw-unit scale differences. Use the retained raw coefficients and scale diagnostics alongside this table. Six complete1226-row synthetic tables do not reproduce the real lipid measurement missingness or supply new clinical evidence.
- Both authors finalized their first candidate after one generated-only trial. There is no observed revision improvement in this unit. The code/source audit found valid finite-moment positive-component laws, while most joint relationships and several lifestyle magnitudes still depended on explicit assumptions.

The minor source-arithmetic attribution correction is documented separately in CONSTRUCTION_CODE_REVIEW_CORRECTION.json: the approximately0.000545kg/m2 discrepancy belongs to A1; A2 differs from its stated exact division by about−0.00000489kg/m2. Neither candidate nor the original frozen audit was edited.
