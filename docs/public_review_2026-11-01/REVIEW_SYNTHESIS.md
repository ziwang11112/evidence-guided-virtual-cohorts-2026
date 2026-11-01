# Public release and independent model review — 1 November 2026

Status: publicization and three website submissions complete; two full reviews received and adjudicated. Claude reported a completed document, but its contents could not be retrieved. This file records a review of fixed scientific snapshot `7f4b38c0c0dfa8da4bbd8df3d5ee754399600562`, not new validation of the method or a three-review consensus.

## Scope and delivery

The user authorized making the curated repository public and seeking independent reviews through the already logged-in ChatGPT, Claude and Gemini websites in the designated Chrome profile. Public visibility was verified through GitHub metadata and a separate browser account. The active README was updated; frozen scientific files and historical reports were not rewritten.

Before publication, a bounded audit examined 6,109 tracked files, 43 reachable commits and 3,770 unique file blobs. No actual credentials, excluded biomedical participant tables or full third-party papers were identified. This is not a guarantee of absence or a licensing warranty. Computational integration inputs constructed from published summaries and explicitly invented engineering fixtures are distinguished from participant records. See [audit summary](PUBLICATION_AUDIT_SUMMARY.md).

All providers received the same common review prompt, 12 complete document files and 11 complete implementation/specification/interface files. The 23 embedded files were verified byte-for-byte against the fixed Git commit. The public repository allowed deeper inspection. No participant-level or generated biomedical rows were uploaded. Each reviewer was asked to disclose what it actually read or executed. The displayed model labels were ChatGPT **Pro**, Claude **Opus 5.5 / highest effort**, and Gemini **Ultra Model Firefly**; these are observed interface labels, not independently verified backend identifiers.

The conversations were separate and other providers' opinions were not supplied. Existing account memory/personalization was not reset. This is independent advice collection, not a blinded model benchmark. Reviewers' self-reported execution coverage is not automatically a root-verified test record.

## Reviewer comparison

| Provider | Actual received artifact and reported scope | Main advice | Adjudication |
|---|---|---|---|
| ChatGPT | Complete response; reports fixed-file hash checks, selected source-check tests and aggregate arithmetic, plus primary-source inspection | Continue with a prospective test of which analyses a frozen whole-cohort release supports; compare marginal evidence with an added joint-evidence block | Useful and closest to the user's research aim. Its regression-role/filter counterexamples were independently reproduced using metadata only. Proposed cohort, tolerances and run budget are not yet an admitted protocol. |
| Gemini | Complete rendered response; reports static reading of attachments, no executed tests | Rank feasibility/identification limits first, an evaluation framework second, adaptive source-conditioned generation third | Useful sensitivity/portability advice, but several material overstatements require correction; see below. Fresh external verification is not substantiated by its captured citations. |
| Claude | Reported a completed Claude Docs artifact; original final reply and source list received, document body unavailable | Not attributed: the final assessment could not be read | Preview remained loading. A delivery-only request for the final document text was blocked by the provider. No complete Claude assessment is synthesized or reconstructed from work-in-progress messages. |

Read the complete captured [ChatGPT review](responses/CHATGPT_REVIEW.md), [Gemini review](responses/GEMINI_REVIEW.txt), and [Claude delivery status](responses/CLAUDE_DELIVERY_STATUS.md). These are external model opinions with separate coordinator checks. Claude's original chat and document remain available in the user's designated Chrome session. Recovering the document through the provider's normal interface is the only outstanding review-delivery item; no safeguard bypass was attempted.

## What the review changes

The central objective remains **useful virtual biomedical data generated from published external evidence and a specified target population**, including whole cohorts with no individual inputs. Enrichment and missing-cell completion remain separate optional information regimes. An ordinary scientific Agent with deterministic tools is a valid implementation. No review establishes a need for more Agents, a new model, model training, or a mandatory superiority contest against another Agent.

The strongest next paper question is whether one frozen generated dataset can support several prespecified scientific analyses, and whether the evidence and assumptions available before target disclosure explain the analyses it can and cannot support. This extends the original data-generation purpose; it does not replace the project with an audit-only software package.

Three plausible storylines remain conditional:

1. **Evidence-guided virtual cohorts for reusable biomedical analyses.** Main route: establish bounded usefulness in a genuinely new, independently held reference case. Distinguish directly supported, algebraically implied and assumption-dependent analyses. Existing M17-B and ENSANUT results are development evidence from earlier versions, not prospective validation of core v0.
2. **Multiple compatible cohorts and the value of missing joint evidence.** A supporting extension: expose how equally source-compatible structures change downstream answers, and whether one independently justified evidence block narrows that uncertainty usefully. Two chosen scenarios are sensitivity examples, not proven identification bounds or calibrated uncertainty intervals.
3. **Study-conditioned evidence translation and revision.** A more demanding methods route: implement only the needed population/measurement operators, then demonstrate a measurable benefit under equal information and budgets. Existing retention-only runs and C4's identical selections do not support this benefit yet.

A defensible working title for the first route is *Evidence-Guided Virtual Biomedical Cohorts for Reusable Scientific Analysis*. A more question-driven title is *Which Analyses Transfer? Building Virtual Biomedical Cohorts from Published Summary Evidence*. These are proposals, not a decision that the method is publication-ready.

## Findings accepted, qualified or rejected

**Accepted implementation finding.** The generic source metadata validator can accept the wrong regression coefficient term, reversed outcome/exposure roles, or omitted source filtering while calling the check aligned. The independent probe used only metadata, not biomedical records. This is a semantic binding gap, not a demonstrated arithmetic error in OLS. It matters because a statistically correct calculation can answer the wrong source question. See [ChatGPT adjudication](responses/CHATGPT_ADJUDICATION.md) and its counterexample record.

**Qualified implementation findings.** Identity-only whole-cohort feedback and machine-specific runtime configuration are real limitations. The frozen F1 integration already provides additional recipe, lineage, authentic-feedback, retained-byte and execution-count checks. Library weaknesses do not retrospectively prove an unguarded F1 failure, forged feedback or sandbox escape. Historical bytes remain frozen; fixes need a new scoped version.

**Accepted reproducibility finding.** Claude's in-progress inspection prompted a separate static check of the README audit entrypoint. The legacy global audit covers 1,693 allowed paths through M10, whereas the reviewed scientific snapshot has 6,109 tracked files. It would flag 4,416 later paths as out of scope and overwrite historical audit outputs. The active README guidance has been corrected; the old audit script and receipts remain intact. This is stale audit scope, not evidence of corrupted science or a failed publication-content inspection. See [entrypoint check](responses/AUDIT_ENTRYPOINT_CHECK.md).

**Rejected scientific attribution.** Gemini's characterization of C3 as demonstrated target negative transfer is incorrect: C3 evaluated source-side constraints and unused simulation seeds, not a new real target. Its claim that marginal drift is the proven chief bottleneck is also untested. C4-B is deliberately underidentified, so it cannot be grouped with fully identified Gaussian fixtures. Preserve the valid evidence-limit argument without these incorrect details. See [Gemini adjudication](responses/GEMINI_ADJUDICATION.md).

**Qualified novelty advice.** A focused primary-source check confirms KMGen (MLHC 2026), the Cossio/Gilardino ISPOR 2026 case study, and Bonofiglio et al.'s statistical synthesis work as genuine relevant predecessors. The broad sequence of literature extraction, program construction and synthetic data generation is not itself a defensible novelty claim. The untested opportunity concerns heterogeneous external evidence, target applicability and reusable analyses. The focused check does not establish priority or exhaust the literature; see [primary-source check](responses/PRIMARY_SOURCE_CHECK.md).

## Smallest useful next work, not automatically executed

First repair and independently test the source-statistic semantic contract: outcome, exposure, coefficient, adjustment set, population filter, event/denominator, unit/transform, weight and measurement definition. Preserve the old frozen integration and demonstrate the counterexamples are rejected in a new version. Add only the operators needed for the next admitted case.

Next complete one bounded case admission before inspecting target effects. CHNS is a candidate, not an acquired or approved case. Review exposure at the relationship/equivalent-estimand level, verify access and measurements, and establish an independent reference with appropriate precision. A model's suggestion to download or use CHNS does not satisfy those gates.

For a feasible case, a prespecified E0/E1 information ablation is promising: E0 uses an intentionally restricted approved marginal-evidence package; E1 adds one independently justified joint-evidence block. E0 does not represent all evidence that might be available. Hold other inputs, construction budget and evaluation fixed; each arm produces its own single frozen release used for approximately three analyses. This tests added evidence under the declared construction procedure, not a pure evidence effect independent of the generator or an Agent advantage. A claim of algorithmic superiority would additionally require a competent same-information statistical alternative. Do not confuse the two questions.

Before freezing, specify scientifically meaningful error tolerances or report errors without inventing equivalence; distinguish source uncertainty, model/transport scenarios, reference uncertainty and Monte Carlo variation. Count every structural-sensitivity execution in the budget. For joint-event proportions, preserve the intended denominator rather than silently conditioning on one event. Failed runs and unfavorable analyses remain in the final record. No target-directed regeneration follows disclosure.

The current package does not establish Nature Communications-level generality or a superior generator. Venue recommendations are conditional reviewer opinions. A rigorous bounded feasibility study, a validated methods contribution and a strong comparative algorithm paper require different evidence; the next experiment should determine the justified claim before the venue is fixed.

## Work performed in this review unit

Publication audit and visibility change; same-input website review submission and capture; public-record and primary-source checks; an independent metadata-only implementation probe; and documentation. No new biomedical target was downloaded, no patient/generated table uploaded, no generator or calibration rerun, and no revealed target retuned by the local coordinator. No training, HPC, paid API or new recurring automation was started. Provider-reported remote testing is documented separately from local verification.
