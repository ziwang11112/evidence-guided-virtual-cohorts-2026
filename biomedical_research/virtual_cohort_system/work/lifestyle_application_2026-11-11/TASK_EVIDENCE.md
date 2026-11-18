# Permitted published evidence for a new lifestyle cohort

This file is for the constructing Agent. It contains original-paper evidence and task context, not project-fitted target coefficients, old generators or old synthetic results.

## Research use

Generate a complete virtual cohort with age, sex, lifestyle category, BMI, total cholesterol (TC), and HDL cholesterol, for comparing three lifestyles with age/sex-adjusted analyses. No real participant rows are supplied. Construct scientific relationships and numerical parameters yourself from the permitted evidence, additional permitted literature and explicit assumptions. The host does not prescribe group differences, distributions, correlations, slopes or residual SDs. Missing outcomes may be represented if the task contract permits them and their mechanism is stated; absence of a reported relationship does not mean independence.

## Primary study to inspect

[Lea et al., Science Advances 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/), DOI 10.1126/sciadv.abb1430. Use Tables 1–2, Figure 2A, and models 1–2 in Methods. [Supplementary methods](https://gurven.anth.ucsb.edu/sites/default/files/sitefiles/papers/lea%20et%20al.%202020%20supplement.pdf) define measurements and lifestyle categories. [Table S1](https://pmc.ncbi.nlm.nih.gov/articles/instance/7577730/bin/abb1430_Table_S1.xlsx) and [Table S2](https://pmc.ncbi.nlm.nih.gov/articles/instance/7577730/bin/abb1430_Table_S2.xlsx) are linked published aggregate workbooks; use only a verified recovered version, not a download landing page.

The source's reported pattern is an urban difference in BMI and TC, but no detected lifestyle contrast for HDL; rural pastoralists and nonpastoralists were not distinguished on these individual biomarkers. Nonsignificance is not a reported zero effect or an equivalence bound. The original main text reports pastoralist BMI 19.99±2.14 kg/m² and HDL 72.69±14.72 mg/dL; preserve their stated population/summary context. Do not treat these as pooled means. Source values and patterns are legitimate inputs for this reconstruction task, not required signs to hard-code without a generative rationale.

## Definitions and source limitations

Use three semantic lifestyle labels: `pastoralist`, `rural_nonpastoralist`, and `urban_nonpastoralist`. In the source they correspond to traditional pastoralism/daily milk in Turkana county, other rural Turkana-county residents, and urban Laikipia-county residents. BMI is kg/m²; TC/HDL are mg/dL venous EDTA/CardioChek Plus measurements. Age is years and eligibility is >18; sex is F/M. Do not invent a laboratory fasting equivalence.

The report's cohort n is 1226. Source Table 2 gives BMI n=1198 and lipid n=406 each, whereas Table 1's displayed age-sex-lifestyle cells sum to 1360. Record how you handle that source inconsistency; do not claim exact demographic recovery. Source public-data counts or fitted relationships calculated by this project are not inputs. The paper does not identify the entire joint distribution, within-group covariate dependence or all conditional residual scales.

The companion `PUBLISHED_TABLE1.json` transcribes the displayed age/sex/lifestyle counts without recalibrating them to 1226. Its printed bins also leave age 70 ambiguous (61–69, then >70). These are source uncertainties to address explicitly, not an invitation to inspect participant data. S1/S2 workbook retrieval did not succeed in the initial source audit: PMC returned HTML pages, and the official Europe PMC supplementary archive timed out. No unverified workbook numbers are supplied here.

## Requested analysis

The fixed evaluation uses age/sex-adjusted lifestyle contrasts on standardized outcomes, with an interaction check and retained sex-specific analyses. The task contract will state exact estimator and output schema. Research questions are visible. You may use the source's published adjusted relationships, distributions or subgroup summaries if their operators and units are recorded correctly. A standardized group coefficient is not a raw-unit mean difference, and a standard error is not an individual SD.

Provide an executable generator, model specification and concise evidence/assumption record. Link each scientific numerical choice to a published statistic, a derivation, or an explicit assumption. Separate variation between individuals from uncertainty about the evidence/model. Use the supplied trial checks, decide whether to revise or retain, and freeze your final choice. New real-data results will not be returned as tuning feedback. The target is a usable possible cohort under the stated evidence; individual measurements are not recovered.
