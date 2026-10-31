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


## Second-cycle additions — 31 October 2026

The fuller [cross-workspace inventory](../reports/autonomous_research_cycle2_2026-10-31/history/DATASET_USE_INDEX.md) records 39 study/cycle entries and supersedes treating the minimum table above as exhaustive.

| Study / family | Newly verified role | Admission consequence | Record |
|---|---|---|---|
| ENSANUT 2018–2019 Mexico; INEGI catalog 590; INSP laboratory/anthropometry release | Processed public files linked; outcome-blind documentation-consistency amendment; 6,931-person eligible reference evaluated once after all final generators froze; independently recomputed | Now revealed and closed to generator tuning or new-confirmation claims. Re-downloading or selecting a new analysis from this release does not reset exposure | [Case admission](../reports/autonomous_research_cycle2_2026-10-31/CASE_ADMISSION.md), [result report](../reports/autonomous_research_cycle2_2026-10-31/results_report/REPORT.md) |
| KNHANES Korea | Candidate metadata/access review only; no new patient file acquired in this cycle | Official access route required personal information/terms; no application submitted; prior literature/source exposure still applies | [International data review](../reports/autonomous_research_cycle2_2026-10-31/admission/INTERNATIONAL_DATA.md) |
| ANSUR II | Backup candidate metadata and incidental public snippets only; not selected; no full IPD acquisition | Not a new validated target; incidental exposure remains recorded | Same international data review |
| Jansen 2013 Lifelines; Pani 2008 NHANES/FOS; Liu 2015 NHANES | Source aggregate evidence read/audited and disclosed to builders; no source IPD supplied. Pani/Liu survey cycles overlap | Source exposure and study-family overlap must be declared; these are not three independent patient validations | [Source audit](../reports/autonomous_research_cycle2_2026-10-31/evidence/INDEPENDENT_SOURCE_AUDIT.md) |

No claim is made that the foundation model had never encountered public study results. The procedural blind separates the supplied task/evidence and newly evaluated target results; it does not establish pretraining non-exposure.

## Core-v0 admission checkpoint — 31 October 2026

The current [bounded intake](../reports/real_case_admission_v0_2026-10-31/REPORT.md) checked PNS, ANSUR II and CHNS. Three family slots are consumed; no new participant file or scientific validation was produced. The first grouped metadata search preceded completion of the full history audit, a recorded sequencing failure. Consult the full inventory before future candidate searches.

| Family | Clarified exposure / access | Consequence |
|---|---|---|
| Brazil PNS 2013 laboratory sample | Previously evaluated M10 HbA1c target; exact history in the full inventory | Closed for fresh confirmation in this intake. Different indicators are not an automatic reset. |
| ANSUR II | Earlier reviewer saw sex-specific anthropometric summaries. The prior note at `work/autonomous_research_cycle2_2026-10-31/admission/ANSUR_METADATA.md` (local provenance summarized in this intake's [history audit](../reports/real_case_admission_v0_2026-10-31/history/CROSS_PROJECT_FAMILY_SCREEN.md)) is more precise than the abbreviated table above. | Unqualified cohort-wide blindness is unsupported; specific joint analyses may remain unexposed but require a new explicit admissibility argument. Not admitted here. |
| CHNS / China Health and Nutrition Survey | Prior approved result-bearing abstracts: PMC8214016 (urate/insulin) and PMC7282081 (BMI/lipid/cognition). Current official site moved to `chns.cpc.unc.edu`; it links UNC Dataverse. Actual public-file acquisition remains unverified. | Not metadata-only or globally unseen; not universally excluded either. Retain as a candidate only, map relation/equivalence exposure and resolve remaining gates before F2. |

See [history audit](../reports/real_case_admission_v0_2026-10-31/history/CROSS_PROJECT_FAMILY_SCREEN.md), [current official access](../reports/real_case_admission_v0_2026-10-31/access/CHNS_ACCESS.md), and [independent admission review](../reports/real_case_admission_v0_2026-10-31/review/INDEPENDENT_ADMISSION_REVIEW.md). Turkana is an unreviewed deferred lead in this intake, not a fourth admitted/screened candidate.
