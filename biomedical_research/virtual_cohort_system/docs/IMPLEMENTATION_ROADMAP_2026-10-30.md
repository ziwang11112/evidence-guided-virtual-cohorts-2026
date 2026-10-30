# Stepwise design, implementation, validation and improvement

30 October 2026. This is the active development sequence, based on the user's request to reorganize the work and proceed one verified step at a time. It does not overwrite historical experiment protocols.

## Scientific objective

Use published biomedical evidence and available covariates to generate reusable virtual data, including entirely unmeasured indicators. Evaluate whether the generated data support useful scientific analyses relative to reserved real measurements. A capable ordinary Agent is a valid implementation. Whole-cohort generation and partial missing-cell completion remain broader uses requiring their own evidence.

The method must connect evidence meaning, a documented generation process (direct Agent-authored rows or an Agent-authored program), and downstream analytical use. More code, more Agents or a better source-fit score alone does not demonstrate this contribution.

## Current adjustment: literature-enabled analytical data

The user clarified that useful published statistics may all be inputs, and that generating more fictional people or additional indicators is an intended purpose. Follow [M15-B design adjustment](M15B_RESEARCH_DESIGN_ADJUSTMENT.md) and its [builder prompt](templates/M15B_BUILDER_PROMPT.md) for the next task. M15-A's no-retrieval policy is historical, not a default restriction for the method. The current harness already supports task-bound retrieval and direct-table submission; enabling them requires a new case-specific task, not changes to the frozen M15-A configuration.

The next bounded unit is case admission and evidence planning, then a complete literature-enabled generation/feedback/reference-evaluation experiment. Full source statistics can inform construction, while source fidelity, independent target transfer and reuse of uncalibrated analyses remain separate claims. Do not artificially hide accessible source SDs and later call them unseen when the Agent can read the full paper. Record returned literature exposure as well as extracted evidence use. A result not cited in the final evidence file may still have been seen.

Keep whole-cohort expansion, unmeasured-variable enrichment and missing-cell completion within the overall method. Enrichment preserves real participants and observed cells; extra fictional rows require whole-cohort mode. Fix the case's output columns and row count before binding its task. Do not equate extra synthetic rows with extra empirical information. The primary contribution is useful generated data, not mandatory superiority over another Agent.

This adjustment includes design documents and reusable instructions only. No new biomedical case has been admitted or run, and no new retrieval session, target download or recurring automation has been started. Interface and scientific reviews are recorded in [M15B_INTERFACE_REVIEW.md](M15B_INTERFACE_REVIEW.md) and [M15B_SCIENTIFIC_REVIEW.md](M15B_SCIENTIFIC_REVIEW.md).

## Latest route-specific pilot

After the user asked to try direct Agent row output, [M15-A](../MILESTONE_15A_RESULTS.md) completed one128-row fictional whole-cohort source-only run using the existing direct-table interface. No statistical generation program created values. A single feedback review ended in retention. Supplied moments were close, but four unprovided same-source urate SDs were all underestimated. This verifies the direct route and its limited source consistency, not repair efficacy or real-population analytical utility. Do not reopen the exposed M13-B body-fat target. A further measured-data comparison requires a separately specified task and explicit development versus fresh confirmation status; no new execution or recurring automation is scheduled by this result.

## Starting point

- M10 showed selected association feasibility and relation-specific failures.
- M11 implemented source-feedback-driven parameter revision. Source-median fit improved while target-level discrepancies worsened; stop that scalar-calibration branch.
- The existing harness supplies immutable candidates, isolated generator execution, source statistics and case-specific evaluation.
- The full [PRO specification](reviews/pro_full_system_spec_2026-10-30.md) is the design baseline; use its [implementation amendments](PRO_FULL_SPEC_REVIEW_2026-10-30.md).

## Development stages and gates

| Stage | Work and deliverable | Evidence required to advance | What it does not yet prove |
|---|---|---|---|
| M12-A: source contracts | Independent source eligibility, target eligibility and model domain; execute the same frozen generator under a source contract | Known arithmetic and invalid-input tests; actual isolated execution; historical bytes preserved | Biomedical accuracy or improved transport |
| M12-B: calibration | Immutable parameter trials, fixed source operators, bounded parameter space, global budget, declared noncomputable-statistic handling | Recover a known fixture's source statistics; reject hidden parameter/context changes; preserve failures, budgets and parent freezes | A calibrated source generator is accurate in a new target |
| M12-C: scientific Agent loop | Evidence interpretation → candidate → calibration → diagnosis → justified revision or retention | One recorded end-to-end run with provenance and actual tool outputs; no silent scientific defaults | Autonomous literature coverage or superiority over ordinary Agents |
| Case admission, parallel with B/C | One external evidence package, population/measurement mapping, allowed covariates, excluded aliases and reserved analyses | Enough admissible information for the selected analyses; exposure review; explicit transfer assumptions | Success on the still-hidden target |
| M13: new real-data screen | Frozen candidate/seed schedule, generated tables, same analysis code on real and generated data | Complete results, effect direction and magnitude/shape, reference uncertainty, uncalibrated reuse analysis and retained failures | Universal validity or all three generation modes |
| M14: targeted improvement | Address the actual observed failure, then evaluate on a new reserved task | Change tied to evidence; improvement without hiding other degradations; comparison appropriate to the claim | Publication readiness merely from adding components |

M12-A and M12-B are implemented: see [independent source contexts](../MILESTONE_12A_RESULTS.md) and [bounded immutable calibration](../MILESTONE_12B_RESULTS.md). The minimum [M12-C source-only integration](../MILESTONE_12C_RESULTS.md) is also complete: an actual Agent constructed a generator, reviewed verified feedback and retained it; selected bytes were promoted with lineage. This exercises retention, not demonstrated structural repair. Automatic retrieval/editing branches and later scientific stages remain proposed.

## M12-B design and implemented boundary

Keep the generator code and structure fixed within one calibration session. Record allowed parameter paths, bounds, sources, context versions, operators, loss scaling, fixed training simulation seeds, independent replay seeds, optimizer settings and stopping rules. A simple bounded optimizer is sufficient initially; analytic solutions can be used where valid.

Every internal trial materializes immutable parameter inputs and uses the existing isolated execution adapter. Never import Agent-generated code into the host optimizer. Bind trial inputs, output and statistics to verified receipts. Separate parameter trials from scientific revisions, and count both against explicit run-level budgets appropriate to their meaning.

Keep the expected constraint set fixed. Undefined statistics cannot silently disappear from the loss. Do not change unreported source covariance, remove an inconvenient study, widen bounds or alter the analysis formula inside the same session. Such changes require a documented scientific decision and a new session without resetting global usage.

Validate with invented cases covering a source mixture, an adjusted relationship, and an incompatible set of constraints. These are computational checks with known answers, not additional biomedical experiments. Do not hand-code their coefficients into a real-case generator.

This stage now has a bounded coordinate-search tool, immutable trial bundles, a permanent per-bundle reservation ledger and diagnostic replay on separately scheduled seeds. The current tool uses every declared source check in the fixed objective and supports top-level scalar parameters. It deliberately rejects automatic recovery of pending sessions. See [the interface](BOUNDED_CALIBRATION.md) for the exact scope. M12-C now adds recorded Agent decisions and development-candidate promotion; it does not yet create a validated target release. The next priority is real-case evidence admission and a locked real-data evaluation, rather than further improving an invented fixture.

## Real-case admission, before target outcome analysis

Current completed step: [M13-B real-target validation](../MILESTONE_13B_RESULTS.md). Four frozen initial/source-reviewed candidates produced12 Agent tables for842 participants; four published-equation references and all62 scheduled estimands per table were also evaluated. Some associations transferred, but primary means and BMI strength were materially mismatched, and source calibration did not improve target analyses consistently. Generated male-age intervals also appeared more certain than measured-data intervals. All results were retained and independently recomputed. No generator or scientific protocol was changed after target access.

The [M13-A real-source execution and review](../MILESTONE_13A_RESULTS.md) and [admission review](REAL_CASE_ADMISSION_2026-10-30.md) remain historical pre-target records. The M13-B XPORT parser repair is separately documented, with original acquisition and freeze preserved. Body-fat source-score tuning is stopped on this exposed target. The bounded [M14-A evidence-portability audit](../MILESTONE_14A_RESULTS.md) is now complete: six studies support one conditional-mean sensitivity specification, but no complete measurement bridge, conditional residual repair or transport-uncertainty law. No target or generator was run during the audit. Its autonomous follow-up ends with the decision; a new testing unit requires separate target admission and a pre-outcome freeze. Urate remains a backup, not an automatic parallel expansion.

The next case needs a real scientific use, not merely an available laboratory column. Decide the permitted population and analyses from evidence and metadata before target evaluation.

For each source, record the reported statistic, original scale, adjustment set, selection, assay and overlap with other sources. Assign its role: fitting, unused source check, qualitative model clue or deferred evidence. Verify that a selected association can be represented by the available variables or a declared integration model.

Separate portable relationship assumptions from absolute-level assumptions. If the evidence cannot anchor target levels, keep explicit sensitivity scenarios and narrow the claims about means/tails; a better optimizer cannot invent that information. Uric acid is a candidate pending evidence resolution and freshness review, not an obligation. Do not inspect successive target outcomes to choose a favorable case.

An initial real-data screen can use two separate Agent constructions and three residual draws per frozen scenario, with a small prespecified total scenario count. These are engineering repeats, not independent biological studies or a power calculation.

## What to assess in the generated data

Prespecify a small set of scientific analyses: one primary association, at least one analysis not directly fitted to source evidence, and a preservation check relevant to their interpretation. Use the same analysis definition for generated and reserved real data.

Report direction, useful effect magnitude, curve or subgroup behaviour, and reference uncertainty. Retain distribution checks when they affect these analyses. Avoid binary claims of general realism from one sign match or nominal significance. Repeated synthetic rows and residual draws do not create new source evidence.

The same release must serve the analyses without response-by-response regeneration. When a method component is claimed to improve performance, compare that component under equivalent information or use an appropriate statistical reference. A universal Agent leaderboard is not required.

## Decision after each step

Each milestone ends with a short record: what changed; which tests and experiments ran; what passed or failed; scientific interpretation; retained limitations; and the next discriminating step. Technical fixes do not retroactively improve historical biological results.

If a mechanism gives no useful signal, stop that mechanism at its budget. If evidence is insufficient, record it and seek specifically relevant information or change the case before unblinding. If a target fails, retain the result and use it as development information; later changes need a new confirmation task.

Artifacts and aggregate results can be synchronized to the existing private GitHub repository under the prior authorization. Real participant-level inputs, outcomes and target-generated tables remain local. Invented engineering fixtures can be shared, explicitly labelled as such.
