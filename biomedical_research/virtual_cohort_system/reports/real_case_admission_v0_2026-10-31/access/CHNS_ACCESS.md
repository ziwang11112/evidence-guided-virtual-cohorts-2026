# CHNS official access and measurement audit

31 October 2026. Metadata only. No participant-file acquisition or effect calculation.

| Item | Observed status / exact source |
|---|---|
| Old project root | `https://www.cpc.unc.edu/projects/china/` redirects with HTTP 200 to `https://chns.cpc.unc.edu/`. |
| Old deep downloads | `/projects/china/data/datasets/data_downloads` and `/projects/china/data/datasets/data-downloads-registration` returned HTTP 404 in the current ordinary HTTP checks. |
| CPC portal | `https://data.cpc.unc.edu/projects/7/view` describes public-use household/individual data, but its Public-Use Data anchor had an empty href. It is not a verified download route by itself. |
| Current release directory | [CHNS Data Sets](https://chns.cpc.unc.edu/data/datasets/) links household/individual master files in SAS format to [UNC Dataverse](https://dataverse.unc.edu/dataverse/chns). Community data have a distinct application requirement. |
| Web-reader result | Dataverse collection returned `Access Denied` / BotStopper. This does not establish that the dataset is restricted to approved researchers or permanently unavailable. |
| Normal browser attempt | Windows Computer Use refused a new-tab action because current browser URL confidence was insufficient to enforce policy. All desktop UI input stopped. No navigation/download success assumed. |
| Future browser preference | User: use the Chrome plugin next time. No silent Windows desktop fallback. |

The official [biomarker landing page](https://chns.cpc.unc.edu/data/datasets/biomarker-data/) describes 26 fasting blood measures for participants aged at least seven in 2009 and links the documents below. This describes the release, not an eligible adult complete-case count.

- [Specimen collection manual](https://chns.cpc.unc.edu/wp-content/uploads/Blood-Collection-Protocol_English.pdf): opened as official protocol metadata; full methods audit not completed.
- [Assay methods and units](https://chns.cpc.unc.edu/wp-content/uploads/Biomarker_Methods.pdf): central `GLUCOSE` and field `Y48_1` are distinct serum-glucose fields; the listed glucose unit is mmol/L. HbA1c `Y50` is percent, with multiple listed instruments/calibration. Do not replace serum with plasma in the field definition or assume interchangeable field/central measurements. Documented clinical reference ranges are not participant distributions.
- [Biomarker codebook](https://chns.cpc.unc.edu/wp-content/uploads/C10BIOMARKER.pdf): link and document identity located; its numeric distribution tables were not deliberately inspected. Schema, missingness codes and exact release compatibility still need a controlled metadata extraction.
- [Survey documentation](https://chns.cpc.unc.edu/data/documentation/) and [survey-data overview](https://chns.cpc.unc.edu/data/): identify the need to resolve IDs, units of analysis, missing codes and corrected longitudinal master variables before joins. No join has been executed.

## Exposure log

1. Historical CHNS source-search packets include PMC8214016 / PMID 34163195 / DOI 10.2147/dmso.s312489 and PMC7282081 / PMID 32513187 / DOI 10.1186/s12944-020-01314-7. The history reviewer located result-bearing abstract sections without extracting numerical effects. Do not claim these relationships or equivalent estimands were unprovided in the project history.
2. The current biomarker page names target-study overview PMC3429648. It was not opened as a source original or supplied to a generator.
3. A general access search incidentally displayed a snippet from *Physiological Dysregulation Proceeds and Predicts Health Outcomes Similarly in Chinese and Western Populations* (DOI 10.1093/gerona/glad146), mentioning cross-system correlations and a magnesium-exclusion check. No estimates were extracted; those concepts must nevertheless be recorded if proposed analyses overlap them. An additional access-only snippet named a biological-age preprint and its CHNS availability statement. Neither was admitted as generation evidence or deeply audited as an original study.
4. Earlier full-history index reads also contain old aggregate-completion snippets. Root/history reviewer are not globally blinded. A future constructor must use a new context with a restricted input packet; do not claim foundation-model pretraining non-exposure.

## Remaining acquisition gate

The official route is identified. Actual downloadable release identity, version, license/terms, relevant file sizes, file hashes, schema and compatible covariate files are not verified. There is no patient file to analyze, and no basis to mark data admission complete. Continue with the user-preferred Chrome plugin; if its access cannot be established, preserve this resource limitation rather than substitute an unverified redistribution.
