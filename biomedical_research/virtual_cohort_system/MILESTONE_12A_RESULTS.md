# M12-A — Independent source context implementation

Completed 30 October 2026. This implements the first step of the [development plan](docs/IMPLEMENTATION_ROADMAP_2026-10-30.md). It is an engineering result, not a new biomedical validation or a claim that target analytical accuracy improved.

## Change

Added `cohort_harness/source_context.py` and `source_replay_v2.py`. Source eligibility, target eligibility and the generator's declared computational domain are separate objects. Source numeric ranges or category subsets can differ without changing target rules. Both supports must fit the model domain, including generated-variable support.

The adapter executes the same frozen generator and parameters through the existing WSL/bubblewrap path under the independent source task. It verifies inputs, child identity, output contracts and recomputed statistics. All contexts and operator structure are checked before execution. Domain/measurement assumptions remain declarations, not learned applicability guarantees.

This version supports enrichment, identical ordered variable identities/types/units and identity measurement. Unit conversion, additional adjustment variables, population reconstruction, a general calibration session and autonomous Agent control are not yet implemented.

## Verification

- **82 new targeted tests passed.**
- Complete suite: **384 passed, 1 skipped**. The existing symlink fixture requires a Windows privilege unavailable to this account.
- Actual isolated execution passed in addition to mocked tests.
- **14 pre-existing Python engine files** match the previous GitHub export byte-for-byte.
- All **228 M11 curated artifacts** retain their frozen hashes.
- The copied M12-A execution record passed verification after curation.

The invented fixture has target x in 0–6, source x in 7–10, and a model domain covering both. Its hand-specified generator is y = 1 + 2x. It contains no patients and is not an Agent-discovered relationship.

| Check | Result |
|---|---|
| Old source replay | Rejected source x above target maximum |
| New replay | Successful isolated execution |
| Source mean | 18.0, matching the known arithmetic |
| Source regression slope | 1.9999999999999996, matching 2 to numerical precision |
| Target rules | Same source rows still rejected as target inputs |
| Parent task, generator, parameters and freeze | Unchanged |

## Review corrections and retained failures

Independent review found three first-draft issues: malformed operators were rejected too late, source categories were parsed with target types, and context IDs differing only by case could collide. These were corrected before the final run. A further regression found that empty-data preflight missed string-versus-number ordering in filters; explicit scalar-type validation now rejects it before execution.

Tests also exercise output bounds, unavailable runtime without fallback, invalid second contexts, altered/re-frozen children, and recomputed feedback integrity. Initial test runs encountered Windows path-length failures and a missing scratch parent. Fresh short workspace scratch resolved them without changing scientific expectations. A curation call initially used an unsupported candidate-name shorthand; `candidates/initial` verified the unchanged copy. Development records preserve these events.

## Interpretation and next step

This removes a confirmed execution limitation. It does not demonstrate source-to-target transport, biological validity of a declared domain, or improved M11 target performance.

Next is **M12-B: bounded immutable calibration**, with parameter whitelists, fixed constraints, run-level budgets, explicit noncomputable-statistic handling and independent replay seeds. Initial acceptance uses known fixtures. Admit a real-case evidence package in parallel, keeping target outcomes reserved until the generator and complete analysis schedule are fixed.

See the [curated record](reports/source_context_engineering_2026-10-30/README.md) and [interface documentation](docs/SOURCE_CONTEXT_V2.md). Latest biomedical findings remain [M11](MILESTONE_11_RESULTS.md) and [M10](MILESTONE_10_RESULTS.md).
