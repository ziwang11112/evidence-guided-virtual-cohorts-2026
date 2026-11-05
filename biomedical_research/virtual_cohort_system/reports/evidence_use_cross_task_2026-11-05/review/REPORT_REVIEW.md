# Final report consistency review

**Numerical and scientific content passes; three minor text corrections are requested below.** This was a read-only comparison against persisted, already-audited results, evidence-use records and the independent scientific interpretation. No numerical tests, generation, reference refits or figure rendering were repeated.

The reports agree with 24 successful physical attempts, 18 distinct final tables, 54 primary outputs, 513 declared outputs, 324 available reference comparisons and 189 unmatched reference diagnostics. All displayed English table entries, manuscript means/ranges and rounded Chinese point summaries agree with the audited values. The evidence totals also agree: 8 distinct studies, 22 author–paper uses, 132 unavailable source checks, 7 gateway queries, 1 download, 2 auxiliary requests, 1 failed HTTP attempt and 35.83 seconds of adapter wall time.

All 54 direction agreements are explicitly point comparisons. The reports preserve the TC reference interval crossing zero, exposed-development context, source-check unavailability and lack of demonstrated revision gain. They claim neither universal superiority nor new clinical confirmation, and retain the H03 dispersion trade-off and weak lipid residual dependence.

Static inspection of `report_results.py` confirms all three authors and all three final seeds in each relevant panel: 54 primary seed points and 36 dispersion seed points. HbA1c bands are labeled empirical cluster-resampling stability; lipid slope bands are labeled HC3 assumption-conditional sensitivity. Residual correlation and lipid SD bands are correctly absent. Reference bands are not acceptance margins, and seed ranges do not represent clinical replication or evidence/structure uncertainty. Root reported visual verification after the title-clipping fix; this review did not repeat it.

Requested corrections, without changing numbers:

1. `RESULTS_ZH.md:13–15`: make HbA1c units explicit. Add before the table: “HbA1c效应均以百分点计：年龄项为每10年，BMI项为每5 kg/m²；年龄项已控制性别、BMI和血糖。”
2. `RESULTS_ZH.md:29`: replace “当前有部分科学分析用途” with “当前可作为透明、假设依赖的情景数据，用于定性关联探索和分析流程检查”, retaining the current warning against quantitative cohort substitution.
3. `CROSS_TASK_RESULTS_INSERT_2026-11-05.md:11`: change `versus42.8466` to `versus 42.8466`.

Optional precision: replace “正向关系稳定” / “负向关系稳定” in Chinese table rows with “各模型/种子均为正向” / “各模型/种子均为负向”.

No reports, frozen artifacts or evaluated results were edited. Exact reviewed-file hashes and structured findings are recorded in `REPORT_REVIEW.json`.
