# Bounded source/target execution bridge v1

This additive bridge dispatches a finite, frozen source/target schedule through
the existing isolated `cohort_harness.execution.run_candidate` adapter. It does
not modify historical harness modules or statistical operators, supply clinical
parameters, import submitted code on the host, run an optimizer, admit a case,
or authorize a campaign release.

The mechanical guarantee is **identical `generator.py` bytes and the complete
scientific model specification except `parameters.active_context`** in every
derived context. All context definitions, assumptions, provenance and numerical
inputs remain identical in the complete specification. Evidence bytes are also
identical. This does not establish Agent authorship, faithful extraction,
source-population reconstruction, compliance of the generator with the declared
scientific structure, or valid transport. Independent review must assess those
scientific matters; the code checks retained commitments and declared structure.

## Frozen parent contract

A normal frozen whole-cohort candidate contains `context_bridge_v1.json`, a
generator, model specification, evidence, decision and checks. It contains no
individual CSV, legacy source-check report or top-level feedback declaration.
Feedback objects live inline in the bridge plan. Registered evidence artifacts
are copied from the exact parent registry prefix into the derived bundles.

`model_spec.parameters` includes:

```text
active_context: <the one declared target ID>
contexts:
  <context ID>:
    population: <description>
    n_rows: <positive finite row count>
    measurement: <description>
    inputs: {<allowed context-varying parameter name>: <Agent-authored value>}
<other shared parameter names>: <Agent-authored content>
```

The bridge plan is exactly:

```text
schema_version: 1
shared_parameters: [all top-level parameter names except active_context, contexts]
context_varying_parameters:
  [{name, reason, evidence_ids, assumption_ids}]
contexts:
  [{id, role, source_ids, assumption_ids, feedback_policy,
    recipe, semantics, supplement}]
trials:
  [{id, context_id, seed, n_rows}]
execution_limits: {timeout_seconds, memory_mb, output_bytes, log_bytes}
budget: {source_attempts, source_rows, target_attempts, target_rows}
```

There are 2–16 distinct contexts, exactly one target, and 2–256 explicit trial
slots. Every context has a scheduled trial. Trial IDs cannot collide by case.
Seeds and resource limits use the existing executor's finite limits. A trial's
rows must equal its frozen context rows; the source/target attempt and row
budgets must exactly equal the complete schedule. These budgets include failed
attempts; they are not counts of successful outputs.

Every context `inputs` dictionary has exactly the declared varying parameter
names. Every other scientific parameter is shared. This restriction describes
where the Agent may declare variation; arbitrary submitted Python could still
ignore or misuse those declarations, and the bridge does not prove otherwise.
The context role, source references and assumptions are frozen. A source
recipe's evidence must cover exactly its declared source IDs; supplementary
checks must reference those same sources. Target source IDs are empty. The
parent task must equal the target descriptor's population and row count.

## Canonical units and feedback

All child task columns, names, order, types, categories, support bounds, scales
represented by the feedback contract, and **units** stay unchanged. The bridge
changes only task population/row count and the specification's active selector.
Measurement descriptions are declared scientific context; there is no assay,
selection, weighting or unit conversion hidden in the bridge.

`feedback_policy` is `none`, `semantic_v1`, or
`semantic_v1_plus_supplement`. A source context must choose a v1 policy.
A target can choose `none`, retaining its validated output and execution
receipt without a scientifically meaningless source comparison. If feedback is
declared, the existing `semantic_feedback_v1` collector is called explicitly.
There is **no fallback** to the legacy collector. Verification additionally
recomputes typed canonical JSON to reject equality such as `true == 1`.

`recipe` is the existing whole-cohort feedback recipe for that exact context;
its measurement mode is `identity`. `semantics` is the existing v1 sidecar with
empty `evidence_sha256` and `recipe_sha256` placeholders. Preparation fills only
these deterministic hashes. The original evidence kind, estimate, uncertainty,
source locator and semantics remain frozen.

For the supplemental policy, `supplement` is the existing
`context_feedback_v1` declaration, with empty task/evidence/specification/v1 hash
placeholders, null `context_review`, and null proxy review slots. Its table
context kind and context ID must match the frozen role. Preparation fills its
hashes; independent supplied reviews fill only the review slots during sealing.
The unchanged supplemental collector checks units, operands, source linkage,
measurement, uncertainty and semantics. It retains its own scope field
`cross_context_generator_linkage: not_supplied_or_verified`; the bridge's
separate receipt supplies only the mechanical cross-context linkage.

The separate `../bridge_units` adapter may apply a reviewed output-to-analysis
unit map downstream. It is not invoked by this bridge and does not extend v1
feedback to mixed units. Its caller must verify the execution and actual task
contracts separately. Neither a unit receipt nor shared generator bytes certify
population or assay transfer.

## Lifecycle and API

With the project root and this directory on `sys.path`:

```python
preflight(bundle, candidate)            # read-only frozen-plan validation
prepare(bundle, candidate)              # derive unsigned draft bundles
requests = binding_requests(bundle, candidate)
seal(bundle, candidate, reviews)        # externally supplied independent reviews
execute(bundle, candidate)              # once, finite schedule, no resume
verify(bundle, candidate)               # no generator launch
```

The only destination is
`<bundle>/context_bridge_v1/<parent-candidate-name>/`. Reservation is exclusive
and happens before preparation. Another destination argument is not accepted.
A second preparation or execution cannot reset this retained parent's budget.
A preparation/sealing failure preserves partial artifacts for inspection and
cannot silently overwrite them. There is no automatic repair, new seed, retry
or additional trial. Host-side deletion or coherent rewriting of an entire
bundle is outside this procedural guarantee; hashes are not signatures or a
global scheduler enforcement mechanism.

Preparation copies the frozen construction and derives every context's task,
selector, feedback recipe and hash bindings. No child is frozen or executed yet.
`binding_requests` verifies the entire draft inventory and returns, per context:

```text
binding: {parent hashes, context ID/role/policy, derived file hashes, trials}
binding_sha256: <independent binding approval commitment>
supplement_sha256: <declaration_digest or null>
proxy_sha256: {<check ID>: <proxy_digest>}
```

The binding includes the frozen parent plan hash, so all other scientific
contexts, shared/varying parameters, trials and budgets are covered too.
Sealing takes exactly one review packet per context:

```text
<context ID>:
  binding_review: <independent approval record>
  supplement_review: <independent declaration approval or null>
  proxy_reviews: {<check ID>: <separate independent proxy approval>}
```

An approval record has the existing supplemental schema:
`decision: approved`, `independent: true`, nonempty `reviewer_id`, `producer_id`,
`reviewed_utc`, `reason`, and exact `approved_sha256`. Reviewer and producer
must differ after whitespace/case normalization. The bridge supplies hashes,
**never approval identities or decisions**. Reviewers inspect the prepared
artifacts, scientific assumptions and binding commitments. All supplied review
records are checked before the first sealing write. Sealing then adds only
those reviews, freezes the children with the real lifecycle, and performs the
real v1/supplement declaration preflights before execution is available.

Execution writes an exclusive attempt intent **before** dispatching each slot.
The existing executor isolates only the submitted generator process, not the
scientific Agent. Failed, timed-out, prelaunch-error and interrupted attempts
consume slots. Other scheduled slots still run after ordinary failures. An
interrupted `execute` call cannot be resumed/retried; untouched slots remain
unexecuted. Every completed attempt binds all retained execution and feedback
files, including partial failure files. Unverifiable early execution receipts
are retained as errors and cannot support generation-link claims. A final
exclusive `completion.json` binds the complete retained file inventory,
including attempt intent/outcome metadata. Unexpected files and directories,
extra runs, changed seeds, altered outputs and changed scientific inputs fail
verification.

The report distinguishes:

- `source_target_generation_link_verified` and
  `all_planned_generation_links_verified`: all scheduled source and target
  generator outputs have verified execution linkage.
- `any_verified_source_target_pair`: at least one verified source/target pair;
  it does not imply all trials succeeded.
- `all_planned_trials_successful`: all scheduled execution and declared
  feedback operations succeeded. A feedback failure can coexist with verified
  generation linkage, which is not promoted to scientific success.
- `status`: `sealed`, `incomplete`, `complete`, or `finished_with_failures`.
  Completed status requires the final completion commitment. Missing outcomes
  remain interrupted/incomplete and consumed.

The CLI exposes `preflight|prepare|requests|seal|execute|verify`, `--bundle`,
`--candidate`, and `--reviews` for sealing. It accepts no comparison table path,
dynamic seed, new destination, arbitrary runtime backend, or optimizer options.

## Invented verification fixture

`invented_fixture.build_parent(new_absolute_path)` creates and freezes an
invented parent without approvals or execution. It declares source 3 rows,
target 6 rows, one shared `scale=1.0` used by the generator, and artificial
`x` values in `example_unit`. An incorrect selector produces the wrong number
of rows. Source feedback exercises v1's unavailable geometric-mean gate and the
existing supplemental descriptive geometric mean with `proxy: null`. Target
feedback is `none`. The fixture is not a clinical construction or source study.

`test_context_bridge.py` uses real lifecycle, v1, supplement and verification
code with only the process/runtime boundary mocked. It does not run submitted
Python, WSL, networking, clinical data or original study retrieval. Its explicit
invented approval records are test scaffolding, not scientific reviews. A real
isolated smoke is a separate root-coordinated bounded operation; unit tests do
not establish sandbox operation or clinical validity.
