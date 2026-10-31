# Independent C3 source-only audit

Both frozen structures and all 20 source checks are retained. Each source table contains 6,000 fictional rows. No target evaluation, refit, new draw, source search or post-replay selection was performed.

## Linear

Result: **tradeoff/incomplete compatibility**. Trial 26 was selected using seed 19101 only. Strict loss improvement at the fitting seed and both unused seeds: True. All selected unused-seed numeric criteria pass: False.

| Seed | Baseline loss | Selected loss | Selected minus baseline |
|---|---:|---:|---:|
| 19101 | 0.6700126606 | 0.370687294 | -0.2993253666 |
| 19111 | 0.6694282055 | 0.3600103662 | -0.3094178392 |
| 19123 | 0.6991423883 | 0.4143094937 | -0.2848328946 |

Selected numeric failures on unused seeds: 3. Exact paired IDs and covariates preserved: True. Full raw source discrepancies and changes are retained in the CSV files.

| Seed | Failed check | Value | Signed source difference | Required interval |
|---|---|---:|---:|---|
| 19111 | P_NHANES_hba1c_age_ge70_mean | 5.61660893 | 0.106608928 | difference: [-0.1, 0.1] |
| 19123 | P_NHANES_age_slope | 0.00799097657 | -0.00200902343 | value: [0.008, 0.012] |
| 19123 | P_NHANES_hba1c_age_ge70_mean | 5.61675346 | 0.106753461 | difference: [-0.1, 0.1] |

Execution: 37/40 trials, 82/88 reserved context executions, 0 infeasible trials and 0 failed executions. Stop reason: minimum_step. Trial cap hit: False. Selected parameter-bound hits: none.
Recorded session elapsed: 191.766000 s; sum of execution elapsed times: 61.613000 s. The 2460 s usage counter is timeout-cap accounting, not measured CPU consumption.

## Alternative

Result: **no robust numerical improvement**. Trial 26 was selected using seed 19101 only. Strict loss improvement at the fitting seed and both unused seeds: False. All selected unused-seed numeric criteria pass: False.

| Seed | Baseline loss | Selected loss | Selected minus baseline |
|---|---:|---:|---:|
| 19101 | 0.2303849445 | 0.2156294056 | -0.01475553889 |
| 19111 | 0.1734611107 | 0.2050375224 | 0.03157641166 |
| 19123 | 0.2366165568 | 0.2599527483 | 0.02333619147 |

Selected numeric failures on unused seeds: 2. Exact paired IDs and covariates preserved: True. Full raw source discrepancies and changes are retained in the CSV files.

| Seed | Failed check | Value | Signed source difference | Required interval |
|---|---|---:|---:|---|
| 19111 | P_NHANES_age_slope | 0.00738997685 | -0.00261002315 | value: [0.008, 0.012] |
| 19123 | P_NHANES_age_slope | 0.00726473779 | -0.00273526221 | value: [0.008, 0.012] |

Execution: 37/40 trials, 82/88 reserved context executions, 0 infeasible trials and 0 failed executions. Stop reason: minimum_step. Trial cap hit: False. Selected parameter-bound hits: none.
Recorded session elapsed: 192.203000 s; sum of execution elapsed times: 59.610000 s. The 2460 s usage counter is timeout-cap accounting, not measured CPU consumption.

## Descriptive structural comparison

The alternative does not meet the complete authored preference rule: lower loss on both unused seeds, no larger worst Pani age-profile error, and no newly failed numeric compatibility requirement. Both structures remain reported; neither is selected or advanced to a target.

The fixed-denominator objective is a weighted mean of squared scaled discrepancies. Literal source criteria use absolute HbA1c mean error 0.05, SD error 0.03, and Pani age-mean error 0.10 percentage points, the stated projection intervals, and all declared marginal limits. The Pani mean objective scale is 0.05, distinct from its 0.10 compatibility limit. Equality is not numerical improvement.

Resource caps were 30 s, 1,024 MiB, 20,000,000 output bytes and 100,000 log bytes per execution. Execution receipts and retained output/log sizes are reported in execution_usage.csv. Peak memory, CPU time and monetary cost were not measured. A search cap, if reached, would not establish impossibility.

## Interpretation and next step

A robust reduction of aggregate source loss does not erase individual source failures. Source-side success could justify designing a separate fresh-target study; this unit authorizes no target access. These engineering limits cannot establish clinical equivalence, target utility, causal or individual validity, conditional biological curvature, or broad method validation.

The independence/covariance assumptions, finite age supports, residual law, Pani unweighted survey proxy, assay comparability and cross-source transport remain unverified. Lifelines' overall mean and Pani's 55–59 mean are distinct fixed source anchors; a future target location remains unidentified. Pani/Liu overlap is not independent replication, Pani SEs are not individual SDs, and Jansen interval confidence levels remain unknown.

## Independent QA and provenance

No production generator, calibration or source-check module is imported. NumPy/pandas independently recompute mean, sample SD (ddof=1), event proportion and raw-unit OLS under exact declared selections. The comparison tolerance for reproducing floating arithmetic is rtol=1e-10, atol=1e-12; numeric source criteria and improvement use literal inequalities without tolerance. All-trial trajectories use aggregate records; only baseline/selected tables at the three fixed seeds are parsed.

The input manifest binds complete result files, release/authorization gates, candidate freezes, source inputs, budgets, execution artifacts and this analysis code. Hashes are retained-artifact commitments, not signatures against replacement of every record. All exported tables contain aggregate results only. Visual figure QA is recorded separately.

Audit mechanics: **PASS**, 26735 checks. Numeric source-compatibility failures are separate from audit failures.


## Final interpretation and closure

The unchanged alternative baseline passed all 20 declared numeric checks on both unused seeds. Its fitted selection lowered fitting-seed loss, increased loss on each unused seed, and introduced a Pani age-slope failure on both. Thus, optimizing this objective lost a declared compatibility property that the baseline already had. The baseline remains retained; this observation does not authorize post-replay reselection.

The linear age-slope value 0.00799097657 on seed 19123 is a small literal miss below the authored lower bound 0.008. It is still a positive association. Its failure is an engineering-threshold result, not a biological reversal or a demonstrated clinically meaningful difference.

The alternative has lower selected loss and smaller worst Pani age-mean error than the selected linear structure on both unused seeds, but introduces a new age-slope failure relative to linear on 19111. The complete descriptive preference rule therefore fails. Numerical stability, source compatibility and structural comparison remain separate conclusions.

This bounded unit is closed with both structures, all baseline and selected results, and every criterion failure retained. No additional fit, model rewrite, evidence request or target step is executed or authorized by this audit.

Resource review: neither 40-trial nor 88-execution cap was reached; all 74 trials and 164 executions succeeded, with no parameter-bound hit across the 370 trial-parameter values. The largest recorded execution elapsed time was 2.672 s, largest generated output was 459,809 bytes, and saved stdout/stderr logs were empty. No timeout, output/log-cap or memory-limit failure was recorded. Peak memory and monetary cost were not measured. Per-structure maxima and totals are in RESOURCE_SUMMARY.json.

Final QA: the maximum absolute statistic reproduction discrepancy was 1.7763568394002505e-15. All 42 paired unrelated marginal diagnostic values were exactly unchanged, in addition to exact row-ID/covariate equality. Both PNG figures were visually inspected with readable labels and no clipping; the PDF versions come from the same Matplotlib figures. The three source-panel files are byte-identical.
