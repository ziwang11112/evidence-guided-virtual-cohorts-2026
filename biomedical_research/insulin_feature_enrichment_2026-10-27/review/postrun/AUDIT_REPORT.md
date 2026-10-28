# Independent postrun audit

Final follow-up: `POSTRUN_AUDIT.md` and `report_v3_checks.json` cover report_v3. Its endpoint roles resolve the labeling gap below; `RESULTS.md` resolves the transformed-median definition. All previously audited numerical cells, correlations and the PNG remain unchanged. The findings below retain their original v2 audit context.

28 October 2026 UTC. The final presentation audited is `results/report_v2/`; `report_v1/` is retained as a superseded layout. This audit read the reserved reference only after the output freeze and evaluated release. It did not import or execute the generator, evaluator, or presentation script, regenerate any column, alter frozen files, or write outside `review/postrun/`.

**Numerical integrity passes. No blocking computational, source-extraction, or generator-code defect was found.** All 84 weighted model fits, their full survey covariance matrices, all 168 endpoint records, and every released aggregate table and correlation reproduce independently. Two presentation clarifications should accompany interpretation: explicit endpoint roles, and the definition of the exponentiated median statistic. Neither requires changing the frozen results.

## Commitments and accounting

The supplied output-freeze SHA256 is unchanged:

`aee9d3b44df52b59a754cdcfd88629eddf414f4e8b2c7e23c4ce102ba271f4c4`

The audit checked **192 local file commitments across 98 distinct files**, including nested custodian/source manifests, raw source files and downloaded documentation, pre-execution inputs, model and evidence files, approved literature artifacts, reviewer specification/code, adapted reference/spine, and every generated CSV. All match. The original failed parser's pre-read commitment is checked against the preserved initial parser file; its documented repair has a separate frozen file commitment. Thus the old commitment was not silently treated as a hash of the repaired code.

The 20 scheduled seeds are exactly 270101–270120 in pre-execution, execution, and evaluation records, paired with draws 1–20. There is one scheduled construction, 20 saved output files and 20 distinct output vectors. Each output has exactly 1,700 rows, preserves the input row order and all observed numerical values, and appends only the insulin column. Every output concentration is positive and finite. The reference adapter preserves the original `insulin_uU_mL` values, and the schema/generator use uU/mL (microIU/mL). This verifies representation and declared units, not physical measurement accuracy or cross-assay calibration.

The exact observed predictor fingerprint reproduces. The spline knots, contrast locations and predictor centers also reproduce solely from the visible input. The analysis uses 1,700 target-domain records and all 2,711 positive-weight design records, including 1,011 outside the domain. Thirty stratum–PSU pairs across 15 strata yield design degrees of freedom 15 and residual degrees of freedom 14, 12, 11 and 11 for models A–D.

The evaluation contains 8 reference endpoints and 160 generated endpoints, totaling 168. All eight endpoint identities appear once per dataset; all 20 draws appear in every endpoint summary. The single saved evaluation directory and matching commitments support the stated run accounting; they are not a tamper-proof counter of every possible historical process execution.

## Independent numerical reconstruction

The standalone audit implementation is `independent_audit.py`. It does not call the released evaluator's functions. It obtains weighted coefficients by QR decomposition of the square-root-weighted design matrix, instead of the evaluator's normal-equation solve. It uses the original, unnormalized weights. For every fit it independently constructs estimating-equation influence vectors, allocates an explicit zero vector to each out-of-domain record, and sums the full-record influences by nested stratum and PSU.

Within each stratum, covariance is accumulated from every pair of PSU totals, using `sum_{j<k}(T_j-T_k)(T_j-T_k)'/(m-1)`. This independently implements the identity equivalent to `m/(m-1)` times the sum of centered PSU outer products. Full-spine membership determines the PSU counts and degrees of freedom. A separate artificial case with two target PSUs and two entirely out-of-domain PSUs verifies the nontrivial zero-domain covariance and full design degrees of freedom. This matters even though the real domain retains the survey's PSU support.

The restricted cubic spline is evaluated using a divided-difference representation. The upper-minus-lower secant-slope contrast is rebuilt from the three frozen BMI locations and expressed per five BMI units. Sex slope contrasts, Student-t intervals, exponentiated intervals and signed/absolute differences are then reconstructed. Weighted correlations use a separate weighted covariance implementation. All 21 datasets were checked, including the first, middle and last generated draws; this exceeds the requested representative-draw minimum.

| Quantity compared | Largest absolute discrepancy |
| --- | ---: |
| Model coefficients, all 84 fits | 1.13 × 10^-14 |
| Full Taylor covariance matrices | 9.58 × 10^-17 |
| Endpoint estimates, SEs, intervals and exponentiations | 1.15 × 10^-14 |
| Endpoint CSV numeric entries | 1.15 × 10^-14 |
| Draw summaries and presentation table | 7.63 × 10^-15 |
| Weighted correlations | 2.78 × 10^-16 |

These are floating-point discrepancies, not scientific equivalence tolerances. The audit's 4,237 checks pass. `audit_results.json` records each check, every retained-file commitment and a digest snapshot of the evaluated/presented results. `independently_recomputed_endpoints.csv` contains aggregate endpoint calculations only.

The presentation's mean, SD, range, signed/absolute differences, log-effect medians, exponentiated summaries, interval-state counts, and correlation summaries reproduce. All eight Markdown rows match their correct rounding. Numerical/text files in reports v1 and v2 are byte-identical. Visual inspection of the v2 PNG confirms all eight rows, readable labels, and distinct legends for reference survey intervals versus generated draw ranges.

## Source and claim qualifications

`SOURCE_ROLE_AUDIT.md` records the separate source/role review. All six evidence-source hashes match, and the three sources supplying numerical parameters describe Brazilian, German and Indian populations rather than NHANES. The transcription and arithmetic behind the BMI contrast, log SD and older-age anchor reproduce. The source-to-conditional-model conversions remain explicit assumptions. Matching nominal concentration units does not identify an assay-calibrated target measurement model.

Static inspection shows no file, network, subprocess, dynamic-code or target-data reads in the frozen generator. The inspected controller supplies the visible input, model specification and fixed seeds and checks the output contract; it does not impose a target-fitted biological relationship. The recorded construction supplies evidence for no target-informed numerical revision and no root target tuning. Shared-filesystem access, model pretraining and unlogged historical actions cannot be ruled out by final artifacts alone. The disclosed prohibited-snippet attempt and subsequent fresh construction must remain visible.

Two report clarifications remain:

1. The protocol requests an explicit role label for each analysis. The final interpretation should use the eight-row mapping in `SOURCE_ROLE_AUDIT.md`. Overall BMI direction is already encoded from Agent-selected external evidence; adjusted BMI and subgroup magnitudes are transport questions under an imposed common slope. Age borrows a constructed age function, while sex, curvature and interaction analyses challenge explicit structural assumptions. Generic statements about “reserved analyses” do not replace these labels. The clean request supplied no biological coefficient or desired result, so “supplied literature relationships” should not imply that the root supplied a target relationship.
2. CSV field `generated_median_ratio` means **the exponential of the median log estimate**. With 20 draws, it is not identically NumPy's arithmetic median of the 20 individual ratios. The largest difference is approximately 4.04 × 10^-6. The reported value correctly implements a transformed log-scale summary; use the explicit definition in prose rather than claiming it is the arithmetic median of ratios. No frozen numerical correction is requested.

This audit verifies the frozen scientific calculations and their provenance, not the validity of unmodeled transport assumptions. Synthetic survey intervals remain conditional on generated outcomes; repeated residual draws do not incorporate all source, model or transport uncertainty. Original survey weights do not automatically remove complete-case outcome selection. No per-person accuracy, causal discovery, equivalence, independent replication or recruitment-savings claim follows from a passing computational audit.

No result-driven fix, source substitution, new generation or retrospective pass threshold was made or recommended.
