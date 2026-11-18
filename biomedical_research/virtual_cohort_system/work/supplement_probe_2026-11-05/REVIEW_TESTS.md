# Independent offline implementation review

Reviewed `probe.py` SHA-256: `67857b32debe4ee4176bb028feefc430fcd92e941d46e22a333396533750fb24`.

Result: **12 focused tests passed** using `python work/supplement_probe_2026-11-05/test_access_review.py` from the system project directory. No `download()` invocation or network request occurred. Socket connection attempts were blocked during the suite. Python bytecode writes were disabled. Only this review, the test script and temporary fixtures under the new probe directory were written; fixtures were removed after their tests.

## What was verified

1. Actual cached parent provenance passed read-only verification: pinned original config and science-request hashes, approved XML/manifest hashes and byte counts, original configuration-matching approval events, registered copies, unique JATS supplement href and exact versioned manifest object/checksum.
2. All 43 source/task/config/session files included by `frozen_hashes()` matched before and after the suite. This statement covers that explicit hash inventory, not an independently enumerated whole-experiment inventory.
3. Local fixture payloads with matching fixture MD5 passed for `application/msword` and the official S3 `binary/octet-stream` type. Wrong checksum, HTML MIME, empty/oversized payload and mismatched declared length rejected. Production constants were patched in memory only for synthetic fixture acceptance; no original/source file was changed.
4. OLE, RTF and ZIP signatures were distinguished. Unknown HTML-like bytes rejected. Signature recognition is format identification, not full container validation.
5. A direct call to the redirect handler rejected a redirect without opening a connection.
6. The production statements preceding the network block were extracted with Python AST and compiled as a separate `reserve_only` function. A first call created a persistent attempt reservation; a fresh compiled function targeting the same fixture directory raised `FileExistsError` on a second call and preserved receipt bytes. The `download` function and its network block were never executed. This demonstrates reservation persistence, not a real HTTP failure test.
7. Original pure `gateway.Screen` accepted benign text. With an in-memory synthetic exclusion configuration, it rejected table text, HTML-split text, percent/entity encoding and a zero-width format character containing the fixture alias, plus a configured regex in fixture metadata.

## Review findings and disposition

Two small findings were communicated before acquisition: accept the documented official S3 binary MIME and retain the original screening normalization rather than a new weaker implementation. Both are present in the reviewed source and covered above. Reusing the pure `Screen` does not instantiate a gateway session or register artifacts. Run conversion/extraction with bytecode writing disabled to avoid incidental vendor-cache updates.

The reviewed acquisition is appropriately constrained for a single fixed-source feasibility probe: pinned object, independent one-attempt reservation, no redirects/retries/search, bounded request, MD5 plus SHA-256, and a distinct `verified_download_only` status. No additional acquisition blocker was found in this focused review.

Conversion, container completeness, active/embedded-content handling, visible-text admission and scientific table accuracy were still pending at review time and are not established by these tests. The acquisition receipt must not be represented as full extraction or original-gateway approval. Retain the PLAN's explicit visible-text screening limitation and independently check rendered S1/S2 headers, signs, units and footnotes before using estimates.

## Post-conversion read-only follow-up

The controller subsequently completed its one acquisition and local conversion. I read the new code/receipts and inspected existing local artifact structure only; I ran no acquisition, conversion or rendering.

- Actual source bytes independently match manifest MD5 `6b96852aaaff8f5a96a3c03080009212`. The acquisition receipt records 263,680 bytes, OLE signature, one attempt and source SHA-256 `121c5cc12b9673fa920c9a08bafb34c5aa08676ec092e9a55d33389d858a6e46`.
- All 11 generated-file SHA-256 values in the conversion receipt match local files. It records LibreOffice 25.8.3.1, four extracted tables, 12 body paragraphs and six PDF pages.
- Converted DOCX inspection found no media/embedded files, external relationships, text boxes, drawings, alternate content chunks, tracked inserts/deletes or vanished-text flags. This reduces specific extraction omissions in the converted document; it does not prove preservation of every possible original OLE stream.
- The converter screens raw XML and its text for all `.xml` members plus extracted body/table text, PDF page text and PDF metadata. Relationships are stored in `.rels` members, which are outside that loop; none is external in this actual file. Visual and scientific review remains the independent cell-association check.
- No material extraction blocker was found. Keep the stated visible-text scope. The receipt's `network_requests: 0` is declared script accounting, not an independent measurement of LibreOffice process egress.

The only subsequent `probe.py` change observed is disabling bytecode writes; current SHA-256 is `72280c942d3e98f844af2a19af85b08382aad1d134eb9ab8f67637d2b41c510b`. Reviewed conversion script SHA-256 is `89a7579dc93aa62cf9cf12e4e6dbb51549b9a0f18af94a62296c8600657abee2`. The 12-test run above binds the earlier acquisition/screening implementation; this follow-up is a read-only review of the completed local extraction and added bytecode setting.
