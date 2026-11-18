# Source admission audit — 16 November 2026

The actual search Agent completed 37 API calls, 14 Europe PMC queries and six full-text downloads (USD 0.4059768 at the recorded tariff). Its report is an admission proposal, not a target answer. The root reviewed the original cached methods and tables separately from that report. This is root-led checking, not a second blinded human review.

## Admitted evidence

**BF_AGE_BMI_JOINT — BMJ Open, DOI 10.1136/bmjopen-2024-089374, PMC12185928.** Methods and Results establish a common complete-case sample of 2,114 partnered adults aged at least 40 in rural Burkina Faso (CRSN Heidelberg Aging Study, 2018), excluding recent antihypertensive use and pregnancy. Tables 1–3 provide sample composition, untransformed BP sample SDs and a Pearson correlation matrix. BP is the average of the last two of three seated Omron measurements. No survey weighting is specified for these calculations. The table entries match the Agent's extraction. Schur-complement calculation from the same-sample age/BMI block is legitimate for a linear projection, without assuming Gaussianity. The separately recomputed values are saved in `inputs/source_derivation_check.json`.

This derivation does **not** adjust for sex. Sex-specific means alone do not complete the required covariance block because age SD and age–sex correlation are missing. It also does not identify a conditional nonlinear distribution. Rounded source correlations provide approximate point constraints, not sampling or transport intervals. The source is admitted as a partial joint constraint; target transfer remains an assumption.

**GHANA_MULTILEVEL_JOINT — PLOS Global Public Health, DOI 10.1371/journal.pgph.0001613, PMC10132648.** Methods and Tables 3–4 describe women aged 15–49 in the 2014 Ghana DHS, with categorical age, binary obesity and several household/lifestyle covariates. The model has paired household random intercepts and paired individual errors. Table 4 gives individual variances 224.49 and 101.75 mmHg² with residual correlation 0.73, and household variances 38.91 and 16.37 mmHg² with correlation 0.81. These are not the requested single-level age/sex/continuous-BMI residual correlation. Table 4's individual-level column is mislabeled “Child”; the methods, equations and narrative identify individual women. The abstract/methods household counts disagree (3,722/3,727). No component CI/SE is given. Detailed BP acquisition and explicit survey-weight fitting are not established by the inspected article. Some prose labels linear coefficients as ORs; no such coefficient is imported as an odds ratio or a target slope.

Admit these as secondary multilevel joint evidence, preserving these limitations. Do not silently sum or average the two correlations, treat the variances as SDs, or pool this estimate with Burkina Faso under a common estimand.

## Withheld from the augmented generator packet

**Uganda — DOI 10.1371/journal.pgph.0003707, PMC11392332.** Root inspection of the methods, Results section and Table 2 confirms the Agent's caution: 0.7307 is described both as an outcome correlation before modeling and as the residual correlation. Table 2 omits sex and uses BMI categories plus other risk factors; treatment users were excluded. The paper therefore does not unambiguously supply the desired operator. Preserve it in the search record rather than presenting it as an additional interchangeable constraint. This exclusion is based on reporting/definition ambiguity, not closeness to PNS.

The other three screened articles remain in the Agent report with the actual inspection boundaries. Their underlying data, supplements and full methods were not independently reanalyzed. No exact target-adjustment source was found. No new patient records were accessed.

## Information boundary and interpretation

Sources were chosen for available joint information, source measurement and statistical definitions before any new output or target comparison. All are separate study families from PNS and the existing packet; lack of indicated overlap is not person-level linkage verification. The target case was already exposed historically and remains developmental. The new Agent sees neither target estimates nor historical model outputs. The root does not prescribe a residual correlation, slope, distribution or transport weight. Reuse of the original packet preserves its historical extraction status; this unit does not reauthenticate every old source.

The two new records are useful enough for the predeclared small generation comparison, despite not identifying the exact target joint law. Their presence may improve, worsen or leave results unchanged. A source review can validate extraction and algebra; it cannot certify transport to Brazil.

Primary source links: [Burkina Faso](https://pmc.ncbi.nlm.nih.gov/articles/PMC12185928/), [Ghana](https://pmc.ncbi.nlm.nih.gov/articles/PMC10132648/), [Uganda](https://pmc.ncbi.nlm.nih.gov/articles/PMC11392332/).
