# C01 independent source and proposal review

2026-11-04. **Decision: PASS_TO_IMPLEMENT.** No concrete transcription, unit, covariance-algebra or finite-moment defect requiring a new scientific proposal was found. This releases candidate implementation under the existing budget; it does not release a freeze or execution and does not certify target fidelity. The author's substantial selection/transport assumptions remain assumptions, not new source findings.

## Scope and integrity

Read C01's task/request metadata, source request, proposed construction and search ledger, and the four admitted original XML articles with focused methods/results/table extraction. Read the evidence-cohort-generation skill and its interface guidance. Verified all 16 registered artifacts against registry hashes, with zero mismatches; the four originals are PMC5591004.1, PMC2871988.2, PMC2551641.1 and PMC6458679.1. Gateway state confirms six query credits and four downloads; the read ceiling is exhausted. Selected source populations are Changfeng, Shanghai Diabetes Study II, FOS/NHANES and Maamu/Health 2011, not CHNS or ENSANUT. An alias scan of the admitted originals also found no excluded-cohort mention. This is a source-identity check, not proof against every possible unreported participant overlap.

No new literature was obtained, no target result or individual data was read, and no candidate code or rows were generated/executed. The reviewer independently calculated only constants and finite collections of model covariance matrices; the author's retained calculation script was not executed. The reviewer has prior historical project-result exposure and is not the scientific author; this review supplies no target-directed parameter or requested sign.

## Original evidence checked

| Source and locator | Finding |
|---|---|
| Wu, Table `pone.0184607.t001`, methods | The cited total and age-stratum means/SDs/counts match the original. The footnote identifies individual SDs. The 4,325-person no-known-diabetes population, sequential exclusions, age >=45, at least ten-hour fast, plasma-glucose assay and HbA1c HPLC are represented correctly. Total summaries include the >=75 group. |
| Bao, Methods/Results, tables `tbl1` and `tbl5` | The 4,886 participants, 360 excluded known-diabetes cases, Pearson glucose–HbA1c correlation 0.619, and distinction from the two-hour correlation 0.622 are correct. Table 5 OGTT-detected subgroup BMI 25.5 (SD 3.7), glucose median 7.2 (IQR 6.2–8.1), and HbA1c median 6.5 (IQR 5.9–7.1) match. The known-diabetes mixing weight is a derived selection-count proxy, not a reported prevalence. |
| Pani, multivariable Results and Table `t1` | Main-text adjusted age estimates 0.012/year for FOS and 0.010/year for NHANES are correctly separated from abstract unadjusted values and from differing adjustment/selection sets. Table entries are mean +/- SE. Declining to reinterpret the anomalous prose dispersions as individual SDs is appropriate. |
| Skogberg, methods and Table `Tab3` | The eight baseline/full-model R-squared pairs match the article. Their partial-R-squared derivation is valid under the stated common-sample least-squares interpretation and conveys magnitude only. Age is binary in this source, with survey weighting and extra fasting-time adjustment for glucose; C01 already records those restrictions. No numeric slope or sign is recovered from an unadmitted figure. |

The two Shanghai studies are distinct named studies but individual overlap is not established. No independent-evidence precision gain is claimed. FOS subgroups and alternative Bao diagnostic definitions remain overlapping. The sources' diagnostic AUC regressions, medians, correlations, adjusted slopes, SDs and SEs have not been interchanged.

## Independent model arithmetic

Recalculation reproduced the proposed female probability 0.5789595376, selection-count mixing weight 0.0686237133, age variance 133.25 and three ecological secants. The total-covariance equation yields conditional glucose–HbA1c correlation 0.6122036085; its stated 0.619 marginal implication applies to the constructed background component under its chosen age law, not the full mixture or the actual source population.

The arithmetic-moment to multivariate-lognormal transformation is correct. Across all forty allowed background ages, minimum latent correlation determinant is 0.5938491782 and minimum log-covariance eigenvalue is 0.0063834099. The second component has determinant 0.5944085378 and minimum eigenvalue 0.0094252516. Thus the proposed covariance matrices are positive definite rather than merely pairwise admissible.

The IQR-ratio log-SDs reproduce 0.1981607352 and 0.1372462911. Derived glucose mean/SD are 7.34276052/1.46944845 and HbA1c mean/SD 6.56150796/0.90480010. The implied quartiles differ from the supplied quartiles exactly as the proposal acknowledges. Finite mixtures over finite ages of these positive-definite multivariate lognormal laws have finite polynomial moments. Independent, nondegenerate sex and age plus positive continuous conditional variance support the stated population full-rank argument. These facts do not guarantee finite-sample numerical rank or acceptable realized tails; those await actual output checks.

## Required meaning to preserve in implementation

- Keep all ecological-to-individual-age mappings, age extrapolation, total-to-conditional SD use, sex/age independence, zero conditional sex effects and assumed BMI dependencies explicitly tagged as assumptions. The R-squared evidence does not identify the proposed signs or the chosen Chinese conditional correlations.
- Keep the known/treated-diabetes component explicitly a surrogate scenario based on newly OGTT-detected cases. Neither its distribution nor its weight is established for previously known diabetes in the target. This is a major applicability limitation, but not a transcription or mathematical defect that requires replacing the author's chosen law.
- Do not mark the background-only correlation constraint or latent-component statistics as exactly checked on all delivered rows: the unobserved mixture label is not an output field and the mixture changes those statistics. A supported all-row operator may be labeled an approximate target/source comparison with its population mismatch; otherwise retain an unavailable check. No source-population replay is established.
- Keep reported source quantities, derived lognormal parameters and author assumptions distinct in the machine-readable evidence/specification. Unsupported weighted, conditional, transformed or latent-subgroup source operators must not be relabeled to fit an available operator.

These are implementation/provenance requirements preserving the submitted proposal, not requests for additional sources, parameters, desired outcomes or model optimization. No further retrieval is warranted under the exhausted original-study allowance.

## Reviewed proposal identities

- `SOURCE_REVIEW_REQUEST.md`: `f99dcacda02264b74445698750fda44cdc8256ca2701c8d7cae7f269a4f62479`
- `PROPOSED_CONSTRUCTION.md`: `7e075d07008ae519534cbd648541e480392ecd1015a8f1467c896ae00f420cd5`
- `SEARCH_LEDGER.json`: `2e251df696e4d54f698bd18b1b29e227f9e0bfc981e6f2788a68c847a30e6c06`
- Task/request hashes match the protocol's C01 bindings. Original XML identities are the hash-named admitted paths recorded in the reviewed source request and registry.
