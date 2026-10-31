# ENSANUT preparation implementation

2026-10-31. Implementation and artificial-data verification only. **No actual participant table has been opened by this implementation; no actual eligibility, readiness, BMI or effect has been calculated.** The script does not create `PREPARATION_RELEASE.json`. The prior preflight, acquisition ledger, adjudication and project STATE files remain unchanged.

`prepare_reference.py` contains small pure parsing, key, join, measurement, eligibility and readiness functions. `test_prepare_reference.py` uses artificial dictionaries and artificial metadata fixtures. Importing the module performs no task-file or participant-file reads. It does not import the analysis engine or call an effect estimator.

## Fixed transformations

Source columns remain strings when CSVs are parsed. Working person keys are validated as digit-only original strings and padded to the catalogue widths: UPM 5, VIV_SEL 2, HOGAR 1, NUMREN 2. Float IDs, decimal-form IDs, scientific-notation IDs, missing/malformed keys and duplicate person keys are holds. Original keys and every other source column are preserved separately with `_lab` and `_anth` suffixes; the normalized join key is additional. Joins are one-to-one, with age/sex agreement required and no coalescing of laboratory and anthropometry design variables.

The fixed sequential flow reports remaining counts after:

1. Inner linkage of the two pinned files.
2. Recorded integer age 25-79 and sex 1/2.
3. Laboratory P7==2; other documented/missing codes are excluded, undocumented codes hold.
4. Integer fasting duration P5_1 from 8 through 12 hours inclusive.
5. Positive finite glucose below 126 mg/dL and positive finite HbA1c.
6. Anthropometry P6==4 for women ages 25-49; this field is not used to invent negative answers for other routes.
7. The age-routed complete standing ordinal pair and the adjudicated documentation/quality restriction.
8. Final reference with preserved laboratory PSU and stratum identifiers.

Only fields active at a stage reached by a row are evaluated for the clinical eligibility rule. Full-file keys and linked age/sex agreement are checked before clinical filters. Earlier exclusion does not authorize inspection of a later clinical field to create a different subgroup.

Under age 60, the measurement block is PESO1/TALLA4 with P3=P5=1. At age 60+, it is PESO12/TALLA15 with P14=P16=1 and P11 in {1,4}. Codes 2/3/9 or missing result flags are exclusions under the investigator's prospective quality restriction, not declarations that numeric values are proven invalid. P11=1 (upper-limb amputation, walks) remains a permitted standing route. P11 codes 2/3/5/6 are alternative routes. Positive nonsentinel standing fields on those known alternative routes are contradictions and hold.

Clothing states 1/2/3 do not invalidate a measurement or trigger a numerical correction. Missing clothing and the documented P2=9 do not alone exclude. P13=9 is undocumented and holds. Clothing code 4 means not weighed; positive nonsentinel weight with that code holds. Weight 222.222 and height 222.2 are nonmeasurement sentinels in both ordinal readings under the declared conservative rule. Nonpositive/nonfinite/missing readings cannot form a pair; malformed nonblank numerical text holds.

The first complete ordinal pair is always preferred; the second is used only when the first pair is incomplete or unusable. No cross-ordinal mixing, averaging, knee-height substitution, clipping, winsorization, target imputation or fitted correction occurs. BMI is kg/(cm/100)^2 from the selected pair. Repeat availability and the documented discrepancy triggers are private audit booleans only; they never change selection or eligibility. The exact result labels, source locators, precedence and third-reading limitation remain in `MEASUREMENT_RULE_ADJUDICATION.md`.

## Readiness is separate from analysis

The private reference schema is exactly:

`age,female,bmi,glucose,hba1c,lab_upm_dis,lab_est_dis`

No participant key is included in this seven-column file. `female` maps sex 1 to 0 and sex 2 to 1. Laboratory design codes remain zero-padded strings. Anthropometry strata and expansion weights remain in the private suffixed source join and are not overwritten or used as national survey weights.

Readiness requires at least 400 total rows, at least 30 in each of the eight fixed age-band/sex cells, variation in all five scientific variables, and full rank for the three required covariate designs. Rank checks use the square-root demographic weights and the protocol's SVD threshold `max(n,p) * machine_epsilon * largest_singular_value`. Only booleans leave the rank check; no singular values, coefficients, means, SDs, quantiles, correlations or effects are returned. The analysis engine is hash-bound by the release but is neither imported nor executed.

## Required root-issued release

The only CLI invocation is `python -B prepare_reference.py`, with no alternate-input, output, override or force arguments. It requires `R/PREPARATION_RELEASE.json`. Missing or mismatched authorization fails before private input existence checks, hashing or parsing. There is no script function that generates a release.

The root must create the release after independent implementation review, using this schema and freshly verified hashes:

```json
{
  "schema": "ensanut_preparation_release_v1",
  "release_id": "ROOT-ASSIGNED-UNIQUE-ID",
  "issuer": "root",
  "status": "approved",
  "purpose": "prepare_reference_only",
  "effects_authorized": false,
  "bindings": {
    "protocol": {"path": "PROTOCOL.md", "sha256": "ROOT-VERIFIED-SHA256"},
    "adjudication": {"path": "custodian/MEASUREMENT_RULE_ADJUDICATION.md", "sha256": "ROOT-VERIFIED-SHA256"},
    "preparation_script": {"path": "custodian/prepare_reference.py", "sha256": "ROOT-VERIFIED-SHA256"},
    "preparation_tests": {"path": "custodian/test_prepare_reference.py", "sha256": "ROOT-VERIFIED-SHA256"},
    "download_ledger": {"path": "custodian/DOWNLOAD_LEDGER.json", "sha256": "ROOT-VERIFIED-SHA256"},
    "analysis_engine": {"path": "ROOT-SPECIFIED-RELATIVE-ENGINE.py", "sha256": "ROOT-VERIFIED-SHA256"},
    "independent_review": {"path": "review/ROOT-SPECIFIED-REVIEW.md", "sha256": "ROOT-VERIFIED-SHA256"}
  },
  "inputs": {
    "laboratory": {
      "path": "custodian/private/DetBioCronicosAdultos.csv",
      "sha256": "d32341b00b7e01ac22d3552f5e07094cd1e7ef05da2421200794b14a0d3d86e3"
    },
    "anthropometry": {
      "path": "custodian/private/CN_ANTROPOMETRIA.csv",
      "sha256": "a2e0d4d0a5eb93d62049d09ebc5880868be7f9143c6d9e0cb26d06d6099b37b1"
    }
  }
}
```

The first five binding paths are fixed. Engine/review paths must be safe relative paths within R and outside private storage, including after symlink resolution. All seven files must exist and match their recorded hashes. The input paths/hashes must exactly match the hard-coded acquisition identities and the corresponding archive members in the separately hash-verified download ledger.

The file-loading boundary **revalidates the release independently**, so merely constructing a `VerifiedRelease` object does not permit a private read. Only after this gate does it read input bytes, verify both actual hashes, and parse those same verified bytes in memory. A further release/hash check precedes output writing. Hashing is a byte read after authorization; participant CSV parsing never precedes the actual input-hash checks.

The CLI creates an exclusive `PREPARATION_ATTEMPT.json` before its first private-byte read. An existing attempt or final output prevents another attempt; there is no automatic retry or overwrite. Failure preserves the attempt. Any later repair/retry requires a separate root decision and must not erase the failed history.

## Outputs only after release

- `private/reference.csv`: seven columns above, all eligible records.
- `private/linked_source.csv`: original component fields with module suffixes plus normalized working keys; kept private.
- `private/measurement_audit.json`: private row-ordinal decisions and repeat/quality/discrepancy diagnostics, with no public value summary.
- `PREPARATION_RECEIPT.json`: eligibility flow, readiness counts/booleans, input/release bindings and output hashes only. Controller/evaluator/reviewer access; builders receive only the readiness decision and unchanged public task.
- `PREPARATION_HOLD.json` on an adjudication hold: aggregate field/reason/count records only. No participant IDs, examples, raw values or exception text.

The CLI never prints raw exception strings or tracebacks. An unexpected failure emits only its exception class under a generic runtime field. Known row errors aggregate by field/reason and prevent all final output writing. No STATE file is read or changed.

## Artificial verification record

Artificial tests and the final bound hashes are recorded in `implementation_logs/`. Test execution does not call the guarded real-data CLI. No `PREPARATION_RELEASE.json`, actual preparation attempt or reference output is created by verification. Independent review is required before the root issues the actual release.

Verification: `python -B -m unittest test_prepare_reference` completed successfully: **65 tests, 0.127 seconds, OK**. This comprises 56 independently written protocol-contract tests, eight additional mocked release/hash checks, and the independent review's floating-point-boundary regression. All input records and mocked metadata bodies were artificial. No actual input file was imported, opened or hashed. The tests include one-to-one joins and redaction, active versus inactive fields, both age blocks and physiological routing, P11 code 2, P11 code 1, result-code quality restrictions, clothing contradictions, same-ordinal fallback, exact BMI units, strict glucose and inclusive fasting limits, eight-cell readiness, and rank failure from artificial collinearity. Gate checks cover every binding hash, input declaration and ledger identities, stale/forged tokens, blocked CSV parsing on mocked wrong input bytes, unsafe paths, missing releases, CLI overrides and prior-attempt refusal.

- `prepare_reference.py` SHA-256: `8d0baa8b1d8429a5795d83298df02f99c24ba0ecf6f22d79ba435cdc15339295`
- `test_prepare_reference.py` SHA-256: `7d7a632d5f2a4ea9cc098a257a283c8540486b64376b41f8391b6bac005d04db`

Independent review identified a representational edge case: an artificial decimal below 126 can round to float 126. The implementation now rechecks the strict bound after conversion and holds on boundary crossing; it never clips or silently changes eligibility. The initial 64-test receipt is preserved as `implementation_logs/TEST_VERIFICATION.json`; the corrected final run is separately recorded in `TEST_VERIFICATION_v2.json`.

The prior preflight report SHA-256 remains `044ccca1465e152aa2c5560735b9b8a972b8d3fa3da631710174b4ce1bdf741c`, adjudication remains `10e99f7d6bf52abb6d74b622813663179eebef3b6a8796379651957560d3e8fd`, and download ledger remains `8615227785d7953d66366ffd64c300d70b0e4fd7e9552a8a4d5851ae16033178`.
