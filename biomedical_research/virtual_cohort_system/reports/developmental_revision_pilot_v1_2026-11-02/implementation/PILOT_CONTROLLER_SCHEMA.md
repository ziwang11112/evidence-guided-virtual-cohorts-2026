# Developmental pilot controller v1

This additive controller does not author science, schedule models, approve reviews,
read reference results, or alter frozen dependencies. It accepts externally
prepared, frozen and sealed candidates. Its ledger and allowlisted packets provide
a procedural information boundary, not OS isolation of scientific authors.

## Release

`PilotController.create(directory, release)` exclusively creates one ledger.
`PilotController.open(directory)` verifies it without generation. `release` has
exactly these keys:

```text
schema_version: 1
kind: developmental_revision_pilot_release
ledger_directory: resolved absolute path
protocol: {path, sha256}
artifacts: [{path, sha256}, ...]       # reviewed public code/design, no results
initial_packet: {path,sha256}           # designated common author input manifest
engine_sha256: engine_hashes()        # controller and frozen dependencies
runtime_identity: {path, sha256}      # prospective runtime_check identity JSON
source_contexts: [three distinct portable IDs]
target_context: distinct portable ID
source_seeds: [three distinct uint32 integers]
target_seeds: [three distinct uint32 integers]
n_rows: 3000
execution_limits: {timeout_seconds, memory_mb, output_bytes, log_bytes}
author_allowance: {candidate_bytes: 1048576, generator_bytes: 65536,
                   schema_returns: 2}
support_contract: {path,sha256}
required_qualified_checks: [{context_id,check_id}, ...]  # exactly four,
                                                      # covering all three sources
evaluator: {path, sha256}
evaluation: {... frozen evaluator-owned metadata ...}
review: {decision: approved, independent: true, reviewer_id, producer_id,
         reviewed_utc, reason, approved_sha256: release_digest(release)}
```

The release digest excludes only `review`. Every file binding uses an absolute
path and lowercase SHA256. `evaluation.reference_report` and
`evaluation.independent_reference_report` are metadata only: the controller never
opens or hashes those reference files. Other evaluator file bindings, protocol,
public artifacts and engine files are verified on every ledger access. Runtime
identity is checked against the frozen runtime before each source or target phase.
No retry is authorized; interrupted phase allocations are consumed in full.
Live source/target dispatch holds a separate nonblocking execution lock. Recovery
cannot close that phase until its dispatcher releases the lock or exits.
Packet construction, version abort and scientific freeze use the same lock.
Scientific freeze inventories all retained packet files, including incomplete
packets from explicitly aborted deliveries.

The designated initial packet has exactly `{schema_version:1,
kind:pilot_initial_author_packet,task:{path,sha256},evidence:{path,sha256},
registry:{path,sha256},files:[{path,sha256},...]}`. Its files admit only reviewed
JSON/Markdown/text/Python inputs, include the three named task/evidence/registry
bindings, and contain no duplicate paths. Both constructors must match those three
exact byte commitments; provenance must name this manifest SHA256, not another
release artifact. Every original permitted file is copied into both branch packets.

The support contract JSON has exactly `required_contexts` (all four context IDs),
`required_checks` (the support module's release-owned checks), and `definition_ids`.
Required native-view checks include the exact `native_mapping` required by that
module; a mere map name is insufficient. Author assumptions and evidence IDs are
derived from the frozen model and evidence, not prefilled clinical parameters.

Constructors are exactly `A01,A02`; versions exactly
`initial,self_review,source_feedback`. `planned_slots(release)` returns 72 slots:
9 source and 3 target per version. Run IDs are
`{constructor}_{version}_{context_id}_{seed}`. All versions use the same source
and target seeds. Retained versions are executed paired repeats, not aliases or
independent constructions.

## Registration and author provenance

`register_version(constructor, version, bundle, candidate, support, provenance)`
accepts an already frozen/sealed candidate with an opened, unattempted source
phase, including the existing controller's scientific and qualified reviews.
`support` is exactly `{assessment: {path,sha256}, review: <independent review>}`;
the review approves the assessment file SHA256. Obtain the assessment with
`support_assessment(bundle,candidate,release)`. Its exact keys are `schema_version`,
`kind:pilot_support_assessment`, `parent`, `declaration_sha256`,
`support_contract_sha256`, `support_engine_sha256`, and `assessment`. Registration
recomputes this envelope from frozen `support_selection_v1.json`, actual candidate
bytes and the release contract, requires `declaration_checks_pass`, and checks the
independent approval. This binds the reviewer to actual code; declaration arithmetic
alone does not prove the generator's law. The unchanged moment gate still applies.
Unsupported conditional/truncated laws remain unresolved; a surrogate declaration
cannot replace the actual final law.

`provenance` is exactly `{actor_id, context_id, packet_sha256, author_turns,
scientific_opportunities, model_calls, output_tokens, schema_returns, author_trace,
common_correction}`. `author_trace` is a file binding to the retained orchestration
and submission-snapshot record. Model calls and tokens must be null: this service
does not expose them. `author_turns` is an observed positive count;
`scientific_opportunities` is one, or two for an initial common correction;
`schema_returns` is an integer from zero to two. This does not claim token matching.
For an initial candidate,
`packet_sha256` binds the designated common initial packet manifest and
`common_correction` is null or `{rejected_candidate, reason}`. The rejected
candidate is the direct frozen parent; its files and reason remain committed.
The initial depth is 0 without correction or 1 with correction. Branch ancestry
is the accepted initial candidate in the same bundle; each branch has one child
freeze and `common_correction:null`. Distinct author contexts cannot be reused.
Branch packet hashes must equal the actual delivered packet. The generator cap
and total submitted candidate byte cap are checked at registration and verification.

`dispatch_sources(constructor, version)` wraps the existing source-only
controller. A durable pilot intent consumes all nine source slots first. A normal
completion or failure is recorded. After interruption,
`finish_sources(constructor, version)` records available receipts and remaining
unrun slots without executing or retrying. Source packets after a branch version
are never delivered through this API.
Closure stores the authenticated full source packet, complete source bridge and
source-controller file inventories, and support counts for every retained source
table. A malformed partial table retains its hash and an unavailable-count reason.
These counts never upgrade a failed source attempt into a successful attempt.

## Branch packets and choices

`deliver_branch_packet(constructor, branch)` creates a fresh packet inside the
ledger using only fixed candidate filenames from the common initial freeze,
its task/frozen registry prefix/registered source artifacts and common protocol/
support requirements, and (only for `source_feedback`)
the verified **initial** source feedback JSON. It returns
`{directory, manifest, packet_sha256}`. Manifest keys are exactly
`schema_version,constructor,branch,initial_freeze_sha256,numerical_feedback,
source_feedback_sha256,files`; `files` maps copied relative paths to SHA256.
Unknown or extra packet files, mutations, and source-feedback bytes in self-review
are rejected. No arbitrary caller-supplied packet files are accepted.

The numerical file is exactly `{source_feedback:<authenticated existing packet>,
source_eligibility:<retained source gate report>}`. It preserves every source
comparison, unavailable/error record and support count. Its manifest records the
original source feedback SHA256 as well as the actual delivered file SHA256.

`record_branch_decision(constructor, branch, decision)` takes exactly
`{action,packet_sha256,reason,addressed_findings,remaining_limitations}` with
`action` in `retain,revise,stop`. One decision binds the packet actually delivered.
Retain/revise precedes registration; registration verifies unchanged/changed
generator+specification accordingly. Stop closes all 12 branch slots. Decisions
are never inferred from a submitted filename or numerical improvement.

`abort_version(constructor, version, reason)` closes an unregistered version or
an unfinished registration/packet path without replacement. An initial abort
also closes unstarted branches. Registered source phases must be finished first;
this API never erases a consumed attempt or successful output.

## Barriers and target execution

`freeze_scientific_inventory()` requires all six versions registered with closed
source phases or explicitly aborted/stopped, both branch choices or explicit
failure dispositions, and zero target execution. It commits a 72-slot inventory,
source feedback, packet, provenance, review and candidate hashes. No subsequent
registration, source execution, packet delivery or branch change is permitted.

Target eligibility requires the source phase to be `complete`, all nine source
executions successful, every retained frame to pass declared-support and required-
domain counts with exactly 3,000 rows, and all four named qualified checks available
on all three corresponding seeds (12 results). Strict unavailable stays unavailable.
No discrepancy tolerance is imposed. Source-ineligible target slots close as
`not_run` with reasons. Their initial source findings can still support the bounded
revision opportunity. No replacement run is allowed.

`dispatch_targets(constructor, version)` executes only that version's three
target slots with `execution.run_candidate(parent_bundle,parent_candidate,...)`.
Parent task/specification already select the target. Outputs live outside the
source bridge; its completion inventory and feedback remain unchanged. The
controller does not claim full bridge completion. Durable intents consume all
three target slots, including interruption. `finish_targets(...)` closes an
interrupted phase using retained receipts; it never launches a process.
Individual target intent/error events preserve dispatch exceptions; ordinary errors
do not authorize retries or alternate seeds. Target retained support is checked
again; a violation marks the analysis slot failed without altering its rows or the
original execution receipt. All partial target artifacts are committed at closure.

`close_targets()` requires every planned slot closed. It returns:

```text
schema_version: 1
kind: developmental_pilot_closed_inventory
status: closed
scientific_closed: true
release_sha256
scientific_freeze_sha256
inventory_sha256                      # digest of slots
slots: [72 slot objects]
scientific_annotations: {<constructor/version>: <annotation>, ...}  # all six
```

Each slot has exactly `constructor,version,role,context_id,run_id,seed,n_rows,
bundle,candidate,status,output_sha256,execution_sha256,error`. `bundle` is the
actual execution bundle (source child or target parent), or null when unadmitted.
Statuses: `pending,success,failed,timeout,error,interrupted,not_run,aborted,stopped`.
Closed inventories contain no pending slots. Error is null or `{type,message}`.
Output hashes bind retained bytes when present; only `success` authorizes analysis.
Target files are `<bundle>/executions/<run_id>/output/generated.csv` and
`execution.json`. Failed, aborted and unrun slots remain in the denominator.

Each scientific annotation has exactly `candidate_binding` (null or
`{bundle,candidate,parent}`), `analysis_evidence` (null or a file binding),
`support_assessment` (null or a file binding), `source_feedback` (a list of file
bindings), `source_feedback_format:pilot_source_closure_event_v1`, and
`unavailable_reason` (null or a reason). A source-feedback binding points to the
immutable `sources_closed` event: its full authenticated packet is
`event.payload.feedback`, its support/qualified coverage is
`event.payload.eligibility`, and source slots are `event.payload.slots`. The
annotations are frozen before target dispatch and carried unchanged into the
closed inventory, preserving labels, assumptions, gaps and complete source
trade-offs for initial and both final versions.

`authorize_evaluation(evaluator_sha256)` exclusively records authorization after
target closure. `verify_evaluation(evaluator_sha256)` re-verifies release,
scientific closure, every retained source/target receipt and inventory, returning
the closed inventory plus `authorization`. Reference access belongs to the
designated evaluator, after this call. `verify()` returns the current ledger state
and slot inventory without granting evaluation authorization.
After authorization, the evaluator may exclusively create `evaluation/` and
`independent_evaluation/` under the ledger. Those reports are outside the immutable
scientific inventory and do not weaken checks of source/target execution artifacts.
