# Independent verification of attempt 02

Status: **PASS_WITH_INTERPRETATION_LIMITS**. 44/44 independent checks passed.

The audit used only the completed attempt_02 batch; it did not rerun generators or edit batch/source artifacts. It verified all input and output hashes, reconstructed comparison metrics and Rubin arithmetic independently, and reran one direct reference PFS contrast.

- Inputs: 144 (1 reference, 3 missing-only, 120 completions, 20 distinct synthetic cohorts).
- Results: 5,040, with exactly 35 unique analyses per input.
- Completion results: 720 affected outputs plus 3,480 copied preservation controls. The controls are excluded below.
- Pooling: 36 results, each from all 20 completions; no full-synthetic pooling.
- Frozen hashes: 251 source files, 4 implementation files, 144 registry inputs, and 5 manifest-listed outputs all checked.

## Affected completion results

Every count below has denominator six. Outcomes and masks are correlated; these are descriptive counts, not independent trials. Statistical reference is the frozen MICE comparator.

| Mask | Missing-only CI matches | Agent CI matches | MICE CI matches | Agent lower error than missing | MICE lower error than missing | Agent lower error than MICE |
|---|---:|---:|---:|---:|---:|---:|
| mcar_a | 6 | 6 | 5 | 1 | 1 | 4 |
| mcar_b | 6 | 6 | 6 | 2 | 1 | 6 |
| baseline_dependent | 6 | 6 | 6 | 3 | 2 | 6 |

Across the 18 affected outcome-mask combinations, Agent and missing-only both match the reference interval state in 18/18, while MICE matches 17/18. Agent has lower absolute effect error than MICE in 16/18, but lower error than missing-only in only 6/18. These results do not establish a general benefit from completing the data. The MICE disagreement is mcar_a PFS month12-minus3 (reference uncertain, MICE negative); the Agent upper limit in that comparison is also close to zero.

Intervals are 95% intervals. `uncertain` means the interval includes zero; it does not prove no association. Numbers below are estimate [lower, upper], followed by interval state.

| Mask / affected outcome | Observed reference | Missing-only | Agent pooled | MICE pooled |
|---|---|---|---|---|
| mcar_a / month_12_minus_0 | -0.38198 [-0.50995, -0.25402] negative | -0.40030 [-0.54070, -0.25991] negative | -0.40523 [-0.54710, -0.26336] negative | -0.42852 [-0.56984, -0.28720] negative |
| mcar_a / month_12_minus_3 | -0.05295 [-0.18135, 0.07545] uncertain | -0.11684 [-0.26788, 0.03420] uncertain | -0.15291 [-0.30663, 0.00081] uncertain | -0.16417 [-0.31078, -0.01757] negative |
| mcar_a / month_3_minus_0 | -0.32903 [-0.45381, -0.20425] negative | -0.28346 [-0.42090, -0.14603] negative | -0.25232 [-0.39187, -0.11277] negative | -0.26434 [-0.40476, -0.12392] negative |
| mcar_a / month_6_minus_0 | -0.34372 [-0.46981, -0.21763] negative | -0.35082 [-0.48679, -0.21484] negative | -0.35415 [-0.48801, -0.22030] negative | -0.34807 [-0.48575, -0.21039] negative |
| mcar_a / month_9_minus_0 | -0.31613 [-0.44348, -0.18878] negative | -0.34646 [-0.48779, -0.20513] negative | -0.34511 [-0.48202, -0.20820] negative | -0.37139 [-0.51121, -0.23157] negative |
| mcar_a / PFS-weight proxy | 0.16572 [0.06943, 0.26201] positive | 0.17052 [0.06245, 0.27859] positive | 0.14809 [0.05077, 0.24540] positive | 0.14070 [0.04765, 0.23375] positive |
| mcar_b / month_12_minus_0 | -0.38198 [-0.50995, -0.25402] negative | -0.37385 [-0.51804, -0.22966] negative | -0.37800 [-0.53171, -0.22429] negative | -0.37523 [-0.52906, -0.22139] negative |
| mcar_b / month_12_minus_3 | -0.05295 [-0.18135, 0.07545] uncertain | -0.05297 [-0.20232, 0.09638] uncertain | -0.05400 [-0.22085, 0.11285] uncertain | -0.06599 [-0.22605, 0.09407] uncertain |
| mcar_b / month_3_minus_0 | -0.32903 [-0.45381, -0.20425] negative | -0.32088 [-0.45459, -0.18717] negative | -0.32400 [-0.46344, -0.18457] negative | -0.30924 [-0.45372, -0.16475] negative |
| mcar_b / month_6_minus_0 | -0.34372 [-0.46981, -0.21763] negative | -0.36623 [-0.50838, -0.22408] negative | -0.38217 [-0.52893, -0.23541] negative | -0.38844 [-0.52974, -0.24715] negative |
| mcar_b / month_9_minus_0 | -0.31613 [-0.44348, -0.18878] negative | -0.32941 [-0.46874, -0.19007] negative | -0.33795 [-0.47896, -0.19695] negative | -0.36522 [-0.50621, -0.22423] negative |
| mcar_b / PFS-weight proxy | 0.16572 [0.06943, 0.26201] positive | 0.17900 [0.11805, 0.23995] positive | 0.23470 [0.07120, 0.39820] positive | 0.33038 [0.23762, 0.42315] positive |
| baseline_dependent / month_12_minus_0 | -0.38198 [-0.50995, -0.25402] negative | -0.38098 [-0.52653, -0.23542] negative | -0.36583 [-0.53046, -0.20120] negative | -0.43265 [-0.58555, -0.27974] negative |
| baseline_dependent / month_12_minus_3 | -0.05295 [-0.18135, 0.07545] uncertain | -0.09346 [-0.24784, 0.06093] uncertain | -0.06133 [-0.22295, 0.10029] uncertain | -0.13090 [-0.28777, 0.02598] uncertain |
| baseline_dependent / month_3_minus_0 | -0.32903 [-0.45381, -0.20425] negative | -0.28752 [-0.42308, -0.15196] negative | -0.30450 [-0.45313, -0.15587] negative | -0.30175 [-0.45301, -0.15049] negative |
| baseline_dependent / month_6_minus_0 | -0.34372 [-0.46981, -0.21763] negative | -0.37155 [-0.50659, -0.23652] negative | -0.34410 [-0.48236, -0.20584] negative | -0.34666 [-0.49606, -0.19725] negative |
| baseline_dependent / month_9_minus_0 | -0.31613 [-0.44348, -0.18878] negative | -0.31430 [-0.45015, -0.17844] negative | -0.34141 [-0.48340, -0.19942] negative | -0.36016 [-0.50627, -0.21405] negative |
| baseline_dependent / PFS-weight proxy | 0.16572 [0.06943, 0.26201] positive | 0.17961 [0.11765, 0.24156] positive | 0.21279 [0.06789, 0.35768] positive | 0.23732 [0.12816, 0.34648] positive |

## Full generation

| Evidence role | Queries | Draw-query records | CI state matches | Point-sign matches |
|---|---:|---:|---:|---:|
| unprovided_baseline | 6 | 120 | 94 | 61 |
| constrained_trajectory | 25 | 500 | 434 | 457 |
| exploratory_proxy | 4 | 80 | 41 | 74 |

These families must remain separate. The 25 trajectory queries were constrained by source marginals. Only the six baseline relationships lacked supplied covariance; their results cannot be rescued by agreement on constrained trajectories. All 20 cohorts remain in every denominator.

| Baseline query | Mean absolute error | CI matches / 20 | Estimate min–max |
|---|---:|---:|---|
| pfs__gng | 0.14367 | 19/20 | -0.22683 to 0.23072 |
| pfs__dd100 | 0.27123 | 0/20 | -0.25565 to 0.20378 |
| pfs__dd1000 | 0.24415 | 17/20 | -0.26687 to 0.27583 |
| gng__dd100 | 0.19520 | 20/20 | -0.20452 to 0.22313 |
| gng__dd1000 | 0.14509 | 18/20 | -0.23656 to 0.28496 |
| dd100__dd1000 | 0.07755 | 20/20 | 0.36600 to 0.69495 |

The PFS-DD100 reference correlation is r=0.22859, unadjusted p=0.04855, near the significance threshold; the publication reports no significant association. Its 0/20 CI-state agreement should therefore be read alongside the mean absolute r error of 0.27123, rather than treated as threshold-only proof of failure.

## Source and numeric checks

[The source article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243530) documents 75 participants, five visits, participant random effects, and REML. Its published weight effect/SE examples support the reconstruction checks. Its t(268)=-3.18 and p<.001 report is internally inconsistent. SAS finite-df details and pooled-model scaling are insufficiently specified for exact CI/proxy equivalence; the batch correctly retains these limitations.

The independent direct reference fit of PFS month12 minus month3 converged: estimate -0.0529511571048, SE 0.0655115946406; both match the batch within rtol=1e-10 and atol=1e-12. The fit read the reference input without exporting patient values.

All 36 pooled rows were rebuilt from per-completion analysis outputs: Qbar, Ubar, B, T, SE, Rubin df, t interval, and p value. All effect errors, CI state labels, agreement flags, missing-only comparisons, and full-generation summaries were also recomputed.

## Interpretation limits

- Known-result retrospective development, not confirmation or unseen-task validation.
- 29 copied outcomes per completion are preservation controls; exclude them from completion success rates.
- 25 full-generation trajectories are constrained by supplied source marginals; separate from six unprovided baseline relationships.
- The exact observed-data reference retains native missingness and sampling uncertainty; it is not population truth.
- Uncertain intervals do not prove a null or equivalence.
- Rubin large-complete-sample pooling arithmetic does not validate proper multiple imputation or repeated-sampling coverage.
- No Rubin pooling of full synthetic cohorts; min/max ranges are descriptive Monte Carlo variability.
- No validation of study-design usefulness, cross-study transfer, causal treatment effects, or added independent patient evidence is performed.
- Only one selected reference analysis was rerun independently; all other statistical fits were checked through code, frozen provenance, arithmetic and consistency.
- No raw patient rows or values are exported in review artifacts.

Detailed machine-readable checks, aggregate comparisons, and SHA-256 values are in `verification.json`. The audit implementation is `audit_attempt_02.py`.
