# Source-method audit: Turkana lifestyle application

11 November 2026. Scope: original-study methods and published aggregate evidence, plus a code-only check of the released lifestyle labels. No participant outcome values, group counts, means, contrasts or associations were inspected or calculated by this audit.

## Primary material

- Lea et al. (2020), DOI [10.1126/sciadv.abb1430](https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/). Exact locators: Materials and Methods, "Data filtering and processing" and "Testing for lifestyle effects on measured biomarkers" (models 1–2); Figure 2A; Tables 1–2.
- [Original supplementary methods](https://gurven.anth.ucsb.edu/sites/default/files/sitefiles/papers/lea%20et%20al.%202020%20supplement.pdf), PDF pp. 3–8, especially measurement and lifestyle definitions.
- Original supplement Table S2A is linked [here](https://pmc.ncbi.nlm.nih.gov/articles/instance/7577730/bin/abb1430_Table_S2.xlsx); Table S1 [here](https://pmc.ncbi.nlm.nih.gov/articles/instance/7577730/bin/abb1430_Table_S1.xlsx). Download verification is recorded separately. A file returning an HTML page is not a recovered workbook.

## Verified analysis definition

The paper standardizes each biomarker with R `scale`, fits lifestyle + age + sex, then tests a lifestyle-by-sex interaction by a likelihood-ratio comparison. Its stated branch threshold is nominal p<0.05; interaction findings lead to sex-specific age-adjusted models. BMI, TC and HDL are not the reported female-only exceptions. Figure 2A displays three pairwise lifestyle contrasts in outcome-SD units. The published multiple-testing analysis spans 11 outcomes, including a composite.

The sources do not settle whether the three pairwise contrasts came from one three-category model versus repeated two-group fits, the exact missing-case denominator used to compute each scaling SD, or the precise FDR grouping across contrasts. They also do not supply the original analysis script. These details must be recorded as implementation choices, not attributed to verified source code.

## Recommended bounded implementation choices

For the present three-trait task, use a single full-rank three-category OLS fit per trait and obtain all three contrasts as linear contrasts. Encode the pastoralist category as the reference for coefficient bookkeeping only; report explicit contrast direction. Keep age in years. Use all available valid rows for each trait, rather than forcing BMI to the lipid-complete subset. Standardize that trait on the exact selected rows before fitting either additive or interaction models. Reuse that pooled scaling for any sex-specific supplemental contrasts, so changes in effect sizes are not caused by a changed denominator. These are reviewer recommendations requiring the root protocol's freeze.

Always retain the nine additive contrasts. Also retain all three likelihood-ratio statistics and all 18 sex-specific contrasts, so a different branch triggered by one synthetic dataset is visible rather than silently discarded. If displaying a source-style chosen branch, label it and retain the unselected branch in the complete results. A Gaussian ML likelihood-ratio calculation (not an F-test labelled LRT) is required if following the stated test. Exactly which LRT implementation the authors used was not recovered.

A three-trait/nine-contrast multiplicity correction, if used, must be named as the present analysis's family; it is not the paper's 11-outcome FDR. Effect patterns and sizes should lead the data comparison. Synthetic-row p-values are conditional on the chosen synthetic sample size and law; more virtual rows are not additional clinical evidence.

## Population, measurement and missingness

Recruitment was >18 years, with pregnancy, extreme biomarker and incomplete interview/covariate exclusions. Public fields do not permit fully recreating those exclusions, and an extreme-value rule was not recovered. Use the processed deposit with declared age/positivity/available-case rules, without adding result-dependent trimming.

BMI uses kg/m². TC and HDL are venous EDTA/CardioChek Plus outputs in mg/dL; they are not automatically central-lab fasting measures. Fasting was recorded, and blood-glucose analyses need that additional variable. Current three traits avoid that missing fasting covariate. LDL is calculated and low triglycerides can be unrecorded; expanding to all ten traits would introduce measurement and missingness obligations beyond this pilot.

Published Table 2 reports BMI n=1198 and TC/HDL n=406 each. These are source counts, not audited counts from the current public file. The available source text's Table 1 age-by-sex counts sum to 1360, while the main reported cohort size is 1226. Do not silently reconcile by substituting public-data group counts. The constructing Agent must identify its choice and any unresolved demographic assumption.

## Lifestyle meaning and literal public-data mapping

Supplement PDF pp. 7–8 defines pastoralists through Turkana-county location, pastoral subsistence and daily milk; rural nonpastoralists are remaining Turkana-county residents; urban nonpastoralists are Laikipia-county residents. A generated `lifestyle` is a modelled categorical attribute, not an existing latent component relabelled after seeing a target result. The public deposit already contains the three labels, so no recovery from biomarkers is necessary.

On 11 November this reviewer verified the existing file SHA256 `7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9`, parsed only its header and distinct `Lifestyle category` tokens, and obtained:

| Public literal | Canonical category |
|---|---|
| Pastoralist | pastoralist |
| Non pastoralist, rural | rural_nonpastoralist |
| Non pastoralist, urban | urban_nonpastoralist |

No category frequencies or outcome data were emitted. Original Table 1 labels M/F as male/female, supporting the recorded sex-token mapping without outcome-based inference.

## Scope decision

Admit BMI/TC/HDL with lifestyle, age and sex for a new whole-cohort generation task and Methods-guided Figure-2A-style analysis. Do not promise the original 10-trait matrix, U.S. comparison, dietary mediation or early-life analysis. The original paper may now be supplied as generation evidence under the user's new instruction; successful replay then evaluates evidence-to-data reconstruction and scientific-use preservation, not transport from independent sources or discovery of unseen target conclusions. The old excluded-target evidence rules continue to describe their own historical experiments and are not silently rewritten.
