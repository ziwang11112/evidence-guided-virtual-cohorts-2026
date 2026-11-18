# Independent selection and analysis review

9 November 2026. Reviewer: `/root/v26_novelty_review`.

**PASS for the selection-lock stage and the fixed numerical estimator.** No material correction remains in the reviewed selection rules, three estimands or uncertainty wording. This receipt is not a full method-release approval: the final evaluator is still a deliberate placeholder, and controller/batch-seal enforcement, source adequacy and author dispatch remain separate gates.

Reviewed exact SHA256:

| File | SHA256 |
|---|---|
| `PROTOCOL.md` | `e8a52b53c2d4e5312e6582c8e53473de15b10eb87a5c0207d53e7c3d665a6d52` |
| `runtime/analysis_tools.py` | `665b6c4ab045abc0868912060a70c7959517003b9bb941ab181076282d493792` |
| `runtime/evaluator.py` | `60ad8a197a4547f3c2ef1d178cf5d443591ea2a1b39d8ac63a7a766ad73f304c` |
| `runtime/independent_check.py` | `64662a8cf460b76b259e867e3a69e8a50328d1209b94aa96214de060855555f4` |

The reviewer wrote only the independent checker and this receipt/JSON. Root-owned implementation and protocol files were not edited. No clinical table, readiness result, target marginal, target relation or generated author output was read. `load_reference`, `readiness` and `evaluate` were never called. All executed records were invented fixtures; temporary CSV/JSON inputs were removed automatically.

## Numerical checks

The independent oracle uses pure-Python weighted orthogonal projection and the Frisch–Waugh–Lovell identity, rather than calling or duplicating the production NumPy least-squares routine. Known artificial BMI slopes are 1.75 and 0.80 per unit BMI; the adapter correctly reports 8.75 and 4.00 mmHg per 5 kg/m². The oracle separately residualizes BMI and both outcomes on age/sex, computes the slopes, then correlates the full weighted residuals.

Ten oracle checks and twelve production-adapter comparisons passed. They cover weighted/equal-weight estimates, raw and residual SD, row permutation, global weight rescaling, singular design, deterministic outcome residuals, invalid-value rejection, exact request-envelope rejection and the generated adapter's unit-weight behavior. Rank failure returns all named estimands as null; a deterministic residual preserves estimable slopes while leaving residual correlation undefined. Invalid generated values raise an error instead of silently deleting rows.

The 500 row-resampling draws at seed 73991 were independently regenerated on invented records, retaining sampled rows' original weights. Each draw's estimates were recomputed with the independent oracle; independently interpolated 2.5% and 97.5% quantiles agreed within numerical tolerance. The result labels correctly say conditional IID row-resampling stability and disavow survey-design or national confidence. The review does not claim bootstrap coverage or calibrated population uncertainty.

The production generated adapter statically reads only its three explicit argument paths and calls the fixed summary routine. It contains no clinical reference path or import of the evaluator. Its structural checks supplement the existing task/output contract; they are not claimed to replace the full host schema validator. Tests ran under local Python 3.12 with NumPy 2.4.5 and pandas 3.0.3; no isolated author execution or WSL sandbox test is claimed by this receipt.

## Selection and readiness boundary

Nine additional selection checks passed using a 70-row invented raw frame, with 56 explicitly expected eligible rows. They verified inclusive age 20–79 and documented anthropometry/BP bounds, sex mapping, BMI units, all seven required non-pregnancy fields, positive finite weights, missing/sentinel handling, and the retained unknown/inapplicable pregnancy states. SBP<DBP records and extreme BMI resulting from otherwise dictionary-valid height/weight were retained. No HbA1c availability/value entered selection. Exact required-field matches were retained. All exclusions were accounted for, empty selection had rank zero, and a missing required column failed explicitly.

One checker-development assertion initially expected one duplicate match, then was corrected to two: two invented spellings of missing pregnancy both coerce to missing and match on all required fields. Production behavior was correct and unchanged; the assertion was corrected to the documented post-coercion diagnostic. No clinical result informed the correction.

Static review confirms that `readiness()` verifies `SELECTION_LOCK.json` before loading the archive. `load_reference()` verifies the frozen archive/member hashes and reads only the eight declared columns. The selection function reports counts, sex support, weighted design rank and retained-row diagnostics, without computing an outcome mean, slope, correlation or comparison. Its prospective readiness rule (>20 eligible rows, rank 4, both sexes) is a feasibility gate, not a performance threshold. No stable person identifier is invented and matching required-field rows are not called duplicate people.

The protocol now clearly distinguishes the single custodian-only readiness read after the selection lock from reference analysis/comparison after the all-author batch seal. It also explicitly exempts pregnancy from the seven-field finite complete-case requirement. Both review corrections were wording clarifications; no numerical endpoint or clinical target was changed. The controller will bind the dictionary hash and measurement metadata/receipt in the selection lock; this receipt relies on the separate metadata review for those dictionary ranges and device/timing facts and does not reopen the workbook or manual.

## Protocol scope and remaining release gates

The protocol accurately limits the claim to a newly prespecified BP task in an exposed PNS release. Generated equal-weight rows target the finite `peso_lab`-weighted complete-case distribution under transport assumptions. The same rows/design serve both BMI slopes and residual correlation; unweighted analysis is a sensitivity panel. Neither WLS nor the supplied weights establishes causal effects, national representativeness or survey confidence intervals.

The five fixed fresh-context author slots, three fixed seeds (271, 409, 557), two-stage maximum, retention of failed/nonestimable cases, no arbitrary accuracy threshold, and no post-reveal generator changes form a coherent descriptive validation plan. Three seeds are Monte Carlo variation and five authors are construction variability, not independent clinical replications. The protocol does not mandate a model family or hand-written desired relation.

Before the full method freeze and author dispatch, separately verify the completed evaluator/controller, exact source and skill inputs, all-author batch closure and checksums, budget/stage accounting, and model-call metadata. The currently reviewed `evaluate()` intentionally raises `NotImplementedError` after the placeholder gate; it cannot yet perform a complete clinical comparison. Any later evaluator change must receive an updated review/hash receipt. After a valid batch seal, independently recompute reference and all selected-output results against the fixed protocol; none of those later analyses is certified here.
