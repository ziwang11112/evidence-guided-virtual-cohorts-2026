# Scientific Agent autonomy for evidence-guided virtual data

User direction, 9 November 2026: give the Agent sufficient freedom. The product remains usable virtual biomedical data for a stated research purpose. A task rubric defines the intended use; skills provide optional reusable procedures. Neither should become a predetermined generator recipe.

## Separate the outcome from the route

| Specify with the research request | Let the scientific Agent decide |
|---|---|
| Population, required variables/units, generation/enrichment/completion mode, intended analyses | Which relevant studies to retrieve and when further retrieval is useful |
| Which real observations must be preserved; which references are permitted calibration inputs or independent evaluations | How to interpret and combine heterogeneous evidence, recording necessary assumptions |
| Output schema and available program/direct-table execution routes | Distribution family, dependence structure, parameters, auxiliary variables and alternative scenarios |
| Available tools, resource allowance and stop conditions | Which skill to load, adapt, combine or skip; whether another calculation is more appropriate |
| Final requested analyses and truthful artifact provenance | Whether to generate, inspect, retrieve, revise structure/parameters, retain or stop next |

The user can reveal the scientific question and authorize real reference statistics for calibration. Independent-evaluation inputs remain distinct when that role is selected. This distinction changes what an assessment establishes; it is not a blanket prohibition on real-data feedback.

## An adaptive workflow

The Agent starts from the research request and available evidence, develops an initial use rubric, then selects the next useful action. It can generate before retrieving every conceivable source, return to retrieval after a diagnostic, try another scientific structure, add a relevant latent variable, or retain a satisfactory candidate. No mandatory agent count, paper count, distribution, relationship sign or ordered skill sequence is imposed.

Diagnostics may evolve as new evidence or computations expose issues. Keep the requested analyses and earlier findings visible. Adding a check is legitimate; silently dropping a failed requested use or retroactively redefining success is not. A genuine new research question gets a new task version.

For example, an adjusted association may reveal missing joint information. The Agent can look for a compatible adjusted estimate or covariance, derive what is implied by admitted statistics, use a scientifically justified alternative construction, or deliver explicit sensitivity scenarios. It is not required to choose any one remedy, assume independence, match an undisclosed target correlation, or add another Agent.

## What changes after the first rubric pilot

The [completed pilot](../reports/rubric_case_pilot_2026-11-09/RESULTS.md) deliberately fixed sources and forbade feedback revision to isolate supplied guidance. Those restrictions do not define the complete system. That pilot found mixed final-data differences and no consistent further benefit of the full procedural guide. It therefore motivates selective use of skills and tool-directed action, rather than a larger universal checklist.

The project-local [analysis-guided-cohort skill](../experimental_skills/analysis-guided-cohort/SKILL.md) now states this autonomy explicitly. Its procedures are a library, not an exhaustive action grammar. Frozen pilot copies, programs, evaluations and the globally installed skill remain unchanged. This is an instruction/design update; it is not a new performance result or a claim that a standalone adaptive controller has been deployed.

## Next implementation unit

The read-only implementation check identified these reusable entry points:

| Capability | Existing implementation |
|---|---|
| Request and generation mode | `request_intake.prepare_request` |
| Task-bound literature search and source/supplement retrieval | `literature.run_literature` |
| Candidate versions and program/direct-table route | `lifecycle.freeze_candidate`, `verify_candidate` |
| Isolated program execution and direct-table validation | `execution.run_candidate`, `verify_execution` |
| Whole-cohort feedback with explicit statistical semantics | `semantic_feedback_v1.preflight`, `collect_feedback`, `verify_feedback` |
| Execution-backed source replay for enrichment | `source_replay_v2.run_source_replay`, `verify_source_replay` |

The action proposal helper `evidence_actions_v1.route_evidence_actions` does not execute retrieval or revision. The older `scientific_loop.py` records `request_evidence` and `revise_structure` decisions, but does not dispatch those branches. Its retain/promotion path is implemented; see [the controller's documented scope](SCIENTIFIC_AGENT_LOOP.md). Existing host orchestration can call the tools, but a general self-running action loop must not be inferred from these decision records. Generator sandboxing does not isolate all Agent file tools, and enrichment replay is not generic whole-cohort or completion replay.

Expose the already implemented literature, isolated generation and statistical-check tools through one usable task session. Give the Agent the research request, available initial evidence and a realistic shared allowance; let it choose the sequence and scientific changes. Keep source identity and actual action/result artifacts automatically, with minimal decision notes. Both program and direct-table paths should remain available where the adapters support them.

Evaluate the final virtual data with the requested analyses and relevant diagnostics, recording evidence acquisition, useful revisions, unresolved assumptions and cost. An inspection tool succeeding or a rubric entry being marked complete is not the final endpoint. The next run needs an explicit new protocol and operational tool manifest; the earlier pilot's zero-retrieval/zero-revision budget is not inherited. No additional clinical generation is launched by this document.
