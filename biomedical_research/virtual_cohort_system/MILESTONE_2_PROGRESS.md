# M2 progress: task-bound evidence and real generator execution

28 October 2026. Version 0.2.0. This is an implementation milestone with invented data, not a new biomedical result or evidence that source-check feedback improves scientific analyses. The original M1 report and previous HDL/insulin experiments remain unchanged.

## Outcome

An independent Agent read two artificial study descriptions, authored a stochastic generator and evidence/specification records, and froze its candidate. The new explicit execution command then ran that program in the inspected WSL/bubblewrap environment. Three executions produced valid 128-row tables: two runs with the same seed were byte-identical, and a different seed changed the generated column. All original cells and row order were preserved.

The task-bound publication adapter also performed a real search and full-text fetch. This was a separate transport/provenance smoke check, not evidence for the fictional generator and not an Agent-led scientific evidence-gap experiment.

## Agent and controller responsibilities

The controller supplied the task, allowed input columns, two explicitly invented sources and the execution interface. It did not supply a generator family, program or target outcome table.

The builder independently chose a gamma conditional distribution with mean (2+x)*(1+0.25*group), shape 4 and scale mean/4. It correctly converted both means and individual SDs from the second source's instrument units by dividing by 10. The source anchors constrain moments; they do not identify gamma tails, interpolation, residual independence or transport. The Agent declared these as assumptions. Scientific parameters were fixed across seeds; only residual sampling varied.

The builder used the existing project skill and authoritative contracts, performed static checks and froze the submission. Its generator was not executed by the builder. It was then inspected and executed by the controller through the new adapter. LLM dispatch used a fresh Codex collaboration subagent; no standalone model API launcher, training or model comparison was implemented.

## Implemented components

- A task-bound literature adapter with one persistent session per bundle, exact task tool permissions and query/download budgets.
- Registered article/supplement artifacts must match gateway approval events and hashes. Registration appends without invalidating earlier frozen registry prefixes.
- An explicit execution command for frozen programs, plus a separate execution verification command. Static validate/source-check/freeze/verify behavior remains non-executing.
- A generator-only WSL/bubblewrap backend with curated read-only input/runtime mounts, no broad workspace mount, no network, and only two writable host output files.
- Wall-clock termination, per-process resource limits and bounded retained logs. These are not aggregate cgroup limits.
- Host-side CSV shape/size checks and original-observation validation before accepting a result.
- Preserved execution receipts for valid outputs, invalid outputs, errors and time/resource termination.
- Updated project/installed skill documentation. Global copies match the project and skill format validation passed.

The direct-row route remains valid: it copies and validates a frozen submitted table without executing code. It does not resample that table when a seed changes.

## Actual checks and results

| Check | Result | What it establishes |
|---|---|---|
| Full project test suite | **153 passed, 1 skipped**, exit 0 | Existing contracts plus adapter behavior and negative cases |
| Skipped test | Windows denied creating a symlink fixture (WinError 1314) | This particular OS fixture was not exercised |
| Independent Agent program | 1 construction, 128 invented rows, 3 successful executions | Real handoff from Agent-written program to isolated execution |
| Same seed | Identical CSV SHA-256 on both runs | Reproducibility for this program/input/runtime |
| Different seed | Different CSV SHA-256; observed columns unchanged | Intended residual sampling for this program |
| Controlled failure probes | raise -> failed; observed-cell damage -> failed; loop -> timeout | Failures are rejected and recorded; their receipts verify |
| Runtime probes | Host mount paths absent, write restrictions enforced, external TCP failed | Tested curated generator environment behavior |
| Live literature smoke | Search + explicitly selected version 1 of PMC8825316 accepted | Actual retrieval, provenance registration and usage recording |

Agent program output hashes:

- Seed 20261028 (two runs): 69510f3d693b78bb5bab8e5b8710ff08283f000e053c7d33b3868f3b4b61cede
- Seed 20261029: b580f62bf6733a1b7c7ece369f0cfe9f24314b573c312cd29abd31090fa7ed10

The live fetch initially returned available versions 1 and 2 and required explicit selection. Version 1 was selected for a fixed transport smoke check; this is not a claim that it is scientifically preferable to another version. Final cumulative usage was one query, one download, three auxiliary requests and five HTTP attempts/successes. Metadata and article artifacts were registered. The artificial generator used only the two invented sources, not the fetched publication.

Unit tests with mocked HTTP or mocked execution do not prove real isolation. Separate live probes and actual isolated executions are identified above; they do not constitute a universal sandbox security proof.

## Bugs found during implementation and review

1. The inspected bubblewrap version requires explicit --unshare-user alongside --unshare-all to use --disable-userns. The launch command was corrected and exercised.
2. A non-object worker JSON could raise an uncaught exception and lose the failure receipt. The adapter now type-checks report objects/states and records malformed/deep JSON failures.
3. A completed report with generator_started=false was internally inconsistent. It is rejected.
4. Host pandas parsing initially lacked a cheap structural guard. Streaming header/order/row/field checks now precede pandas, with physical-line and field limits.
5. Worker reports now have a separate 64 KiB cap. Bounded output/log sizes do not imply calibrated scientific uncertainty.

An independent read-only boundary audit found no remaining blocking issue within the stated trusted-controller, generator-only scope after these fixes.

## Evidence locations

Local artifacts (excluded from ordinary code exports):

- work/m2-controlled-agent/candidates/agent_initial/: original frozen Agent submission.
- work/m2-controlled-agent/executions/: three execution records and invented output tables.
- work/m2-controlled-agent/integration_summary.json: aggregate independent preservation/seed checks.
- work/m2-controlled-agent/gateway-smoke-*.json and gateway/: actual literature transport records.
- work/execution-smoke-8aa0fc1e/: real successful execution and mount/network probes.
- work/execution-failure-smoke-8c94996b/: real exception/damage/timeout probes.
- work/m2-runtime-readiness.json: installed versions, environment/probe results and retained failures.
- work/m2-test-run.txt: full test summary.

Portable aggregate metadata and source hashes are in m2_validation.json. Adapter documentation is in docs/LITERATURE_ADAPTER.md and docs/EXECUTION_ADAPTER.md.

## Remaining boundaries

This stage does not complete the full research framework:

- The LLM builder's general file/tools are not isolated by the generator process sandbox. A new locked biomedical confirmation still needs a genuinely restricted builder/tool boundary.
- The caller launches the Agent. A standalone provider/API orchestration adapter is not implemented.
- Source-context generation is not automatically linked to source-statistic check plans; generation_link_verified remains false in those reports.
- No generic locked target evaluator or ordinary-versus-source-feedback comparison ran here.
- No source/structure/transport uncertainty calibration, measurement savings, patient-level recovery or scientific superiority was established.
- The runtime is currently specific to inspected Windows + Ubuntu-24.04 paths. Bubblewrap 0.9.0 came from the Ubuntu base package after the cached updates-package URL returned 404; it is not asserted to be the latest security release.
- Receipts bind recorded bytes; writable worker reports and hashes are not signatures against an adversarial host writer.

The two-source fixture intentionally provides simple moment constraints so interface and execution errors can be diagnosed. It cannot establish effectiveness on heterogeneous biomedical papers, unreported real relationships or independent cohorts.

## Next discriminating step

Connect a declared source-population recipe, a frozen generator execution and a source-statistic operator using verified run artifacts, without manually copying or asserting a table's origin. Let the same Agent receive only that source feedback and choose re-extraction, retrieval, revision or retention. First verify that linkage on controlled development data; then evaluate any scientific benefit on a fresh locked public case with a restricted builder boundary.

Keep ordinary Agent generation as a valid main method. No larger trial matrix, additional model training or HPC job follows automatically from these interface results.

