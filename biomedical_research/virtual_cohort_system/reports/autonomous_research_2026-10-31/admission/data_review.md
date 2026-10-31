# Metadata admission review: NAGALA and Framingham teaching data

Date: 2026-10-31. Scope: exactly the two requested candidate families. This is a metadata decision, not a target-effect review or a generation/evaluation run. No patient-data file was downloaded, opened, or analyzed. No target paper result table was requested. No installation, model run, or paid API was used. Only this report was written.

## Recommendation

**Prefer conditional admission of NAGALA; reject the Framingham teaching version for a publication-facing real-data validation.** NAGALA has an identifiable investigator deposit and explicit CC0 licensing. Its schema, original units, categorical coding, selection rules, and event-time interpretation still require a custodian's metadata-only confirmation. There is no separate dictionary in the repository file listing. Do not infer these from convenient third-party copies or compute them from target rows in the generator context.

A fresh builder should receive only an admitted schema and independently sourced external evidence. This reviewer encountered incidental target summaries and must not serve as an allegedly blinded generator. No exposed target effect estimates or descriptive means are reproduced below.

## 1. NAGALA / Murakami Memorial Hospital, Japan

The original authors are **Okamura et al.**; Murakami is the hospital name. The investigator-linked [Dryad deposit](https://doi.org/10.5061/dryad.8q0p192) was published 2019-02-19 and links to the [original article](https://doi.org/10.1038/s41366-018-0076-3), published online in 2018 and in the 2019 volume. Its abstract describes 15,464 participants (8,430 men; 7,034 women), baseline obesity measures, and subsequent diabetes. BMI uses kg/m², waist circumference cm, and fatty liver was assessed by ultrasound. This is longitudinal follow-up, not proof that serial biomarker measurements are included in the released workbook.

The [dataset API](https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.8q0p192) reports dataset 22202, version 1, and `https://spdx.org/licenses/CC0-1.0.html`. The [file listing](https://datadryad.org/api/v2/versions/22266/files) contains exactly one file: `Data set Int J Obesity.xlsx`, 3,255,571 bytes, file 76808, MD5 `47edfb147078657a0eecfff7f9364532`. [Download endpoint](https://datadryad.org/api/v2/files/76808/download) is recorded but was not invoked. Metadata and listings were accessible without login; workbook delivery itself was not tested. [Dryad terms](https://datadryad.org/terms) permit dataset reuse under the stated instrument, with scholarly citation expected.

### Schema and selection admission gaps

| Required element | Metadata finding and admission status |
|---|---|
| Age, sex | Named in incidental secondary-method snippets; original age units and sex codes remain unverified in admitted primary metadata. Do not assume a particular binary code. |
| BMI | kg/m² confirmed in the original abstract; exact workbook header unverified. |
| Systolic/diastolic BP | Reported present in secondary-method snippets; mmHg is plausible but must be confirmed from original documentation/header metadata. |
| Glucose | Secondary descriptions identify fasting plasma glucose and HbA1c; original workbook units and HbA1c scale are unverified. Do not equate glucose reported in mmol/L in secondary publications with the workbook's original unit. |
| Lipids | Secondary descriptions identify triglycerides, HDL-C, and total cholesterol; original units unverified. LDL-C availability is not established. |
| Follow-up | Secondary-method snippets name follow-up days and diabetes/censor indicator. Original field names, event coding, censor interpretation, and repeated-measure availability require confirmation. |
| Population/selection | Secondary snippets describe Japanese health-exam attendees at Murakami Memorial Hospital during 2004–2015, with exclusions for baseline diabetes/elevated fasting glucose, medication use, liver disease, heavy alcohol consumption, and missing covariates. These are leads, not a verified primary selection contract. Do not combine differing secondary exclusion rules. |

No primary standalone data dictionary was found in the official listing. These unresolved fields prevent unconditional schema admission. The custodian should supply a small metadata artifact containing original column names/units/codes, row-versus-person structure, eligibility rules, endpoint ascertainment, and event/censor-time definition. It must omit distributions, event totals, correlations, model coefficients, and patient examples.

### Clinically coherent three-analysis case (proposal, not target-informed estimates)

If the needed fields are confirmed, a coherent question is whether adiposity-related cardiometabolic associations transport from published evidence into a whole generated screening cohort:

1. Association of BMI with systolic BP, adjusted for age and sex, using a prespecified linear model.
2. Association of BMI with fasting glucose, adjusted for age and sex, using a prespecified linear model and the same documented glucose unit in both tables.
3. Association of baseline BMI with incident diabetes, adjusted for age, sex, baseline fasting glucose, and a prespecified lipid measure, using time-to-event analysis with the documented censoring definition.

The same eligibility, transformations, adjustment sets, and estimators must run unchanged on the generated whole table and the reserved target table. This is association validation, not causal identification. Longitudinal biomarker change is not an admitted analysis because serial biomarker data have not been established. Availability of independent quantitative source evidence for this exact triad is a separate admission step; this review did not certify it.

### Source–target overlap

The Okamura paper, this Dryad deposit, NAGALA/NAfld in the Gifu Area publications, Murakami/Asahi health-check cohorts, and secondary reanalyses of this DOI may overlap. They cannot serve as independent external evidence for validating this target. Screen cohort names, hospital, recruitment dates, authors, and DOI ancestry before admission. An external publication using NAGALA only as a validation cohort is also overlapping for that component. Independent Japanese or other East Asian cohorts may be candidates only after that separate screen; no extra dataset family was reviewed here.

## 2. Framingham public teaching-data family

The official [NHLBI teaching page](https://biolincc.nhlbi.nih.gov/teaching/) offers the teaching dataset by request and explicitly deems it unsuitable for publication because it was altered for anonymity. Its statement about public-domain research data occurs under a separate public-use heading; it should not be silently applied to Framingham teaching data. The [request link](https://biolincc.nhlbi.nih.gov/requests/teaching-dataset-request/) redirected to login. No request was submitted.

The [2021a official documentation](https://biolincc.nhlbi.nih.gov/media/teachingstudies/FHS_Teaching_Longitudinal_Data_Documentation_2021a.pdf) specifies 4,434 participants and 11,627 person-examination records, up to three examinations approximately six years apart, roughly 1956–1968, and 24-year event follow-up. The landing page instead says 20 years; use the version-specific dictionary if ever teaching with it. Variables include age (years), sex (1 men/2 women), BMI (kg/m²), systolic/diastolic BP (mmHg), casual serum glucose (mg/dL), and total/HDL/LDL cholesterol (mg/dL); HDL/LDL exist only at period 3. Missing values are periods. Selection into the teaching subset is incompletely described. The data filenames behind the request were not verified.

**Decision:** documented lawful official teaching route, but no admission for this real-data research validation. Third-party `framingham.csv` mirrors were not treated as equivalent or independently licensed. In principle the teaching schema supports cardiometabolic cross-sectional, repeated-BP, and incident-CVD exercises; the anonymization restriction and period-specific measurement availability prevent treating those as validation against unmodified clinical observations. Original Framingham publications would also be overlapping evidence if this target were used. No alternate Framingham research-access dataset was searched or substituted.

## Read budget and exposure audit

- **One deliberately targeted original research paper:** Okamura et al., DOI 10.1038/s41366-018-0076-3. Only its abstract/publication metadata were returned via the official publisher search result and repository landing page; no full article or supplement was opened. Charge this as one paper, even though the planned use was metadata. No second primary paper was deliberately opened/read.
- **Official metadata documents consulted:** Dryad landing page; dataset API; version API (`https://datadryad.org/api/v2/versions/22266`); file-list API; Dryad terms; NHLBI teaching page; request/login route; FHS 2021a dictionary. The initial canonical FHS PDF web fetch timed out; a query-string version of the same official PDF succeeded. A local PDF-parser availability check failed; no package was installed and no PDF was saved.
- **Incidental NAGALA exposure:** the Dryad landing page and the publisher search result returned the original abstract's event counts, follow-up medians, hazard ratios, intervals, and qualitative conclusions. They were not requested as evidence, copied into the schema, used to select a favorable analysis, or forwarded as numerical tuning inputs. This review cannot claim complete target-result blinding.
- **Incidental FHS exposure:** a metadata search unexpectedly returned dictionary summary tables containing baseline means and other descriptive summaries. Opening the dictionary's first pages also exposed its illustrative participant example and variable-level counts. No data-file rows were accessed. These summaries/example values are excluded from the recommendation and any model inputs.
- **Incidental secondary search snippets:** results included NAGALA reanalysis methods, variable lists, selection descriptions, and occasional qualitative target associations. Examples were PMC9352654, PMC13649437, PMC8579827, PMC11544252, PMC9980900; DOIs 10.1186/s12889-023-15442-z, 10.3389/fendo.2022.851338, 10.1038/s41598-024-84709-1, 10.1038/s41598-024-84597-5, 10.1038/s41598-022-17837-1, 10.1038/s41598-025-88478-3, 10.1038/s41598-025-89849-6, 10.1038/s41598-020-78716-1, 10.1038/s41598-026-42134-6, and 10.1038/s41598-025-99540-5. These pages were not opened as research sources and are not admitted evidence. The search engine also returned unrelated papers; they were ignored, not additional candidate families. If a global budget charges search-result snippets as paper reads, the controller should use this disclosed exposure rather than assume a two-full-paper interpretation.
- No numerical target results are carried forward in this report. A clean generation context is necessary; disclosure alone does not undo exposure.

## English note for the controller

NAGALA is a credible open-data candidate, not yet a fully admitted benchmark. Confirm the original schema and follow-up semantics without releasing target summaries, then freeze the independent-evidence construction and three analyses before custodian evaluation. The Framingham teaching data should remain a teaching resource, not the reserved real clinical target for a publication-facing validation.

## Dated correction — 2026-10-31: prior workspace exposure found

**The provisional preference for NAGALA as a fresh validation target is withdrawn pending the root controller's exposure and freshness adjudication.** The original metadata review did not check prior use across the broader workspace; it established repository provenance and access, not target novelty within this project.

After that review, the root controller reported a pre-existing NAGALA workbook at `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/cross_study_virtual_cohort_pilot_2026-10-25/data/target_reserved/nagala/Data_set_Int_J_Obesity.xlsx`, with related earlier protocol, results, and case-population-audit documents from 2026-10-25. This correction records the controller's finding; this reviewer has not inspected those files, patient rows, or numerical target results.

The earlier conditional recommendation remains above as historical text and must not be read as current admission of a fresh benchmark. Repository openness and a fresh generator context do not by themselves resolve prior workspace exposure. The root controller will examine only the earlier protocol/admission information needed to determine whether NAGALA has already been used and what claims, if any, remain permissible. No additional web search or raw-data access was performed for this correction.
