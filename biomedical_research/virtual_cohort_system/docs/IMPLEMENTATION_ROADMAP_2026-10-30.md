# Stepwise design, implementation, validation and improvement

30 October 2026. This is the active development sequence, based on the user's request to reorganize the work and proceed one verified step at a time. It does not overwrite historical experiment protocols.

## Scientific objective

Use published biomedical evidence and available covariates to generate reusable virtual data, including entirely unmeasured indicators. Evaluate whether the generated data support useful scientific analyses relative to reserved real measurements. A capable ordinary Agent is a valid implementation. Whole-cohort generation and partial missing-cell completion remain broader uses requiring their own evidence.

The method must connect evidence meaning, a stochastic generator, and downstream analytical use. More code, more Agents or a better source-fit score alone does not demonstrate this contribution.

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

M12-A and M12-B are implemented: see [independent source contexts](../MILESTONE_12A_RESULTS.md) and [bounded immutable calibration](../MILESTONE_12B_RESULTS.md). The latter has three actual isolated engineering runs, including failure controls. M12-C and the later scientific stages remain proposed until their artifacts and checks exist.

## M12-B design and implemented boundary

Keep the generator code and structure fixed within one calibration session. Record allowed parameter paths, bounds, sources, context versions, operators, loss scaling, fixed training simulation seeds, independent replay seeds, optimizer settings and stopping rules. A simple bounded optimizer is sufficient initially; analytic solutions can be used where valid.

Every internal trial materializes immutable parameter inputs and uses the existing isolated execution adapter. Never import Agent-generated code into the host optimizer. Bind trial inputs, output and statistics to verified receipts. Separate parameter trials from scientific revisions, and count both against explicit run-level budgets appropriate to their meaning.

Keep the expected constraint set fixed. Undefined statistics cannot silently disappear from the loss. Do not change unreported source covariance, remove an inconvenient study, widen bounds or alter the analysis formula inside the same session. Such changes require a documented scientific decision and a new session without resetting global usage.

Validate with invented cases covering a source mixture, an adjusted relationship, and an incompatible set of constraints. These are computational checks with known answers, not additional biomedical experiments. Do not hand-code their coefficients into a real-case generator.

This stage now has a bounded coordinate-search tool, immutable trial bundles, a permanent per-bundle reservation ledger and diagnostic replay on separately scheduled seeds. The current tool uses every declared source check in the fixed objective and supports top-level scalar parameters. It deliberately rejects automatic recovery of pending sessions. See [the interface](BOUNDED_CALIBRATION.md) for the exact scope. Next implement M12-C's source-only Agent decision and scientific-release promotion; a better engineering fixture score is not the next research objective.

## Real-case admission, before target outcome analysis

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
