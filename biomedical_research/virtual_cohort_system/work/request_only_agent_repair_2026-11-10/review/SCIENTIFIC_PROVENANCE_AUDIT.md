# Request-only repair pilot: source, process and scientific attribution audit

Scope: all four terminal episodes; immutable submissions, source text actually returned to authors, selected tables already cached by their gateway, and API/tool/execution receipts. No new literature searches, credentials, private reasoning interpretation, clinical-reference files, generated patient tables or author-program execution were used in this audit. The automated metadata report is `TOOL_SOURCE_COST_AUDIT.json/.md`.

## Completion, cost and the correct denominator

| Episode | API calls | Search actions / query requests | Full texts fetched | Submitted candidates / trials | Final disposition | Tariff estimate |
|---|---:|---:|---:|---:|---|---:|
| PNS ordinary | 21 | 12 / 12 | 4 | 1 / 1 | v001 selected; trial succeeded | $0.2112039 |
| PNS workflow | 20 | 13 / 12 | 2 | 1 / 0 | Input-byte limit; v001 unselected and untested | $0.2155262 |
| Lipid ordinary | 20 | 8 / 7 | 3 | 1 / 1 | v001 selected; trial succeeded | $0.1833251 |
| Lipid workflow | 24 | 8 / 8 | 6 | 0 / 0 | Model-call limit; no candidate | $0.2002798 |

Total: 85 API calls and $0.8103350 recorded tariff cost, with no unknown-usage call. Search actions and actual network queries differ because rejected queries can be screened before a request. All recorded model returns are `gpt-6.1-sol`.

Two of four episodes selected a generator. Three candidate artifacts exist, but the untested PNS workflow artifact is **not** a completed final submission and must not be silently promoted or added to the primary evaluated set. No author submitted a revision. Both selected programs passed their first fixed-seed trial; therefore neither needed the specification-wrapper repair observed in the previous pilot.

The repaired interface improves what is exposed per search, but does not by itself establish improved scientific accuracy or general workflow superiority. In this very small run both ordinary episodes finished and neither workflow episode did. That is a descriptive completion result, not a stable model/policy ranking.

## What the presentation repair changed

| Episode | Admitted unique titles | Complete titles exposed | Admitted unique PMCIDs | PMCIDs exposed | Returned metadata characters |
|---|---:|---:|---:|---:|---:|
| PNS ordinary | 53 | 51 | 35 | 33 | 73,685 |
| PNS workflow | 68 | 62 | 40 | 37 | 92,536 |
| Lipid ordinary | 36 | 34 | 33 | 31 | 52,383 |
| Lipid workflow | 47 | 43 | 43 | 39 | 67,046 |

These are literal exposure measures, not comprehension. Nearly all admitted titles became visible, whereas the original pilot's full-title counts were 10/35, 5/33, 6/29 and 4/12 respectively. The already completed offline replay, using identical saved hits, is the cleaner engineering comparison; the live authors chose different queries and sources.

Budget-related failures remain. The last sent PNS workflow request was 217,626 bytes, including 148,894 bytes of function outputs and 47,372 bytes of opaque encrypted strings. Its next request would have included the submitted program and notes and was rejected by the 250,000-byte limit. It did not get a subsequent execution/finalization turn. Lipid workflow consumed all 24 turns on eight searches and sixteen source reads; its last action requested another article's section index. Neither outcome should be described as a demonstrated failure of generated scientific relationships.

## PNS ordinary: direct external coefficients plus an assumed joint law

The selected generator adopts BMI slopes of 6.7/3.6 mmHg per 5 BMI units from Chen et al., [PMC4537884](https://pmc.ncbi.nlm.nih.gov/articles/PMC4537884/). The returned source text supports these numbers and units, distinguishes the waist-adjusted analysis, and describes the untreated rural Chinese analysis population. Thus these are genuinely reported numerical inputs rather than coefficients invented by the host. The article's erratum was also fetched; it concerns licensing, not numerical corrections.

The author uses ELSA-Brasil summaries from [PMC12622929](https://pmc.ncbi.nlm.nih.gov/articles/PMC12622929/) as loose anchors. The recorded female proportion, BMI mean/SD and BP mean/SD match the cached article. These source summaries do not identify the requested laboratory-substudy population. The generated age masses, sex gradient, BMI shape, BP intercepts, age functions and residual SDs remain author assumptions. A healthy Chinese age-pattern article, PMC6275465, is cited only qualitatively.

Key scientific choices and their consequences:

- The observed-source BMI slopes are transported from untreated Chinese adults with additional adjustments to a Brazilian all-treatment population analyzed with age and sex only. This bridge is acknowledged but not estimated.
- Person/visit BP innovations use a bivariate Student-t construction with 12 degrees of freedom, age-dependent scales and assumed latent correlation 0.65. Added reading-error SDs 4/3 mmHg and within-reading correlation 0.5 are also assumed.
- Two rounded readings are averaged. The final released target aggregation is unknown; reproducing an assumed two-reading measurement process does not establish its correctness.
- Joint BP rejection enforces broad bounds and pulse pressure at least 15 mmHg. BMI is also bounded and rounded. These transformations can change the final OLS slopes and residual correlation, so the declared coefficients are not exact predictions of those estimators.
- Nonlinear age terms and age-by-sex effects introduce another difference between structural slopes and the requested linear-age projections.

The model is a fully specified stochastic scenario with visible source/assumption distinctions. No retrieved study identifies its final joint residual covariance, demographic selection or treatment transfer.

## A source-exposure caveat in PNS ordinary

The author received an incidental excluded-family result despite the alias screen. `episodes/PNS_BASE/tool_actions/action_0016/result.json` contains the second full-text page of PMC12622929. Its discussion cites a nationally representative Brazilian adult survey's hypertension prevalence, 32.5% with CI 31.7–33.0. The cached article identifies that reference as Malta et al., *Prevalence of arterial hypertension according to different diagnostic criteria, National Health Survey*, DOI 10.1590/1980-549720180021.supl.1.

The indirect wording did not match the configured excluded aliases. The author expressly states that incidental survey comparisons were ignored, and no generator coefficient is visibly taken from that prevalence. Nevertheless, exposure and claimed use are different: this episode cannot be called completely unexposed to the excluded study family. The incident concerns an ancillary hypertension summary, not the held evaluation slopes or residual correlation; no target-reference files were read by this audit. Preserve this disclosure rather than asserting that screening proves independence or retroactively deleting the source page.

Exposure locator: PMC12622929 version 1, source XML SHA256 `3141047d0fe496bb6df4ac77bb8562868a462693973aefc5bcd84f3d9835d550`; actual returned tool-result SHA256 `795513a23eeda35adca9e6eaced8c49716fc510fdadb9c322ca780d48ba3a150`. The prevalence string begins 8,269 characters into the returned page, at character 18,269 in full source text. The source reference identifying the national survey is farther down the cached article and was verified by this audit; the author demonstrably saw the incidental prevalence passage, not necessarily that later bibliography entry. Its stated non-use appears in selected `candidates/v001/notes.json`, SHA256 `31dd60b2505d7bac345a611609c175076e7d602cad90aaea24842652b7aeb593`. This distinguishes cached content, actually shown text, and claimed use.

## PNS workflow: a submitted but untested cross-source derivation

The unselected v001 specification accurately copies sex-specific age, BMI and BP moments from the retrieved ELSA-Brasil Table 1 in [PMC7433850](https://pmc.ncbi.nlm.nih.gov/articles/PMC7433850/). It also reads the complete abstract of INTERSALT PMID 2180281 through `hit_0010_003`: the BMI partial correlations 0.215/0.229 match the abstract. The model correctly does not mislabel them as BP regression slopes or as SBP–DBP residual correlation. It recognizes that the accompanying INTERSALT publication uses overlapping participants.

Its proposed construction fits a discrete source-age distribution to reported moments, assigns age curves, decomposes marginal variance into age-related and residual terms, and derives a common BMI slope from a variance/partial-correlation bridge. This is a substantive Agent-authored numerical combination of sources, not an externally reported fitted model. It depends on assumed age functions, compatible moments, conditional homogeneity, and transfer from INTERSALT's broader adjustment set to the proposed age/sex conditioning. Nonlinear age residualization is not automatically identical to the reported partial-correlation operator.

The innovation correlation remains an explicit assumption of 0.65. Joint rejection and rounding may alter pre-rejection moment claims. Because the author never ran or finalized this candidate, this audit does not certify numerical solvability, output validity, exact moment replay or scientific usability. It documents a promising modeling attempt with an incomplete execution path, not a third successful deliverable.

## Lipid ordinary: a component construction with qualitative association evidence

The final generator uses HDL and positive non-HDL components and defines TC as their sum. Its source anchors are actually retrieved:

| Source | Verified use | What remains a modeling choice |
|---|---|---|
| Rural Kenyan study, [PMC6435188](https://pmc.ncbi.nlm.nih.gov/articles/PMC6435188/), Table 1 | Sex/group BMI and lipid means/SDs summarized in the notes match the table | Target group weights, generated group means, age distribution and transport are not estimated from that table |
| Tanzania/Uganda study, [PMC6897412](https://pmc.ncbi.nlm.nih.gov/articles/PMC6897412/), Tables 2/4 and methods sections | Residence differences and categorical LDL/HDL BMI associations match the cited statistics | Chosen continuous HDL/non-HDL log slopes are extrapolations, not extracted age/sex-adjusted TC slopes |

PMC7490939 was fetched but is not cited as a numerical parameter source in the final notes. Retrieval count should therefore not be equated with the number of studies constraining the generator.

The HDL and non-HDL log innovations are independent conditional on the modeled predictors; TC shares the HDL component. Therefore TC–HDL dependence is positive by construction even with innovation correlation zero. Additional dependence comes from latent lifestyle. This is a coherent component model and guarantees TC ≥ HDL without deleting records, but it does not estimate the requested residual correlation from evidence.

The chosen continuous log slopes, age/sex effects, mixture weights and component log-SDs are declared assumptions or approximate external-scale choices. TC is a sum of two lognormal components, so it is not itself a single lognormal variable. Raw-unit BMI effects vary with the covariates and component means; the log coefficients cannot be presented as fixed raw-unit OLS slopes. Gaussian innovations, including those used for BMI, are clipped at eight SDs. This is a nonidentity transformation and produces bounded support; no claim of an exactly unmodified lognormal law or exact source-SD replay is warranted.

## Lipid workflow: evidence search without a delivered model

This episode retrieved six full-text articles (PMC6747887, PMC6895384, PMC6897412, PMC7101029, PMC7347104 and PMC7579460), including section/table reads, and exhausted its call budget before submission. No parameter attribution or scientific output assessment is possible. Do not retrospectively infer a model from its source list, promote a narrative plan to a candidate, or replace the missing result with another episode's data.

## Findings that belong in the synthesis

1. Compact search cards materially improved evidence visibility, and direct specification pass-through worked on both tested submissions. These are observed interface outcomes.
2. Autonomous ordinary Agents selected distinct evidence, authored runnable models and completed both tasks. Neither required host scientific constants or a prepared paper packet.
3. Both completed models retain substantial unmeasured-dependence and transport assumptions. Their source fidelity must be separated from final analytical utility.
4. The workflow policy did not finish either task under this run's fixed limits. Source acquisition and model completion compete for the same turns and context, even when money is not the binding limit.
5. No scientific revision benefit was tested: there were no revisions. Final quality must be reported from the independent evaluation with both missing workflow outcomes retained.

The study now has a clearer separation between retrieval/interface usability, completed scientific construction, source support, and downstream data quality. These four levels should not be combined into one success label.
