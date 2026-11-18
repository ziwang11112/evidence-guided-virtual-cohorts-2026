# Fixed-analysis reuse on existing virtual cohorts

11 November 2026. New descriptive analysis unit following the user's request to keep a published analysis fixed and replace its data. No new Agent construction, model revision, download, API payment, or method comparison is authorized by this unit.

## Selected task and scope

Reuse Lea et al. (2020), DOI 10.1126/sciadv.abb1430, supplementary Methods, PDF page 7, "Correlations between measures": regress biomarker values on age and sex and calculate Pearson correlations of residuals. The original study has ten biomarkers. Our available output schema supports exactly three unordered pairs: BMI–TC, BMI–HDL, TC–HDL. All three are mandatory; neither their reference values nor this unit's results select the pairs.

This is a Methods-guided partial reanalysis, not unchanged author code, the full original matrix, a lifestyle/mediation replication or an independent new target. The original implementation was not located. Exact original missingness/outlier rules cannot be reconstructed. HRS remains an alternative source-model reconstruction example; it lacks real participant inputs here and is not this unit's real-versus-virtual comparison.

## Fixed data inputs

1. Existing processed public Turkana file `work/scaleup_2026-11-01/private_data/22Jul20_for_Dryad_noIDs.txt`, SHA256 `7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9`.
2. All six initial lipid constructors from `work/request_only_repeatability_2026-11-11/FINAL_TABLES.json`, each with seeds 54001, 54003, 54007: 18 previously generated tables. Retain every constructor in original policy/repeat order.
3. The already completed R04_GENERIC and R04_STRUCTURED corrections from `work/scientific_check_revision_2026-11-11/FINAL_TABLES.json`, three seeds each: six dependent tables, separately labelled, never replacing the original LIPID_BASE_R2. They repair its mathematical tail defect, not a new independent construct or a target-selected winner. Other retained-output reviews duplicate original tables and are not new inputs.

Bind all file hashes and selection manifests before decoding rows. Check those hashes again after calculation. Do not import or execute generators, old launchers or API code. Read only these 25 input tables. Individual rows and IDs must never be saved in new report artifacts. Original real/generated files remain local and immutable. Previously exposed data remain developmental. These three new comparisons are retrospective analyses of frozen outputs, not claims of fully unknown relationships.

## Identical analysis operator

- Canonical columns: age (years), sex (literal F/M), BMI (kg/m²), TC and HDL (mg/dL). Public real file uses tab-separated UTF-8-sig and original field names. Generated CSVs use the registered six-column schema with lipids in mmol/L; multiply both by the existing 38.67 conversion. No values are inferred from target statistics.
- Complete-case rules apply identically after canonicalization: all five variables available, finite numeric entries, recognized F/M, strictly positive BMI/TC/HDL, and **age >18** following the original study's stated recruitment rule. Do not assert n=397 before execution; the old project used age >=18.
- Missing tokens: empty/whitespace or exact NA. Unexpected nonnumeric or sex tokens fail the table; do not silently coerce. No additional upper-age cutoff, trimming, winsorization, imputation or exclusion of HDL>TC. Record exclusions and schema errors, without patient values.
- One common complete-case subset is an investigator-resolved choice for the three-variable matrix. Original pregnancy, interview and unspecified extreme-outlier exclusions cannot be reimplemented from the public schema. The file is a processed deposit, not original raw measurement data.
- Center and scale each of the three outcomes by its own sample SD. Fit OLS with an intercept, continuous age and I(sex=F); use numerical least squares. Compute signed Pearson r and r² for each pair of residual vectors. Include neither lifestyle nor BMI as an additional nuisance regressor. Full-rank design and nonzero residual variance are required; otherwise record unavailable results without replacing tables or pairs.
- There is one canonical function shared by real and generated data; only the schema/unit adapter differs. This unit estimates neither slope nor mediation, and performs no FDR or significance claim. Correlation is not causation.

## Reporting and interpretation fixed before this analysis

Publish all 3 real point estimates, all 54 initial synthetic seed estimates and all 18 dependent-correction seed estimates (75 total planned estimates), their r², row/exclusion counts and input lineage. Summarize each constructor with its three individual estimates, mean and range. Ranges are generated-draw variation, not population confidence intervals. Do not pool all virtual people or treat seeds as independent clinical samples.

Display real and virtual results in a shared three-panel plot and matching correlation matrices, with the same [-1,1] colour scale. Report signed and absolute differences as descriptive quantities, without inventing a clinical success cutoff or a universal quality score. Real and generated sample sizes differ (generated releases have 3000 rows before filters); no inference that more virtual rows increase clinical evidence. No new bootstrap, nominal population interval or p-value is needed for this bounded descriptive reuse.

Explain the retained and altered relationships in the context of this specific analysis. The reference is one selected real sample, not known population truth. Preserve differences rather than adjusting frozen laws. Later repaired candidates are a labelled sensitivity appendix. No raw or generated individual records, third-party papers, prompts or credentials are distributed by the report.

## Release and stop

Before table decoding: independent source/schema and implementation review; meaningful invented-data operator checks; freeze protocol, code and input hashes. Then execute this one fixed batch, independently recompute all three correlations on each admitted file, and verify immutable inputs. Technical errors must be recorded and reviewed before any correction; no outcome-driven changes. Close after the full result/figure/report with a use-specific decision. Do not automatically request new sources, new variables, another model or another generation batch.
