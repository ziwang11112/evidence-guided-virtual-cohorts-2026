# Claude PDF: ENSANUT arithmetic and scientific interpretation

**Verdict:** the direct-value calculations are broadly reproducible, but the claimed causal attribution of error to population transfer or residual dependence is unsupported. The approximate 40/60 split is a scale-dependent descriptive identity, not a mechanism decomposition.

Scope: extracted PDF pp. 4–6, with pp. 11–13 inspected for proposed tests. Read pinned `7f4b38c0c0dfa8da4bbd8df3d5ee754399600562` aggregate endpoints/source checks, admitted Pani/Jansen summaries, conversion rules, and both initial generator texts. Only aggregate arithmetic was executed. No participant/generated rows, generator execution, new fitting or tests. Original source papers were not independently re-reviewed.

## Direct-source comparison

The admitted values give age `0.010 × 10 = 0.100000`; BMI `0.13 × 0.09148 × 5 = 0.059462`; glucose `2.29 × 0.09148 / 18 × 10 = 0.116382889`. These are HbA1c percentage-point effects per stated increment. The adjustment-variable lists match Q1, Q2 and secondary glucose respectively. [Pani:5–7](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31/evidence/packet/sources/PANI2008/source_summary.md#L5), [Jansen:17](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31/evidence/packet/sources/JANSEN2013/source_summary.md#L17).

Claude's “midpoints” reproduce as **midranges, `(minimum + maximum)/2`**, not three-seed means or individual outputs:

| Endpoint | Direct source | A midrange | B midrange | Finite reference |
|---|---:|---:|---:|---:|
| Q1 age /10 years | 0.10000000 | 0.09758705 | 0.10017250 | 0.07513236 |
| Q2 BMI /5 kg/m² | 0.05946200 | 0.05885280 | 0.05453863 | 0.08364284 |
| Glucose /10 mg/dL | 0.11638289 | 0.11922454 | 0.11366211 | 0.11419981 |
| Q3 BMI additionally adjusting glucose | Unreported | 0.02425283 | 0.02220998 | 0.05663754 |

All six direct-endpoint midrange/source differences are below 0.005, as claimed. However, **+33.10%/−28.91% describe direct-source/reference differences**. Generated Q1 errors are +29.89%/+33.33%; generated Q2 errors are −29.64%/−34.80%. Q3 midranges reach 42.82%/39.21% of reference; all six draws instead span **28.79%–49.64%**. [Exact aggregate CSV:2–6](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31/results_report/all_31_endpoints.csv#L2).

“Generated did not improve on citation” is not uniformly true descriptively: secondary-glucose B midrange has absolute reference discrepancy 0.000538, versus 0.002183 for direct citation. This isolated observation establishes neither superiority nor equivalence.

## Q3 decomposition: ratio, log and raw scales

Let `r = Q3/Q2`; reference `r = 0.67713550`. Using the above midranges:

`log(G3/T3) = log(G2/T2) + log[(G3/G2)/(T3/T2)]`.

| Construction | G3/T3 | G2/T2 | Attenuation-ratio factor | Log components | Log shares: Q2 / attenuation |
|---|---:|---:|---:|---|---|
| A | 0.428211 | 0.703620 | 0.608583 | −0.848139 = −0.351516 −0.496622 | 41.45% / 58.55% |
| B | 0.392142 | 0.652042 | 0.601407 | −0.936130 = −0.427646 −0.508484 | 45.68% / 54.32% |

Thus 40/60 is a reasonable rough description for A, less accurate for B. On the original coefficient scale:

`T3−G3 = (T2−G2) + [(G2−G3)−(T2−T3)]`.

- A: `0.03238471 = 0.02479004 + 0.00759467`: shares **76.55%/23.45%**.
- B: `0.03442755 = 0.02910420 + 0.00532335`: shares **84.54%/15.46%**.

Both identities are correct. Neither partitions causal responsibility. Separate endpoint midranges need not describe one actual draw; midrange is not additive, so B's independently summarized `Q2−Q3` midpoint must not replace `mid(Q2)−mid(Q3)`. The original report already states most raw Q3 shortfall is present in Q2 and rejects causal interpretation. [Report:53](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31/results_report/REPORT.md#L53).

## Attribution and operator limits

`G−T = (S−T) + (G−S)` is bookkeeping. Even arithmetically, A's secondary-glucose `G−S` accounts for 56.55% of its raw `G−T`, so “almost all” is not uniform. Calling `S−T` population-transfer error conflates population composition, selection, weighting, measurement, source-estimate uncertainty and model applicability. Calling the attenuation term the effect of residual correlation 0.30 likewise lacks an intervention or controlled contrast. That assumption influences the construction, but other parameters and truncation also matter. [B generator:66–111](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31/b2/candidates/initial/generator.py#L66).

Matching adjustment names is not full estimator equivalence. Pani uses survey weighting; the target is an age/sex-standardized finite reference. Source supports, selection and assays differ. All source checks are explicitly approximate. For example, A's source-context BMI projection is 0.01053256 versus 0.0118924, despite its target-draw Q2 midrange nearly matching direct citation. [Source checks:11–13](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31/results_report/all_40_source_checks.csv#L11), [target operators:27](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/7f4b38c0c0dfa8da4bbd8df3d5ee754399600562/biomedical_research/virtual_cohort_system/reports/autonomous_research_cycle2_2026-10-31/results_report/REPORT.md#L27).

Q3 is the principal prespecified conditional coefficient not directly supplied for calibration, **not the only analysis involving a joint distribution**. Q1/Q2, coefficient change and residual diagnostics also depend on joint structure. Failure of this Q3 construction does not establish universal failure of reusable virtual data.

## Implications for proposed tests

Retain direct-citation diagnostics where estimands are comparable, explicit information categories, same-information alternatives for advantage claims, and separate uncertainty sources. Do not call a reference half-split a proven noise lower bound, a target-fitted copula an upper bound, or a million-row draw an exact infinite-sample value. Each requires qualification and budget accounting. A no-evidence LLM arm does not isolate memorization. Arbitrary four-way causal error decomposition is not identified by these aggregates. Useful whole-cohort data remain the objective; superiority over direct citation is a distinct claim, not a prerequisite for every feasibility study.
