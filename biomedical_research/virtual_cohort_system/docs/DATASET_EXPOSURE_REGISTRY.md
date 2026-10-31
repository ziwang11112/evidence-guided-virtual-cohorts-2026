# Dataset exposure: cross-project admission entry point

31 October 2026. This is a minimum verified index, not an exhaustive list of every historical dataset. Consult the [27 October experiment index](../../github_review_preparation_2026-10-27/EXPERIMENT_INDEX_DRAFT.md) and source dossiers when admitting a candidate. A search restricted to `virtual_cohort_system` is insufficient: relevant earlier experiments live in sibling directories.

## Mandatory admission order

1. Search candidate study names, cohort aliases, DOI/accession and filenames across the complete `biomedical_research` workspace, including its historical experiment index. Inspect protocol/admission and completion records, not patient tables, to classify prior use.
2. Inspect already available file identities before trying downloads. A matching checksum establishes file identity, not a new independent cohort. Reacquisition, a new folder, another Agent or a different analysis cannot reset exposure.
3. Classify source-only, development-target, revealed-confirmation-target, metadata-only and uncertain prior use. Preserve aliases and study-family overlap. An unrecorded prior result must be resolved before calling a target fresh.
4. Only then pursue data/metadata access and a prospective protocol. Previously exposed datasets can support explicitly labelled development work where authorized; they cannot be silently promoted to new confirmation.

## Verified minimum registry

| Study / alias | Known prior role | Admission consequence | Record |
|---|---|---|---|
| NAGALA; Murakami Memorial Hospital; Okamura; Dryad 10.5061/dryad.8q0p192; Zenodo 4996032 | Reserved population target in the completed 25 October cross-study pilot; actual target correlations independently audited | Closed to new-confirmation claims in this cycle; local original workbook already exists | [Prior protocol](../../cross_study_virtual_cohort_pilot_2026-10-25/PROTOCOL.md), [population audit](../../cross_study_virtual_cohort_pilot_2026-10-25/CASE_POPULATION_AUDIT.md), [completion audit](../../cross_study_virtual_cohort_pilot_2026-10-25/FINAL_NUMERIC_AUDIT.md) |
| DIETFITS, six-month intervention | Reserved intervention target in that same completed pilot | Not a new independent confirmation target | Same protocol and completion audit |
| Rich Healthcare, China | Source study/data summaries in the 25 October population pilot | Prior source exposure must be declared; do not assume its relations are unseen | Same protocol and population audit |
| NHANES 2011–2012 | Source study/data summaries in the 25 October population pilot | Same survey family as later targets; not an unseen source | Same protocol and population audit |
| NHANES 2007–2008 | Revealed M17-B reference | Closed to tuning and fresh confirmation | [M17-B](../MILESTONE_17B_RESULTS.md) |
| Other M13-B, M15-B, M16 references | Completed/revealed in their respective milestone records | Closed; check exact cycles and inclusion sets in their original manifests | [Roadmap](IMPLEMENTATION_ROADMAP_2026-10-30.md) |
| Framingham teaching data | Candidate metadata inspected in this cycle; earlier Framingham literature also appeared as source evidence | Reject current teaching release for publication-facing validation under official documentation; do not confuse it with research-access cohorts | [Current review](../reports/autonomous_research_2026-10-31/admission/data_review.md) |
| LARS / Efron diabetes 442-patient example | Candidate metadata and incidental teaching snippets inspected in this cycle | Not admitted: source-population/measurement metadata insufficient for this task | [Current review](../reports/autonomous_research_2026-10-31/admission/lars_diabetes_metadata.md) |

The current cycle initially preferred NAGALA from official repository metadata before the full sibling-directory audit. That provisional preference was withdrawn when prior use was found. No new generator or target evaluation had occurred. Keep this controller workflow failure and the superseded recommendation visible; do not count the discovery as a new biological result.
