# Final PDF layout review — v0.14

**Decision: PASS for the current reading copy.** All 16 pages were freshly rendered from the final PDF, reviewed on a contact sheet and inspected individually at full-page image resolution. Five enlarged detail views were also inspected. No page clipping, overlapping body/figure/caption content, broken glyph, malformed table or missing display was observed. This is a layout review, not venue-format or clinical validation.

## Artifact binding

- PDF: `manuscript/conference_draft_v14_2026-11-05/paper.pdf`; 16 pages; 776,516 bytes.
- PDF SHA-256: `f501552df80d7be8ae1eb5f7a7dd176b02974c26c1395d9221b1b5c51557c68a`.
- TeX SHA-256: `72e158c43aeaf2783a81734df1f77ec69c504208a3ba7800c8d492be69d2eb7b`.
- Reviewer: `/root/v14_manuscript_author`, separately reviewing the root-compiled artifact. This agent authored the manuscript text but did not compile or edit the reviewed PDF/TeX.
- PDF and TeX hashes were unchanged from rendering through report creation.

## Images actually inspected

Poppler rendered every page at 144 dpi into this new `pdf_independent_review` directory. The stale 17-page images elsewhere were not used. I inspected `contact_all_16.png`, every full-page image `page-01.png` through `page-16.png`, and five additional PyMuPDF detail views at 234 dpi: Figures 6 and 7, the page-13 reference tail, Table S3 and Table S4. The JSON report records image hashes and every page inspected.

| Page | Observed layout |
|---:|---|
| 1 | Title, reading-copy notice, abstract and introduction; two-column body and footer clear. |
| 2 | Contribution continuation, problem definition and boxed workflow; no box or column collision. |
| 3 | Methods, boxed projection equations and experiment heading; all text within margins. |
| 4 | Figure 1 and caption, full Table 1 including Q5, and evaluation-design continuation; cells and labels intact. |
| 5 | Evaluation text and Q1/Q2/Q3 headings; normal column continuation, no clipped lines. |
| 6 | Table 2 and Figure 2 with six panels and legend; caption and continuing narrative separated. |
| 7 | Table 3 and Figure 3 with five panels and legend; all ranges visible and Q4 heading intact. |
| 8 | Figure 4 and caption, Q4 continuation and Section 4.6 evidence-gap heading; confidence bars and labels intact. |
| 9 | Figure 5 and caption, evidence-gap continuation and Q5 heading; six panels, author labels and intervals intact. |
| 10 | Q5 results and discussion start; units, negative signs and 10^-14 superscript render cleanly. |
| 11 | Figure 6 and caption, discussion; six panels, all author rows, legends and explanatory text intact at zoom. |
| 12 | Figure 7 and caption, discussion tail and supporting-materials section; four panels and all SD/RMS labels clear. |
| 13 | All 28 references in two columns on one page; references 14 and 28 finish inside the page, no orphan reference page. |
| 14 | Supplement heading, eight-panel Figure S1 and full Table S1; labels, analytical-scenario values and all table rows intact. |
| 15 | Continuation note, complete Table S2 and full 18-row Table S3; long labels wrap within their cells; no omitted/clipped rows. |
| 16 | Complete Table S4, total row and explanatory paragraph; clear spare space on the final supplement page. |

## Display and reference completeness

The PDF contains seven main figures plus Figure S1, three main tables plus Tables S1–S4, and all 28 references. References occupy page 13 only; the final entry is complete and no orphan reference page remains. Supplementary results occupy pages 14–16. Table S3 has all 18 author–analysis rows with readable numerical ranges, including negative HDL ranges. Table S4 has all six authors and the total of 132 unavailable checks. Full-page views and the enlarged details show no row or caption collision.

The plots retain their visible panel letters, axis titles, tick labels, author labels, keys and captions. Figure 6 visibly includes the TC reference band spanning zero and the separate residual-correlation reference. Figure 7 preserves both marginal and residual dispersion views. The old figures remain legible at the reviewed rendering scale. An additional text-bound check found no extracted text span outside a page boundary; it supplements, rather than substitutes for, the image inspection.

## Nonblocking layout limits

Figure 6's smallest explanatory text is approximately 4.54 pt in the compiled page. It is vector text, sharp and readable when zoomed, but should be enlarged or reflowed during venue-specific typesetting. The current pass is for a screen reading copy and does not certify physical print-size readability or a submission template. References use approximately 8.47 pt text and fit clearly; the supplementary table text is approximately 7.97 pt and remains readable in the full-page views. Page 16 has substantial spare space after the complete S4 table and note; no content appears lost.

No source, manuscript, figure, generator, evaluated output, PDF or TeX was edited, and no compilation or experiment was run. Only fresh review renders and these review records were created.
