# M15-B scientific design review: literature-enabled virtual data

30 October 2026. Design review only. No literature search, data acquisition, generation, target analysis, or change to a historical protocol was performed for this review.

## Decision

Allow the scientific Agent to search and read approved original papers, use their available distributions and relationships, and seek additional evidence when a desired analysis depends on an unresolved assumption. Full use of source SDs is appropriate. Artificially hiding a statistic in an otherwise available source is not necessary to demonstrate useful data generation.

The distinction to preserve is the role of a result: reproducing an input is a source-consistency check; reproducing a relation in an independent target is transport evidence; supporting analyses not used as construction constraints is evidence of analytical reuse. A source-informed relation can validly be tested in a different target. It need not be absent from every source to count as target validation.

M15-A establishes neither the success nor failure of this fuller capability. Its packet contained only 20 marginal moments and prohibited retrieval. A new task should replace that restriction prospectively, without repairing or relabeling the old table.

## Primary question

Can a literature-enabled Agent produce one frozen, usable analytical data release from incomplete observed data and heterogeneous published evidence, such that several compatible analyses on that release agree usefully with measured-data analyses?

The main deliverable is data with provenance and an explicit applicability statement. It is not an Agent leaderboard, a citation-count score, or an optimization score. More Agents are optional. No superiority claim is required for the next feasibility case.

## Minimum informative next case

Choose one clinical panel using metadata, evidence availability, measurement compatibility and exposure history before inspecting its outcome values. Urate is a candidate, not a compulsory choice. Do not reopen the exposed M13-B body-fat target as independent confirmation.

The minimal case has age, sex and an anthropometric variable plus one genuinely measured biomarker that can be hidden for evaluation. A second biological variable is useful only if it enables a specific reusable analysis and has a defensible evidence link. Avoid adding many columns merely to increase output width.

Prefer one entirely unmeasured-column enrichment task for the first scientific validation because preserving actual covariates separates biomarker construction from the problem of inventing a full covariate distribution. Direct Agent output remains the primary implementation route: the Agent writes the missing biomarker values, while tools calculate evidence and diagnostics. If the selected task instead emphasizes whole-cohort expansion, freeze that choice before construction and provide enough target population/covariate information to make the joint-covariate assumptions explicit. These modes are both legitimate but should not be pooled into one claim.

Case admission should require at least one usable relationship object relevant to the primary analysis and a distributional anchor appropriate to the source or target question, with unresolved transfer assumptions recorded. This is not a requirement that every relationship or coefficient be known. A complex adjusted effect with unavailable covariates may remain a qualitative clue, be used through an explicit integration model, or support a sensitivity construction. It must not silently become a simple conditional slope.

Do not impose a relationship sign, Gaussian residuals, exact symmetry, artificial monotonic row sorting, a fixed scientific formula, or the old table's values. The Agent chooses a construction using admitted evidence and declared assumptions.

## Evidence workflow

1. Give the Agent the scientific use, target population description, variable dictionary, permitted covariates, output mode and tools. It first identifies the statistical information needed for the intended analyses.
2. Allow neutral, gap-directed searches and original full-text/table retrieval. Do not restrict the initial information to a few marginal moments. Give it access to complete admitted source statistics, including SDs and appropriate relationships.
3. Record each paper's cohort, time period, selection, measurements, units, transformations, adjustment set, overlap and relevant original locations. Distinguish reported quantities, reproducible derivations and construction assumptions. An article being relevant does not make every statistical quantity numerically portable.
4. Classify evidence as quantitative constraint, qualitative structural clue, conflicting/incompatible evidence, or unresolved. Do not discard contrary evidence merely because it worsens a source-fit score.
5. Let the Agent generate directly, review deterministic source diagnostics, and either revise, supplement evidence, retain, deliver sensitivity alternatives, or report insufficient evidence for a particular use.
6. Freeze the selected release before evaluating the reserved measured data. Apply every planned analysis to the same release. No endpoint-specific regeneration after seeing its reference result.

There is no scientific reason to ban calculators or diagnostic statistics. Tools may compute source operators and diagnostics. For a direct-row claim, provenance must still distinguish literal Agent-authored values from values populated by a sampler, optimizer, rescaling script or other program. A mixed or program-assisted route is acceptable if labeled honestly; it is not evidence of literal direct authorship.

## Evidence exposure and evaluation roles

Maintain an exposure ledger during the build, not only a list of accepted citations. Suggested fields are artifact hash/version, retrieval time, cohort and population, statistic/analysis involved, whether the content was visible, whether it was used, overlap status, and resulting evaluation role.

All visible content can influence the builder even if it is absent from its final citation list. A same-paper statistic found during retrieval becomes source-exposed; it is no longer a blind same-source check. It may still be a source-consistency endpoint. Do not suppress useful input merely to preserve an artificial blind score.

Source studies that use the actual reserved target cohort or overlapping participants cannot serve as independent external evidence for those target analyses. A paper that merely cites the target cohort is not automatically overlapping evidence; verify the underlying data source. Use metadata screening before full-text delivery when available. If a target answer is encountered incidentally, preserve the exposure record, classify the affected endpoint as exposed/development, and continue honestly within the bounded task. Do not erase the incident or automatically abandon every unaffected endpoint. If the primary target endpoint was exposed, obtain fresh confirmation later rather than claiming this run remained independent.

An outcome variable or analysis being absent from the prompt does not establish blinding. File separation also cannot rule out pretraining knowledge. State the actual procedural protections and their limits.

Before reference access, assign each endpoint a role:

| Role | What is tested | Interpretation |
|---|---|---|
| Source consistency | Original statistic, with its original operator and source context | Checks use of available evidence; not independent utility. |
| Target transport | Comparable relation or distribution in a nonoverlapping target | Tests whether the construction transfers; the same relation may be present in source evidence. |
| Analytical reuse | A prespecified compatible analysis not used as a fitting or selection target | Tests additional use of one release; disclose any qualitative prior evidence. |
| Exploratory sensitivity | An unanchored relation or alternative plausible structure | Describes assumption dependence, not a confirmed finding. |

Avoid claiming an analysis is fully unknown merely because its exact coefficient was not fitted. The ledger should distinguish unseen target values, source-informed signs or structures, and directly constrained quantities.

## Meaning of expansion

| Starting information | Permitted expansion | Claim boundary |
|---|---|---|
| Ten reported summaries, potentially estimated from a large cohort | Generate a larger virtual table | Number of summaries is not the clinical sample size; unknown joint structure still needs evidence or assumptions. |
| Ten measured people | Generate 100 fictional people or augmentation scenarios | Additional rows do not create 90 new independent empirical observations. |
| Ten observed variables | Add supported unmeasured variables using other studies | Evaluate the new variables jointly with existing ones; plausible marginals alone are insufficient. |
| Existing observed participants | Fill a wholly unmeasured column | Preserve rows and observed cells; do not call adding duplicate participants enrichment. |

Row count is a delivery requirement, not an accuracy metric. A later 100-versus-1,000-row check can study analytical stability and authoring consistency under the same evidence and construction. It cannot prove increased clinical information or independent biological replication. In the immediate case, select one practical count or fixed target covariate subset before construction, based on tool capacity and the analysis design, not outcome favorability.

## Small evaluation plan with scientific meaning

Select approximately four to six analysis objects after reviewing source and target metadata but before any target result is available. Use the same definitions, units, transformations, eligibility and applicable survey design for measured and generated data.

- One primary adjusted biomarker association with a prespecified covariate set and effect scale.
- A second association or age relation relevant to the scientific use.
- One curve contrast or subgroup interaction if estimable and substantively meaningful; do not require a sign when the real-data evidence is inconclusive.
- One reuse analysis not used as a fitting/selection target, such as a conditional relation involving a bridging variable or a subgroup contrast. If retrieval exposes it, update its role before evaluation and report that limitation rather than inventing a new favorable endpoint afterward.
- One or two distributional checks that affect those analyses, such as subgroup spread, an appropriate tail quantile, or threshold prevalence. Distribution checks are supportive diagnostics, not the whole definition of usefulness.

Report real and generated effect estimates in interpretable units, absolute differences, curve/subgroup patterns, and real-reference uncertainty. Use a scientifically justified practical tolerance when one can be set without target outcomes; if not, report estimates transparently without inventing a universal pass threshold. Correlation sign agreement and p-value agreement alone are inadequate. Do not treat a generated-data confidence interval as clinical precision created by fictional rows. Intervals or scenarios need an explicit interpretation separating source, model, transport and realization uncertainty.

The absence of an individual-level match is not automatically failure: this task concerns population analytical use. Conversely, a table that reproduces one relation but creates unsupported certainty or distorts another relevant relation has a restricted use, not general validity.

## Bounded pilot and stopping proposal

Recommended next unit: one admitted case, one scientific Agent construction, complete source access, up to two source-feedback revisions, and one final measured-data evaluation. Initial and intermediate candidates remain frozen. One construction can establish a traceable instance, not robustness across Agents, populations or random realizations.

For a practical initial budget, consider up to 12 query actions and up to eight original full-text fetches in one session, counting failures and fetch-related searches according to the actual adapter. These are engineering limits, not scientifically optimal amounts. The parent/controller must reconcile them with implemented tool accounting before execution. This review does not itself start or authorize a new run.

Stop source-directed revision when there is no specific new evidence-based change, the declared budget is exhausted, or the remaining alternatives cannot be distinguished by accessible evidence. Retention is valid. Missing evidence can yield an explicitly limited data release or sensitivity alternatives rather than a compulsory total task failure. Do not force a revision merely to demonstrate a loop.

Before reference evaluation, verify the source extraction of the few quantities that determine the primary construction, the actual evidence exposure record, the identity of the released data, and the analysis plan. Evaluate every prespecified endpoint once. If the target utility is poor, retain the result and diagnose the failure; further changes belong to development and need a new confirmation task. Do not search successive targets for a favorable result.

Do not add a baseline solely to complete a paper template. A feasibility report can first establish a valid evidence-to-data-to-analysis chain. Later claims that retrieval, source-condition handling or revision improves results require a comparison that isolates that claimed component; an extra-paper comparison primarily measures added information and its use, not algorithm superiority.

## Review conclusion

The needed correction is broader information access with stronger accounting of how evidence is used, not more restrictions on usable source statistics. The key next experiment is a complete, bounded scientific-use case with honest source/target distinctions. The current framework should not be expanded into a large benchmark or additional model training before that case has supplied a meaningful result.
