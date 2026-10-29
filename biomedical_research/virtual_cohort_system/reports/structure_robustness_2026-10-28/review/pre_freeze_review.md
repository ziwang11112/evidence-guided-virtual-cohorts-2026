# Independent pre-freeze methodology review

Reviewed 2026-10-28. This review inspected current `cohort_harness/lifecycle.py`, `execution.py`, `source_replay.py`, and `source_portfolio.py`; the approved source interface documents; and the prior *methods only* `survey_analysis.py` and `evaluate_committed_v2.py`. It did not inspect participant rows, prior target-result contents, or old report conclusions. No harness or analysis code was modified. Review recommendations are design requirements or interpretive cautions, not target-derived model settings.

## Findings that should be resolved before freeze

1. **Commit the complete experiment, not just individual candidates.** An external protocol commitment should fix candidate-set membership, source review/revision schedule, source and target seed grids, all primary/secondary endpoints, domains, adjustments, transformations, contrasts, reporting rules, and the target release gate. Freeze candidate structures before any target evaluation. The source-portfolio API checks the supplied schedule but cannot establish that it was declared before execution.

2. **Strengthen the target release gate beyond the legacy evaluator.** The legacy evaluator hashes candidate receipts and generated CSVs, but does not call `verify_candidate`/`verify_execution`, require successful execution status, prove each output belongs to its stated frozen candidate and seed, or match all output tuples against an independently frozen expected grid. The new gate should do those checks before any target participant table load, preserve failures, and reject omitted, duplicated, relabelled, wrong-seed, or substituted outputs. Receipt timestamps and hashes provide a procedural audit trail, not externally authenticated chronology or protection against coordinated host rewriting.

3. **Fix endpoint meanings precisely.** The legacy model uses B=(BMI-25)/5 and A=(age-50)/10. Its full-domain quadratic contrast is 2 times the B-squared coefficient: the modeled second difference at BMI steps of 5, holding age and sex fixed. On log-TG this is a log ratio-of-ratios; exponentiation is not an ordinary TG ratio. State which fitted model supplies adjusted age (linear BMI versus quadratic BMI). Use all eligible records for the full-domain quadratic fit, not a selected BMI window.

4. **Keep raw-TG curvature secondary and on its own scale.** The legacy interval function always exponentiates. A raw-TG extension requires an identity-scale interval in mg/dL. A linear conditional mean on log TG can produce positive raw-TG curvature through exponentiation; a raw-only pattern must not count as confirmation of log-scale curvature. Freeze treatment of any nonfinite/raw-tail numerical failure rather than truncating or changing the domain after results appear.

5. **Keep model construction with the builder.** Require explicit, mathematically distinguishable conditional structures and an evidence/assumption map, but do not prescribe favorable age effects, curvature signs, coefficients, or target-derived thresholds. If structures share one builder context and source packet, call them structure sensitivities or candidate constructions, not independent Agent replications. Source-fit trade-offs should be retained per statistic rather than collapsed into an automatic winner score.

6. **Do not conflate conditional simulation with scientific uncertainty.** Fixed-seed draws describe what the generator varies. Residual-only draws are not independent builds, extra clinical evidence, or uncertainty in source estimates, model form, and transport. Generated survey intervals condition on synthetic outcomes and are not calibrated imputation intervals. Reference survey intervals describe target sampling uncertainty, not an acceptance threshold or a formal model superiority test.

7. **Control what changes in structure comparisons.** Prefer the same admitted evidence, source covariate recipes, source assumptions, and scheduled diagnostics when comparing structures. If a candidate also changes evidence interpretation or source population reconstruction, describe the comparison as combined changes. Approximate joint covariate distributions can materially control marginal correlations and apparent source fit.

## Harness assessment

- Candidate freeze/verify binds task, observed input, registry prefix, every candidate artifact, and parent lineage. It explicitly claims structural acceptance only and no Agent sandbox.
- Generator execution stages frozen inputs and uses the supplied isolated process adapter. `verify_execution` can return an intact failed receipt, so callers must also require `status == "success"` and the expected program route, candidate, and seed.
- Source replay copies identical candidate code/specification into declared source contexts, verifies output linkage, binds replay/operator implementation hashes, and recomputes diagnostic values. That establishes numerical provenance, not the truth of source-population assumptions or target validity.
- Source portfolio retains the scheduled diagnostic set and descriptive variation without a scalar success score. It does not independently commit declaration timing.

## Statistical verification performed

Executed only the legacy `survey_analysis.py` self-check on invented fixtures with `python -B`. It passed: analytic stratified mean variance including an empty domain PSU, weight-scale invariance, agreement of coefficients with WLS, positive semidefinite covariance, and row-permutation invariance. No target table was read by that check. The self-check's domain-df assertion tests the chosen convention; it is not an external validation of that convention. The code includes full-design zero-score PSUs for covariance and uses occupied-domain PSUs minus occupied-domain strata for t degrees of freedom. Freeze and explain that convention; no R `survey` cross-validation was performed.

## Minimum discriminating report

Report every frozen structure on adjusted age and full-domain log-TG quadratic curvature, with raw-TG curvature as a secondary transformation diagnostic. Show estimates, units, source-fit trade-offs, target-reference discrepancy, all scheduled seed draws, and explicit limitations. Agreement or disagreement across structural assumptions is the scientific result; no automatic winner, no favorable-seed selection, and no claim that nonsignificance demonstrates equivalence.

This is a pre-freeze review of infrastructure and methodology. Candidate-specific evidence traceability, final evaluator enforcement, and actual freeze/release order remain pending until their new artifacts are available.
