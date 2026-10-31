# M17-B local exposure audit

31 October 2026. Metadata/provenance audit only. New target rows and outcome summaries were not opened.

## Sources checked

- Current `docs/IMPLEMENTATION_ROADMAP_2026-10-30.md` and `MILESTONE_17A_RESULTS.md`.
- Historical milestone records M10, M13-A/B, M15-B, M16, and `reports/m13_admission_2026-10-30/exposure_audit.md`.
- Filename inventory under `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research`, including source/custodian data-file names, exposure manifests, and acquisition records.
- Targeted content searches of Markdown, Python, JSON, YAML, and text provenance under the biomedical project, then the workspace, for cycle names and component aliases. These do not inspect binary participant files. The final whole-workspace filename pass included hidden and ignored paths and enumerated 1,304,763 files; it found no canonical DEMO_E/BMX_E/BIOPRO_E XPORT/HTML files and no participant-data filename explicitly identifying NHANES 2007–2008.

## Prior cycles and the decision

| Cycle / task | Established prior exposure | Consequence |
|---|---|---|
| 2011–2012 | Prior `cross_study_virtual_cohort_pilot_2026-10-25/data/source/nhanes2011_2012/DEMO_G.XPT`, `BMX_G.XPT`, and `BIOPRO_G.XPT`. Earlier extraction concerned ALT/AST, but the entire biochemistry file co-stores urate. M13 admission already documented this. | Reject a wholly unopened claim. Prior urate analysis is unresolved, and prior raw acquisition is established. |
| 2009–2010 | Existing `virtual_cohort_system/work/analysis-evidence-gap-2026-10-29/custodian/raw/DEMO_F.xpt` and `BMX_F.xpt`; earlier triglyceride work. | Do not use as a wholly new age/sex/BMI cohort. |
| 2013–2014 | Existing `evidence_gap_loop_2026-10-28/custodian/raw/DEMO_H.xpt` and `BMX_H.xpt`; earlier HDL task. | Do not use as a wholly new age/sex/BMI cohort. |
| 2015–2016 | M10 fasting-insulin cohort and existing DEMO_I/BMX_I files. | Previously used M10 cohort, excluded as fresh. |
| 2017–2018 | Earlier triglyceride/HbA1c/insulin work; M13-B DXA target and M16 urate target. | Closed exposed targets; no tuning or fresh-confirmation reuse. |
| 2021–2023 | M11/HbA1c work and M15-B urate target. | M15-B target is closed; no tuning or fresh-confirmation reuse. |
| 2007–2008 | No canonical DEMO_E/BMX_E/BIOPRO_E files or corresponding acquisition/endpoint-analysis provenance located in scoped searches before this admission record. Initial broad year search found unrelated China-PAR/CIMIC 2007–2008 source-population references. The broader workspace pass found a generic prior literature mention of NHANES 2007–2010 ferritin/hemoglobin work, disclosed below. | Conditional candidate for newly reserved local-cycle evaluation; do not claim absence of every prior mention. |

The broader workspace text search found `biomedical_research/obesity_multimodel_review_2026-10-25/CLAUDE_ROUND1_RAW.txt:46`, a general discussion of published ferritin, hemoglobin and soluble-transferrin-receptor research spanning 2003–06/2007–10/2015–18. It contains no age/BMI/urate measurements or local acquisition claim. Other returned matches were third-party software symbols such as `demo_e`. The broader check therefore qualifies, rather than invalidates, this target's local acquisition/endpoint-analysis freshness.

## Information boundary

The case custodian may later acquire and prepare the reserved real target only after the protocol gate. Root/builders receive metadata and eligibility, not raw target files, real participant covariates, target distributions, or analytical results before freeze. The whole-cohort generator has no observed individual rows. Corpus exclusion covers NHANES studies and NHANES-derived quantitative findings embedded in otherwise independent articles.

This is procedural separation, not OS-enforced isolation. All agents can technically access the shared workspace. The audit cannot establish absence from model pretraining, prior chats, browser history, unindexed archives, external disks or other workspaces. It distinguishes fresh local target acquisition from globally unknown biomedical relationships.

No historical file was changed. No training, paid API, HPC, or raw-target download was initiated by this admission.
