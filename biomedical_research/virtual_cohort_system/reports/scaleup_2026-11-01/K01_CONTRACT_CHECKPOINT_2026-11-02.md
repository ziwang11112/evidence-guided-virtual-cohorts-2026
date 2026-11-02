# K01 design and necessary implementation checkpoint

The scientific objective remains whole-cohort generation from published evidence for reusable analyses. This checkpoint fixes a reviewed K01 design and adds the computations necessary to test it. It has not generated a new clinical cohort, fitted actual source parameters or evaluated HAALSI target effects.

## Outcome

The [scientific decision](case_k01/CONTRACT_DECISION_2026-11-02.md) fixes three glucose analyses, source roles, measurement/population assumptions, one statistical reference and the finite schedule. The [request packet](case_k01/request/README.md) contains only approved-scope source/target metadata and selected published evidence; it excludes participant rows, target moments, availability counts and prior conclusions. Its preparation status still prevents automatic construction. The [independent review](case_k01/CONTRACT_INDEPENDENT_REVIEW.md) separates scientific design acceptance from production execution readiness.

Eighteen source descriptors are now precisely defined: four means, four individual SDs and ten fractions. Their conventions are explicitly approximate. The two source populations have age bounds different from the target; one global column-bound rule would be wrong. The new whole-frame guard binds context to the task population and rejects an invalid table without filtering. The source-bin arithmetic keeps all original rows in the denominator, preserving the BMI boundary gap and the declared age-bin interpretation.

S01 is a transparent independent-marginal reference with explicit transport assumptions, not an optimized or universally sufficient statistical model. Its analytic parameter derivation and sampler are implemented, but the real source values have not been fitted. A separate normalized source-input view binds the exact shared evidence and preserves integer count operands before division. No target-derived parameter enters either reference preparation or Agent request.

## Verification and failures

The new author checks cover 86 distinct invented-input tests: ten analysis, eight context guard, three source-descriptive, 54 statistical-reference and eleven metadata-normalization tests. The initial analysis/guard run passed seventeen and failed one test because its independent statsmodels oracle mutated its design-column metadata after fitting. The test was repaired using a separate interaction frame; the affected test passed. No analysis implementation change was needed for that failure. The other new suites passed on their first runs; previously passed suites were not rerun.

One independent composed check fit invented source summaries, sampled 24 rows in each of two source contexts and a target context, and applied the guards, eighteen source descriptors and three target analyses. The 72 invented rows are software fixtures, not participants or a clinical experiment. Independent arithmetic agreed to floating-point precision; the exact errors and artifact hashes are retained by the reviewer. No CSV, frozen scientific candidate or isolated clinical execution was produced by that check.

Static review also checked the eight builder-file commitments, 34 retained source records, exact eighteen diagnostic definitions, source-input normalization and context/population mappings. The existing K02 and historical MIND commitments remain unchanged. This evidence validates implementation and provenance at the stated boundaries, not measurement transport, synthetic-data accuracy or a new biomedical conclusion.

## Next required execution unit

Bind the committed K01 and existing K02 packets into the actual finite controller: source registry and candidate model; immutable source/target execution and context guard; explicit semantic-v1 collection followed by separately reviewed descriptive reports; revision/retention and failed-attempt accounting; and reserved-reference custody. Finish and globally freeze the protocol and permitted input artifacts before clinical construction. Later, close all final Wave A candidate/output identities before any target evaluation. The new source helper cannot be used to bypass unavailable strict semantic checks.

No new study search, endpoint, baseline family, training run, HPC job, paid API or scheduler is added. Intake remains four of six candidate families and five of twelve original studies. Downloads remain 253,787,333 metered bytes; browser traffic from earlier work is unmetered. Patient-level data, complete third-party documents and contact details remain local. Foreground work is not a scheduled run.
