# Independent preparation v2 amendment and implementation review

**PASS for the scientific amendment and v2 implementation. No outstanding blocker remains for a separate root-issued release of the single reviewed second preparation attempt.** This review creates no release and authorizes no actual preparation, clinical generation or target effects. Actual v2 readiness remains unknown.

Reviewed on 2026-10-31. The scientific decision is justified without investigating individual truth: a finite analytical reference can prospectively require internally consistent measurement documentation and exclude contradictory records while acknowledging that neither recorded field has been proven false. This is an investigator-defined restriction, not an official ENSANUT validity rule. Selection and generalizability limitations remain; it supplies no new clinical evidence.

The timing is explicit: the amendment follows one failed target preparation attempt, which disclosed only `anthropometry.P13 / not_weighed_with_numeric_weight / count 1`. It was adopted before any reference effect, distribution or readiness result was released and before any endpoint-based adjustment. It must not be described as having been frozen before all target-data contact. The first attempt and original policy remain intact. The code inspected for that failed attempt computes no effect and raises its aggregate HOLD before its readiness return and final output writes. The present reviewer read no private participant file or individual value.

## Review decisions

- **outcome_blind_justification: PASS.** The first attempt exposed only the named P13 contradiction and count 1. Its preparation script contains no effect estimator and raises before readiness return or final writes. The amendment uses documentation consistency as eligibility, not an inferred truth about the contradictory participant fields or a target-fit optimization.

- **transparent_timing_and_target_definition: PASS.** This is a pre-effect amendment after one failed preparation attempt, not a claim that the rule was frozen before all target-data contact. The trigger, original HOLD, changed rule and narrower consistently documented reference remain explicit and versioned. It does not establish that excluded numeric measurements are false.

- **uniform_clothing_and_route_rule: PASS.** Only explicit not-weighed versus usable weight and age-60+ alternative-route versus usable standing-field contradictions change from HOLD to EXCLUDE_DOCUMENTATION_CONSISTENCY. The active P2/P13 blocks, both ordinals and every applicable record follow the same policy; younger P11 remains inactive. No key, observed count, value or outcome is special-cased.

- **precedence_and_retained_holds: PASS.** Active code validation and numeric parsing precede consistency exclusion. Undocumented/malformed fields, numerical conversion failures and linkage errors retain their HOLD behavior. Older alternative-route exclusion precedes clothing exclusion when both apply. Pair 2 cannot rescue a contradiction.

- **unchanged_scientific_logic: PASS.** The protocol diff leaves questions, finite demographic standard, source evidence and checks, generated row count, all seeds, stability algorithm, budgets and readiness floors unchanged. The code diff leaves all other eligibility, key handling, ordinal pairing, sentinels, positive/finite output and SVD logic unchanged. Bound analysis engine is byte-identical.

- **counts_and_private_audit: PASS.** A distinct consistency decision and reason remain in the private audit. Both consistency reasons are explicit in the aggregate subset count map including zeros. Those counts are also included in the general measurement exclusion map; the documentation explicitly warns against summing the two maps as disjoint groups. No row value or identifier is released.

- **separate_second_attempt_gate: PASS.** The v2 schema requires effects_authorized false, attempt_number 2 and attempt_budget 1, eleven exact hash bindings and pinned inputs. The gate binds prior release/attempt/HOLD, verifies their history link, and is revalidated before input bytes and output writes. The v1 release alone cannot authorize v2.

- **exclusive_outputs_and_no_automatic_retry: PASS.** All new paths are versioned and created exclusively. Any v2 attempt/HOLD, either version successful receipt or either version private output prevents another load. The implementation contains no force/override, deletion, overwrite, automatic third attempt or effect execution.

- **v1_preservation: PASS.** All 17 protected v1 baseline files match their original hashes. The reviewer also rechecked the prior review bindings, for 21 unique preserved nonprivate artifacts in total. The original release/attempt/HOLD relationship and exact sole aggregate HOLD are intact.

- **artificial_validation: PASS.** The current 76-test custodian receipt matches current implementation/test/document hashes and covers unchanged-v1 parity on 400 invented rows plus versioned gate/output guards. The independent reviewer separately ran 32 handmade in-memory cases for the changed decisions and retained HOLD precedence, with filesystem methods patched to fail during the probes. All passed; no full suite rerun or actual preparation occurred in this review.

- **reference_interface_and_builder_boundary: PASS.** The private seven-column reference schema and analytical engine remain unchanged; v2 outputs are now reference_v2.csv, linked_source_v2.csv and measurement_audit_v2.json. Evaluation must use the bound v2 receipt path. Before clinical generation, the public task must describe the consistently documented subset without contradiction counts, target values or preparation history.

## Independent artificial evidence

The reviewer inspected the minimal v1-to-v2 source and test diffs, then independently executed 32 handmade cases covering both active clothing blocks at ages 59/60, both weight ordinals, all four older alternative routes crossed with all four standing fields, refusal to rescue by another complete pair, malformed/undocumented active-field HOLD precedence, inactive younger P11 and precedence when both contradiction types apply. All passed. File-opening and Path read methods were patched to raise during the pure-function probes. No effect function, real CLI or full test suite was executed by the reviewer.

The custodian's separately recorded **76 unique artificial tests, 0.210 seconds, exit 0, OK** match the final reviewed hashes. The full suite includes parity of unamended preparation on an invented 400-row cohort, all changed branch expectations, separate flow reasons, mock release/history checks and exclusive second-attempt output behavior. The earlier v1 test and review receipts remain unchanged.

## Release and interpretation limits

A separate root-issued `PREPARATION_RELEASE_v2.json` must use schema `ensanut_preparation_release_v2`, purpose `prepare_reference_only`, `effects_authorized: false`, `attempt_number: 2`, `attempt_budget: 1`, the eleven bindings in the companion JSON and the unchanged pinned input identities. This is one reviewed second attempt; a new HOLD or failed readiness floor must remain reported and preserved. No third attempt is automatically permitted.

Use the v2 receipt's bound `private/reference_v2.csv` for later evaluation, preserving columns `age,female,bmi,glucose,hba1c,lab_upm_dis,lab_est_dis`. The source files are still subject to actual byte-hash verification by the authorized custodian; this reviewer verified their identities only from prior nonprivate metadata. The analysis engine, source/target execution budgets and candidate-freeze requirements are unchanged.

The updated public task must disclose the consistently documented measurement subset before builders start. It must not expose this amendment's observed count, eligibility counts, private values or preparation history. That task/execution-package gate and actual readiness are separate from this preparation review. No effect-based record repair, reference tuning or national-population interpretation is approved.

## Bound artifacts

The table includes the v2 artifacts and all preserved nonprivate artifacts checked by this reviewer. The preservation baseline covers 17 original files; its union with the prior independent review bindings covers 21 unique original files. All hashes were verified again after writing this review.

| Path relative to R | SHA-256 |
|---|---|
| `PROTOCOL_v2.md` | `8f87ecd5bae60958b4e58727f6c09d1d033c739c2aa6d3a645404bf33a431807` |
| `PREPARATION_AMENDMENT_01.md` | `2db776115fac089b023371517c8af4ecfe2d691ea69a5d4d73f204bc6ab7b936` |
| `custodian/prepare_reference_v2.py` | `f80a8986e36761d01156567fed4102abe5abcf1fe6a79b3f330780c8c84a0c8b` |
| `custodian/test_prepare_reference_v2.py` | `8351aa26bd0112b7605a9707094a96b5063482b4774b809c64a9d1894d08aacc` |
| `custodian/PREPARATION_IMPLEMENTATION_v2.md` | `285b27e01abe78dd28abab199a7ba23c60c950dd48048f85040be8c0c9e7fe3e` |
| `custodian/implementation_logs/PREPARATION_V2_PRESERVATION_BASELINE.json` | `db1cf6124c990792cfe852e3cebf952dca2fb02d38d5458870d434be8650a98c` |
| `custodian/implementation_logs/PREPARATION_V2_DIFF.patch` | `de967bfc4d30da2629cd4164d53e9e2ce5c19fe01104b14b8ce3830f26901e42` |
| `custodian/implementation_logs/PREPARATION_V2_TEST_VERIFICATION.json` | `4ef8ddbe8eee33b8c6055f0095b772f0f2e61579887b64d755736caafc7a2926` |
| `PROTOCOL.md` | `fe1bbe83b0bf847a090575389272dfdbeeba3ef65c9d3af8e5bb53f9def795cd` |
| `PREPARATION_RELEASE.json` | `28854700f0913f7155690a34ddf77778a3b63be92bee87ede418075cd6ba841c` |
| `custodian/prepare_reference.py` | `8d0baa8b1d8429a5795d83298df02f99c24ba0ecf6f22d79ba435cdc15339295` |
| `custodian/test_prepare_reference.py` | `7d7a632d5f2a4ea9cc098a257a283c8540486b64376b41f8391b6bac005d04db` |
| `custodian/PREPARATION_IMPLEMENTATION.md` | `5b8799046c09cdc54ebc39e43970c77ac72ac2b1086b6c8ea1eaf53d3f7bebb5` |
| `custodian/MEASUREMENT_RULE_ADJUDICATION.md` | `10e99f7d6bf52abb6d74b622813663179eebef3b6a8796379651957560d3e8fd` |
| `custodian/DOWNLOAD_LEDGER.json` | `8615227785d7953d66366ffd64c300d70b0e4fd7e9552a8a4d5851ae16033178` |
| `custodian/PREFLIGHT_REPORT.md` | `044ccca1465e152aa2c5560735b9b8a972b8d3fa3da631710174b4ce1bdf741c` |
| `custodian/PREFLIGHT_METADATA.json` | `cd903ec8fcf8c685b88f43eae2bb929c372bbaa41bbde9e84766996657a5f9c0` |
| `custodian/READINESS_COUNTS_AND_CODEBOOKS.json` | `4614abcbe36b8ea9f367295867fc6d70b3cd7d16438ea273cf7e9e40941db920` |
| `custodian/PREFLIGHT_STORAGE_RECEIPT.json` | `42ed2de8bb0664c7d31ea8ca3af87468461ff216440e4a13bb24b95194f6a50e` |
| `custodian/PREPARATION_ATTEMPT.json` | `914e7ac7e3a072e8cd87e7e3c509898b81abd7cb50d11344537aa7aafcb3b8d1` |
| `custodian/PREPARATION_HOLD.json` | `5e27dc640225ab005adaf38c7f9b843030d76a5be806b014ab778dbd827016a7` |
| `custodian/implementation_logs/TEST_VERIFICATION.json` | `f4d67569904d7d8caeb1d1afe9b31f18d85f66be1a20b46d44cb1ff7cf166636` |
| `custodian/implementation_logs/TEST_VERIFICATION_v2.json` | `c81172db734ab5c8ab0d923f7cd7432190f59ae11a16ea584ac70226441eab38` |
| `review/PREPARATION_IMPLEMENTATION_REVIEW.md` | `253a52f37da587645f527cb3d80f02919f533557d3db939281ee967c35cc1819` |
| `review/PREPARATION_IMPLEMENTATION_REVIEW.json` | `2a55bcc07b8432a95bc217629000876afb7f7a873f4a9143b8fe01ac75eccf63` |
| `review/PROTOCOL_FINAL_REVIEW.json` | `ac8d83975ea77bb470112092f0e23dc8649acc247809e3adbd3effefa697ee18` |
| `analysis/analytical_engine.py` | `1799c017b60f8fd3a9af409a524d3ebd9e54c81016e52da760aeafaefe03289d` |
| `analysis/ENGINE_READINESS.md` | `dc5111fbb987ee03f6706db35ca950d827657740def6436ac13c8a3af332eab1` |
| `analysis/logs/independent_review_verification_after_fix.md` | `02442832af3c1dd8d7064cb6f9fc5eeb0a896d32ded493621e440d736102d81d` |

The companion JSON binds this Markdown report and supplies all root-release binding records. Its own hash is delivered separately to avoid circular self-binding.
