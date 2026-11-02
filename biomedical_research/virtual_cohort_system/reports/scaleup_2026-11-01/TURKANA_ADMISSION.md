# First scale-up candidate: Turkana

1 November 2026 (America/Chicago). Decision: **retain for evidence/measurement qualification; not scientifically admitted and no generation released**. Intended fit is the K02 measured-lipid case. The original 144-slot plan remains disabled and unassigned.

## What was actually acquired and inspected

The official [Dryad release](https://datadryad.org/dataset/doi:10.5061/dryad.2z34tmpjk), published 24 September 2020, supplies `22Jul20_for_Dryad_noIDs.txt` under CC0. The local file contains 87,736 bytes, SHA256 `7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9`. Chrome's download-event watcher timed out, but the exact requested file was found in Downloads and verified before making a project-local copy. No duplicate network download was initiated to repair that event.

The bounded [schema audit](TURKANA_SCHEMA_AUDIT.json) processed identifiers and missing-value flags without emitting clinical values, ranges, means, covariances or regression results. There are **1,226 rows and 1,226 distinct identifiers**, with no missing/duplicate IDs. Fourteen columns include one identifier; the thirteen substantive fields are not thirteen independently measured biomarkers. The five fields age, sex, BMI, total cholesterol and HDL are jointly nonmissing in **397 rows**. This is an availability count, not a finalized analysis population. The reported cohort size cannot be substituted for the effective lipid-analysis sample size.

The downloaded file includes 825 missing total-cholesterol values and 820 missing HDL values. Availability is therefore a material sampling question. No missingness mechanism or national representativeness is inferred from those counts. The root and an independent reviewer inspected the primary study's [sampling/filtering methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/#sec11) and relevant [supplementary methods](https://pmc.ncbi.nlm.nih.gov/articles/instance/7577730/bin/abb1430_SM.pdf), rather than relying on repository variable labels alone.

## Measurement decisions that affect the scientific task

| Item | Verified method / limitation | Consequence |
|---|---|---|
| Target recruitment | Healthy consenting adults of self-reported Turkana ancestry in Turkana and Laikipia counties; April 2018 to March 2019 | Define this study's released analytical subset; do not claim a representative Kenyan population. |
| TC and HDL | Venous EDTA blood; CardioChek Plus lipid panel | Plausible directly measured lipid endpoints; external assay/population transfer still needs a declared assumption or support. |
| LDL | Calculated by the device using the Friedewald relation | Exclude as an independent measured validation endpoint. Reproducing the identity is not recovering new biology. |
| TG | CardioChek could not read values below 50 mg/dL; low TG and corresponding LDL were not recorded | Exclude an unrestricted TG-distribution or continuous-population analysis. NA does not identify which values were censored versus otherwise missing. |
| Glucose | Capillary whole-blood OneTouch measurement | Not automatically interchangeable with central-laboratory fasting plasma glucose. No verified fasting instruction was located in the inspected measurement passages. |
| BMI / waist / fat | BMI from weight/height; waist averaged across three measurements; body fat by bioelectrical impedance | These are different measurement constructs; body fat must not be treated as DXA. |
| Sampling dependence | No site/household/cluster or survey-weight field in the released header | Cannot reproduce cluster inference by using lifestyle category as a fabricated cluster ID. Any uncertainty claim must explicitly address the unavailable dependence information. |

Supplement pp.5–6 establish that the repository's loose LDL label, "measured from blood", does not mean a separate direct LDL assay. These methods change which endpoints are valid, without looking at whether our generator would succeed.

## Current scientific route, without fixing favorable answers

Continue screening **joint generation of age, sex, BMI, measured TC and HDL**, optionally a scientifically necessary sixth variable, using independent external study evidence. Examine whether an external packet can constrain two quantitatively useful conditional relationships and one additional prespecified analysis using the same table. Exact operators, adjustment sets, clinical tolerances and all-five-constructor aggregation are unresolved; no expected sign, slope, mean or target SD is supplied here.

This is a cross-sectional, measured-protocol use case. It is not a causal intervention, individual measurement reconstruction or demonstrated national-population simulator. External studies must support applicable relationships and variability, not only marginal means. If sufficient evidence cannot be admitted within the campaign budget, or the promised analytical population/inference cannot be defined, reject this candidate for the intended confirmatory role. Do not switch to an easier endpoint after revealing target coefficients.

## Exposure and independence boundary

Historical checks found an earlier repository landing-page lead, not a completed local target evaluation. This turn was **not globally outcome-blind**: the article title, abstract and results headings exposed broad urban/rural, diet and early-life conclusions. Supplement p.6 embedded sensitivity-result statements alongside measurement methods: no lifestyle effect on LDL (p > .05) and TG lifestyle-contrast p-values .00166 and .000475. A visible p.7 fragment described generic age/sex-residualized biomarker correlation strength and the proportion of pairs not correlated. A filtering paragraph also stated a birth-location-missingness comparison. No pair-specific TC/HDL/BMI/age coefficient or raw clinical value was calculated or extracted.

Record these as prior knowledge; do not silently relabel the entire study unexposed. The Turkana paper and these result-bearing materials are **excluded from external construction evidence**. The exposed lifestyle/early-life conclusions, LDL/TG contrasts and generic correlation summary cannot count as new withheld validation. A later independent admission review must determine whether explicitly scoped analyses remain unaffected enough for the campaign's independence claim; this note does not certify that. Fresh builders receive only the approved source/task packet, not this exposure/result note or the target file.

## Cost, failure and next step

This unit consumed **one of six new candidate-family slots**. The one original target study was seriously inspected for methods and conservatively consumes **one of twelve new-original-study slots**; independent rereading is not another study. No external generation source has yet been admitted. Two locally saved responses total **89,553 bytes**: the data file plus an invalid 1,817-byte HTML response saved with a PDF filename. The latter was identified by its HTML signature and retained privately as a failed acquisition; it is not cited as a successfully downloaded PDF. The actual supplementary PDF was viewed in Chrome. Total inherited plus newly measured saved-download bytes are **232,810,156**, leaving **291,477,844** of the 500 MiB ceiling. Browser traffic remains unmetered.

Next discriminating work: identify applicable independent conditional lipid evidence and spread information; resolve the released-subset and inference definition; then decide admit/reject. Parallel work can check the next family's access and measurements. Do not launch constructors merely because an accessible file exists. This candidate currently contributes **zero admitted cohorts, zero generated tables and zero target-effect evaluations** to the scale-up campaign.

Independent method assessment: [review](TURKANA_METHOD_REVIEW.md). Historical aliases: [history screen](HISTORY_SCREEN.md). Raw rows and third-party documents remain local.

## External-source follow-up within the same foreground checkpoint

One additional original was then seriously reviewed: [Greiner et al. 2021](https://gh.bmj.com/content/6/5/e005222), including its latest linked supplement and name correction. **The cumulative new-phase count is now 2/12 originals and 1/6 target families.** This is one source article containing several population analyses, not several new target cases. No source participant files or new local PDF assets were acquired.

The source provides sex-specific HDL–BMI and HDL–non-HDL estimates and distributional summaries from Uganda/Malawi, alongside UK comparisons. Thus relevant external joint information exists. However, the precise raw/log regression mapping remains unresolved; adjusted rows include unavailable smoking/alcohol variables; and laboratory/eligibility differences from Turkana remain. Geometric-mean confidence intervals cannot directly supply person-level variation. The [independent operator review](GREINER_SOURCE_OPERATOR_REVIEW.md) admits reported evidence while marking exact numerical calibration unavailable and transfer scenarios provisional. No executable evidence packet, construction parameter or generation release was produced.
