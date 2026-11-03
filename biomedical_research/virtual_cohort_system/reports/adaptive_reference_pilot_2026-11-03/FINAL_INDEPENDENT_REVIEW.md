# Final independent review — adaptive CHNS reference pilot

**Conclusion:** The nine recorded executions, their feedback, and the final reporting have no identified unresolved implementation or arithmetic blocker. The pilot is complete as a bounded, explicitly reference-assisted development record. This conclusion does not certify independent target validity, statistical equivalence, clinical utility, population recovery, or publication readiness.

This report supersedes the pending-delivery statements in the earlier chronological implementation review. The reviewer authored no scientific generator or parameters, ran no generator, produced no synthetic table, and read no raw participant records. The reviewer read already generated synthetic CSVs locally for independent aggregate analysis. No patient-level or synthetic-row export was performed by the reviewer.

## What was independently checked

| Check | Observed result |
|---|---|
| Execution budget | 9 of 10 slots: 2 initial trials, 1 revision trial, 3 initial deliveries, 3 final deliveries |
| Execution outcomes | 9 successes; no failed generator attempts; one allowed trial slot deliberately unused |
| Output size | 3,000 rows per table; 27,000 row instances across all recorded outputs |
| Independent calculations | All 270 run-statistic values, compared with both recorded calculators: 540 value comparisons |
| Arithmetic mismatches | 0 at absolute/relative tolerance 1e-10, used solely for implementation agreement |
| Paired comparisons | All 30 statistics for each of the 3 prescribed initial/final seed pairs |
| Report summaries | All 180 delivery statistic values, 90 paired changes and 240 summary entries checked independently |
| Table identity | 9 distinct CSV hashes and 9 distinct measurement-multiset hashes |
| Within-table quality | 3,000 unique IDs per output; no complete duplicate measurement rows; no nonpositive glucose/HbA1c |
| Feedback engine | `semantic_feedback_v1` used explicitly throughout; no legacy fallback |
| Closing workflow | Same-author initial and final handbacks recorded; final decision and freeze precede every final delivery |

Same delivery seeds reuse synthetic row identifiers across initial and final versions. The 27,000 row instances are not 27,000 independent people or clinical observations. The three final draws are not new biomedical evidence.

The independent auditor uses the standard CSV reader, `statistics.fmean/stdev`, explicit sorted linear interpolation, independently implemented average ranks and centered correlations, and SciPy pivoted QR for regression. It imports neither the scientific generator, the primary evaluator, nor the cohort harness. It verifies the session bindings/event chain, successful execution identity, output hashes and feedback bindings before comparing arithmetic. Its machine-readable report is [INDEPENDENT_RECOMPUTE_CLOSED.json](D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work/adaptive_reference_pilot_2026-11-03/INDEPENDENT_RECOMPUTE_CLOSED.json).

## Actual scientific result and trade-offs

The final change reduced the initial excess rank association on all three paired seeds. Other discrepancies were retained. The final sample coefficients remain estimates from generated rows under a model fitted to exposed CHNS aggregates.

| Seed | Initial Spearman | Final Spearman | Exposed reference |
|---|---:|---:|---:|
| 3101 | 0.41604442 | 0.34838453 | 0.36145732 |
| 3102 | 0.41284221 | 0.34447726 | 0.36145732 |
| 3103 | 0.43812381 | 0.37438012 | 0.36145732 |

| Statistic | Initial mean absolute reference discrepancy | Final mean absolute reference discrepancy |
|---|---:|---:|
| E1: BMI coefficient | 0.00516415 | 0.00526505 |
| E2: glucose coefficient | 0.02306085 | 0.02350731 |
| E3: age coefficient | 0.00031031 | 0.00033201 |
| Pearson correlation | 0.03614475 | 0.03589318 |
| Spearman correlation | 0.06087950 | 0.01432522 |
| HbA1c SD | 0.03700528 | 0.03790917 |

All three regression mean absolute discrepancies increased slightly; E2's absolute discrepancy increased in every paired seed. HbA1c SD also had a slightly larger average absolute discrepancy. The Spearman improvement is a specific development result, not global scientific improvement. No composite accuracy score, post-hoc equivalence margin, favorable-seed exclusion or significance claim was introduced.

Age, female, BMI and glucose values are unchanged within each paired seed because the generator and the corresponding random-number use remain unchanged. HbA1c dependence changes produce the small changes in regression/SD results. Complete values and differences for every statistic and seed are retained in [COMPLETE_RESULTS.json](D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work/adaptive_reference_pilot_2026-11-03/COMPLETE_RESULTS.json) and in the independent recomputation report. The reviewed summary and figure display the observed trade-offs and identify the reference as exposed development information. The figure is legible and its shaded intervals are correctly identified as reference coefficient intervals.

## Scientific change, internal sampling and provenance

The initial and final generator bytes are identical:

`05dad2abd52dd3abaf97f06fcecaee417f4f4772a89f85bc63d765422ac8025a`.

The only initial-to-final scientific parameter change is component copula correlations:

`[0.28, 0.5871524663503118]` → `[0.12, 0.6076353385661598]`.

The final generator and specification are byte-identical to the third trial's submission. Initial specification SHA256 is `c0fe73df932f657e32f8f2db75757698f0f92e438a0150b8f36ac1a0f8981d04`; final specification SHA256 is `ae4b0f8142890b1a2be638e272246912af45f4f39c34cd568ef55cd43db7b11e`. The scientific author declares this change; the coordinator reports no scientific code/specification edits. Byte inspection verifies the declared difference and retained execution inputs, not adversarial proof of authorship.

Static generator inspection found six primitive random arrays, each of length 3,000, on the same person positions. There is no oversampling/rejection loop, random integration cohort, hidden fitting table, or extra source-context output. Deterministic support grids and quadrature nodes in the mathematical scripts are not sampled people. The harness itself counts attempted tables and emitted rows; this particular static review supplies the additional internal-sampling evidence. It must not be generalized into a claim that the harness instruments arbitrary internal random rows.

The unchanged bounded construction has pre-rounding glucose support [2.2133316354, 25.3434581885] and HbA1c support [2.4881376894, 18.0302554800]. Rounding preserves positivity; age is supported on 35–74, BMI is clipped to 10–55, female is binary, and the copula correlations are admissible. Finite output moments follow. These bounds, mixture membership and rounding resolution are assumptions, not recovered reference extrema or clinical categories.

The new deterministic rank calculation has the correct shared-mixture and age conditioning, independent BMI integration, rounded mid-distribution ranks and discrete-rank variance identity. Its finite quadrature is approximate; 48/64-node agreement is not a certified error bound. The actual trial and final output results were kept separate from those expected numerical calculations.

## Actual author, freeze and feedback flow

The session binds `/root/adaptive_scientific_author` as its sole scientific author. It records two author phases, two delivery-feedback rounds and one explicit revision decision. The coordinator confirmed actual full initial feedback was sent before the matching handback and revision dispatch. The initial feedback's hash is:

`c98f183d8173b6f7360442086fc23f2a642901d42225f3af1f3085e154e808bc`.

The revision decision is event 0025; final freeze is event 0026; final attempts are events 0027, 0029 and 0031. The final freeze has revision index 1 and binds the initial delivery candidate as parent. The final candidate was therefore committed before seeing any paired final result.

Final feedback is event 0033 with SHA256:

`79d6300e6d37e399ad2b6b55d1d33d5d38c89f89f5f1cc45a20849e2d77053a5`.

The coordinator confirmed sending it to the same author as closing feedback with no further revision. Event 0034 records that identical feedback hash and recipient. This closes the requested actual feedback loop; the final outputs were not used for another model change. The session's final integrity verification also passed.

## Meaning of the reference and limits of approval

All 30 CHNS statistics were explicitly exposed construction inputs. The selected reference sample has n=6,631; generated n=3,000 is a design choice. The three coefficient intervals retain `CR1_t`, 218 groups and 217 degrees of freedom. Unknown estimator uncertainty for the other diagnostics remains unknown. Sample SDs are not treated as estimator SEs; synthetic seed variation is not evidence, model, structural or transport uncertainty. Interval membership is not equivalence.

The legacy `published_evidence`/`source_only` schema labels are interpreted by this task as all declared admitted inputs, including `CHNS_DEV_REF`. They do not establish an external-evidence-only experiment. External papers retain their own populations, measurements, adjustment sets and uncertainty and supply qualified context. No external source-population replay was performed; none is implied by internal reference feedback.

The construction assumes covariate independence, no female biomarker term, a particular latent mixture, bounded tails and measurement rounding. These assumptions do not support untested sex/subgroup effects, causal effects, clustered inference, tail-risk or clinical claims. The declared three regressions and distribution/joint diagnostics can be inspected under those model assumptions; successful arithmetic checks do not establish empirical adequacy for further uses.

Whole-cohort execution receives `observed=None`; there is no participant input table. The existing WSL/bubblewrap adapter isolates generator execution and has no local-generator fallback. That boundary does not sandbox the author's broader tools or sign files against hostile host alteration. The reviewer did not read raw records, did not alter old experiments and did not rerun old tests. No comprehensive certification of all historical filesystem bytes or author-side tool actions is claimed.

## Retained incidents

The first ar02 freeze failed before execution because of mixed text encoding. Its technical repair did not preserve an original before-hash and left mojibake in copied prose. That imperfect frozen artifact and the failed verification are retained in the updated encoding incident record; later author prose is corrected. This is not a failed generator attempt and did not consume a table slot. The scientific code and parameters were not part of that repair.

The first covariance solver ran inline and was retained in a later candidate. The provenance gap remains disclosed, rather than retroactively changing the frozen first candidate. The final candidate retains/hash-binds the mathematical scripts and their input/result artifacts.

The coordinator also disclosed that automatic approval review blocked deletion of two mocked-test temporary directories. They remain local and are excluded from the proposed export. This reviewer did not attempt deletion or certify cleanup.

The complete machine-readable review, artifact hashes, all 90 paired statistic changes, and scope qualifications are in [FINAL_INDEPENDENT_REVIEW.json](D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system/work/adaptive_reference_pilot_2026-11-03/FINAL_INDEPENDENT_REVIEW.json). No further generation or scientific revision is needed to close this bounded pilot.
