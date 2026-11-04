# Provisional submission text for manuscript v0.8

Prepared 3 November 2026. These are author-review materials for a prospective PLOS Digital Health Research Article reporting a method. They are not a submitted manuscript, completed declarations or an assertion of acceptance. See the [venue assessment](VENUE_AND_SUBMISSION_PLAN_v08_2026-11-03.md) for current official sources and the distinction between rules and our fit judgment.

## Author Summary

Biomedical researchers often need measurements that were not collected, cannot be accessed, or were never observed together in one study. Published papers still contain useful information about these measurements and their relationships. We developed an agent-assisted procedure that turns curated published findings into a model that generates virtual datasets. The agent decides how reported findings enter the model, states assumptions about missing relationships, and supplies executable code. Researchers can then apply familiar statistical analyses to the generated records.

We examined generation from external studies, generation with accessible summaries of a target population, and reconstruction of a published longitudinal model. Additional relationship evidence improved agreement for several analyses but not all. Target summaries supported closer reconstruction. The longitudinal example reproduced a stronger relationship but did not consistently preserve a weak relationship or the spread of high biomarker values.

Our results show practical analytical uses of virtual data and identify where the available evidence remains insufficient. These datasets express the consequences of evidence and modeling assumptions; they do not recover an individual's unmeasured results or create new clinical observations.

## Suggested keywords

Synthetic biomedical data; scientific agents; published evidence; joint generative models; scientific analysis; virtual cohorts.

## Cover-letter scientific paragraph for author review

This manuscript addresses a practical biomedical research problem: constructing analyzable data when individual measurements are inaccessible or unavailable, while relevant findings remain distributed across published studies. We present an agent-assisted procedure that retains the population and statistical meaning of those findings, constructs an executable joint model, and makes completion assumptions explicit. Our evaluation separates external-evidence development, target-summary reconstruction and a published longitudinal-model example. The results demonstrate analysis-specific utility while retaining effect-size mismatches, weak-effect instability and distributional limitations. The contribution is a reusable evidence-to-model procedure and its observed scientific uses, supported by public code, aggregate results and reproducible displays.

This paragraph is not a complete cover letter. Exclusivity, originality, author consent, conflicts and any related-submission statements require author confirmation and have not been supplied or inferred.

## Availability text: supported facts and unresolved submission items

Supported wording for the draft:

> Original code, curated evidence specifications, protocols, analysis-level aggregate results and independent checks are available in the public project repository. A versioned offline entry point reconstructs the manuscript's numerical displays and redraws quantitative figures from pinned public aggregate artifacts. Real participant records, generated individual-level tables, third-party full documents and credentials are excluded from this public export. The entry point reproduces aggregate displays, rather than rerunning the clinical-data analyses or Agent constructions.

Before submission, reconcile the journal's data and software requirements with the actual project release:

- Give official dataset identifiers, versions and access conditions for each underlying reference. Public code does not grant access to those datasets.
- Determine which minimally sufficient underlying artifacts must be accessible for the claims. Do not describe all excluded files as legally restricted merely because they are currently kept local. Real and generated individual-level tables remain local under the user's current instruction.
- Choose and apply an appropriate software license only after ownership and third-party components have been checked. A filename search of the current public checkout found no LICENSE, COPYING or CITATION file; repository visibility alone is not an open-source license.
- Complete the data-availability statement and repository release identifier for the actual submitted edition. The older v0.7 reproduction lock remains intentionally versioned and unchanged.

## Author information still needed

| Item | Current state |
|---|---|
| Author names, order, affiliations and corresponding author | Not finalized for this manuscript; do not infer from download registration |
| Author contributions | Must reflect actual scientific and writing contributions |
| Funding and competing interests | Not yet supplied; do not invent a negative declaration |
| Reference-data access and ethics statement | Must describe actual secondary-data use, source conditions and applicable institutional requirements; Agent review is not ethics approval |
| AI-use disclosure | Describe actual model-assisted scientific construction, coding, reviewing and writing; distinguish documented runtime metadata from historical information that was not metered |
| Software licensing and final data availability | Requires release/rights decisions described above |
| Submission exclusivity and author approval | Required before an actual submission; not assumed here |

## Current preparation boundary

The paper can now be edited and formatted around its completed results. No new experiment, patient-file release, software licensing action, journal contact or submission is performed by this document. The current review draft remains the source for scientific content; the v0.7 aggregate reproduction package remains its numeric and figure foundation.
