# Evidence-gap-driven generation loop: completed HDL pilot

**Completed:** [Results and decision](RESULTS.md). All forty scheduled output files were generated and evaluated after freezing; independent numerical reconstruction passed. Broad relationships were retained, but the explicit gap/action policy did not demonstrate a stable advantage. Its two builders retained their numerical models, so their revisions did not improve the generated data. See [all analytical comparisons](report/ALL_ANALYSES.md) and [the figure](report/final_analysis_comparison.pdf).

The user requested an implemented Agent loop for identifying missing evidence, retrieving more relevant literature and revising a virtual-data generator, followed by a comparison with a capable ordinary Agent on a fresh public case.

## Scope and current execution

The case is whole-column enrichment of HDL cholesterol in NHANES 2013-2014, with BMI, age and sex observed. Selection used source metadata/access and prior-case inventory before outcome analysis. The staged packet contains 4,885 eligible adults. Source IDs and all true HDL values remain with the custodian. All NHANES-derived outcome evidence is excluded from builder literature access.

Two independently initialized builders per arm produce an initial candidate and a reviewed final candidate. Each version yields five fixed-seed draws: 40 datasets if all scheduled executions succeed. Scientific relationships and parameters are Agent-selected. The controller implements preservation, provenance, action records and state transitions, with no prescribed HDL relationship.

The current pilot uses Agent-authored executable generators so that evidence and model changes can be inspected. Direct row generation, whole-cohort synthesis and partial completion remain in the larger project scope; they are not mixed into this small policy comparison.

LLM construction and review are executed through fresh Codex collaboration agents. The Python tools implement the persistent experiment state, literature access, provenance and numerical execution. This repository is not yet a standalone model-API client that launches those LLM sessions from a single shell command. No relation coefficients are supplied by the coordinator, and no LLM weights are trained.

## Important files

- [Protocol](protocol.json) and [reporting plan](reporting_plan.json): no expected biological directions, composite success threshold or arm-superiority test.
- [Common builder guide](BUILDER_GUIDE.md), [ordinary policy](policies/ordinary.md), and [gap/action policy](policies/gap_policy.md).
- [Controller](loop_control.py) and [runner interface](runner_contract.json).
- [Literature gateway](tools/README.md): independent sessions, cumulative budgets, primary-text and source-linked supplement retrieval, registered approved artifacts.
- [Implementation audit](review/implementation_audit.txt): 18 independent synthetic tests, including a complete four-construction release fixture and provenance tampering checks.
- [Custodian release contract](custodian/evaluation_release_contract.json): target evaluation cannot proceed until every required candidate/review/execution/output commitment is verified.
- [Framework freeze](framework_freeze.json): verified code/configuration and protocol hashes before model submissions.

Participant-level observed, reference and generated data, original identifiers and source fulltexts are local research inputs. They are excluded from the sanitized private GitHub export. Code, aggregate results, decisions, test reports and reproducibility metadata may be exported through the existing reviewed allowlist.

## What is and is not controlled

Both arms have the same strong model configuration, tool access, numerical libraries, maximum literature budgets and one initial/one revision/one external scientific-review schedule. The ordinary Agent may discover gaps and revise freely. The intervention adds an explicit consequential-gap map and verified action history; it does not give the intervention extra source evidence or hidden feedback.

Query/download/tool-time usage is observable. Exact provider revision, model token counts and total reasoning time may be unavailable. Equal caps are not a claim of exact compute equality. Fresh contexts and source screening are procedural isolation on a shared filesystem, not OS-enforced blinding or proof of no pretrained knowledge.

All eight scientific endpoints will be evaluated for every construction irrespective of support labels. Better caveats are distinct from better generated analytical results. Repeated draws are not independent method replications, and a matched direction built into the generator is evidence translation rather than discovery of a new biological fact.

No prior frozen experiment is modified. Target evaluation is deferred until all builders and revisions are finished; revealed results will never be sent back for tuning within this pilot.
