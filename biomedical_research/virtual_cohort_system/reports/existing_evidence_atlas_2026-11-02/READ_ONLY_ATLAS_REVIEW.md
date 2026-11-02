# Read-only atlas review

2 November 2026. This review recommends a descriptive re-presentation of existing frozen aggregate results. It authorizes no patient-row reads, new fitted models, new scientific endpoints, generator revision, target-based selection or new validation claim.

Project-relative paths below resolve under `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system`.

## Recommended complete scientific panel

Use all eight M17-B locked analyses, all three ENSANUT primary questions plus their explicitly required Q2-minus-Q3 companion, and all three CHNS primary estimands: **15 display rows, 90 generated points**, representing **14 primary quantities plus one predeclared companion contrast**. Show all six unique tables in each case. The scientific units remain three cases and six constructions, not 90 experiments. The 18 unique complete tables contain 31,920 fictional rows (6×320 + 6×2,000 + 6×3,000).

The inclusion rule is each frozen protocol's complete primary analysis panel; it does not select successful directions, close estimates or favorable seeds. M17-B's uncertain curvature and interaction must remain. ENSANUT's magnitude discrepancies and CHNS's weak BMI effects must remain. This is a retrospective descriptive atlas, not a new preregistered multi-case benchmark.

## Exact loader contracts

| Case | Aggregate input | Values and reference fields | Duplicate handling |
|---|---|---|---|
| M17-B | `work/m17b_whole_cohort_2026-10-31/custodian/results/evaluation.json` | `reference.endpoints[id].estimate/ci95_lo/ci95_hi/se_hc3`; `generated[*].endpoints[id].estimate`; identity `builder,stage,seed,sha256` | Select `stage=="final"`: b1/b2 × 17111/17112/17113. Six unique hashes. Initial and final hashes match within builder/seed. |
| ENSANUT | `work/autonomous_research_cycle2_2026-10-31/results_report/all_31_endpoints.csv` | Row key `endpoint`; `unit,reference,reference_band_lower,reference_band_upper`; six columns `A_18203,A_18211,A_18223,B_18203,B_18211,B_18223` | CSV already contains one column per unique target table. Do not expand it into initial/final copies. |
| CHNS F2 | `work/chns_admission_2026-11-01/f2/evaluation_results/REPORT.json` | `reference.estimands[id].coefficient/unit/interval.lower/interval.upper`; `slots[*].analysis.estimands[id].coefficient`; identity `construction,stage,seed,status` | Select `stage=="revised"`: C1/C2 × 1701/1702/1703. “Revised” is a retained stage, not changed science. Use `FINAL_INVENTORY.json` for paired generated-hash equality. |

Do not follow the JSON's participant-table `path` fields. Read only the aggregate objects above. Preserve existing numbers at full precision; round only labels. Fail visibly on missing IDs, unexpected counts, failed status or absent values rather than silently dropping points. Do not recalculate coefficients, uncertainty intervals, pooled effects, equivalence thresholds or statistical tests.

## IDs, scientific labels and numerical spot-checks

The reference values below are transcribed from existing aggregates, rounded for review. Loader output should use the original precision.

| Case / endpoint ID | Display label | Native unit | Reference point [displayed interval/band] |
|---|---|---|---|
| M17 `adjusted_bmi` | Age/sex-adjusted BMI–urate | mg/dL per 5 kg/m² | 0.272166 [0.181853, 0.362479] |
| M17 `adjusted_age` | BMI/sex-adjusted age–urate | mg/dL per decade | 0.148490 [0.069450, 0.227530] |
| M17 `adjusted_sex` | Adjusted female-minus-male urate | mg/dL | −1.281686 [−1.549753, −1.013619] |
| M17 `bmi_curvature` | BMI finite-difference curvature | mg/dL | −0.039142 [−0.126739, 0.048455] |
| M17 `bmi_sex_interaction` | Female-minus-male BMI slope | mg/dL per 5 kg/m² | −0.000385 [−0.198464, 0.197695] |
| M17 `male_bmi` | Male BMI–urate slope | mg/dL per 5 kg/m² | 0.272441 [0.107673, 0.437210] |
| M17 `female_bmi` | Female BMI–urate slope | mg/dL per 5 kg/m² | 0.272057 [0.162654, 0.381460] |
| M17 `reverse_urate` | Adjusted reverse urate–BMI slope | (kg/m²)/(mg/dL) | 1.527657 [0.847466, 2.207848] |
| ENS `Q1_age10` | BMI/glucose/sex-adjusted age–HbA1c | HbA1c pp per decade | 0.075132 [0.067124, 0.082185] |
| ENS `Q2_bmi5` | Age/sex-adjusted BMI–HbA1c | HbA1c pp per 5 kg/m² | 0.083643 [0.070373, 0.095214] |
| ENS `Q3_bmi5` | Additional glucose-adjusted BMI–HbA1c | HbA1c pp per 5 kg/m² | 0.056638 [0.043901, 0.068006] |
| ENS `Q2_minus_Q3_bmi5` | BMI coefficient change after glucose adjustment | HbA1c pp per 5 kg/m² | 0.027005 [0.021969, 0.032421] |
| CHNS `E1` | Age/sex-adjusted BMI–HbA1c | HbA1c pp per kg/m² | 0.054946 [0.045726, 0.064166] |
| CHNS `E2` | Age/sex-adjusted glucose–HbA1c | HbA1c pp per mmol/L | 0.402093 [0.371287, 0.432900] |
| CHNS `E3` | BMI/glucose/sex-adjusted age–HbA1c | HbA1c pp per year | 0.008107 [0.006387, 0.009827] |

M17's `bmi_curvature` already equals twice the quadratic coefficient: f(35)−2f(30)+f(25). Do not multiply it again. ENS Q2-minus-Q3 is a descriptive adjustment contrast, not causal mediation. CHNS's literal percent-unit fields mean HbA1c percentage-point changes, not relative percent change; changing the label to “pp” requires no rescaling. Keep CHNS per-year/per-BMI-unit scales and ENS per-decade/per-five-BMI-unit scales explicitly distinct, or document any later purely dimensional conversion separately.

## Uncertainty and plotting requirements

- **M17-B:** 95% normal HC3 intervals conditional on the selected unweighted 320-person age/sex quota sample and regression. These are neither NHANES survey-design intervals nor source/transport uncertainty. The curvature and interaction reference intervals span zero.
- **ENSANUT:** 2.5th–97.5th percentile empirical stability bands from 399 valid, frozen cluster-resampling attempts, recomputing the eight-stratum age/sex standard. These are not nominal confidence intervals, national survey inference or equivalence bounds. Reference N=6,931.
- **CHNS:** nominal 95% CR1/t intervals, 218 communities and 217 df, for unweighted OLS on 6,631 common complete cases. Not nationally representative inference. Generated estimates deliberately have no inferential interval.
- Display the six generated estimates as separate points, grouped by construction and identified by seed. They are conditional realizations, not independent clinical replications or calibrated structural uncertainty. Avoid treating their range as a confidence interval.
- Use case-separated panels and native units with an explicit zero line where relevant. Reference points and bands need separate legend labels by case; a generic “95% CI” label across all three would be wrong.
- No global “accuracy,” winner, percentage-sign-success score or interval-membership equivalence claim should be added. Close point signs do not show effect-size adequacy; reference uncertainty neither guarantees truth nor excuses substantial mismatch.

## Complete supporting evidence and method-version caveat

Keep the three cases' predeclared diagnostic outputs linked or fully tabulated: M17 `reference/generated.diagnostics`, all 31 ENS CSV rows, and CHNS `reference/slots[*].analysis.diagnostics` (25 marginal statistics plus Pearson/Spearman). Diagnostic inclusion follows existing plans, not post-result explanatory selection. Separate these from the primary plot rather than call all statistics independent scientific questions.

These cases used different source packets, source-context handling and controller versions. M17 used approximate checks on its specified cohort, ENS used a declared source-context bridge, and CHNS explicitly used `semantic_feedback_v1` plus separately approved task-population proxies. The atlas cannot retroactively turn M17/ENS into validations of the current CHNS implementation. Retain CHNS as the current-system case and label the earlier cases historical supporting evidence. All six constructors retained their initial scientific models after feedback; no plot should imply successful repair.

The boundary is **target-held-out scientific analysis with source-informed assumptions**, not entirely unknown biology. M17's complete `ENDPOINT_EXPOSURE.md` classifies supplied reverse slopes, demographic information, assumption-encoded age/sex dependence and uncalibrated curvature. ENS Q1/Q2 are source-indexed transfers; Q3 is not directly calibrated but depends on joint assumptions. CHNS's three relations are held out from feedback/target fitting but related source evidence exists. Do not erase those distinctions or claim discovery of novel biomedical mechanisms.

## Audited aggregate identities

- M17 evaluation JSON SHA256: `e7326021f3419a0a57360fbc4a4ccd4b5e78286122bb4021b77141a259417d16`.
- ENS all-31 CSV SHA256: `cd73426e9dd0d4c626c06f3dd391ce2b2976ca0faef562d3ae74eac5185e1cc2`.
- CHNS evaluation JSON SHA256: `55c307e230d1d59eded5d5af0dd15b0ca376d8a2b045cb00621c5b0e5409794f`.

Protocol bases: `docs/M17B_WHOLE_COHORT_PROTOCOL.md`; `work/autonomous_research_cycle2_2026-10-31/PROTOCOL_v2.md`; `work/chns_admission_2026-11-01/f2/analysis_plan.json`. This review wrote only this original Markdown artifact; all frozen results remain unchanged.
