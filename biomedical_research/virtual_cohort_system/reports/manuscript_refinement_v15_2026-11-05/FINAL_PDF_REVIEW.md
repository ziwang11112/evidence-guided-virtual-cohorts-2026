# Final v15 reading-PDF review

Decision: **PASS_FOR_READING_COPY**

All 18 pages were inspected from the actual Poppler PNGs at 100 dpi (850 x 1100 pixels), followed by PDF text, font, page-geometry, link-annotation and source checks. The current file contains eight main pages, one reference page and nine supplementary pages. It is a generic reading copy, not an official submission template.

## Reviewed artifacts

- PDF SHA256: `230d524683a061eb7c9e1a45b40efaee3079ee3cce9dd09d57a025d8db6441de`
- TeX SHA256: `42031e4ced7678abb4cb0059ed80df21874da316e7c11fb1551986a84ba78ece`
- All 18 supplied renders postdate the current PDF; both input hashes remained unchanged through this update. Pages 2-8 were visually re-inspected after the minipage change. Page 1 and pages 9-18 have PNG hashes identical to the preceding complete visual review.

## Result

No blocking defects were found. All eight figures, seven tables, 28 references and page numbers 1-18 are present. Captions and displayed panel letters agree, including the left HbA1c/right lipid arrangement in Figure 3. The Figure 3 TC interval crosses zero, and residual correlation has no invented interval. All five supplied-summary outcomes remain present. Supplementary table rows, source inventories and retained implementation incidents are intact.

There is no text outside the page, no replacement glyph, no unresolved-reference marker and no overfull horizontal box or undefined-reference warning. The log has one 0.5949-point overfull output-vbox warning at page 8; direct inspection confirms no visible clipping or overlap. The final PDF retains vector figures. All 47 external-link annotations have HTTPS targets; annotations and target strings were checked, not remote HTTP uptime.

The body is 9.963 pt, captions 8.966 pt, tables 7.970 pt and references 8.468 pt. The new figures have minimum extracted sizes of 7.564 pt (Figures 2, 3 and S3) and 7.262 pt (Figure 4 constructor IDs). All new figures are readable at their final manuscript width.

## Nonblocking limitations

- Retained Figure 1 contains five subscript `j` glyphs at 6.948 pt. Retained Figure S2 tick/seed labels are 6.858 pt. Retained Figure S4 includes scenario values at 6.657 pt and ticks/legend at 6.858 pt. These are readable in the full-page review, but this pass does not certify a universal 7-point minimum.
- The page-8 balancing step emits a 0.5949-point output-vbox warning. Both columns, all text and the final sentence are fully visible; this is nonblocking for the reading copy.
- The earlier split-listing issue is resolved: both framed code blocks now stay together, confirmed on pages 2 and 3.
- Final submission declarations and official venue formatting remain unfinished, as disclosed in the document. This review does not certify submission readiness.

## Page-by-page inspection

- Page 1: Title, reading-copy status, abstract and introduction are legible; columns remain inside the page.
- Page 2: Related work, problem definition and method opening are readable. The complete framed pseudocode block now stays together at the top of the right column; no split or missing lines.
- Page 3: Figure 1, full caption and method text remain readable. The two-equation framed listing now stays together in the right column. Retained subscript j glyphs are slightly below 7 points; no visual clipping.
- Page 4: Evaluation design and results opening have stable headings, readable columns and no clipped content.
- Page 5: Table 1 and all six Figure 2 panels fit. The caption identifies all adjustment sets and retains 24 constructions, 72 tables and 216 estimates.
- Page 6: All six Figure 3 panels fit; the left HbA1c and right lipid column order matches caption letters. The TC band crosses zero; residual correlation has no band.
- Page 7: All five Figure 4 panels fit. Caption preserves L/R input conditions, 18 final tables, 30 means and 90 seed statistics; no hidden-reference claim is introduced.
- Page 8: Discussion and supporting materials remain fully visible in balanced columns. The 0.5949-point output-vbox warning produces no visible clipping, overlap or lost sentence; the repository link and final submission-status sentence remain intact.
- Page 9: All 28 references fit on one readable page. Link annotations align with the blue source labels; no truncation is visible.
- Page 10: Supplement begins cleanly. Table S1 retains six endpoints and native-unit contrasts; S2 introductory text remains readable.
- Page 11: Table S2 retains all five summary-study analyses. Open-retrieval methods and results continue without clipping.
- Page 12: Figure S1 retains all six primary panels, reference rows and interval distinctions. Caption and following text remain readable.
- Page 13: Tables S3 and S4 retain all 12 author-analysis rows and all 12 original sources, followed by the longitudinal-study introduction.
- Page 14: Figure S2 contains both spline panels, all stored conditional intervals and a complete caption. Tick/seed labels are 6.858 points but readable at the inspected size.
- Page 15: Figure S3 retains four dispersion panels and 36 values. Units, SD definitions and missing lipid intervals are distinguished in the caption.
- Page 16: Table S5 retains all 18 author-analysis combinations; Table S6 retains all six authors and the 22/132 totals. All rows and notes fit.
- Page 17: Figure S4 retains seven effect panels and the dependence-sensitivity panel. Small retained labels are 6.657-6.858 points but readable; no clipping or label overlap is visible.
- Page 18: Final supporting-record and implementation-incident text is complete, with repository link and clear unfinished submission-declaration status.

The JSON companion records per-page render hashes, font minima, link counts and complete checks. No source or plot was modified during this review.

Update verification: the changed main pages 2-8 were re-inspected; all unchanged reference and supplementary page renders match the prior reviewed bytes. The decision remains **PASS_FOR_READING_COPY**.
