# Finite Wave A campaign control

`campaign_control.py` coordinates K01 and K02 construction, frozen execution slots, one source-feedback opportunity, final output inventory, and a separate target-reveal authorization. It performs no fitting, generator execution, scientific analysis, or measured-target file read. It does not create a clinical release. The API is for the trusted coordinator; constructors receive only `deliver_source_feedback()`'s source-only packet, never the complete ledger, generated target files, target logs, or coordinator verification reports.

Each case reserves A01–A05 and S01, an initial stage, and a possible final stage. Every table has 5,000 rows. Source seeds are 3101–3102 for K01's fixed MIND/Ayele order and 3101–3106 for K02's fixed six-stratum order; target seeds are 2101–2103. `stage_trials()` and `fixed_schedule()` are the executable schedule. Limits per execution are 60 seconds, 1,024 MiB, 2,000,000 output bytes and 10,000 log bytes.

| Case | Reserved source slots / rows | Maximum new source slots / rows | Reserved target slots / rows | Maximum new target slots / rows |
|---|---:|---:|---:|---:|
| K01 | 24 / 120,000 | 22 / 110,000 | 36 / 180,000 | 33 / 165,000 |
| K02 | 72 / 360,000 | 66 / 330,000 | 36 / 180,000 | 33 / 165,000 |

The maximum-new counts assume all five Agents revise once and S01 retains. Retention aliases initial candidate and output identities; it does not execute final slots again. The final target inventory across both cases has **36 entries** (12 constructors × three seeds), while the initial-plus-final target reservation has 72 slots. Failures and unrun slots remain explicit entries. Neither execution success nor an integrity check asserts scientific success.

## Release boundary

`CampaignLedger.create(directory, manifest)` requires an independently reviewed release, verifies its code/design artifact bytes, and permits only the exact resolved `ledger_directory` in that release. A copied ledger cannot be opened at another location and a second create at the same location fails. No actual clinical release or clinical ledger has been created by this component's tests.

The exact release keys are:

```text
schema_version: 1
kind: "wave_a_global_clinical_release"
campaign_id: nonempty string
status: "released"
released_utc: nonempty string
ledger_directory: one resolved absolute directory
designated_evaluator: {path: resolved absolute Python-file path, sha256: SHA256}
schedule_sha256: digest(fixed_schedule())
cases:
  K01 and K02, each with exactly:
    scientific_commitment_sha256
    constructor_packet_sha256
    task_template_sha256
    budget_contract_sha256
artifacts: [{path: resolved absolute code/design-file path, sha256: SHA256}, ...]
review:
  decision: "approved"
  independent: true
  reviewer_id, producer_id, reviewed_utc, reason: nonempty strings
  approved_sha256: release_digest(manifest)
```

`release_digest()` excludes the review record; `digest(manifest)` binds the complete release in ledger receipts. Producer/reviewer IDs must differ after trimming and case folding. All eight case commitments and the designated `.py` evaluator must be present among the artifacts. The minimum runtime artifacts are this controller, `bridge/context_bridge.py`, `production_integration/case_execution.py`, `bundle_assembly.py`, and `k01_sources/k01_sources.py`. The release producer must also include their reviewed scientific and runtime dependency inventory; this minimum is not a transitive dependency scanner. Only code/design metadata extensions are accepted, and private data/document/source directories are rejected. No target dataset belongs in this artifact list.

The designated evaluator must be implemented and independently reviewed before release. `authorize_target_reveal()` permits only that evaluator's exact hash after both case inventories close. It records authorization; it neither executes the evaluator nor reads targets. Evaluator enforcement of this receipt and verification of closed output identities remain the evaluator's responsibility.

## Coordinator sequence

```python
ledger = CampaignLedger.create(release["ledger_directory"], release)
ledger.begin_construction(case, constructor, unique_construction_id)
ledger.bind_stage(case, constructor, "initial", bundle, candidate,
                  derivation_mode="fixed_parameters")
ledger.begin_bridge(case, constructor, "initial")  # durable full allocation debit
try:
    execute_case_stage(bundle, candidate, ledger.directory,
                       case, constructor, "initial")
finally:
    ledger.finish_bridge(case, constructor, "initial")
# K01 coordinator collects its source descriptives before feedback delivery.
packet = ledger.deliver_source_feedback(case, constructor)
ledger.decide_final(case, constructor, "retain", reason)
ledger.close_constructor(case, constructor, reason)
# Repeat closure for all 12 reserved constructors, including authoring failures.
ledger.close_wave_a()
authorization = ledger.authorize_target_reveal(designated_evaluator_sha256)
```

An Agent may choose `revise` once after the single initial source-feedback packet, bind a distinct final candidate with the same task/evidence, and consume its one final allocation. Final feedback is not delivered to the constructor. Identical generator/model bytes must retain rather than resample. Every retained initial stage must have whole-stage verified success. S01 must retain a valid initial stage or stop after failure; it cannot revise. A stopped constructor may close an unrun inventory. A changed final failure cannot fall back to initial outputs. The coordinator must call `finish_bridge()` after a runner exception or process recovery; this records failure without retrying execution.

The runner calls the read-only module function:

```python
verify_dispatch(ledger_path, case, constructor, stage, bundle, candidate)
```

It requires the durable open intent and exact current frozen parent/plan binding, then returns `authorization_sha256`, `release_sha256`, `stage_intent_sha256`, `case`, `constructor`, `stage`, `parent_binding`, and `planned_trials`. The runner saves that authorization. `finish_bridge()` calls actual bridge/case verifiers and requires the saved authorization to match this ledger's exact stage intent. Caller-supplied success booleans are not an API. Whole-stage success requires completed bridge execution, all successful trial statuses, all valid case guards, and all successful guarded slots. Linkage alone is insufficient.

The unchanged bridge executes all source and target slots in one call; this controller adds no source-only pause or hidden resumption. Target context feedback must be `none` at binding. Source delivery re-verifies the retained execution/guard artifacts and the applicable semantic, K01 descriptive or K02 supplemental reports. It yields exactly two K01 or six K02 source entries once, with unavailable entries for failed slots. Valid source slots can be delivered when another slot failed, but partial success cannot qualify for retention. If whole-stage verification cannot be established, all source feedback entries are unavailable.

## Failure accounting and derivation

`begin_bridge()` debits the entire frozen stage allocation before dispatch. A timeout, guard failure, verification failure, early interruption or dispatch failure consumes that allocation; changing candidate/version/path cannot reopen it. The ledger separately reports observed verified attempt records/generated tables. An incomplete stage whose artifacts cannot be verified has unknown physical execution counts, recorded as a verification-failed stage. Reserved/debited slots are never described as proof that all planned runs physically occurred.

Separate analytic jobs are **unavailable**: no isolated job adapter exists, and `reserve_analytic_job()` always fails. A stage may declare `fixed_parameters` or `inline_deterministic`. The latter means reviewed fixed source-only formulas execute inside the existing isolated generator; their repetition follows each actual generator invocation, not an invented successful external-job receipt. The controller records the mode and actual verified run records, but does not instrument formula invocation inside a failed process. The coordinator's prospective operational addendum must authorize this zero-separate-job route before release. It cannot introduce adaptive fitting, favorable-cohort redraws, parameter/seed searches, or extra cohorts.

Receipts use exclusive creation, an OS file lock, fsync, a hash chain, and repeated release-byte checks. These support procedural local accounting and detect ordinary mutation; they are not authenticated signatures, a hostile-host security boundary, or scientific validation. The trusted coordinator and isolated execution system must preserve constructor isolation and target privacy.

## Focused verification

Run from the project root using a fresh, non-existing short `--basetemp` directory:

```text
python -m pytest work/scaleup_2026-11-01/production_integration/campaign_control/test_campaign_control.py --basetemp <fresh-short-temporary-directory> --tb=short -q
```

Tests use invented metadata and replace only the runtime/artifact verification boundary. No source parameters are fit, generator is launched, clinical table is made, target file is read, or genuine approval is fabricated. Coverage includes consumed failures/interruption, same-release ledger reset refusal, fixed schedules, one revision, S01 aliases, invalid retention, stopped-stage dispatch, exact cross-case caps, source-only delivery, saved dispatch authorization, designated evaluator binding, both-case final closure and byte tampering.

Author verification history on 2026-11-02:

1. Default pytest temp root: 31 setup errors in 6.32 seconds from a Windows ACL error; no test body ran.
2. Fresh explicit temp directory: 30 passed and one failed in 4.93 seconds. This exposed the 36 final versus 72 reserved target-slot accounting label; corrected both implementation and assertion.
3. After that correction and a focused Agent-retention/stopped-dispatch test: **32 passed in 4.70 seconds**.

Before the second run, the invented verifier was corrected to return its saved dispatch authorization on repeated verification, matching the real runner instead of requesting a new dispatch after completion. Independent review uses a separate bounded invented coordinator composition; it is not represented as a clinical campaign run.
