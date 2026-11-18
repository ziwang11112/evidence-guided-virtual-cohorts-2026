# Independent review of derived highlights

9 November 2026. **PASS for arithmetic and the corrected interpretation.** No unresolved numerical discrepancy was found.

## Scope

Reviewed `derive_highlights.py` and `DERIVED_HIGHLIGHTS.json` without executing the derivation script or changing either file. Independently recalculated descriptive arithmetic from these frozen aggregate inputs:

- `work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json`
- `../obesity_temporal_prediction_2026-10-25/results/compact_comparison.csv`
- `../obesity_temporal_prediction_2026-10-25/results/metrics.csv`
- `../obesity_temporal_prediction_2026-10-25/results/ordinary_summary.csv`

Temporal interpretation was checked against the frozen `PROTOCOL.md`, `RESULTS.md` and `NUMERICAL_AUDIT.md`. Only aggregate estimates and authored reports were opened. No patient/generated rows, predictions, models or target-input files were opened; no generator, model fit, clinical analysis, new experiment or broad test suite was run. This checks the synthesis arithmetic, not the original biomedical estimators.

## Verified arithmetic and denominators

A separate Decimal-based calculation checked 160 numerical fields, ratios and counts. Maximum absolute difference was **3.16e-16**; zero mismatches exceeded 1e-12. Both source hashes recorded in the derived JSON match the current frozen aggregate files.

All six main endpoint rows contain five complete Agent constructors per information arm and one complete fixed statistical comparator, with three available seed discrepancies per construction. The script first averages each constructor's absolute sample-reference discrepancies, then weights the five constructors equally. It does not take the absolute discrepancy of the pooled mean effect. Here “MAD” means **mean absolute discrepancy**, not median absolute deviation.

All ratios use the stated comparator as denominator and the form `1 - Agent/comparator`; the E1/E0 ratio uses E0 as denominator. All author counts and constructor-mean minima/maxima match the frozen records. Verified tallies are:

| Descriptive comparison | Lower-discrepancy endpoint count |
|---|---:|
| Agent E1 versus Agent E0 | 5/6 |
| Agent E0 arm versus its fixed statistical specification | 6/6 |
| Agent E1 arm versus its fixed statistical specification | 4/6 |

Negative “reductions” must retain their adverse meaning. E1 CHNS BMI discrepancy is **54.85% higher** than E0. E1 Agent glucose discrepancy is **100.30% higher** than its fixed comparator; E1 ENSANUT glucose-adjusted BMI discrepancy is **223.04% higher**. These are descriptive ratios, not probabilities, accuracy gains, equivalence or clinical significance.

## Temporal result interpretation

All six temporal compact rows are copied exactly. Their metric values, real-reference deltas, ordinary-median AUC deltas and counts of ordinary draws with lower AUC were independently reconciled to aggregate metric rows. There are 100 ordinary runs per model family.

Primary logistic AUC is real128 **0.734936**, A1 **0.712130**, A2 **0.726871**, ordinary median **0.717394**. A1/A2 are respectively 0.022806/0.008065 below real training and 0.005264 below/0.009477 above the ordinary median. They exceed 38/67 ordinary AUCs. Histogram-boosting counts are 43/61. These counts are not inferential win probabilities.

The source-information description is correct: both authors and the ordinary generator received outcome-by-sex-conditioned counts, means, SDs, seven quantiles and regularized rank-correlation matrices computed from the **same 128 real development records**. It was not literature-only synthesis. Development was NHANES 2015–2016; locked evaluation used **1,811 later 2017–2018 participants** from the same survey program. The endpoint classifies **current measured HbA1c >=5.7%** in adults with BMI >=30; it is not prediction of a future disease event. The later-cycle evaluation supports temporal transport of predictive information in this pilot, not a new clinical-institution family, replacement of outcome collection or a stable Agent-specific benefit. Both Agent primary AUC/Brier results are worse than the same-budget real comparator, and the ordinary-generator comparison is mixed.

## Interpretation correction observed

At first inspection, the statement that E0 has “zero unspecified cross-variable correlations” was too broad because mixing source components can induce aggregate dependence. The root corrected both files during review to:

> The E0 statistical specification completes unprovided within-source dependence by independence; mixing source components can still induce dependence.

The corrected sentence has the appropriate scope. This review did not reopen generator specifications under the aggregate-only assignment. The remaining stated qualifications are sound: different authors across information arms; five Agent laws versus one fixed statistical law per arm; no superiority over statistical generation in general; no pooling across endpoint units, old versions, cohorts or repeated seeds.

