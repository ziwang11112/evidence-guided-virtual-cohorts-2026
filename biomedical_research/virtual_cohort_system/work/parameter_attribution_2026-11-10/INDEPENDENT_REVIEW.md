# Independent review of the attribution master

**PASS. No required correction remains.** This review independently checked the master against original frozen aggregates and prior recorded algebra. It did not read individual patient/generated records, run a generator/evaluator or assembler, modify frozen artifacts, or perform a new literature search.

The reviewer also authored the PNS detail audit earlier in this unit. This is an independent check of the assembly and numerical copying, not a second independent authentication of PNS primary sources.

| Check | Result |
|---|---|
| Coverage | 96 unique rows: 90 requested analyses + 6 supplementary marginal SD diagnostics. 30 constructions: 10 CHNS, 10 ENSANUT, 5 PNS, 3 Q5 lipid, 2 iron. |
| Main results | All 60 rows match original frozen RESULTS means, ranges, native units and complete reference/interval objects exactly. |
| PNS results | All 15 medians and ranges recomputed from the three retained-draw aggregate estimates match exactly; weighted references and interval endpoints match. |
| Lipid/iron results | All 21 generated means, ranges and reference values match the original 2026-11-08 audit. Recomputed means from its aggregate seed estimates also match exactly. |
| Theoretical results | 7 requested analyses + 6 SD diagnostics match existing algebra. The other 83 remain null. SD conversion is mmol/L × 38.67 = mg/dL. Null does not mean the requested analysis cannot run. |
| Detail pointers | All 96 resolve to the intended row. PNS and lipid/iron cited evidence files exist. |
| Markdown | All 96 rows, joined by their detail pointer, match JSON author, analysis/unit, mean/median, theory, range, reference and six-significant-digit rendering. |
| Hash bindings | 3 master inputs; 6 main manifests; 20 main freeze files; 80 model/generator/uptake/evidence files and their actual freeze commitments; 3 PNS source/results hashes all match. |
| Prediction fields | All 96 predicted errors and validated reliability classifications remain null. |

PNS literal residual parameters are A01 0.50, A02 **0.65**, A03 0.50, A04 0.55 and A05 0.55. They were checked at each original model-specification pointer. A02's generated median 0.644023 is a different quantity; it was not used to infer the declared parameter. Requested population projections and post-selection residual correlations remain uncomputed.

For the PNS descriptive comparison, the absolute difference between the mean of five author medians and the reference, divided by their sample SD (denominator 4), is **1.02238 / 5.11135 / 2.94896** for SBP / DBP / residual correlation. Using the median of author medians gives **1.28799 / 4.95360 / 3.33221**. Recalculation differs only by floating-point rounding (maximum 1.8e-15). These are noncalibrated descriptive ratios for five authors sharing a host and packet, not z statistics or estimates of bias against known population truth.

The main-study counterexample is also accurate: ENSANUT E0 A05 Q2 mean absolute discrepancy is 0.00795492196, below all five E1 values (0.02112779481–0.02718364134), while 5 of 6 overall information contrasts improve descriptively. E0 and E1 are different author groups, not paired revisions. The narrative correctly uses this to reject a universal accuracy guarantee; it does not rule out a future statistical relationship between provenance and accuracy.

The narrative separates source statistics, adopted parameters, whole-model implications, sampled output and empirical reference. Its evidence/assumption-card proposal is explicitly retrospective and requires a separately frozen prospective assessment before any prediction claim. The PNS sentence was tightened during review to say that the requested projection need not equal the declared coefficient and was not exactly derived here. That wording is consistent with the null theory fields. The previously missing STATE.json now exists; the root agent owns its final completion update.

The assembler was statically inspected and parsed, never executed by this reviewer. It reads the three detail audits, preserves the summary operators, converts the six SD theoretical values, writes the master JSON/Markdown, and checks count/null constraints. No generator imports or record-table reads occur in it.

## Evidence and limits

Original numerical anchors:

- [Frozen main RESULTS](../main_study_freeze_2026-11-03/final_evaluation/RESULTS.json): construction_summaries, references and agent_information_contrasts.
- [PNS RESULTS](../next_case_validation_2026-11-09/RESULTS.json): comparisons, reference_weighted and reference_row_resampling_stability.
- [Original lipid/iron audit](../analysis_use_diagnosis_2026-11-08/IRON_LIPID_AUDIT.json): analyses/observed_result and deterministic_checks_completed.

The prior PNS subaudit directly checked local INTERSALT BMJ1988 **p322, Table II and its adjustment footnote**, and selected text in local PMC9278591.txt. Those exact files and hashes are recorded in PNS_AUDIT.json/direct_original_verification. This master review does not authenticate every original paper. Main and lipid/iron source statements retain their prior extraction/audit basis. Hash agreement proves byte identity, not scientific truth or transportability.

The main HbA1c `%` units retain the frozen convention: percentage-point outcome differences per predictor increment, not relative percentage change. Marginal SD, residual Pearson correlation, pooled Spearman correlation and threshold OR remain distinct operators. The seven requested theoretical numbers and six SD numbers were checked against existing algebra, not newly derived here.

All audited file SHA256s, numerical anchors, check counts, resolved notes and boundaries are recorded in [INDEPENDENT_REVIEW.json](INDEPENDENT_REVIEW.json). The result supports accurate integration and bounded interpretation; it does not establish causal error allocation, clinical validity or predictive calibration.
