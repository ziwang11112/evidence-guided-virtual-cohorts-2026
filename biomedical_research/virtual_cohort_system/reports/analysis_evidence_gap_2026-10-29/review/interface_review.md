# Interface review: analysis-specific evidence gaps

Reviewed 2026-10-29. Scope: installed evidence-cohort-generation skill and harness-interface reference; `cohort_harness` contracts, lifecycle, CLI, source checks, source replay and literature interfaces; `docs/SOURCE_CHECKS.md`, `docs/SOURCE_REPLAY.md`, and the literature adapter contract; invented contract-test definitions. No target rows/results, project README, milestone reports, prior experiments, or agent inventory were inspected. No implementation or biological validation was performed.

## Recommended smallest interface

Use an optional **task-owned list of requested analyses** plus a candidate-owned `analysis_evidence.json`. Require one candidate entry per request, including explicitly unassessed requests. A candidate-only list permits silently omitting the difficult analyses. Do not let manifest prose modify the task, approved sources, tool access, or budgets.

```python
validate_analysis_evidence(manifest, task, evidence, model_spec) -> None
summarize_analysis_evidence(manifest, task, evidence, model_spec) -> dict
```

Keep the validator pure: JSON declarations and references only; no row access, generator execution, retrieval, LLM scoring, or target feedback. Use existing `ContractError`, `exact_keys`, `string_list`, `read_json`, and finite-number helpers. Prefer the task optional-field route over a separate uncommitted bundle file. Existing tasks without requests remain valid; require the manifest when requests exist and reject entries for unknown requests.

Minimal records:

| Record | Required information |
|---|---|
| Task analysis request | Stable `id`, description of estimand/use, variable roles (outcome/exposure/covariates or explicitly other), target population/selection/measurement, adjustment set, and needed evidence components. Preserve unsupported requests as descriptions rather than forcing them into an implemented estimator. |
| Candidate analysis | `analysis_id`; evidence links; model assumption IDs; gaps; planned retrieval actions. No numeric confidence, quality score, calibrated support category, or scientific acceptance boolean. |
| Evidence link | Existing `evidence_id`; which requested component it addresses; explanation; **per-link** population, measurement, selection, and adjustment comparisons. Each comparison has `declared_same`, `declared_different`, or `unknown`, a nonempty explanation, and existing assumption references when an explicit bridge is used. |
| Gap | Stable `id`; kind (including joint/dependence, interaction/nonlinearity, population, measurement, selection, adjustment, uncertainty, or other); missing information; consequence for the named use; assumption IDs; action IDs. A declared assumption describes how a model proceeds; it does not close an evidence gap. |
| Retrieval action | Stable `id`; linked gap IDs; exact permitted tool/action or explicitly unavailable action; concrete query/identifier and sought information; planned/unavailable/deferred status plus reason. A plan is never recorded as an executed search. |

Avoid duplicating source estimates, locators, source IDs or artifact hashes in each link: resolve existing evidence IDs against the already validated ledger. Retain comparisons as **author declarations**, not validator findings; identical text, variable names or units cannot establish population/measurement equivalence. Unknown adjustments need an explicit unknown state; an empty list cannot simultaneously mean known-unadjusted and unreported.

The summary should expose mechanically checked coverage, reference integrity, declared gaps, referenced assumptions, known shared `cohort_ids`, and action availability. Fixed output scope: `declarations_and_references_only`; `scientific_validity: not_assessed`; `joint_distribution_identification: not_assessed`. If support labels are required for display, name them `declared_support` and echo their author origin. Never derive them from counts, residual size, source-check success, or seed repetitions.

## Integration findings

1. **Wire both validation paths.** CLI `validate_bundle` (`cohort_harness/__main__.py:31`) and lifecycle `_state` (`lifecycle.py:224`) validate separately. Calling the new validator only from CLI permits direct `freeze_candidate` to bypass it. Both must reject malformed or incomplete requested-use coverage. Existing `freeze` already hashes every candidate file, so no new candidate hash mechanism is needed.
2. **Preserve replay semantics.** `_make_child` copies every frozen candidate artifact, while `_input_task` changes only task population and row count (`source_replay.py:61`, `:132`). Bind requests inside an unchanged task field and retain their original intended target context; do not compare a manifest's target-population string or full task hash with the derived source task. A separate strict task hash in the manifest would break valid replay. Include a replay regression using a request-bearing fixture.
3. **Do not promote weak mappings.** `_check_metadata` (`source_replay.py:22`) and `run_source_checks` (`source_checks.py:202`) compare variable sets and an adjustment subset. They do not establish directed outcome/exposure roles, semantic adjustment equivalence, selection equivalence, or measurement validity. Their `variable_set_matches_source` and `generation_link_verified` flags must not close applicability gaps. The evidence schema itself currently has no directed OLS outcome/term metadata; require a declaration or retain that limitation instead of inferring roles from set membership.
4. **Keep requests immutable once retrieval starts.** The literature gateway binds exact task bytes (`literature.py:_prepare`). Adding request fields to an already initialized task will invalidate that binding. New task creation should populate requests before initialization; historical tasks need no rewrite. Retrieval proposals use the existing fixed session and literal allowed-tool list; unavailable/budget-limited proposals remain visible gaps and do not trigger a new session.
5. **Reuse strict loading and path handling.** `lifecycle.read_json` rejects duplicate keys and NaN; `safe_relative`/`_path` reject traversal, links/junctions and unsafe Windows paths. Do not add permissive `json.load` or a second ad hoc path resolver. A summary that is saved and treated as authoritative needs input hashes and recomputation, or should remain derived output rather than a claimed check receipt.
6. **Keep dependency limitations explicit.** `validate_spec` knows parameter-to-evidence/assumption references but cannot know which parameters a requested analysis uses. If analysis entries name parameter keys, validate them and include their provenance assumptions; report that dependency completeness is declared. Do not claim to have inferred scientific dependencies from generator source or a submitted parameter list.

## Meaningful adversarial tests

Use invented fixture data and declarations only. The highest-value tests are cross-record invariants, not one test per field.

1. **Omission/extra-use attack:** two task requests, one manifest entry; duplicate request IDs; invented request ID. All reject. An explicit unassessed second entry with no evidence and a concrete gap passes structural validation.
2. **Reference laundering:** dangling evidence/assumption/gap/action IDs; duplicate IDs; link to an unapproved source; action marked executed with no actual adapter receipt. Reject dangling/unapproved claims; the minimal planned-only schema rejects execution claims entirely.
3. **Pairwise-to-joint escalation:** means, SDs and all pairwise correlations from even one invented population, then a requested tail probability, interaction, conditional distribution or causal effect. Structural validity must never yield `joint_law_identified`, calibrated confidence, or automatic support. A dependence/transport assumption remains an assumption and its gap remains visible.
4. **Direction/adjustment mismatch:** same variable set but reversed outcome/exposure; omitted confounder; source adjustment unknown versus target adjustment empty. These cannot become machine-confirmed matches. A declared bridge may be recorded, never promoted to biological certification.
5. **Context mismatch:** equal unit labels with different measurement methods; same variable names across differing populations or selection. Require per-link declared differences/unknowns and explicit bridges when used; report the author declaration without asserting its truth.
6. **Duplicate evidence amplification:** duplicate publications with shared declared `cohort_ids`; repeat the same source diagnostic across many seeds. Summary keeps overlap visible and does not increase confidence or independent-evidence count. Empty cohort IDs mean unknown overlap, not independence.
7. **Check-result promotion:** a successful exact source check or verified source replay with zero discrepancy, combined with an unresolved joint/transport gap. Gap and unassessed scientific validity remain unchanged.
8. **Permission/budget boundary:** planned `literature.search` without task permission, zero remaining budget, or prior-only mode. Output records unavailable/deferred action or rejects a claim of permitted execution; no adapter call, session reset, or registry mutation occurs.
9. **Lifecycle parity/tamper:** malformed manifest rejects through CLI validate and direct freeze; valid frozen manifest modification invalidates verify; removing a required manifest rejects; legacy request-free bundles still validate/freeze; source replay with unchanged request contract succeeds under a changed source population/row count.
10. **Parser hardening:** duplicate JSON keys, Boolean schema version, NaN/Infinity, malformed nested values, unknown confidence fields, and path traversal if any artifact references are admitted. Reject cleanly as contract errors rather than incidental exceptions.

A passing suite establishes these representation and linkage rules only. It does not establish exhaustive evidence extraction, truthful comparison declarations, source population reconstruction, joint-law identification, or valid downstream biomedical inference.
