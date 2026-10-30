# M15B target metadata admission — 2026-10-30

Serum urate is metadata-compatible with the proposed NHANES August 2021–August 2023 adult case. This admission verifies documentation, available variables, and public file headers. It does not establish target sample size, target completeness, or outcome utility. No participant outcome record or urate distribution was opened or computed.

## Verified public source and outcome

The official [BIOPRO_L documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BIOPRO_L.htm) was first published in September 2025 and identifies `LBXSUA` as uric acid in **mg/dL**. `LBDSUASI` is the same measurement expressed in µmol/L, calculated as `LBXSUA × 59.48`; it is not an independent outcome. All examined participants aged 12 or older were eligible. The serum samples are analyzed at the University of Minnesota Advanced Research Diagnostics Laboratory.

The assay uses uricase, followed by a peroxidase color reaction measured at 546 nm with 700 nm as secondary wavelength, on the Roche Cobas 8000. CDC reports unchanged laboratory method but an instrument upgrade from Cobas 6000; this can matter when transporting evidence from earlier cycles. The urate lower detection limit is 0.2 mg/dL. The documentation describes LLOD/√2 substitution for below-limit analytes in general; it does not list a dedicated `LBDSUALC` flag for urate. Do not infer the number of censored results. [Assay method PDF](https://wwwn.cdc.gov/nchs/data/nhanes/public/2021/labmethods/BIOPRO-L-MET-Uric-acid-508.pdf) was located through documentation/search but not opened as a PDF.

## Metadata-compatible selection and covariates

Join the components one-to-one on `SEQN`, checking uniqueness at the later data preparation stage.

| Purpose | File and variable | Selection or interpretation |
|---|---|---|
| Age | DEMO_L `RIDAGEYR` | 20 through 56 inclusive; age at screening, which CDC recommends for most analyses |
| Sex/gender | DEMO_L `RIAGENDR` | 1 male; 2 female; retain the source wording and coding |
| Race/ethnicity | DEMO_L `RIDRETH3` | 3 non-Hispanic White; 4 non-Hispanic Black; `RIDRETH1` uses the same codes for these groups |
| Exam participation | DEMO_L `RIDSTATR` | 2 means interviewed and examined |
| Body mass index | BMX_L `BMXBMI` | kg/m²; use as measured/released rather than recomputing unless specified |
| Waist | BMX_L `BMXWAIST` | cm; available for adults; require completeness only if used |
| Supporting body measures | BMX_L `BMXWT`, `BMXHT` | kg and cm, respectively |
| Body-measure completeness | BMX_L `BMDSTATS` | 1 complete age-appropriate data; 2 height/weight only; 3 other partial exam; 4 no body measures; direct required-variable availability is preferable to automatically excluding every partial exam |
| Diabetes history | DIQ_L `DIQ010` | 1 yes; 2 no; 3 borderline; 7 refused; 9 unknown; dot missing |
| Diabetes treatment | DIQ_L `DIQ050`, `DIQ070` | Current insulin and diabetic pills; question routing means missing is not automatically no |
| Survey design | DEMO_L `SDMVSTRA`, `SDMVPSU` | Masked stratum and PSU |
| Blood-analyte weight | BIOPRO_L `WTPH2YR` | Use for urate analyses, rather than defaulting to the full MEC weight |

Variable definitions were checked in [DEMO_L](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm), [BMX_L](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm), and [DIQ_L](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DIQ_L.htm). These components span the requested ages. No covariate participant file was downloaded.

For an unambiguous “no diagnosed diabetes” case, the conservative metadata-compatible default is `DIQ010 == 2`. It excludes borderline responses as well as positive/unknown responses; this is an explicit population choice, not an interchangeable synonym for “not yes.” If the admitted literature includes borderline participants or uses treatment exclusions, harmonize that rule before generation. `DIQ010` is self-report of professional diagnosis, excluding pregnancy-only diabetes in the adult-female wording. It does not identify undiagnosed diabetes. Do not use the standard-biochemistry serum glucose variable to diagnose diabetes: CDC explicitly recommends the separate reference glucose assay for that purpose.

Pregnancy is a transport limitation if the source requires nonpregnancy. `RIDEXPRG` is released only for women aged 20–44. Codes are 1 pregnant, 2 not pregnant, 3 cannot ascertain; missing outside this range does not establish nonpregnancy. A uniform nonpregnant 20–56 selection cannot be fully verified from that variable alone. No pregnancy exclusion is assumed by this admission.

## Weights, missingness, and target separation

CDC introduced the additional phlebotomy weight in this cycle to address blood-collection nonresponse. Eligible people without a blood specimen can have `WTPH2YR = 0`. The urate survey analysis should use positive `WTPH2YR` with `SDMVSTRA` and `SDMVPSU`, with the intended adult/race/diabetes population represented as a survey domain where appropriate. CDC asks analysts to assess outcome and covariate item missingness and consider additional nonresponse adjustment. Neither that assessment nor any outcome-complete-case selection was performed here. The codebook missing value is SAS numeric missing (`.`).

BIOPRO eligibility is not restricted to the fasting subsample. No fasting restriction is required by the urate component metadata. If the source population requires fasting or excludes medications, those restrictions need explicit harmonization; a fasting-dependent assay or subsample would also require its appropriate weight. Diabetes-treatment variables alone do not establish absence of all urate-modifying medications.

The cohort size, subgroup precision, joint covariate availability, and urate missingness remain unknown. Required-covariate missingness rules and the independent evaluator's handling of nonmissing urate should be fixed before target-outcome access. Retain the appropriate design variables even if an unweighted analysis is also planned. General-population national representation cannot simply be claimed for an arbitrary complete-case subset.

## File availability and recency

The [official release listing](https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Cycle=2021-2023) supplies these verified URLs:

| Component | Public XPT | Header range result |
|---|---|---|
| Urate | [BIOPRO_L.xpt](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BIOPRO_L.xpt) | HTTP 206; valid SAS library header |
| Demographics | [DEMO_L.xpt](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.xpt) | HTTP 206; valid SAS library header |
| Body measures | [BMX_L.xpt](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.xpt) | HTTP 206; valid SAS library header |
| Diabetes questionnaire | [DIQ_L.xpt](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DIQ_L.xpt) | HTTP 206; valid SAS library header |

Only bytes 0–79 were read from each file, after anomalous HTTP HEAD length metadata prompted bounded verification. These bytes contain the SAS library signature, not participant records. Full files and covariate data remain undownloaded. The exact status, Content-Range, timing, and URLs are recorded in `target_access.json`.

The [official cycle index](https://wwwn.cdc.gov/nchs/nhanes/Default.aspx) lists August 2021–August 2023 and 2025–2027, with no 2023–2024 entry. The latter landing page did not provide a verified later serum-urate file in this review. Thus August 2021–August 2023 is the latest public urate file **confirmed here**, not a claim that every later CDC endpoint has been exhaustively audited.

## Boundary and exposure record

One web search query was used (limit four). The first eight legacy URL opens failed; the relocated official URLs then worked. A Windows output-encoding error interrupted one metadata-printing batch and was corrected with UTF-8. These failures and every query/open batch are preserved in `target_access.json`.

Full codebook HTML was temporarily fetched in memory. Outcome frequency/range tables were suppressed before output; no urate participant count, minimum, maximum, mean, percentile, or relation was exposed to this agent or copied to these artifacts. Categorical code/label extraction omitted frequency columns. Official narrative did expose general phlebotomy participation, pregnancy disclosure, and design metadata. A search snippet incidentally displayed assay quality-control lot statistics; these describe laboratory controls, not participant outcomes, and were neither transcribed nor used. The search also returned an unrelated NHANES HbA1c/sex-hormone paper snippet with population/sample-size metadata; that paper was not opened. These incidental exposures prevent an overly broad claim of zero aggregate exposure, while no participant serum-urate outcome summary was examined.

The prior HbA1c experiment used this same NHANES cycle, per the supplied task history. This proposed case is a new outcome task with independent public outcome evaluation; it is **not wholly new participants or a wholly new cohort**. No old local target results were read. Target selection rests on variable availability and scientific compatibility, not favorable target outcomes.
