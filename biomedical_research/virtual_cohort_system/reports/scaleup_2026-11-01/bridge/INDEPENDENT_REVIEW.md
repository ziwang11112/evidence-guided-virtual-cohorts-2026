# Independent review of the bounded source/target bridge

2 November 2026. Reviewer: `/root/context_bridge_review`, separate from bridge
producer `/root/context_bridge_build` and unit-adapter producer
`/root/context_unit_contract`. This is an implementation review and an invented
fixture review, not approval of a biomedical model, source extraction, unit
factor, case admission, or campaign release.

## Decision and scope

The reviewed implementation is suitable for the separately approved, finite
invented source/target smoke. No unresolved implementation finding currently
blocks that fixture. Concrete fixture binding review is complete; actual
isolated execution is pending in this checkpoint. Adapter tests do not establish runtime
isolation or scientific validity.

Reviewed files include `context_bridge.py`, `invented_fixture.py`,
`test_context_bridge.py`, the bridge README, `../bridge_units/unit_conversion.py`,
its test file and README, the design-v1 and implementation-scope documents,
the prior source-context bridge, and the current lifecycle, execution, semantic
v1 and supplemental interfaces. No private target table or target-result
contents, new original study, clinical factor, or campaign state was consulted.
No historical implementation was edited by this reviewer.

Reviewed implementation SHA256 commitments:

| File | SHA256 |
|---|---|
| `context_bridge.py` | `211a9d09be5fdb218e5cfb78eb4f0ef0d7577e8889c6eb55f5e1e677845e5dfc` |
| `invented_fixture.py` | `6582038f84514fecb826ebc346d7318936fac0b6313364d60d1eaaca499f399c` |
| `../bridge_units/unit_conversion.py` | `23ef409eac2b1afd6c4230b6bd9eb4ef47da541a1b7b2644557f44c014ddd6a9` |

## Findings resolved before fixture execution

1. **Independent unit-review identities.** The unit adapter initially compared
   reviewer and producer names without normalization. An independent probe
   accepted `constructor-a` and ` Constructor-A ` as different identities.
   The owner now strips surrounding whitespace and folds case, consistent with
   the existing supplemental review contract. Targeted adversarial cases pass.
2. **Declared source identity.** The bridge initially checked that source IDs
   existed, without ensuring the context's recipe used those sources. It now
   requires exact declared source coverage in source recipes and restricts
   supplemental checks to those same declared sources.
3. **Attempted versus successful work.** The initial summary could label all
   consumed slots complete and treat any successful source/target pair as full
   linkage. Final reporting separates `any_verified_source_target_pair`, all
   planned generation links, all planned successful diagnostic trials, and
   incomplete or finished-with-failures states. A feedback-only failure may
   leave genuine generation linkage verified, without implying diagnostic
   success.
4. **Retained failures and interruption.** Partial execution and feedback
   artifacts now receive an outcome inventory even after an exception. An
   unverifiable early execution receipt is retained as an error with no
   generation-link claim. Final `completion.json` commits all retained files,
   including attempt metadata. Missing outcomes remain incomplete and consumed;
   failed or interrupted attempts cannot be silently retried.

The fixed preparation destination prevents a new output-directory argument
from resetting this retained candidate's finite schedule. Source and target
tasks retain identical columns and canonical units; their population and row
counts may differ. Child generator bytes match the parent, and the full
specification differs only in `active_context`. Preparation derives hashes but
creates no review decisions. Sealing inserts externally supplied commitments
before child freezing and execution. Original semantic v1 is explicitly used
without legacy fallback, with an additional typed JSON check by the bridge.

## Scoped verification

The independent bridge command ran only `test_context_bridge.py` with pytest
caching disabled and a fresh external temporary directory. **37 tests passed
in 24.37 s.** These tests use the real candidate lifecycle, semantic v1,
supplemental collector and verifier, but mock the process/runtime boundary.
They do not execute submitted Python, WSL or networking. The suite covers
preparation and review separation, changed generator/specification/units,
source-ID mismatch, finite budgets, duplicate attempts, partial and invalid
receipts, feedback failures, output and receipt tampering, unexpected artifacts,
and final metadata commitments.

The first independent invocation had **37 setup errors** because the chosen
external temporary parent `D:/Codex/tmp` did not exist. No fixture or assertion
ran. One corrected invocation used the previously nonexistent
`D:/Codex/home/context_bridge_review_20261102_run02`; no prior test output was
overwritten or removed. Its 37 passes are the independent result above.

For the unit adapter, the author initially reported 54 passing tests, and the
reviewer independently ran those **same 54 tests**, passing in 0.53 s. After
the identity finding, the author reported the expanded 56-case suite passing;
the reviewer reran only the affected review selection: **6 passed, 50
deselected in 0.47 s**. These are separate runs, not 108 or 116 unique tests.
All unit tests use invented in-memory arrays and a toy factor of 2.

The historical `execution.py`, `lifecycle.py`, `semantic_feedback_v1.py`,
`operators/execution_feedback.py`, and `operators/contextual_statistics.py`
retain the same SHA256 values recorded at the beginning of review. No old
passing test suite was rerun.

## Proof limits and remaining live check

The bridge establishes retained mechanical linkage, not adherence of arbitrary
generator code to its declared scientific model, faithful evidence extraction,
valid transport, Agent authorship, or protection against coherent host-side
rewriting. Its budget is one exclusive bridge per retained parent candidate;
the campaign controller still governs global scientific budgets.

Generation uses one canonical unit per variable, selected to match the
supported source-native feedback path. The separate unit adapter supplies an
explicit positive multiplicative **target-analysis** view. It does not provide
general mixed-unit source feedback, assay harmonization, changed source
evidence, nonlinear transformations, or derived-variable feedback. The caller
must verify the execution and connect both declared unit contracts to its
actual task and analysis schema. A unit receipt by itself does not authenticate
those caller assertions. Production factors and scientific approvals remain
unactivated.

The final invented helper declares source 3 rows, target 6 rows, seeds 101 and
103, and a shared scale of 1.0 used by the generator. Its x values cycle through
1, 2 and 4. An incorrect selector therefore produces an observable row-count
mismatch. Source geometric mean remains unavailable in v1 and descriptive in
the supplement, with unknown weights preserved and no proxy difference.
Target feedback is absent by declaration. Concrete prepared binding requests
and the separate invented x-times-2 analysis map must be reviewed before the
root coordinator launches the two existing-backend executions. Results of that
real isolated smoke will be recorded separately and added to this review only
after the retained artifacts are independently checked.

## Concrete fixture commitments approved before execution

At `2026-11-02T10:07:08.856382+00:00`, this reviewer inspected the actual
prepared bundle at `D:/Codex/home/tmp/vc_bridge_live_20261102_v1/bundle`, its
frozen parent, source and target tasks/specifications, source recipe/semantic
and supplemental declaration, `SMOKE_PLAN.json`, both unit contracts and the
invented unit-map proposal. Fresh `binding_requests()` verification matched
the saved requests. The source and target row counts were 3 and 6, the frozen
seeds were 101 and 103, and the execution-receipt count was **zero**.

The reviewer then supplied actual scoped fixture approvals in
`context_reviews.json` and `unit_mapping_approved.json`. These are decisions
made after inspection, not approvals emitted by the bridge or derivation
helper. The former identifies `/root/context_bridge_build` as producer; the
unit proposal identifies `/root` as producer. No proxy approval was needed or
issued. Every reason limits approval to the invented finite software smoke,
excluding clinical construction, transport, real unit factors and release.

| Commitment | SHA256 |
|---|---|
| Frozen parent receipt | `60cdefae6dccfb05c29ed2b6dff9a7d8130a8feb98ad9334e998163849b40177` |
| Source binding request | `482886ad6588a677852cbed5f1254c2da800e7e858134e327ff5b916061289f4` |
| Source supplemental declaration proposal | `09fd6a34c89bad6e388ec34f71d9fcc8c8f9e144e8930a61ddaed5f73f0a799e` |
| Target binding request | `91ebdf0580c560476c397d91e0bdce76e949fe90b0468e03c3360a5fa0f8100d` |
| Invented unit-map proposal | `9db7783bd3a00bd68322e3e766df4aa54e2f8585954c4bf37cd13a1bffd04d35` |
| Supplied `context_reviews.json` bytes | `a9208b57ce4702b9a790022b12f59170b1fd8aeb6d13141a721fa053c0243ac2` |
| Supplied `unit_mapping_approved.json` bytes | `5cfa6d47295259405aebf194f3df7a8219301578b07bd806a9ef8edf2019c883` |

The unit proposal maps only x by the invented factor 2, from `example_unit`
to `example_unit_scaled`, retaining identifier, column order, analyte, kind
and original scale. Its input contract matches the prepared canonical target
task. The root coordinator remains responsible for invoking the reviewed
driver and preserving the two execution outcomes. This reviewer did not
execute either generator while issuing the approvals.

## Subsequent live closeout

The pending isolated check above was subsequently completed by the root
coordinator with exactly the two approved attempts. Both succeeded on their
first dispatch. This reviewer then verified the retained bridge, execution,
feedback and unit-view commitments and independently recomputed the invented
arithmetic, without rerunning a generator. Geometric-mean arithmetic and the
explicit target scaling both had discrepancy 0.0. The separate
[`../bridge_smoke/INDEPENDENT_LIVE_REVIEW.md`](../bridge_smoke/INDEPENDENT_LIVE_REVIEW.md)
records that later checkpoint and its hashes. The preceding pending statements
are retained as the pre-execution review history, not the final task status.
