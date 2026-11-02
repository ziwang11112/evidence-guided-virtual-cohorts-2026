# K01 MIND-China reuse candidate

2 November 2026. **Candidate readmission only; approved_for_builder=false.** This additive view selects seven items from the retained Wang 2024 audit for source continuous-scale evidence. It adds no original-study slot, new paper read, download, patient/target-data access, fit, sample or execution. Selection was not based on target fit. The old source files remain unchanged.

Original: Wang et al., *Comparing glycemic traits in defining diabetes among rural Chinese older adults*, [DOI 10.1371/journal.pone.0296694](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0296694), Table 1 total column and explicit mean(SD) footnote. No original was reopened. [MIND_REUSE_CANDIDATE.json](MIND_REUSE_CANDIDATE.json) binds five retained files by path/SHA-256 and each selected numerical item by JSON pointer. The old independent review concerned other tables and arithmetic; it is provenance for the earlier review's scope, not a new independent Table 1 transcription.

| Item | Estimate | Meaning |
|---|---:|---|
| Age mean | 69.5 years | Direct source arithmetic mean |
| Age SD | 4.2 years | Direct individual dispersion |
| BMI mean | 25.0 kg/m² | Direct source arithmetic mean |
| BMI SD | 3.6 kg/m² | Direct individual dispersion |
| Serum glucose (FSG) mean | 5.2 mmol/L | Direct source arithmetic mean |
| Serum glucose (FSG) SD | 1.4 mmol/L | Direct individual dispersion |
| Female sample proportion | 2049/3547 ≈ 0.5776712714970398 | One division of reported female count by total analysis n; not separately reported weighted population prevalence |

All six moments describe the selected 3,547-person source analysis sample. This is the source-wide analysis n, not a verified field-specific complete/imputed count. SD divisor convention and analytic weights are unreported. Individual SDs are neither estimator SEs nor conditional residual SDs; no confidence intervals or precision estimates are reconstructed. The ratio is derived, with both integer operands preserved, and adds no independent observation.

The source comprises selected rural residents aged 61–80 in Yanlou, Shandong, free of dementia and functional disability. The 2019 follow-up excludes missing laboratory/history records and includes known diabetes history. Demographics and BMI were obtained in 2018; laboratory testing was in April–May 2019. Mean filling of continuous variables and mode filling of categorical variables are reported, but field-specific imputation counts and effects are unavailable. Preserve this selection and time separation instead of treating the margins as contemporaneous, nationally representative or untreated-adult values.

FSG used serum from a coagulant tube, centrifuged at 3,000 rpm for ten minutes, glucose oxidase on a CS-600B in a local laboratory within two hours. Overnight fasting is reported; exact hours and individual adherence are not established. This is a new applicability question for **HAALSI pooled cleaned capillary POC glucose**. Shared mmol/L units do not establish specimen, device, cleaning, handling, feeding or assay equivalence. No conversion, target moment or inherited CHNS comparability claim is provided.

Yanlou, China and Agincourt, South Africa are distinct named recruitment geographies. That supports research-frame separation, while record-level nonoverlap remains unverified. Source follow-up selection, age range, imputation, calendar period, country and fasting differ from the proposed target. Source exclusions do not become target exclusions. No target feeding proportions or demographic distribution are reconstructed.

The three proposed glucose projections—adjusted BMI, adjusted age and sex×BMI interaction—remain **joint-assumption dependent**. The selected marginals do not determine any of them, a distribution family or a complete joint law. The future construction Agent owns missing dependence, residual/distribution structure and source-to-target context transport; zero effects or independence are not defaults implied by absent evidence. Other biomarkers, correlations, agreement and quarantined bundles are omitted. Nothing is diagnostically activated, approved for construction or released here.
