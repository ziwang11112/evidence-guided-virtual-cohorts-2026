# M17-A: evidence-only whole-cohort interface readiness

Date: 2026-10-31. Scope: static inspection of existing contracts, execution, source-statistic interfaces, tests and explicitly admitted historical method documentation. No patient tables, closed target files, candidate generation, third-party execution, paid API, training or HPC were used. No scientific or historical artifact was changed.

## Decision

The base harness already supports **whole-cohort generation without an observed individual table**, for both Agent-written programs and literal Agent-written tables. The next unit does not require rewriting generation modes.

The important missing piece is **generic execution-linked source feedback for whole-cohort programs under different source populations**. Both existing source-replay versions are deliberately enrichment-only. A bounded first test can use existing whole-cohort execution and source operators with an explicit controller-owned linkage record. It must not mislabel this as the implemented multi-source replay adapter.

## 1. What exists now

| Capability | Verified code / documentation | Boundary |
|---|---|---|
| Three task modes | `cohort_harness/contracts.py:93,133–135` | Whole-cohort tasks reject every `observed` column role; substantive variables are `generated` |
| No observed input in whole-cohort mode | `contracts.py:177–182`; `__main__.py:37–43`; `lifecycle.py:231–239` | Input must be `None`; a bundle-level `observed.csv` is rejected by validation and freeze |
| Program interface | `lifecycle.py:143` and `cohort_harness/_worker.py:35–49` | Top-level `generate(observed, spec, seed)` returns a DataFrame; whole-cohort invocation uses `observed=None` |
| No observed table staged for execution | `execution.py:203,226–229` | The candidate must jointly generate every substantive column; there is no covariate template in this mode |
| Direct table route | `__main__.py:50–57`; `execution.py:275–280` | Submit `generated.csv` instead of `generator.py`; validation/copying does not resample rows |
| Output and preservation contracts | `contracts.py:187–207` | Full schema, finite values, bounds, categories, unique fictional IDs and row count remain enforced; whole-cohort output has no individual-to-individual matching |
| Source statistics | `source_checks.py:103,202`; `docs/SOURCE_CHECKS.md` | Mean, SD, quantile, Pearson/Spearman, OLS coefficient and event-proportion operators are available; table/source meaning remains a declared scientific assumption |
| Frozen candidates and revisions | `lifecycle.py:331,361`; `__main__.py:97–102,151–160` | Append new candidates, bind parent/revision and actual feedback; preserve retention and failures |
| Generator-only isolation | `execution.py`; `docs/EXECUTION_ADAPTER.md` | Existing WSL/bubblewrap adapter; no unsandboxed fallback. The LLM's general file tools are not isolated by this adapter |

`tests/test_contracts_lifecycle.py:156–161` parametrizes valid contracts across all three modes, and `:183–198` tests invalid whole-cohort outputs. In contrast, the central mocked program fixture in `tests/test_execution.py:16–55` assumes an observed enrichment table. A dedicated whole-cohort execution-boundary regression test would be useful before M17-A generation. These tests were inspected, not rerun here.

M15-A is already a historical source-only whole-cohort direct-authorship pilot: all age, BMI and urate values were fictional, with 128 rows and source-moment feedback. Its report establishes that route and a retention cycle, not general analytical usefulness. M17-A should not be described as the first time the project ever generated a whole cohort. See `MILESTONE_15A_RESULTS.md`, opening and input/schedule sections.

## 2. What does not exist as a generic whole-cohort adapter

- `source_context.compile_source_task` explicitly requires `mode="enrichment"` (`source_context.py:56–69`). It needs a declared source covariate table.
- `source_replay_v2.py:115` likewise rejects other modes. Its source context preserves variable identities/roles and allows identity measurement mapping only.
- The legacy `source-replay` also supports enrichment programs with source covariates only; see `docs/SOURCE_REPLAY.md`.
- `source-checks` computes values from a candidate-contained declared table and does not certify that a particular generator produced it. The CLI refuses to write a new source-check report into an already frozen candidate (`__main__.py:142–149`).
- `source_checks.apply_operator(frame, operator)` is a numerical primitive, not a provenance or evidence-eligibility validator. A controller using it must also validate the evidence/operator definition and bind the verified output, candidate, task and source packet.
- The contracts enforce the absence of the canonical observed table. They do not semantically inspect every admitted document for individual records or prevent an unrestricted LLM file tool from opening a custodian path. An evidence-only claim still needs a visible-input manifest and independent packet inspection.

There is no clear base-generation defect requiring a quick patch from this inspection. Generalizing source replay is a new feature with scientific design choices, not a one-line relaxation of an enrichment guard.

## 3. Minimum M17-A construction

1. **Separate the controlled truth from the visible packet.** A controller prepares an invented joint distribution and computes selected summary evidence. Label the source artifacts as synthetic study briefs or engineering fixtures, never real published studies. Keep truth code, parameters not disclosed by the evidence, reserved data and reserved analyses outside the builder bundle.
2. **Use a genuine whole-cohort task.** All substantive variables have role `generated`; a fictional identifier has role `identifier`; no `observed.csv` exists. Population description, schema, output size and allowed tools are explicit. Target/source individual records are not permitted inputs in this arm.
3. **Admit a small fixed evidence packet.** Register hashes and declare which relationships are reported, derived or assumed. The initial mechanism test can use compatible source/target conditions so execution linkage is tested before adding heterogeneous source reconstruction.
4. **Choose one route for the first pass.** A program produces the joint table through `generate(None, spec, seed)`; a direct-row candidate supplies the table itself. Do not hand-code desired biological coefficients in the controller. An invented truth is appropriate for a controlled test, but the scientific proposal must be attributable to the builder's allowed evidence.
5. **Link feedback outside the frozen candidate.** For a program, run and verify the existing execution adapter, calculate only permitted source statistics on its verified output, and save a controller feedback receipt binding all inputs and operator versions. That small controller is still work to implement and test. For direct rows, existing `source_checks.json` can point to the candidate's `generated.csv` before freeze; later verified feedback stays outside old candidates and is bound in a new child.
6. **Evaluate only after the scheduled candidates are frozen.** Compare distributions and scientific analyses, not row-wise individual errors. Keep at least one unprovided analysis and distinguish a recoverable relation from a deliberately underidentified relation.
7. **Optional observed-covariate arm.** Use a separate enrichment bundle with an explicitly different information contract. Keep the evidence packet and method budget comparable where appropriate. Its access to observed covariates is an intervention on information availability, not evidence that the full-cohort arm used those rows.

## 4. Verified command forms

The following are **documented command forms, not commands executed by this audit**. Run from the project root, substitute newly prepared bundle/candidate/runtime paths, and use the configured Python environment.

```powershell
python -m cohort_harness validate --bundle BUNDLE --candidate initial
python -m cohort_harness freeze --bundle BUNDLE --candidate initial
python -m cohort_harness verify --bundle BUNDLE --candidate initial
python -m cohort_harness execute --bundle BUNDLE --candidate initial --run-id initial_seed01 --seed 17001 --runtime RUNTIME_JSON
python -m cohort_harness verify-execution --bundle BUNDLE --run-id initial_seed01
```

The CLI requires `--runtime` even though a direct-table execution does not launch generated code. Inspect the actual status in every execution receipt; successful integrity verification of a failed run is not successful generation.

For a prepared direct-row source-check recipe, this command must occur before the candidate freeze because the CLI writes its report inside the candidate:

```powershell
python -m cohort_harness source-checks --bundle BUNDLE --candidate initial
```

For a later revision, prepare its artifacts and truthful feedback/revision record first:

```powershell
python -m cohort_harness freeze --bundle BUNDLE --candidate revised --parent initial --revision REVISION_JSON
```

Do not invoke `source-replay` or `source_replay_v2 run` on a whole-cohort task and then bypass its rejection. A new whole-cohort source-context feature should have its own explicit protocol/version and tests.

## 5. Boundary tests worth implementing before a run

- Reject an evidence-only bundle containing `observed.csv` or an `observed` column role, at both validation and freezing.
- Execute a small trusted fixture with `observed is None`; confirm staged files contain no observed table and that all substantive output columns are generated.
- Verify that a whole-cohort direct table is copied without stochastic resampling, while a program seed is recorded and independently replayable as appropriate.
- Reject missing/extra columns, nonfinite values, wrong row count, duplicate fictional IDs and invalid category values.
- Independently recompute source statistics from the verified generated bytes; detect a mismatched receipt, changed output, source/operator mismatch or added hidden reference statistic.
- Confirm feedback cannot change the frozen candidate and that retention preserves the same table/program bytes rather than counting as an improved independent construction.
- Keep the separately labeled enrichment arm's observed rows out of the evidence-only builder manifest. Use a fresh builder context that has never seen the controlled truth.

These are meaningful contract and information-boundary tests. Passing them would establish readiness to run the small experiment, not scientific quality, physical isolation of every Agent tool or publication readiness.

## Completion record

This audit added only this document. No generation, target access, test execution, code changes, downloads or Git operations were performed. The root task owns the M17-A protocol, implementation and publication decisions.
