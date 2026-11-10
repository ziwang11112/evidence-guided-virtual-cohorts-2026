# Reproducibility guide for the v0.27 research record

This guide separates reproduction of an aggregate display, replay of a frozen statistical program, and reproduction of the Agent session that authored that program. It documents existing interfaces and records. No command below was executed for this revision, no virtual cohort was generated, and no clean-install or cross-platform replay was tested.

## What is available at each level

| Task | Required inputs | Supported scope and limits |
|---|---|---|
| Regenerate an aggregate display | Released aggregate results, completion hashes and the corresponding plotting script | Recreates the specified study display without Agent calls, row generation or clinical fitting. It does not independently verify the underlying participant-level analyses. |
| Replay a frozen program | Unchanged generator, its recorded hash, row count, seeds, interface, numerical dependencies and isolated worker | Samples the recorded probability law. Original receipts and new replay receipts are distinct. The example below is a static reference recipe for the documented host environment. |
| Reproduce original Agent authorship | Model/service snapshot, inference configuration, operative task and follow-ups, source/tool state and review sequence | Not fully recoverable from this release. Tasks, programs and many decisions are recorded, but historical model metadata and complete conversations are incomplete or unpublished. A new authoring session would be a new construction. |
| Recompute a clinical-reference comparison | Appropriate source data, access permissions, eligibility/weighting definitions and the study evaluator | Requires separate data and environment preparation. Aggregate plotting and generator replay do not perform this task. |

## 1. Example of aggregate-only reproduction

The Q4 script `build_result_display.py` recreates the original open-retrieval study display from `evaluation_v2/RESULTS.json` and the outputs bound by `evaluation_v2/EVALUATION_COMPLETED.json`. It checks the completion-record hashes before plotting. Python and Matplotlib are required. This is an example of the Q4 study display, not a promise that it reproduces every later manuscript layout.

In a separate working copy of the exported Q4 report directory, use:

```powershell
Set-Location 'C:\path\to\fresh-copy\core_workflow_replication_2026-11-04'
python .\build_result_display.py
```

The path is a placeholder to replace with the copied report directory. The script writes to that copy's `display` directory. No participant or synthetic row files are needed. The existing public scope describes this aggregate-only entry point; a public export may use `reports/` where the research workspace uses `work/`.

## 2. Frozen-program reference recipe: iron model B

This example uses the already selected B law. Its initial and final generator files have identical recorded bytes:

```text
SHA-256: 9ad315b8edd523bf6f4d5ef9b722f2814fa84ca4cfac111074e407f3ae9cce0f
```

The digest is recorded in the original `BATCH_LOCK.json` and was checked against the existing final program while preparing this guide. Hash inspection did not execute the program.

### Scientific interface

The authored entry point is:

```python
generate(n, rng, context) -> pandas.DataFrame
```

The trusted bridge supplies `rng = numpy.random.default_rng(seed)`. `context` is either `"zhu_source"` or `"target"`. The returned columns must be exactly `hb_g_dl` and `ferritin_ug_l`, in that order, with positive finite numeric values. B uses the same scientific law in the two contexts. The adapter selects 100,000 rows at source seed 4101 or 5,000 rows at each target seed 5101, 5102 and 5103. These are draws from the fixed law, not reruns of its Agent authoring session.

This interface description is not an instruction to import the scientific generator into an unsandboxed host Python session. The original route stages the unchanged author module and a trusted bridge inside the isolated worker.

### Required environment and working-copy layout

The retained execution adapter supports a specific Windows/WSL environment:

- WSL distribution: `Ubuntu-24.04`.
- Numerical environment: `/home/zwang/.cache/evidence-cohort-runtime/m2/venv`.
- Bubblewrap executable: `/home/zwang/.cache/evidence-cohort-runtime/m2/bubblewrap/usr/bin/bwrap`.
- Documented inspected versions: Python 3.12.3, NumPy 2.4.5, pandas 3.0.3 and bubblewrap 0.9.0.

The host Python must be able to import the retained project modules and their dependencies. The adapter validates its configured runtime and provides no unsandboxed fallback. The isolated program has no network or project/target-data mount; staged input and runtime mounts remain read-only. This guide neither changes those controls nor supplies a new portable runtime installer.

Prepare a fresh working copy containing the project `cohort_harness/` modules and the iron case at the same relative depth, for example:

```text
<fresh virtual_cohort_system>/
  cohort_harness/
  work/iron_breadth_2026-11-05/
    iron_runner.py
    candidates/B/initial/generator.py
    candidates/B/final/generator.py
```

Keep historical receipts and participant files in their archive. The fresh copy must not already contain the attempt directories used below. The adapter creates each attempt once and rejects overwriting; do not delete original attempts to make a replay fit their paths. A researcher without the documented worker must first arrange an appropriately reviewed deployment; these commands are not a tested clean-machine setup.

### Example commands, not executed for this revision

In the fresh case directory, inspect the two code hashes and compare them with the digest above:

```powershell
Set-Location 'C:\path\to\fresh\virtual_cohort_system\work\iron_breadth_2026-11-05'
Get-FileHash -LiteralPath '.\candidates\B\initial\generator.py' -Algorithm SHA256
Get-FileHash -LiteralPath '.\candidates\B\final\generator.py' -Algorithm SHA256
```

With the documented isolated worker available, the existing command-line interface is:

```powershell
python .\iron_runner.py --generator .\candidates\B\initial\generator.py --sha256 9ad315b8edd523bf6f4d5ef9b722f2814fa84ca4cfac111074e407f3ae9cce0f --author B --stage initial --mode source
python .\iron_runner.py --generator .\candidates\B\final\generator.py --sha256 9ad315b8edd523bf6f4d5ef9b722f2814fa84ca4cfac111074e407f3ae9cce0f --author B --stage final --mode target
```

The first command requests one source execution; the second requests all three target executions. Both use the unchanged B law. Each attempt records staged-input identities, runtime information, launch details, logs and `execution.json`; successful sampling produces `output/generated.csv`, and the source attempt also produces `source_diagnostics.json`. Output locations follow `private_runs/B/<stage>/source_4101` or `private_runs/B/final/target_<seed>` within the fresh case copy.

Inspect the process exit status and every attempt's receipt. A failed attempt remains a failure with its receipt; a printed command or existing output path does not establish success. Matching the author-program hash establishes code identity, not identical output bytes across untested environments. A later independently performed replay should report its actual environment and results without replacing the historical records.

These commands replay the selected program only. They do not recreate the original author/reviewer conversation, reseal the original study, acquire clinical data or run target evaluation.

## 3. What cannot be recovered by running the code

Q1 records inherited-host dispatches without the exact backend model identity. Q4 records fresh author identifiers and timestamps, and Q5 records fresh author contracts and a shared model service, but those records do not specify complete backend/inference configurations. Iron admission files bind program/model/decision bytes rather than model-service calls. Public Q4 scope excludes conversation contexts and some local audit dependencies. Consequently, the final laws and recorded decisions can be inspected, but the original Agent sessions cannot be fully reconstructed from this release.

The original controller also delegates scientific judgments to reviewers. Reproducing its file checks alone would not reproduce those judgments. Any future authoring reproduction should name the model and configuration actually used, preserve the task and follow-up instructions, and describe the review sequence; it must not retrospectively label historical sessions with a later model name.

## Source pointers for verification

Paths are relative to `biomedical_research/virtual_cohort_system` and refer to retained files. This section is a repository navigation aid, not proposed main-text prose.

- Aggregate-only scope and command: `work/core_workflow_replication_2026-11-04/PUBLIC_SCOPE.md:5–15`; script imports, input hashing and output path: `build_result_display.py:1–27` in the same directory.
- Iron replay policy and fresh-copy requirement: `work/iron_breadth_2026-11-05/REPRODUCTION.md:3–5`; command interface and seed policy: `EXECUTION.md:3–14`.
- B program identity: `work/iron_breadth_2026-11-05/BATCH_LOCK.json`, entries for `candidates/B/initial/generator.py` and `candidates/B/final/generator.py`; authored ABI: `candidates/B/final/generator.py:71–77`.
- Adapter sizes, seeds, bridge and domain checks: `work/iron_breadth_2026-11-05/iron_runner.py:21–47`; hash checking, exclusive attempt creation, sandbox launch and receipts: `:103–156`; exact CLI flags and output directories: `:159–174`.
- Runtime versions and boundary: `docs/EXECUTION_ADAPTER.md:18–36`; fixed configuration and validation: `cohort_harness/execution.py:25–48`.
- Authoring limits: Q1 `FIRST_PAIR_DISPATCH.json:5–26` and `RESULTS.md:52`; Q4 `STATE.json:10–38`, `PUBLIC_SCOPE.md:5`; Q5 `sessions/H01/contract.json`, `RESULTS.md:29`; iron `admission/B_initial.json`, `admission/B_final.json`. See the implementation cards in `METHOD_INSERT.md` for the review-stage differences.
