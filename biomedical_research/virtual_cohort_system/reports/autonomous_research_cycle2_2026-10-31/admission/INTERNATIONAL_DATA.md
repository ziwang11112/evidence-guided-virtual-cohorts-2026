# International data admission screen — 2026-10-31

Scope: exactly two candidate families, Korean KNHANES and Mexican ENSANUT. This is an access/provenance and variable-metadata screen for an evidence-driven **whole virtual cohort**. It is not a target analysis, source-statistic extraction, data acquisition, or generator run. No accounts, access applications, paid APIs, pledges or consent forms were submitted. No participant-data archive body was downloaded or read. No primary cohort-method paper was opened (budget used: 0 of 2).

## Decision

| Family | Decision from this screen | Reason |
|---|---|---|
| **ENSANUT 2018–2019, Mexico** | **Preferred new family; admit to controlled custodian preflight and task-contract preparation.** | Official public-use provenance, direct download route, adult metabolic variables, units, fasting-duration field, compatible person identifiers and survey-design fields are documented. No prior ENSANUT alias was found in the project search. |
| **KNHANES IX, Korea, 2022–2024** | **Defer from an immediately executable new case.** | Official provenance and relevant survey content are established, but live data access requires personal information and consent/pledge submission. Exact year-specific variable coding/units remain unverified because the official guide attachment did not return a PDF in this session. Prior KNHANES literature exposure also requires a recorded overlap boundary. |

Neither decision authorizes hidden-target inspection by a builder. ENSANUT still needs a custodian-owned, fixed-release data contract, analytic inclusion rules, matching and missingness checks, and separation of the held-out real cohort before generation. Selection here does not use apparent target means, coefficients, correlations, prevalence or performance.

## Prior-role audit and exposure boundary

The first action searched aliases `KNHANES|Korea National Health|ENSANUT` using `rg` across all `biomedical_research` Markdown/JSON, with literal mirror/mirrors/tests/private exclusions. **Correction:** the initial exclusion patterns did not recognize the separate `github_virtual_cohort_2026-10-27` directory as a mirror; matching copied files were returned. Subsequent filename-only screening explicitly excluded that directory and `mirror*` paths. No mirror was treated as independent evidence.

- **KNHANES prior roles:** proposed external donor/new public-cohort option in `three_model_review_2026-10-28/CLAUDE_REVIEW_USER_SUPPLIED.md` and `CLAUDE_PRIMARY_SOURCE_CHECKS.md`; cross-study transport discussion in the scientific-utility plan/reviews; a KNHANES VII dietary-fiber/urate paper in `virtual_cohort_system/work/m13/urate_evidence.md` and its report copy. Source-report records also contain a negative cohort distinction (the Healthy Twin Study is not KNHANES). This does **not** establish that KNHANES participant data were previously acquired or used as a target.
- **ENSANUT:** no alias hit in the initial search or the corrected non-mirror filename-only search. This supports “not found in searched project history,” rather than a claim of no possible pretraining knowledge.
- **Accidental local exposure:** initial line-printing `rg` output exposed an earlier KNHANES urate summary with numerical moments and a long JSON reviewer-response line containing prior-study numeric examples. Those values are not reproduced or used here. The search was changed to filename-only output. This screening context must not be certified as pristine blinding for KNHANES; the parent agent was informed.
- **Accidental web-snippet exposure:** initial searches returned third-party/non-method article snippets and unrelated Korean administrative sample-record snippets. No such result was opened or used. Official ENSANUT conceptual-design snippets also showed diagnostic cutpoints, assay precision and background scientific definitions; these are documentation, not target summaries, and none is a synthesis parameter here. No ENSANUT target numerical outcome was intentionally sought or observed in the material used for this screen.

## ENSANUT 2018–2019: official provenance and access

**Identity:** INEGI catalogue **590**, statistical-project identifier **MEX-INEGI-ESD3.04-ENSANUT-2018**. The catalogue lists Mexico 2018–2019 and metadata modification on 2022-10-06. The database-structure manual is explicitly updated November 2020. No immutable microdata version number or checksum was supplied by the live download page/response headers; do not equate the metadata update date with the current database revision. [Official INEGI catalogue](https://www.inegi.org.mx/rnm/index.php/catalog/590), [structure manual](https://ensanut.insp.mx/encuestas/ensanut2018/doctos/otros/ensanut_2018_estructua_base_datos.pdf).

**Access and scientific reuse:** INSP’s FAQ says its hosted survey data/documentation are freely accessible and describes icon-based direct downloads. INEGI labels access public use and allows statistical use with source attribution; its terms permit extraction/adaptation/publication while preserving metadata and avoiding misleading representations. This is not a finding that every ancillary restricted product is open. No registration, payment, institutional account or application was encountered for the public codebooks. Data-archive responses returned HTTP 200 with ZIP metadata without credentials; only headers were inspected. [INSP FAQ](https://ensanut.insp.mx/preguntas_frecuentes.php), [INEGI access policy and terms](https://www.inegi.org.mx/rnm/index.php/catalog/590).

**Recruitment/design:** a cross-sectional probability household survey with stratification and clusters, using INEGI’s master dwelling frame. Health fieldwork ran 2018-07-30–2019-06-28; nutrition fieldwork ran 2018-07-30–2019-02-15. Selected dwellings, principal households and selected household persons are distinct units. Adult questionnaire eligibility is age 20 years or older. National/state sampling design must not be mistaken for municipality-level representativeness, nor for representativeness of an arbitrary complete-case lab subset. [Official survey introduction](https://ensanut.insp.mx/encuestas/ensanut2018/index.php), [download inventory](https://ensanut.insp.mx/encuestas/ensanut2018/descargas.php).

### Variable feasibility from official catalogues

The `Catálogo` XLSX files below were retrieved to memory and their `Variables`/`Valores` sheets read. They are codebooks, not participant tables. Official download location for all named files: [ENSANUT 2018 downloads](https://ensanut.insp.mx/encuestas/ensanut2018/descargas.php).

| Required item | Verified field / metadata | Unit or coding status |
|---|---|---|
| Adult age | `EDAD` in `DetBioCronicosAdultos` and `CN_ANTROPOMETRIA`; adult survey eligibility ≥20 years | Age in years; separate `EDAD_MESES` exists in anthropometry. Missing/special age codes still need explicit contract handling. |
| Sex | `SEXO`, both catalogues | 1 = Hombre, 2 = Mujer. Do not silently map unknown or missing values. |
| BMI | Derive from measured weight and height; `PESO1_1/2`, `TALLA4_1/2`, with a separate older-adult measurement block `PESO12_1/2`, `TALLA15_1/2` | kg and cm are documented; BMI is kg/m² after cm-to-m conversion. The questionnaire’s age routing and repeated-measure rule must be frozen; no ready-made BMI field was asserted. |
| Serum glucose | `VALOR_GLU_SUERO` | mg/dL in official conceptual-design variable table. |
| HbA1c | `VALOR_HB1AC` (retain official spelling) | Percent, whole-blood determination. |
| Lipids | `VALOR_COL_HDL`, `VALOR_COL_LDL`, `VALOR_COLEST`, `VALOR_TRIG` | mg/dL. Catalogue labels for several lab fields are blank, so units come from the conceptual-design table rather than inference from observed magnitudes. |
| Blood pressure | `P27_1_1`, `P27_1_2`, `P27_2_1`, `P27_2_2`: first/second systole/diastole | mmHg documented in methods; digital Omron HEM-907 XL. Reading-average/validity rule remains to be frozen. |
| Fasting status | `P5_1` in adult lab catalogue | Hours since last food. The existence of a fasting-duration field is verified; this screen does not claim that every row is fasting or choose an eligibility cutpoint from target rows. |
| Join and design | `UPM`, `VIV_SEL`, `HOGAR`, `NUMREN`; `EST_DIS`, `UPM_DIS`, `ponderador_glucosa`; anthropometry also has `F_ANTROP`, `F_ANTROP_INSP` | Compatible component keys are documented. Numeric versus string key types differ between catalogues. Matching, uniqueness and suitable joint-subset weighting are not tested here. |

The lab-unit table is on PDF page 236 and HbA1c on page 237 (one-based viewer numbering); BP methods are on viewer page 118. BMI definition is on viewer page 234. [Official conceptual design](https://ensanut.insp.mx/encuestas/ensanut2018/doctos/metodologia/ensanut_2018_diseno_conceptual.pdf). The structure manual describes the person key and uses `CN_MUESAN_DETBIO_ADU` for an adult biochemical table, while the live distribution is named `DetBioCronicosAdultos`. Treat that as a documented naming/version reconciliation requirement, not proof that files are byte-identical. [Structure manual, linkage and table descriptions](https://ensanut.insp.mx/encuestas/ensanut2018/doctos/otros/ensanut_2018_estructua_base_datos.pdf).

### Download inventory and observed sizes

The official portal supplies SPSS, Stata and CSV ZIP choices; codebooks are separate XLSX. The approximate sizes below are **compressed response Content-Length**, not row counts. Archive requests were closed immediately after header inspection without reading their bodies. No Last-Modified header was present.

| Official filename selected from live portal | Header bytes | Approximate decimal MB |
|---|---:|---:|
| `DetBioCronicosAdultos.csv.csv.zip` | 1,264,138 | 1.26 |
| `CN_ANTROPOMETRIA.csv.csv.zip` | 1,218,701 | 1.22 |
| `ponderadores_hipertension.csv.csv.zip` | 871,449 | 0.87 |
| `CS_RESIDENTES.csv.csv.zip` | 3,575,595 | 3.58 |

Read-only codebook sizes: adult lab 353,335 bytes; anthropometry 355,143; hypertension-weight catalogue 355,268; resident catalogue 369,919. These were observed directly from official responses. No raw download URL was invented: the portal uses a POST form with an `ArchId...` button name for each listed file, so the stable reproducible link is the download page plus exact filename/category.

**Next permitted preparation:** use these official catalogues to freeze adult eligibility, fasting handling, repeated anthropometry/BP measurements, joins, design weighting and missing-code treatment. Have the custodian pin actual release bytes/hashes and retain real rows outside the generator. Require published-source evidence from independently admitted populations or a declared exposure-compatible source role; no target summary is supplied by this report.

## KNHANES: official route and unresolved checks

**Identity/release:** KNHANES IX spans 2022–2024. KDCA’s 2026-07-31 notice describes an additional raw-data release. The ordinary basic database naming pattern is `HNYR_ALL`, with two-digit year; SAS/SPSS formats are listed. A proposed year such as 2023 must be pinned to the actual revision, not merely its nominal survey year. [Official raw-data page](https://knhanes.kdca.go.kr/knhanes/rawDataDwnld/rawDataDwnld.do), [data introduction](https://knhanes.kdca.go.kr/knhanes/postSendPage.do?postparam=%7B%22menuId%22%3A%224003%22%7D&url=%2Feng%2Fintr%2FdataIntr.do), [KDCA release notice on main portal](https://knhanes.kdca.go.kr/knhanes/main.do).

**Actual access requirement:** the live raw-data page exposes mandatory email, name and affiliation; consent for collection/use of these details; and a pledge restricting use to statistical analysis and prohibiting disclosure of information learned about individuals. The page states that refusal of personal-information consent prevents provision of data. The latest notice also refers to a security pledge. None was submitted. This evidence supports an accessible **user-information/pledge route**, not anonymous download, and does not establish this user’s completed access. A separate restricted/linked-data application route should not be conflated with ordinary raw-data access. [Official access form](https://knhanes.kdca.go.kr/knhanes/rawDataDwnld/rawDataDwnld.do).

**Design:** KNHANES IX uses the 2019 census frame, region-to-household sampling, geographic/housing strata and implicit demographic strata. Household screening precedes systematic household selection and scheduled examination. Trained staff conduct examination/interview in mobile examination centres; nutrition staff visit households. [Subject selection](https://knhanes.kdca.go.kr/knhanes/eng/intr/sbjSlct.do), [survey methods](https://knhanes.kdca.go.kr/knhanes/eng/intr/srvyMtd.do).

**Variable coverage versus year confirmation:** the official survey-content page lists household age/sex, measured height/weight, systolic/diastolic BP, fasting glucose, HbA1c, total/HDL/LDL cholesterol and triglycerides. However, this live table explicitly describes **2025** survey items. It therefore supports family-level feasibility only, not definitive 2023 availability, age routing, units, missing codes or field names. Adult interview eligibility on that page is ≥19 years; lab/measurement ages are item-specific. Do not silently transplant the live page into a 2023 contract. [Official survey contents](https://knhanes.kdca.go.kr/knhanes/eng/intr/srvyCtnt.do).

**Guide metadata:** the public guide list returned record **52**, title `2023_원시자료이용지침서`, registered 2024-12-13 and modified 2026-07-31. Its public attachment metadata names the KNHANES IX **2022–2024 raw-data user guide**. Record 110 is the 2024 guide, also modified 2026-07-31. The attachment URL returned a 1,520-byte HTML response rather than PDF. Accordingly, **no KNHANES codebook text or exact data filesize was verified**. [Public guide page](https://knhanes.kdca.go.kr/knhanes/dataAnlsGd/utztnGd.do), [guide-list metadata endpoint](https://knhanes.kdca.go.kr/knhanes/dataAnlsGd/findUtztnGdbkDataList.json?utztnGdbkDataKnd=1&pageSize=10&pageNo=1).

Remaining admission conditions: inspect the correct public guide/version without acquiring participant rows, establish exact age/sex/measurement coding and units, record assay-year changes and weights, and complete an authorized access route. Until then retain KNHANES as a deferred family, with its earlier urate-source exposure disclosed.

## Readlist and execution/exposure receipt

| Item read/requested | Scope actually exposed | Use in decision |
|---|---|---|
| Local alias `rg` then filename-only `rg -l` | Matching filenames; initial matching lines inadvertently included old urate/reviewer numbers and copied-mirror lines | Prior-role flag only; no values retained |
| `evidence-cohort-generation/SKILL.md` and `references/harness-interface.md` | Workflow/boundary instructions | Kept metadata screening separate from generation and target inspection |
| PDF skill | Read-only extraction guidance | Documentation inspection only; no output PDF created |
| Web search results | Official metadata plus incidental off-topic/third-party snippets described above | Only official survey metadata used |
| INSP ENSANUT 2018 download page, FAQ, introduction | File inventory, access route, fieldwork/design descriptions | Access and provenance |
| INEGI catalogue 590 | Identifier, design/access policy, terms; background narrative snippets | Identity/reuse only; no quality-indicator/result links followed |
| Four ENSANUT `Catálogo.xlsx` files | Dictionary rows, labels, coding and schema only | Variable feasibility, joins and design fields |
| Four ENSANUT CSV ZIP requests | HTTP status, content type, Content-Length; body not read | Approximate filesize and direct route only |
| ENSANUT structure PDF | Front matter, update date, linkage and table-description sections | Version caveat and keys |
| ENSANUT conceptual-design PDF | Front matter; targeted measurement/unit/method sections and surrounding metadata snippets | Units and measurement context; no analytical results sought |
| KDCA main/data-introduction/design/content pages | Release/access/design and 2025 item metadata | Family feasibility and year-mismatch caveat |
| KDCA public page scripts/menu JSON | Only navigation/API mapping needed to retrieve public metadata pages | Technical route, not scientific evidence |
| KDCA raw-data page | Consent/pledge text and blank user-information fields | Actual access requirements; no submissions |
| KDCA guide list and public guide attachment request | List/attachment metadata; attachment failed to return PDF | Version locator only; codebook remains unverified |

All online checks performed 2026-10-31. Failed tools were retained as limitations: a guessed legacy English KNHANES page failed; web extraction could not render several KDCA pages, while official public POST navigation did; one Python PDF attempt failed because `pypdf` was absent before any network request; the final KNHANES guide response was HTML. No new library was installed. Only this admission report was written by this screening subtask.
