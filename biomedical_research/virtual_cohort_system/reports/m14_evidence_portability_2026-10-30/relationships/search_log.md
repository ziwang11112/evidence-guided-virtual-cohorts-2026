# M14-A relationship/residual search log

Audit date: 2026-10-30. Branch limit: three additional primary studies fully read. No target files or target-result websites were accessed. The supplied M13-B aggregate report was the only target-result context.

## Actual search queries, in execution order

1. `Jackson Stanforth Gagnon 2002 effect sex age race estimating percentage body fat body mass index HERITAGE Family Study pdf`
2. `Deurenberg Weststrate Seidell 1991 body mass index measure body fatness age sex specific prediction formulas pdf`
3. `Gomez Ambrosi 2012 clinical usefulness new equation estimating body fat CUN BAE full text SEE`
4. `"The effect of sex, age and race" "10.1038"`
5. `"body mass index" "conditional" "DXA" "residual" non NHANES`
6. `"body fat" "BMI" "SEE" "heritage" 2002`
7. `"0802006" pdf Jackson Stanforth`
8. `"Clinical Usefulness" "CUN-BAE" "RESEARCH DESIGN" 2012`
9. `"The effect of sex, age and race" filetype:pdf`

Search was bounded and purposive, not systematic or exhaustive. Search output snippets were screened; unrelated results were not opened. Results containing NHANES were not followed as generator evidence. In particular, the Berkson-error paper with NHANES 1999-2006 data was excluded at snippet screening; other NHANES disease/obesity hits were irrelevant. A 2026 BIA-only body-fat paper and child-cohort articles were not selected because they did not match this adult DXA evidence gap. Review articles and repositories of formulas were not admitted as primary evidence.

## Selection chronology and access

- Initial declaration to root, before fulltext reads: Deurenberg1991; Jackson2002; Gomez-Ambrosi2012.
- Deurenberg1991 publisher PDF opened successfully and its full relevant methods/results/tables were read.
- Jackson2002 DOI 10.1038/sj.ijo.0802006: metadata/abstract snippets only. Nature article and PDF requests redirected to an inaccessible identity-provider page. No fulltext was read. A search result reference list then surfaced Pasco2012 by title.
- Before reading Pasco2012 or any Jackson fulltext, the replacement was declared to root for closer adult population-based DXA relevance. Root acknowledged. No target-fit comparison motivated selection. Jackson remains an access-limited, non-admitted screen. There were no replacements after a study was fully read.
- Pasco2012 publisher HTML and PDF succeeded. Full methods/results/table4 and relevant figure/table footnotes were read; table4 and methods were visually verified from rendered PDF.
- Gomez-Ambrosi2012: DOI/publisher web access returned403, PMC returned a browser challenge, and CiteSeer PDF returned403. The official Europe PMC fullTextXML endpoint succeeded via Python urllib (60,140 bytes). Complete relevant main-text methods/results/discussion were read from that XML. The main XML includes equation and numerical SEE results. It links image-only tables and a supplement.
- Gomez supplementaryFiles endpoint first timed out at30s; a second55s attempt also timed out. EuropePMC PDF returned403; the PMC supplementary PDF endpoint returned404. Final supplement status is recorded in selected_studies.md and source_manifest.json.

## Local retrieval and verification

Python urllib downloaded the two publisher PDFs and the official Europe PMC XML. The bundled runtime lacked `requests`, so the initial retrieval script failed before downloading and was rerun with standard-library urllib. A first console extraction failed on Windows encoding after writing the Gomez text; rerunning with UTF-8 stdout succeeded. PyMuPDF extracted source text and rendered relevant PDF pages. These are retrieval/encoding issues, not missing scientific results.

Cache content is excluded by relationships/.gitignore and is local only. No source PDF, fulltext XML/text, table image, or participant data is intended for GitHub. The small original extraction/decision files and manifest contain citations, facts and audit reasoning only.
