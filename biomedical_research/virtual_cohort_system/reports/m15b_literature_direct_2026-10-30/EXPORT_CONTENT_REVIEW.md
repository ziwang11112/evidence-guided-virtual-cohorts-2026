# Independent M15-B1 export content review

30 October 2026. **PASS for the exact reviewed code, documentation, provenance metadata and aggregate-result export.** No blocking export-boundary or narrative issue was found. This is a file/content/hash review, not a rerun of the biomedical experiment or an independent scientific validation claim.

## Reviewed set and binding

The reviewed `export/plan.json` contains **82 unique source-to-destination records**: 78 copied archive payloads and four project documents. Its SHA-256 is `f07dec76ec9ff1d3f2cfc09e27af139c437f323110878c0044c8ce32b799cd48`. Every source file matches the source hash recorded in that plan. Every destination matches its reviewed source bytes or the explicitly reviewed link transformation. The archive README was reviewed separately; before this review is appended, the archive manifest lists 79 payload files and its exact on-disk file set matches those entries plus the manifest itself.

The canonical hash of the 82 ordered source/destination/hash records is `1e77bf160d5f4c4799aa16b1b4c4325d8d1e925dc7d2945c34536dd57e415905`. Each record has exactly `source`, `destination`, `source_sha256`, and `export_sha256`; the digest uses UTF-8 JSON with `sort_keys=True`, separators `(',', ':')`, `ensure_ascii=False`, preserving plan order. The archive manifest and bounded export receipt retain the individual source and export hashes. This report binds the reviewed plan and content, not a self-referential final archive-manifest hash; adding this report requires the exporter to regenerate the manifest and receipt while preserving the reviewed payloads.

## Content boundary

- Both included CSVs contain exactly 24 estimand-level records: `results/estimands.csv` and `independent_target_audit/released_audit_results/independent_estimands.csv`. Their fields are statistical estimates, differences, units, counts, ranks and statuses, not participant observations.
- The released JSON contains the scheduled estimands, grouped leave-one-PSU-out sensitivity records and numerical audit comparisons. Candidate JSON contains evidence, assumptions, source operators, decisions, freeze hashes and procedural receipts. Recursive structure review found no participant-shaped objects carrying `sample_id`, `age`, and `bmi`, and no exported row-ID or selection mapping.
- Source/admission and research records summarize extraction, published aggregate evidence, queries, access events, exposure and applicability. No full article, supplement, full abstract response, rendered source image or gateway payload was included. Source-file paths and hashes refer to omitted bytes.
- The three selected `private/` JSON files contain only controller commitments, release paths/hashes and the source-pass marker. `private/custodian/prepare_target.py` is acquisition/parser/selection code without embedded participant values. Its presence does not authorize or imply execution from the export.
- The implementation and test files contain methods and explicitly invented algebraic fixtures. No real/generated table or test scratch output is included. Content and credential-pattern inspection found no secret material in the selected payloads.
- The exact path/extension inspection excludes observed/reference/generated row CSVs, original identifier mappings, raw XPT, source XML/DOCX/PNG/PDF/HTML/full-text copies, gateway payloads, caches, environments and scratch trees, including `invented_test_tmp*`, `independent_test_tmp*`, `__pycache__` and `.m15b_evaltest*`.

Actual observed/reference/generated participant tables, raw XPT and original article bytes were not opened for this review. No generation, fitting, scientific tests, acquisition or evaluation code was executed. Historical exported reports were read only as bytes for preservation hashing.

## Interpretation and chronology

The final milestone, archive README, continuation and current index/roadmap retain the one-candidate, zero-change retention finding; all 24 target estimands; the negative-reference/positive-generated age mismatch; distribution mismatch; and the limits of this finite quota benchmark. They distinguish approximate source checks from measured-reference transfer evaluation, overlapping Bogalusa papers from independent recruitment populations, and descriptive PSU sensitivity from confidence intervals. The independent audit corroborates the same fixed analyses and is not presented as another experiment or validation cohort. The final narrative review hash matches the source milestone.

The archive README explicitly labels admission, preparation and intermediate review status statements as historical. It explains retained machine-local paths and omitted inputs, and does not claim that a clone can replay patient-level analyses. Historical global sync inventories remain unchanged and are explicitly labelled as applying to earlier exports, not to the new archive.

## Transformations and preservation

The source milestone hash is `f4958ecd10c7411b8ba9ee27fbac80723d0e4b80915dfbcb7082474a5a2f33fb`; the exported milestone hash is `a4be7a62a4516a58d72da7fe83407e1e6349218352ced4a55d53adb7b7c9d4a3`. Its only byte transformation replaces the seven `work/m15b_literature_direct_2026-10-30/` link prefixes with `reports/m15b_literature_direct_2026-10-30/`. The two other records marked `reviewed_archive_links` (project README and roadmap) contain no such prefix and are byte-identical to their reviewed source files. All other selected records are unchanged copies.

All **3,823 previously exported report files** match their recorded preservation SHA-256 values. Git comparison against prior commit `23faaac0760da50a7a3b60ac3df2dbf7b11a96a5` confirms that among the **4,828 previously tracked files**, only the authorized project README, implementation roadmap and source-check documentation changed. No prior report changed. The source-check documentation change adds the existing recipe envelope; it contains no scientific harness-code change.

Selected source-content bindings (also unchanged in their archive copies):

| Artifact relative to the M15-B1 run | SHA-256 |
|---|---|
| `PROTOCOL.md` | `37b3dc73b97c09ebd2a5e6c9af06a48dd8a588e7498dea444d090d57b3c6d822` |
| `FINAL_RELEASE_REVIEW.md` | `e7f9d982bcdc46f11048e2f97270ae2c3a6258c3ac7733a09180b9aa8b50202c` |
| `FINAL_NARRATIVE_REVIEW.md` | `2a371ed134f7cc2adb727a4bae9b740268576a76108ee23dca8b658fa4f8c31d` |
| `CONTINUATION.json` | `caaf001541e8bc18a5cd3f6d09b6440235a36c6061f8dd843c1da641a97299c2` |
| `results/evaluation.json` | `6a2448df658b016588039b9482391d17cdd2b4086ab690cbf2eb1eb44ea459e2` |
| `results/estimands.csv` | `dfc896020cff5c7edc8bed3d0f5d9d4fc6441a0505477f242019f0abda215c2c` |
| `independent_target_audit/AUDIT_REPORT.md` | `532965b3366522e77db1e7d8d2e71f4c1b4b5761c0ad33f4088d9a631daddc3c` |
| `independent_target_audit/released_audit_results/audit_checks.json` | `7c39f35c5582bbf320fb1d3d767a4f6394987f99b211025aa6603ed4f494d31d` |
| `visible/bundle/candidates/initial/freeze.json` | `558effb25a1ede3ef7b514a5e0c028b4185881a80466451c4dd0a441a5499a1b` |
| `visible/bundle/candidates/final/freeze.json` | `1cd0da713677689509cbdcd8bc8c44bf12bb69a2eaf3c081c66f9cf1f7e24a4e` |

Any later substantive payload change falls outside this review and requires a bounded follow-up check. The exporter remains responsible for binding this review into the final exact manifest/receipt and checking the final Git change set before publication.
