# Next real case: evidence admission and pilot decision

30 October 2026. Status: literature and metadata screening completed; no new real-data generation or target evaluation. This is a preparation decision, not an M13 results report.

## Decision

Prioritize **enriching an unmeasured whole-body fat percentage from ordinary anthropometry**. Keep serum urate as a backup rather than launching both cases. Body composition connects the method to a concrete use: inexpensive measurements are available, but a more involved body-composition examination is missing.

There is enough evidence to prepare a bounded **cross-study transport pilot**, with explicit assumptions. There is not enough evidence to claim that all source and target DXA measurements are interchangeable, that the complete joint distribution is identified, or that general obesity populations are already covered. A missing measurement bridge blocks a measurement-equivalence claim; it does not make an honestly labelled transfer experiment meaningless.

The proposed case remains in preparation. Its machine-readable contract, screened source artifacts, evaluator, budgets and release rules are not yet frozen. No target score has influenced this choice.

## What this screening established

| Candidate | Evidence available | Main unresolved issue | Decision |
|---|---|---|---|
| Whole-body fat percentage | External age/sex/BMI equations, source group moments and selected correlations; documented public NHANES DXA component | Scanner/software differences; source population selection; unreported covariate dependence | First preparation priority; explicit transport assumptions required |
| Serum urate | Independent US Bogalusa summaries and adjusted associations; several Asian cohorts | Standardization/adjustment differences, treatment selections and conditional dispersion | Backup; no broad-population calibration package yet |
| CRP | External body-composition associations in Dallas Heart Study | Capped measurements and additional fat-depot covariates do not match a simple BMI-only case | Do not add a third pilot now |

The full screening notes are retained in `work/m13/` and curated alongside this document under `reports/m13_admission_2026-10-30/`. They distinguish exact extractions, assumptions, retrieval failures and incidental target-related exposure.

## Source package to prepare

**Pongchaiyakul 2005** provides a tractable first source context: rural Thai adults, Lunar DXA, sex-specific summaries and an age/BMI/sex equation. Its development and validation subsets must remain separate. The reported cohort contained no participants with BMI at least 30, so it cannot alone anchor obesity-tail claims. A text/table inconsistency in the mean prediction difference must be excluded from numerical calibration. [Primary article, Tables 1–4 and predictive-equation results](https://onlinelibrary.wiley.com/doi/full/10.1038/oby.2005.82).

**Gallagher 2000** supplies a different DXA equation with inverse BMI and interactions, from a healthy convenience sample across US, UK and Japanese sites with BMI at most 35. It supplies alternative structural evidence, not proof that the Thai equation should be averaged into a universal model. Ethnicity, site and measurement must stay attached to the evidence. The DXA and four-compartment equations are distinct. [Original article, pp. 694–701](https://zakboekdietetiek.nl/wp-content/uploads/2015/11/Am-J-Clin-Nutr-2000-Gallagher-694-701.pdf).

**Urate fallback:** Bogalusa 2021 improves on the earlier candidate sources, but its standardized association and subgroup SDs do not directly identify a conditional generative model. The related Bogalusa 2014 paper uses a reverse regression and overlapping participants. Keep those distinctions; do not invert a regression slope or count overlapping papers as independent replication. [2021 primary paper](https://www.nature.com/articles/s41366-021-00810-9), [2014 primary paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0089696).

Source covariate-only simulations will be approximations when individual source covariates are unavailable. Marginal age/BMI summaries do not establish their dependence. The Agent may propose a small, fixed set of dependence and residual models with reasons; the controller must not silently assume independence or convert a marginal outcome SD into residual SD. Report source checks as approximate where appropriate. Do not make perfect source-data recovery a prerequisite for studying an evidence-limited method.

## Measurement and population boundaries

The candidate target is NHANES 2017–2018 `DXX_J`, outcome **`DXDTOPF`**. Its documented BCA processing reallocates 5% of lean mass to fat mass. This is not an instruction to add five percentage points to published fat percentages, nor a justified Lunar-to-Hologic conversion. Device and software differences remain explicit transport assumptions unless independently bridged. [Official documentation, Protocol and Data Processing](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm).

Proposed primary scope: adults aged 20–59 with valid total-body scans and complete allowed anthropometry. Begin with a BMI range supported by the selected sources; a Thai-only source package cannot claim BMI≥30 coverage. If Gallagher is admitted, BMI 30–35 should be reported as a distinct transfer domain. Final limits, ancestry treatment and exclusions must be set before outcome access. Source replay must retain each source's original age support, even when the target is narrower.

NHANES scan validity depends on body size and age. The first estimand is therefore the declared valid-scan domain, not all adults. Use the cycle's examination weights and design variables with a prespecified survey-domain/missingness approach. No adult analytic sample size has been computed. [DXA eligibility/analytic notes](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm), [demographic design variables](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm).

The same survey cycle and some covariates have been used previously. This can be a new-outcome evaluation; it is not a wholly untouched participant cohort. Search snippets also exposed target-related literature. Use a fresh builder context and a screened source packet, and disclose the reconnaissance exposure rather than claiming ignorance of all target-related knowledge.

## Minimal scientific experiment

1. **Prepare one contract.** Custodian fixes endpoint, target population, allowed covariates, source roles, analysis definitions and exposure record. Age, sex and BMI are the starting observed variables. Additional covariates require an explicit scientific reason and source support before freezing, not after seeing failures.
2. **Build from evidence.** Two independently instantiated builder turns interpret the same screened sources and propose stochastic generators. They must specify conditional location, individual dispersion, population differences and unresolved measurement assumptions separately. The controller supplies tools and checks, not the biomedical coefficients or the preferred functional form.
3. **Run the existing source loop.** Apply the same declared source operators before and after a bounded revision opportunity. Let the Agent retain a structure when revision is unsupported. Preserve both versions, all failed checks and changes in assumptions. Incomplete evidence is not repaired by silently changing the source context.
4. **Freeze before evaluation.** Fix at most two retained scientific scenarios per construction and three residual draws per scenario, yielding at most twelve final target tables. The exact calibration, retrieval and revision budgets are still to be recorded in the executable contract. Simulation repeats are not independent clinical datasets.
5. **Evaluate one reusable release.** Run identical analyses on the frozen generated tables and measured target, through a separate custodian. No endpoint-specific regeneration. Return all scheduled analyses together after freeze, not a sequence of answers used to tune the same target.

The whole DXA measurement family must be withheld from the builder: total/regional fat and lean mass, total mass, subtotal percentages and related derived values can reveal or closely proxy the hidden outcome. A whitelist is safer than deleting only `DXDTOPF`. Eligibility flags stay with the custodian; participant rows stay local.

### Analyses and interpretation

| Layer | Planned question | What a positive result would establish |
|---|---|---|
| Source replay | Does the stochastic model reproduce the admitted source statistics under declared source conditions? | Correct use of constraints, subject to source-context approximation |
| Target transfer | Do sex-specific age/BMI associations and response shapes carry to the reserved target? | Utility for those relationships in that target domain |
| Unfitted reuse | Do the same data support conditional quantiles/spread across fixed BMI/age strata that were not fitting targets? | Additional analytical usefulness beyond matching a source conditional mean |
| Sensitivity | Do useful conclusions persist across the few declared source-dependence/residual assumptions? | Limited robustness to those assumptions, not calibrated uncertainty for all unknowns |

The evaluator must operationalize this panel before running it: formulas, contrasts, strata, sparse-cell handling and uncertainty calculations. Reproducing a positive sign is encouraging, but also report effect magnitude, shape and reference uncertainty. Absolute means and thresholds remain interpretable as measurement-inclusive transfer results; without a validated bridge, differences cannot be attributed uniquely to the Agent. Do not invent a correction to improve a target score.

Generated rows and extra draws do not enlarge the underlying biomedical evidence base. Separate conditional simulation variation, between-generator/scenario variation and uncertainty of the measured reference. Do not label repeated-draw intervals as calibrated multiple-imputation or transport intervals without a justified inferential procedure.

### Small reference comparison

Use a published equation as an inexpensive contextual reference; also retain an explicitly documented stochastic version if feasible. It answers whether the proposed virtual data contribute beyond an already available conditional mean. This is not an ordinary-Agent superiority requirement and not a broad synthetic-data leaderboard. If the Agent merely copies an equation and adds noise, describe that as an implementation/reference result rather than new methodology.

## Continue and stop rules

- Proceed to the source-only build when the source packet and the provisional measurement assumptions can be represented faithfully. Unknown joint dependence can be investigated with labelled scenarios; it must not be sold as recovered fact.
- Proceed to target evaluation only after a technical/statistical audit of the frozen protocol and generator outputs. The audit may correct an implementation error without seeing target answers.
- If only a known direction survives while scientifically useful magnitudes or conditional behaviour fail, retain the negative result and narrow the supported use. Do not count it as general validation.
- If useful conclusions change across equally supported assumptions, report that limitation and identify the missing evidence. Any next improvement needs external evidence and a new reserved task; do not optimize repeatedly against this target.
- If the case becomes only a scanner comparison or cannot support any meaningful unprovided analysis, stop this pilot and revisit the narrower Bogalusa-like urate candidate. Do not enlarge the framework merely to avoid a scientific failure.

## What was actually done in this step

Completed parallel source reviews and a metadata/code exposure audit. Identified usable external body-composition evidence, a measurement mismatch, a source-support restriction and deterministic leakage paths. No participant-level data were read, no new target outcome file was downloaded, no model was generated or calibrated, and no target relationship was evaluated. Existing generators, frozen experiments and the M12 engineering results remain unchanged.

The immediate next deliverable is **one screened body-composition source packet and a frozen pilot protocol**, followed by the first source-only Agent construction. This screening has not demonstrated new biomedical performance.
