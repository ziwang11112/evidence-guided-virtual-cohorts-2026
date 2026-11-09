# Independent review of the follow-on specification

2026-11-09. Read-only review of `FOLLOW_ON_SPEC.md`, `verify_partial_relation.py`, and `PARTIAL_RELATION_CHECK.json`. No tests, downloads, source retrievals, generated rows, or target/old-result access were performed. Only this review file was written.

## Verdict

**Scientifically defensible and implementable with four narrow clarifications before execution.** The specification correctly admits useful source operators without pretending they match the requested estimands. It permits explicit nuisance and transfer assumptions, preserves the Agent's choice of model, retains uncertainty, and prevents simple replacement of a published multivariable projection by a different regression. It should not be tightened into a requirement that every source variable, source SD, or finite-sample estimation convention be empirically known before any assumption-dependent replay can run.

The aggregate correlation calculation is correct by inspection and agrees with the independently derived calculation. No substantive mathematical correction is required.

## Required clarifications

### 1. State the source-to-target model connection

The current source replay contract can be satisfied by a source generator that reproduces the printed statistics while an entirely separate target-like generator is unconstrained. A `target_use_mapping` label alone does not demonstrate that the admitted evidence actually constrains a target-like result.

Add a declaration of which parameters, functions, distributions or hierarchical relationships connect each source law to the proposed target law; which transport assumptions enable that connection; and which target components remain free. Do not require identical source and target coefficients, a particular parametric family, or a particular direction of effect. An assumption-dependent connection is legitimate. If no connection is proposed, label the source replay context-only for target use and do not count a successful source fit as evidence-guided target construction. This makes the proposed scientific question evaluable without choosing the Agent's model.

Suggested text: “Before execution, declare the source-to-target model or transport link, including shared and population-specific components. Any induced constraint on a requested target use must follow through that declared link. Disconnected source and target laws may support source-method demonstration, but do not establish evidence constraint of the target output.”

### 2. Bound source diagnostics, calibration, and follow-up retrieval

“Necessary source-law diagnostic samples are counted separately” provides accounting but no ceiling. Unlimited source simulations, optimization evaluations, or candidate attempts could occur inside the nominal initial construction or one revision. The follow-up retrieval allowance similarly lacks a finite limit for the new unit.

Before the first execution, register finite source-replay sample sizes, a finite total source evaluation/calibration budget, and a finite definition-retrieval request/byte budget. Count optimizer objective evaluations and discarded source diagnostic attempts in that budget; distinguish deterministic analytic evaluations from random sample draws without making either unlimited. Record the stopping rule and retain attempted configurations sufficiently to audit selection. A declared bounded optimizer is legitimate and is not automatically an additional model revision. The resource limits need not be clinically motivated and should not be numeric goodness-of-fit thresholds.

Also state that every generated target-like table under a parameter, nuisance or transport alternative counts toward the six-table cap; the cap is not six per alternative. Sensitivity that needs more outputs must be analytic/source-law-only within its registered budget or belong to a separately specified later unit. This closes the ambiguity while preserving useful sensitivity work.

### 3. Make feedback separation operational

“Freeze construction and mappings before any common analysis” is good, but specify that the initial and optional revised constructions are both frozen before the common requested-use results are revealed to the constructor. The one revision must use source-replay feedback only. Do not let initial target-like slopes/correlation select the revised model, its nuisance assumptions, or a reporting subset. Store all predeclared final seeds and outputs, including no-change and failed/unavailable outcomes.

This does not prohibit predeclared implementation checks for schema, finite values or calculation errors. If a check discovers a coding defect after freezing, record the repair as such and repeat the same predeclared protocol rather than treating it as unrecorded scientific tuning. No clinical coefficient or sign should be supplied as a repair criterion.

### 4. Avoid requiring the paper to settle an unreported convention

The sentence requiring the chosen BMI SD reference rule to be “justif[ied] ... from the paper” could become an impossible gate when the same specification acknowledges that the paper does not resolve it. Replace that requirement with grounding the choice in the available source structure and explicitly labelling the remaining convention as an assumption. At least one scientifically relevant alternative should be exposed when consequential, within the registered execution budget. The Agent may conclude that a result is sensitive or unresolved; it need not discover the uniquely correct unpublished rule to perform a labelled replay.

The same principle applies to batch encoding, missingness handling and nuisance distributions. Source-faithful labels are mandatory; exact recovery of unpublished implementation details is not. Distinguish: “reported source operator,” “implemented replay under declared conventions,” and “claim of exact finite-sample reproduction.” Only the first two are needed for the proposed assumption-dependent exploration.

## Aggregate calculation review

`verify_partial_relation.py` uses the three independently verified Liu Figure S1 entries (0.16, 0.05, -0.35) under age/sex/batch residualization. The Schur complement and recursive expression both produce 0.18972228326286447 for the additional-BMI partial correlation. It retains batch and does not produce the requested age/sex/BMI-only estimand.

The nearest-0.01 rounding box is handled correctly. The partial-correlation function increases with its first two arguments and decreases with its third throughout the sign-defined box, so the reported extrema [0.18186387273754528, 0.19768038353580558] follow from the stated corners. Positive definiteness at all box vertices also implies positive definiteness throughout the box by convexity of positive-definite matrices. The JSON correctly calls the interval rounding-only and leaves the sampling confidence interval null. No patient or generated rows enter the script.

A small metadata improvement would add the original Methods-versus-caption adjustment discrepancy to the JSON `unresolved` list. Companion review documents already preserve it, so this is not a mathematical blocker. The rounding assumption is an assumption about numerical precision, not evidence of statistical independence among correlation estimates; no joint likelihood should be inferred from it.

## Conditions that already work

Keeping all eight Soares2019 coefficients avoids result-based source selection. Using Soares2020 as an overlapping source check avoids false independent precision. Treating Liu as a different-population, batch-adjusted sensitivity operator avoids an unjustified empirical covariance merge. Source CIs remain estimates' uncertainty rather than residual SDs, the derived Liu statistic is correctly redundant, and missing source information cannot be filled with target records. These provisions should remain.

With the clarifications above, the next unit can execute a bounded, honest assumption-dependent source replay and report unresolved target-use sensitivity. It need not establish exact source identification or clinical validation to produce informative results. This review approves the corrected design concept; it does not report an executed experiment or approve a claim of improved target data.

## Disposition after revision

2026-11-09: independently reread the revised `FOLLOW_ON_SPEC.md` once. **All four requested clarifications are satisfactorily addressed; the revised design is approved for the proposed bounded follow-on.**

The revised specification declares an explicit source-to-target link while preserving model freedom, permits grounded assumptions for unpublished BMI-standardization conventions, separates source-feedback revision from requested target-use results, and records coding repairs. The caps now cover all alternatives: six target-like tables of at most 3,000 rows each; 24 source-sample evaluations of at most 10,000 rows each; 200 total calibration objective evaluations including internal/discarded calls; and at most five further definition-discovery requests inside the remaining parent request allowance. The cumulative saved-source ceiling remains 100 MiB. These are resource bounds, not clinical fit thresholds.

The accepted specification has SHA-256 `ba5877270281ee350d55aae367793fcd3d8f8ce48af2b5fe3f132ecc579c1b06`.

Execution must still instantiate the declared source/target mapping and enforce the registered ledgers and feedback separation. Approval concerns design adequacy only: no experiment has been run, source uncertainty has not disappeared, and no improved-target or clinical-validation claim follows. No further tests, source inspection, downloads or other files were needed for this disposition.
