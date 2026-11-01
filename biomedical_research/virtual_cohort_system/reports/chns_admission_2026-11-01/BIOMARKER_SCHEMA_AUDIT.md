# CHNS biomarker schema audit — 1 November 2026

**Decision: the legacy C10BIOMARKER codebook is not a compatible data dictionary for the downloaded `biomarker_09.sas7bdat` without a separately verified mapping.** The actual SAS header provides current field names and labels, but does not supply demographics, fasting or medication information. F2 remains unfrozen; no clinical distribution or effect was calculated.

## Bounded inspection and provenance

The local [official codebook](https://chns.cpc.unc.edu/wp-content/uploads/C10BIOMARKER.pdf) has 36 pages, 238,242 bytes, SHA-256 `44bd3be3e37d67ff0ae6014c412b77f6bfe8b1d678b27c2f32c8c38beb739c7f`. It contains empirical summaries beside definitions. This audit did **not** extract full-page text or render full pages. PyMuPDF drawing geometry and the table-header band identified the grid boundary **before Format**, stricter than stopping before Length. Body extraction was confined to Variable Name, Variable Label and Type, excluding the top file-observation-count header and the Mean/Range/Frequency/Percent columns. Page-specific crop rectangles are recorded in `schema_only/BIOMARKER_DEFINITIONS.json`. Cropped definition-only images of pages 1, 21, 22 and 33 were visually inspected.

Separately, `pandas.read_sas(..., iterator=True)` was used only to inspect `column_names`/column objects and their labels/types/formats in the acquired private SAS file. No `read()`, `get_chunk()`, row iteration, value summary, sample filtering or join was performed. The reader was closed. Header metadata was saved to `schema_only/BIOMARKER_SAS_HEADER.json`; raw participant identifiers were never extracted or printed. The file has **49 declared columns**; this is a schema dimension, not an eligible sample count.

## Codebook versus actual SAS header

| Object | Legacy definition columns | Actual header finding | Consequence |
|---|---|---|---|
| Person key / wave | Page 1 has `HHID` (household identifier tied to C05MAST), `LINE` (household-member line) and `SURVEYED` (2009 participation label). | `IDind` is labelled individual ID; `wave` is labelled survey year. `HHID`, `LINE`, `SURVEYED` are absent. | Do not reconstruct `IDind` from legacy household/line fields or assume key uniqueness from labels. Companion-file and key validation remain separate work. |
| Age / sex | Page 1 has `AGE`, labelled calculated years to two decimals, and `GENDER`. | Neither field exists. | Adult eligibility and age/sex adjustment require compatible external files; no coding or completeness is established here. |
| Quality flags | Page 1 defines `FLAG_GLUCOSE` and `FLAG_LIPIDS` as questionable-value indicators. | Neither flag exists. | Do not invent, transfer or reconstruct these flags from old summaries or numerical cutoffs. |
| Central/non-field glucose | Page 22 defines `GLUCOSE` as CJFH glucose in mmol/L; page 23 includes an mg/dL derivative. | `GLUCOSE` is labelled blood glucose in mmol/L; `GLUCOSE_MG` has an mg/dL label. | Units are directly supported by the current header. The header alone does not prove laboratory provenance or the derivation/equality of paired-unit fields. |
| Field glucose | Page 21 has `Y48_1` in mmol/L; page 22 has `Y48_1MG` in mg/dL. | `Y48_1` is absent. `Glu_field` explicitly says field glucose in mmol/L; `Glu_field_MG` has an mg/dL glucose label. | This resolves the actual field-glucose unit question, but is not proof of a historical rename or row-for-row equivalence. Preserve field versus non-field measurements. |
| HbA1c | Page 33 labels `Y50` and related derived fields with **mmol/L**. | `Y50` is absent. `HbA1c` explicitly has **%** in its label. | The legacy label conflicts with both the actual header and the official methods table's percent unit. Do not convert or relabel current HbA1c using that legacy label. |
| Reference/derived variables | The codebook includes `_CD`, `_CS`, `_SD`-style reference/classification/dispersion fields. | These codebook flags/derivatives are not reproduced as a general family in the acquired header. | Such labels do not provide current missingness codes, participant uncertainty or sampling SE. |

The actual `INS` label mentions both 2009 and 2015 unit conventions and has a character-encoding artifact around the micro symbol. This signals that a harmonized label can survive in a year-named file; it does **not** establish which waves actually occur. No wave values were read. Other label discrepancies, including transferrin unit wording, likewise argue against treating the old methods sheet/codebook as a universal conversion map. Preserve literal labels and resolve only variables required for a prospectively fixed analysis.

## Fasting, medication and measurement scope

No current-header field explicitly records fasting duration/compliance, collection time, glucose-lowering medication, diabetes treatment or the two legacy questionable-value flags. No age/sex field is present. Absence here is a **column-inventory finding**, not a claim that such information is unavailable anywhere in CHNS. The codebook's definition columns inspected do not establish replacement fasting/medication fields for this SAS release.

The prior assay/manual audit remains applicable as intended-procedure metadata: serum glucose fields must not become plasma by relabelling; the provincial HbA1c protocol and documented fasting/storage ambiguities are not resolved by a numeric variable label. Header units are necessary but insufficient for common assay, calibration, population or estimand assumptions. No identity conversion or renaming dictionary is approved by this note.

Whole-cohort generation is not ruled out by this mismatch, but neither is feasibility established. Before admission, independently identify compatible demographic/physical-examination variables and IDs, validate a permitted key/wave linkage, resolve measurement and eligibility definitions, and freeze the intended analyses without inspecting their clinical outcomes. This audit did not join the biomarker file to mast or physical-examination files.

## Exposure record without values

The coordinator reported an incidental first-page view during browser saving that included summary areas for `HHID`, `LINE`, `AGE`, `GENDER`, `SURVEYED`, `FLAG_GLUCOSE`, `FLAG_LIPIDS`, `UREA` and `UREA_CD`. Exposure classes are: identifier summaries; demographic summaries; survey-participation summaries; quality-flag/reference-category summaries; and a clinical-variable summary. **No means, ranges, counts, frequencies, percentages or participant identifiers are reproduced here.** This report records the coordinator's disclosure rather than repeating that inspection. The companion audit's separate exposure record remains separate.

This reviewer subsequently used schema-only crops and header-only inspection. The earlier exposure prevents a blanket claim that the coordinating context is globally unexposed; a future constructor needs its restricted approved packet. It does not justify using exposed summaries to choose a favorable analysis or supply generator parameters.

No state files were edited. No new download was made by this subtask; acquisition/consent/checksum accounting belongs to the coordinator's transfer ledger. No new original study was deeply audited: **quota remains 0/6 used**. Codebook originals, SAS data and local crops/header extracts remain local; no public export is implied.
