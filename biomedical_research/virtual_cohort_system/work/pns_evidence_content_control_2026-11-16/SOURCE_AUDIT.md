# Same-publication content audit

16 November 2026. Reuses the cached original XML of the Burkina Faso study, PMC12185928, DOI 10.1136/bmjopen-2024-089374. No new paper download or target measurement read. The previous PNS source audit is retained unchanged.

Original T1 reports N=2,114, women 826 and men 1,288, total mean age 51.7 years. Original T2 total-sample columns give SBP mean/SD 125.22/18.22 mmHg, DBP 80.54/10.98 mmHg and BMI 22.10/3.90 kg/m². Only those total columns are admitted to the SUMMARY increment. The full sex-specific columns and hypertension categories are not included.

T3 contains the six raw Pearson coefficients for the common SBP/DBP/age/BMI block: SBP–DBP .78, SBP–age .21, DBP–age .02, SBP–BMI .12, DBP–BMI .16, age–BMI −.17. They are added only in JOINT. The XML extraction keeps original table/row/column strings in an audit artifact outside the constructor prompts. The reported block is checked for symmetry, valid diagonal and positive definiteness. It can support a within-source linear age/BMI residual derivation; it does not identify the target age/sex/BMI residual relation. The root's previously derived .788 is not provided to any constructor in this pilot.

Both augmented conditions share the same provenance and context: rural partnered adults aged at least 40 in the 2018 CRSN Heidelberg Aging Study; pregnant participants and recent BP-medication users excluded; specified missing/outlier exclusions; seated Omron measurement after rest, using the last two of three readings; no inspected survey weighting. PNS includes younger adults and treated people, uses a differently defined weighted analytical distribution, and has incompletely matched measurement aggregation. These differences remain visible. Source rounding is not a sampling/transport uncertainty interval.

No cell in the SUMMARY increment gives an outcome-outcome relationship, sex-specific outcome mean, joint threshold prevalence, derived residual correlation, covariance or variance of an outcome difference. Thus no additional numerical covariance can be algebraically reconstructed from those added marginals alone. The unchanged *base* packet may still inform dependence, and the model may use prior knowledge; this is not a conditional-independence requirement.

The new constructor packets are derived by an explicit allowlist, not by deleting only a visible correlation cell from the old augmented JSON. All contextual prose in the two new source cards is common, and the source IDs do not reveal an expected target relation. This is an audit of information supplied, not proof that the LLM has never encountered the source in training.

Original source: https://pmc.ncbi.nlm.nih.gov/articles/PMC12185928/ . Earlier audit: ../pns_joint_evidence_2026-11-16/SOURCE_AUDIT.md. Root performed this extraction/control audit; no blinded external human source review is claimed.
