# Export byte-repair review

**Status: ready.** The reviewed change is a bounded publication serialization repair. No unresolved blocking issue was found. It does not reopen scientific execution, model selection, reference analysis or the prior scientific review.

Base commit: `d485c1d86ea5d6ac544ad43a10c4df25d2590d1f`. Original 842-file export manifest SHA-256: `3ff534e4814d29fd26ccce005a037b5039ceea01c7f18d12355c271a0db3bc2d`. Exact current hashes of the exporter, repair helper, note, audit, original manifest/reviews and core scientific artifacts are recorded in `EXPORT_REPAIR_REVIEW.json`.

## Independently verified findings

The reviewer read the 259 disputed Git blobs directly using `git cat-file` at the base commit. All 259 sources still matched their original manifest SHA-256 values. Every committed blob exactly equalled its original source after CRLF-to-LF replacement alone; there were no exceptions. This verifies the stated newline-only defect independently of checkout newline filters.

Across the original 842-file manifest, 841 source hashes remain unchanged. The only changed source is `publication/prepare_export.py`. Its diff against the published version is exactly one line: replace `read_text(encoding='utf-8')` with `read_bytes().decode('utf-8')`. Decoding preserves the original UTF-8 newline bytes and prevents universal-newline normalization.

The current raw bytes require updates to 260 original-inventory Git blobs: the 259 newline restorations and the deliberately changed exporter. With five named repair metadata files, the expected payload contains 265 files, and the complete verification inventory contains 847 files.

## Repair helper and preserved boundaries

`prepare_byte_repair.py` requires a ready repair review, pins the exact base HEAD and original export manifest, and verifies original source hashes with only the exporter exception. It computes Git blob identifiers directly from raw source bytes, selects only differing original-manifest objects, and adds the named helper, note, audit and review records. It writes a separate repair-export directory and full verification inventory. The original export manifest and published history are retained.

The original `FINAL_REPORT_REVIEW.json` and `.md` remain byte-identical to their reviewed hashes. The release, manuscript, aggregate results and independent audit retain their earlier hashes. The new review complements the previous export-plan review; it does not rewrite it. No scientific result, model instruction, protocol or numerical analysis changed in the original inventory.

The repair remains confined to the reviewed manifest and five explicitly named metadata/code files. It does not add real or generated individual tables, source acquisitions, third-party full texts or complete runtime bundles. Public artifacts retain their documented reproducibility limits.

## Required publication verification

After preparation, compare the 265 changed payload entries and all 847 inventory entries with the exact current source bytes. Publish as a child of the recorded base commit under the existing branch lease. Then read the committed Git object bytes and verify the complete inventory's SHA-256 and expected Git blob identifiers; checkout hashes alone are insufficient when newline filters may apply. Retain the resulting publication receipt.

The reviewer did not execute the repair helper, export payload or publication action. No patient/generated rows, scientific generators, evaluators, tests or new literature were used. This is a publication-byte review, not clinical or external expert validation. The operational retry history mentioned in the note was not independently reconstructed.
