# Independent HAALSI definition and availability review

Reviewer: `/root/context_bridge_review`, 2026-11-02. Definition/audit producer:
`/root/context_unit_contract`; acquisition coordinator: `/root`.

**The definition-only review supports the bounded baseline-file acquisition,
and the subsequent schema/ID/physical-missingness audit is independently
confirmed. HAALSI remains a provisional K01 candidate.** This is not target
admission, a frozen analysis population, independent clinical validation or a
campaign release. No numerical codebook summary or participant measurement
value was displayed. No clinical distribution, association or effect estimate
was computed or used in this review.

## Acquisition identity and document boundary

I recomputed the local document byte sizes, MD5s and SHA256 hashes. They match
the coordinator's official-file acquisition commitments. This was a no-network
review: official-page provenance and its displayed MD5s are recorded by the
coordinator in `HAALSI_ACCESS.json`, not independently revisited online here.

| File | Bytes | MD5 | SHA256 |
|---|---:|---|---|
| Baseline Codebook PDF | 1740530 | `57893c50d15dd0653e38ee126acdfa57` | `49d79434d4836485f2e3291ff884535b42b356821a183985d20f6d7bcbfcaa07` |
| Baseline Survey and Variables DOCX | 194943 | `898d6239a9e6a01dbd1c9c45f9d628cc` | `451d7dad209bae21b324604c95696f60143f825acedd28b12360ddb3de416c67` |
| Original `HAALSI_baseline_dataverse_14Apr2017.dta` | 19039887 | `e11a69121c7cee6726835d6106820104` | `27c968d5c9e53948bc8ee21e0a5bdc2262ed3c17f1dbafb5bb303050b6715b9f` |

The access record distinguishes the older 2016 PDF documentation from the
14 April 2017 survey/variable update and participant-file label, within baseline
release DOI `10.7910/DVN/F5YHML`, version 3.0. These are retained as distinct
documents. Listing a field in the older PDF cannot establish that a later
release supplies it, and a later document date does not resolve every older
definition. The selected-field audit of the exact acquired original Stata file
was therefore necessary. It does not certify the remainder of that release.

I reviewed `haal_si_schema_only.py`: the hash-bound PDF must have the checked
page geometry/header positions, and text retention is restricted to variable,
type, label and source columns. Observation count, mean, minimum and maximum
columns are excluded. I viewed only the six already-masked definition images
for pages 87, 88, 90, 93, 94 and 95; their summary columns were obscured. The
masking code also removes summary-word spillover beyond nominal boundaries.
No unmasked PDF summary page or empirical paper was viewed.

## Definition and color reconciliation

I inspected the pertinent DOCX OOXML rows directly, preserving text colors,
run/paragraph styles and default-style information. The color legend is from
the coordinator's official file-description record: orange denotes restricted
confidential fields, grey denotes unavailability during coding/cleaning, and
green directs use of an alternative variable. My verification concerns the
actual document colors, not a fresh online verification of that legend. The
producer corrected its report to make this attribution explicit.

The DOCX contains orange `F79646`, grey `808080` and green `00B050` markings.
The cleaned core fields `c_bs_bmi`, `c_bs_glucose`, `rage` and `rsex` have no
colored run or inherited style override. The original glucose entry/check/
re-entry rows are green and explicitly direct use of `c_bs_glucose`; original
height and weight entries similarly point to their cleaned replacements.
Colors were not flattened into a false statement that every questionnaire
field is publicly available.

The following definitions are supported by the selected rows and masked PDF:

- `c_bs_glucose` is cleaned point-of-care glucose in mmol/L, assembled from
  original CareSens readings and comments. It is not automatically a fasting
  venous-plasma laboratory value. Exact assay equivalence remains unverified.
- `c_bs_bmi` is derived from cleaned height and weight; their definitions state
  cm and kg. The actual BMI variable label is simply `BMI`, so the conventional
  BMI unit interpretation should be declared in the later contract rather than
  attributed to an explicit unit string in that label.
- `rage` is census age on **31 July 2014 at sample selection**, not automatically
  age on the interview date. `rsex` is census-preloaded respondent sex.
- `c_bs_hrslastate` is a constructed timing measure with a previous-day
  assumption; `c_bs_fasting8hr` derives from it. Neither proves a universally
  fasting sample.
- The codebook lists `prim_key` as a character primary key; I did not locate
  that token in the DOCX. Its actual string type and integrity were subsequently
  verified in the acquired file.

Locators are retained in `HAALSI_CODEBOOK_SCHEMA.md`; the independent DOCX
checks include all-table, zero-based table 41 rows 32/40 and table 42 rows
18/20. No HbA1c/glycated-hemoglobin definition was located in the reviewed
documents. Hemoglobin in g/dL must not be substituted for HbA1c. The participant
audit used a fixed whitelist and did not establish that no HbA1c exists anywhere
in this or another release.

The legacy composite-diabetes definitions remain unresolved. Masked PDF p. 94
calls the narrow construct current treatment but cites `cm007` sex-specific
diagnosis questions, while the broad diagnosis construct cites `cm010`, whose
DOCX wording is current treatment. The composite's greater-than-eight-hour
wording also differs from the fasting field's at-least-eight-hour wording.
These discrepancies were retained; no field swap, boundary choice or composite
outcome was silently implemented. They do not prevent auditing continuous
glucose availability.

## Pre-first-run script review

Before the first actual-file audit, I reviewed
`haalsi_data_schema_audit.py` at SHA256
`6c15cc3c56170e868c3fc1f0931d70657d1cd2ee98f1ae57161f18ca625aeafe`
and confirmed that its result did not yet exist. The script pins byte size,
MD5, SHA256 and pandas 3.0.3; parses the same verified bytes through `BytesIO`;
reads metadata first; and materializes only the prescribed 13-column view.
It emits selected labels/dtypes, physical missingness, exact-ID aggregate
counts, joint core availability, and tokens for only six categorical fields.
It emits no ID tokens, measurement values, moments or category frequencies.

Native Stata missing values, including tagged missing, are preserved and
counted explicitly. Empty/whitespace strings and other native NA are separate
missing classes. Labelled numeric sentinels are not automatically reclassified,
and no range, diagnosis, fasting or other clinical eligibility filter is applied.
Unexpected warnings/errors stop with the exception class only; an existing
result is never overwritten. This was cleared for the one bounded audit,
not for general clinical analysis.

The author reports one invented in-memory self-check, followed by the
reviewed actual-file audit succeeding on its first attempt. I did not rerun
that self-check or any old test suite.

## Independent prescribed recomputation

After the author's audit, I made **one** independent read-only recomputation
from the same hash-verified original bytes and fixed 13-column whitelist.
The independent inline code used separate missingness loops, ID counters and
joint-availability logic; it did not import the author's counting helpers.
It used the same pinned Stata reader, so this is a separate arithmetic check,
not validation with an independent file-format backend.

All 13 selected field labels, value-label dictionaries, dtypes and missingness
records matched, as did all six permitted category-token sets and every
prescribed aggregate. The independently confirmed results include:

| Permitted check | Result |
|---|---:|
| File rows / columns | 5059 / 1933 |
| Selected fields present | 13 / 13 |
| Nonmissing unique primary keys | 5059 |
| Missing IDs / duplicate excess / rows in duplicate groups | 0 / 0 / 0 |
| Missing age / sex | 0 / 0 |
| Missing BMI | 370, all `.e` |
| Missing glucose | 433: `.` 417, `.d` 15, `.e` 1 |
| Age, sex, BMI and glucose all physically present | 4394 |
| At least one of those four physically missing | 665 |

The actual value-label dictionary resolves sex coding as 1=Male and 2=Female;
fasting and the selected flags use 1=Yes, 2=No. These are verified file metadata,
not inferred biological labels or a 0/1 coding assumption. No category
frequencies were calculated or disclosed. No meaning was invented for the
letters of tagged missing values.

**4394 is physical availability, not final analysis N.** Measurement/range
flags, nonfinite or sentinel handling, age/time definition, fasting choices,
eligibility, sampling design and the eventual estimands still require a
prospective case contract. Counts and file metadata are not constructor-facing
clinical relationships or calibration inputs. The audit does not establish
representativeness, source overlap, transport validity or an independently
admitted K01 case.

## Retained review commitments and closeout

| Artifact | SHA256 |
|---|---|
| `HAALSI_CODEBOOK_SCHEMA.md` | `49e145fabfb3020b806edcd1f9512ca65da313c4b6dbe607de2d830fe2203511` |
| `haal_si_schema_only.py` | `4e3d2095a2ce095722d0f114c43351a4a595c7838fb78861d33023394b62e3c9` |
| `haalsi_data_schema_audit.py` | `6c15cc3c56170e868c3fc1f0931d70657d1cd2ee98f1ae57161f18ca625aeafe` |
| `HAALSI_DATA_SCHEMA_AUDIT.json` | `8d062862a640765308f4003cdfcf6853e33565f5e82c75cfadb79edc81ab3517` |

The document-only checkpoint preceded the acquired-file audit; its historical
statement that participant data had not yet been opened remains correct for
that stage. The later two authorized schema/count passes (author and reviewer)
are distinct from target-effect evaluation. Neither created a cohort, fitted
evidence, ran a generator or computed a clinical effect.

No additional paper search, network call, study, test-suite rerun, STATE/export
or Git edit occurred in this reviewer unit. The only reviewer-authored
repository artifact is this report. Raw documents, masked intermediates and
participant data remain local; this review is original prose and permitted
aggregate audit information. There is no case or global release flag.
