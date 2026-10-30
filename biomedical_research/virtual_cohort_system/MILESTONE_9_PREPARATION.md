# M9 Preparation of two scientific analysis tasks

29 October 2026. Two public-data enrichment packages and their external evidence packets are now prepared. **No new scientific generator, target association analysis or method comparison has run.** This milestone prepares the previously proposed 30-table screen; it does not report its outcome.

| Task | Retained participants | Agent-visible covariates | Entirely hidden biomarker |
|---|---:|---|---|
| NHANES 2015–2016 | 1,961 | Age, sex, measured BMI, fasting glucose | Fasting insulin |
| Brazil PNS laboratory sample | 7,979 | Baseline age, sex, measured BMI | HbA1c |

The goal remains evidence-guided virtual data for downstream scientific analysis. These first tasks isolate unmeasured-variable enrichment; whole-cohort synthesis and missing-cell completion remain separate extensions. The experiment asks whether one frozen generation recipe supports multiple reserved analyses and whether structured evidence handling adds value over an equally informed ordinary Agent.

## Real data are prepared and separated

NHANES preparation acquired six official XPT files and codebooks, retained adults aged 20–79 with the specified morning/fasting eligibility, and excluded current insulin use. CDC's reported below-detection-limit fills are preserved. The visible table contains no insulin duplicate, insulin-derived measure, original SEQN or survey design field. A bounded historical inventory found prior 2017–2018 insulin use but no 2015–2016 insulin use within its inspected scope; it does not certify complete historical independence. [CDC insulin metadata](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2015/DataFiles/INS_I.htm).

PNS preparation acquired the official laboratory workbook and dictionary. The 8,952 laboratory records became 7,979 complete eligible records after age, measured anthropometry and availability checks. HbA1c `Z034`, its estimated-average-glucose derivative `Z035`, original worksheet linkage and laboratory weights are kept outside the builder package. No target magnitude trimming occurred. [Official PNS files](https://www.pns.icict.fiocruz.br/bases-de-dados/).

Both packages passed existing task/input contracts, serialized-input checks and exact preparation replay. Identifiers are opaque, with linkage material under local custody. This is procedural separation in a shared filesystem; it is not an access-control guarantee for every LLM tool or a claim of anonymization.

## External evidence was checked before admission

The source-only search produced seven primary papers, four for insulin and three for HbA1c. NHANES and PNS results were excluded from both construction packets. The initial proposals contained 155 numeric items. Independent controller review checked source tables, methods, units and recorded hashes; **137 items were admitted with interpretation restrictions**: 78 for insulin and 59 for HbA1c. Items and papers are not independent replications; overlapping Hoorn evidence and repeated Framingham observations remain linked.

Three concrete issues are preserved:

- **Conflicting source text:** SHIP Table 3 disagrees with the abstract/results paragraph for older-age HbA1c upper limits. All 18 extracted healthy-reference items in that family are withheld from numeric calibration pending resolution. The original proposal remains intact. [SHIP paper](https://doi.org/10.1186/s12902-019-0338-7).
- **Different adjustment:** Hoorn BMI coefficients condition on fasting/postload glucose, waist/hip and lifestyle. They cannot directly serve as BMI slopes for a model using only age, sex and BMI. Their signs and conditioning are retained. [Hoorn paper](https://doi.org/10.1371/journal.pone.0233769).
- **Different time horizon and scale:** DIRECT predicts later HbA1c with additional covariates; Framingham insulin coefficients use standardized log outcomes. These are restricted evidence contexts, not ready-to-copy target equations. [DIRECT](https://doi.org/10.1371/journal.pone.0171816), [Framingham](https://doi.org/10.1136/bmjdrc-2021-002581).

No packet fully identifies the target biomarker distribution from exactly the visible covariates. Residual variation, unmeasured covariate dependence, treatment mixtures and population transfer remain scientific choices for the generator. No target direction, slope or curvature was written into generation code; no generation code has been submitted yet.

This is a curated common-packet experiment. Preparing it does not demonstrate autonomous evidence retrieval by the future builder. Ordinary and structured Agents will receive identical admitted evidence bytes and numerical tools.

## Reserved analyses and implementation

Both tasks have the same four priority analysis types: adjusted age association, adjusted BMI association, BMI quadratic curvature, and a sex-by-BMI slope contrast. The insulin analyses use log insulin and additionally adjust log glucose; HbA1c analyses use percentage points. Secondary analyses retain all 18 prespecified age/sex/BMI cell means, including sparse or empty cells. Expected directions are unspecified.

An endpoint-to-evidence map distinguishes source-related transport from unreported conditional analyses and assumption-dependent curvature/interactions. Reproducing an age relationship already present in the source papers will not be labelled discovery of a previously unreported relationship.

The common point-estimation module uses identical calculations for future real and generated outcomes, strict record-ID alignment and explicit field/sex adapters. Seven invented-fixture tests passed, including positive and negative curvature, an interaction coefficient, global weight rescaling, unit conversion for the HOMA1 example, invalid inputs, row-order rejection and retention of empty cells. These tests establish implementation behavior, not scientific performance.

Independent review caught two integration details before use: both prepared tasks encode sex as strings rather than 1/2, and the linear HbA1c analysis must not silently introduce a positive-outcome selection rule. Both were corrected and the seven tests passed afterward.

HOMA1-IR is a secondary demonstration of a derived analytical use. It is calculated from insulin and glucose and is not a second independent biomarker validation. Some adjusted log-linear associations would be algebraically redundant and will not be counted twice.

## Important preparation findings

1. **PNS inference differs from NHANES.** The released laboratory workbook supplies `peso_lab` but no explicit PSU or stratum. This task therefore permits provided-weight point estimates and a predeclared unweighted sensitivity; it does not invent survey confidence intervals or automatically claim national representativeness. Baseline survey measurements and laboratory collection also have a time gap.
2. **The NHANES reader needed a reproducible repair.** The installed pandas XPORT decoder interpreted an all-zero IBM numeric encoding as a tiny positive value, preventing the correct morning-session selection. The custodian fixed only the exact raw zero encoding, verified invented encodings, retained failed attempts and replayed preparation exactly. Eligibility and outcome-dependent rules were not changed. No operating-system policy was bypassed when a native alternative was unavailable.
3. **Source heterogeneity is a real test condition.** Selected-healthy reference intervals, standardized associations and prospective models cannot all be pooled as if they were raw conditional coefficients for the target population. Whether a structured Agent handles this better is the next experiment, not a result already established here.

## What remains before the comparison

The visible inputs, admitted source packets, task contracts, prompts, analysis definitions and point-estimator code are available. The shared-bundle hashes and preparation checks are bound in the validation snapshot. Before launching the scheduled 30 final tables, finish four concrete items:

- Specify the conventional statistical family and its unidentified-parameter rule from source information only.
- Record the actual base-model settings and feasible resource accounting. The current harness does not enforce a token budget; fixed steps must not be described as proven equal token cost.
- Bind the existing isolated execution runtime to these tasks and freeze construction schedules and source-only selection rules.
- Complete and review the NHANES full-design variance adapter before reference inference. The generic point module is not a survey-variance implementation; the PNS point-only scope remains explicit.

All target analyses remain withheld. After these gates, run two independent constructions for each Agent method and one conventional fit per task, with three residual draws each. Retain failures, all constructions and every reserved endpoint. Do not select a favorable seed or tune on the reference after release.

See the [curated preparation package](reports/analysis_utility_preparation_2026-10-29/README.md) and the [research plan](docs/SCIENTIFIC_ANALYSIS_UTILITY_PLAN.md). Full source papers, participant covariates, hidden biomarkers and linkage keys remain local and are excluded from the curated package. No HPC allocation or model training was used.
