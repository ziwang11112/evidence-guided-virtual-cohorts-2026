# CHNS schema-only audit plan

1 November 2026. The user has explicitly consented to the CHNS Terms and requested the necessary codebooks/data and restored automatic progression. The controller handles acceptance, browser access, downloads and scheduling; the earlier pending-consent wording in the historical checkpoint is superseded by that instruction. This plan changes no state and does not claim that any newly requested transfer has completed.

**Purpose:** establish whether a coherent, versioned CHNS reference can support a later independently reviewed whole-cohort generation task. This unit selects no final scientific question, target effect direction or generator. F2 remains unfrozen; three family slots are exhausted; newly deeply audited original studies remain **0/6**. Codebook/methods review is metadata work, not an original-study audit or evidence of method efficacy.

## 1. Minimum file sequence

Reuse locally verified copies before any transfer. The controller's current download ledger, including concurrent transfers, determines remaining budget. Preserve the existing 200 MiB per-file and 500 MiB cumulative caps; displayed decimal sizes do not establish exact byte lengths.

| Priority / file | Why needed and acquisition condition |
|---|---|
| Existing `Biomarker_Methods.pdf` and `Blood-Collection-Protocol_English.pdf` | Already acquired and hashed in [MEASUREMENT_AUDIT.md](MEASUREMENT_AUDIT.md). Reuse their measurement/procedure findings; do not download again. They do not prove released-record compliance. |
| Official `C10BIOMARKER.pdf` dictionary, linked in the earlier [access audit](../real_case_admission_v0_2026-10-31/access/CHNS_ACCESS.md) | Resolve actual biomarker names, types, units, missing codes, linkage fields, assay/collection indicators and release compatibility. Confirm the document's version/date and relationship to `biomarker_09.sas7bdat`; the filename alone is insufficient. Exclude its numeric distribution sections from the review packet. |
| `pexam_00.pdf`, versioned file **7504991** | Determine whether the examination release contains required contemporaneous anthropometry, age/sex or eligibility fields and how wave/repeated observations are represented. This small codebook precedes the large examination-data decision. |
| `mast_pub_12.pdf` **7504949** and `surveys_pub_12.pdf` **7504999** | Resolve identifier continuity, survey participation/wave definitions, corrections and where required demographic/linkage fields actually reside. Their data counterparts are conditional, not automatic downloads. |
| Official identifier, missing-value and analysis-unit documentation referenced by the CHNS documentation index | Read only what is necessary to settle ambiguities left by these dictionaries. Identify exact documents before transfer; no speculative family expansion or unrelated documentation collection. |
| `biomarker_09.sas7bdat` **7505013**, biomarker DOI **10.15139/S3/GQ9GPP**, v1.0 | Candidate measurement reference. Acquisition may proceed under the user's authorization and controller allowlist. Keep rows sealed from the construction context; schema inspection uses header/dictionary metadata only. Its CC0 terms do not replace companion-release terms. |
| Conditional companion data: `pexam_00.sas7bdat` **7504992**; `mast_pub_12.sas7bdat` **7504950**; `surveys_pub_12.sas7bdat` **7505000** | Download only files the dictionaries show are needed for the eventual population/measurement contract. Companion DOI **10.15139/S3/9PQ5KV**, v1.0. Names and displayed sizes do not prove 2009 compatibility. Verify exact length before the approximately 191.8 MB examination file; do not acquire the unrelated 280.7 MB physical-activity file. |

Versioned companion identities, displayed sizes and publisher checksums are in [FILE_ACCESS_AUDIT.md](FILE_ACCESS_AUDIT.md); biomarker metadata are in [CHNS_ACCESS_UPDATE.md](../post_review_semantics_2026-11-01/CHNS_ACCESS_UPDATE.md). A publisher MD5 is not an independently computed local hash. Record actual bytes and SHA-256 after each transfer; retain official terms/citations locally. No duplicate download or browser action is performed by this planning unit.

## 2. Field inventory to establish, without values

The audit should return one row per candidate field with: release/file/version; exact stored name and label; storage type and format; documented unit; code/value-label definitions; missing/special codes; measurement occasion; source document/page; intended role; unresolved ambiguity. Record definitions, never observed frequencies or participant examples.

Minimum common requirements are person-linkage key(s), wave/occasion, unit of observation, repeated-measure distinction and documented join cardinality. Resolve whether household/community keys are needed to disambiguate linkage without exposing their values. Record the intended key recipe, not a completed join. Preserve leading zeros, string versus numeric identifiers and special missing values; never infer cross-wave identity from matching row order.

Age or birth-date-derived age, sex coding and survey participation are candidate population-definition fields. Identify their time reference and correction rules before treating them as compatible with 2009 biomarkers. Anthropometry—height, weight, waist or a supplied BMI field—is conditional on the eventual task. If BMI must be derived, document units, formula, repeated-measure rule and contemporaneous pairing before use. No observed age/sex composition, BMI distribution or eligibility count is needed for this schema stage.

Inventory available biomarker names broadly enough to avoid prematurely restricting whole-cohort utility to one marker. For the already discussed fields, keep `GLUCOSE`, field `Y48_1` and HbA1c `Y50` separate. Verify actual names and released-file units; `Y48_1` lacks its own unit row in the reviewed methods table. Preserve serum versus plasma and whole-blood distinctions. Record assay/laboratory/instrument/collection-time and fasting-status/duration fields if documented; absence remains explicit. The manual's intended fasting schedule is not proof of participant compliance.

Medication, diagnosis, pregnancy, survey weight/design or additional adjustment fields are required only if the later scientifically justified population or estimand needs them. Verify availability and definitions; do not invent exclusions, assume weighting, or acquire extra files merely because such fields might exist.

## 3. Leakage controls

- Codebooks may mix schema with frequencies, minima/maxima, means, percentiles or example records. Isolate dictionary/definition sections before passing text or page images to the reviewer. Do not dump a complete codebook into the model context. Log any incidental result exposure precisely; do not reprint it or silently claim continued blindness.
- If acquired data need header verification, use a verified metadata-only path that does not materialize or print records. A file-header record count, if incidentally shown, is not an eligible sample count. Do not run `head`, descriptive summaries, value counts, plots, correlations, missingness summaries, eligibility filters or joins in this unit. Actual key uniqueness/match rates and sample feasibility require a separately bounded custodian step; label them untested here.
- Keep raw/corrected/derived participant rows, full third-party PDFs, screenshots and browser/session details local. A constructor receives only the later approved evidence and population/task contract. Target-derived marginal summaries cannot quietly enter that contract as “metadata.”
- Apply [EXPOSURE_MAP.md](EXPOSURE_MAP.md): urate/HOMA and lipid–cognition/BMI/sex-age results are already exposed; cross-system/magnesium concepts are incidentally exposed. New columns, subgroups or transformations do not automatically create unseen confirmation. External source evidence must be distinguished from target-family summaries.

## 4. Audit output and exit gate

Produce a concise metadata field map, minimum-file decision, proposed linkage/occasion specification and unresolved-definition list. Mark each assertion **documented**, **ambiguous** or **not found**; header compatibility, actual join validity and biological applicability are separate questions. Do not convert missing definitions into defaults or infer units from plausible values.

Schema sufficiency permits the next bounded admission step, not generation or F2 approval. Before F2, the controller still needs genuinely external source evidence within the six-study limit; approximately three scientifically useful estimands chosen without target effects; explicit selection, adjustment, weighting, transformation and uncertainty semantics; prospective exposure classification; supported operators and independent review. Any required unit conversion or unsupported source estimator needs a separately reviewed implementation scope; the existing semantic identity gate supplies no automatic conversion. Whole-cohort construction remains central, with optional observed-data regimes treated separately.

If required measurements or compatible keys remain unresolved, return the exact missing definition or necessary document. Do not select an alternative endpoint for a favorable result, claim an untested join works, consume a fourth family, or redefine the case by intuition.
