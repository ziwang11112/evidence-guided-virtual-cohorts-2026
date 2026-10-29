# Independent post-run audit

2026-10-29. **Passed for protocol execution, aggregate consistency, and the stated limited interpretation.** The independent audit recorded 99 checks and 129 hash comparisons with no failures. It read aggregate JSON/CSV, code, commitments, receipt metadata, and file hashes; it did not read generated source/probe row tables, patient rows, or invoke a generator. Details are in `review/POSTRUN_CHECKS.json` (SHA-256 `e1d63983b12e524e419588da6638f2d46d718e961943d3a8be27c664f0dfba61`). The audit script is `review/audit_aggregates.py`.

## Integrity and chronology

All files bound by the protocol commitment, harness-core hashes, runtime configuration, candidate freezes, and analysis artifact hashes remain unchanged. The independent pre-execution audit/status were not edited. Candidate freezes precede the protocol commitment. Every controller call returned zero; all nine source replay receipts contain successful, linked executions for both contexts, and all nine probe receipts identify the correct frozen candidate and seed.

The retained UTC sequence is protocol commitment 08:45:17.090247, first source execution 08:45:18.296080, source commitment 08:49:51.422055, source-gate-bound probe authorization 08:51:13.195785, first probe execution 08:51:13.196787, and complete output commitment 08:52:26.407719. The source commitment exposed no probe outputs. The probe authorization binds the successful source gate. No uncommitted redesign, threshold change, or scientific revision appears in the retained record.

Key SHA-256 bindings:

- Protocol commitment: `0990cd1bf0d0e4b4190e81a0a376012e9b69d376a625d0c493da0eef7886f1a1`.
- Source commitment: `ec3b3b17dddc1f23d8fa28e5b8439dd7b19650624ae998d60184ae2be48f6ac7`.
- Complete commitment: `e4026d7e1186f521b17a5b645e6d3343f303c97efbe9841d009cbdb21091fc86`.
- Source aggregate: `81084b0f60be510c07a55fdcf65431b6c8cc21ab6849d9ad2e9a811821f1fbbf`.
- Complete aggregate: `dc3e8b60f83cd247c0065b378cbf1ee4845fa51c8e73b21bc3722cd5e0e698e7`.

## Source screen and retained mismatches

The source aggregate has 414 unique statistic records: 46 checks by three candidates by three seeds. Recomputing from the separately retained portfolios reproduced the values, paired differences, paper discrepancies, thresholds, and pass flags. All 276 alternative-versus-zero comparisons passed. There are 24 nonzero paired changes and 252 exact diagnostic invariants. All 18 source input-preservation checks and all 12 paired row-invariant sets passed. Bansal and female outcomes remain exactly paired; the source 200/500 indicators remain unchanged.

The largest absolute paired change divided by its frozen limit is 0.391850, for plus/seed 78102/male TG below 150. The observed change is 0.000518303 against limit 0.001322707. This is a descriptive screen on a historical simulation scale. It is neither a joint statistical equivalence test nor acceptance by the clinical evidence.

All 360 Table 2 records are retained: 20 sex/age-or-BMI strata, two possible mean interpretations, three labels, and three seeds. The maximum perturbation-versus-zero drift is 0.0489103 mg/dL. Small paired drift does not repair the reference's source mismatch:

| Source summary | Zero replay mean across new seeds | Published value |
|---|---:|---:|
| Bansal TG Q25 | 76.6842 mg/dL | 81 mg/dL |
| Bansal median | 111.9335 mg/dL | 115 mg/dL |
| Bansal TG Q75 | 162.5669 mg/dL | 169 mg/dL |
| Bansal TG–age Spearman | 0.139669 | 0.18 |
| Oh male TG below 150 | 0.662601 | 0.684159 |

For Table 2, the largest zero discrepancy under the arithmetic interpretation is female highest-BMI stratum, seed 78101: 142.5584 versus 127.3 mg/dL. Under the geometric interpretation it is male highest-BMI stratum: 169.8922 versus 220.5 mg/dL. These are labeled alternative interpretations, not resolved source estimands; the implemented highest-BMI interval is >=30 while the printed label is >30. The three additionally adjusted/family/co-twin estimands remain unassessed. All nine replayed Table 3 BMI coefficients lie inside the reported interval, which remains a location diagnostic only.

The marginal contrast means are exactly zero using the declared rational source counts. The actual finite source table is not a product population: empirical mean(hA*hB) is 0.00005848724, predicting a plus-minus marginal mean drift of -0.000579482 mg/dL. The age–BMI correlation is -0.004380. Full-grid total-variation departure is 0.206898 and reflects fine-grid finite sparsity; it is not a clinical independence test. Exact pairwise-law invariance belongs to the declared product population, while this finite context demonstrates small retained departures.

The historical three-seed SDs are not stable uncertainty estimates. For example, the new zero BMI-coefficient seed SD is 0.098252 versus historical 0.012991 (7.56 times), and the new male TG-SD seed spread is 1.040306 versus 0.183557 (5.67 times). These differences do not change the frozen paired gate. They reinforce why neither historical nor new seed spread supplies a source-study SE, clinical confidence interval, or correctness probability.

## Synthetic probe

All nine fixed probe outputs are committed. The aggregate contains 63 regression records (seven endpoints by nine outputs), 36 block records (four blocks by nine outputs), and 24,840 unique cell aggregates (2,760 cells by nine outputs), each based on ten generated rows. The nine input-preservation and six paired-invariant sets pass. Independent recomputation from aggregates confirms paired changes, block differences, summary means, counts, and uniqueness. The complete analysis retains the source-phase arrays unchanged.

The analytic male-cell plus-minus conditional-mean gaps at (age,BMI)=(40,23), (40,27), (60,23), and (60,27) are -3.3749, +4.8249, +6.9303, and -9.9078 mg/dL. The prespecified MAX-over-four threshold is met; two cells exceed 5 mg/dL individually. These values were known before execution and are a construction criterion, not an empirical discovery.

The corresponding four male-block mean gaps average -3.2381, +4.8024, +7.0281, and -10.0308 mg/dL across the three paired draws. For the last block the draw range is -10.9246 to -8.9416 mg/dL. These are finite synthetic illustrations, not human-population intervals.

Broad synthetic projections move little. For example, the mean log-TG age-by-BMI coefficient is -0.0116681 for zero, -0.0116351 for minus, and -0.0117012 for plus. The experiment demonstrates localized conditional differences; it does not demonstrate a reversal or large change in the broad regression conclusions. The equally weighted synthetic grid is a chosen probe distribution, not a representative clinical cohort.

## Permitted conclusion and limits

The frozen diagnostic screen did not distinguish a deliberately constructed, locally different conditional density from its source-conditioned reference under the stated reconstruction. This is a constructive ambiguity demonstration with an imperfect anchor. It is not evidence that either alternative fits all published results, that the original source covariates were independent, or that the piecewise interaction is biologically plausible. The checkerboard-style age/BMI perturbation is a planned stress case, not an established mechanism. No new independent clinical target was evaluated, and no clinical recovery, causal validity, measurement saving, or publication-ready inferential claim follows.

The source operator limitations did not remove evidence: both Table 2 interpretations and the unavailable estimands remain visible. Conditional-law difference and source-screen passage must be reported together with the absolute source mismatches, rather than summarized as successful source compatibility.

The reviewer continuation retains the earlier disclosed accidental exposure to unrelated completed-agent target summaries from a general agent inventory. No linked historical files or patient rows were opened and no scientific choice used those summaries. The design/gate review and independent algebra preceded that exposure; subsequent review was mechanical. Perfect outcome blinding is not claimed for the reviewer continuation.

## Final narrative review

The final `MILESTONE_6_RESULTS.md` and current README v0.6 M6 description agree with the audited aggregate results and limits. They retain the 276/252 comparison counts, all 63/36/24,840 probe records, the signed block results, the known pre-run analytic separation, the unchanged broad age/log-curvature directions, the imperfect source fit, and the lack of independent clinical validation. The report identifies the piecewise interaction as a constructive stress case rather than biological evidence, distinguishes the synthetic-grid raw-curvature result from the earlier real-cohort analysis, and includes the 7.56-fold/5.67-fold changes in three-draw reference SDs without changing the gate. No further M6 narrative correction is needed.

This review did not independently reevaluate earlier milestone results referenced as background. It covers the M6 findings and current M6 README description, with the whole-file hashes below identifying the exact reviewed document versions:

- `MILESTONE_6_RESULTS.md`: SHA-256 `1beea79e4786a0dab25c04d695bbf155f23f78f2c8405365fa2d455f51f508ce`.
- `README.md`: SHA-256 `b4a9092835d3ec76f4a62df1dd4986b0a5fba2a31f9abfa85be77fff4c2a7326`.

The numerical, receipt, and final M6 narrative audit is complete. The earlier frozen pre-execution files remain unchanged.
