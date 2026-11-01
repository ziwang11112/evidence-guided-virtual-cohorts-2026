# CHNS acquisition and linkage checkpoint

1 November 2026. The user explicitly authorized the CHNS Terms acceptance, necessary codebooks/data, careful review and restored automatic continuation. The access obstacle is resolved. **This is an acquisition/schema/key-integrity result, not a new scientific validation or an admitted F2 case.**

## What was obtained and checked

Four codebooks and four SAS data files were acquired. The current downloads total **230,687,569 bytes**; adding the earlier two methods/protocol documents gives **232,515,025 bytes** (about **221.7 MiB**), below the 500 MiB ceiling. The largest file, examination data, is **201,113,600 bytes**, below the 200 MiB file ceiling. Exact companion sizes were read from the official Dataverse JSON export before transfer. Seven Dataverse files match their publisher MD5 checksums; all eight current files have local SHA256 hashes. The separate older biomarker PDF has a local checksum but no independently verified publisher checksum. See [ACQUISITION_LEDGER.json](ACQUISITION_LEDGER.json) and [FILE_SIZE_PREFLIGHT.json](FILE_SIZE_PREFLIGHT.json).

Dataverse downloads and the unchanged Terms acceptance used the requested requested Chrome extension. The biomarker dataset separately displays CC0. The older biomarker-codebook link was verified on the official CHNS page; plugin `downloadMedia`, PDF toolbar and Alt-click attempts returned no saved file. A bounded HTTPS transfer of that same public URL then saved the document. No desktop UI fallback, account, application or external contact was used. Browser traffic and unsuccessful browser-save traffic were not metered; the byte total counts saved downloads and is not a claim about total network traffic.

The companion-file selection was independently justified from definitions: examination supplies height/weight, master supplies gender, and survey-wave index supplies contemporaneous age. Unneeded physical-activity and unrelated files were not acquired. Patient-level files, full codebooks, local screenshots and the terms handoff record remain local.

## Schema findings that change implementation

1. **The old biomarker dictionary is not the current release schema.** It describes 197 variables and a blood-draw organization. The acquired SAS header contains 49 fields with `IDind` and `wave`; demographic and quality-flag fields shown in the old document are absent. The current fields include `HbA1c` and `Glu_field`, rather than assuming that old names `Y50` and `Y48_1` can be used directly.
2. **Units require field-specific reconciliation.** Actual SAS metadata labels `HbA1c` as percent and `Glu_field` as mmol/L. The older dictionary's `Y50` unit conflicts with the methods table and current field label. It must not trigger a silent conversion. File labels alone do not certify assay equivalence or transportability. See [BIOMARKER_SCHEMA_AUDIT.md](BIOMARKER_SCHEMA_AUDIT.md).
3. **Companion dictionaries also require actual-file checks.** Examination has the expected 206 fields and includes 2009; master has 9 fields. The acquired surveys file has 19 fields and includes 2015, whereas the supplied older dictionary describes 20 fields and inconsistent wave coverage. Independent comparison identifies the absent dictionary field as `AGE_DAYS`; the actual release has `AGE`, not both age fields. The remaining semantic differences must be reconciled before a clinical eligibility specification is implemented.

## Key-only audit

The separately reviewed [audit script](audit_schema_keys.py) reads file headers and decodes SAS chunks internally, retaining only identifier/year columns. It does not retain a clinical merged cohort, print participant identifiers, calculate clinical means/correlations, or choose endpoints. Before joining it checks decoded/header counts, missing keys, finite integral exact-range identifiers, uniqueness and join cardinality. Review identified an incomplete-key validation edge; it was fixed before the first execution. Output: [SCHEMA_AND_KEY_AUDIT.json](SCHEMA_AND_KEY_AUDIT.json).

| File | Total records in file | Records with wave 2009 | Duplicate declared-key rows | Missing-key rows |
|---|---:|---:|---:|---:|
| Biomarker | 9,549 | 9,549 | 0 | 0 |
| Examination | 110,449 | 11,929 | 0 | 0 |
| Person master | 39,674 | Not a person-wave table | 0 | 0 |
| Surveys | 143,564 | 12,178 | 0 | 0 |

| Link from 9,549 biomarker records | Matched | Unmatched | Cardinality verified |
|---|---:|---:|---|
| Examination, individual + year | 9,516 | 33 | One-to-one |
| Person master, individual | 9,549 | 0 | Many-to-one |
| Surveys, individual + year | 9,548 | 1 | One-to-one |

These are linkage counts, **not** adult, complete-case, fasting-compliant or analysis-eligible sample sizes. No unmatched record was silently discarded. Successful person-wave linkage does not prove same-day blood/anthropometric collection, complete clinical fields, correct missing-code decoding or appropriate study-population transport.

An [independent recomputation](INDEPENDENT_KEY_AUDIT.md) used **pyreadstat/ReadStat with explicit ID/year columns**, Python Counter and set membership, rather than reusing the root's pandas/merge calculation. The reviewer computed first and opened the root result afterward. All header/record counts, file hashes, duplicate/missing-key counts, wave counts and linkage counts agree. No clinical values or participant identifiers were reported. This verifies the integrity calculation, not a biological finding.

## Exposure and next decision

The PDF schema extraction initially exposed marginal-summary cells and partial summary fragments. The root's first-page old biomarker view also exposed several marginal summaries. They are recorded in the [dataset exposure registry](../../docs/DATASET_EXPOSURE_REGISTRY.md), [companion audit](CODEBOOK_SCHEMA_AUDIT.md) and biomarker audit. No target joint relationship or clinical effect was computed. Do not call this cohort globally unseen, use those summaries as independent external sources, or feed them to the generator.

Next: resolve actual-file semantics and missing/cleaning rules; obtain genuinely external original-study evidence within the existing **0 of 6** consumed quota; define approximately three scientific estimands based on evidence and measurement availability; independently review and freeze F2. Only then construct/generate and evaluate under the unchanged bounded protocol. The three candidate-family slots remain consumed; no new family is authorized. No old revealed target, frozen generator, module or receipt was modified.

The deleted `automation-4` was replaced by a single ACTIVE `chns` heartbeat in the same chat, every 30 minutes. This foreground work is not a scheduled run; the verified historical count remains **1**. Automatic continuation stops at the pre-existing case/quota/resource conditions and starts no new work after 14 November 2026 (America/Chicago).
