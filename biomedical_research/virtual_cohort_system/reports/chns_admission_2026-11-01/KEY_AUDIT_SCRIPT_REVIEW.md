# Static review of the CHNS schema/key audit script

1 November 2026. **PASS for the bounded metadata and identifier-linkage purpose** at script SHA-256 `1934cf90e7ffca2afb1950378b889369c8e21b0510b9d9e84f17313cc6e5f720`. This is a code review, not validation of clinical eligibility, source applicability, person-identity equivalence or biomedical outcomes.

The initial review and requested corrections preceded the coordinator's reported execution. The coordinator reports that both corrections were applied before its first run. This reviewer inspected the corrected file after receiving that execution report; this note does not claim a separate final approval timestamp before the run. No script execution or data-row inspection was performed by this reviewer. Independent count verification was assigned separately.

## Corrections and their disposition

The initial script checked finite/integral keys only after dropping rows with any missing key. Its subsequent wave counts included nonmissing WAVE values from those dropped rows. An invalid fractional or infinite WAVE paired with a missing ID could therefore bypass validation and be truncated or fail at `int(k)`. The revised script validates **every nonmissing key cell**, including incomplete-key rows, before counting or joining (`audit_schema_keys.py:43–55`). It rejects nonfinite, nonintegral and conservatively unsafe float-integer magnitudes (`abs(value) >= 2**53`).

The revised script also requires decoded-row count to match the file header (`:39–41`). A mismatch stops processing instead of being silently accepted as complete. These changes close the concrete static issues reported in review.

## Approved scope and controls

- The four inputs are explicit local filenames. Case-insensitive name collisions and absent required keys stop the script (`:23–29`).
- The reader decodes complete SAS chunks internally, as the docstring and receipt disclose. Only the selected ID/wave columns are copied into the retained key frames (`:34–38`). It does not compute a clinical mean, distribution, correlation, effect, medication/fasting exclusion or analytic cohort.
- Missing-key exclusions are counted explicitly. All-wave duplicate counts precede the 2009 restriction; relevant duplicate keys prevent linkage rather than being deduplicated (`:42,51–64`). Counts of wave values explicitly include rows with missing IDs, while the linkage uses complete keys; the receipt labels this difference.
- The master-file join is on individual ID with `many_to_one` validation; wave-specific files use ID plus WAVE with `one_to_one` validation (`:73–76`). The biomarker key frame itself must have passed its uniqueness check. These controls prevent silent join multiplication in the supported successful path.
- Output consists of schema labels/types, file hashes, row/key counts and linkage cardinalities. The code serializes neither raw IDs nor joined key rows nor clinical values (`:77–81`). Hashing file bytes does not interpret participant values.

## Limits and result attribution

The coordinator reports successful execution of the corrected version and nonzero unmatched keys for some companions. This reviewer has not rerun or independently authenticated those counts; the separate count verifier and `SCHEMA_AND_KEY_AUDIT.json` own that evidence. Record counts and successful joins are **not** adult eligible counts or evidence that HbA1c, glucose, fasting and covariates are jointly observed or scientifically compatible.

Exact numeric-key agreement cannot by itself establish that independently documented identifier systems mean the same thing. That requires the official schema/provenance review. The script does not validate field-level clinical missing-value codes or reproduce survey weighting. For a duplicate biomarker key set, `join_ready` would be false and the join dictionary empty; callers must inspect file statuses rather than treating an empty dictionary as successful zero linkage. Empty files or unexpected nonnumeric key types stop rather than producing an approved result.

The script writes a current audit receipt and does not mutate source SAS files, old scientific candidates or frozen receipts. This review does not authorize clinical analysis, reopening a revealed target, public participant-data export or F2 admission.
