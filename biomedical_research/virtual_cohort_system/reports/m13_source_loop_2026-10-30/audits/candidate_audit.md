# M13 independent pre-execution candidate audit

Status: **Both candidates passed the pre-execution audit and subsequent independent source-output arithmetic checks. Build02's original source-context contradiction was corrected and independently rechecked before execution.** These conclusions establish implementation/report consistency, not source-population accuracy or target validity. Both source fits retain nonzero discrepancies.

## Scope and boundary

Read the two admitted initial candidates, their task/registry/controller contracts, screened Thai/Gallagher JSON evidence and relevant harness interfaces. Read candidate preparation scripts as text. Independently inspected both candidates' covariate CSVs and JSON metadata with ordinary CSV/JSON/numerical operations. Parsed generator syntax without importing or executing either generator. Did not read target observations or target outcomes. After the parent explicitly authorized post-run review, the permitted reads expanded to both candidates' retained source-generated outputs and their reports. No candidate or calibration artifact was changed. Audit outputs are this file and `postrun_audit.json`.

The two submissions are treated as equally legitimate independent scientific constructions. Shared source equations and a similar bounded conditional family do not invalidate independence. No source-fit or target-performance ranking is made.

## Material finding

**Build02 original Thai covariate shape contradicts the reported full-cohort BMI>=25 count.** In `build02/candidates/initial/reconstruction_diagnostics.json`, original development men have BMI>=25 fraction 0.17372448979591837 at 3920 integration rows, and development women have fraction 0.441 at 5000 rows. With the declared 40-fold integration factor these imply `(681 + 2205)/40 = 72.15` development participants with BMI>=25. The full Thai cohort has n=436 and reports 15%, approximately 65.4 participants. Even allowing ordinary rounding to an integer percentage, 15% admits at most 67 of 436 participants. A development subset cannot contain more such cases than the whole cohort. The minimum whole-cohort prevalence implied by the original development reconstruction alone is 72.15/436 = 16.548%, before any validation participants are counted.

The problem is in the single-beta reconstruction, not the generator equation or outcome noise. The original `model_spec.json` assumption `A_source_shape` and `decision.md` distinguish full-cohort prevalence from a subgroup target, but that does not remove the subset bound. The original BMI>=30 count is zero and correctly respects the reported absence. Required repair: choose and explicitly document a different covariate-shape scenario compatible with the admitted margins and the whole-cohort subset constraint, update source inputs/diagnostics/recipe hashes and linked artifacts, then repeat covariate-only validation. This does not require forcing every subgroup to exactly 15%, altering the conditional model, adding an outcome constraint, or inspecting target information.

Parent was notified before execution and requested the builder's pre-freeze repair. The original candidate was preserved by its builder under `build02/agent_exchange/preflight_archive_v1/initial`. The correction and its independent re-audit are recorded next.

## Build02 correction and independent clearance

The repaired candidate replaces only the Thai BMI marginal reconstruction with an explicitly assumed threshold-stratified mixture; it preserves the generator, conditional equations, numerical calibration whitelist and all 18 checks. Independent inspection verifies 400/3920 male and 920/5000 female integration rows with BMI>=25, corresponding to 10+23=33 development participants under the declared replication factor 40. None has BMI>=30. The corrected development fraction is 33/223=14.7982%, and BMI lies in 14.05000049–29.93453397. Recomputed male BMI mean/sample SD are 22.300000000000004/2.6999999999999997; female values are 23.8/4.0. Age quantile-grid approximations remain explicitly recorded.

The assumed allocation of a further 9 male and 23 female validation cases yields a compatible total 65/436=14.9083%, rounding to 15%. This allocation is a feasibility example, not a reconstructed fact or outcome fitting target. Independently recomputed lower-component validation mean/variance values are 21.597297/3.969993 (men) and 23.289720/14.389801 (women), below the corresponding bounded-support variance ceilings 25.851344 and 15.888025 on [14,25]. Thus the remaining validation BMI moments do not make this assumed allocation impossible. No validation rows or outcomes were generated.

All 15 files listed in `build02/agent_exchange/preflight_corrected_hashes.json` matched their hashes. The manifest SHA256 is `79061dcf993d2f76ed5e6401ecdc2adbe58678c1accfa199d98f977dd70bda38`. Source recipe hashes, linked check-artifact hashes and admitted registry hashes also matched. Both CSV schemas contain only permitted covariates and unique IDs; all five derived columns have zero recomputed error. Thai/Gallagher OLS design ranks remain 4/8. Every one of the 18 evidence values, original predictor/adjustment sets, source operators and controller scales was independently checked; all remain present exactly once. Seeds, limits and trial allowance match the controller.

| Repaired build02 artifact | SHA256 |
|---|---|
| generator.py, unchanged | `bbbf88e566d8b28481a1d5d7f72798528edcaa5ceaadf7207054b07f05451ad5` |
| model_spec.json | `870b18f85ebd900311e8eac9799c568576985769abae34584fc80e9db8a59fe5` |
| source_replay_v2.json | `f14bc302a4ae4c427765e42bc77faa1fea7dc2c258bbeda2aacf8effce5ed31d` |
| source_contexts/thai_development.csv | `b858496b37ba6d7bf7210945d281a347152f281bb08fbef8195271fa845a15f4` |
| source_contexts/gallagher_full.csv, unchanged | `9925831443ccfcd03a03d0eda477ec0e7d415f8c3a09885a450adf7f094473ad` |

**The original material blocker is resolved. No new pre-execution blocker was identified.** Component means/variances, threshold allocation, gap around 25, finite-support shape and covariance remain declared assumptions; this repair establishes compatibility, not recovery of source individual data. Detailed independent checks are retained in `postrun_audit.json` under `build02_preexecution_reaudit`.

## Equations, coding and conditional mechanics

Both `generator.py` files and both model specifications correctly preserve the admitted printed equations:

* Thai: `-10.672 + 1.648*bmi + 0.065*age - 15.3*male`.
* Gallagher DXA Equation 1: `76 - 1097.8/bmi - 20.6*male + 0.053*age + 95*asian/bmi - 0.044*asian*age + 154*male/bmi + 0.034*male*age`.

Male is coded 1, female 0. The source Asian indicator is 1 for Thai/Japanese and 0 for the supplied non-Asian groups, with that transport assumption stated. All seven Gallagher predictors are retained; no standalone Asian intercept was invented. Neither implementation selects a formula by source ID, row ID, row count or file lookup. Both copy input columns and append bodyfat; derived equation terms are recomputed from base covariates.

Build01 blends toward Thai only for Asian rows using one weight, then adds declared shared level/male shifts. Its residual SD is 4.31 times a common multiplier, with a fixed female multiplier 1.10. Build02 original uses sex-specific Asian bridge weights and residual SDs. Those are explicit alternative assumptions. Thai marginal bodyfat SDs and instrument CVs are not substituted for residual SD. Gallagher SEE=4.31 percentage points is identified as a residual-scale anchor whose transport is assumed.

For either implementation, let the clipped mean be `m` percentage points, and the chosen conditional variance be `v = min(sd^2, 0.95*m*(100-m))`. With `k = m*(100-m)/v - 1`, `alpha=(m/100)*k`, `beta=(1-m/100)*k`, the return `100*Beta(alpha,beta)` has conditional mean `m` and variance `v`. The formulas therefore have the correct factor of 100, preserve the bounded conditional mean and use squared percentage-point units for variance. Positive SDs, interior mean bounds and the 0.95 cap keep the shape parameters valid within the proposed calibration bounds. Mean clipping changes a raw regression prediction at extreme support and is disclosed. This algebraic check does not assert that draws or source statistics have been executed.

## Extraction, operators and calibration contract

Both original submissions map the required 18 source statistics correctly: Thai men/women means 14.1/31.8%, sample SDs 6.5/8.4 percentage points, unadjusted Pearson BMI-bodyfat correlations 0.72/0.77, all four Thai BMI-age-male OLS terms, and all eight Gallagher OLS terms. Means, sample SDs, correlations and regression coefficients remain distinct quantities. Source locators and development/pooled selections are preserved; unknown coefficient uncertainty remains unknown.

Thai operators use sex selections for the six marginal diagnostics and the pooled intercept-plus-BMI/age/male design for four coefficients. Gallagher operators use intercept plus `inv_bmi,male,age,asian_inv_bmi,asian_age,male_inv_bmi,male_age`. Each coefficient is estimated with the complete original adjustment set. The harness interface implements arithmetic mean, sample SD with ddof=1, Pearson correlation, and full-rank OLS with an intercept as declared. No Spearman/Pearson substitution or four-compartment/DXA substitution was found.

Each plan includes exactly 18 constraints once: means scale 2 percentage points, SDs scale 1 percentage point, correlations scale 0.1, intercepts scale 10 percentage points, BMI coefficient scale 0.25 percentage points per kg/m2, age/age-interaction scales 0.05 percentage points per year, male coefficients scale 2 percentage points per code unit, inverse-BMI scale 100 and inverse-BMI interactions scale 50 percentage points per m2/kg. The two textual unit-label styles are internally consistent with each candidate's evidence and operators and represent the same dimensions. The plans identify these as engineering scales, not uncertainty or likelihood weights.

Both original plans use fit seeds 13101/13102, replay seeds 23101/23102, max_trials=9, shrink=0.5, min_step_fraction=0.01, target_loss=0, and the controller's execution limits. Only four declared top-level scalars are adjustable in each. Context shapes, covariance scenarios and equation coefficients are fixed during numerical calibration. Shared-cohort constraints are disclosed as correlated, and Thai validation is not fitted.

## Build01 independent covariate verification and remaining assumptions

Directly recomputed both source CSV hashes, identifiers, column sets, deterministic columns, categorical counts, support ranges, BMI threshold counts and OLS design ranks. No generated outcome is present. Every derived-column maximum error was exactly 0 in the read numeric values. Thai design rank is 4; Gallagher rank is 8. All 18 metadata mappings/scales and controller seeds/limits passed the independent checks. Registry artifact hashes match the admitted sources.

| Build01 source context | Rows | Age range | BMI range | BMI>=25 | BMI>=30 |
|---|---:|---:|---:|---:|---:|
| Thai development | 8920 | 20.010336–83.956383 | 14–29.995667 | 1338 (15%) | 0 |
| Gallagher full | 9756 | 18.005316–95.904197 | 14.305879–34.889288 | 4059 | 869 |

Thai has 3920 male/5000 female rows, exactly 40 times 98/125. Gallagher has male Asian/non-Asian 1932/1746 and female Asian/non-Asian 3798/2280, consistent with sixfold source group composition. Preparation code constructs all six sex/ethnicity strata with their corresponding admitted age/BMI moments, before shuffling rows.

Build01's fixed 15% overweight component per development sex is an explicit unidentified shape scenario, not a reported subgroup fact. It is compatible with the full-cohort count constraint. The women's lower BMI component is strongly U-shaped (reported beta shapes about 0.070765 and 0.014327); its lower support at 14 and concentration near the upper threshold are assumptions with potential consequences for inverse-BMI projections. These limitations are disclosed rather than disguised as observed distributions. They are not pre-execution blockers but remain reasons why source replay cannot validate the source population or target application.

Age/BMI dependence is also unreported: build01 fixes latent correlation -0.15 for Thai and +0.10 for Gallagher; original build02 fixes +0.15. These choices are scenario assumptions, not fitted source correlations. Bounded marginal shapes, unknown BMI minima, Gallagher lower adult age, pooled White/Black structure, and identity transport across DXA devices are likewise explicit assumptions. Matching moments or obtaining a full-rank design does not identify these missing distributions.

## Audited build01 artifact binding

| Artifact | SHA256 |
|---|---|
| generator.py | `432b1948ae864069eed11bb4875a3793c835915cb9ca14e2bf77318cfe9d34c2` |
| model_spec.json | `2350dbe96988047ff0b7678b86ab30a29e17dbbe9795dc517e570afb896419b2` |
| evidence.json | `89812f5b0a390d6c0d374b7ecacb14f64697747ce06dc2ed6cbf321d6a46a3b1` |
| source_replay_v2.json | `07be2a0c47c9c06ef900a37d2a751cc3ba31941d9a32fa6c4ad601c8ef7584ce` |
| proposed_calibration_plan.json | `bd17ab76c9a53288153c7230e5312bb724094f011a03895fe0b321d153ab3913` |
| source_contexts/thai_development.csv | `88961c31535ae31af51830ea9b8013c2a8f5d7b46ce7d9731659288d648cd716` |
| source_contexts/gallagher_full.csv | `3d9d114a3cb86e801682e7ca4f7948372eb4d94f3eb9ed592b8e60efdafa4363` |

The initial pre-execution clearance did not assert execution success or source agreement. The subsequent source-only output audit below uses the parent's separately authorized retained executions.

## Build01 post-run source-output recomputation

**Independent recomputation passed; all required diagnostics are retained.** No generator was imported or executed by the auditor. Read only the explicitly authorized source-generated tables and reports under `build01/cal/initial_fit/`, never the trial-level qualification-grid observations or any target outcomes. Calculated arithmetic means, sample variances and Pearson correlations directly from CSV numbers, and OLS through centered/scaled QR decomposition rather than calling the harness operator implementation.

Recomputed all 18 statistics for the initial trial's two fit seeds, selected trial 6's two fit seeds and its two replay seeds: 108 statistics from 12 source-generated tables. Maximum absolute discrepancy from the stored statistic was `1.1101519703515805e-10`; maximum discrepancy after dividing by its declared engineering scale was `6.05765437811101e-12`. This is ordinary numerical roundoff, well within the audit tolerance `1e-8`. Source covariates and identifiers were preserved exactly in the parsed values for those 12 outputs; outputs were finite and within 0–100.

Separately checked all 20 source reports, all 40 successful execution-receipt/output-hash bindings and every stored constraint record. All nine fit trials retain 36 records each (18 checks times two seeds), and selected replay retains another 36: 360 diagnostics total. Operators, reported evidence values, counts, units, differences, scales and aggregate loss arithmetic agree. No constraint disappeared because it fit poorly. The recorded minimum fit-loss trial is correctly selected; the recorded stop at the nine-trial allowance and status `fit_threshold_not_met` are accurate.

| Source-only engineering loss | Value |
|---|---:|
| Initial trial, two fit seeds | 1.0702249438702736 |
| Selected trial 6, two fit seeds | 0.6681018957027327 |
| Selected trial 6, two replay seeds | 0.7939137387717018 |

Selected numerical parameters are Asian blend 0.5, level shift 0, male shift -1 percentage point and residual multiplier 1.0. Source discrepancies remain, including the Thai female marginal spread/correlation, Thai BMI slope and Gallagher male-inverse-BMI term. A lower engineering loss does not validate the reconstructed source populations, prove global optimization or establish target utility. Zero discrepancy was not attained.

Machine-readable provenance and all 108 independently recomputed values are in `postrun_audit.json` under `build01_source_output_recomputation`. The audited calibration `result.json` SHA256 is `a275358b81f81706d912b08c9775a20649ccc3bc1c047d165473d8ba02ff7d09`.

## Build02 post-run source-output recomputation

**Independent recomputation passed with all 18 diagnostics retained.** Applied the same source-only audit method and numerical tolerance as build01. Recomputed 108 statistics from 12 generated source tables: initial trial fit seeds, selected trial 8 fit seeds and selected trial replay seeds. Maximum absolute discrepancy from a stored statistic was `7.936051815704559e-11`; maximum scaled discrepancy was `6.439987432216299e-12`. Source covariate/identifier preservation error was zero in the parsed values, and all audited bodyfat outputs were finite and within 0–100.

Checked all 20 reports, 40 execution-receipt/output-hash bindings and 360 diagnostic records. Every report retains the complete 18-check set, with the original operators, evidence values, counts, units and engineering scales. All differences, scaled errors and aggregate losses recompute correctly. Trial 8 is the minimum recorded fit-loss trial. `max_trials` and `fit_threshold_not_met` accurately describe the nine-trial stop without exact source agreement.

| Build02 source-only engineering loss | Value |
|---|---:|
| Initial trial, two fit seeds | 0.6950506982337636 |
| Selected trial 8, two fit seeds | 0.6237954002452131 |
| Selected trial 8, two replay seeds | 0.7064306967978499 |

Selected parameters are male/female bridge weights 0.75/0.25 and male/female residual SDs 4.81/3.81 percentage points. Remaining replay discrepancies include Gallagher male-inverse-BMI coefficient 43.9447–82.0497 versus 154, Thai BMI coefficient 2.02521–2.02942 versus 1.648, Thai female Pearson BMI-bodyfat correlation 0.90437–0.90622 versus 0.77, and female SD 9.63424–9.70092 versus 8.4. These discrepancies remain visible and are not reclassified as validation success. The two candidates use distinct assumed source covariate scenarios, so their engineering scores are not a target-performance ranking.

All prior preflight and build01 audit data remain in `postrun_audit.json`; build02 recomputed values and source-table/report hashes are appended under `build02_source_output_recomputation`. The audited build02 `result.json` SHA256 is `7d8dae9efa2bade805cfb7de1e2a593840f8e20f38d5750847315ce9dec54e11`. No generator was imported/executed, no target data were read and no candidate/calibration files were modified for this audit.

## Aggregate change-count definitions

Independently checked all 108 rows in `source_results/source_diagnostics.csv` against the initial fit, selected fit and selected replay records, plus the per-source squared scaled-error summaries in `source_results/summary.json`. Both aggregate artifacts are numerically consistent. Initial-to-selected **fit-seed** improvement counts depend on the explicitly named error summary:

| Error summary across the two fit seeds | Build01 improved/worsened | Build02 improved/worsened |
|---|---:|---:|
| Mean absolute per-seed error: `mean(abs(estimate_s - reported))` | 10 / 8 | 9 / 9 |
| Absolute error of the seed mean: `abs(mean(estimate_s) - reported)` | 11 / 7 | 9 / 9 |

There are no unchanged constraints under either definition. The second summary allows opposite-signed seed errors to cancel; it is not the first summary. Build01's sole classification difference is Gallagher `asian_age`: mean absolute per-seed error increases from 0.0040733006 to 0.0055944389, while absolute error of the seed mean decreases from 0.0005536282 to 0.0002298440. Thus the builder's 11/7 statement and the controller's clearly labeled 10/8 statement can both be correct. Use the controller's mean-absolute-error definition when reporting its aggregate count, and label the alternative explicitly. Neither summary is the mean squared scaled-error objective used for numerical selection, and neither supports target-performance claims.

The calculation and both count definitions are appended to `postrun_audit.json` under `aggregate_metric_definition_audit`. Audited aggregate hashes: `summary.json` = `0d924a1ff17955397fcf385101f9f7db0bc35fb65351a161d7aea610807d2df6`; `source_diagnostics.csv` = `ef3538b05b5eb13172ede47f64fec6f6ba99397fc05f5603002f365ce347211a`. No frozen artifact or review decision was changed.
