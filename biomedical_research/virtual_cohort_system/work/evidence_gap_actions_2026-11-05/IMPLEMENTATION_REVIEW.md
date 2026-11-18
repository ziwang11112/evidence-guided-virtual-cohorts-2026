# Independent implementation review

Reviewed 2026-11-05 by the separate `gap_policy_review` agent. This review covered the new pure router, its existing analysis-evidence/task contracts, the literature adapter and relevant gateway cost paths, and the development replay script. It did not inspect case target outputs, run candidate generators, retrieve literature, or read/create participant rows.

## Validation

Command run from the project root:

```text
python -m pytest tests/test_evidence_actions_v1.py -q
...................................                                      [100%]
35 passed in 0.48s
```

Only the new test file was run. Its fixtures consist of in-memory invented task, evidence, specification and action-card declarations. The existing transported-manifest helper is reused; no prior test suite or case execution is rerun.

The tests cover required-use/gap completeness, same-analysis reference binding, exactly-once gap coverage, unsupported action/claim fields, source-location binding, immutable deterministic planning, closed acquisition, task permission and author-unavailability blockers, consumed budgets, deduplication without permission inheritance, and preservation of unresolved gaps and declared assessments. Operator and scenario routes remain review proposals. Their tests do not establish scientific validity, valid scenario ranges, successful extraction, calibrated uncertainty, improved data, or operating-system isolation.

## Findings and corrections

1. Supplement-fetch planning originally charged a metadata query although the existing gateway requires an already approved parent and then performs one download without a search. The root agent corrected the planning cost to zero queries and one download. The focused regression confirms that a permitted supplement with remaining download budget is proposed for live-adapter rechecking when query budget is zero. A missing parent remains a live-adapter check.
2. The original `shared_proposal_card_id` could identify the first card itself or a blocked identical request. It now appears only on an actual shared proposal. Regressions confirm that ordinary and blocked proposals have no shared-card identifier.
3. Replay path calculations were checked against the directory structure; all four derived bundle directories exist. The script binds source bytes to approved registry entries and acquisition commitments and checks closed task/request/registry/usage inputs. The root agent added the requested narrow bindings for evidence/specification files against their candidate freeze receipt and for the acquisition commitment against its session contract, including author and bundle identity. All integrity assertions now use explicit contract checks. Independent rereading of the final script confirmed these changes. The checks do not open other candidate artifacts or row files.

## Scope judgment

No router blocker remains after the two routing corrections. The function does not execute actions, modify input dictionaries, grant task permissions, reserve real budget, close gaps, or upgrade assessments. Its source locations are declarations until independently checked against registry/file bytes, as its limitations state. Required-use completeness depends on the caller supplying the original request IDs honestly; typed diagnoses and nonempty action prose do not certify the diagnoses or usefulness of the proposed scientific work.

The action union is small enough for this prototype. The meaningful next step remains external work specified by each card: source rereading, a task-permitted targeted retrieval, an operator review, scenario design review, or a restricted-use decision. A structurally valid card is not evidence that any of those actions succeeded.

No static replay blocker remains within this procedural, source-only scope. The actual case replay result is separate from the invented-fixture test result above.

## Completed replay confirmation

Independently inspected only the completed `replay/SUMMARY.json` and four aggregate case reports; the replay was not rerun. The summary completed at `2026-11-05T06:45:09.582683+00:00`. Case counts match the reports exactly:

| Case | Required analyses | Additional diagnostic | Unresolved gaps | Action cards | Retrieval blocked | Local review proposed |
|---|---:|---:|---:|---:|---:|---:|
| C01 | 3 | 1 | 30 | 18 | 2 | 16 |
| C02 | 3 | 1 | 27 | 12 | 6 | 6 |
| E01 | 3 | 1 | 31 | 15 | 8 | 7 |
| E02 | 3 | 1 | 32 | 21 | 2 | 19 |
| Total | 12 | 4 | 120 | 66 | 18 | 48 |

The required IDs are `E1`, `E2`, `E3` for C01/C02 and `Q1_age10`, `Q2_bmi5`, `Q3_bmi5` for E01/E02. All 120 `(analysis_id, gap_id)` pairs are covered exactly once by the 66 cards. Action types total 14 local re-extraction proposals, 18 targeted-retrieval proposals, two operator reviews, 16 scenario reviews, and 16 restricted-use proposals.

Every retrieval proposal is blocked and includes the closed-acquisition blocker. Every other route remains a local review proposal. All route execution flags are false and gaps remain unresolved. Every case reports no retrieval, candidate modification, or budget reservation; estimated remaining budgets are unchanged. Scientific validity remains `not_assessed` and data-quality gain remains `not_tested`.

The summary records source-only scope, no row reading or candidate execution, and 80 unchanged input-hash entries. Those receipt statements are consistent with the reviewed replay code; this aggregate inspection does not add an OS-isolation or independent scientific-validity claim. The separately verified E02 local extraction is documented in `LOCAL_EXTRACTION_REVIEW.md`; it does not retroactively turn the pure router's proposals into execution receipts or close their gaps.
