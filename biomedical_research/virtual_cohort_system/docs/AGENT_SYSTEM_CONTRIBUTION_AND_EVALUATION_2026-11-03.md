# Agent-system contribution and minimal evaluation

3 November 2026. **Current user-approved direction:** a complete research-demand-driven Agent system for generating useful biomedical data. The proposed 24-table evidence-selection study is optional, not a prerequisite for the paper. This note changes prospective priorities; it changes no frozen experiment or manuscript result.

## The contribution to develop

Researchers may have a scientific question, population description and scattered publications, with optional individual observations. They should be able to request a virtual cohort or additional variables without first designing the entire joint probability model.

The system's proposed contribution is a reusable procedure:

**Research request → evidence acquisition and interpretation → Agent-authored generation → numerical inspection and revision → analyzable data and a concise evidence/assumption record.**

The Agent chooses scientific structure, parameters and evidence use. Deterministic tools calculate, sample and inspect; the controller manages execution and resources. A different request may produce a different generator. Whole-cohort generation without individual input remains central; enrichment and missing-cell completion are additional modes. Neither multiple Agents nor training defines this contribution. See the [accepted adaptive scope](ADAPTIVE_DATA_GENERATION_SCOPE_2026-11-03.md).

Three connected claims can support one paper:

1. **Problem formulation:** turn heterogeneous published biomedical knowledge and a research request into a usable data-construction task.
2. **System method:** delegate consequential scientific choices and appropriate tool use to an Agent across that task, rather than requiring a separately hand-designed generator for each request.
3. **Demonstrated use:** generated data support the requested scientific analyses, with preparation effort, unsupported assumptions and failures reported.

These are candidate system contributions. Autonomy, reduced preparation and broad adaptability require corresponding observations.

## Existing capability versus unfinished integration

| Evidence already available | Boundary |
|---|---|
| The [main-study author contract](../reports/main_study_freeze_2026-11-03/AUTHOR_CONTRACT_TEMPLATE.md) delegates structure, parameters and assumptions to an Agent. | Sources were curated; that comparison allocated no new browsing. |
| The [manuscript](../manuscript/DRAFT_v0_8.md) includes an actual translation from separate adjusted projections into a joint law. | This demonstrates scientific authorship, not autonomous discovery of every source quantity. |
| The [adaptive pilot](../reports/adaptive_reference_pilot_2026-11-03/RESULTS.md) executed tool feedback and scientific revision. | One supplied-reference construction improved rank agreement while slightly worsening three regression discrepancies. |
| [Literature access](../cohort_harness/literature.py) and [recorded scientific decisions](../cohort_harness/scientific_loop.py) have adapters. | The latter does not launch an LLM. Availability is not proof of an integrated autonomous run. |

The minimal [request entry](REQUEST_INTAKE_V1.md) is implemented: two request-only CLI demonstrations and 19 new interface tests passed. A subsequent [bounded live integration](../reports/agent_system_live_2026-11-03/RESULTS.md) actually dispatched two scientific Agents through the host, retrieved originals, executed eight tables and delivered six. The library entry itself still does not launch a model. The live result shows partial analytical utility and a substantive source-population replay gap; it does not certify a general autonomous system.

## Positioning against neighbors

The [prior-method audit](../manuscript/TOP_VENUE_NEIGHBOR_AUDIT_2026-11-03.md) establishes overlapping components, not equivalence of whole systems. G-Sim uses LLM structural proposals with numerical calibration and diagnostic refinement. LLMSynthor uses dependency inference and discrepancy-guided record proposals. Both give LLMs substantive decisions; describing them as purely fixed scientific code would be unfair.

Our intended distinction concerns the complete research task, evidence semantics, autonomy over scientific construction and the amount of preparation required from a user. Published-method inputs and evaluated tasks differ. “Agent” is an appropriate system framing when its decisions and tools are observable; the label alone neither proves novelty nor eliminates contribution. The current work does not establish superiority over either predecessor.

## Smallest integration demonstration

Prepare two request-only fixtures using the already studied variable family:

- **Request A:** complete adult virtual cohort containing age, sex, BMI and HbA1c; request an age/sex-adjusted BMI association.
- **Request B:** add glucose and request the BMI association additionally adjusted for glucose. In the executed case this was central serum glucose with unverified individual fasting adherence, not a verified fasting measurement for every participant.

No desired coefficient, sign or probability family is inserted. These are interface fixtures, not new clinical cases or generation experiments.

The first check is that the same entry produces task-specific author packets, variable/unit requirements, visible analytical goals, permitted literature/execution actions and delivery expectations without case-specific scientific code. Use mocked handlers where necessary and identify them explicitly. Test unsupported capabilities as unsupported. Request preparation alone does not demonstrate retrieval, model dispatch, scientific adaptation or data quality.

After the entry works, specify a bounded actual author/tool demonstration using existing permitted evidence. Preserve all earlier targets as exposed development references. Scientific output evaluation requires a separately frozen run specification; neither this document nor a passing interface test supplies biological validation.

## Evidence needed for the system claim

- **Cross-request reuse:** unchanged orchestration, changes made by the Agent, any coordinator edits and unsupported requests.
- **Preparation burden:** actual source selection, extraction, schema work and scientific interventions by humans or coordinating Agents; count them separately from routine execution. Measure time only when recorded.
- **Data usefulness:** requested effect direction and scale, uncertainty, relevant joint structure and distribution diagnostics. Exact row matching is not the goal.
- **Actual process:** tool calls, failed attempts, retention, revision and delivered versions. A functioning loop need not improve every request.
- **Comparisons:** retain existing reconstruction references; add a published method on compatible inputs when informative. Universal superiority over bespoke statistics is not a prerequisite.

Prioritize connecting and evaluating the complete generation workflow. Introduce an evidence-selection mechanism only if observed workflow failures make it useful.
