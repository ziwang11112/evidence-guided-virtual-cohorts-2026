# Independent postrun source and role audit

Final follow-up: report_v3 now contains all eight explicit role labels below and identifies them as postrun provenance-based labels. `POSTRUN_AUDIT.md` records the resolved reporting gap; the original v2 findings are retained below. No numerical result changed.

Audit date: 28 October 2026 UTC. Scope: frozen construction provenance, external source extraction, implementation roles, and scientific claim labels. The final presentation examined is `results/report_v2/`; `report_v1` was superseded for presentation layout only. No generation was executed, no model or data were altered, and no participant rows or identifiers are reproduced here. The separate numerical audit checks the released evaluation calculations.

**Finding: no blocking source-extraction or generator-code defect identified.** The parameter arithmetic reproduces, and the documented numerical sources are external to NHANES. The released presentation needs explicit endpoint-by-endpoint role labels to implement the protocol's requested distinction between evidence consistency, target-specific transport, and assumptions. This is a reporting gap, not grounds for changing the frozen simulation.

## Source provenance and arithmetic

All six fulltext SHA256 values in `agent_clean/EVIDENCE_LEDGER.json` match the local approved source files. A separate case-insensitive scan of those six texts found no literal NHANES or expanded survey-name occurrence. More substantively, the three parameterizing papers describe Brazilian laboratory users, German Leipzig cohorts, and Indian community volunteers. This supports external-source provenance; text screening cannot certify that an unnamed overlap is impossible.

| Source and use | Independently checked evidence | Assessment |
| --- | --- | --- |
| S1, Schrank et al., PMC11554367 | Main methods describe the Rio de Janeiro laboratory population, fasting requirement, Roche assay, and healthy normal-BMI exclusions. Table 2 contains age-bin insulin medians 7.25, 6.28, 6.03, 6.37 and BMI medians 22.58, 22.83, 23.01, 23.07. | Inputs are correctly transcribed. Treating paired marginal medians as an individual conditional median function is assumption A1. |
| S2, Hammel et al., PMC10350850 | Main methods describe the LIFE Adult Leipzig sample. Table 1 gives fasting-insulin medians 42.1 and 47.0 pmol/L for adult and older groups. | The dimensionless ratio is valid arithmetic. `6.37 * 47 / 42.1 = 7.111401425178147` matches the fifth anchor. Its conditional-age interpretation is assumption A2. |
| S3, Sarkar et al., PMC6887811 | Table 1 non-diabetic columns have sample sizes 307 and 168, BMI means 21.07 and 28.96, insulin means 4.29 and 6.05, and insulin SEM 0.16 and 0.37. Methods explicitly identify mean and standard error. | `log(6.05/4.29)/(28.96-21.07) = 0.04357053727538965` matches the BMI parameter. Converting SEM to SD, moment-matching lognormal variances, and pooling with sample-size-minus-one weights gives 0.6341865562510045. Neither quantity is an estimated conditional regression parameter from the source. |
| S4–S6 | Framingham correlates, MILES mediation, and UVA physiology papers are retained as context or documented nonuse. | None contributes a numerical coefficient to the executable model. No mediation percentage, partial correlation, standardized waist effect, or T1D insulin contrast was repurposed as a continuous BMI slope. |

The matching numerical concentration units do not establish assay calibration. The model borrows serum Roche scale, plasma ELISA spread and relative BMI contrast, and a German age ratio, without an identified Tosoh calibration. It assumes a lognormal distribution, constant conditional log SD, independent row noise, one common BMI slope, and no explicit sex effect or interaction. Source group spreads are marginal, not residual conditional variation. Those limitations are clearly disclosed in A1–A9.

Two initial documentation issues are already resolved by frozen addenda, without rewriting history: `SOURCE_LOCATOR_CORRECTION.json` points S2's older-age values to approved-text lines 674–684; `REVIEW_RESPONSE.md` replaces the interpretation of “latent positive concentrations” with simulated concentrations on borrowed assay scales without a target-assay or censoring model. Reports must use the corrected interpretation. The unchanged initial phrase alone must not be quoted as the final scientific claim.

## Separation of roles and limits of the evidence

The clean construction request gives the generation Agent the observed BMI/age/sex packet, eligibility and assay metadata, literature-access rules, output interface, and fixed seed schedule. It explicitly supplies no biological slope, correlation, subgroup effect, residual variance, or desired conclusion. The Agent selects the six substantive searches, three numerical sources, conditional model, transformations, and assumptions. The search record matches the relevant gateway audit entries; the neutral gateway test article is not a seventh model-evidence source. One substantive query was repeated to recover artifact metadata.

The generator imports only NumPy, pandas, and future annotations. Full source and AST inspection show no file/network I/O, subprocess invocation, dynamic execution, reference-data access, target summaries, clipping, or target fitting. Its scientific constants come from the supplied model specification. The controller reads that model and the visible covariates, enforces preservation/positivity, uses prescheduled seeds, and records hashes; its inspected code does not impose a scientific relationship or score outputs against the target. The source audit response requested documentation corrections only and retained the numerical model.

These artifacts support the narrow statements “no target reads in the frozen generator” and “no target-informed numerical adjustment is present in the recorded construction.” They do not prove that an Agent never encountered relevant knowledge before the task, that no unlogged file read was possible, or that the shared filesystem enforced isolation. The initial prohibited-snippet exposure and restart are disclosed in `review/INCIDENTS.md`; the entire exercise should not be called a pristine first attempt. No evidence of root numerical tuning was found in the inspected code and provenance, but absolute historical non-access cannot be inferred solely from final files and self-reported logs.

## Endpoint roles for final interpretation

The following labels distinguish the hidden target analysis from the information and restrictions already embodied in generation. “Reserved” means the target result was withheld; it does not make the synthetic relationship free of prior modeling assumptions.

| Endpoint | Appropriate role and qualification |
| --- | --- |
| Overall BMI association | External-evidence consistency plus target-specific magnitude transport. A positive BMI relation is built into the selected external-evidence model. Recovering its direction is not independent biological discovery. The exact overall coefficient also depends on the supplied covariate distribution and age model. |
| Adjusted BMI association | Reserved target-specific transport of an evidence-informed, explicitly imposed common BMI slope. Its magnitude is not a newly learned relationship from the synthetic column. |
| Adjusted age association | Reserved transport check of A1/A2's borrowed and interpolated age function. The evaluator's linear age coefficient summarizes that function and the observed covariate distribution; it is not a source-extracted adjusted-age effect. |
| Adjusted female–male contrast | Reserved challenge to A4's zero direct sex coefficient. A shared reference interval in a source does not identify a conditional null effect. |
| Upper–lower BMI slope contrast | Reserved challenge to A3's single linear conditional BMI slope. There is no evidence-estimated BMI curvature in generation. |
| Female–male BMI slope difference | Reserved challenge to A4's absence of a BMI-by-sex interaction. There is no evidence-estimated interaction in generation. |
| Male BMI slope | Reserved subgroup transport under the same imposed common BMI response; it is not an independently fitted male-specific response. |
| Female BMI slope | Reserved subgroup transport under the same imposed common BMI response; it is not an independently fitted female-specific response. |

The imposed zero sex/interaction terms and linear BMI form do not guarantee that the evaluator's sample projection coefficients or curvature contrasts equal exactly zero. Sampling noise, covariate dependence, and approximation of the generator's nonlinear age function by a linear evaluator age term can produce nonzero coefficients. Thus disagreement should be described as a failure of this complete construction to preserve the reserved analysis, without claiming that a nonzero result proves the generator secretly included that structure.

`report_v2/ALL_ANALYSES.md` correctly cautions against equivalence from matching signs, interprets intervals overlapping zero as unresolved rather than proof of null effects, and distinguishes repeated draws from independent studies. Its phrase “supplied literature relationships” is ambiguous about who supplied the biology: in this run, the clean request supplied no numerical biological relation, while Agent-selected external literature and the model did supply the BMI relation to generation. Prefer “relationships already encoded from the Agent-selected external evidence.” Explicit role labels such as the table above should accompany the final interpretation; generic caveats alone do not complete the protocol's requested per-analysis tagging.

No result-driven source replacement, parameter correction, new generation, or retrospective success threshold is justified by this audit. The fixed-parameter draws remain conditional simulation replicates and do not establish proper multiple-imputation uncertainty, target-assay calibration, causal identification, patient-level accuracy, independent biological discovery, or reduced recruitment requirements.
