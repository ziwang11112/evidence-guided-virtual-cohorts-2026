# Source-only evidence gap map — age × BMI and triglycerides

Separate age–TG and BMI–TG evidence does not identify their joint conditional distribution. A subgroup conclusion can change while both source marginal associations remain compatible. No direction of association was specified in advance, and no target outcomes were inspected.

| Intended conclusion | Evidence that would constrain it | What this search obtained | Remaining gap |
|---|---|---|---|
| TG means or quantiles in age × BMI × sex cells | Matched cell estimand, sample count, interval, measurement protocol | Tromsø published 15 joint categories per sex; exact coefficients are in an inaccessible supplement | The 28 nonreference ratios and CIs remain unextracted; ratios would not supply arithmetic means or residual spread |
| Does BMI association change with age? | Explicit age interaction, age-stratified slopes, or joint contrasts on the same scale | China-PAR reports raw-TG standardized-BMI slopes before/after age 54; Tromsø reports interaction tests | Exact standardized-BMI denominator and between-stratum coefficient covariance |
| Does age association change with BMI? | Age slopes within BMI or nonparametric conditional curves | Tromsø joint model addresses this; China-PAR BMI curves are supplementary | No exact complete conditional curve extracted |
| Probability of TG exceeding a threshold | Joint-cell event counts/proportions or valid threshold model | None retained | Tail behavior, residual distribution, threshold-specific uncertainty |
| Inference from a generated cohort with only age, sex and BMI | Conditional model after appropriately integrating omitted covariates, covariance/uncertainty and transport evidence | Both retained papers adjust for additional covariates | A published conditional coefficient is not automatically the reduced model for available covariates |
| Validity of subgroup significance and standard errors | Sampling model, source parameter covariance, model/transport sensitivity | Reported source CIs and interaction P values only | Simulated rows/seeds cannot manufacture missing evidence precision |

## Newly retrieved primary evidence

**Mikkelsen et al. 2023, Tromsø7.** Cross-sectional Norwegian adults aged 40+, nonfasting serum TG in mmol/L. Its sex-specific log-TG model combines five age bands with three BMI bands. The age × BMI test is P<0.001 in women and P=0.32 in men; the latter does not prove no interaction. The detailed 28 contrasts could not be retrieved. Main text gives 9,341 men in the model; Figure 2 caption gives 9,583. Both give 10,143 women. Adjustment includes meal timing and lifestyle; Figure 2 identifies education/medication as women-only. Exact final joint-model implementation remains to be checked. These are conditional back-transformed log effects, not arithmetic cell means. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10308115/)

**Zhang et al. 2026, China-PAR.** Longitudinal Chinese cohort: 83,487 people, 217,239 measurements, 10-hour fasting TG in mg/dL. Table 3 reports adjusted mixed-model BMI slopes per 1 SD, before/after the age-54 sex-trajectory crossing:

| Sex | Before 54, estimate (95% CI) | After 54, estimate (95% CI) |
|---|---:|---:|
| Men | 29.98 (28.49–31.47) | 17.53 (16.66–18.40) |
| Women | 17.96 (17.05–18.88) | 13.63 (12.88–14.38) |

Both age contrasts carry the footnote P<0.05. The main Pinteraction column instead compares sexes. Exact SD normalization is unresolved; these numbers must remain per-SD estimates. Repeated-measure, adjusted, broad-age associations do not automatically calibrate a cross-sectional 40–79 target. Waist-based curves were not treated as BMI evidence. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13491077/)

## Applicability decision and minimal choice

There is usable new conditional evidence. The bounded search does **not** establish that joint evidence is absent. It also does not supply a fully calibrated target distribution.

**Recommended minimal choice: retain the current primary generator unchanged in this evidence round, and record a justified no-op for coefficient calibration.** I have not inspected that generator, so this is a decision against a new numerical update from these sources, not an endorsement of its existing assumptions.

An additional, explicitly labelled hypothesis-transfer sensitivity would be scientifically supportable if the experiment needs a second model: posit age-dependent BMI effects by sex, then evaluate that assumption independently. The source supports testing age dependence. It does not establish a target effect size. If numerical older/younger multipliers are used, assuming a common BMI SD gives derived ratios 17.53/29.98 = 0.58472 for men and 13.63/17.96 = 0.75891 for women. **Those ratios are not reported effects, have no calculated CI, and are interpretable as slope attenuation only under the unverified common-SD assumption.** If standardization was stratum-specific, the ratios also contain SD differences. The broader source age strata, omitted adjustment covariates, and longitudinal-to-cross-sectional transfer require additional assumptions. This sensitivity must not be described as source-calibrated or as independent confirmation of the primary generator.

The prospective 40–79 task scope was provided by the parent after search. No target covariates/outcomes, baseline candidate, prior evaluation, or desired signs were consulted. No data generation, tuning, harness registration, or execution occurred.

## Files

- `candidate_evidence.json`: exact estimates, uncertainty, locators, measurement, adjustment, and limitations; candidate source registry only.
- `source_artifact_manifest.json`: original retrieval URLs and SHA-256 hashes of saved source bytes; no approval claims.
- `PMC10308115.xml`, `PMC13491077.xml`, `Mikkelsen2023_publisher.html`: full primary source artifacts.
- `retrieval_log.md` and `supplement_retry_log.jsonl`: actual searches and access outcomes.
