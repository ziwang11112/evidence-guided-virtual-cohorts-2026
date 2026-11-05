# Turkana measured-lipid admission — source/schema only

5 November 2026. Decision: **GO for root review and a prospectively frozen, assumption-dependent developmental task.** This is not a generation release, an identified target joint model, or fresh independent confirmation. Selection was fixed before this review and is supported by existing measured TC/HDL availability, a precise evaluator, and external numerical evidence. No pair-specific target coefficient, reference-result file, participant row, generator, or fitted model was opened or computed in this review. Embedded historical result prose was incidentally displayed as detailed below.

## Exact feasible task

Generate a complete joint table with ordered columns `id, age, sex, bmi, total_cholesterol, hdl_cholesterol`. ID is unique/nonmissing; age is years, BMI kg/m², sex literal F/M, and both generated lipids mmol/L. The existing reviewed analysis mapping multiplies each lipid by 38.67 to mg/dL; other fields are unchanged. The factor changes numerical representation, not assay equivalence. Root must freeze the new row count and execution schedule.

On one common eligible subset, fit unweighted OLS with intercept, age, I(sex=F), and BMI, with M as the reference category. Retain all three endpoints:

1. `K02-HDL-BMI`: five times the BMI coefficient for HDL; mg/dL per 5 kg/m².
2. `K02-TC-BMI`: five times the BMI coefficient for TC; same units.
3. `K02-LIPID-RESIDUAL`: Pearson correlation of the two models' residuals, after age, sex **and BMI**, on the same rows; dimensionless.

Eligibility is age ≥18, recognized sex F/M, finite age/BMI/TC/HDL and strictly positive BMI/TC/HDL. There is no age maximum or added lifestyle, disease, pregnancy, fasting, outlier, LDL/TG, or TC≥HDL exclusion. Unknown nonmissing sex or malformed numeric schema fails the invocation. Empty/degenerate/rank-deficient analyses remain unavailable instead of disappearing. This preserves the existing endpoint definitions; it does not choose desirable signs or effect sizes.

The target methods metadata describes 2018–2019 Turkana/Laikipia recruitment, interview age, BMI from measured weight/height, and immediately measured CardioChek Plus TC/HDL from venous EDTA blood. Fasting, demographic/site/lifestyle composition, and assay transport remain unverified or unspecified. Recorded F/M labels do not independently establish a biological label legend. The task concerns the selected empirical sample, not national or causal inference.

## Existing access and code, without reference-value access

Paths below are controller-only and must not enter constructor inputs.

- Existing file: `work/scaleup_2026-11-01/private_data/22Jul20_for_Dryad_noIDs.txt`. A filesystem metadata check found 87,736 bytes. Its historical schema digest is `7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9`; this review did not rehash or decode it.
- Historical schema metadata: `work/scaleup_2026-11-01/TURKANA_SCHEMA_AUDIT.json`. It records 1,226 deposited rows and 397 jointly available age/sex/BMI/TC/HDL records. These counts are historical metadata, not recalculated here, and are omitted from the constructor packet.
- Raw mapping and NA handling: `work/scaleup_2026-11-01/production_release/evaluation/evaluate_campaign.py`, `MAPPINGS['K02']` and `_canonical_tsv`. It maps the six named raw fields, strips literal blank/NA missing tokens, and expects mg/dL reference lipids.
- Analysis: `work/scaleup_2026-11-01/analysis/k02_analysis.py::analyze_frame` and `analysis/K02_ANALYSIS_SPEC_v0.json`. Internal design is intercept, `(age−50)/10`, I(F), `(BMI−25)/5`.
- Existing reference summary: `work/scaleup_2026-11-01/production_release/evaluation/PUBLISHABLE_AGGREGATES.json`; selector `$.references.K02`, then `$.estimands`. Its existence was checked through directory metadata; values were not opened. This selector is established by the evaluator's writer code. `FULL_EVALUATION.json` is a code output name but was absent from that directory listing; do not invent its presence.
- Generated-unit map: `work/scaleup_2026-11-01/case_k02/unit_mapping/APPROVED_MANIFEST.json`, `INPUT_CONTRACT.json`, `OUTPUT_CONTRACT.json`, implemented by `bridge_units/unit_conversion.py::convert_frame` and evaluator `_map_generated_units`.

Existing slope intervals are HC3 normal sensitivity intervals under unmodeled sampling assumptions. The existing residual-correlation interval is unavailable. Cluster/design information is absent. Reusing the existing summary can support fixed point comparisons and its available uncertainty; any newly proposed reference uncertainty needs its own prespecified, independently reviewed evaluator. No such analysis ran here.

## External evidence disposition

The constructor-safe artifacts contain reported facts and operator definitions, not proposed generator parameters. They are curator extractions requiring root admission and hash binding; no literature-gateway receipt or approval has been fabricated.

**Greiner 2021, reused.** Existing source IDs `greiner_malawi_rural_men`, `greiner_malawi_urban_men`, `greiner_uganda_men`, corresponding three women IDs, and `greiner_pooled_african` are retained. The source provides subgroup geometric summaries, low-HDL percentages, age quantiles, and pooled sex-specific regressions. This review rechecked the original Analysis section and indexed DC2 table. The generic log-transformation statement still does not identify the transform of each regression variable; no raw-scale conversion is admitted. The correction changes author names only. Printed anomalous intervals, rounded intervals and inconsistent table denominators remain flagged. The exact adjusted source models additionally need smoking/alcohol absent from the target schema. [Original published article](https://eprints.whiterose.ac.uk/id/eprint/181857/1/e005222.full.pdf), [DC2 supplement](https://gh.bmj.com/content/bmjgh/suppl/2021/06/08/bmjgh-2021-005222.DC2/bmjgh-2021-005222supp001_data_supplement.pdf).

**Obirikorang 2015, new primary 1/2.** The Ashanti community study supplies six explicitly Spearman correlations for BMI–TC, BMI–HDL and TC–HDL in rural and urban strata. Table orientation was checked in primary XML. Source eligibility, fasting serum assays, geography and unspecified weighting/missing-pair details limit transport. These rank correlations are executable with declared approximations; they do not equal raw OLS slopes or adjusted Pearson residual correlation. [Original article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0129494).

**Agongo 2018, new primary 2/2.** The Navrongo study adds age/BMI and pooled TC/HDL arithmetic means and SDs for ages 40–60. It explicitly log-transforms lipid responses; selected univariate regression rows remain context only because log base/intercept conventions are not explicit, and the target estimands differ. A methods/table male-count discrepancy is retained. The 2019 correction concerns hip/waist entries and a citation; neither is used here. [Original article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206326), [correction](https://pmc.ncbi.nlm.nih.gov/articles/PMC6392312/).

No further primary study was seriously reviewed. Search snippets for other papers were not admitted. Different named locations/years provide no known Turkana overlap but do not constitute an individual-level overlap audit. Repeated strata, statistics and regressions within a paper are not independent evidence replications.

## Computability and assumptions

The current `docs/SOURCE_CHECKS.md` and `cohort_harness/contracts.py` support arithmetic mean, SD, proportion, Pearson, Spearman and explicitly declared OLS operators. Mean/SD and the new Spearman constraints can be checked in declared source scenarios. Source weighting, source composition, missingness and measurement reconstruction are assumptions. Numerical comparability is not exact population reconstruction.

The core does not support geometric means, derived non-HDL views, or transformed-response operators directly. Greiner geometric means require an honestly labelled reviewed descriptive path; they cannot be changed into arithmetic means. Its non-HDL mean requires computing TC−HDL within rows before a positive-domain geometric mean. Age-quantile convention is unknown. Greiner regression scale and Agongo log base remain unresolved. Keep these operators unavailable or expressly assumption-defined; do not silently substitute an available statistic.

The constructor must name assumptions for covariate composition, age/sex adjustment, residual spread/dependence, distributional tails, source exclusions, fasting/assays, and transfer to the target. A missing conditional relation is neither zero nor a release blocker. No source identifies the exact three target endpoints, and no scenario probabilities or uncertainty calibration are established. These limits support a transparent developmental test rather than a NO-GO based on incomplete identification.

## Exposure and actual activity

Turkana was historically evaluated and is already exposed development. New authors, outcomes, seeds or a new folder cannot restore independent-confirmation status. Turkana papers and target-derived numerical results are excluded from external construction evidence.

The admission reviewer opened the exposure registry as instructed. It mixed exposure metadata with embedded historical pass-count/direction prose, which was incidentally displayed and reported promptly to root. The old admission note also embeds prior-study exposure notices. No pair-specific target coefficient, reference-result file or participant row was opened. Thus this reviewer is not wholly outcome-blind; the constructor packet excludes these notes, all target-size information, and historical results. This limitation should remain in the controller record.

Actual work comprised metadata/code reads, source-only primary retrieval/extraction, file-existence checks and original documentation writes. There was no cohort download, target decoding, generation, fit, scientific test, candidate freeze, execution, git sync, or edit to old frozen files. Two source XML calls outlasted the first shell output window; their final correction output was not captured, so the correction was re-read successfully. No newly started Python process remained at the final process-metadata check. Exact source-access attempts and budgets are recorded in `LIPID_SOURCE_ACCESS_LOG.json`.

## Deliverables and root next action

Constructor-safe: `LIPID_CONSTRUCTOR_TASK_METADATA.json` and the three files under `sources/`. Controller-only: this admission report and `LIPID_SOURCE_ACCESS_LOG.json`.

Root should review and admit the curator artifacts, fix the new task row count/schedule and source-check policy, and hash-bind the exact reference selector before construction. Do not expose this controller note or old reference files to authors. This recommendation leaves all scientific law and parameter choices to the constructor and all current-task release decisions to root.
