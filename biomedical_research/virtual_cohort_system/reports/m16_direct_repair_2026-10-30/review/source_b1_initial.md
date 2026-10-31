# B1 initial source and construction review

**PASS for source extraction, declared assumptions and pre-authoring construction.** No actual table, biological accuracy or target release is approved by this result. The reviewer did not read observed participant rows, generated rows or hidden measurements.

The three admitted original articles, their numerical tables and Yun's DOCX supplement/figures were inspected. Registered source hashes and contract evidence/specification validation passed. Two supplementary transparent PNG diagrams required white-background inspection copies in this review directory; originals were unchanged. Those inspection copies contain source figure content and must remain local, not enter Git exports.

`check_source_b1_initial.py` independently verifies 97 numerical evidence items against manually transcribed original values, including reported SDs. It checks all 33 planned source operators and 72 expression comparisons on invented age/BMI/group combinations. Results are in `check_source_b1_initial.json`. No fit, generator or target analysis was run.

## Findings

- Yun Table 2 adult means/SDs and subgroup counts match. The source-centered group anchors are approximate transport assumptions rather than claimed target means.
- Sun Table 1 moments and Table 2 age-adjusted BMI-on-urate slopes match in the original direction: WM1.38, WF2.59, BM1.29, BF2.14. The BMI model's footnote correctly excludes BMI as a covariate. No reciprocal-slope conversion is used.
- Yun main adult BMI-to-urate standardized path0.322, supplementary subgroup paths0.337/0.302/0.332/0.407, and alternative DBP/HTN paths0.323/0.378 are accurately extracted. Alternative downstream models are retained as same-cohort specification context, not independent confirmations.
- The approximate raw-SD conversion and missing smoking/alcohol transport assumptions are explicit. This does not prove that the transferred reduced-model slope equals the fully adjusted source path.
- Yun cohort-II baseline/follow-up mean/SD values match. The age guides use a heuristic subtraction of BMI-associated mean change; the builder explicitly states that period, selection and other changes prevent identification of a cross-sectional conditional age effect. Their sign and scale remain assumptions, not source estimates.
- Bonaccorsi values retain micromol/L units; pre/post urate225/239 with SD76 and BMI-urate Pearson correlations−0.013/0.345 match. No menopause status is inferred from age, no BMD regression is repurposed as an urate regression, and these values are not numerically pooled into the US target.
- The 40-BMI hinge, attenuated slope, deviation scales and literal-authoring distribution remain explicitly unestimated choices. The exact expression agrees with the readable group anchors, centers, age guides and scale guides. Interpretation is `working_guides`, not conditional moment truth.
- All33 source checks are retained: 20 approximate comparisons and13 not computable. Race/sex selections, units and operator direction match each cited item. Sun comparisons deliberately retain target ages20–56 rather than original19–54, and this mismatch is disclosed. Their differences cannot be interpreted as exact source-replay errors.
- Overlap of the two Bogalusa originals is explicitly recorded. Ferrara is independently recruited. Retrieval failures and unavailable CARDIA full text are not represented as inspected evidence.

## Nonblocking precision note

Yun subgroup evidence arrays repeat the overall study adjustment list including race and sex. This should be interpreted as the source's study-level adjustment description, not a claim that a constant subgroup-defining variable was an estimable regressor in each within-group fit. These effects are all marked not computable under the available X; no incorrect subgroup fit is submitted. Any manuscript-level description should state the applicable subgroup adjustment/standardization uncertainty explicitly.

## Bound scientific files

| File | SHA-256 |
|---|---|
| evidence.json | `197217345aa2d83b3990db46ca72e19f146eca0d556477f905d113d7f2132f08` |
| model_spec.json | `a3de2680f3ea1ef0deef03c766dd6870c09af1a07834eb901ebdab4b2419ae79` |
| audit/construction.json | `17dfd8e78b3bd437187bd9fa897d260640411b67a2ec5e68964ad2a3033a4bda` |
| audit/revision_plan.json | `f07b00714e8af33e8879b0179b22e63160431d2f1b87087bdd0ad362dfaf0cc9` |

These are the files reviewed before any output-row authorship was authorized. The review accepts transparent assumptions for testing; it does not endorse their target accuracy or give numerical target corrections.
