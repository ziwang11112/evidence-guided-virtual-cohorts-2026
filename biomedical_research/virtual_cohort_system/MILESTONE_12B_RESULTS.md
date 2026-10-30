# M12-B — Bounded immutable calibration

Completed 30 October 2026. This is the second engineering step in the [active roadmap](docs/IMPLEMENTATION_ROADMAP_2026-10-30.md). No new patient outcome was opened or biomedical candidate tuned in this milestone.

## What now works

An Agent-selected scientific structure can be passed to a numerical calibration tool with an explicit parameter whitelist and bounds. Every trial is a new frozen bundle. The program, evidence, source populations, operators and unselected parameters remain fixed. All generated code runs through the existing isolated adapter.

The tool evaluates the complete fixed source-constraint set. Unavailable statistics make a trial infeasible; they cannot silently disappear from its loss. A deterministic search is limited by trials, search rounds and representable step size. A fixed bundle-level ledger reserves the maximum session cost before dispatch and preserves actual usage and unused reservations. An interrupted session cannot be restarted automatically or reset under a new session name.

Selection is committed from fit results before separate simulation seeds execute. Those seeds are diagnostic only. Verification recomputes the statistics and the complete numerical search, rather than trusting the saved best score.

## Actual isolated runs

The fixture contains 12 invented source rows with an unbalanced 8:4 category mixture. Its additive structure and fixed category effect are deliberately known. Three parameters control the intercept, adjusted x relationship and residual scale. The evidence supplies a mean, an adjusted regression coefficient and sample standard deviation. This is a software fixture, not a relationship discovered by an Agent.

| Fixture | Parameter trials | Generator executions | Observed outcome |
|---|---:|---:|---|
| Compatible source summaries | 20 | 42 | Recovered intercept 3, slope 2 and residual scale 1; separate-seed summaries also matched |
| Two contradictory means for the same context/operator | 3 | 8 | Stopped at the declared small budget; fit threshold not met; both constraints retained |
| Rank-deficient adjusted regression | 3 | 6 | All trials infeasible; no selected model or replay; undefined constraint retained |

For the compatible fixture, the mean squared scaled source discrepancy fell from **2.0047391913** to **2.1365 × 10⁻³¹**, numerical precision for this deliberately recoverable arithmetic. The separate-seed discrepancy was the same. These numbers are not a biological accuracy metric.

The conflict fixture improved its score from **5.5035543935** to **4.1285543935** but correctly failed the fit criterion. It was given only three trials; no global optimization result is claimed. Independently of search, the two same-operator means, 11/3 and 17/3, cannot both hold. The controller reports insufficient fit; interpreting the cause belongs to the scientific Agent.

The undefined fixture generated valid tables, but its adjusted regression selected only one category and had a rank-deficient design. Execution success therefore did not become a false calibration success. All **56** actual generator executions and all **26** parameter trials remain available in the [invented-run archive](reports/m12b_2026-10-30/README.md).

## Review and verification

New tests cover known arithmetic, adjusted relationships, fixed parameters, disjoint seeds, heldout failure without reselection, complete constraint accounting, interrupted sessions, global budget exhaustion, rehashed artifact tampering, optimizer replay and numerical edge cases. Mock execution tests are labelled separately from the actual WSL/bubblewrap runs above.

The complete suite passed **481 tests**, with **2 skips** because this Windows account cannot create the symbolic links required by those fixtures. The new calibration modules contribute 97 passing tests and one of the skips. Actual isolated execution was checked separately, not inferred from the mocked tests.

Review corrected an exclusive-write collision in trial materialization, required a selection record before replay, bound the actual pre-dispatch budget receipt, and caught a floating-point case that could otherwise loop without consuming trials. Tests now cover subnormal steps and rounded duplicate proposals.

All **16 historical engine files** match commit `4d3db0bf6a8d1376ad19a3d7f2c2c453e600f784`. All **228 M11** and **54 M12-A** curated artifacts retain their frozen hashes. The full-suite output, independent arithmetic audit and hash inventory are retained with the curated archive.

## Limits and next step

This proves that bounded parameter fitting is implemented and traceable. It does not prove scientific transfer, restore individual measurements, establish statistical intervals or improve any real-data analysis. In particular, M11's source-to-target deterioration remains a negative result.

Current limits include top-level scalar parameters, enrichment with identity measurements, one active session per bundle, no automatic interruption recovery and a simple local coordinate search. All declared source checks enter the objective. Cached source-check reports require a fresh scientific submission; selected numerical trials still need explicit promotion into a scientific release. Agent tools remain procedurally restricted, although generator execution is isolated.

Next is **M12-C: one recorded scientific Agent loop**. Give the Agent permitted evidence and the source diagnostics, let it justify retention or a changed scientific structure, calibrate through this tool, and materialize a proper frozen release. Start with a source-only integration case. A real biomedical confirmation follows only after evidence admission and a complete locked analysis/output schedule. No additional mechanism should be added merely to improve this invented fixture.

See [interface and limits](docs/BOUNDED_CALIBRATION.md). Latest biomedical evidence remains [M11](MILESTONE_11_RESULTS.md) and [M10](MILESTONE_10_RESULTS.md).
