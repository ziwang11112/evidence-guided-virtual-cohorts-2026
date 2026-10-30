# M13 candidate exposure audit — metadata and code only

Date: 2026-10-30. Auditor: `/root/m13_exposure_audit`.

## Decision supported by this audit

**NHANES 2017–2018 whole-body DXA total percent fat and serum urate remain potentially fresh outcomes under this bounded audit. Neither is certified globally unexposed, and neither is a wholly new participant cohort.** This report establishes an information-boundary starting point, not that a case is scientifically ready or that its target relationships are unknown to model pretraining.

No patient-level file was opened or parsed, no target outcome was summarized, and no outcome data were downloaded. Local reads covered documentation, acquisition/analysis code, metadata manifests and filenames. Official codebook reads extracted metadata paragraphs and variable labels with frequency tables removed. No experiment was run and no existing file was changed.

| Candidate | Classification | Evidence and consequence |
|---|---|---|
| NHANES 2017–2018 `DXDTOPF`, whole-body total percent fat | **Potentially fresh outcome; metadata-only, not certified** | No `DXX`/`DXXAG` raw component file or exact `DXDTOPF` use found in the scoped local inventory/code scans. The period and some participants/covariates have already been used for other outcomes. Body-fat outcomes in other studies and DIETFITS DXA literature have previously been discussed. |
| NHANES 2017–2018 `LBXSUA` / `LBDSUASI`, serum urate | **Potentially fresh outcome; metadata-only, not certified** | Proposed in the PRO system specification. No prior exact outcome-alias use in the selected experiment code/docs and no raw `BIOPRO_J` file found in the scoped inventory. Its source packet still needs scientific admission; proposal is not evidence of successful calibration or fresh-target certification. |
| NHANES 2011–2012 urate | **Prior raw co-measurement storage established; prior analysis exposure unresolved** | `BIOPRO_G.XPT` is already present in an earlier pilot's source folder, and the official codebook confirms both urate aliases are in that component. Earlier documentation names ALT/AST extraction, not urate analysis. Storage of the entire component prevents claiming that urate was never acquired. |
| Previously used triglycerides, HbA1c, fasting insulin and HDL tasks | **Known previously used endpoint families** | Milestone and prior pilot records document use. They are unsuitable as globally untouched confirmation endpoints. A different cycle might still support a narrowly defined transport test, with prior exposure disclosed. |
| Other obesity biomarker or PNS creatinine fallback | **Unable to establish** | Not sufficiently audited in this pass. Absence of a finding about these candidates is not an admission decision. |

## Local scope and procedure

Path abbreviations below are anchored to:

- `B = D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research`
- `P = B/virtual_cohort_system`

Read or searched within `P`:

- `README.md`, root `MILESTONE*.md`, `docs/IMPLEMENTATION_ROADMAP_2026-10-30.md`, `docs/PRO_SYSTEM_ADVICE_ADOPTION_2026-10-30.md`, `docs/PRO_FULL_SPEC_REVIEW_2026-10-30.md`, `docs/SCIENTIFIC_ANALYSIS_UTILITY_PLAN.md`, `docs/CONTRIBUTION_FOCUS_AND_PRO_REVIEW_2026-10-29.md` and the PRO specification references returned in `docs/reviews/pro_full_system_spec_2026-10-30.md`.
- Metadata-only `work/m11/custodian/freshness_access_manifest.json`; acquisition code in `work/m11/custodian/prepare_target.py`; inventory logic in `work/analysis-utility-preparation-2026-10-29/nhanes_insulin/inventory_freshness.py`.
- Bounded Python/Markdown searches and filename inventories for endpoint aliases and component names. No referenced patient table was opened.

Parent-directory coverage was not limited to the new system. Selected sibling directories matching `obesity_*`, `cross_study_*`, `exploratory_*`, `insulin_*`, `evidence_virtual_*`, `agent_real_*`, `agent_review_*`, and `population_framework` were searched in code/docs. Additional explicit searches covered `exercise_data_discovery_2026-09-19`, `exploratory_exercise_paper_transfer_2026-10-27` and `evidence_gap_loop_2026-10-28`.

Content searches used `.py` and `.md`, excluding data, reference, source, results, candidate/execution and source-replay directory patterns where applicable. Search terms included word-bounded `DXA`, `DEXA`, `body fat`, `body composition`, `uric acid`, `urate`, `LBXSUA`, `LBDSUASI`, `DXDTOPF`, `DXDTOFAT`, `DXDTOTOT`, `DXDSTPF`, and component aliases `DXX_[A-Z]`, `DXXAG_[A-Z]`, `BIOPRO_[A-Z]`. Earlier tentative `DXXTOT*` aliases were corrected using the official codebook; absence under an incorrect alias was not treated as evidence.

The parent-tree filename inventory excluded the GitHub export clone, `.git`, runtime/cache/virtual-environment directories. These exclusions, selective extension searches, and occasionally truncated aggregate-document output limit completeness. This was not a whole-disk, archive-content, browser-history or prior-chat audit.

### Material local findings

1. **Urate co-measurement already stored.** `B/cross_study_virtual_cohort_pilot_2026-10-25/data/source/nhanes2011_2012/BIOPRO_G.XPT` exists by filename inventory. `B/cross_study_virtual_cohort_pilot_2026-10-25/CASE_POPULATION_AUDIT.md` names the broad panel among the downloaded files and describes `SEQN`, `LBXSATSI` and `LBXSASSI` extraction. The official [BIOPRO_G codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/BIOPRO_G.htm) lists `LBXSUA` and `LBDSUASI`. The raw file itself was not read.
2. **Body composition is not a wholly new topic for the project.** `B/obesity_multimodel_review_2026-10-25/REVIEW_SYNTHESIS.md`, `INTERNAL_JOURNAL_WETLAB_REVIEW.md` and `INDEPENDENT_FINAL_AUDIT.md` discuss DIETFITS DXA, public clinical files versus requested regional imaging data, and the difference between trunk fat and MRI visceral adipose tissue. These are not proof of prior NHANES `DXDTOPF` exposure, but prohibit claiming that all body-composition knowledge is new.
3. **Earlier body-fat measurements exist in another pilot.** `B/obesity_larger_replication_2026-10-25/METHODS_AUDIT.md` describes paired body-fat data in an earlier trial. `B/exercise_data_discovery_2026-09-19/LARGER_DATA_DECISION_2026-09-22.md` discusses baseline body-fat percentage and fat-free-mass availability. Neither establishes NHANES DXA target freshness.
4. **Body fat appeared as a source adjustment variable.** Code and decision documents in `B/evidence_gap_loop_2026-10-28/runs/` mention Taiwan Biobank HDL analyses adjusted for body fat. This is source-literature exposure, not a hidden NHANES DXA evaluation.
5. **Same cycle is not the same as fresh outcome.** Earlier NHANES 2017–2018 TG and HbA1c work, 2015–2016 insulin work, and 2021–2023 TG/HbA1c work are documented. `P/work/m11/custodian/freshness_access_manifest.json` already distinguishes endpoint freshness from participant/cohort freshness and records its own audit limits. The M11 special phlebotomy-weight choice must not be copied into a DXA task.

## Official DXA metadata and its scientific consequences

Source: [NHANES 2017–2018 DXX_J documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm), especially Eligible Sample, Data Processing and Editing, Analytic Notes, and variable headings. Only metadata and labels were used.

### Measurement and eligibility

- Whole-body DXA was administered in NHANES **1999–2006 and 2011–2018**, according to this documentation. The verified candidate is the publicly documented **2017–2018 `DXX_J`** component. No 2021–2023 DXX outcome file was established by this audit; existence of a 2021 body-composition manual alone does not establish a released outcome file.
- Eligibility in 2017–2018 was **8–59 years**. Pregnancy, recent radiographic contrast/barium, self-reported weight over 450 pounds and height over 6 feet 5 inches were exclusion considerations stated in the documentation. An adult-only case would therefore need a declared age range such as 20–59, subject to source compatibility.
- `DXAEXSTS` distinguishes completed valid scans, completed invalid scans and non-scan reasons. Invalid body regions are set missing. The documentation describes declining validity with age and BMI. A valid-DXA domain is a selected measurement population; it should not be silently generalized to all adults or all severe obesity.
- Scan analysis used Hologic **APEX v4.0**. Crucially, the [Data Processing and Editing section](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm#Data_Processing_and_Editing) describes the NHANES BCA option transferring **5% of lean mass to fat mass**, citing the earlier QDR-4500A bias assessment. This is distinct from the machine phantom-QC paragraph saying no additional participant correction was required there.
- Therefore a source labelled merely “DXA body fat” is not automatically on the same measurement scale. Source admission should resolve device/software and BCA correction where possible. A percent-fat-only conversion should not be invented when required mass definitions or components are absent. Unknown compatibility belongs in a documented sensitivity or exclusion decision, independent of target outcomes.

### Alias and leakage boundary

The official total-percent-fat alias is **`DXDTOPF`**, not `DXXTOTPF`. Relevant companion labels include `DXDTOFAT` (total fat mass), `DXDTOTOT` (total lean plus fat), `DXDTOLE` and `DXDTOLI` (lean measures), `DXDTOBMC` (bone mineral content), `DXDSTPF` (subtotal percent fat), subtotal masses and regional fat/lean/percent-fat variables.

Hiding only `DXDTOPF` would leave direct reconstructors or close measurement proxies. A clean enrichment task should withhold the entire DXA measurement family from the builder, including derived percentages and regional/subtotal measurements. Conventional permitted covariates must be explicitly enumerated. Eligibility/validity metadata are handled by the custodian under the fixed population rule; they must not become an informal route to outcome-guided selection.

### Survey design

The DXX_J Analytic Notes instruct use of examination sample weights. That paragraph contains a reused `DXX_G` label, so the cycle-specific demographic documentation should also be recorded. The official [DEMO_J codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm) confirms:

- `WTMEC2YR`: full-sample 2-year MEC examination weight;
- `SDMVSTRA`: masked variance pseudo-stratum;
- `SDMVPSU`: masked variance pseudo-PSU.

An age/validity-restricted target requires an explicit survey-domain and missingness plan. Adding fasting-only covariates can change the eligible sample and weighting requirements; the current DXA recommendation must not be applied automatically to such a combined task. No target completeness assessment or reweighting was performed here.

## Urate metadata boundary

The official [BIOPRO_J documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BIOPRO_J.htm) establishes eligibility at 12 years and above and the aliases `LBXSUA` (mg/dL) and `LBDSUASI` (umol/L). A builder must not receive either alias, derived hyperuricemia flags, or deterministic conversions of the hidden outcome.

Its Analytic Notes describe the 2017–2018 transition to Roche Cobas 6000 and bridging recommendations for some analytes relative to earlier cycles. Analyte-specific bridging coefficients were **not inspected**; the existence of general bridging guidance does not establish that urate needs a particular correction. Cross-study assay compatibility remains a source-admission item. The notes require appropriate NHANES survey variables and warn about missing specimens; fasting glucose and triglyceride reference components have distinct recommendations and should not be casually replaced by broad-panel aliases.

## Incidental public-summary exposure and residual limits

- An initial public search returned official other-cycle codebook snippets containing sample counts/ranges. No patient rows or target association analysis were opened or used. Subsequent codebook extraction removed tables and selected metadata/labels only. Thus an absolute claim of zero exposure to every public summary would be inaccurate.
- The parent investigator reported that a separate broad search incidentally surfaced the title/snippet of a **2025 Frontiers paper about NHANES 2017–2018 body composition and CRP**. It was not opened or used. **Body-fat–CRP must not be advertised as a wholly unseen confirmation relationship.**
- The parallel urate evidence reviewer reported incidental NHANES snippets despite exclusion terms in public searches, and secondary NHANES summaries in a candidate source's discussion. That reviewer reports no deliberate target-paper read, target-value extraction/use or patient-file read. Source packets should screen out these target-derived summaries before a new builder context is instantiated; bibliographic independence alone is insufficient.
- Filenames and bounded code searches cannot resolve prior browser activity, external workspaces, unindexed archives, all earlier conversations or LLM pretraining. Future source-only builder contexts improve operational separation but cannot erase prior model knowledge or investigator exposure.
- Legacy outcome exposures do not disqualify scientific reuse. They change the claim: an explicitly disclosed new-outcome or transport test can remain useful, whereas globally untouched-cohort or unknown-relation claims would be overstated.

## Required next custodian gate

Before acquiring or revealing a new outcome, freeze the endpoint/cycle, permitted target covariates, eligibility/validity domain, hidden aliases and proxy families, source overlap exclusions, and analysis roles. Resolve the source measurement mapping—including DXA BCA compatibility if DXA is chosen—without fitting target relationships. Record any source or analyst exposure already known.

After that gate, the custodian can acquire and quarantine the outcome component, record hashes and column names, construct covariate-only builder inputs, and retain outcome evaluation separately. This report does not authorize changing a target rule in response to favorable observed relationships, nor certify that either candidate is yet ready for a valid real-data pilot. The intended evaluation is whether generated data support reusable scientific analyses, not a framework leaderboard.
