# Initial source and generator review

The inspected implementation has no identified blocking extraction, unit-conversion, or coding defect. No numerical or structural model revision is required before execution. It can be executed as an explicitly assumption-dependent external-evidence simulation pilot; it should not be described as a fitted conditional prediction model or a calibrated imputation procedure. The final evidence ledger, initial decision, and search record were reviewed and are consistent with the source values and model roles, subject to the two documentation clarifications below.

This review used the six approved primary fulltexts, `agent_clean/initial/generator.py`, `agent_clean/initial/model_spec.json`, `agent_clean/EVIDENCE_LEDGER.json`, `agent_clean/INITIAL_DECISION.md`, and `agent_clean/SEARCH_LOG.md`. Dynamic verification used six artificial rows. No reference outcomes, survey spine, evaluation results, or earlier project outcomes were inspected. The review contains no evaluator formulas or recommendations derived from them.

## Source extraction and arithmetic

| Item | Check | Assessment |
| --- | --- | --- |
| S1 age anchors | Table 2 reports insulin medians 7.25, 6.28, 6.03, and 6.37 microU/mL for ages 20–29, 30–39, 40–49, and 50–60, with corresponding BMI medians 22.58, 22.83, 23.01, and 23.07. | Correct transcription. These are marginal medians, as documented by A1. |
| S2 older-age factor | Table 1 fasting-insulin P50 values are 42.1 pmol/L for ages 24–59 and 47.0 pmol/L for ages 60–80. | Correct values and dimensionless ratio. Multiplying 6.37 by 47/42.1 gives 7.111401425178147. Treating this as an older-age adjustment is assumption A2, not an estimated conditional coefficient. |
| S3 groups | Table 1 non-DM groups have n=307 and 168; mean BMI 21.07 and 28.96; mean insulin 4.29 and 6.05 microU/mL; reported insulin SE 0.16 and 0.37. | Correct columns and units. The paper distinguishes this descriptive Table 1 from the adjusted Table 2. |
| S3 BMI contrast | log(6.05/4.29)/(28.96−21.07). | Recomputes to 0.04357053727538965. This is a between-group contrast, not an individual-level fitted slope. |
| S3 dispersion | Convert SE to SD using each group's sample size, moment-match lognormal variance, then pool log variances with n−1 weights. | Arithmetic is correct: group log SDs 0.5963212737377662 and 0.6982603762701631; pooled 0.6341865562510045. Source SE was not confused with SD. |
| S4 contextual effects | Framingham Table 3 fasting-insulin male-sex coefficients differ across adjustment models and are coefficients on standardized log insulin; longitudinal results differ from these cross-sectional estimates. | Appropriate as contextual evidence. No standardized coefficient was incorrectly inserted as a raw log effect. |
| S5 mediation study | The MILES study estimates delivery-mode effects and their BMI mediation. | Correctly excluded from direct numerical BMI-slope extraction. A mediated percentage is not a BMI coefficient. |
| S6 external contrast | UVA Table 1 reports lean healthy and class-I-obesity fasting insulin means, with SEM; T1D basal insulin is not reported as an endogenous comparison. | Appropriate as context only. The inspected model imports no numerical parameter from this table. |

The insulin units microU/mL, microIU/mL, and mU/L have matching numerical concentration scales here. S2 contributes a within-unit ratio, so no pmol/L conversion is needed for its use. The selected papers used different assays and sample matrices; this unit agreement does not establish laboratory calibration agreement.

Primary sources: [S1, Brazilian reference intervals](https://pmc.ncbi.nlm.nih.gov/articles/PMC11554367/), [S2, lifespan reference values](https://pmc.ncbi.nlm.nih.gov/articles/PMC10350850/), [S3, nonobese and obese groups](https://pmc.ncbi.nlm.nih.gov/articles/PMC6887811/), [S4, Framingham correlates](https://pmc.ncbi.nlm.nih.gov/articles/PMC8862500/), [S5, MILES mediation](https://pmc.ncbi.nlm.nih.gov/articles/PMC9165426/), and [S6, UVA metabolic/microvascular responses](https://pmc.ncbi.nlm.nih.gov/articles/PMC8169863/).

## Scientific assumptions that remain material

These are limitations of the proposed construction, not extraction defects that can be repaired by substituting a known correct coefficient:

- Marginal median insulin and marginal median BMI do not identify insulin's conditional median at that BMI. Interpolation through the paired S1 summaries is a modeling choice.
- S1 selected adults with BMI from 18.5 to below 25, excluded adverse metabolic measurements and relevant medication use, and removed outliers. Its sample was 86% women. Its location anchors therefore need substantial transport assumptions outside that selected population.
- The older-age factor combines separate reference populations and an age-band ratio. It does not isolate age from BMI, health selection, medication, or assay differences.
- The single between-group S3 contrast does not determine the individual response function throughout the full BMI range. Applying it to conditional medians assumes equal log variance even though the source groups imply different marginal log variances. The specification states this explicitly.
- The pooled spread is marginal within broad BMI groups, not a residual standard deviation conditional on all supplied predictors. Reusing it as conditional noise may overstate some residual variation, while omitted diseases or transport shifts could produce other discrepancies. The direction and extent of total mismatch cannot be established from these summaries.
- Common reference intervals by sex do not establish a zero conditional sex effect. The zero coefficient is correctly disclosed as a pragmatic assumption, rather than a source estimate.
- Serum Roche measurements, plasma ELISA measurements, and the documented target assay are not automatically interchangeable. No approved source identifies a correction factor for this transport. Neither an invented correction nor a target-informed adjustment would be justified.
- Independent normal residuals on the log scale and fixed parameters do not reproduce source sampling uncertainty, model uncertainty, transport uncertainty, or cluster dependence. Twenty seeds remain draws from one construction, not twenty independently supported models.

The model specification already states these limitations in A1–A9. Their presence alone does not require replacing the model before this pilot. Any claim of calibrated prediction, proper multiple-imputation coverage, or a fully evidence-identified conditional distribution would require stronger evidence than is currently provided.

## Documentation clarifications

1. **Source locator only:** S2's age60–80 fasting-insulin values appear at approved-text lines674–684. The ledger's locator606–672 for that entry excludes those rows. The values themselves are correct; correct the locator without changing the model.
2. **Measurement interpretation:** The phrase “latent positive concentrations” could imply an identified latent physiological distribution. The sources provide measured assay summaries, and the model contains no measurement-error decomposition. More precisely, these are simulated positive concentrations on borrowed source assay scales, without an explicit target-assay or low-value censoring model. Evaluation against released assay measurements therefore mixes distribution-transport error and measurement-model mismatch. This calls for clear wording, not an invented assay correction or a target-informed change.

## Implementation checks

All 36 checks in `initial_source_code_checks.json` passed, including ledger-to-approved-source file hashes. The reproducible audit is `check_initial_generator.py`. The two documentation findings are reported separately from passing numerical and contract checks.

- Full source review and AST screening found no file/network I/O or dynamic execution in the generator; imports are NumPy and pandas plus future annotations. This is a procedural review, not a security sandbox.
- The documented equation exactly reproduced toy outputs using the same seed. There was no extra scale conversion, clipping, sign correction, or hidden calibration step.
- Observed values, row order, and evidence dictionaries were unchanged; the returned table adds only insulin. Same-seed calls were identical and a different seed changed the simulated column.
- Import and generation left NumPy's legacy global RNG state unchanged. The generator uses a local `default_rng` instance.
- Outputs were finite and positive on the toy domain. Invalid BMI, invalid sex, unsupported age, missing predictors, and duplicate row IDs were rejected in the exercised cases. The root runner supplies the remaining schema/row-key and CSV round-trip checks.

Reviewed generator SHA256: `226a0b528041c36fef4233443b1b00ca3a9ccb6d2a35d810f85a7742374b1ab0`.

Reviewed model specification SHA256: `28e1b6fa6863214891556fc49d222759de835a5e518ef64f6980abe752377589`.

Recommendation: retain the initial construction for this transparent pilot and clarify the documentation as described above. Do not revise it merely to impose an expected biological pattern or to make a future evaluation look better. Any source-grounded numerical revision should be versioned and justified before target results are opened. No such numerical revision is indicated by this review.
