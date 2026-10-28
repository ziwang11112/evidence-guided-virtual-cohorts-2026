# Milestone 1: contracts, source-statistic tools and Agent skill

Completed 28 October 2026. Version 0.1.0. This is software/interface validation with invented data, not a new biomedical result or demonstration of superior data generation.

## Delivered

- A reusable `evidence-cohort-generation` skill, stored in this project and copied to the local Codex skill directory with matching hashes. Skill format validation passed. It preserves Agent discretion over evidence, relationships, distributions, parameters and justified revisions.
- Three task modes: whole-cohort synthesis, entirely unmeasured-variable enrichment, and partial missing-cell completion. Both program and direct-row candidate routes are supported as submissions.
- Explicit task variables, units, preservation rules, information mode and budgets. Prior-only mode does not require invented citations. Retrieval-budget enforcement awaits the gateway adapter.
- Typed source statistics, uncertainty descriptions, source-cohort overlap fields, model parameter provenance and declared assumptions. Unsupported numeric statistics can remain `reported_other` evidence rather than being silently discarded or treated as zero.
- Mean, sample-SD, correlation, OLS-coefficient and event-proportion operators, with declared selection, missing-data handling, unit labels and variable/adjustment checks. Results report numerical differences without inventing scientific success thresholds.
- Immutable-by-contract candidate records, parent/revision checks, actual check-artifact hashes, source registration and append-only registry-prefix commitments. Source additions can support a new version without rewriting an earlier one.
- Program ABI `generate(observed, spec, seed)`, called positionally, checked without importing or executing the program.

## Verification performed

| Check | Result | What it establishes |
|---|---|---|
| Independent pytest suite | **98 passed, 1 skipped**, exit 0 | Tested representation, preservation, source binding, lineage, ABI and negative cases |
| Skipped test | Windows denied creation of a symbolic link (WinError 1314) | The real symlink fixture was not exercised on this host; no claim it passed |
| CLI integration | `demo`, `validate`, `source-checks`, `freeze`, `verify` all exit 0 | Direct-row fixture goes through the complete implemented interface |
| Source operator fixture | Mean 7.0; OLS slope 2.0000000000000004 against declared 7 and 2 | Correct arithmetic on seven invented rows; slope difference is floating-point rounding |
| Independent skill use | A separate Agent authored a new program, evidence/spec/decision/check records; validate/freeze/verify exit 0 | Another Agent can use the interface and declare unsupported/generalization limits |
| Installed skill | Both files match project bytes; format validator passes | Local skill installation matches the versioned source |

The independent test run is retained locally as `work/test_run_final.txt`. The direct-row integration is `work/integration-m1-final/`. The final skill trial is `work/skill-forward-abi/`. Work artifacts, temporary paths and toy data tables are excluded from the GitHub export; code and aggregate validation metadata are retained. The test helper creates only invented fixtures. Existing HDL, insulin and earlier experiment files were not changed or rerun.

## Problems actually found and corrected

1. **Declared versus bound checks:** the older study guide requested an artificial-check file that was absent from its freeze list. The new lifecycle binds the check record, result artifacts and all candidate files.
2. **Wrong source variable or adjustment:** statistic kind and units alone could allow checking the wrong variable. The engine now checks the represented variable set and adjustment inclusion; deliberate differences require an explicit approximation with assumptions.
3. **Percentage scale:** proportion evidence and operator outputs now agree on `1` versus `%` ranges.
4. **New evidence after freeze:** hashing the entire mutable registry would invalidate an earlier candidate whenever a new source was added. The new receipt commits an append-only prefix and its source bytes.
5. **Stale source reports:** changing a model, evidence item, plan or table after a source check could leave an apparently valid old report. Freeze now recomputes a present machine source report and rejects a mismatch. Later verification checks committed bytes rather than recalculating across different numerical environments.
6. **Missing program ABI:** the first independent Agent correctly followed the incomplete instruction and wrote a one-argument function. The contract and skill now specify three positional inputs. A fresh submission completed the updated contract. The earlier developmental trial is preserved rather than relabeled as passing the final ABI.

These are software and interface findings, not new biological mechanisms or measured improvements in target analyses.

## Boundaries of this result

No LLM/API launcher, new literature retrieval integration, sandbox runner, independent source-population execution or locked target evaluator is implemented in v0.1.0. The standalone skill trial used an existing subagent and procedural file restrictions; it did not run through an integrated provider adapter. The program route is submitted and statically inspected, not executed. The ordinary Agent method and direct-row route have not been compared for scientific utility here.

Source-table checks retain `generation_link_verified: false`. They verify statistics on submitted tables; they do not certify that those tables came from a frozen generator. Units, outcome/exposure roles and study selection still need substantive review. The registry is a trusted input rather than an automated literature filter or authorization boundary. Hashes detect changes relative to a receipt; they do not prevent a process from reading files or rewriting both data and receipts.

The local Docker CLI was present but its Linux engine was not running at inspection. WSL distributions were listed, but no secure execution setup was claimed or tested. A real confirmation run must place reference data outside the builder's accessible environment; a separate directory and AST checks do not achieve that by themselves.

## Next milestone

Connect the existing screened literature gateway and a bounded execution adapter to one ordinary Agent. Give it a controlled task, capture its actual source retrieval and generation decisions, execute the frozen program in an environment without custodian data, and validate produced tables and seed behavior. Then bind source-context generation to the source-statistic checks and allow one evidence-driven revision or a justified no-op under the declared budget.

Only after that end-to-end loop works should a fresh public biomedical case assess whether source-check feedback improves reserved analyses. Uncertainty calibration, support-label performance and measurement savings remain separate later hypotheses. No model training or HPC allocation was required for this milestone.
