# Offline search-projection replay

**PASS.** Replayed every old approved cached search page: 34 pages / 114 accepted record occurrences. No HTTP, gateway session, constructor/dispatch, generator, credentials, patient data or reference was used. No old source content was placed in new episode inputs.

| Old episode | Cached search pages | Accepted record occurrences | Old initial bytes | New initial bytes | All new hit-page bytes |
|---|---:|---:|---:|---:|---:|
| LIPID_BASE | 8 | 31 | 91,999 | 51,952 | 51,952 |
| LIPID_WORKFLOW | 3 | 12 | 34,536 | 20,134 | 20,134 |
| PNS_BASE | 11 | 37 | 116,252 | 63,492 | 63,492 |
| PNS_WORKFLOW | 12 | 34 | 137,675 | 57,247 | 61,049 |

Initial tool-output bytes fall from **380,462** to **192,825** (49.3% reduction). Traversing all projected hit pages uses 196,627 bytes. These compare the same approved records, retaining the historical usage metadata; they are not a forecast of live context use or scientific performance.

All record identities, original ordering, stable hit IDs and full-record hashes match. Every present abstract and every full record was reconstructed exactly through local pagination, including forced 257-character abstract pages. Missing abstracts remain unavailable. Old first outputs exposed 11 complete literal title fields; new first outputs expose 112 complete identity cards, with any remaining hits reachable by local cursor.

The specification chain also passes static inspection: the submitted model_spec is stored directly, staged byte-for-byte, and passed by the unchanged worker to generate(observed, specification, seed). The task is separate metadata; the evaluator checks staged hashes and uses the same runtime. No host task/model wrapper or root-key remapping is required. No author program was executed to establish this.

The new audit extractor counts returned structured hit cards and explicitly read hit identity/metadata/abstract pages. It does not treat all cached records as exposed. Scientific provenance remains unassessed.

Formatter SHA256: `524bbda37fbe50a228c126cea9f3b8962cf528041adcbf609a127fa677cd14f1`. Full per-page metrics, record hashes and input bindings are in `REPLAY_SEARCH_PROJECTION.json`.
