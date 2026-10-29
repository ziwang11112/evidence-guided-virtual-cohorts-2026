# M8 aggregate conclusion and chronology audit

**Disposition: PASS — no blocking findings.** All 49 scoped checks pass. The report's numerical conclusions and qualifications are supported by the retained aggregate results. This audit changes no report, candidate or evaluator code and performs no participant-data analysis.

The reviewed `MILESTONE_8_RESULTS.md` SHA-256 is `dba4129cecb27adfdf4e1748da8e8c63b8d4b1131dfc1f3dcfc46a3f848fa984`. Exact input hashes, numerical recalculations, checks and scope limits are in `POSTRUN_CONCLUSION_AUDIT.json`.

## Conclusions and numerical fidelity

- All 67 endpoints occur exactly once for each of two candidates and three target seeds: 402 comparison rows, with zero nonestimable records. Reference values and stored errors are consistent throughout; all 134 per-candidate endpoint summaries reproduce the rows.
- The priority estimates, reference 95% intervals, and three-draw means/ranges reproduce to the report's stated rounding. Both baseline and joint evidence match positive adjusted age association and negative log-BMI curvature, and all six points for each endpoint fall inside its reference interval.
- Age mean absolute error decreases from 0.0109142708 to 0.0066611866. Paired changes are −0.0065524461, +0.0003456397 and −0.0065524461: precisely two draws move closer. Log-BMI curvature error decreases by approximately 0.0003352993 in each pair.
- Both candidates already agree on all seven global and 24 ordered-contrast point directions. Exactly 16 of 24 ordered reference intervals exclude zero. The report correctly denies added directional success, excludes positive cell means/proportions from direction counting, and does not treat the 31 endpoints or three draws as independent replications.
- The subgroup arithmetic-mean absolute-error changes reproduce: men aged 60–79/BMI≥30, −16.8206144 mg/dL; women aged 60–79/BMI25–<30, +7.3299201 mg/dL; women aged 40–59/BMI≥30, +5.9682375 mg/dL. The excessive adjusted BMI effect and weak raw-scale curvature examples also reproduce.
- Raw mg/dL, log-TG curvature, geometric means and arithmetic means retain their stated scales. The report distinguishes marginal survey reference intervals from synthetic draw ranges and does not claim equivalence, calibrated synthetic uncertainty, causal validity, individual recovery, clinical replacement or ordinary-Agent superiority.

## Source feedback and recorded chronology

All 276 source check-runs are retained and finite. All 92 diagnostic summaries reproduce their seed values. The bound source review identifies 12 covariate-only and 34 outcome-related diagnostics; covariate equality is not counted as TG validation. The stated Bansal median/quantile improvements, worsening BMI rank association/reverse-conditional separation, and worsening Oh BMI-slope discrepancy are supported. The source review records no tuning or candidate revision and excludes target-result inspection. The new adjusted joint ratios remain outside the available execution-backed source replay operators.

Scoped protocol/evaluator anchors, the amendment, the release commitment and result hashes match. Initial/final candidate identifiers agree with the protocol, source portfolios and execution-path amendment. The amendment records 69 copied-input hashes and unchanged scientific parameters, seeds and endpoints. Pre-execution review precedes the path amendment/protocol commitment, which precedes the evaluation commitment and then the reference-release receipt. The release receipt records guard passage and validation of all generated outputs before reference parsing. Existing static-source and paired numerical review receipts support their narrowly stated claims. Original frozen evaluator files retain their recorded hashes.

## Audit boundary

Only the authorized report, README, aggregate endpoint CSV/JSON, source portfolios/review summaries, review JSON and protocol/evaluator metadata were read. No participant table, generated target row, hidden outcome CSV/XPT, full source context or source article was opened or byte-hashed. No generator, sandbox, scientific fit or evaluator was rerun. Copy-input equality, isolation and successful execution are supported by bound receipts, not independently re-executed here; the audit did not traverse forbidden row-file paths in those receipts.

No-target-tuning support is limited to unchanged frozen candidate identifiers, retained schedules, the source-review decision and release receipts. Hashes cannot prove the absence of unrecorded access. This preparer previously hardened the evaluator and disclosed incidental historical aggregate exposure; this review is independent of narrative drafting, not independent of all evaluator implementation. The report discloses that exposure and the temporal-holdout limitation.

## Draft-check correction

An initial literal-text check falsely flagged the uncertainty caveat because it searched for “not a synthetic uncertainty calibration”; the report says “nor a synthetic uncertainty calibration.” Substantive review confirmed the limitation was already explicit. No report change was needed. The prior draft state was reconstructed after it had been overwritten and retained in `POSTRUN_CONCLUSION_AUDIT_INITIAL_DRAFT.json`; the final JSON records that recovery method and exact correction.
