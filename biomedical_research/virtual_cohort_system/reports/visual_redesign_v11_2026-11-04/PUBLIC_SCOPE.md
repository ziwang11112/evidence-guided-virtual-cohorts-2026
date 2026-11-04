# Public scope of the v0.11 visual redesign

This versioned release contains original revised manuscript text, an expanded scientific Agent framework, five original scientific figure sets, a local HTML gallery, the reading/Overleaf package, and independent scientific and visual reviews. It changes presentation, organization and explanation. It adds no cohort generation, clinical model fitting or scientific experiment.

The gallery's static links, image assets and ZIP integrity were checked. Browser rendering remains unverified because the Chrome plugin rejected its local file URL; no alternate browser surface or indirect workaround was used. The exact manuscript PDF and standalone scientific figures were visually inspected separately.

The fixed allowlist in `export_reviewed.py` includes:

- The framework content audit and input manifest; Figure 1 and Figures 2–5 independent reviews; draft-change audit; final PDF reviews; completed state; visual-design note; this scope; the exporter and diagram-repair helper.
- The project README, manuscript README and current research-focus pointers; the root README template, published as the repository-root README; and the complete v0.11 Markdown draft.
- Exactly five original figures in SVG, PNG and PDF, three figure-build/render scripts, two numeric-binding JSON files, two caption documents, a figure README and its HTML gallery. The editable diagram is embedded in its exports and can be regenerated; a standalone `.drawio` source is neither required nor exported.
- The v0.11 reading package: `paper.tex`, `paper.pdf`, the build script, input manifest, README, `overleaf_v11.zip`, and the five copied figure PDFs. ZIP contents are checked against the specified original package members.

Patient-level records, generated participant tables, original reference images, complete third-party papers and codebooks, internal model contexts, credentials, browser caches, intermediate screenshots, logs and temporary files are excluded. Scientific coefficients, uncertainty limits, aggregate summaries, exact display transformations, source locators and hashes remain available for reproduction and review. Existing frozen experiments and earlier draft versions remain unchanged.

The exporter requires a clean existing review checkout at commit `e82f3b170e6fe84d360b21d54c02e0ecd2a8ef94`, a state of `complete_independently_reviewed`, and every required allowlisted file. Pending artifacts must be completed before execution. Missing files, unexpected ZIP members or unresolved public links cause a failure; no current manuscript reference is silently removed. Markdown links and concrete HTML `href`/`src` references are checked against existing tracked public files and the new allowlist. Local navigation from `work/` is rewritten to `reports/`, with unique historical report-path resolution retained.

JSON values and whitespace are preserved. Frozen hashes and local source paths within scientific bindings continue to identify their original artifacts. A separate export manifest records each local-source hash and the actual public-byte hash, including any changed navigation or UTF-8 byte representation. These distinct identities must not be confused when reproducing a figure.

PDF, PNG and ZIP payload entries use `content_base64`; the coordinating publisher must create the corresponding Git blobs with base64 encoding and replace each payload field with its returned blob `sha` before tree creation. Other allowlisted files use text `content`. Payload parts retain complete file entries and report their exact sizes; an individually large figure can occupy a part larger than the normal grouping limit.

The exporter only prepares payload parts and manifests in this report directory. It does not modify the review checkout, create remote blobs, commit, submit or push. The HTML gallery uses the original figure assets; no analysis is performed in the browser. The PDF remains a generic reading copy, and the ZIP is an editable starting package rather than a certified official conference submission template.
