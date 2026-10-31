# Preparation v2: documentation-consistency eligibility amendment

2026-10-31. Implementation and artificial verification only. **No actual v2 input read, preparation attempt, eligibility count, readiness computation, reference output or effect execution has occurred.** No v2 release was created. Version-1 code, tests, documentation, original release and failed attempt remain unchanged.

The controlling amendment is `../PREPARATION_AMENDMENT_01.md`, incorporated in `../PROTOCOL_v2.md`. The original `MEASUREMENT_RULE_ADJUDICATION.md` remains authoritative for source code meanings; the amendment replaces only its two specified contradiction HOLD decisions with an investigator-defined consistency exclusion. This is not a claim that the numeric reading or the contradictory flag has been proven false.

## Minimal implementation delta

`prepare_reference_v2.py` was cloned from reviewed v1; it does not import or monkeypatch the v1 implementation at runtime. The only scientific-decision changes are:

| Condition in the active measurement block | v1 | v2 decision and exact reason |
|---|---|---|
| Explicit not-weighed clothing code 4 with usable numeric weight on either ordinal | HOLD | `EXCLUDE_DOCUMENTATION_CONSISTENCY` / `not_weighed_with_numeric_weight` |
| Age 60+ P11 in {2,3,5,6} with any usable value in the standing weight/height fields on either ordinal | HOLD | `EXCLUDE_DOCUMENTATION_CONSISTENCY` / `alternative_route_with_standing_values` |

The clothing rule applies uniformly to P2 below age 60 and P13 at age 60+, for every record reaching the existing measurement stage. P11 remains **inactive under age 60**. No particular key, record, value or observed count is special-cased. Usable retains the reviewed definition: positive finite numeric value unequal to the documented nonmeasurement sentinel. There is no second-pair rescue of a contradiction.

The existing order is preserved: validate active codes and parse active numeric fields first; assess the older alternative-route contradiction; assess the no-weighing contradiction; assess completeness and documented standing route; require both result flags to be code 1; select ordinal pair 1, otherwise pair 2. If both contradiction types apply, alternative-route exclusion has precedence, so reason counts are mutually exclusive. Undocumented or malformed active codes, malformed measurements, identity/linkage failures, representational numerical failures and other unadjudicated errors still HOLD. A malformed field cannot be hidden by the new exclusion.

The remaining eligibility rules, five-variable definition, unit conversion, first-complete-ordinal selection, sentinel handling, explicit code-1 quality criterion, pregnancy/lactation routing, glucose boundary check and eight-cell readiness/rank logic are unchanged. No source generation, analytical engine or effect logic is changed or executed.

The existing `measurement_exclusion_reasons` count map remains. A separate `flow.consistency_exclusion_reasons` map contains both exact consistency reason keys, including zero counts when applicable. A consistency exclusion is counted in both the general measurement-exclusion map and its clearly named consistency subset; these two maps must not be summed as disjoint totals. The private audit retains the distinct decision and reason. Root/controller/reviewer can inspect only the permitted aggregate flow/readiness; builders receive neither the history nor its counts.

## Separate release, attempt and outputs

The CLI is `python -B prepare_reference_v2.py`, with no force or override arguments. It does not generate a release. It requires `R/PREPARATION_RELEASE_v2.json` with:

```json
{
  "schema": "ensanut_preparation_release_v2",
  "release_id": "ROOT-ASSIGNED-UNIQUE-ID",
  "issuer": "root",
  "status": "approved",
  "purpose": "prepare_reference_only",
  "effects_authorized": false,
  "attempt_number": 2,
  "attempt_budget": 1,
  "bindings": {
    "protocol": {"path": "PROTOCOL_v2.md", "sha256": "ROOT-VERIFIED-SHA256"},
    "amendment": {"path": "PREPARATION_AMENDMENT_01.md", "sha256": "ROOT-VERIFIED-SHA256"},
    "adjudication": {"path": "custodian/MEASUREMENT_RULE_ADJUDICATION.md", "sha256": "ROOT-VERIFIED-SHA256"},
    "preparation_script": {"path": "custodian/prepare_reference_v2.py", "sha256": "ROOT-VERIFIED-SHA256"},
    "preparation_tests": {"path": "custodian/test_prepare_reference_v2.py", "sha256": "ROOT-VERIFIED-SHA256"},
    "download_ledger": {"path": "custodian/DOWNLOAD_LEDGER.json", "sha256": "ROOT-VERIFIED-SHA256"},
    "prior_release": {"path": "PREPARATION_RELEASE.json", "sha256": "ROOT-VERIFIED-SHA256"},
    "prior_attempt": {"path": "custodian/PREPARATION_ATTEMPT.json", "sha256": "ROOT-VERIFIED-SHA256"},
    "prior_hold": {"path": "custodian/PREPARATION_HOLD.json", "sha256": "ROOT-VERIFIED-SHA256"},
    "analysis_engine": {"path": "ROOT-SPECIFIED-RELATIVE-ENGINE.py", "sha256": "ROOT-VERIFIED-SHA256"},
    "independent_review": {"path": "review/ROOT-SPECIFIED-V2-REVIEW.md", "sha256": "ROOT-VERIFIED-SHA256"}
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

All eleven nonprivate bindings are mandatory. Only engine/review paths are variable, subject to the existing within-R/nonprivate path checks. The prior attempt's `release_sha256` must match the bound v1 release, and the prior hold must state `HOLD`. Thus the failed history is checked rather than erased. The pinned CSV identities and download-ledger member hashes remain unchanged.

As in v1, the gate is revalidated at the private loader, actual input byte hashes precede CSV parsing, and release bindings are checked again before output writing. A constructed gate object alone is insufficient. No analysis engine is imported or called.

After a future separately authorized invocation, exclusive filenames are:

- `PREPARATION_ATTEMPT_v2.json` before input-byte access.
- `PREPARATION_HOLD_v2.json` if an unadjudicated HOLD occurs.
- `PREPARATION_RECEIPT_v2.json` for aggregate flow/readiness and output hashes.
- `private/reference_v2.csv`, `private/linked_source_v2.csv`, `private/measurement_audit_v2.json` for private outputs.

The seven reference columns stay `age,female,bmi,glucose,hba1c,lab_upm_dis,lab_est_dis`. Original module columns and keys stay private and suffixed. The script refuses an existing v2 attempt, v2 hold, either version's successful receipt, or either version's private output names. All new writes use exclusive creation. There is no overwriting, deletion, automatic third attempt or automatic scientific generation.

## Artificial verification and preservation

`python -B -m unittest test_prepare_reference_v2` passed **76 unique test methods in 0.210 seconds**. The suite clones the independently reviewed v1 contract tests, changes only the specified contradiction expectations, and adds uniform age/sex/ordinal coverage, every P11 alternative/field combination, contradiction precedence, separate aggregate reason counts, retained HOLD precedence, and versioned-gate/output safeguards. An artificial 400-row cohort produces identical reference rows, joined rows, readiness and private diagnostics under v1 and v2 when neither amended contradiction is present; the only additional flow item is the zero-valued consistency map.

The tests use invented in-memory rows and mocked metadata/file operations. They did not inspect participant files or create a real release/attempt/output. The versioning tests verify that a simulated failed v2 run opens only the new attempt/hold filenames in exclusive mode and that any simulated successful v1/v2 output prevents a new load. The v1 module is imported only for an artificial pure-function parity check, never as v2 implementation code.

The preservation baseline and final verification cover 17 existing nonprivate v1 artifacts, including its protocol, release, failed attempt/hold, reviewed code/tests, original preflight/ledger/adjudication and review/test receipts. Their hashes remain identical. The private source files were neither reread nor rewritten during this amendment implementation; their existing pinned identities are carried forward.

- v2 implementation SHA-256: `f80a8986e36761d01156567fed4102abe5abcf1fe6a79b3f330780c8c84a0c8b`
- v2 tests SHA-256: `8351aa26bd0112b7605a9707094a96b5063482b4774b809c64a9d1894d08aacc`
- Audit artifacts: `implementation_logs/PREPARATION_V2_PRESERVATION_BASELINE.json`, `PREPARATION_V2_DIFF.patch`, and `PREPARATION_V2_TEST_VERIFICATION.json`.

Independent v2 review and a root-issued release are still required before the one permitted second actual preparation attempt. A new HOLD or readiness failure must be preserved and reported without automatically revising the scientific population or launching another attempt.
