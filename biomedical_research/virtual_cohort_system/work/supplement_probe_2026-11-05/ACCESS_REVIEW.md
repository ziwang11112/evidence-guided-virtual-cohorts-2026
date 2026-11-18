# Independent access review

Scope: one previously identified supplement for PMC6458679, Additional file 3, `12889_2019_6698_MOESM3_ESM.doc`. This initial review read only gateway/adapter source, adapter documentation and the prior E01 source-only notes. It made no network request, accessed no row-level/target/evaluation data and changed no existing file.

## Minimum implementation

The vendored `FORMATS` omits `.doc`; `source_links` therefore records this linked item as unsupported and `fetch_supplement` rejects it before downloading. An allowance change alone cannot make the existing parser support it. Preserve that behavior and the frozen session. A standalone additive probe can acquire precisely this item without refetching the already approved article.

Before any request, verify the cached parent XML and manifest using their content-derived paths, byte lengths, SHA-256 hashes and matching `artifact_approved` events under the original configuration. The adapter's `_approved_bytes` supplies the relevant pattern; do not instantiate a mutating Session or call `_prepare`/`_register_result`. Bind the new probe contract to the original task/configuration/exclusions, source identity, parent version and source artifacts. Check the exact href occurs in a JATS supplementary-material element, maps uniquely to the manifest basename and points to the pinned version's official object with its expected MD5. Preserve the original unsupported status in the receipt.

Use a fixed, separately declared cumulative probe budget, a lock and atomic reservation before each HTTP attempt. Failed requests spend budget. Permit no implicit search, retries, other supplements, parent download, alternate host or redirect. Enforce finite response size and timeout, byte count, final URL, acceptable MIME and manifest checksum before extraction. A later local parse must consume the existing verified bytes rather than redownload them.

Choose a parser from actual bytes, not the `.doc` extension. Reject unsupported containers, partial extraction and malformed/truncated payloads. Record parser/version and extraction scope. Macro or embedded-object handling must fail closed or be explicitly bounded; extracted text is not a claim to have screened every binary payload. Screen full extracted text, table text and textual metadata with the original exclusions before returning accepted content. Maintain opaque error reporting for rejected material. Persist accepted probe artifacts/receipts only under this new work directory; do not register them in the original evidence bundle.

## Focused verification

- Provenance: changed artifact bytes/size/name, missing or configuration-mismatched approval event, changed parent version, absent/multiple href or manifest matches, and changed checksum must reject before usable content is returned.
- Acquisition: wrong final URL/redirect, unexpected content type/encoding, oversized or short response, timeout and checksum failure must reject; a consumed budget must remain consumed on rerun, including after failure.
- Parsing: test the actual detected file format; malformed container, incomplete parser output, table boundary loss and exclusion aliases in table/metadata must not silently produce accepted evidence.
- Conservation: compare frozen-bundle file hashes before and after; confirm no old state/audit/registry/config/task changes, no network call during cached local extraction, and no second source acquisition.
- Scientific readout: verify S1/S2 table titles, complete headers, row labels, units, signs, reference groups, superscripts, missing-symbol conventions, confidence limits and footnotes. Record exact model adjustment, analytic sample, survey weighting and HbA1c scale before interpreting any number.

## Scientific interpretation boundary

The prior cached caption identifies S1 as anthropometry/glucose and S2 as anthropometry/HbA1c regression tables adjusted for age and sex. Actual signed BMI estimates may therefore help the Q2 evidence gap. A caption does not establish a glucose-adjusted BMI estimate, residual covariance, conditional variance or a complete match to the target continuous-age/equal-cell model. The probe must distinguish directly reported estimates from transport/model assumptions and leave unresolved fields unresolved. This initial review has not read supplement contents and makes no numerical conclusion.

Independent code review and test observations will be appended when an implementation is available.
