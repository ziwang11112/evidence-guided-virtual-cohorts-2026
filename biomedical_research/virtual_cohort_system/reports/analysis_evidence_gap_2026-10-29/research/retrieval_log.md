# Bounded retrieval log

Date: 2026-10-29. Six search queries used of maximum six. Source-only: no target, prior results, project README, milestone reports, or agent inventory inspected. Read the evidence-cohort-generation skill, its harness interface, and `cohort_harness/contracts.py` for schema orientation only. This extraction is not a harness-approved evidence registry.

## Search calls

First batch (3 queries, web search):

1. `triglycerides body mass index age interaction cohort age stratified triglyceride levels BMI study`
2. `"triglycerides" "age" "BMI" "interaction" "HUNT"`
3. `"triglycerides" "age" "body mass index" "stratified" "Copenhagen"`

Second batch (3 queries, web search):

4. `"Chinese Population-Wide Lipid Trajectories" BMI triglycerides age full text`
5. `"Age-related trends in lipid levels" "034226" PMC`
6. `triglycerides BMI "age groups" interaction fasting "cohort" -NHANES -Korea -Korean -TyG`

No later search queries or metadata searches were issued. URL opens, source-mirror fetches, and attachment retries below are retrieval actions, not unreported searches.

## Screening decisions

- **Retain Mikkelsen 2023 Tromsø7**, DOI 10.3389/fnut.2023.1158383: direct joint age × BMI model; main-text tests extracted; table magnitude access failed.
- **Retain Zhang 2026 China-PAR**, DOI 10.1016/j.jacasi.2026.01.013: exact age-stratified BMI slopes and CIs extracted from primary full-text XML, Tables 2–3.
- **Not retained after access failure:** `https://bmjopen.bmj.com/content/10/3/e034226` and `https://bmjopen.bmj.com/content/bmjopen/10/3/e034226.full.pdf`, both 403. This age-trend paper appeared promising for adjusted age association but no numeric evidence was admitted from snippets.
- **Not pursued:** Greenfield 1980 (167 subjects), GOLDN lipidomics, British 1958 birth cohort, Copenhagen meal-timing/lipoprotein study. These were source leads only; no extracted eligible age × BMI effect entered evidence.
- **Excluded:** NHANES and Korean national-survey search results; no outcome tables from them were opened or extracted. Incidental excluded snippets may appear in web results. Cancer/CVD/diabetes outcome interactions and TyG composites were not treated as models of TG conditional on age and BMI.
- **Known evidence, not new:** Bansal 2007 appears in Tromsø references; no re-discovery counted. Oh 2019 was not pursued.

## Successful retrievals

| URL | Outcome |
|---|---|
| https://pmc.ncbi.nlm.nih.gov/articles/PMC10308115/ | Web full text accessible |
| https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2023.1158383/full | Web full text and local publisher HTML retrieved |
| https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10308115/fullTextXML | Full XML saved; 136142 bytes |
| https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13491077/fullTextXML | Full XML saved; 135875 bytes; Tables 2–3 inspected |

Exact saved-byte hashes are in `source_artifact_manifest.json`. Same-paper mirrors are not independent evidence.

## Unsuccessful retrievals and exact supplement status

- `https://www.jacc.org/doi/full/10.1016/j.jacasi.2026.01.013` and `https://www.jacc.org/doi/10.1016/j.jacasi.2026.01.013`: web 403; primary XML mirror subsequently succeeded.
- `https://pmc.ncbi.nlm.nih.gov/articles/PMC13491077/`: browser-check page returned; `?pdf=1` inaccessible. No challenge bypass attempted.
- `https://pmc.ncbi.nlm.nih.gov/articles/instance/10308115/bin/Table_1.DOCX`: web browser-check page; direct request produced 1817-byte HTML, verified not ZIP/DOCX and saved as `Mikkelsen2023_supplement_access_failure.html`. It is not a source table.
- `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10308115/supplementaryFiles`: first 30-second timeout; one final 60-second timeout. No bytes saved as a valid supplement.
- `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13491077/supplementaryFiles`: 30-second timeout. No supplemental log-TG or BMI-curve extraction.
- `https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC10308115` and `https://pmc.ncbi.nlm.nih.gov/utils/oa/oa.fcgi?id=PMC10308115`: 404. No OA tarball URL was obtained.
- `https://europepmc.org/articles/PMC10308115/bin/Table_1.DOCX`: 403.
- `https://www.frontiersin.org/api/v4/articles/1158383/file/Table_1.DOCX`: 404.
- `https://www.frontiersin.org/files/Articles/1158383/fnut-10-1158383-HTML/image_m/fnut-10-1158383-t001.docx`: 404. This was a guessed public route, not an observed valid source URL.
- `https://pmc.ncbi.nlm.nih.gov/articles/PMC10308115/bin/Table_1.DOCX`: 404.
- `https://www.frontiersin.org/files/Articles/1158383/fnut-10-1158383-s001.docx`: 404. This was a guessed public route, not an observed valid source URL.
- `https://www.frontiersin.org/articles/10.3389/fnut.2023.1158383/supplementary-material/10.3389/fnut.2023.1158383.s001`: redirected to full article HTML, not supplement.
- Parent independently identified the exposed XML path `ec58/10308115/fac328bf60fe/Table_1.DOCX` (686738 bytes, bucket app); the same value was then verified in locally saved primary XML. `https://cdn.ncbi.nlm.nih.gov/pmc/blobs/ec58/10308115/fac328bf60fe/Table_1.DOCX` returned 404 directly and inaccessible via web. Path/size metadata do not establish successful retrieval.

No Figure 3 digitization or coefficient inference was performed. The requested 28 nonreference ratios and CIs remain unavailable. Repeated access failures justify stopping retrieval rather than fabricating extraction.

## Extraction checks actually performed

- Confirmed XML well-formedness with Python ElementTree.
- Read main methods and complete Table 2–3 text for China-PAR; inspected exact Table 3 footnotes to distinguish sex interaction from age interaction.
- Cross-checked Tromsø sample-count conflict in main results versus Figure 2 caption.
- Checked failed alleged DOCX bytes for ZIP header; renamed the HTML response to prevent mistaken reuse.
- Computed SHA-256 for three successful source artifacts.
- No simulation, generator execution, source replay, target evaluation, or harness admission occurred.
