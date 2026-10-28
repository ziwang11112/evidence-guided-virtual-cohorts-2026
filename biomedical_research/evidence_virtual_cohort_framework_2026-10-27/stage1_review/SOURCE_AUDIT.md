# Stage 1 source and scientific-protocol audit

Independent read-only review of source adapters and the new Stage 1 contract. This directory is evaluator/custodian material, not an additional builder input. No new generator has been run by this reviewer, and no reserved outcome estimate, correlation, test, interval or reference-analysis answer is reported here.

## Source interpretation verified before new evaluation

The source preparation scripts for Travers and He are at each replication project's root, not its `generator/` subdirectory.

| Case | Source read | Required scientific interpretation |
|---|---|---|
| Travers | `obesity_public_data_replication_2026-10-25/generator/INPUT.md` and `prepare.py` | 12 men, ages 35–55, abdominal overweight/obesity, before/after 3 days of about 50% usual energy intake. Single fasting paired cohort, without a control arm. Leptin is ng/mL, body mass kg, glucose and triglycerides mmol/L. The four supplied marginal summaries are rounded sample means/SDs from the workbook, not necessarily verbatim paper statistics. |
| He | `obesity_larger_replication_2026-10-25/generator/shared_moments.json` and `prepare.py` | 44 children, ages 7–14, completers after a 3-month home diet/exercise programme. Not a randomized parallel-arm contrast. Leptin is on the analysis scale log10(pg/mL); body mass is kg and glucose/TG are mmol/L. The former has 44 complete pairs, as does body mass; glucose/TG each have 43. All supplied means/SDs are computed on the endpoint's complete pairs. |
| Ross | `obesity_paper_replay_2026-10-27/allowed/evidence.json`, `allowed/schema.json`, `prepare.py`, and `paper_analysis.py` | 75 participants, months 0/3/6/9/12, all 375 person-visit slots retained. Marginal observed counts do not identify individual masks or missingness mechanism. Weight kg, PFS 1–5, integer No-Go errors, and delay-discounting AUC 0–1. Larger AUC means less discounting. No untreated comparison arm. |

### Pairing and missingness

Travers extracts each endpoint's pre rows 3–14 and post rows 15–26 in matched order. The source preparation verifies the paired analysis against the workbook formula. The new adapter must retain person-level pairing, never use two independent groups or treat 24 visits as 24 people.

He deliberately represents unavailable endpoint analysis pairs by setting both pre and post to null on the last synthetic row. The original source has an unavailable pre observation and an observed post observation for the excluded analysis pair; the supplied statistics are nevertheless complete-pair statistics. This synthetic contract is appropriate for the four paired changes and six cross-endpoint change correlations. It does not reproduce raw visit-level missingness. It must not be used to claim fidelity to the raw post-only marginal or to an all-observations longitudinal model. The source has the same excluded analysis pair for glucose and triglycerides, so the frozen change-correlation pair counts are consistent with the shared synthetic analysis-pair mask. Source row identity is not needed by builders.

Ross's available nonmissing counts are per endpoint per visit. Matching them does not establish correct dropout, cross-variable missingness, or MAR/MNAR behavior. The source preserves unusual observations; any source anomaly sensitivity must be separately declared, not silently used to replace the primary source or repair generated records toward a target answer.

### Claim-family semantics

For each paired case, keep all four paired mean-change outputs and all six Pearson correlations among endpoint changes. Mean change is post minus pre, in the supplied analysis unit. The means of complete paired samples algebraically determine the mean-change point estimate, apart from rounding. Therefore the point estimate is supplied/reconstruction; its paired change SD, SE, interval, test and evidence state still depend on withheld joint structure. The six cross-endpoint change correlations are reserved and unidentified by the supplied marginals. Correlations must use pairwise complete changes with the actual person denominator reported.

Ross `paper_analysis.py` produces six baseline Pearson correlations plus five time contrasts for each of five outcomes, totaling 31 paper-replay outputs. The additional four pooled standardized random-intercept associations are exploratory proxies, not exact replications of published regression coefficients. The time-model interval/test is normal-Wald; it is not asserted to reproduce SAS's unspecified finite-denominator-df method. Supplied marginal moments constrain the time trajectories but do not completely determine random-intercept estimates in the presence of missingness. Keep formula, transformation, missingness, actual participant/row counts, fit status, warnings and inferential method visible.

### Required inference boundaries

- A statistically unresolved real-data relationship is not a population null. A newly confident synthetic relationship is an unsupported-evidence discrepancy, not an established false positive. Preserve these relationships in the denominator.
- Generated full cohorts are Monte Carlo outputs. Do not concatenate them into one enlarged study or use Rubin pooling as though they were multiple imputations.
- The three source cases are previously exposed development cases. A fresh builder context does not turn them into untouched confirmation studies, nor establish absent model pretraining exposure.
- Synthetic effect intervals are within-cohort analysis intervals. Between-output variation and structural scenario sensitivity are separate quantities. At most three scenarios do not cover all evidence-compatible joint distributions.
- An analysis can have a supplied point-estimate component and a reserved uncertainty component; a single coarse label must not hide this distinction.

## Audit scope and pending gate

The source review and amended Stage 1 protocol review are complete. `PROTOCOL_REVIEW.md` records PASS for builder launch on the `stage1_v3` freeze, backed by 62 source/contract checks and eight artificial guard checks. It also preserves the initial defects and their prelaunch resolution. Reserved target evaluation still requires the complete committed 21-arm final inventory.
