# Repeated autonomous evidence-to-cohort construction

Completed 11 November 2026. This report closes the frozen request-only repeatability unit. All twelve sessions and all 36 final tables are retained. The original v0.29 manuscript, earlier experiments, new construction programs and launch receipts remain unchanged.

## Main finding

The economical GPT configuration repeatedly completed autonomous literature search, model construction, execution and final data delivery from a research request alone. This establishes operational repeatability in two existing biomedical contexts. Scientific usefulness remains analysis-specific: some blood-pressure associations approach the sample reference, while lipid dependence and HDL dispersion remain weaker in every new constructor. The organized workflow does not show an overall quality advantage over the equally capable ordinary Agent in this small developmental comparison.

Source-to-code review makes these outcomes interpretable. Agents used different external studies, converted reported statistics, selected conditional distributions and filled unidentified relationships with assumptions. The audit also found one generator whose continuous ideal law has an infinite raw total-cholesterol mean, despite successful finite-table execution. Traceability therefore has a concrete inspection use; faster review, automatic fault detection and validated analysis-confidence labels have not been demonstrated.

## What actually ran

| Item | Frozen design / observed outcome |
|---|---|
| Requests | Brazilian adult blood pressure; Turkana-context adult lipids |
| Input | Population and variable descriptions, desired analyses and output contract; no individual target data or prepared scientific evidence packet |
| Policies | Ordinary Agent and scientific workflow, both free to search, model, execute, check and revise |
| Model | `gpt-6.1-sol`, high reasoning, same shared capabilities and ceilings |
| Constructors | Two requests × two policies × three fresh sessions = 12 |
| Final repetitions | Three prescribed seeds × 3,000 rows per selected law |
| Delivery | 12/12 selected laws; 36/36 successful final tables; 108,000 fictional rows |
| Attempts and revisions | Twelve candidate submissions and twelve successful trials; all selected v001 |
| Model use | 331 received model calls; returned model identity recorded for every call |
| Retrieval | 127 provider queries; 54 episode-level full-text downloads, representing 36 distinct PMC IDs and 38 versions |
| Cost | USD3.9851613 known and accounted token-tariff cost; zero unknown-usage calls |

Download operations are not independent studies. The 108,000 rows are simulation output, not new participants or an increased clinical validation sample. Cost is not an invoice and excludes human review, infrastructure and unmetered browsing. The total allowance was USD48; no additional batch is launched by this report.

The shared scientific runtime, task requests and policy texts were byte-identical to the preceding capacity round. New orchestration registered repeats, enforced closure gates and updated conservative long-context cost accounting. Root did not supply scientific coefficients, select favorable papers for an arm or edit any generated scientific law. The first block received operational review only; all twelve sessions closed before final-table production and reference evaluation. See [protocol](PROTOCOL.md), [launch freeze](LAUNCH_FREEZE.json) and [independent closure review](review/INDEPENDENT_CLOSURE_REVIEW.json).

## Scientific results

Each constructor below is summarized across its three seeds. All individual estimates and dispersion/coherence diagnostics appear in [complete tables](AGGREGATE_TABLES.md), [primary figure](figures/primary_analyses.pdf) and [machine-readable analyses](ANALYSIS_RESULTS.csv). The ranges here span three constructor means per policy; they are not confidence intervals.

| Prespecified analysis | Ordinary Agent, range | Workflow, range | Existing sample reference |
|---|---:|---:|---:|
| BMI–SBP, mmHg per 5 BMI | 3.293–4.722 | 3.362–5.597 | 3.524 |
| BMI–DBP, mmHg per 5 BMI | 2.595–2.987 | 2.424–3.704 | 2.260 |
| SBP–DBP residual correlation | 0.611–0.669 | 0.616–0.783 | 0.717 |
| BMI–TC, mg/dL per 5 BMI | 8.829–14.615 | 8.810–13.337 | 5.683 |
| BMI–HDL, mg/dL per 5 BMI | −2.312 to −1.155 | −1.414 to −0.012 | −4.623 |
| TC–HDL residual correlation | 0.331–0.423 | 0.146–0.356 | 0.512 |

BMI coefficients adjust for linear age and recorded sex. Residual correlations adjust both outcomes for age, sex and BMI. These are associations, not intervention effects. Lipid units use the frozen 38.67 conversion. The six endpoints are analyses within two contexts, not six independent clinical tasks.

**Blood pressure.** Several generated associations have useful proximity to the existing sample reference, but the largest workflow slopes are substantially higher. Workflow improves the descriptive mean absolute reference difference for residual correlation and both marginal SD diagnostics; ordinary Agent is closer on the two primary BMI coefficients. One workflow residual correlation exceeds the reference, so universal dependence shrinkage is not supported.

**Lipids.** Across all six authors, residual correlation is 0.146–0.423 versus 0.512 and HDL SD is 11.38–13.18 versus 20.18 mg/dL. The near-zero workflow R2 HDL coefficient is retained. Workflow is closer on the mean absolute TC-coefficient difference; ordinary Agent is closer on HDL association and residual dependence. A broad reference interval for the TC coefficient includes zero: a point-estimate discrepancy is not proof of a population bias. The saved reference intervals are shown rather than replaced with post hoc success thresholds.

**Coherence.** One generated row has HDL > TC: workflow lipid R1, seed 54003, one of 3,000 rows in that table and one of 9,000 for that author. It is one of 54,000 lipid rows in this batch. The corresponding reference fraction is unavailable. No row was removed or repaired. All blood-pressure tables satisfy the evaluated SBP ≥ DBP condition.

**Policy interpretation.** Descriptively, workflow has the smaller mean absolute difference on two of the six primary endpoints and ordinary Agent on four. This is not a statistical win count or a task-general ranking. Both policies are valid autonomous implementations. All selected v001; there is no demonstrated scientific revision gain in this batch.

Reference values come from previously exposed project samples, not known population parameters or new independent holdouts. Blood-pressure uncertainty is conditional row-resampling stability, not a complex-survey interval; lipid coefficient uncertainty retains the saved HC3 convention. Overlap does not establish equivalence. PNS_BASE_R3 samples shared parameters per seed, so its spread includes scenario variability as well as individual sampling. Other eleven programs use fixed scientific parameters. Seeds never become extra independent constructors; see [seed interpretation](SEED_INTERPRETATION_ADDENDUM.md).

## What the Agent did scientifically

The [independent provenance audit](review/SCIENTIFIC_PROVENANCE_AUDIT.md) inspected captured original sources and all twelve frozen programs, with 36 requested-analysis maps and 48 candidate artifact hashes. It did not read the current reference evaluation or execute generators. Representative, verified choices include:

| Agent choice | Concrete implementation | Remaining scientific assumption |
|---|---|---|
| Derive blood-pressure covariance | One workflow uses reported SBP, DBP and pulse-pressure variances through Cov(S,D) = [Var(S)+Var(D)−Var(S−D)]/2, then a modeled covariate variance budget | Source subgroup moments, target covariate distribution and adjustment sets are not identical |
| Convert standardized lipid effects | Workflow lipid authors infer or assume BMI SD before converting source effects into physical units | IQR/mean shape assumptions, source-subset differences or a transported SD affect the adopted slope |
| Translate longitudinal dependence | Workflow lipid R1 combines random-intercept and error variances from a joint longitudinal model | Between-person correlation is not the same as raw single-visit or pooled residual correlation |
| Enforce a biochemical identity | Both R3 lipid authors independently construct TC from positive components | Their distinct component-dependence assumptions still leave the requested joint relationship unidentified |

These decisions demonstrate substantive Agent modeling, beyond a host-written formula with populated coefficients. They also show why “parameter has a citation” is insufficient: an accurate extraction may require an unvalidated operator or population bridge. The audit maps reported quantities, derived quantities and assumptions without converting these categories into validated confidence scores.

## A defect that finite-output checking missed

The uniform tail audit found **LIPID_BASE_R2** draws BMI as B = 12 + exp(Z), with nondegenerate Gaussian Z, and uses a TC conditional mean proportional to exp(cB), c > 0, without a cap. The positive moment-generating integral for this lognormal term diverges. Thus the ideal stochastic law has E(TC) = infinity. Finite tables still permit arithmetic regression/correlation calculations; successful execution does not establish the population moments required for their usual interpretation.

**LIPID_BASE_R1 is different:** the shipped code caps log values, so its actual law is bounded and has finite moments. Removing its caps would create the analogous divergence, but that is a counterfactual. The warranted concern is cap-dependent tail behavior, not an infinite mean in the shipped law. All twelve programs received the same static review; the remaining laws have finite positive moments or bounded returned outputs under their documented conditions.

This is an implementation/design defect separate from missing external evidence or population transport. Keep all outputs in the analysis. Do not infer a general workflow safety advantage from one ordinary-arm failure, and do not fix this frozen batch after seeing reference agreement. The finding motivates a generic law-level check for any future version, without encoding target coefficients.

## Inspection limits and reconciliation

One workflow PNS search received the title and a truncated abstract preview of a target-family paper, including approximately 1% ideal cardiovascular health prevalence. No explicit full-text fetch or literal candidate citation was observed for that hit; absence of a citation does not prove no influence. The preview did not provide the prespecified BMI coefficients or residual correlation. The author is retained and the exposure is recorded in the [adjudication](review/SOURCE_EXPOSURE_ADJUDICATION.json) and project registry. These runs cannot be described as perfectly screened or newly independent.

Independent checks passed: 10,564 execution/accounting checks, 3,449 saved-row recomputation checks and 115 closure/history checks. Every final table was recomputed using independent linear-algebra code; the maximum reported numerical difference was 9.06e−14. These establish result integrity, not scientific validity of every generated law.

An earlier manuscript transcription error was found: v0.29 line 878 reports the DBP SD reference as 10.757; the pinned snapshot and both evaluations correctly contain **11.09413727799307**. The correction for the next manuscript version is **11.094**. No underlying result changed. The old manuscript and its prior PASS receipt remain intact; see [reconciliation record](review/REFERENCE_VALUE_RECONCILIATION.json).

## Paper contribution and decision

Continue the paper around **autonomous construction of analyzable biomedical virtual data, with inspectable evidence and assumptions**. Use this complete repeatability study to substantiate that both policies can retrieve and construct a working cohort from a request, and use all analysis profiles to delimit where the resulting data are useful. Treat source-to-code traceability as an implemented audit capability. Neither superiority, calibrated trust, universal population fidelity nor feedback improvement is established.

The [manuscript insert](MANUSCRIPT_INSERT.md) gives ready-to-integrate English Methods, Results, Discussion and figure placement, plus the explicit v0.29 correction. It preserves the application story instead of replacing it with a universal failure headline.

Separately, [twelve traceability dossiers](../provenance_audit_materials_2026-11-11/README.md) from the earlier four-law capacity round have passed independent source/code and package checks. They support a future reviewer study. Human responses remain zero; the curated maps add audited interpretation and were not autonomously produced without human effort. Browser interactive/visual inspection of those HTML packets remains unverified because the requested Chrome surface blocked local-file navigation; no workaround was used.

**Bounded next decision:** integrate this evidence first. Before another paid model or task expansion, define a generic scientific-law review that checks support, moments, physiological identities and whether each requested analysis depends on unidentified covariance or scale. Apply it to frozen existing examples as an audit; do not repair and rescore them as new confirmation. A prospective correction comparison, second GPT configuration or extra glycemia request requires its own versioned question and protocol. None starts automatically here. No new cohort acquisition is needed to finish reporting this unit.

Public synchronization has not been performed in this unit. Local patient/generated rows, raw API captures and full source documents remain excluded from any prospective public export.
