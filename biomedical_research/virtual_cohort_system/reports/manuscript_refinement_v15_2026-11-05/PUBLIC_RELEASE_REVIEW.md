# Independent public release review — v0.15

**PASS** for the exact manifest `1a94d89d4ff4c67a5681cd8f89b73cd923372e15dda2919abf48d40f663668be`. No actionable release finding remains.

Reviewed on 5 November 2026 by `/root/venue_and_story_audit`. This audit covers the explicit local staged allowlist and raw transport bytes; it performs no remote operation.

## Verified release boundary

The 73 manifest records total **5,593,705 bytes** and reference 64 unique blobs. An independently reconstructed allowlist matches all 73 paths. The release adds 69 v15 paths and updates four navigation/current-focus files against base commit `0b41c907da1fc391aa81e547c676d9e3d13166bf`; it contains no deletion or replacement of an existing frozen scientific result.

Included artifacts are the original manuscript and reading package, eight figures (four redrawn from frozen aggregates and four retained), original plot/build/export code, aggregate numeric bindings, editorial and independent review records, and navigation. No real or generated participant tables, third-party original papers/codebooks, unrelated data files, private review screenshots or detected credentials are staged. Citations and source provenance are references, not copies of third-party originals.

## Integrity and links

For all 73 records, independently recomputed local and staged SHA-256, Git blob SHA-1 and byte count match the manifest. Every referenced blob exists. All non-Markdown bytes equal their declared local sources. Six Markdown files differ only in link targets; the manifest enumerates 36 rewrites. Every relative Markdown file/directory destination resolves against the pinned base tree plus staged paths.

The scientific review binds local draft `eb8a813bb328700a03f186033c4ff102ac0093f00b9a33425c936f71ef021cf3`. Public draft `ab2a10ed28064fcadedbcc17687748b0cec7737f3cfc32542ad2ce6f96b9beb3` differs only in those navigation rewrites. The final 18-page PDF is `230d524683a061eb7c9e1a45b40efaee3079ee3cce9dd09d57a025d8db6441de`; its hash agrees across the PDF review, state, manifest and package inventory. The TeX and eight figure-PDF hashes agree with the build inputs.

The ZIP `dd952676df7b8b154097cae38ab4bcf9d25b4c095ee57d5ffe2d61dfcda960da` contains exactly 13 reviewed members: TeX, PDF, build inputs, build script, README and eight figure PDFs. CRC/path checks pass, every member matches its staged counterpart byte-for-byte, and the inventory matches every member hash and size. No hidden extra archive payload is present.

Nine JSON files parse; 17 PDF files open without embedded attachments; PNG verification and SVG parsing pass. Credential/private-key pattern checks of staged bytes, PDF text and ZIP members produce no match. The only external SVG href is a draw.io documentation help link.

## Scope notes and limitations

**Eleven unreferenced old transport blobs are excluded from this PASS.** They remain local and must not be uploaded by directory glob. Only the exact manifest records are reviewed. Neither this report nor the manifest asserts that GitHub synchronization has happened; remote bytes need a separate verification receipt.

This audit does not repeat scientific experiments or the separate visual review, certify the full historical repository, or guarantee detection of every possible secret pattern. Relative destination checks do not test external servers or Markdown anchors. The reading copy remains generic formatting, and the ZIP is a local package rather than an online Overleaf project. Any changed manifest or payload invalidates this exact-byte approval until checked again.
