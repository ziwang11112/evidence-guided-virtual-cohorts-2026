# Existing-data task admission: scientific feasibility

9 November 2026. This is an outcome-free task proposal and metadata audit, not a completed experimental release. It selects a priority task for source/measurement admission; no target effect, mean, correlation, eligible candidate sample size or generator result was inspected or calculated. No participant rows were opened and no new file was downloaded. The accompanying JSON records the same decisions.

## Recommendation

**Priority: a joint systolic/diastolic blood-pressure task in the existing PNS 2013 laboratory-substudy workbook.** Generate age, recorded sex, BMI, systolic blood pressure (SBP) and diastolic blood pressure (DBP) as one whole cohort. Evaluate two adjusted BMI coefficients and the residual SBP–DBP correlation from the same table. This adds a new endpoint task within the already exposed PNS family; it is not a new dataset family or a claim that every project context has been blinded to PNS.

**Conditional backup: CHNS 2009 age/sex/BMI and high-sensitivity CRP.** It has an established demographic/anthropometric linkage and a documented current field, but unresolved released-field/legacy-method unit mapping and detection-limit semantics make it less ready than PNS BP. PNS hemoglobin/creatinine remains a lower-priority reserve because age timing, creatinine calibration and eGFR definition add further unresolved assumptions.

The choice is based on measurement identity, available file structure and a meaningful three-analysis joint task, not expected signs or favorable target values. Neither priority task is ready for clinical execution until its original-source evidence and remaining measurement gates are closed. No prespecified pass/fail accuracy threshold is introduced here.

## Priority task: PNS BP

### Verified local metadata and inventory

The retained archive is `work/analysis-utility-preparation-2026-10-29/pns_hba1c/custodian/raw/PNS2013_Exames.zip`. Its existing acquisition record identifies 8,952 official laboratory-workbook records; this is **not** the new BP analytic N. The prior 7,979-person HbA1c subset must not be reused as the BP reference: doing so would impose an unnecessary HbA1c-completeness condition. The raw archive was not decoded in this audit.

The already saved `visible/field_map.json` contains the actual 509-column source header inventory. It confirms `Z001`, `C008`, `z004`, `z005`, `P005`, `W00407`, `W00408` and `peso_lab`. The separate dictionary workbook is metadata, not participant data, and was read here. Its **Plan2 columns A–D** are the field definitions; column E is a separate unaligned list and is not a mapping.

| Field | Verified definition and coding | Exact dictionary locator, one-based worksheet rows |
|---|---|---|
| `C008` | Age from the IBGE baseline database, years. Do not replace with `Z002`, whose time reference is unresolved. | Plan2 A:D, row 8; `Z002` at row 7 |
| `Z001` | Recorded sex: 1 male, 2 female. | Rows 5–6 |
| `z004` | Final measured weight, kg; dictionary domain 30–200; 999 error; `.` unavailable/inapplicable. Dictionary prints `Z004`, actual header is lower case. | Rows 15–17 |
| `z005` | Final measured height, cm; dictionary domain 120–210; 999 error; `.` unavailable/inapplicable. Actual header is lower case. | Rows 18–20 |
| `W00407` | Final SBP, mmHg; dictionary domain 60–290; 999 error; `.` unavailable/inapplicable. | Rows 1890–1892 |
| `W00408` | Final DBP, mmHg; dictionary domain 30–200; 999 error; `.` unavailable/inapplicable. | Rows 1893–1895 |
| `P005` | Baseline interview question asking whether currently pregnant; code 1 yes. | Row 515 onward; existing preparation documents the retained unknown/inapplicable categories |
| `peso_lab` | Laboratory weighting variable. The inventory has no explicit sampling stratum, PSU or stable official person-ID field. | Row 1901; `field_map.json`, `design_audit` |

The recorded dictionary SHA-256 is `5aa4a3685fa2b1a9b8aa3739e3da2b83cf72fdb0affe988f2b6cc4442a6833c0`. The recorded archive SHA-256 is `d31544efdad138f3292ab86c9606cd722bf091781cc86ef371354ba63c9994bb`. These identifiers come from retained acquisition records; no new raw-data hash or decode was performed.

### Locked scientific proposal, pending measurement/source release

**Question:** Can a scientific Agent use external study summaries to construct the joint age/sex/BMI/SBP/DBP distribution needed for two adjusted pressure associations and the remaining dependence between pressures?

**Population proposal:** Existing PNS laboratory-substudy records with **baseline C008 age 20–79**, sex coded 1/2, dictionary-admissible weight/height and both final BP fields, and finite positive `peso_lab`. Derive BMI as kg/(cm/100)^2. Exclude reported baseline pregnancy `P005=1`, retaining unknown/inapplicable status explicitly rather than claiming confirmed nonpregnancy. Require complete fields for all three analyses on one common subset. Do not condition on HbA1c, other laboratory markers, hypertension diagnosis or treatment, and do not invent a treatment-free population. Do not use an SBP≥DBP filter to remove observed pairs; retain a separately reported consistency diagnostic if the protocol adopts it.

The proposed 20–79 age span reuses the project's already documented adult baseline-age scope, before any BP outcome inspection. The weight, height and BP bounds are **dictionary admissibility ranges**, not outcome-derived trimming or claims that measurements outside those domains are clinically impossible. Do not change these ranges because of the resulting target means or fit. Their enforcement and sentinel handling must be verified against official measurement documentation before the executable reference contract is sealed.

**Timing and measurement:** The old preparation explicitly distinguishes the 2013 interview from the 2014–2015 laboratory visit. `C008` is baseline IBGE age. The parent subsequently verified the official PNS 2013 anthropometry/BP manual: page 16 names **G-TECH MA100**; page 19 specifies **5 minutes of rest and three readings 2 minutes apart**. Its official 2013 launch material places BP at the initial interview. This metadata verification was reported to this reviewer and must be bound to the parent's methods receipt; the manual was not independently downloaded or read by this subtask. The retained dictionary identifies W00407/W00408 as the released final values but does not establish their exact aggregation algorithm. Analyze those released fields without claiming they are the mean of the last two readings. The unknown final aggregation is a stated measurement limitation, not automatically a reason to reject documented final fields. Describe the task as baseline/interview BP in the later laboratory-substudy release, not “2014–2015 blood pressure.” Do not add years to age, reconstruct individual visit dates, or infer measurement timing from the laboratory weight.

Parent-verified official manual URL: `https://homologacao-pns.icict.fiocruz.br/wp-content/uploads/2021/02/Manual-de-Antropometria-e-de-Medida-de-Pressao-Arterial-PNS-2013.pdf`. The parent also reported incidental national age/sex BP-prevalence information in a search snippet; preserve that exposure record and exclude it from generator evidence. This audit has neither reproduced those numbers nor used them for task choice.

**Primary descriptive estimand:** Apply the existing supplied `peso_lab` to the common complete-case subset for weighted point estimates, with a prespecified unweighted sensitivity panel. This defines a finite weighted analytical distribution. It does not establish nationally representative baseline BP inference: the laboratory subsample selection, calibration and additional BP complete-case exclusions need explicit qualification. With no public PSU/stratum fields in the saved inventory, do not substitute region as a stratum, invent design degrees of freedom or label an IID bootstrap/HC3 interval design-based. A defensible first release can report weighted point discrepancies and conditional simulation spread without a survey-confidence claim. Any uncertainty display must have its meaning frozen before revealing target effects.

The whole-cohort output can be equally weighted while representing that stated target distribution; authors must receive the **definition** of the weighting/selection target, never its empirical cell shares, weighted moments or fitted effects. More generated rows do not identify that target distribution.

### Three proposed analyses, same rows in every delivery

| ID | Fixed analysis | Focal result and units |
|---|---|---|
| PNS-BP-SBP | WLS: SBP ~ 1 + (age−50)/10 + female + (BMI−25)/5 | BMI coefficient, mmHg per 5 kg/m², adjusted for age and recorded sex |
| PNS-BP-DBP | WLS: DBP ~ 1 + (age−50)/10 + female + (BMI−25)/5 | BMI coefficient, mmHg per 5 kg/m², adjusted for age and recorded sex |
| PNS-BP-RESID | Fit both preceding models on the same common rows and weights; weighted Pearson correlation of the paired residuals | Dimensionless residual SBP–DBP correlation |

Centering constants are numerical coordinates, not target-derived parameters. These are association projections, not effects of intervening on BMI. The third analysis requires a joint SBP/DBP law beyond two marginal regressions. A source lacking residual covariance can still inform the first two analyses; the missing dependence must remain an explicit modeling assumption to be evaluated, not be presented as learned fact.

Prespecify a small diagnostic panel: SBP/DBP marginal and residual dispersion, the BP-pair ordering diagnostic, and feasibility/rank/finite-value checks. None becomes a substitute endpoint, a retrospectively chosen quality score or a reason to discard a difficult construction. Return all three analyses and diagnostics together after the delivery seal. No desired direction is supplied.

### External-evidence admission: concrete requirement, not a completed claim

This audit **has not yet admitted an external BP original or quantitative source packet**. Metadata sufficiency must not be mistaken for evidence sufficiency. The next source-only step should admit original non-PNS studies reporting jointly measured SBP/DBP and age/sex/body-size information: useful quantities include sex/age-stratified pressure means and participant SDs, adjusted BMI-pressure regressions, and an SBP–DBP covariance/correlation or enough joint group information to support a declared dependence model. Source participant SDs must remain distinct from SEs; raw and adjusted correlations must remain distinct; treatment, seated/resting/repeat protocol and population selection must be attached to each quantity.

The protocol need not demand that every source identifies the whole joint law. It **does** need enough quantitative location/dispersion/relationship evidence for a nontrivial construction, plus declared assumptions for what is missing. One PNS paper reproducing target results is not independent construction evidence. A published equation with no dispersion support is insufficient by itself to claim a reusable joint cohort. If no defensible external packet is available within the fixed search budget, stop before generation; do not compensate with target summaries. The independent history reviewer located an existing external lead, **PMC9278591**, in `work/public_review_2026-11-01/responses/CHATGPT_REVIEW.md`: reported SBP/DBP/pulse-pressure SDs may identify a **raw** covariance, subject to same-sample/definition checks. This is not an adjusted residual covariance and is not yet source admission; inspect the original before use.

### Remaining gates before generation/reference reveal

1. Bind the parent's official BP methods receipt (occasion/device/rest/repeats), verify final-field coding and anthropometry timing/weight interpretation, and retain the unknown final-reading aggregation as a limitation. This is document review, not a target fit.
2. External original-source packet and applicability review, including quantitative roles and missing joint information. No target-derived slope or source chosen for closeness to a target effect.
3. Custodian-only **readiness** after the eligibility contract is fixed: field types, missing/sentinel codes, eligible common N, sex support, weight validity and design rank. The present audit supplies no candidate analytic N. Do not disclose target distributions, correlations or regression results to authors.
4. Exposure ledger for the exact proposed endpoints, completed independently of this feasibility review. The independent history reviewer currently reports no located previous PNS SBP/DBP adjusted/joint evaluation, but PNS remains an exposed family; an absence-of-record check is not proof of universal non-exposure.
5. Bind author model/tool interfaces, permitted evidence, review stages, generation allocation, seeds, failure handling, evaluator and target-access barrier. The user's authorization to pursue a case does not make these unprepared components already frozen.

## Conditional backup: CHNS 2009 hsCRP

**Available:** saved `schema_only/BIOMARKER_SAS_HEADER.json` explicitly lists `HS_CRP`, “High-sensitivity CRP (mg/L),” numeric; the age/sex/BMI linkage has already been established for the 2009 wave. A new hsCRP reference must start from the appropriate linked frame and its own completeness mask, not require glucose/HbA1c completeness merely because that earlier reference exists. Current candidate N is unknown.

**Possible three-analysis task:** generate age, sex, BMI and hsCRP; examine the BMI coefficient per 5 kg/m² and female-minus-male coefficient in one prespecified log-hsCRP model adjusting for age, plus an age coefficient or a prespecified conditional-dispersion contrast. Final scale and any threshold are not admitted until detection/censoring definitions and external source estimands are resolved. Do not define low-grade inflammation by deleting high target values after inspection; an acute-inflammation restriction would change the target and must have a source-supported, prospective purpose.

**Material metadata issue:** the current SAS header says `HS_CRP` in **mg/L**, whereas the retained legacy official `Biomarker_Methods.pdf` page 2 labels its `CRP` row **mg/dL**. Page 1 describes serum, immunoturbidimetry, Denka Seiken and Hitachi 7600. This does not prove that current values are mis-scaled or authorize a factor-of-ten transformation; the legacy-to-current field mapping must be verified. The page's instrument linearity range is not an established LOD or an instruction for recoding zero/below-limit observations. Known old codebook version mismatch makes this a real admission requirement.

**Source path:** the earlier admission memo identifies external Dallas Heart Study body-composition/CRP evidence, but also records capped measurements and extra fat-depot covariates incompatible with a simple BMI-only task. That lead alone is not an approved BMI–hsCRP conditional model. Further original-source admission and exact-endpoint exposure review remain necessary. CHNS hsCRP is therefore backup, not ready to execute.

## Why PNS renal/hemoglobin is parked behind these options

The PNS dictionary verifies `Z007` hemoglobin in g/dL (Plan2 rows 23–24) and `Z025` creatinine in mg/dL (rows 61–62); `Z026` is an existing eGFR derivative, not an independent measurement. The old biomarker-breadth memo identifies Han et al., DOI `10.1371/journal.pone.0150029`, Table 4, as an external source of sex-specific adjusted Hb means across eGFR bands. This is a useful original-source lead, but not yet a complete admitted task.

Creatinine assay/calibration, the eGFR equation/race convention, baseline versus laboratory age and source adjustment-set compatibility remain unresolved. The existing workbook lacks exact participant laboratory dates; using baseline age in a lab-date eGFR formula is an assumption, not an innocuous identity. Sparse eGFR strata also cannot be assumed adequate from the 8,952 file records. A single laboratory visit cannot establish chronic kidney disease. These conditions add more unresolved definition work than the BP proposal, so this audit does not recommend launching both.

## Audit scope and source pointers

- Read: retained metadata/admission documents; the separate PNS dictionary; the previously saved PNS actual-header inventory; existing acquisition/preparation metadata; CHNS saved SAS header and two pre-existing **methods-only** images. No PNS source archive worksheet or participant file was opened.
- PNS: `work/analysis-utility-preparation-2026-10-29/pns_hba1c/preparation_report.md`, `visible/field_map.json`, `custodian/raw/dictionary_lab_2013_05052023.xlsx`, saved official `exames-laboratoriais.html` (collection stage 2014–2015, venous blood; this does not prove BP timing).
- PNS official retained provenance: `https://www.pns.icict.fiocruz.br/bases-de-dados/`; `https://www.pns.icict.fiocruz.br/exames-laboratoriais/`; dictionary URL in `field_map.json`. No network call was made in this audit.
- CHNS: `work/chns_admission_2026-11-01/schema_only/BIOMARKER_SAS_HEADER.json`, `BIOMARKER_SCHEMA_AUDIT.md`, `MEASUREMENT_AUDIT.md`, `measurement_sources/methods_page_1.png`, `methods_page_2.png`; legacy method PDF original is already local.
- Earlier feasibility: `docs/REAL_CASE_ADMISSION_2026-10-30.md`, `docs/biomarker_breadth_2026-11-05/CASE_SELECTION.md`, `work/existing_data_benchmark_2026-11-02/DATA_INVENTORY.md`. Historical uses noted there are not reclassified as fresh validation.
- Broader biomedical workspace was inspected by directory/file inventory; raw files outside the selected metadata paths were not opened. Complete history review is delegated separately and is not claimed by this scientific-feasibility document.

**Disposition:** lock PNS BP as the priority *task proposal*; complete the stated metadata/source/readiness/exposure gates, then freeze and execute one experiment. Do not simultaneously expand to CRP, renal markers or many disease labels merely because the fields exist.
