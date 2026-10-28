# Independent Stage 1 postrun review

**Disposition: PASS for computational integrity and a qualified development-feasibility release.** No production output needs correction or exclusion. This is not a finding of clinical validity, confidence-interval coverage, independent confirmation, or policy superiority.

The source audit was completed before this reviewer read reserved outputs. Numerical verification began only after the controller signaled that `custodian/evaluation_v1/evaluation_manifest.json` was complete. The evaluated manifest SHA-256 is `ee3d4358cabd9e4a0813a4f10d56675826f961f7d16cf77272092c4a28d7428b`. This reviewer changed only files inside `stage1_review/postrun/`, generated no additional production cohorts, and did not call the production evaluator.

## Integrity and numerical verification

The source audit passed 3,030 assertions across 30 frozen candidates, including nine initial parents, eighteen paired revisions and three fixed statistical arms. All parent copies and sibling parent identities agree; protocol, staged inputs, generator decisions, candidate manifests, final CSVs and per-draw records retain their committed hashes. The complete inventory contains 21 final arms and 420/420 saved cohorts, with the scheduled seeds and 20 or 7/7/6 allocations. `SOURCE_EXECUTION_REVIEW.md` documents the implementation review and budget qualifications.

The post-evaluation audit passed **127,271/127,271 assertions**. These are software checks, not independent scientific observations. All custodian input hashes also agree with the freeze. Accounting is exact:

| Item | Verified count |
|---|---:|
| Reference analysis terms | 55 |
| Synthetic term records | 7,700 |
| Ross / Travers / He records | 4,900 / 1,400 / 1,400 |
| Cohort groups | 420 |
| Per-scenario term summaries | 825 |
| Scenario sensitivity rows | 385 |
| Paired lineage-term comparisons | 165 |
| Generation or dataset-level analysis failures | 0 |
| Terms with `status=ok` and usable comparisons | 7,700 |

An independent implementation recomputed every synthetic paired-change and change-correlation result and every Ross baseline correlation from the committed local CSVs: **3,640 synthetic rows and 26 reference rows**. It checked estimates, SEs, confidence intervals, p-values, denominators, paired change SDs and paired correlations. The largest absolute difference was `7.44e-15`, attributable to floating-point evaluation order.

Eight representative mixed-model terms cover the Ross reference, an ordinary arm, a proposed alternative scenario, and a fixed statistical arm; each includes a weight trajectory contrast and a standardized PFS association. Explicit design matrices reproduce all saved quantities exactly. A separate scalar restricted-likelihood optimization and generalized least-squares calculation independently reproduce their estimates within `2.67e-8`. This checks the specified normal-Wald/REML implementation, not exact SAS finite-degree-of-freedom inference or the validity of random-intercept assumptions. The explicit-matrix check shares the pinned numerical fitting library; the scalar likelihood check does not share its optimizer.

Every result's registry role/family, evidence state, reference fields, agreement, unresolved-direction qualification, unsupported-evidence indicator, absolute error, SE ratio and paired covariance diagnostics were recalculated. All scenario summaries, state frequencies, modal-state comparisons, estimate ranges and paired reports agree with the committed term records. No raw errors are combined across different endpoint units. Reference-overlaps-null rows correctly have no established scientific direction.

The first audit invocation reported one inventory mismatch because the evaluator serialized Windows backslashes while the inventory used forward slashes. Normalizing separators in the **audit code only** resolved it; all 21 path/hash pairs agreed. This audit implementation correction is preserved in `evaluation_audit.json`. No production artifact was amended.

## Fit warnings remain material

Successful execution must not be described as 7,700 warning-free or validated analyses. Among the 1,260 synthetic Ross model fits, **184 unique fits carry a boundary warning**, appearing on 828 term records. A trajectory contributes five terms and must not be counted as five independent fit failures. The warning threshold also depends on the variable scale, so warning counts are not a method ranking.

One of those fits, **fixed statistical case_a, rho_0, draw 7, `dd100_time_reml`**, also has a non-positive-definite Hessian warning. Its five contrasts remain `status=ok` and enter the predeclared summaries because the model converged with finite SEs under the frozen status rule. An additional check reproduces the month-12-minus-baseline estimate `0.05586078728462037` and SE `0.02886750319411511`; independently optimized GLS gives `0.05586078728325793`. Computational agreement does not remove the warning or establish trustworthy Wald calibration. Retain all five terms and state this limitation. `warned_fit_check.json` records the targeted verification.

For a subsequent protocol, distinguish executable, converged, warned and inferentially usable fits explicitly and predeclare handling before outcomes are opened. A post hoc exclusion or substitute fit in this run would violate the frozen comparison.

## What the completed run supports

The proposed branches executed the intended finite structural sensitivity exercise. The following counts retain each scientific family and count a term once within each of its three lineages:

| Case and family | Lineage-term comparisons | Different modal evidence-state sets across proposed scenarios |
|---|---:|---:|
| Ross baseline correlations | 18 | 9 |
| Ross exploratory proxy associations | 12 | 10 |
| Ross time contrasts | 75 | 5 |
| Travers cross-endpoint change correlations | 18 | 10 |
| Travers paired changes | 12 | 7 |
| He cross-endpoint change correlations | 18 | 18 |
| He paired changes | 12 | 3 |

These are descriptive finite-scenario counts, not independent experiments, probabilities over models, or proof that structural assumptions caused each difference. Each scenario has only six or seven draws, so Monte Carlo fluctuation can contribute. Paired-change mean matching is reconstruction; differences in paired evidence states can arise through assumed covariance and SEs. Ross time estimates can also change under missingness and the assumed joint structure. The four Ross proxy outputs remain exploratory and must not be presented as exact paper replay.

The construction evidence still limits policy interpretation: eight ordinary arms are justified exact no-ops; one ordinary arm changes PFS granularity; proposed branches use more of the same maximum calibration allowance; and lineages use different degrees of finite-sample marginal conditioning. Neither this table nor an apparently favorable scenario can establish superiority, coverage, optimal model selection or independent prediction. All three cases were already exposed development studies.

## Release and expansion recommendation

Release the frozen, auditable **development feasibility results** with all branches, scenarios, warning counts, source-only calibration logs and construction limits visible. A sanitized release may include code, protocol, aggregate results and these aggregate audit notes; participant reference inputs remain local. Do not advertise sensitivity ranges as calibrated uncertainty intervals, source compatibility as clinical validation, or the best scenario as a selected winner.

Proceed to a bounded, separately preregistered **held-out feasibility experiment** before broad expansion. Use genuinely unexposed cases, retain a predeclared complete inventory gate, and hold measurement mapping and marginal-conditioning strategy constant within policy comparisons. Record actual diagnostic calls and available model/token/cost metadata, and predeclare fit-warning handling. Decide the target criteria before viewing outcomes: a comparison of scenario reporting, a comparison of predictive accuracy, and interval-coverage calibration require different designs. If coverage is a goal, add a simulation with known generating truth; empirical agreement against one small observed reference cannot establish it.

Preserve this completed run as its own frozen development experiment. New scientific revisions belong in a new experiment, not repaired versions selected after these results.

## Audit artifacts

- `audit_source_execution.py` and `source_execution_audit.json`: source execution integrity, parent equality, allocations and declared budgets.
- `audit_evaluation.py` and `evaluation_audit.json`: independent numerical checks, result accounting, all summary checks, and fit warning counts.
- `warned_fit_check.json`: targeted verification of the Hessian-warning trajectory.
- `SOURCE_EXECUTION_REVIEW.md`: source-only implementation review and limitations recorded before reserved numerical review.

All participant-level data remained local. The saved audit outputs contain only aggregate or term-level scientific results and artifact metadata.
