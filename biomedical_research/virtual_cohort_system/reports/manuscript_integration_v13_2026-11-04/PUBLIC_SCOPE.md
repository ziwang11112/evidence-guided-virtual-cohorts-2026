# Public scope of the v0.13 manuscript integration

This package integrates a completed, separately frozen open-retrieval workflow replication into the manuscript. It contains original manuscript prose and code, original scientific figures, full-precision aggregate figure values, interpretation guides, the reading/Overleaf package, and independent manuscript/PDF reviews. This packaging step creates no virtual cohort, reads no participant/generated row table, and fits no clinical reference.

The fixed allowlist in `export_reviewed.py` includes:

- Manuscript v0.13; project, manuscript and root-repository navigation; current research focus.
- Five main figures and supplementary Figure S1, each in SVG/PNG/PDF. Figures 1–4 and S1 preserve the earlier figure bytes. Figure 5 contains all six primary analyses, four authors and twelve final tables from the completed replication.
- Figure 5's aggregate-only builder, input/output hash bindings, exact aggregate CSVs, caption and Chinese reading guide, plus the figure-package README.
- The reviewed TeX and 13-page generic reading PDF, six copied figure PDFs, build inputs and builder, build/readme instructions and the allowlisted Overleaf ZIP.
- Integration, provenance, source-bibliographic metadata, independent numerical/manuscript and visual PDF review records, preparation scripts and the final planning/status documentation specifically named by the coordinator.

No individual real or generated table, full third-party paper, retrieval cache, credential, rendered PDF review page, contact sheet, compilation log, auxiliary LaTeX output or hidden working directory belongs in the export. The review records may identify original source artifacts by name and hash; those records do not include the source contents. The ZIP admits only the reviewed paper source/instructions, six own figure PDFs and explicitly permitted build/output files, with every member byte-compared to its allowed local source.

Independent draft and PDF decisions must pass and bind the exact current local draft, figure, TeX and PDF bytes. Historical figure reuse must also match the v0.12 local originals and the existing blobs in base commit `baeaf8cf11be00a6f79df5971ad3279a8c6f5aa3`. Fifteen historical figure exports and five identical copied figure PDFs use these verified Git blob SHAs rather than redundant binary uploads. Newly authored binary files use local base64 payload fields for the coordinator's later GitHub connector operation.

All text starts from a raw-byte UTF-8 decode and preserves existing CRLF line endings and any UTF-8 BOM. JSON, code, CSV, TeX and SVG content is not normalized. Markdown link destinations are rewritten from local `work/` to public `reports/` only as needed and every relative Markdown link must resolve against the existing public tree plus the explicit allowlist. No reference is dropped to make validation pass. Scientific hash records retain their original local paths and identities; the export manifest separately records public-byte hashes and any navigation rewrites.

Running the exporter without `--prepare` performs read-only validation. The coordinator must declare the package ready before `--prepare` writes local payload parts and manifests. That operation still does not publish, create Git objects, update refs or push. `PUBLIC_EXPORT_MANIFEST.json` is a nonrecursive release record; local transport parts and `PUBLIC_PREPARATION.json` remain outside the release allowlist. Publication and any separate post-publication receipts are controlled by the parent task.
