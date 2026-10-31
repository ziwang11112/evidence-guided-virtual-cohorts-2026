# M17-B target metadata admission — before outcome access

31 October 2026. Independent case-custodian record. No new participant file has been downloaded, parsed, selected, or analyzed at this stage. This record contains metadata only.

## Admission decision

**Conditionally admit NHANES 2007–2008** as the next candidate for a reserved whole-cohort evaluation of age, recorded sex, BMI, and serum urate. The local audit found no prior acquisition or analysis of this cycle in the checked project records. This is a bounded local-provenance finding, not proof that no investigator, browser, archive, external workspace, or model pretraining has ever encountered the cycle.

Do not claim that the age/BMI/urate relationships are globally unknown. Earlier cycle targets and related scientific findings are exposed development information. This pilot tests a newly reserved local cycle and a new whole-cohort information regime.

## Official metadata and files

| Component | Permitted measurement | Definition / units | Official documentation | Published data URL, not fetched |
|---|---|---|---|---|
| DEMO_E | RIDAGEYR | Age in completed years at household screening; ages 80+ are top-coded at 80 | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/DEMO_E.htm | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/DEMO_E.xpt |
| DEMO_E | RIAGENDR | Recorded sex: 1 male, 2 female; public codebook label is Gender | same | same |
| BMX_E | BMXBMI | Body mass index, kg/m² | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/BMX_E.htm | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/BMX_E.xpt |
| BIOPRO_E | LBXSUA | Serum uric acid, mg/dL | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/BIOPRO_E.htm | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/BIOPRO_E.xpt |

The official [cycle data index](https://wwwn.cdc.gov/nchs/nhanes/search/DataPage.aspx?Cycle=2007-2008) advertises all three XPORT files; their links were extracted from that index, without requesting the files. SEQN provides the join key. The urate alias LBDSUASI (µmol/L) is the same underlying outcome and must remain private. Other raw variables, participant identifiers, diagnostic aliases, derived flags, and individual observed covariates must not be supplied to the generator.

The biochemistry component covers participants aged 12 years and older. Body measurement eligibility includes all survey participants, and BMI is released for ages 2 years and older. The proposed adult domain is therefore covered by metadata, but metadata alone does not prove complete-case capacity in each quota cell.

The biochemistry methods describe a change from Beckman Synchron LX20 in 2007 to Beckman Coulter UniCel DxC800 in 2008. Urate uses a uricase timed-endpoint assay on both instruments. No target-derived instrument adjustment is inferred or fitted. Source-to-target measurement differences remain a declared transfer assumption.

RIDSTATR code 2 identifies participants both interviewed and MEC examined, but it is not an additional selection condition in the subsequently supplied root protocol. The frozen protocol requires finite age in [20,80), valid recorded sex, finite positive BMI, and finite nonnegative LBXSUA. BMI measurements include pregnant women in the public component; the task specifies no pregnancy, race, diabetes, fasting, medication, or disease exclusions. No additional status, weight, or laboratory-value restriction will be applied.

## Proposed target definition pending the root protocol

- Age 20–79 at screening, with fixed bins [20,35), [35,50), [50,65), [65,80).
- Two recorded-sex categories, yielding eight quota cells.
- Forty complete BMI/urate records per cell, n=320, if capacity permits.
- A fixed seed or salted hash, eligibility, tie-breaking rule, and shortage rule must be committed before acquisition. Selection may depend on outcome availability but not urate magnitude.
- All four substantive columns are generated. No observed.csv, participant-level covariates, target quantiles, target cell moments, or target regression results are builder inputs.
- This is an explicitly standardized, unweighted finite quota cohort. It is not a survey-population prevalence or nationally representative inference target. Native sample weights do not automatically become valid quota-sample weights.
- NHANES-derived literature statistics are excluded as independent generation evidence. Incidental NHANES material in otherwise independent sources must be disclosed and not used as a constraint.

## Gate and exposure status

Do not select, download, or analyze target outcome data until the root evaluation protocol is committed. The current work only supports conditional metadata admission. Complete-case capacity, exact selection, file integrity, parser correctness, and real analytical results remain unassessed.

For public documentation, frequency tables were removed before inspection; only category-code labels were extracted from RIAGENDR and RIDSTATR tables. Public search results incidentally displayed method/limit snippets for other candidate cycles and unrelated paper titles. No target association, target sample moment, target quantile, or individual row was acquired or used for this admission.
