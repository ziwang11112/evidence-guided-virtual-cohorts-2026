# Filshtein et al. (2021): implementation audit and comparison with the frozen virtual-cohort study

Date: 3 November 2026. Scope: the named paper, its official author repository, and the current local manuscript/results. This is a reading and static-code audit, not an experiment. No author code was run, no patient rows were inspected or acquired, and no frozen artifact was changed. The filename follows the requested spelling; the author's name is **Filshtein**.

## Assessment

Filshtein et al. is a substantive methodological predecessor and a useful baseline candidate. The paper already connects a scientific question, an explicit joint model, shared aggregate parameters, complete synthetic cohorts and subsequent biomedical analysis. Its earlier existence does not decide whether the present project is useful. The important comparison is which inputs each method requires, what uncertainty and heterogeneity it handles, and which analytical uses its validation actually supports.

The strongest demonstrated advantage of Filshtein's implementation is faithful recovery of the particular regression fitted in each source cohort, together with an implemented longitudinal pooling/imputation analysis. Our current study asks a different and more underdetermined question: construct a joint law from heterogeneous published fragments without requesting bespoke source-microdata fits, then inspect its consequences in separately prepared target references. That input difference can be useful, but it is not evidence that our method produces better data. A fair empirical comparison has not been run.

## Sources and access record

All URLs below are primary sources. The main paper and the listed code/parameter files were read on this date.

| ID | Source and precise location | Reading status |
|---|---|---|
| P | [Main article, DOI 10.1097/EDE.0000000000001373](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/): Methods Steps 1–5; Tables 1–4; Simulation Study; Discussion; Reproducibility footnote | Full main text and tables read |
| R | [Official repository](https://github.com/powerepilab/Sim_for_data_pooling), latest observed commit [6708e43d5e342fa76d57b31d5a6d0bfcc2979539](https://github.com/powerepilab/Sim_for_data_pooling/commit/6708e43d5e342fa76d57b31d5a6d0bfcc2979539), 16 September 2020 | Root inventory and README read; 10 files, no subdirectory in returned inventory |
| H | [HRS source-fitting script](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/HRS_sim_data_code_postGitHub_20200728.R): `jd_cses`, `jd_educ`, `jd_hba1c`, `jd_mem` | Read statically |
| A | [ARIC source-fitting script](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/ARIC_sim_data_code_postGitHub_20200728.R): education, diet, HbA1c and memory fits | Read statically |
| C1 | [RCTSim1](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/RCTSim1_postGitHub_20200728.R): `preamble_sim` and both cohort calls | Read statically |
| C2 | [RCTSim2](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/RCTSim2_postGitHub_20200728.R): `dataGen`, `modFitPool`, `B=5000` | Read statically |
| C3 | [RCTSim3](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/RCTSim3_postGitHub_20200728.R): coefficient extraction and `rPool` | Read statically |
| HP | [HRS parameter output](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/HRSmodels_20200902_fullDemoTable.txt) | All aggregate output read |
| AP | [ARIC parameter output](https://github.com/powerepilab/Sim_for_data_pooling/blob/6708e43d5e342fa76d57b31d5a6d0bfcc2979539/ARICmodels_20200902_fullDemoTable.txt) | All aggregate output read |
| S1 | [eMethods/eAppendix A DOCX](https://pmc.ncbi.nlm.nih.gov/articles/instance/8338788/bin/NIHMS1702978-supplement-eMethods_eAppendixA.docx) | Link verified; binary not retrieved: PMC returned browser/reCAPTCHA HTML. Publisher route was challenged; Europe PMC supplementary/full-text endpoints did not supply it |
| S2 | [Supplemental Appendix B XLSX](https://pmc.ncbi.nlm.nih.gov/articles/instance/8338788/bin/NIHMS1702978-supplement-Supplemental_Appendix_B.xlsx) | Link verified; binary not retrieved for the same reason |

**Access limitation:** this report does not claim to have read S1/S2. Exact supplement-only equations, scenario parameters, bias/RMSE/coverage values and any extra diagnostics remain unverified. The code provides an independent primary record of the actual implemented formulas, but does not substitute for verification of every supplement result. No numerical supplement result is invented below.

Local comparison sources are [DRAFT_v0_5.md](../manuscript/DRAFT_v0_5.md), especially Methods/Allocation and Table 2, and the frozen [RESULT_INTERPRETATION.md](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/publication/RESULT_INTERPRETATION.md). All local numbers below are retained results, not new analyses.

## What the implemented method actually requires

**Verified from H/A/HP/AP:** local analysts have source microdata. The HRS script loads prepared `hrs_cross.rda` and `hrs_long.rda`; ARIC loads `Atable_0.rda` and `memData2.rda`. They fit the generator parameters from those records. The recipient's simulation stage does not need the underlying rows, but someone must first estimate the required conditional models. The public text outputs include demographic counts, regression coefficients, dispersion and random-effect summaries.

Thus “the generating analyst need not receive all source records” is accurate. “The method starts only from whatever statistics happen to be published in unrelated papers” is not an accurate description of this implementation. Conversely, nothing prevents a sequential model from using published parameters when they are sufficient. Its mathematics is not intrinsically restricted to bespoke collaborator fits.

The scripts explicitly warn that saved R model objects can inadvertently retain raw records/environments, recommending explicit text parameter exports. This is a useful implementation lesson to borrow; a model object is not automatically a safe aggregate artifact. [H; A]

## Exact fitted and sampling structure

Let `a0=(baseline age−60)/10`, `a=(age at observation−60)/10`, and let `Z` contain sex, race and education indicators. Let `H−=min(HbA1c−6.5,0)` and `H+=max(HbA1c−6.5,0)`.

| Stage | Conditional law implemented | Primary evidence |
|---|---|---|
| Demographics | Joint age-category/sex/race frequencies; sample a category combination, then uniform age within its interval | H/A demographic tables; C2 `d_dem`, `Age_Low`, `Age_High` |
| Childhood SES, HRS | `CSES = b0 + b1*a0 + b2*Black + Normal(0,sigma²)` | H `jd_cses`; C2 |
| Education | Multinomial logits on `a0 + sex + race`, with CSES additionally in HRS | H/A `jd_educ`; C2 category probability sampling |
| Two diet scores, ARIC | Separate linear models on `a0 + sex + race + education`, with normal residuals | A `jd_diet_p`, `jd_diet_w`; C2 |
| HbA1c | Gamma GLM with log mean on demographics/education and observed CSES or diet; generation uses shape `1/phi`, scale `mu*phi` | H/A `jd_hba1c`; C2 |
| Memory trajectory | `memory ~ a*(H− + H+ + race + education + sex + observed CSES/diet) + (1+a|ID)`; correlated normal random intercept/slope and normal observation error | H/A `jd_mem`; C1 covariance extraction; C2 |

The source-specific factorization can be written compactly as:

`p(demographics) × p(CSES|age,race) × p(education|parents) × p(diet|parents) × p(HbA1c|parents) × p(memory trajectory|parents,random effects)`

with the unavailable CSES or diet factor omitted in that cohort before imputation. These formulas clarify Table 1's dependency order without implying that a fully specified causal graph is empirically identified.

Two implementation details matter for fidelity. C2 uses 50–55 through 75–80 intervals, then **80–100**, so the top category is not five years wide. C1 requests **four observations spaced two years apart for both cohorts**. HP reports 43,500 original HRS observations for 11,509 people; AP reports 29,307 ARIC observations for 12,043 people. The generated design is consequently a regular complete follow-up design rather than an exact recreation of original visit attendance. These are verified code facts; whether changing them would improve any performance measure would require an experiment.

## Pooling, imputation and uncertainty

**Verified implementation:** C2 stacks two generated cohorts, retains one baseline row per synthetic person for MICE, removes cohort/IDs from the imputation predictors, and calls `mice(m=1, method='norm')`. It imputes CSES for ARIC and diet for HRS, then attaches the completed baseline values to all visits. Its pooled regression includes cohort-specific exposure intercept terms and cohort-by-age-by-confounder terms, while keeping the age-by-HbA1c slopes common. Reduced and no-cohort models are also fitted. [C2]

**Verified implementation:** C3 extracts the coefficient estimates from the repeated fits and computes their mean and **standard deviation across 5,000 realizations**. Although C2 also extracts each model's SE, the displayed `rPool` summary uses the empirical SD of coefficients. No Rubin combining formula is present in C3. Source regression coefficients remain fixed in C2; random covariates, random effects, residuals and imputation draws vary. [C2; C3]

**Interpretation:** this repeated procedure is substantially more informative about Monte Carlo behavior than three fixed-law draws, but 5,000 simulations are not 5,000 source cohorts. A fitted-model simulation can approximate sampling variation under its assumptions. This audit does not establish full-pipeline coverage after source fitting, graph selection, source harmonization and missing-covariate transport. Those uncertainty layers should not be confused with the reported empirical SD. Our current three seeds also omit source-estimation, structural and transport uncertainty, so we cannot claim an established advantage here.

## Quantitative evidence: successful fitted-model recovery and visible limitations

The numbers below are paper values, with no new fit. For the memory-change coefficients, age is in decades (the code's `/10` scale), and HbA1c is in percentage-point units. P Table 3 reports:

| Cohort and HbA1c segment | Original estimate (95% CI) | Synthetic before imputation | Synthetic after imputation |
|---|---|---|---|
| ARIC, below 6.5 | −0.055 (−0.089, −0.022) | −0.055 (−0.082, −0.029) | −0.056 (−0.083, −0.030) |
| ARIC, above 6.5 | 0.007 (−0.015, 0.028) | 0.007 (−0.036, 0.049) | 0.006 (−0.037, 0.048) |
| HRS, below 6.5 | −0.047 (−0.076, −0.017) | −0.047 (−0.065, −0.028) | −0.047 (−0.065, −0.029) |
| HRS, above 6.5 | 0.013 (−0.012, 0.038) | 0.013 (−0.020, 0.046) | 0.013 (−0.020, 0.046) |

P Table 4 / Results:

| Analysis | Below 6.5 | Above 6.5 |
|---|---|---|
| Pooled, imputed, cohort terms | −0.050 (−0.065, −0.035) | 0.010 (−0.016, 0.036) |
| Pooled, without imputed covariates | −0.050 (−0.065, −0.035) | 0.010 (−0.016, 0.036) |
| Pooled, imputed, without cohort adjustment | −0.032 (−0.045, −0.019) | −0.002 (−0.025, 0.020) |
| Random-effects meta-analysis | −0.050 (−0.073, −0.028) | 0.010 (−0.007, 0.026) |

P Table 2, original → synthetic mean (SD):

| Diagnostic | Original → synthetic |
|---|---|
| HRS HbA1c overall | 5.9 (1.0) → 5.9 (0.96) |
| ARIC HbA1c overall | 5.8 (1.2) → 5.8 (1.2) |
| HRS HbA1c above 6.5 | 7.7 (1.4) → 7.2 (0.6) |
| ARIC HbA1c above 6.5 | 8.5 (2.0) → 7.4 (0.7) |

**Analysis of these facts:** excellent recovery of a model's coefficients coexists with poor upper-tail dispersion. The supplied outcome regression is also the regression used to evaluate pre-imputation synthetic data; recovery is a legitimate implementation/analysis-preservation test, but not a test of an unseen relationship. Conversely, it would be wrong to dismiss the recovery as worthless: sharing an executable approximation without sharing source rows is exactly a practical objective here.

The imputation and cohort-adjustment analyses go beyond simply replaying the original covariate set. Their large scientific limitation is identification: structurally missing true values are unavailable for a direct recovery test. The unchanged imputed versus non-imputed pooled slopes show little benefit from those added confounders in this example; they do not establish that imputation cannot help elsewhere. The no-cohort result is a useful warning that pooling assumptions can dominate the apparent benefit of a larger synthetic sample.

P's Simulation Study describes three scenarios: matching models; exposure-model misspecification; exposure plus outcome misspecification. It compares synthetic coefficients against the same chosen analysis fitted to simulated originals. Exact scenario results remain unverified because S1/S2 were inaccessible. Do not convert the qualitative conclusion into a coverage, bias or general robustness guarantee.

## Difference from our present study, and what can fairly be called better

| Dimension | Filshtein implementation | Frozen local study | Judgment |
|---|---|---|---|
| Information available | Source-specific conditional fits from local microdata | Published, population-qualified fragments and completion assumptions | Different information regimes; no accuracy ranking follows |
| Target | Reproduce source analyses and estimate a pooled longitudinal coefficient | Construct an externally informed target cohort and inspect six target projections | Transport adds unresolved difficulty in ours |
| Data complexity demonstrated | Repeated outcomes, correlated random effects, structural missingness across cohorts | Five-variable whole-cohort generation, cross-sectional projections | Filshtein is stronger on demonstrated longitudinal pooling |
| Prespecified analysis preservation | Original outcome fit explicitly supplied | Target-reference coefficients withheld from constructors; some source-analogous projections supplied | Our evaluation tests some unsupplied target consequences, but both target families were researcher-exposed |
| Author variability | A coordinated specified model | Five Agent-authored models per information condition | Our design exposes construction variability; this is not biological replication |
| Evidence provenance | Explicit DAG and source-cohort fits | Source/operator/units/adjustment/role and completion/transport records | Our richer record is useful for heterogeneous fragments, not a proven accuracy improvement |
| Uncertainty | 5,000 repeated realizations with one imputation each | Three fixed final seeds per construction; uncertain reference estimates | Neither establishes comprehensive uncertainty propagation |
| Comparative performance | No direct comparison to our framework | Four asymmetric fixed statistical constructions | Named-method superiority untested |

The local study's strongest descriptive evidence is that relational information reduced average discrepancy for five of six specified coefficients. Its counterexamples matter: CHNS BMI discrepancy increased **0.020380 → 0.031557**; statistical E1 was closer than every corresponding Agent for CHNS glucose (**0.012021**, Agent arm **0.024079**) and ENSANUT conditional BMI (**0.007940**, Agent arm **0.025649**). These values are endpoint-specific discrepancies in different units, not comparable to Filshtein's coefficient values or a common quality score. [Local DRAFT Table 2; frozen interpretation]

Potential advantages of our procedure are practical hypotheses: reuse incomplete literature when bespoke source fits cannot be obtained; make heterogeneous evidence-use decisions explicit; inspect several intended projections and author-dependent joint completions. No current result proves that those advantages beat a carefully adapted sequential statistical model. More variables, multiple studies, a DAG, complete synthetic rows, or analysis-specific construction should not be claimed as capabilities absent from Filshtein's method.

## Strengths to borrow

1. Start with the analytical estimand and a transparent dependency structure, then state every conditional law and residual distribution.
2. Publish a compact numerical parameter contract sufficient to reconstruct the generator, rather than requiring opaque fitted objects.
3. Separate source-fit recovery from new analytical uses; report both coefficient behavior and distributional failures.
4. Preserve cohort heterogeneity in pooled analyses and show an explicit sensitivity analysis when pooling assumptions change.
5. Make missing-covariate transport assumptions visible. Cross-source interactions involving variables never jointly observed are not automatically learned by imputation or by an Agent.
6. Distinguish Monte Carlo variability, imputation variability and uncertainty in the source evidence/model. More generated rows cannot supply missing evidence.

These are methodological lessons, not claims that the earlier study solves all of them perfectly.

## Reproduction and fair baseline feasibility

**Original end-to-end reproduction is not currently turnkey.** The repository scripts expect prepared microdata and fitted `.RDA` files absent from the root inventory; the posted source-fitting scripts begin after those analytic datasets have been prepared. The README specifies R 4.0.1 and package versions, including mice 3.9.0 and lme4 1.1-23. Exact original sample construction, full-precision model objects and original retained outputs have not been obtained. [R/README; H; A; C1]

**A faithful reconstruction of the simulation stage is plausible without new source rows.** HP/AP contain full demographic tables and printed parameters, including residual scales and random-effect information. Those permit explicit parameter construction instead of relying on missing model objects. This would be an implementation reconstructed from rounded published parameters, not a verified bit-for-bit reproduction. It still needs agreement on variable coding, output targets, tolerances and reproducible dependency versions. No such reconstruction was executed here.

**A same-input adapted baseline for our question is feasible in principle.** Use the same admitted E0/E1 packets, population/measurement rules, visible queries, generated sample size and seed/feedback budget as our constructions. A statistical author would prespecify a DAG/order, conditional families and completion assumptions, then solve or fit only the admitted aggregate constraints. Where the packet does not identify a conditional coefficient or residual dependence, retain a declared assumption/sensitivity range rather than covertly fitting target rows. This is a “Filshtein-style sequential synthesis adapted to published fragments,” not the unmodified original method.

Before that comparison, the following information must be frozen: complete admissible aggregates and their joint uncertainty if available; source eligibility and measurement definitions; whether an association is marginal, adjusted or a projection; required conditional families/order; handling of incompatible sources; residual dependence and support assumptions; identical numerical-use opportunities; and genuinely withheld evaluation quantities. If either method receives bespoke target/source microdata fits while the other receives only sparse literature fragments, label it as an information-rich reference rather than a fair same-input method comparison.

Use distinct evaluation groups: supplied constraints, unsupplied relationships, subgroup/tail behavior, uncertainty behavior and operational cost. Include every constructor and failure. The existing statistical E1 comparisons already show that a competent non-Agent construction can win some endpoints. A future named-method benchmark should test that possibility, not build a deliberately weak baseline.

## Remaining evidence gap

The only major reading gap in this bounded audit is S1/S2. Their exact equations and simulation tables should be checked before making any numerical statement about robustness to misspecification or reproduction of the supplementary simulation. This gap does not erase the verified main-table results, static implementation facts, or the practical strengths identified above. It does limit a claim that the entire original study has been fully re-audited.
