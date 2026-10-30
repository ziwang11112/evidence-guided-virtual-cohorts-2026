# Bounded source calibration

M12-B implements numerical fitting of one frozen scientific structure. It does not propose a structure, search papers, optimize target performance or estimate a posterior. The scientific Agent must first submit a reviewed generator, evidence and source contexts. All generated Python still runs through the existing WSL/bubblewrap adapter.

## Inputs and objective

`cohort_harness.calibration.run_calibration(bundle, candidate, session_id, plan, runtime=...)` accepts an existing frozen enrichment generator with a `source_replay_v2.json` recipe. Use `candidates/initial` or an absolute candidate path. Create the bundle-level budget once with `calibration_budget.create_budget` before requesting sessions.

The version 1 plan fixes:

- `parameters`: named top-level scalar parameters, finite lower/upper bounds and initial search steps. Initial values come from the parent spec and must be in bounds. Other parameters cannot change.
- `constraints`: every `(context_id, check_id)` in the parent source recipe exactly once, with a positive numerical `scale` and written `scale_reason`. Reported estimates, operators, source selections and adjustment sets remain in the frozen evidence/recipe.
- Non-overlapping `fit_seeds` and `replay_seeds`, each with no duplicates.
- `optimizer`: method `bounded_coordinate_search`, `max_trials` including the initial evaluation, `shrink`, `min_step_fraction`, and `target_loss`.
- `execution`: per-execution timeout, memory and output/log limits.
- `noncomputable: "infeasible"`.

For each seed and constraint, compute `(simulated statistic - reported estimate) / scale`. The objective is the mean of the squared errors across all seed–constraint pairs. This is not a likelihood. It does not treat correlated published summaries as independent statistical evidence. Scales are explicit design choices; a source standard error must not be silently replaced by simulation error or population standard deviation.

Every required statistic must be available and finite. A failed execution or undefined statistic makes the complete trial infeasible (`loss: null`), with the missing constraint retained in diagnostics. Constraints never vanish from the denominator.

## Search and separation of decisions

The deterministic search evaluates the initial vector, then coordinates in plan order, with positive before negative steps. Each coordinate's pair uses the incumbent at the start of that pair. Values are clipped to the locked bounds; previously evaluated vectors are skipped. Strictly lower loss wins, with the earliest trial retained on ties. A full round without improvement shrinks all steps. The process stops at the fixed loss threshold, trial count, or minimum step rule. Search rounds also cannot exceed `max_trials`, and a shrink with no representable change stops explicitly. Underflowed minimum thresholds are rejected before dispatch. This simple optimizer is not guaranteed to find a global optimum or prove incompatibility.

Fit uses common random seeds. A `selection.json` record commits the chosen trial and fit-record hashes before separately scheduled replay seeds execute. Replay never changes the chosen model, seeds or fit loss. These are independent simulation draws under the same sources, not independent populations, unseen scientific analyses, or parameter uncertainty draws.

Changing a formula, source population, unreported source covariance, operator, parameter bound or evidence set requires a new scientific decision and session. A new session consumes the same bundle-level budget. Numerical trial bundles cannot directly parent another session. Promoting selected parameters into a scientific revision/release with the broader draw schema is a later controller step, not an implicit operation here.

## Immutable artifacts and verification

Each session is stored at `cal/<session_id>/`; each `tNNNN` is a complete immutable trial bundle with task, covariates, registered source prefix and frozen candidate `candidates/t`. The only scientific-spec changes are whitelisted parameter values and their explicitly calibrated provenance. A sidecar binds the trial to its parent and plan. The original program, evidence, source contexts and other candidate artifacts remain byte-identical.

The session stores its locked plan, intent/reservation, per-trial outputs and source receipts, selection seal, separate replay and final result. `verify_calibration` verifies parent and engine bindings, recalculates statistics from execution outputs, reconstructs the entire deterministic search, checks every allowed delta, and recomputes selection, termination and usage. Hashes support integrity and reproducibility, not cryptographic attestation against a malicious artifact owner.

Current implementation rejects candidates containing cached `source_check_report.json`, rather than carrying a potentially stale report across changed parameters. Prepare a new scientific submission with current source-check declarations first. Historical reports remain preserved in their original candidates.

## Budgets and interruption

The fixed `calibration_budget/` ledger counts sessions, parameter trials, generator executions and reserved timeout seconds. A session reserves its complete worst-case allowance before any trial creation or dispatch:

`contexts × (max_trials × number_of_fit_seeds + number_of_replay_seeds)` executions.

Unused allowance is not refunded. Actual completed counts are reported separately. Reserved seconds are the sum of per-generator timeout allowances, not measured total wall time or a cap on verification/copy overhead. A new session cannot reset the existing budget. Budget enforcement is local to this bundle and does not prevent an unrestricted operator from creating another project or deleting ledger files.

This first version supports one active session and no automatic recovery. An unexpected interruption leaves a pending record and blocks another reservation; it must not trigger a fresh uncharged session. Terminal generator failures remain ordinary charged trial outcomes. Only the generator process is isolated; Agent filesystem and research access remain procedurally controlled.

## Scientific scope

Passing calibration demonstrates consistency with supplied source statistics under declared populations and modelling assumptions. It does not show those assumptions are transferable, identify an otherwise unidentified joint distribution, restore any individual's true measurement, or establish the usefulness of subsequent analyses. The next scientific evaluation must use a frozen release and new reserved real-data analyses. M11's negative source-to-target transfer result remains unchanged.
