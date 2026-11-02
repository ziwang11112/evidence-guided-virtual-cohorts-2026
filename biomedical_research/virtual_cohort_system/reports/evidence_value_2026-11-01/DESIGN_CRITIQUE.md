# Bounded evidence-to-generator responsiveness pilot: independent design critique

Status: recommendation for custodian/protocol review, **not a frozen protocol or execution authorization**. Reviewer: `/root/chns_f2_review`. This note follows the coordinator's explicit scope revision to four packets, one fresh constructor per packet and three fixed output seeds: **12 Agent-generated tables maximum**. It supersedes the initial discussion of three tiers with two constructors per tier. No data, candidates, fixture rows or tests were generated for this note; no downloads or schedule changes occurred.

## Why this is worth a small test, and what would be redundant

The completed C3 study showed source-calibration tradeoffs, including worse unused-seed analytical compatibility after lower fitting loss. C4 already showed that an Agent can generate an identified Gaussian joint law, that an unprovided OLS coefficient can be algebraically implied by pairwise moments, and that incomplete moments permit opposing adjusted effects. Its selector comparison was nondiscriminating because all revisions retained the same model.

A new Gaussian covariance-to-OLS demonstration, another retention/selector loop, or another general identification counterexample would add little. The revised proposal has a narrower additional purpose: **test whether a changed conditional evidence packet actually changes the Agent-authored target generator in the appropriate way when the source marginal/pairwise summaries remain unchanged and the target group composition differs.** This is a controlled translation/responsiveness check. It is not publication proof or a solution to the nonidentification problem.

## Smallest approved-in-principle layout

Use neutral, explicitly artificial variables (a binary group G and continuous X,Y), an invented source population and an invented target population. A separate custodian chooses and commits the numerical fixture, source operators, target analytical operators and answers before constructor access. Source/target composition and transport premises are visible task definitions, never inferred from a real cohort. No CHNS value, biomedical name or prior candidate is reused as scientific input.

| Packet | Information available | Constructor/output budget |
| --- | --- | --- |
| T0 | Variable/domain/units, intended output, target description and common controlled transport premises; no numerical source moments | One fresh context; three output seeds |
| T1 | T0 plus exact invented source marginal means/SDs and specified pairwise moments/correlations | One fresh context; three output seeds |
| T2-plus | T1 plus one admitted set of group-conditional slopes and dispersion summaries | One fresh context; three output seeds |
| T2-minus | The same T1 plus the counterfactual group-conditional packet | One fresh context; three output seeds |

Use one prompt template, one available model family, the same tool/code/sampling allowance, and one frozen generation candidate per packet. Packet labels shown to builders should be neutral; do not tell them which target sign or structure is desired. No source-feedback revision, optimizer, root-entered generator parameters, forced model family, best-candidate selection or extra construction. All source fit is evaluated after freeze. The actual budget is at most 12 final tables (suggest 4,000 rows each), not extra source-replay/calibration tables. Failed slots remain failures; no replacement packet, seed or world is selected after seeing them.

The coordinator defines interfaces and information boundaries. The **custodian**, independently of the constructors, defines artificial truth. Each **constructor** chooses its own scientific structure/parameters and explicitly distinguishes evidence, derivation and additional assumptions. The reviewer checks these roles and exact packet commitments; the reviewer does not author a scientific candidate.

## Separate three claims and corresponding endpoints

1. **Evidence compliance:** compare the output's appropriate group-conditional statistics with its own admitted packet, alongside marginal/pairwise diagnostics. Source group composition differs from target composition, so raw whole-target moments cannot be passed off as source replay. Either fixed reweighting/stratum recombination is prospectively justified from the controlled premises, or label the check as target-conditional compliance rather than source reproduction. No additional generated table is needed. Empty/insufficient strata or undefined regressions produce explicit unavailability.
2. **Identified composition check:** the primary target projected X coefficient tests numerical translation of conditional evidence under the stipulated mixture shift. In the coordinator's illustrative interaction law with common conditional X variance and X independent of G, it is `b + (2*p_target-1)*d`. Given the two subgroup slopes and target composition, it is a weighted sum of supplied evidence. This is an **algebraic composition check, not a genuinely unknown held-out relationship**. Evaluate both the target coefficients and the T2-plus minus T2-minus contrast against their committed values. Do not reveal this answer/formula to the constructors as a required model or target value.
3. **Unreported analytical reuse/limit:** precommit one scientifically interpretable artificial joint-tail contrast, at fixed thresholds. The custodian provides normal and heavy-tailed compatible error worlds with the same admitted conditional means/slopes/variances but different tail answers. Do not admit a normal-family assumption that would identify the supposedly hidden tail answer. The endpoint must not be an algebraic restatement of a supplied statistic. It measures what the generated joint data imply beyond the supplied summaries and may fail; no guaranteed positive result is required.

T0/T1 do not identify which conditional packet/world is true. Score their same outputs against all precommitted compatible sign/tail worlds, without choosing the favorable world or inventing probability weights. T2-plus/T2-minus are scored against their respective compatible normal/heavy-tail pair. Report world-specific errors and raw quantities, never an unqualified average ranking across differently informed packets. These are alternative artificial laws, not independent clinical cases.

## Custody admission checks before any author sees a packet

- Verify algebraically/numerically that the two conditional worlds really have identical T1 summaries, while T2 differs and implies a nonzero target-projection contrast under the stated composition shift.
- Verify the normal/heavy-tail pair preserves every visible T2 quantity but changes the tail endpoint. Specify finite moments, thresholds and target-tail truth accuracy; deterministic integration is acceptable, with its numerical error declared. Do not silently include marginal quantiles or full bivariate distributions that destroy the claimed packet equivalence.
- Freeze exact source/target selection, conditional-variable meanings, any invariance premises, endpoint formulas, tolerances used solely for implementation checking, row/seed limits and all visible/hidden hashes. Separate visible source values from hidden target values.
- Have an independent reviewer check information leakage and implied quantities. Lack of full identification does not block this controlled pilot; falsely labelling an identified answer as discovery does.

## Interpretation and stop rules

The strongest attainable positive result is: the two enriched-packet generators encode their differing conditional evidence and produce the corresponding derived target projections; the same outputs show explicitly what tail conclusions remain assumption-dependent. If compliance fails, the Agent has not demonstrated reliable numerical evidence incorporation. If compliance succeeds but composition fails, study-to-target translation failed. If both succeed but tail behavior fails, the limitation is documented rather than repaired against hidden truth. If all results resemble a simple prior despite the altered packet, the evidence-to-generator link is not demonstrated here.

One constructor per packet cannot separate packet effects from stochastic authorship variation. Three sampling seeds estimate only output Monte Carlo variation, not constructor reproducibility. The contrast is therefore a concrete responsiveness demonstration, **not** a general causal/average benefit estimate, an Agent-superiority claim or a method benchmark. Counterfactual packets improve discrimination relative to C4 but do not establish novelty themselves.

Stop after the complete 12-slot report and independent recomputation. Preserve duplicates, failures, favorable and unfavorable compatible worlds. No added selectors, real target, parameter repair, further evidence tier or extra seed follows automatically. The broad project still covers complete generation, variable extension and missing-cell completion; this toy checks one necessary connection within that scope, rather than replacing it.

Read-only basis: `docs/C3_SOURCE_CONSTRAINED_GENERATION_RESULTS_2026-10-31.md`, `docs/C4_REVISION_ACCEPTANCE_RESULTS_2026-10-31.md`, and C4 protocol/admission/commitment/visible-contract metadata. No C4 private custody code, row table or hidden artifact was opened for this review.
