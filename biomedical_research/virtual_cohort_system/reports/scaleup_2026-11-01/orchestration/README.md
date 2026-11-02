# Scale-up metadata readiness preflight

This is a new, bounded **readiness validator**, not a campaign runner. It imports
only the Python standard library. It cannot author a candidate, launch a process,
collect source feedback, read a participant table or release target evaluation.
The existing `campaign_plan.json` remains unchanged and blocked: execution is
disabled and the four case identities are unresolved.

The fixed 4 × (5 Agent + 1 reference) × 2 stages × 3 seed schedule comes from
`docs/SCALED_EXPERIMENT_CAMPAIGN_2026-11-01.md`. This version accepts precisely
that schedule, 5,000 rows and the original resource policy. A different design
requires a separately reviewed version, not quietly changing plan counts.

## Invocation and result

From the project root:

```powershell
python reports/scaleup_2026-11-01/orchestration/preflight.py --project-root . --plan reports/scaleup_2026-11-01/campaign_plan.json
```

The existing plan produces JSON with `status:"blocked"`, `inventory_valid:true`,
the 144-slot counts and a release-disabled blocker. Exit 2 means blocked;
exit 0 means `ready_metadata_only`. In either case, `execution_authorized`,
`generator_executed` and `target_data_accessed` are false. Readiness does not
authorize an execution or evaluation, including Wave B.

For a future explicitly released plan, add `--readiness` with the exact
project-relative readiness-release JSON. There is no default release discovery.
The validator first validates inventory and admission. Disabled/unresolved plans
stop **before any readiness file or referenced artifact is opened**. The JSON
reports metadata paths read, counts and the first blocker; it never echoes file
contents. No output file is written by the validator.

## Documented metadata contract, version 1

These are prospective interfaces, not existing approvals or new scientific
criteria. The independent reviewer determines scientific adequacy; this module
checks that the declared requirements are present, consistent and committed.

A released plan preserves the existing schema/schedule but has
`campaign_status:"released"`, `execution_enabled:true` and four admitted cohorts.
Each cohort has a distinct, meaningful `actual_case_id`, nonempty `study_family`,
`admission_status:"admitted"`, a reviewed `reference_exposure_status` of
`unexposed` or `qualified_after_prospective_exclusions`, and a nonempty
`authorized_release` **identifier**. At least three family names are
required. Known CHNS-2009 labels and placeholder labels are rejected, but this is
not a complete historical-exposure registry. Reviewer assessment still governs
cohort identity, prospective exclusions and independence. Qualification is
specific to approved analytical uses; incidental exposure to another result
does not require a false declaration of global blindness. It also does not
automatically reopen CHNS 2009 or another closed development case.

`task_contract`, `evidence_packet` and `analysis_plan` are each exactly
`{"path":"project/relative/file.json","sha256":"64 lowercase hex characters"}`.
Their paths are explicit, never globs. All referenced JSON must be metadata or
admitted aggregate evidence, never participant records. The task's `task_id`
matches `actual_case_id`; mode is `whole_cohort`, `n_rows` is 5000,
`budget.revisions` is 1, information mode is `published_evidence`, and no column
is observed. This is a readiness subset; full harness task/evidence/candidate
validation remains mandatory in a future runner. Evidence and analysis objects
are hash checked, not interpreted or recursively followed. Analysis metadata
must explicitly declare `primary_analysis_ids`: exactly three distinct named
IDs. The scoped exposure approval must name this same set. In particular,
`input_files` inside an analysis plan never causes a read.

The readiness release has **exactly** these top-level keys:

```text
schema_version: 1
campaign_id: biomedical_scaleup_2026-11-01
status: released
plan_sha256: SHA256 of the exact released plan bytes
design: {path: <explicit .md>, sha256: <must equal plan.design_sha256>}
feedback_engine:
  name: semantic_feedback_v1
  artifact: {path: cohort_harness/semantic_feedback_v1.py, sha256: <exact code bytes>}
  legacy_fallback: false
required_gates: {each of the nine existing plan.required_release keys: true}
cases: [four case release records]
independent_review: {path: <explicit .json>, sha256: <review bytes>}
```

The strict engine is hashed, never imported or invoked. The nine gate values
are reviewed **declarations**, not newly implemented admission, scientific
review or orchestration. In particular `campaign_orchestrator_reviewed:true`
must not be supplied merely because this preflight file exists.

The independent review follows the existing F2 procedural approval pattern:
exactly `schema_version:1`, `decision:"approved"`, `independent:true`, nonempty
`reviewer_id`, `coordinator_id`, `reviewed_utc`, `reason`, and `approved_release`.
The identities must differ after case/whitespace normalization.
`approved_release` equals the full release object **without** its
`independent_review` reference, avoiding circular hashes. The plan is bound by
its byte hash; no release path/hash is inserted into that plan. Each cohort's
`authorized_release` is instead an opaque identifier matched below.

Each case release record has exactly `cohort_slot`, `actual_case_id`,
`release_id` (matching `authorized_release`), `reference_arm` and `case_gate`.
The last two are explicit JSON `{path,sha256}` references.

The reference-arm JSON has exactly:

```text
schema_version: 1
case_id: <actual_case_id>
task_contract: <exact same reference as cohort>
evidence_packet: <exact same reference as cohort>
target_row_fitting: false
source_feedback_rounds: 1
extra_simulation_calls: 0
family: <nonempty declared distribution/model choice>
fitting_rule: <nonempty analytical/deterministic aggregate fitting rule>
unhandled_constraints: <nonempty explicit disclosure, including "none" if appropriate>
```

The case-gate JSON has exactly:

```text
schema_version: 1
case_id: <actual_case_id>
independent_validation_eligible: true
exposure_review: {path: <explicit .json>, sha256: <review bytes>}
source_overlap_reviewed: true
adapters_reviewed: true
target_access: closed_pending_separate_evaluation_release
quantitative_use_bundle: <nonempty prospectively specified scientific criterion>
all_five_constructor_rule: <nonempty rule using all five constructors>
primary_analysis_count: 3
secondary_analysis_count: <integer 0 through 2>
```

These strings carry case-specific scientific decisions; the validator does not
invent a tolerance, success threshold or generic definition of biological
validity. The reviewed release binds their exact file hashes.

The hash-bound exposure/overlap review has exactly these fields:

```text
schema_version: 1
case_id: <actual_case_id>
classification: unexposed | qualified_after_prospective_exclusions
decision: approved
independent: true
reviewer_id; coordinator_id; reviewed_utc; reason: <nonempty strings>
prospective_exclusions_applied: <boolean>
approved_primary_analysis_ids: <same three IDs as analysis metadata>
exposed_scope: [{scope_id, description, analysis_ids: [...]}]
excluded_scope: [{scope_id, description, analysis_ids: [...]}]
```

Reviewer and coordinator identities must differ; the classification must match
the cohort declaration. `unexposed` requires empty scope lists and no claimed
prospective exclusion. A qualified case requires both nonempty lists and
`prospective_exclusions_applied:true`. Every exposed/overlapping `scope_id`
must occur in the excluded list, and all its affected analysis IDs must also
be excluded there. Scope descriptions must state the actual exposure and
prospective remedy. A participant-overlap scope may have an empty analysis-ID
list when the remedy concerns excluded participant groups; its named scope
still must be mapped to an explicit exclusion. No participant identifiers or
rows belong in these metadata records.

Approved primary IDs must be disjoint from all exposed/excluded analysis IDs;
the disjointness checks ignore letter case. This explicitly supports an
unaffected conditional use after another relationship is excluded. An exposed
analysis cannot regain qualification merely by changing its ID or cohort
label. The independent reviewer must assess whether any changed population,
evidence exclusion or relationship restriction sufficiently restores the
claimed independence. The validator checks only the declaration and mapping;
it cannot determine semantic overlap between differently named analyses,
prove that participant exclusions happened, or establish biological validity.
No new case has been approved by implementing this contract.

This scoped check covers the declared **primary** analyses only. It does not
confer independence on secondary analyses, undeclared relationships, source
extraction, prior knowledge or the whole cohort. Those claims still need their
own scientific review. The approved metadata, reason and exclusions must be
reported with any qualification; a globally unexposed label is inappropriate
for a qualified case.

## Inventory and retention

Every Cartesian slot must exist once under its canonical
`Kxx_Axx_initial_2101` / `Kxx_S01_final_2103` form. Seeds are 2101–2103;
initial/final stage, wave, arm and evidence access must match the fixed plan.

Allowed statuses are `planned_not_released`, `ready`, `not_run`, `success`,
`failed`, `retained`. The first three have null candidate/output hashes,
execution ID and retention pointer. Success requires candidate/output hashes
and a unique execution ID. Failure requires candidate hash and unique execution
ID, but cannot nominate an output. Metadata `success` does not independently
verify an execution receipt; that remains the existing harness's job.

A `retained` slot is a final-stage alias to the successful initial slot for the
**same cohort, arm, construction and seed**. It reuses that initial candidate
hash and output hash, has `execution_id:null`, and names its initial `slot_id`
in `retained_from`. This schema records retention by reference to the original
candidate; it does not create a new frozen candidate or claim a new sampling
draw. Cross-seed/case aliases, failed origins, cycles and duplicate executions
are rejected. Materialized seeds within a construction stage must share one
candidate hash; a final stage cannot mix retention with newly executed seeds.
Pending/not-run seeds remain visible during partial progress. This inventory
check is not a scientific retention review.

`attempted_slots` counts success + failure. `successful_slots` counts actual
successful executions, excluding retained aliases. `not_run_slots` counts the
three unexecuted/non-alias statuses. `retained_aliases` is separate, and
`unique_outputs` counts distinct non-null output hashes. Thus attempted +
not-run + retained = 144. The other published cohort/construction/stage counts
are recomputed and checked exactly, with Boolean integers rejected.

## Boundaries and verification

Only explicitly named `.json`, design `.md` and fixed engine `.py` artifacts
are read, bounded to 1 MiB each. Traversal, drive/UNC/absolute paths, wildcards,
Windows device paths, symlinks, junctions and hard links are refused. These
checks follow the existing lifecycle path-boundary approach without importing
scientific modules. They are not a sandbox and do not protect against an
adversary changing the filesystem between checks and reads.

Hashes and reviewer identities are procedural commitments, not signatures or
proof of independent review, extraction correctness or cohort non-overlap.
Declared metadata can be mislabeled or coherently rewritten by the host owner.
The false target-access field describes this module's API behavior; it is not
proof that a caller did not put clinical rows into a JSON metadata file.

The future runner still must validate full task/evidence/candidate contracts,
review adapters, enforce the start cutoff, enforce the two-wave continuation
gate and construction budgets, reserve attempts, invoke strict feedback and
close all construction opportunities before a separate target-access release.
Passing this preflight is insufficient for any of those actions. Current
disabled plans do not become released by passing inventory validation.

Focused tests use invented metadata, fake review records and a fake strict
engine that would raise if imported. They cover early rejection without
artifact reads, exact schedule/counts, unsafe paths/links, retention, stale
hashes, independent review, strict engine routing, target-fitting rejection,
case gates and absence of execution/network/nested data reads.

On 1 November 2026 the focused suite passed **51 tests in 0.54 seconds** after
the construction-stage consistency fix. A subsequent defensive change to return
machine-readable rejection for deeply nested invalid JSON was checked with its
new affected test: **1 passed, 51 deselected in 0.04 seconds**. The complete
52-case suite was not rerun. No old scientific suites or generators ran.

After the scoped-exposure correctness fix, only its affected tests ran:
`-k 'scoped_exposure_qualification or release_and_information_gates or success_has_no_execution'`
gave **22 passed, 41 deselected in 0.50 seconds**. This includes approved scoped
qualifications and participant exclusions, rejected unmapped/overlapping scopes,
mismatched primary IDs, missing independent review and concealed exposure.
The full expanded suite was not rerun.

Temporary fabricated fixtures remain under `test_artifacts_run*/`. Automatic
policy rejected their cleanup. They are test-only records, not case admissions
or release approvals; exclude all `test_artifacts_run*` directories from any
public source package. The three deliverable source/document files are
`preflight.py`, `test_preflight.py` and this `README.md`.
