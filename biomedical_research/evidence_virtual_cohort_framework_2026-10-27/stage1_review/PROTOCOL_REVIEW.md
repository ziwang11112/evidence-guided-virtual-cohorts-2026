# Independent Stage 1 protocol review

**Final disposition: PASS for builder launch, `stage1_v3`.** All six findings below were resolved before builder exposure or target evaluation. Independently rerun: 62/62 source/contract checks and 8/8 artificial prelaunch guards. All active staged inputs are the nine `initial_v3` contexts; v1/v2 are retired with original snapshots retained. The reviewed `protocol_freeze.json` SHA-256 is `d0256c313fd23ce0eaa2f29b1336562dd8f3f2cbec134dab3016d744e9244d34`.

The final changes correct raw adult leptin wording; match and log both revision policies' candidate/calibration budgets; require exactly 21 committed final arms and 420 requested draws before any reference analysis read; keep summaries term/family-specific; qualify direction when the reference is unresolved; and retain per-scenario empirical state distributions plus within-lineage ordinary/proposed comparisons. Modal-state disagreement is expressly a finite-Monte-Carlo descriptive sensitivity indicator, not proof of structural disagreement or a probability over models.

The additional Ross eligibility guard now rejects weight above 180 kg at baseline only. An independent artificial fixture confirms that 181 kg is rejected at month 0 and permitted at month 3. No global postbaseline 180 kg cap is imposed. Source checks and reference equality still pass after this addition.

**This PASS authorizes only the prespecified source-restricted builder stage. Target evaluation remains gated until all 18 Agent and 3 fixed statistical arms are complete and committed.** No production target analysis was run or reserved inferential answer inspected by this reviewer. The complete expected evaluator inventory is 7,700 term-level records, including failure placeholders.

Final evidence: `source_contract_checks_stage1_v3.json` and `prelaunch_guard_checks_stage1_v3.json`. The original review and its reasons are retained below for provenance.

Status at first review: **source extraction passes; protocol implementation needs prelaunch amendments before a valid same-budget comparison and complete final evaluation.** This is a scientific/contract review, not a report of target performance.

The accompanying `source_contract_checks.json` records 62 passing checks against the snapshot it hashes. The checks independently verify original-public-source-to-custodian numeric extraction, permitted packet transcription and analysis units, endpoint-complete marginal definitions, nine staged initial contexts, the 55-item analysis registry, the 360 Agent + 60 statistical cohort budget, staged packet equality and freeze hashes. They compute only already-permitted marginal statistics and equality checks; no reserved correlation, change SD, test or confidence interval is computed.

## Required amendments

1. **Correct the Travers measurement description before builders read it.** `stage1/packets/case_b/evidence.json` says `pediatric leptin already log10(pg/mL)` in `E_marginals.measurement`, while this adult case supplies leptin in ng/mL. The per-endpoint unit is correct, but the common description is misleading. Remove the pediatric clause for case_b, preserve it for case_c, and update staged copies and hashes through an explicit prelaunch amendment. Already-frozen files must not be silently replaced.

2. **Equalize and log the numerical source-calibration budget.** The protocol allows ordinary policy to examine up to three structures but permits three diagnostic cohorts “per retained scenario.” Ordinary retains one and proposed can retain three, so the literal diagnostic allowance is three versus nine. Use the same maximum total number of unique diagnostic draws across up to three examined structures for both branches, including rejected ordinary candidates. Retain candidate identities and actual calibration calls. Repeating a seed to check determinism is verification, not additional independent Monte Carlo information. The final-output budget is already correct: 20 total, with 20 / 10+10 / 7+7+6 allocation.

3. **Freeze the complete final-run inventory before opening reference analyses.** `runner.evaluate()` currently reads reference data immediately and discovers finals with recursive globbing. It does not require all eighteen Agent branches and three statistical cases, and can discover finals from multiple repaired versions. An explicit immutable selection manifest must identify one scheduled final version per paired branch and one fixed reference per case. Validate its hashes and expected 21-run / 420-requested-cohort inventory before reference inference. Retain failed draws; do not replace them or choose versions after seeing target performance.

4. **Separate scientific families and scales in summary metrics.** `scenario_summaries` currently groups by case, lineage, branch, scenario and validation role. Its median absolute error consequently mixes Ross time effects measured in kg, PFS units, error counts and AUC, and combines reserved paper-replay correlations with the four exploratory proxies. Absolute errors should be reported by term or scientifically comparable family/scale, or transformed by a prespecified defensible dimensionless scale. Keep 31 replay outputs and four proxies explicitly separate. Do not choose a scale or family after observing which makes the policy look better.

5. **Distinguish numerical sign from established scientific direction.** `direction_agreement` currently compares point-estimate signs even when the reference interval overlaps zero. This is descriptive numeric-sign agreement; it must not count as recovery of a known biological direction. Report scientific direction as unresolved for such reference rows, while retaining all rows and their uncertainty-state disagreement. The existing `unsupported_evidence_discrepancy` wording is appropriate and must not be renamed to population false positives.

6. **Complete the policy-level reporting contract before evaluation.** The declared between-scenario evidence-state disagreement metric and paired ordinary/proposed lineage summaries are not implemented in the reviewed evaluator. Preserve full term/scenario/cohort records, compare branches within their common initial lineage, and show all case results. Report how many scenarios/cohorts are usable; do not treat rows, correlated terms or seeds as independent studies. A policy-level “robust” result can describe only the examined precommitted scenario set, not all compatible models.

## Scientific conditions already correct

- Scope is A0 summary-conditioned whole-cohort development synthesis, with no completion or independent-confirmation claim.
- Three cases × three common initial lineages × two branches × twenty final outputs = 360; fixed statistical references add sixty. Eighteen branches are paired descendants, not eighteen independent initial constructions.
- Each paired case contains four paired mean changes and all six cross-endpoint delta correlations. Complete-pair selection and actual correlation denominators are used. He leptin remains on log10(pg/mL); no raw concentration/log-scale substitution occurs.
- Mean-change point estimates are reconstruction quantities; withheld covariance governs their uncertainty. The analysis rows retain reserved paired covariance diagnostics rather than pretending the means are independent target predictions.
- Ross contains six baseline correlations, 25 time contrasts, and four expressly exploratory standardized association proxies. The pinned analysis reports normal-Wald inference and fit warnings/status; exact SAS finite-df inference is not claimed.
- Unknown clinical relations remain evaluated. Source marginals do not establish zero cross-endpoint dependence. Source compatibility diagnostics are explicitly descriptive, not clinical equivalence tests.
- Structural scenarios share the same total output budget; scenario frequencies are not posterior probabilities. Separate fully generated cohorts are neither row-stacked nor Rubin-pooled.
- Unavailable local model/provider/token metadata are explicitly recorded as unavailable. Controller timestamps are not described as isolated model inference latency.
- Fresh builder contexts get a path allowlist and no original source IDs, rows, inferential outputs or paper findings. The boundary is correctly described as procedural, not an adversarial sandbox, and previous development exposure remains disclosed.

## Additional source caveats for interpretation

He's both-times-null synthetic pattern is an endpoint analysis-pair contract. The source itself has an available post-only value for the excluded pair; the supplied means/SDs exclude that pair. This design is appropriate for the frozen paired analyses but is not a raw-visit missingness reconstruction.

Ross random-intercept time estimates are constrained by the supplied visit moments but, with missingness, are not generally algebraically fixed by them. Their broad reconstruction label is conservative, but the report should state that both the fitted estimate and its uncertainty can vary with the assumed joint structure and missingness. The original No-Go ceiling of 512 is a conservative mathematical bound, not an expected biological range.

## Re-review rule

Amendments made before builder exposure/target evaluation should preserve the reviewed snapshot and record the reason and timing. Re-run `audit_contract.py` after the amended freeze and staging files exist, and add a dated disposition here. This reviewer does not authorize opening the reserved evaluator while the inventory/budget/reporting gates remain unresolved.
