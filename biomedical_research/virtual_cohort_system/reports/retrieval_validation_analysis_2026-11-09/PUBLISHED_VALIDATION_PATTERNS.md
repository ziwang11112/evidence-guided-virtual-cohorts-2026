# Published validation patterns for biomedical synthetic cohorts

Research-only comparison, checked against primary papers online on 2026-11-09. No data generation, model fitting, or project experiments were performed. Four examples were selected for contrasting information access and downstream biomedical analyses; this is not a systematic review. SynthIPD is an arXiv preprint, distinguished below from journal publications.

**Answer to the practical question:** repeating the same biomedical analysis on real and synthetic data is a well-established way to assess *utility for that analysis*. Close results support a bounded claim about the specified population, variables, estimand, and analysis. They do not establish general interchangeability, new causal discoveries, or preservation of every untested relationship. The studies below illustrate why the generation inputs and validation independence must accompany any claim of closeness. This interpretation is our synthesis, rather than a universal acceptance rule supplied by these papers. [Filshtein, Discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/); [Eckardt, Results and Discussion](https://www.nature.com/articles/s41746-024-01076-x).

## Primary-paper comparison

### 1. Zhao et al., SynthIPD: training-free synthetic individual patient data generation

**Status/access.** arXiv:2509.16466v2, 24 July 2026; no patient-level training data. Inputs include arm-level Kaplan–Meier (KM) curves and subgroup counts, median survival, hazard ratios (HRs), and available intervals. Covariate assignments are optimized against these summaries. [Sections 2–3](https://arxiv.org/html/2509.16466v2#S2).

**Validation.** N9741 subgroup median progression-free survival and HRs/intervals match the supplied summaries; separately supplied subgroup KM curves were used for comparison. Simulations examine Cox, accelerated-failure-time, and crossing-hazard settings using survival-curve distances and summary-statistic losses. [Section 4.1, Table 4/Figure 5; Section 5, Table 6; Appendix D.2](https://arxiv.org/html/2509.16466v2#S4.SS1).

**Boundary.** Matching optimization inputs is reconstruction consistency; the comparison-only subgroup curves add evidence beyond those inputs. The paper explicitly states that multiple IPDs can share the reported summaries. Its current covariate-generation step uses discrete covariates; more complex dependence remains a development direction. Do not label displayed CIs or repeated reconstruction variability as demonstrated frequentist coverage for arbitrary new analyses. [Section 3 opening; Section 6; Appendix D.2](https://arxiv.org/html/2509.16466v2#S3).

### 2. Filshtein et al., Proof of Concept Example for Use of Simulation to Allow Data Pooling Despite Privacy Restrictions

**Status/access.** Epidemiology 32:638–647 (2021). This is model/summary sharing, not generation from ordinary publications alone. Each analyst accessed one cohort's individual records (HRS or ARIC); regression coefficients and residual-distribution parameters were shared after DAG-guided source-side fitting. [Introduction; Methods, Statistical methods, Steps 1–2](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/).

**Validation.** Across 5,000 synthetic iterations, the authors compared covariate distributions, HbA1c–memory-decline effect estimates, and associated standard errors with the cohort-specific originals. They then pooled synthetic cohorts and imputed covariates measured in only one source. Results report similar original/synthetic coefficients and precision. [Methods, Step 3; Results, Tables 2–4](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/).

**Boundary.** This establishes reproduction for the specified model more directly than transfer to a new question. The authors explicitly restrict repurposing when the causal structure changes, and identify cross-cohort imputation assumptions and interactions involving separately missing covariates as limitations. The proposed confounders were not strong confounders empirically. [Discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/).

### 3. Callender et al., SynthCraft: An AI partner for synthetic data generation to support data access and augmentation in healthcare

**Status/access.** PLOS Digital Health 5:e0001290 (2026). Generators train on real NHANES/TCGA records on the user's device. The LLM's lack of access to records does **not** make the overall method aggregate-only. [Methods, framework description and Synthetic data generation and performance evaluation](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001290).

**Validation.** NHANES analyses compare myocardial-infarction logistic-regression odds ratios/95% CIs, then train on synthetic and test on real data (TSTR), reporting overall/subgroup AUCs. TCGA evaluates tumour-purity prediction MSE with five-fold cross-validation. [Statistical analysis; Table 3; Figure 2](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001290).

**Boundary.** Real/ADS-GAN/CTGAN AUCs were 0.818/0.781/0.797, while ethnic-group augmentation did not improve performance. AUC assesses discrimination, not probability calibration. The main-text NHANES TSTR description alone should not be treated as proof that test records were excluded before generator fitting. These experiments use learned patient distributions, a different information setting from literature-only cohort construction. [Results of synthetic data generated from NHANES; Figure 2; Statistical analysis](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001290).

### 4. Eckardt et al., Mimicking clinical trials with synthetic acute myeloid leukemia patients using generative artificial intelligence

**Status/access.** npj Digital Medicine 7:76 (2024). CTAB-GAN+ and normalizing flows learned from individual records of 1,606 patients pooled from four AML trials. [Abstract; Methods](https://www.nature.com/articles/s41746-024-01076-x).

**Validation.** The authors repeated remission logistic regression and event-free/overall-survival Cox and KM analyses, comparing odds/HR estimates, 95% CIs, survival curves, marginals, and correlations. [Results, Tables 2–3/Figures 2–3; Methods, Statistical analyses](https://www.nature.com/articles/s41746-024-01076-x).

**Boundary.** Median event-free survival was 7.2 months originally versus 12.8 (CTAB-GAN+) and 9.0 (normalizing flows), despite favorable fidelity assessments. Although Results describes EFS as exempt from direct tuning, Methods specifies tuning remission, overall survival, and the OS–EFS difference; EFS is therefore not a clean untouched endpoint. Small treatment subgroups limited arm-specific synthesis; trial populations limit generalization. [Survival Results; Methods, synthetic data generation; Discussion](https://www.nature.com/articles/s41746-024-01076-x).

## An adaptable evaluation protocol

The following is a proposed design informed by these examples, not a protocol claimed to have been tested by all four papers.

1. **Define the intended use before construction.** Freeze the population, sample size, endpoints, units, transformations, adjustment variables, missingness handling, and estimation code. For an analysis-oriented cohort, use the actual biomedical analyses as primary outcomes; distribution checks support their interpretation.
2. **Label every reference by exposure.** Distinguish generation inputs, adaptive feedback, untouched internal comparisons, and external validation. A coefficient deliberately fitted during generation can establish implementation consistency; reserve stronger validation claims for comparisons unavailable to construction. Record whether source-side patient-level fitting was required.
3. **Report a complete endpoint panel.** For each estimand, show real estimate, synthetic estimate, signed/absolute difference in scientific units, available uncertainty, and computability status. Add relevant marginal tails, joint/conditional associations, residual variation, subgroup behavior, and sample eligibility. Retain failures and unavailable comparisons. Avoid replacing these with one global quality score.
4. **Specify what “close” means prospectively.** If practical equivalence is required, justify an endpoint-specific tolerance before seeing results and analyze the difference against it. Matching signs, a nonsignificant difference, or overlapping CIs alone is not an equivalence demonstration. Without justified tolerances, provide descriptive agreement rather than inventing pass thresholds.
5. **Separate uncertainty sources.** Fixed-generator seeds measure sampling variability conditional on that generator. Reconstruction alternatives probe underidentification. Sampling uncertainty in the source and variation from rebuilding the model are different quantities. CI overlap is not coverage: coverage requires a known truth or a justified repeated-sampling design. Do not turn added synthetic rows into additional observed information.
6. **Validate the intended downstream use.** For prediction, use a real test set withheld before all generator fitting/selection, and evaluate calibration as well as discrimination and relevant subgroups. For scientific estimation, evaluate the prespecified coefficients/effects and sensitivity to plausible dependence structures. External-population claims need external-population evidence.

The defensible conclusion is therefore “usable for these evaluated analyses under these information and population assumptions,” when the evidence supports it. Broader usefulness remains a separate empirical question.

## Verification notes

- The requested surname “Ilshtein” resolves to **Filshtein** in the verified primary publication.
- Primary methods/results were inspected through arXiv, the publisher, or the primary full-text record. PMC's direct page sometimes returned a browser challenge; its indexed full-text methods/results for Filshtein were accessible through search. No review was substituted for that primary evidence.
- No claim is made that these four papers demonstrate universal statistical equivalence, automatic privacy, arbitrary causal identification, or validation of our own system.
