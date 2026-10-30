# M13-B target custody

Preparation uses only official CDC metadata and invented tests. Acquisition is a separately gated action; do not run it until the controller explicitly authorizes the frozen manifest. The `evidence-cohort-generation` skill's source/target information boundary was applied to this custody task; source models and parameters were not modified.

`metadata_sources.json` records the three official planned XPT URLs obtained from the 2017 CDC index pages, variable definitions, scan eligibility, and weight interpretation. These are planned URLs, not a claim of XPT acquisition. Actual resolved URLs, acquisition times, sizes, and SHA256 hashes are written only after acquisition. DXX_J's examination-weight paragraph has a stale literal `DXX_G` name; DEMO_J independently specifies the cycle's two-year weights and identifies WTMEC2YR as the full examination weight.

Metadata exposure disclosure: one web search-within-page response unexpectedly included adjacent published codebook frequency/completion excerpts. No XPT was downloaded, no participant rows were read, and no endpoint values, associations or computed target counts were accessed during preparation. Later metadata extraction suppressed numeric frequency columns. The official metadata document is not an additional independent source cohort.

## Freeze and authorization

The root manifest is `schema_version:1`, `phase:"before_target_acquisition"`, `created_utc`, `scientific_revision_allowed:false`, and `files:{relative_path:sha256}`. Paths resolve against the manifest's directory (M13-B). The manifest must bind `custodian/prep.py`, `custodian/metadata_sources.json`, `protocol.json`, `PROTOCOL.md`, and the remaining controller/evaluator/source identities required by the root audit. Every listed file is checked before any network request; the protocol's target, column whitelist and BMI bounds must agree with custody.

Root writes a separate authorization JSON only after freeze. Required fields:

```json
{
  "schema_version": "m13b_target_access_authorization_v1",
  "freeze_manifest_sha256": "EXACT_SHA256_FROM_ROOT_FREEZE",
  "authorized_by": "root",
  "authorized_at_utc": "ISO_8601_UTC_TIME_AFTER_FREEZE",
  "target_access_authorized": true
}
```

The authorization record is an auditable procedural assertion, not cryptographic authentication of a human. Its freeze hash must also be supplied explicitly to the CLI. No implicit authorization, preexisting data import or local cached-data fallback exists.

From the harness project root (replace uppercase placeholders with actual frozen values):

```powershell
python work/m13b/custodian/prep.py check-gate --freeze-manifest FREEZE_PATH --freeze-sha256 HASH --authorization AUTH_PATH
python work/m13b/custodian/prep.py acquire --freeze-manifest FREEZE_PATH --freeze-sha256 HASH --authorization AUTH_PATH --output work/m13b/custodian/acquisition
```

`check-gate` reads only metadata/source/code/protocol artifacts. `acquire` demands a new output directory beneath custody, writes a start receipt before requesting XPT files, verifies XPORT signatures, records each actual request, and preserves partial failures. Existing output directories cannot be overwritten. A failed run requires explicit controller review before any new acquisition attempt.

## Local outputs and schema

- `private/raw/`: downloaded XPT components.
- `private/full_frame.csv`: exact columns `id,SEQN,WTMEC2YR,SDMVSTRA,SDMVPSU,RIDAGEYR,RIAGENDR,RIDRETH3,BMXBMI,DXAEXSTS,DXDTOPF`. It retains every DEMO row with finite positive WTMEC2YR and finite design identifiers, including zero-domain PSUs. The evaluator computes the frozen domains itself.
- `private/id_mapping.csv`: opaque ID to SEQN mapping. IDs use independent random 128-bit tokens and do not encode SEQN.
- `generator_input/observed.csv`: exact columns `id,age,bmi,male,asian,inv_bmi,male_inv_bmi,asian_inv_bmi,male_age,asian_age`. It contains the disjoint primary/extension union in consistent ascending internal SEQN order; SEQN is never exposed to the generator. Asian and its interactions are zero; other interactions are deterministic functions of permitted covariates. No race, weight, design, DXA family, scan or missingness field is released.
- `private/quality_report.json`: sequential exclusion flow, weighted/unweighted completeness, domain counts and full-design checks. Completeness is reported separately within the primary and extension age/race/BMI sampling frames, plus the age/race frame before BMI selection. The latter makes missing BMI visible. These are local aggregates for the controller/evaluator, not builder feedback.
- `private/acquisition_receipt.json`: frozen gate identity, raw-file provenance, output hashes and completion/failure status.

All participant outputs, including covariates and generated rows, remain local and must not be sent to GitHub. The output directory gets a deny-all `.gitignore`, which guards ordinary adds but is not an access-control boundary and must not be overridden with a forced add. No target rows or summaries are printed by the CLI.

SEQN is nonmissing, integer and unique within each component; component keys must belong to DEMO; merges are one-to-one left joins. Full-design singleton strata stop custody. Any available DXDTOPF outside [0,100] or infinite triggers an integrity failure even outside the analysis domain. Missing endpoint/invalid scans exclude the analysis domain without deleting full-frame rows. No endpoint trimming, imputation, additional health exclusions, or nonresponse reweighting is implemented.

## Invented-fixture checks

```powershell
python -m pytest work/m13b/custodian/test_prep.py -q
```

Tests cover exact schemas/derivatives, boundary membership, full-frame retention, zero-domain PSUs, source key uniqueness, invalid endpoints (including outside-domain rows), weighted/unweighted completeness, left-join missingness, row permutation, singleton strata and pre-network gate rejection. They do not certify the later target acquisition or the evaluator's survey formulas.
