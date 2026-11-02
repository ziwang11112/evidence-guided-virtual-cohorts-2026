# K01 external glucose evidence: bounded original-source review

2 November 2026. **Source review only; no source item is approved or activated by this document.** Two original-study slots are conservatively consumed: Ayele 2020 was read in full rendered HTML; Bahendeka 2016 was seriously assessed but only its publisher abstract was accessible. No third original was opened. No patient dataset, HAALSI result paper, target clinical value, fit, sample, generator or target-effect analysis was used. This unit changes no STATE, registry, frozen packet or export.

The useful result is a source-native age/sex/BMI margin set and six categorical diabetes odds ratios from an independent Ethiopian community study, plus a more limited weighted fasting-capillary survey abstract from Uganda. **Neither verified source supplies continuous glucose mean/SD, an adjusted continuous glucose–BMI or glucose–age coefficient, or sex-specific BMI slopes.** Binary diabetes odds ratios do not determine any of the three proposed continuous-glucose projections. Missing joint laws remain possible, explicitly declared Agent assumptions; they are not evidence for zero slopes, zero interaction or conditional independence.

## Search and intake boundary

Search used only wang Chrome extension in agent-created tabs. The first query was `capillary glucose BMI age sex population Uganda Accu-Chek -HAALSI -Agincourt -AWI-Gen`. A short metadata shortlist preceded original reading. Exact-title lookups resolved identity/access for Kasujja, Arman and Bahendeka; no search result or generated search overview was admitted as numerical evidence.

| Lead | Selection decision and reading status |
|---|---|
| Ayele et al. 2020, DOI [10.1177/2050312120975235](https://doi.org/10.1177/2050312120975235) | Selected for community recruitment and capillary measurement. PMC's initial tab creation unexpectedly emitted the full article tree while citation metadata was being checked; the root was immediately notified and the slot counted. Thus the intended prior notice preceded further extraction, but not that automatic full-tree exposure. |
| Bahendeka et al. 2016, DOI [10.1111/tmi.12663](https://doi.org/10.1111/tmi.12663) | Identified in Ayele's references, then shortlisted from PubMed/Wiley search metadata. Title and DOI sent to root before opening. Selected for national community recruitment and explicit fasting capillary measurement. Abstract-only access; conservatively consumes the second slot. |
| Kasujja et al. 2022, DOI 10.1371/journal.pone.0272515 | Search/citation metadata only: diagnostic accuracy among outpatients in Uganda. More selected population than the national survey; not opened or used. |
| Arman et al. 2025, DOI 10.1371/journal.pgph.0004828 | Search/citation metadata only: random-glucose screening in professional drivers in northeastern Bangladesh. Occupational and geographic selection; not opened or used. |
| Mayega 2018, PMC6307025; Kibirige 2014, PMC3974012 | Initial search snippets concerned newly diagnosed diabetes or clinical diabetes patients. Not opened; not suitable as unrestricted community margins on that metadata alone. |

This is a bounded shortlist, not a systematic review or a claim that stronger sources do not exist. Incidental non-target source snippets and titles were exposed. No HAALSI/Agincourt or AWI-Gen results were selected as generation evidence.

## Ayele 2020: source-native candidate evidence

Original: *Prevalent, uncontrolled, and undiagnosed diabetes mellitus among urban adults in Dire Dawa, Eastern Ethiopia: A population-based cross-sectional study*, SAGE Open Medicine 8, 2050312120975235. Inspected version: [PMC rendered original](https://pmc.ncbi.nlm.nih.gov/articles/PMC7686592/) on 2 November 2026. Relevant population, measurement, analysis and table excerpts are retained privately in `../private_sources/AYELE_2020_BROWSER_EXCERPTS.txt`; they are selected DOM transcriptions with whitespace normalization, not a publisher PDF or independent reopening.

The expanded original copyright notice identifies © The Author(s) 2020 and [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). The private excerpts retain the article title, DOI and source URL; omissions and whitespace normalization are declared. The excerpts are for this noncommercial research audit and are not on the public allowlist.

The recruitment frame was Dire Dawa urban households in June 2017: residents for at least six months, methods age 25–64, multistage selection of five of nine urban subdistricts, systematic household selection and a lottery when several adults were eligible. Pregnant people, people described as physically/mentally disabled and nonconsenters were excluded. Those exclusions are source selection, not proposed target exclusions. Methods identify 872 valid observations from a planned 903; results state 822 complete responses. MICE handled missingness in five variables, with age and BMI marked as imputed. The paper does not document a usable survey-weight formula or cluster-adjusted inference in the inspected analysis text; do not assume equal weights or population-calibrated precision merely because sampling was multistage. See [population section](https://pmc.ncbi.nlm.nih.gov/articles/PMC7686592/#section8-2050312120975235) and [analysis section](https://pmc.ncbi.nlm.nih.gov/articles/PMC7686592/#section12-2050312120975235).

Glucose used capillary blood and an Accu-Chek digital glucometer, material number 06453970018, batch/lot 496915. An exact commercial model name and plasma-equivalence calibration were not established. Time since the last meal was asked, and three measurements on consecutive days were averaged. The paper mixes fasting and random diagnostic criteria, reporting FBG ≥126 mg/dL or RBG >200 mg/dL; current diabetes medication also identifies previously diagnosed diabetes. It does not give a reproducible fasting-hours boundary, fasting/random mixture, or a rule for mixed states across the three visits. This is not the same operator as one pooled cleaned HAALSI POC measurement. BMI is measured weight divided by squared height, kg/m². See [measurement section](https://pmc.ncbi.nlm.nih.gov/articles/PMC7686592/#section10-2050312120975235).

| Directly printed candidate summary | Value | Operator / uncertainty / locator |
|---|---|---|
| Age | Mean 40.4 years; SD 13.0 years | Marginal arithmetic mean and participant SD, not CI or residual SD. Age is imputed; exact mean column placement is not separated in the table. [Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC7686592/#table1-2050312120975235). |
| Sex | Male 286 (32.8%); female 586 (67.2%) | Sample counts/printed percentages, n=872; not target composition. Table 1. |
| Age categories | 25–34: 371 (42.6%); 35–44: 187 (21.4%); 45–54: 121 (13.9%); 55–64: 193 (22.1%) | Imputed-data column, n=872. Complete-case age counts differ. Table 1. |
| BMI categories | <18.5: 65 (7.5%); 18.5–24.9: 467 (53.5%); ≥25: 340 (39.0%) | Total sample column, n=872, BMI imputed; preserve printed cut labels/rounding. No continuous BMI mean/SD recovered. [Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC7686592/#table2-2050312120975235). |

The six adjusted ORs below are **composite-DM logistic associations**, not continuous glucose slopes. Use the imputed analysis column consistently; complete-case alternatives are retained in the private excerpt rather than mixed into one constraint. Adjustment-variable headings are sex, age group, education, marital status, current smoking, vegetable consumption, physical activity, BMI category and hypertension. The reported inclusion screen is bivariable p<0.25. Exact model design/coding and the repeated-state diabetes operator are not fully reconstructible, so these remain contextual, not executable constraints for a four-variable task. [Table 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC7686592/#table4-2050312120975235).

| Contrast | Adjusted OR | Reported 95% CI |
|---|---:|---|
| Male vs female | 1.1 | 0.7–1.6 |
| Age 35–44 vs 25–34 | 1.2 | 0.7–2.1 |
| Age 45–54 vs 25–34 | 1.5 | 0.8–2.8 |
| Age 55–64 vs 25–34 | 2.1 | 1.2–3.6 |
| Underweight vs normal BMI | 0.8 | 0.3–1.8 |
| Overweight (≥25) vs normal BMI | 1.6 | 1.1–2.1 |

These CIs are uncertainty about OR estimates; they are not subject-level glucose dispersion. Taking logarithms would change the OR scale, not identify a glucose regression coefficient. No log-OR conversion or reconstruction was performed.

Source inconsistencies are preserved: methods age 25–64 versus Tables 1/2 captions 25–65; prose inclusion cutoff printed as p≥2.5 in the results versus p<0.25 in methods; physical-activity labels overlap at 600 in Table 4. Table 3 gives uncontrolled-DM counts 12/26 treated males and 11/50 treated females, while adjacent prose says uncontrolled DM is higher among females. This latter direction claim is not used. Table 3 percentages condition on DM/control columns, not the whole cohort. Do not silently repair these issues or use their ambiguity to infer a target rule.

## Bahendeka 2016: abstract-only evidence, restricted disposition

Original: *Prevalence and correlates of diabetes mellitus in Uganda: a population-based national survey*, Tropical Medicine & International Health 21(3):405–416. Inspected official [Wiley abstract](https://onlinelibrary.wiley.com/doi/10.1111/tmi.12663) and [Ovid abstract](https://www.ovid.com/journals/tmih/abstract/10.1111/tmi.12663~prevalence-and-correlates-of-diabetes-mellitus-in-uganda-a), both the same original. The survey was national Uganda, April–July 2014, ages 18–69, n=3689, multistage stratified sampling and explicitly weighted survey analysis. Fasting capillary glucose is explicit, but the accessible abstract does not verify device/model, hours, numeric glucose units/cutoffs, medication inclusion, exclusions, exact adjustment coding or table estimates.

The abstract directly prints male age mean/SD 35.1/12.6 years and female 35.8/13.2 years; 1467 males. It reports IFG 2.0% (95% CI 1.5–2.5) and diabetes 1.4% (0.9–1.9). Sex-specific IFG is male 2.1% (1.3–2.9), female 1.9% (1.3–2.6); diabetes male 1.6% (0.8–2.6), female 1.1% (0.6–1.7). These are **abstract-verified values only**. No numeric BMI effect, continuous glucose scale/dispersion or table-level operator was verified. The percentages cannot become equal-weight or simple threshold constraints from the accessible information. Qualitative associated-factor lists are not numerical coefficients.

Wiley/Ovid full text required access. An already observed public Uganda National Research Repository link timed out without rendering content; no assertion about its content is made. Abstract evidence remains unapproved and no exact table locator is invented.

## Independence, transport and next-use limits

The stated recruitment frames—Dire Dawa households in Ethiopia and a national Ugandan survey—are geographically distinct from the HAALSI baseline Agincourt, South Africa frame. No HAALSI/Agincourt reuse is described in the inspected Ayele methods or Bahendeka abstract. This is recruitment-provenance support for independence, not an individual-identifier linkage proof. Neither selected source is presented as an AWI-Gen analysis; Bahendeka's full recruitment protocol was unavailable, so its complete overlap assessment remains limited. Any later discovery of AWI-Gen incorporation would require excluding the affected estimate. Do not pool unverified overlapping source estimates.

Ayele's three-day capillary average, unknown fasting mixture, source imputation and selection are substantive differences from pooled released cleaned POC glucose; Uganda's fasting weighted survey is another different context. A mg/dL-to-mmol/L unit transformation, if separately reviewed later, would not resolve device, specimen calibration, feeding, averaging, selection or weighting. No conversion factor, target demographic composition, clinical parameter or target effect has been prescribed here.

Candidate evidence objects are in `CANDIDATE_EVIDENCE.json`. The age/sex/BMI margins can inform a source-specific assumption-labelled model after review; the diabetes ORs and abstract prevalence items are contextual under the current four-variable request. All three proposed continuous-glucose uses are **joint-assumption dependent relative to these verified inputs**, rather than directly reported or algebraically implied. The finite source packet does not identify a complete glucose-generating law. This is a scientific information limitation, not an automatic demand for complete identification or automatic case rejection. Root may separately assess the previously audited, more distant fasting-serum MIND source; this unit did not reread it or treat serum as capillary.

## Acquisition and capture accounting

No valid original PDF was acquired. The Ayele ordinary browser download attempt left `C:/Users/ziwan/Downloads/10.1177_2050312120975235.pdf`, 1,817 bytes, SHA-256 `336edf8d6baafbe3d4cc3a1a8487e18dfa4ddfc01533ec7272426348baccf0a6`; its bytes are HTML titled `Preparing to download ...`, not PDF. A copy is retained privately as `AYELE_2020_DOWNLOAD_INTERSTITIAL.html`. The root was notified for acquisition accounting. No observed repository saved filename was returned, so no additional saved original is verified. No CAPTCHA, paywall or browser warning was bypassed. Local DOM excerpts are separately labelled browser captures; unmetered browser traffic is not represented as zero network usage. The excerpts and failed response stay private; public artifacts contain original review, short factual tables and provenance only.
