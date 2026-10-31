# Independent M16 export content review

31 October 2026. **PASS for the exact reviewed code, documentary metadata and aggregate-results export.** No blocking privacy/content or narrative issue was found. This review concerns the bounded export; it does not rerun the experiment or establish biomedical validity.

## Exact reviewed set

The reviewed `review_exports/plan.json` contains **75 unique source-to-destination records**: 69 archive copies and six project code/document files. Its SHA-256 is `123faef1ab185f4db9a9f48e333505f4a09e85f621926faa82a5d90acf8c4395`. Every current source matches its recorded source hash, and every destination matches the declared export hash and permitted byte transformation. The archive README was additionally reviewed. Before adding this report, the exact archive set contains 70 payload files plus its self-excluding manifest, with no extra file.

The canonical SHA-256 of all 75 ordered source/destination/hash records is `af495987b5583aeba753a62b1291db10b1ad1841121996b3d5941db8ac9f96b3`. Each record contains exactly `source`, `destination`, `source_sha256`, and `export_sha256`; serialization is UTF-8 JSON with `sort_keys=True`, separators `(',', ':')`, `ensure_ascii=False`, preserving plan order. Individual bindings are retained in the manifest and bounded export receipt. This review binds the stable plan/content rather than a circular final manifest hash. The exporter must append this review and refresh only the manifest/receipt metadata without changing reviewed payloads.

## Content findings

- `results/estimands.csv` contains **144 estimand-level records**, the complete six-stage ledger of 24 analyses per stage. `results/initial_final_changes.csv` contains **72 endpoint-change records**, 24 per builder. Headers and content are aggregate estimates, units, differences, counts, ranks, signs and statuses; neither file contains participant records.
- The released evaluation, summary and independent audit JSON contain aggregate estimands, preservation/change counts, grouped PSU-deletion statistics and verification metadata. Recursive structure checks found no participant-value objects or changed-row ID/value inventory. The public `admission/variable_metadata.json` dictionary contains variable definitions and categorical codes without counts; a broad key scan matching `SEQN` and `LBXSUA` was resolved as codebook metadata, not a participant row.
- The only participant-ID-format string in selected admission prose is the documented pseudonym naming range. It is not a mapping, selected-ID list or participant observation. Reference/observed/generated file paths and hashes are documentary bindings for omitted data.
- `SOURCE_EXPOSURE_CLOSURE.json` was reviewed in full as metadata. Its source-eligibility narrative, budget counts and 95 path/hash bindings contain no row identifiers, row values or full abstracts. `B1_RETENTION_CHAIN_AUDIT.json` likewise contains scalar counts/flags, a table hash and six path/hash bindings, with no row payload. Both are safe unchanged copies.
- `review/REVIEW_SUMMARY.json` is the explicitly derived export summary written during this review. It binds final release checks, B1 retention and all three historical closure snapshots by source hash, preserves the early pending state and later pass states, and retains assertion/stage/change/preservation counts and pass flags. Its 319 deduplicated bindings are path/SHA-256 metadata only. Detailed stage and scientific-parameter-change payloads are omitted. The empty operational-failure fields are faithfully reported as empty in those snapshots, not as proof that the entire workflow was error-free. Referenced raw files were not opened or rehashed by this export reviewer.
- The three full `CLOSURE_DETAIL` files, raw release-check detail, candidate/visible/feedback trees, changed-row reports, research notes, full source originals/extracts, gateway payloads and scratch artifacts are excluded. This is a bounded summary choice; no row-level payload was found in the inspected review-JSON structures.
- All 22 selected Python files were inspected statically, including syntax-tree parsing without importing or executing them. Implementation code has no embedded participant table. The three published test suites explicitly construct invented algebraic fixtures. No secret-pattern or unexplained embedded full-text payload was found in selected text. `ENVIRONMENT.json` contains package/platform versions only, not environment variables or credentials.
- The one included PNG was visually inspected. It is a four-panel comparison of global initial/final coefficients and measured-reference lines, with no participant points or source-article image. Its labels identify descriptive effects and explicitly state that confidence intervals are absent.

No actual observed/reference/generated table, raw XPT, original article/extract, gateway payload, research-note tree or candidate changed-row report was opened in this review. No scientific code, acquisition, fitting, evaluation, source check or test suite was executed here. The separately authored export test report describes 96 passing invented-data tests in the source workspace; it is not a claim that this content review ran them or that real scientific analyses were repeated.

## Claims and reproduction limits

The milestone, current index/roadmap and archive README preserve three constructions on one finite 200-person benchmark, six scheduled stage records and four unique tables. B1 and b3 retention and b2's single 12-cell repair remain explicit. The report retains b3's age-direction failure and b2's mixed endpoint changes; it does not convert correlated endpoint counts into an overall score or winner. Source fit, consistency with a working guide and measured-reference utility remain separate. Reference PSU ranges are described as sensitivity, not confidence intervals or national inference.

The final milestone's reviewed source SHA-256 is `5318a2c94609ae21a5308969ff074d7a97510923fe33d51b95b0d52a6526eb5e` and its export SHA-256 is `93afe7fae77385703206641289d9c2c91632343693fa0e063b05cd547f8023b9`. Its only transformation replaces eight `work/m16_direct_repair_2026-10-30/` link prefixes with `reports/m16_direct_repair_2026-10-30/`. Project README and roadmap have no such prefixes and remain byte-identical to their reviewed source copies. Every other selected record is an unchanged copy.

The archive README explains that historical preparation/review statements and `CONTINUATION.json` are preserved snapshots. In particular, the continuation's pending Git status predates synchronization; it does not reopen biomedical work. Original paths and frozen bindings are retained, omitted inputs are identified, and the package makes no standalone patient-data replay claim. All **66 local entrypoint references**, including the figure embed, resolve in the export. Links inside preserved historical artifacts may still name intentionally omitted originals.

Historical global sync inventories and prior milestone receipts remain unchanged and explicitly labelled as earlier evidence rather than current whole-checkout validation. The M16 manifest, bounded receipt and this review provide the new bounded checks.

## Earlier-file preservation

All **3,904 previous report files** independently match their recorded preservation hashes. Comparison against prior Git commit `fbfcc3d01f575ebbc7f4a300429aceb86258e47f` confirms that among **4,911 previously tracked files**, only the authorized project README and implementation roadmap changed. No prior report archive or existing scientific implementation changed. New checker/code/docs and the new M16 package are separately enumerated by the exact export plan.

Selected source-content bindings (unchanged in their corresponding archive copies):

| Artifact relative to the M16 run | SHA-256 |
|---|---|
| `PROTOCOL.md` | `024fa098fe813a601ff9be3ec44135bc59d835e28356f52ecfd0f672f117e277` |
| `prelaunch.json` | `a7afedd93b3d60128964fa263c69d92b767b7fce209a2a773a7998feaa3e264a` |
| `private/evaluation_release.json` | `989bd13c6f35655df1fddb7ce9245d399aab122d4f78f901b728b6ad388fddad` |
| `results/evaluation.json` | `89ad70a294faf6a0869cf5b1f4286bbb51858b718f9b6826602c1336b0de0a53` |
| `results/estimands.csv` | `d16e995fc3daec07ddb7858eb11c6f3bf7853c938bb23dee7d3345db984924aa` |
| `results/initial_final_changes.csv` | `8d326b71f038a49e8632ce8484c7fb575c60b19318e0aff64813f9d439e8886a` |
| `independent_target_audit/actual_audit.json` | `bfb1cabef74003d9d341f122f817ca1a5ad0d70da5ee3dad8afc962e6e7eafba` |
| `review/SOURCE_EXPOSURE_CLOSURE.json` | `dcf4d5eca0947114bb5d95de34395fb036d4183305bda6ac25e3918a239b154e` |
| `review/B1_RETENTION_CHAIN_AUDIT.json` | `f09bb2dba6fe122775bd1bb4600ab95bbe06dc5d7dc9348ea4b1ed7e5fd3038a` |
| `review_exports/REVIEW_SUMMARY.json` | `a5d76ab35cb9cd60c3d781d5680073c8c805f9d8638fc80916244e839264e7e3` |
| `review_exports/TEST_REPORT.md` | `b43daafe164a2f8c55a5aadb7c86e27429eb180bf06792c28a83af4a9972a90e` |

Any substantive payload change after this review requires a bounded follow-up check. Adding this review itself and updating its final manifest/receipt bindings does not change the reviewed scientific payloads. Final staged-file and Git checks remain the export agent's responsibility.
