# ANSUR II — metadata admission review

Review date: 2026-10-31. Scope: one candidate family, the 2012 U.S. Army Anthropometric Survey (ANSUR II), for genuine joint measured anthropometry. This is a metadata assessment, not a source approval, downloaded-data audit, or validation result.

## Decision

**Scientifically relevant, with conditional metadata eligibility; not a clean unexposed benchmark for this reviewing agent.** Official Army release information establishes a genuine participant-level anthropometric survey and explicitly contemplates academic use. It does not establish laboratory biomarkers, measured adiposity, clinical outcomes, or civilian-population validity. File-byte provenance, detailed measurement procedures, and record integrity remain unverified. Search snippets incidentally exposed summary results; that exposure is documented below and prevents an unqualified claim of blindness.

## Prior-role search

The first action was a filename-only, case-insensitive `rg -l` search across `biomedical_research` for `ANSUR|Gordon.?2014|Army anthropometric`, restricted to `.md` and `.json`, excluding `**/mirrors/**`, `**/mirror/**`, `**/private/**`, and `**/tests/**`. It returned no matching filenames (exit code 1). Therefore no prior-role file contents, effects, or target results were opened. The evidence-cohort-generation skill and its harness-interface instructions were read for boundary guidance; no harness execution or source registration was attempted.

## Release and file identity

The Army's 31 May 2017 release announcement identifies public raw data for 4,082 male and 1,986 female Soldiers, containing demographic information and body measurements. It describes industrial and research-relevant design uses and gives the historical distribution endpoint. This supports authorized public reuse without relying on an unverified Kaggle redistribution. It is not a verified modern license identifier. [Army release announcement](https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey)

The current official database page (displayed update: 4 March 2025) names `ANSUR II MALE Public.csv` and `ANSUR II FEMALE Public.csv`, clears the databases for unlimited public release, and describes 93 directly measured and 15 administrative/demographic variables. It withholds 3D scans. No dataset version number or file checksum was verified; the website update date must not be treated as a CSV version. [Official database metadata](https://ph.health.mil/topics/workplacehealth/ergo/Pages/Anthropometric-Database.aspx)

The selected primary report is Gordon et al. (2014), *2012 Anthropometric Survey of U.S. Army Personnel: Methods and Summary Statistics*, NATICK/TR-15/007, DTIC accession ADA611869. The NTIS record identifies a 454-page report, covering October 2010–April 2012, and an original survey sample of 7,435 men and 3,922 women. Its abstract describes 94 measured dimensions, derived dimensions, and scans; these are not the public CSV field count or public subset size. [NTIS report record](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA611869.xhtml)

## Minimum variable map

The following map comes from the official database metadata linked above. These are schema facts, not inspected participant values.

| Concept | Public field | Meaning / storage unit |
|---|---|---|
| Participant | `subjectid` | Described as a unique participant number |
| Age | `Age` | Years |
| Sex | `Sex` | Recorded Male/Female category |
| Measured height | `stature` | Stature, mm |
| Measured body mass | `weightkg` | Stored as kg × 10; divide by 10 for kg |
| Measured waist | `waistcircumference` | Waist Circumference (Omphalion), mm |
| Self-reported height | `Heightin` | Inches; separate from measured stature |
| Self-reported weight | `Weightlbs` | Pounds; separate from measured mass |

The public metadata names the waist landmark but does not fully specify posture, respiratory phase, tape tension, clothing, or calibration. These procedures were not verified from an accessible primary protocol. Do not assume equivalence to another survey's waist definition. An unverified secondary quotation of stature and scale procedures was not admitted as protocol evidence.

## Population, selection, and repeated records

The primary report's indexed sampling-method paragraph says demographic minorities were oversampled. Public working samples were created separately by sex using age, race/ethnicity, and component strata matched to DMDC census distributions dated 30 September 2011. Reserve personnel were pooled with National Guard. Five candidate subsets per sex were compared with weighted estimates for five dimensions; the closest was selected. Thus, the public sample is a selected working subset, not simply every recruited participant or a fresh independent sample. [Official Defense-hosted report, sampling paragraph beginning “Because demographic...”](https://dacowits.defense.gov/LinkClick.aspx?fileticket=EbsKcm6A10U%3D&portalid=48)

The release recommends separate sex-specific analyses and cautions against transport to other populations. Metadata implies one measurement occasion per participant, not longitudinal follow-up. [Official database metadata](https://ph.health.mil/topics/workplacehealth/ergo/Pages/Anthropometric-Database.aspx)

The unique-ID description is not a duplicate audit. No rows were fetched to check repeated IDs, repeated measurement occasions, missingness, completeness, or whether reliability remeasurements enter the public release. Those remain custodian-side checks. A future protocol should name one sex-specific historical Army population or justify explicit population weights; the two raw sample sizes do not define a defensible population sex ratio. Eligibility ages, installation clustering, recruitment exclusions, and the exact final inclusion algorithm also need protocol confirmation before stronger inference.

## Three possible descriptive analyses requiring joint data

These are prospective estimands, not claims of observed relationships or effect signs.

1. Within each recorded sex, describe the conditional waist distribution as a function of measured mass, stature, and age, allowing nonlinear terms. Compare conditional curves and dispersion, rather than validating only marginal distributions.
2. For a prespecified seating specification, estimate joint accommodation using measured sitting hip breadth, popliteal height, and buttock–popliteal length. The multivariate fit probability depends on co-occurrence of dimensions within people and cannot be recovered from independent marginal percentiles.
3. Describe joint self-report discrepancies for height and weight, conditional on age and measured body size, within each recorded sex. Compare paired error distributions and the frequency of combined discrepancies without assuming a direction.

These uses concern anthropometry and measurement behavior. BMI or ratios, if calculated later, would be deterministic derived variables. Neither they nor a body-fat formula constitute an independently measured clinical or adiposity outcome. No clinical prediction or causal interpretation is nominated.

## Access and evidence limits

- No registration, payment, data-file download, participant-row read, numerical extraction, correlation calculation, or generation occurred. No download larger than 10 MiB was initiated.
- Direct web opening of the Army health database timed out; its official indexed metadata was available. HTTPS HEAD to that page failed certificate validation; DTIC HEAD returned 403. HEAD requests to the Defense-hosted PDF and PSU metadata page failed connection checks. The PSU page also returned a web 502. These failures were not bypassed.
- Original-file names and release authority are verified at metadata level only. Current download success, byte size, revision, encoding, checksums, and schema capitalization are unresolved. Do not substitute a cleaned, merged, Kaggle, GitHub, or demo-repository copy without separate provenance verification.
- One primary methods report was selected. Only its NTIS catalog/abstract and an indexed sampling paragraph were read; no full report PDF or results section was deliberately opened. The separately cited measurer's handbook, NATICK/TR-11/017, was not read.

## Incidental exposure record

The general discovery search and one later broad protocol search returned material outside the intended metadata boundary. These results were not deliberately opened or used to choose analysis directions. Numerical results are intentionally not reproduced here.

- [Third-party ANSUR explorer](https://ergoassessment.cam/ansur-2-data-explorer/): search snippets exposed sex-specific waist/chest means, anthropometric percentile tables, age-range and data-cleaning/anomaly statements. The earlier snippet also displayed a transformation example and purported CSV corrections. No raw participant table was opened. The source is not admitted as official evidence. This is real exposure, not a claim that the agent remained blind.
- [Auburn dissertation PDF](https://etd.auburn.edu/bitstream/handle/10415/6025/R%20Garnett%20Dissertation%20%28Final%29.pdf?isAllowed=y&sequence=2): a snippet reproduced stature/weight procedure text attributed to ANSUR; no full document was read and these procedures were not accepted as verified primary documentation.
- [Older aviation anthropometry report on the official Defense site](https://dacowits.defense.gov/LinkClick.aspx?fileticket=Iz2YVbRQyNE%3D&portalid=48): an official-domain search unexpectedly displayed a historical waist summary table for other samples. It was not the selected ANSUR II report and was not used.
- Initial discovery also surfaced an unverified Kaggle-hosted memorandum copy, GitHub copies, a TU Graz demo repository, and third-party reference pages. None was used to establish authorization, file bytes, version, or results. No third-party result signs or numerical summaries were transferred into the proposed analyses.

Consequently, any later study using this family must retain this exposure flag. A strict clean-blind admission gate should hold or reject ANSUR II for the current agent; a separate evaluator may decide whether an explicitly exposure-aware descriptive project is acceptable. This review does not self-authorize such an exception.
