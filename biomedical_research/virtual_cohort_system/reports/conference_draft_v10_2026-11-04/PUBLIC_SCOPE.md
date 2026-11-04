# Public scope of the v0.10 conference-style draft

This publication unit contains original scientific writing, original aggregate figures, plotting and document-build code, independent reviews, numeric bindings and a two-column reading/Overleaf package. It changes presentation and narrative only. It includes no new cohort generation or clinical refitting and claims no conference acceptance or official template compliance.

The explicit allowlist in `export_reviewed.py` includes:

- The v0.10 Markdown draft; the project README, manuscript README and current-focus document; and the local `ROOT_README.md` template published as the repository-root README.
- The original G-Sim and LLMSynthor reading notes, design decisions, draft/figure reviews, independent numerical-review script, state and this export documentation. Cached primary papers, PDF page previews, browser material and build logs are excluded.
- All five original figure SVGs and PDFs, three plotting/build scripts, captions and numeric/export checks. The method diagram's editable source is embedded in its exports and can also be rebuilt by `build_overview.py`; no standalone `.drawio` source is required. PNG reading previews are deliberately omitted because vector originals are included.
- The article-class LaTeX reading package: `paper.tex`, `paper.pdf`, five copied figure PDFs, README, build-input manifest, build script and `overleaf_v10.zip`. The ZIP is restricted to these specified original package members; it cannot silently include logs, caches or records.

Real or generated participant records, complete third-party papers/codebooks, credentials, private model contexts and unreviewed workspace artifacts are excluded. Aggregate estimates, intervals, distributions, source pointers and file hashes are included to support scientific and graphical checking. Previously frozen experiments and source files remain unchanged.

The exporter requires the expected clean review checkout at commit `a21b08629aa30b3e5b530f3b36565d224147df2d`, a complete independently reviewed state and every explicitly required artifact. Missing files or unresolved public Markdown links stop preparation. Local Markdown navigation is rewritten from `work/` to `reports/`; no draft reference is silently deleted or replaced by a local-only label. External scholarly links remain intact.

Frozen byte hashes inside scientific bindings continue to identify their original local artifacts, including retained local-path identities. JSON values and whitespace are preserved. The public manifest separately records each source hash and the actual exported-byte hash, including any Markdown navigation change. Figure scripts retain their documented local/public input profiles.

PDF and ZIP files are represented by `content_base64` in the locally prepared payload. The coordinating publisher must create each Git blob with base64 encoding and substitute its returned `sha` before tree creation. Text entries use normal `content`. The exporter itself only writes payload parts and manifests in this report directory; it does not change the review checkout, create remote blobs, commit or push.

The supplied PDF is a reading copy and the ZIP is an editable starting package. Venue selection, official submission formatting, authorship and required declarations remain separate work. The existing complete scientific references, all unfavorable outcomes and historical supporting reports remain accessible through the draft and repository navigation.
