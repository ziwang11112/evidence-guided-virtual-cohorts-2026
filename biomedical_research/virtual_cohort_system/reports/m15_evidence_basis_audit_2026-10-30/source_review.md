# M15-A independent source-basis audit

Date: 2026-10-30. Scope: read-only review of admitted source material, task, initial evidence/specification/decision, and the cached original primary article. No candidate, source packet, or frozen file was changed. No target records were opened; no generation or revision was run. This report audits provenance and what the evidence supports, not the numerical properties of the 128-row table.

## Finding

The table has a genuine published basis for its group-level marginal summaries. Its joint structure and individual urate values are constructed assumptions. Calling the whole table "supported by the paper" without this distinction would overstate the evidence. The builder did disclose this distinction accurately in its specification and decision record; no fabricated relationship citation was found in the inspected candidate.

Only one source was admitted. This is not yet an implementation test of combining different studies' relationship evidence.

## Original source and independent check

Yun et al. (2021), *Temporal relationship between body mass index and uric acid and their joint impact on blood pressure in children and adults: the Bogalusa Heart Study*. DOI: [10.1038/s41366-021-00810-9](https://doi.org/10.1038/s41366-021-00810-9); [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8236402/fullTextXML).

Cached original: `private/source/PMC8236402.fullText.xml`.

SHA-256: `f3f4c658fe8ef90fb92ebc283f0dc4ddf87d0af81c10b127b734e2ce10f608a3`.

Independent XML parsing matched **all 20 admitted estimates exactly** to Table 2's adult rows. The evidence file contains **zero relationship items**. Table 2 identifies its continuous entries as means and participant SDs, not standard errors. The four urate SDs are present in the original article but intentionally absent from the builder's approved excerpt and 20-item evidence file.

| Source stratum | Original n | Age mean / SD (years) | BMI mean / SD (kg/m2) | Admitted urate mean (mg/dL) |
|---|---:|---:|---:|---:|
| White male | 1012 | 36.9 / 11.0 | 28.6 / 6.0 | 6.1 |
| White female | 1209 | 37.1 / 10.9 | 28.0 / 7.4 | 4.5 |
| Black male | 509 | 34.3 / 11.5 | 28.2 / 7.3 | 6.2 |
| Black female | 672 | 35.1 / 11.8 | 31.4 / 8.7 | 4.6 |

The Methods, "Study cohort," describe 3,402 nondiabetic adults in Bogalusa, Louisiana, examined once in the combined adult cross-sectional cohort. The adult surveys span ages 20–56. "Measurements" describes repeat height/weight measurement for BMI and the Olympus AU-5000 uricase serum urate assay. These support the excerpt's population context, units, and measurement description.

## Support matrix

| Feature | Actual basis | Audit interpretation |
|---|---|---|
| Four race/sex stratum labels | Original Table 2 | Published descriptive labels; not causal mechanisms. |
| Age/BMI means and SDs; urate means | 20 original Table 2 values | Valid marginal construction targets. Matching them does not establish individual or joint validity. |
| Age 20–56 | Adult-survey age ranges, then task contract | Source-context bound. It does not identify the within-range density or age–urate relationship. |
| Exactly 128 rows and 38/46/19/25 allocation | Pilot/task design | Engineering allocation informed by source proportions; not a reported empirical sample. |
| BMI greater than zero; nonnegative urate; unique IDs; no missing values | Task schema | Admissibility checks, not scientific evidence of distributional accuracy. |
| Generally positive within-stratum BMI–urate ordering | `A_joint`; `joint_structure.evidence_ids=[]` | Agent-selected relation. Neither sign nor strength is supplied by the admitted packet. |
| Individual age/BMI/urate pairings | Manual construction | No source-level row correspondence or evidence that an individual's simulated value approximates a measurement. |
| Age dependence, curvature, interactions, conditional variance | No admitted relation evidence | Unidentified by the supplied marginal constraints. Manually mixing ages does not establish independence or a correct age effect. |
| Urate ranges: 4.2–8.0, 2.5–6.5, 4.3–8.1, 2.7–6.5 mg/dL | `A_urate`; `urate_dispersion.evidence_ids=[]` | Construction limits chosen by the Agent. They are not observed ranges, physiological limits, confidence intervals, or source dispersion estimates. |
| Integer ages and one-decimal BMI/urate | `A_marginals` | Authoring precision, not proof of the source measurement precision. |
| Symmetric pairs about group centers | `A_marginals` and initial decision | Declared construction artifact. Exact means may coexist with incorrect spread and dependence. |
| Nondiabetic eligibility | Source cohort description only | Intended source context. The fictional table lacks diagnosis/glucose/eligibility variables, so membership cannot be independently checked in its rows. |
| Population or clinical uncertainty | Not supplied/established | The 128 fictional rows do not add clinical observations or identify evidence/transport uncertainty. |

The supplied age and BMI SDs constrain individual marginal spread. They do not constrain conditional residual spread, study-to-study uncertainty, or the sampling uncertainty of source estimates. The evidence file correctly distinguishes participant dispersion from estimate uncertainty.

## Important distinction: the full paper contains more than the Agent received

The paper's Figure 2 and Statistical methods describe an adult BMI-to-urate component with standardized coefficient 0.322, adjusted for age, race, sex, smoking and alcohol. This is real published relationship evidence, but **it was not admitted to this builder or used in its registered construction record**. It cannot retrospectively become the provenance of an already authored table. Access in pretraining cannot be ruled out, but undocumented model knowledge is not an auditable extraction.

That standardized coefficient is also not numerically interchangeable with an unstandardized urate-on-BMI slope in mg/dL per kg/m2. The pilot's exploratory model omits smoking and alcohol, and the exact transformation/operator would need reconciliation before a quantitative comparison. Agreement in direction alone would not resolve these differences. The article's longitudinal cross-lagged effects use still another design and must not be treated as a cross-sectional raw slope.

Likewise, the four original urate SDs are withheld checks in this pilot. Their later availability to the evaluator does not make them constraints that the builder had satisfied or even seen. They should not be fed back to repair this frozen pilot under the old protocol.

## Consequence for interpretation and a later experiment

The evidence basis currently supports the statement: "A direct Agent authored a fictional table guided by 20 published marginal summaries and disclosed additional construction assumptions." It does not support: "The generated table's adjusted correlations, age effects, subgroup interactions, tails, or individual measurements were grounded in those 20 summaries."

The restrictive packet deliberately tested literal construction from marginal evidence. Therefore unsupported dependence in this pilot is partly an experimental-design limitation; it is not evidence that an unrestricted literature-enabled Agent cannot extract useful relationships. Conversely, the pilot cannot demonstrate the project's wider cross-study scientific-analysis claim.

A later, separately frozen experiment could admit a verified joint-evidence packet, with population, units, adjustment and transformation retained for each relation. It should reserve genuinely unused analyses or a new target for evaluation. Before invoking a relational claim, trace that claim either to an admitted, compatible source operator or to an explicit assumption with sensitivity analysis. Do not replace this distinction with a generic "literature-informed" label.

## Files inspected

- `visible/TASK.md`
- `visible/bundle/sources/U1_screened_excerpt.md`
- `visible/bundle/candidates/initial/evidence.json`
- `visible/bundle/candidates/initial/model_spec.json`
- `visible/bundle/candidates/initial/decision.md`
- `private/source/PMC8236402.fullText.xml`

No generated rows or empirical target records were needed for this source-provenance audit.
