# Independent M15-A post-run review

Reviewer: `/root/direct_pilot_admission`. Date: 2026-10-30.

**Verification passed. The table matches supplied marginal summaries fairly closely but underestimates all four withheld urate SDs. The explicit retain decision leaves initial and final results identical.** This is a source-only finding, not independent clinical validation.

## Independent numerical checks

The separate `independent_recompute.py` uses standard-library CSV parsing, `math.fsum`, and an explicit sample-SD formula with denominator n−1. Source references were transcribed from U1 Table 2 during the pre-run audit; the script does not import controller or harness calculation functions. It computed all 20 visible moments and four withheld SDs separately for both frozen candidates, checking observations, references, errors and aggregate summaries against the controller report. All 214 numerical comparisons passed at absolute tolerance 1e−10; maximum discrepancy was 7.11e−15. Audit numbers are saved in `postrun_audit_numbers.json`.

The 128 rows have the required columns, unique nonempty IDs, finite values, declared bounds and group counts 38/46/19/25. The visible joint mean absolute relative error is 1.098%; the separate averages are 1.119% for eight age moments, 1.626% for eight BMI moments, and effectively zero for four urate means. These are descriptive fitted-source discrepancies with no prespecified success threshold.

| Source group | Reported urate SD, mg/dL | Table urate SD, mg/dL | Relative shortfall |
|---|---:|---:|---:|
| White male | 1.3 | 0.857085 | 34.07% |
| White female | 1.2 | 0.984322 | 17.97% |
| Black male | 1.5 | 1.053565 | 29.76% |
| Black female | 1.7 | 1.082436 | 36.33% |

The four-SD mean absolute relative error is **29.533%**. All four deviations are in the direction of underdispersion. This illustrates that close agreement with supplied means does not establish recovery of omitted dispersion. It does not identify why the author chose these spreads or establish the behavior of direct LLM generation generally.

## Integrity, schedule and authorship

- All 20 precommitted task artifacts and 17 harness files retain their committed hashes, including the screened excerpt and archived source XML. The report binds the original precommit SHA256 `fdfa22abb8ea95158b21e240447e16f1ed9487fbc0a46baa1f576611c8a865ff`.
- Both candidate freezes and every listed commitment match. Final is the sole revision-index-1 child of initial, and its recorded revision kind is `retain`. CSV and model files are byte-identical across versions. CSV SHA256: `3e95264632fc2e9fd4e022147724b028c06c105eea753bee30eff4e435c915fb`.
- The feedback binds the frozen initial CSV and freeze receipt; final checks contain a byte-identical copy of that feedback. The budget receipt specifies one pass, and the controller event record contains one successful 20-moment feedback completion and one final evaluation completion. Recorded timestamps place feedback after initial freeze and evaluation after final freeze.
- Both execution receipts report success, `generator_executed: false`, backend `direct_rows_validation`, and byte-identical candidate/input/output CSVs. Every file hash listed in those receipts verifies. No generation program was executed through these receipts.
- The initial decision/model explicitly declare literal `apply_patch` authorship, chosen positive BMI–urate ordering, manual age pairings, artificial symmetry, coarse precision and assumed urate ranges. The parent reports observing the literal CSV tool submission and no sampling or row-generation code. This reviewer inspected the saved declarations and receipts, not a complete independent recording of every builder action. Neither these artifacts nor this audit can prove the internal LLM token-generation process or exclude remembered source information from pretraining.

## Interpretation and limits

The published SD holdouts come from the same source table as the fitted moments. Parent/controller knowledge and procedural rather than enforced builder isolation were disclosed before generation. Four source-summary comparisons are not four independent studies. The one retained table supplies no estimate of between-generation variability or evidence that feedback improves the method.

The builder's positive BMI–urate ordering is an explicit construction assumption. The report's regression, curvature, interaction and quartile outputs therefore describe this fictional table; they have no external relationship truth and support no clinical confidence intervals, p-values, causal interpretation or validation claim. This concise post-run audit did not independently recompute those optional exploratory analyses; it verified the requested 20 visible and four heldout statistics and their provenance.

No candidate, source packet, controller, historical artifact or real target file was modified. Only this review, the independent audit script and its numerical audit output were added. No new generation, revision, target access or feedback was performed.
