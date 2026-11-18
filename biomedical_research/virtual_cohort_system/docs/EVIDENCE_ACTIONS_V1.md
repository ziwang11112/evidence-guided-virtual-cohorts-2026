# Evidence-gap action planning prototype

This optional pure API extends the existing [analysis-evidence declaration](ANALYSIS_EVIDENCE.md). A scientific Agent identifies relationships needed for the requested uses, links source evidence and diagnoses remaining gaps. The planner validates the declarations and turns typed action cards into feasible or blocked proposals. It does not infer meanings from prose, retrieve papers, repair a model or establish better generated data.

```python
from cohort_harness.evidence_actions_v1 import route_evidence_actions
report = route_evidence_actions(
    manifest, cards, task, evidence, spec,
    {"retrieval_phase": "closed", "queries_used": 6, "downloads_used": 4},
    required_analysis_ids=["E1", "E2", "E3"],
)
```

Use the original request for `required_analysis_ids` and actual acquisition state for `availability`. The pure API validates task, evidence, specification and existing manifest schemas. The accompanying source-only replay also checks admitted artifact bytes against the registry and original source commitment. Availability remains caller-supplied procedural information, not authentication or OS isolation.

## Action cards

`cards` has exactly `schema_version: 1` and a `cards` list. Each card contains:

| Field | Meaning |
|---|---|
| `id`, `analysis_id`, `gap_ids` | Unique card ID and scoped analysis/gap references. Every declared gap must appear in exactly one card; a card can group gaps of the same analysis. |
| `diagnosis` | Agent judgment: `missing_relation`, `unverified_bridge`, `context_difference`, `source_conflict`, `undefined_statistic`, `operator_missing`, or `unassessed`. |
| `evidence_ids` | A subset of evidence links in this analysis; locators and artifact references are derived from those items, not invented by the router. |
| `action_kind` | `local_reextract`, `targeted_retrieval`, `operator_review`, `scenario_review`, or `limit_use`. |
| `retrieval_action_id` | Existing analysis retrieval action when targeted; otherwise null. The linked action must cover this card's gaps. |
| `request` | Specific information to recover or review work to perform. |
| `success_criterion` | What would constitute useful information or a completed review; not an effect-direction or target-fit objective. |
| `fallback` | `scenario_review` or `limit_use` if the action supplies no usable information. |

Source conflicts first route to local re-extraction, scenario review or limited use; an optimizer or generic extra search does not resolve a conflicting original statement. Operator gaps route to operator review or limited use. Local re-extraction needs existing linked source artifacts. These category checks do not validate the Agent's diagnosis. Scenario review proposes examining alternatives; it neither creates scenarios nor treats them as a posterior, confidence interval or identified set.

## Budget and lifecycle

Old closed tasks remain closed. An open phase alone does not override task permissions, exhausted quotas or an author's `unavailable` action. Distinct proposed requests receive sequential estimated allocations in author order; identical tool/request pairs can share an estimated allocation. These are planning estimates only: no real budget reservation, source admission or execution occurs. Article fetch estimates conservatively include one query and one download. Supplement fetch needs one download and an already admitted parent, but no search query; supplementary listing can cost auxiliary requests even though its query/download estimate is zero. The live gateway must recheck the admitted parent, auxiliary requests, bytes, exclusions, failed-attempt accounting and actual remaining usage.

Every route retains `gap_status: unresolved`, `executed: false`. Existing support assessments are unchanged. A locally feasible review is not a scientifically resolved relationship. Budget status is not a data-quality score. No automatic controller upgrade or scientific model change is included.

## Current use and next integration

The development replay at `work/evidence_gap_actions_2026-11-05/replay.py` reads only original task/request, evidence/specification, acquisition bookkeeping, source bytes and new Agent declarations. It covers all primary request IDs and additional explicitly named diagnostics across the four existing cases. Previously exposed cases remain development cases; the replay does not provide independent evidence of improved data.

Before a new generation experiment, bind this optional artifact into a new controller version; reserve part of the same total acquisition budget for identified gaps; append a second source packet without changing the first; execute permitted actions through the live adapter; re-evaluate returned evidence and then decide whether a new candidate is justified. This prototype does not reopen old tasks or implement that entire lifecycle. The next useful scientific action should target an actual unresolved statistic, not add more documentation alone.

### 5 November source feasibility increment

A [separate one-file probe](../work/supplement_probe_2026-11-05/RESULTS_ZH.md) has now executed the E01 S2 supplement lead. The original gateway did **not** support its legacy `.doc` format. A bounded additive acquisition/conversion route recovered and independently checked signed source coefficients; the old gateway/session and frozen candidate remain unchanged. The source supports the previously assumed positive signs but leaves outcome-unit interpretation, coefficient uncertainty, transport, glucose-adjusted HbA1c and conditional variance unresolved. This is one completed controller-assisted source action, not a generic live upgrade of this planner or evidence of improved generated data.

The subsequent [Agent-authored source increment](../work/source_increment_revision_2026-11-05/RESULTS_ZH.md) was frozen and tested on three outputs. Source slope/R² ratio use produced a real numerical model change but mixed target-analysis agreement and narrower conditional spread. It demonstrates execution of one controller-assisted evidence-to-model-to-data sequence; it does not establish acquisition-policy superiority or automatically upgrade this pure planner. Preserve the unfavorable outcomes and the distinction between source algebra and target transport.
