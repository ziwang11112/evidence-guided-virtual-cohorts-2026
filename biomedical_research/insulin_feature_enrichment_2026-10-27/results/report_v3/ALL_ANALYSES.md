# Prespecified scientific-analysis comparison

All effects below are on the natural-log insulin scale. Ratios and their reference survey intervals are provided in the accompanying aggregate CSV. No equivalence margin or binary method-success threshold was specified.

The reference interval reflects the survey analysis. Generated ranges describe repeated draws from a fixed Agent-authored generator; they do not include all model, source, or transport uncertainty. Matching sign or interval state alone is not proof of equal effects.

The generated_median_ratio CSV field is exp(median(log-effect)), not the arithmetic median of the exponentiated draws. Endpoint evidence-role annotations were finalized from the frozen provenance after evaluation and do not change the numerical analyses.

## initial_v1

| Question | Real estimate [95% survey interval] | Generated median [draw min, max] | Real interval state | Generated positive / unresolved / negative draws |
|---|---|---|---|---|
| Overall BMI association (per 5 kg/m²) | 0.296 [0.263, 0.329] | 0.208 [0.183, 0.249] | positive | 20 / 0 / 0 |
| Adjusted BMI association (per 5 kg/m²) | 0.297 [0.265, 0.330] | 0.207 [0.184, 0.250] | positive | 20 / 0 / 0 |
| Adjusted age association (per 10 years) | 0.010 [-0.020, 0.041] | -0.004 [-0.022, 0.021] | interval includes zero | 1 / 19 / 0 |
| Adjusted female–male contrast | -0.065 [-0.188, 0.058] | 0.017 [-0.059, 0.090] | interval includes zero | 0 / 20 / 0 |
| Upper–lower BMI slope contrast | -0.123 [-0.174, -0.072] | 0.003 [-0.039, 0.052] | negative | 0 / 20 / 0 |
| Female–male BMI slope difference | -0.109 [-0.176, -0.042] | 0.006 [-0.045, 0.058] | negative | 1 / 19 / 0 |
| Male BMI slope (per 5 kg/m²) | 0.370 [0.306, 0.433] | 0.201 [0.152, 0.256] | positive | 20 / 0 / 0 |
| Female BMI slope (per 5 kg/m²) | 0.260 [0.228, 0.293] | 0.210 [0.178, 0.247] | positive | 20 / 0 / 0 |

## Evidence roles

Labels below were finalized in postrun review from the frozen source/model provenance. No endpoint was removed or rescored. Target answers were withheld, but some synthetic patterns are already encoded from the Agent-selected external evidence or explicit assumptions.

| Question | Evidence/assumption role |
|---|---|
| Overall BMI association (per 5 kg/m²) | External-evidence consistency and target magnitude transport |
| Adjusted BMI association (per 5 kg/m²) | Transport of evidence-informed common BMI slope |
| Adjusted age association (per 10 years) | Transport of assumed age interpolation (A1/A2) |
| Adjusted female–male contrast | Challenge to zero direct sex-effect assumption (A4) |
| Upper–lower BMI slope contrast | Challenge to linear BMI assumption (A3) |
| Female–male BMI slope difference | Challenge to absent BMI-by-sex interaction (A4) |
| Male BMI slope (per 5 kg/m²) | Male subgroup transport under common slope |
| Female BMI slope (per 5 kg/m²) | Female subgroup transport under common slope |

## Interpretation limits

- Reproduction of relationships already encoded from Agent-selected external evidence is consistency, not independent biological discovery. The coordinator supplied no numerical biological relation.
- Reserved target-specific analyses test transfer under a specified model. Explicit structural assumptions may determine some synthetic patterns.
- A reference interval overlapping zero does not establish absence of association. A synthetic-only confident result is not new empirical confirmation.
- Same people and repeated stochastic generation draws are not additional independent patients or studies.
- Report failures and mismatches alongside preserved conclusions; do not rank models by a chosen favourable endpoint.
