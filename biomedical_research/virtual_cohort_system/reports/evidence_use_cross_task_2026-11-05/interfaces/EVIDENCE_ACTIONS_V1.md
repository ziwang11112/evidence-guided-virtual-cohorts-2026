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

