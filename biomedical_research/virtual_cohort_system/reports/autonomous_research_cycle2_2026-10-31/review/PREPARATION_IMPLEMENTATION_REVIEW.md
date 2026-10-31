# Independent preparation implementation review

**PASS for a separate root-issued preparation-only release. No outstanding blocker remains.** This review does not itself authorize private-data access, actual preparation, clinical generation, target effects or target evaluation. Actual readiness is still unknown.

Reviewed on 2026-10-31 using the frozen protocol, final protocol review, adjudication, preflight report, preparation implementation/tests, implementation receipts, redacted acquisition metadata and the analytical engine interface. The custodian confirmed the final repaired files were stable before these hashes were bound. The reviewer wrote only this Markdown report and its companion JSON. No participant/private file was opened or hashed; no actual eligibility, BMI, readiness, scientific summary, generator output or effect was calculated. No network retrieval or STATE mutation occurred.

## Findings and disposition

One artificial interface defect was found and repaired before PASS: Decimal glucose `125.999999999999999999` passed the exact `<126` check but converted to float `126.0`, which violates the analytical engine input contract. The custodian added a strict post-conversion bound check, without clipping or silently excluding the row, and an artificial regression test. The independent reviewer repeated the exact fixture: it now raises a redacted HOLD with field `conversion.glucose`, reason `strict_boundary_crossed_by_float_conversion`, count 1. No prepared result is returned. This is a numerical representation guard, not a new scientific eligibility rule.

The first 64-test receipt is preserved. The corrected receipt records **65 tests, 0.127 seconds, exit 0, OK**; its code/test/document hashes match the reviewed files. The reviewer did not rerun the full suite or engine arithmetic suite. The two reviewer executions were only this in-memory invented boundary probe before and after repair. The separately bound engine review reports PASS for its independent arithmetic scope.

## Contract checks

- **authorization_before_private_access: PASS.** run_authorized verifies the root-issued preparation-only release before private existence checks or bytes. The loading boundary revalidates every nonprivate binding and release identity before reading the pinned inputs. Both input byte hashes are checked before parsing those same in-memory bytes.

- **release_and_single_attempt: PASS.** Exact fixed protocol/adjudication/script/tests/ledger paths, safe nonprivate engine/review paths, exact pinned input identities, archive-member ledger matches, and effects_authorized is False are required. CLI overrides are rejected. An exclusive attempt receipt precedes input bytes; an existing attempt/output blocks another run. Release and bindings are checked again before output.

- **string_keys_and_source_provenance: PASS.** Digit-only original string keys use widths 5/2/1/2 without numeric coercion; missing/malformed/duplicate normalized keys hold. The one-to-one inner join requires linked age/sex agreement, retains all original columns with _lab/_anth suffixes, and preserves separate design fields and weights.

- **eligibility_and_module_names: PASS.** Age 25..79, sex 1/2, laboratory P7==2, integer P5_1 in inclusive 8..12, positive finite serum glucose below 126 and positive finite HbA1c, and anthropometry P6==4 only for women 25..49 implement the frozen eligibility. Laboratory P6/P3 and conditional pregnancy-month fields cannot substitute for anthropometry fields.

- **active_measurement_codes_and_routes: PASS.** Under 60 uses PESO1/TALLA4 with P3=P5=1; age 60+ uses PESO12/TALLA15 with P14=P16=1 and P11 in {1,4}. Known alternative P11 routes {2,3,5,6} with any usable standing value hold. Missing route is quality exclusion. Active undocumented codes hold; inactive age blocks/unrelated flags are not filters.

- **quality_qualification_and_clothing: PASS.** Result codes 2/3/9 or missing are documented-quality exclusions, not proof all numeric readings are invalid. P2/P13 codes 1/2/3 or blank make no correction; P2=9 is allowed unknown, P13=9 holds. Clothing code 4 with usable weight holds and otherwise excludes.

- **ordinal_pair_sentinels_and_bmi: PASS.** First complete positive nonsentinel ordinal pair wins, otherwise second complete pair. Numeric 222.222 kg and 222.2 cm are excluded in both repeats. No cross-pair mixing, averaging, stature reconstruction, clipping, target imputation or favorable-pair choice. BMI is kg/(cm/100)^2. Repeat discrepancy triggers remain private diagnostics only.

- **missing_nonfinite_and_conversion: PASS.** Missing/nonpositive/nonfinite biomarker or measurement values cannot become valid inputs; malformed nonblank numerical text and undocumented codes hold. Finite positive floating-point output is required, and the repaired strict glucose bound is rechecked after conversion.

- **no_effects_and_readiness_only: PASS.** Preparation imports no analysis engine and fits no effect. Readiness requires >=400 total and >=30 in all eight age/sex cells, variation in all five scientific fields, and full rank in the three fixed covariate designs at max(n,p)*epsilon*s0 with square-root standardization weights. Only counts and rank/variation booleans are returned, not singular values or scientific summaries.

- **private_outputs_and_redaction: PASS.** The seven-column reference, full suffixed join and ordinal measurement audit stay under private/. Public preparation receipt contains flow/readiness and hashes only; holds aggregate field/reason/count. CLI suppresses raw exception text and tracebacks. A known preparation hold prevents all final outputs. Builder access remains limited to readiness and the unchanged public task.

- **analysis_engine_interface: PASS.** Exact scientific fields age,female,bmi,glucose,hba1c and string lab_upm_dis,lab_est_dis match the bound engine. The engine uses named cluster columns, so their CSV order is immaterial. The readiness designs, demographic cells, weights and SVD cutoff agree with the fixed engine; no engine function was called during this review.

- **artificial_verification_and_binding_integrity: PASS.** Reviewed all artificial contract tests and mocked gate tests. Final custodian receipt records 65 successful tests after the one numerical guard repair and matches current code/doc hashes. The reviewer independently ran only the targeted invented Decimal-boundary probe before and after repair. Prior receipt and final protocol/adjudication/preflight bindings remain consistent.

## Release boundary

The root may issue a separate hash-bound `ensanut_preparation_release_v1` with purpose `prepare_reference_only`, `effects_authorized: false`, the exact seven required bindings and the pinned input identities. The companion JSON supplies those ready-to-use binding records, including this report's hash. The script will then independently verify metadata before private bytes, require an exclusive first attempt and verify input hashes before CSV parsing. No release is created by this review.

After preparation, the controller/evaluator/reviewer may receive only the flow and readiness material allowed by the protocol. Builders receive the readiness decision and unchanged public task. Any hold, failed readiness floor, changed bound artifact or attempted retry requires the existing root decision process; this PASS does not approve a repair using observed target effects. Target evaluation remains behind the later execution and candidate-freeze gates.

The private reference schema is exactly `age,female,bmi,glucose,hba1c,lab_upm_dis,lab_est_dis`. Input hashes below were checked against ledger metadata only; the reviewer did not verify them by reading private bytes.

## Bound artifacts

| Path relative to R | SHA-256 |
|---|---|
| `PROTOCOL.md` | `fe1bbe83b0bf847a090575389272dfdbeeba3ef65c9d3af8e5bb53f9def795cd` |
| `review/PROTOCOL_FINAL_REVIEW.json` | `ac8d83975ea77bb470112092f0e23dc8649acc247809e3adbd3effefa697ee18` |
| `custodian/MEASUREMENT_RULE_ADJUDICATION.md` | `10e99f7d6bf52abb6d74b622813663179eebef3b6a8796379651957560d3e8fd` |
| `custodian/PREFLIGHT_REPORT.md` | `044ccca1465e152aa2c5560735b9b8a972b8d3fa3da631710174b4ce1bdf741c` |
| `custodian/prepare_reference.py` | `8d0baa8b1d8429a5795d83298df02f99c24ba0ecf6f22d79ba435cdc15339295` |
| `custodian/test_prepare_reference.py` | `7d7a632d5f2a4ea9cc098a257a283c8540486b64376b41f8391b6bac005d04db` |
| `custodian/PREPARATION_IMPLEMENTATION.md` | `5b8799046c09cdc54ebc39e43970c77ac72ac2b1086b6c8ea1eaf53d3f7bebb5` |
| `custodian/DOWNLOAD_LEDGER.json` | `8615227785d7953d66366ffd64c300d70b0e4fd7e9552a8a4d5851ae16033178` |
| `custodian/implementation_logs/TEST_VERIFICATION.json` | `f4d67569904d7d8caeb1d1afe9b31f18d85f66be1a20b46d44cb1ff7cf166636` |
| `custodian/implementation_logs/TEST_VERIFICATION_v2.json` | `c81172db734ab5c8ab0d923f7cd7432190f59ae11a16ea584ac70226441eab38` |
| `analysis/analytical_engine.py` | `1799c017b60f8fd3a9af409a524d3ebd9e54c81016e52da760aeafaefe03289d` |
| `analysis/ENGINE_READINESS.md` | `dc5111fbb987ee03f6706db35ca950d827657740def6436ac13c8a3af332eab1` |
| `analysis/logs/independent_review_verification_after_fix.md` | `02442832af3c1dd8d7064cb6f9fc5eeb0a896d32ded493621e440d736102d81d` |

The companion JSON binds this Markdown report; its own hash is reported separately to the controller to avoid circular self-binding.
