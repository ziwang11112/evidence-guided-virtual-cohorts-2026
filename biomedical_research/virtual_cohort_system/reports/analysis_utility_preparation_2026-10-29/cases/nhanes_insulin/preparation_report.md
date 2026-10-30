# NHANES fasting-insulin preparation

Prepared **1,961 eligible adults** from NHANES 2015–2016. The visible input contains only opaque row IDs, age, sex, BMI and fasting glucose in mg/dL. The entire insulin measurement, its alternate unit, detection-limit flag, original respondent identifiers and survey design data remain in `custodian/`.

This is a prepared enrichment task and a validated input table. No generator was run, no target distribution or association was computed, no literature model was fitted, and no source-registry approval was created. Public-data downloads belong to custodian preparation. The downstream builder budget remains **0 source queries, 0 source downloads and 2 revisions**, using the separately prepared shared evidence packet.

## Cycle choice and the exact freshness boundary

The recorded inventory used `rg --files` over `biomedical_research`, followed by filename matching and a top-level protocol-metadata allowlist. It covered 16,605 filenames within a maximum of eight relative path components and selected metadata from 54 JSON protocol/task files of at most 200,000 bytes. The exact paths, globs, allowlist and timestamp are in `freshness_inventory.json`; `inventory_freshness.py` reproduces the scope.

Review, runtime, replica, Git snapshot, source-replay, execution, candidate and run trees were excluded, along with package environments and this new preparation directory. The initial exploratory filename-only listing additionally returned names in source-replay, execution and Git snapshot trees; no contents were read there, and these replicas were excluded from the recorded bounded inventory.

The inventory found `insulin_feature_enrichment_2026-10-27/custodian/raw/INS_J.xpt`, its codebook and evaluation-related **filenames**. This is sufficient to treat 2017–2018 as previously used. No `INS_I` or `INS_H` filename, nor a 2015–2016/2013–2014 insulin entry in the whitelisted protocol metadata, was detected in this scope. The 2015–2016 files were then verified as available from CDC and chosen. No prior result contents or participant files were opened for cycle selection, and no result was used to choose the cycle.

**This task is not certified clean or historically unexposed.** Filename absence cannot rule out unnamed analyses, non-whitelisted protocol contents, excluded trees, prior chats, other workspaces or outside analyses. A later agent-slot listing incidentally returned historical completed-agent summaries containing unrelated HDL aggregate results. They were not insulin results and were not used for this task; this disclosure distinguishes the file-inventory boundary from incidental chat-tool exposure.

## Official provenance and definitions

Six official XPT files and their six codebooks were downloaded without copying any prior experiment's data. Exact URLs, byte sizes and SHA-256 hashes are in `source_manifest.json` and `artifact_manifest.json`.

| Component | Official metadata | Role |
|---|---|---|
| DEMO_I | [CDC demographics](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/DEMO_I.htm) | RIDAGEYR, RIAGENDR, RIDSTATR, RIDEXPRG; masked design fields and weights remain hidden |
| BMX_I | [CDC body measures](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/BMX_I.htm) | BMXBMI in kg/m² |
| FASTQX_I | [CDC fasting questionnaire](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/FASTQX_I.htm) | Morning is **PHDSESN = 0**; fasting hours are PHAFSTHR + PHAFSTMN/60 |
| GLU_I | [CDC fasting glucose](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/GLU_I.htm) | LBXGLU in mg/dL, preserved as released |
| INS_I | [CDC insulin](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/INS_I.htm) | Hidden LBXIN in µU/mL; WTSAF2YR; LBDINLC; hidden LBDINSI duplicate |
| DIQ_I | [CDC diabetes questionnaire](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/DIQ_I.htm) | DIQ050 current insulin-use classification |

Age is age at screening. Adults coded 80, which includes everyone aged 80 or older, are excluded by the prespecified upper age of 79. RIAGENDR is the public file's two-category variable labelled “Gender,” mapped to `male` and `female` in the task's `sex` field.

Fasting duration uses the official food-fast hours and minutes, not a rounded hours-only cutoff. The additional intake questions in FASTQX_I were not used as extra exclusions: the task uses recorded food-fast duration and a positive official fasting subsample weight. This definition may not capture every possible intervening intake. Fasting duration duplicates in INS_I and fasting weights in GLU_I were checked against their primary preparation fields.

The released 2015–2016 glucose values already incorporate CDC's instrument harmonization for specimens measured on the prior analyzer. This package makes no additional glucose correction and does not pool cycles.

## Prespecified eligibility and retained counts

`preparation_spec.json` fixes the rules before the first row parse. The failed parser attempts and their pre-read freezes are preserved; the repairs changed data decoding and optional-field handling, not eligibility thresholds or target-dependent rules.

| Sequential eligibility step | Retained |
|---|---:|
| DEMO_I base | 9,971 |
| Age 20–79 | 5,343 |
| Interviewed and MEC examined, RIDSTATR = 2 | 5,131 |
| Morning examination, PHDSESN = 0 | 2,435 |
| Finite fasting duration, 8.5 to less than 24 hours | 2,215 |
| Positive finite fasting subsample weight | 2,141 |
| Exclude recorded pregnancy | 2,117 |
| Confirm nonpregnancy for women aged 20–44 | 2,104 |
| DIQ050 explicitly reports no current insulin use | 2,005 |
| Finite covariates and valid sex category | 1,993 |
| Measured finite insulin; no magnitude filter | **1,961** |

Pregnancy status is publicly released only for women aged 20–44. These women must have RIDEXPRG = 2; unknown or missing status is excluded. All recorded RIDEXPRG = 1 participants are excluded. Older women are retained, with **576 final participants** in the group whose pregnancy cannot be established from the public field. Thus “nonpregnant” applies where publicly ascertainable; this is not an assertion that pregnancy is ruled out for every participant.

DIQ050 is defined for both sexes aged one year or older. The released DIQ_I has 9,316 explicit “No,” 256 “Yes,” one refusal, two “Don't know,” and no missing DIQ050 values. Among respondents with DIQ010 = 2 (no diagnosed diabetes), 8,563 explicitly report no insulin use, three report use, one refuses and one does not know. Requiring DIQ050 = 2 therefore does **not** restrict this cycle to diagnosed diabetics or misclassify structural missing values. It excludes current users and unresolved answers. This remains self-report. `insulin_use_classification_counts.json` records the audit without insulin laboratory statistics.

CDC's released LBXIN values are retained exactly, including its lower-limit-of-detection substitution. The documented insulin LLOD is 1.0 µU/mL; below-LOD values are CDC's LLOD/√2 fill values, with LBDINLC retained under custody. There is no positivity filter, winsorization, percentile exclusion, upper bound, replacement or other target-magnitude trimming. “Measured finite” includes the official below-LOD fills. The target's physiologic nonnegative output contract is a representation rule, not a reference-data selection rule.

## Custody, reproducibility and verification

`visible/observed.csv` has exactly five columns in contract order: `row_id`, `age_years`, `sex`, `bmi_kg_m2`, `fasting_glucose_mg_dl`. `visible/task_metadata.json` and `visible/field_map.json` describe their definitions. `task.json` is the schema-valid enrichment contract. NHANES, its expanded name, PNS and the Brazilian National Health Survey are excluded from the downstream published-evidence policy.

`custodian/reference.csv` binds opaque IDs to hidden LBXIN, its unit duplicate, detection-limit flag, SEQN, SDMVSTRA, SDMVPSU and weights, plus eligibility audit fields. The original XPTs and full codebooks, which contain public frequencies, also stay under custody. Only the visible table and explicitly admitted metadata/evidence should enter a builder session. The directory layout is an information boundary, not an operating-system access-control guarantee.

Opaque IDs are HMAC-SHA256 tokens generated with a random key held only in `custodian/row_id_key.bin`; rows are sorted by those opaque IDs. Exact re-creation requires the retained key and original official bytes. A fresh key creates a different ID map and ordering while leaving eligibility unchanged. Neither original IDs nor a mapping key appears in visible artifacts.

The installed pandas XPORT converter misdecoded an exact IBM zero as a tiny positive float. The preparation now recognizes zero from the **original all-zero eight-byte encoding**, with no numerical threshold. Synthetic 0, 1, 2 and −1 encodings verify the fix and unchanged nonzero decoding. pyreadstat was unavailable because Windows Application Control blocked its native DLL; no policy bypass was attempted. GLU_I also lacks the generic codebook's named LBDGLULC field, so that flag is not fabricated; insulin's actual LBDINLC field remains preserved. Details and original attempts are in `preparation_repair_log.json` and `custodian/`.

Run from an environment containing pandas, NumPy, requests and Beautiful Soup:

```powershell
python acquire_official.py
python prepare.py
python finalize_package.py
```

The acquisition script checks CDC codebook identity and SAS XPORT headers, preserves original bytes, and records hashes. The preparation checks those hashes, source-ID uniqueness, one-to-one merges, weight consistency, fasting-duration consistency, final reference alignment, and the exact visible-column boundary. Existing `cohort_harness.contracts.validate_task` and `validate_input` passed for both the in-memory observed table and the serialized CSV. `preparation_validation.json` records the environment and actual check scope.

A fresh-context independent reviewer inspected only permitted code and metadata and found no substantial issue. Its official metadata lookup incidentally included a general demographic sampling table, with no insulin outcome statistics or participant rows. `metadata_review.json` records the review scope and limitation. `finalize_package.py` verifies the visible contract and source hashes, updates the complete file manifest, and verifies every binding without opening hidden reference rows.

Any HOMA-IR analysis must derive it algebraically from generated insulin and observed glucose. It is not an independently measured reference outcome, and agreement on it cannot count as independent target confirmation. All scientific utility evaluation remains downstream and unperformed here.
