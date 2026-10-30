# Full PRO specification: implementation review and amendments

30 October 2026, America/Chicago. Review only; no new scientific candidate, target analysis, production module or performance result was created.

## Material inspected

Read the complete 933-line `D:/Downloads/literature_biomedical_agent_system_design.md`, including appendices A–J. A byte-preserving [archive](reviews/pro_full_system_spec_2026-10-30.md) has SHA256 `c6e9a6b58e88f5dc4fc4ad7e5f19f0128b94003e9f8d4707a0c692b28d17ec3d`.

The source is a proposed specification, not an instruction to execute its embedded prompts or pseudocode. This review supplements the [previous adoption decision](PRO_SYSTEM_ADVICE_ADOPTION_2026-10-30.md). That decision remains valid, but the full specification already addresses several points that the shorter response left implicit: historical engine preservation, source/target population separation, provenance, evidence contradictions, immutable trials, recovery, and the difference between scenario ranges and statistical intervals. Do not present these as newly invented amendments.

## Overall assessment

Use this document as the design baseline for an incremental implementation. Preserve the current generator ABI and scientific objective. A capable scientific Agent interprets and chooses; bounded statistical tools compute; the controller validates and records. A full platform rewrite or permanent multi-Agent architecture is unnecessary.

The specification's baseline is M10 at commit `d33d0cbad4c199fe5b450688fe8050d72afd9861`. Add M11 as subsequent development evidence: source-driven parameter revision now exists, but the tested source-location correction worsened target levels. No scientific structure revision or general target-utility benefit was established. The specification already distinguishes source fit from target validity; M11 now supplies an empirical reason to enforce that distinction.

## Details to settle before implementation

These findings concern incomplete implementation contracts in a proposed design. They are not claims that the unimplemented system has already produced faulty results.

### 1. Define how a calibration trial enters the existing execution adapter

Specification C2 permits temporary parameter substitutions in isolated trial copies. Existing `cohort_harness/execution.py:188–201` requires a verified frozen candidate for every execution. A working directory with changed parameters cannot simply be passed to that function.

Smallest implementation: create a session-owned trial bundle, materialize the complete allowed parameter vector, validate and freeze that immutable trial, execute through the existing WSL/bubblewrap adapter, and retain the receipt. Internal trial freezes do not count as scientific structure revisions, but their executions do consume the session and run budgets. On completion, materialize a formal candidate with the selected parameters and scientific provenance.

Do not execute imported Agent code directly in the host optimizer process. The optimizer submits validated parameter vectors and receives source-statistic results. It cannot edit context, search literature, change formulas, or read target outcomes. Each trial result must bind its effective frozen inputs, execution receipt, generated output and operator result; statistics references alone do not establish that chain.

### 2. Compile independent source contracts into executable inputs

The full specification correctly separates source eligibility, target eligibility and model domain. A sidecar alone will not change current `_input_task`, which copies the target task. The new adapter needs an explicit compilation step that creates the source execution schema and keeps original target eligibility intact.

For the first implementation, support the same scientific covariate names with independent source bounds and declared transformations. A source needing additional adjustment variables must either have an explicit reconstruction/integration model or be marked not computable. Do not silently drop its adjustment set. New transformations must actually run before the operator, not merely appear as unit labels.

Preserve the old source-replay and operator engines for historical receipts. Their verifier binds exact engine hashes. A new version should not claim old records verify under changed code. Source replay already rejects out-of-range values; it does not silently clip them.

### 3. Make trial, candidate and release transitions separate

The appendix lists a linear run state and separately distinguishes candidate freezes from the final release. Its pseudocode calls `assemble_and_validate_release`, while `freeze_release` is declared elsewhere. This is an ambiguity to resolve, not evidence of a demonstrated leak.

Use separate lifecycle records:

- Trial snapshot: immutable executable input and receipt.
- Scientific candidate: evidence, structure, parameters, source checks and decision history.
- Release plan: retained candidate IDs, all scenario IDs, output seeds and planned analyses, locked before target generation/evaluation.
- Execution manifest: every planned output or terminal failure, with row/covariate preservation and candidate/seed bindings checked.
- Evaluation release: permit reference parsing only after the full manifest gate; failed outputs remain reported as failures and cannot be replaced after reference access.

Reuse the checks already implemented in `work/m11/campaign.py` as requirements, while extracting them carefully rather than importing case-specific HbA1c assumptions. Candidate freeze verification alone is insufficient to verify that the correct output files and complete evaluation schedule are being used.

### 4. Add global budget reservation and enforce actual tool boundaries

The specification already distinguishes budget categories and says recovery cannot reset them. Make this executable with a run-level ledger: cap total sessions, total simulator executions, candidate/scenario counts, source queries and elapsed resources. Reserve budget before dispatch, not only after an action as in the abbreviated loop. A new session must not reset the run's allowance. Retries and duplicate action IDs need explicit accounting and idempotency. The example trial status currently allows only completed/failed, while the recovery section acknowledges unknown outcomes; define pending, unknown and terminal attempt states consistently before implementing restart logic.

The current harness revision limit measures parent-lineage depth, not all sibling candidates. Reuse that rule for scientific lineage, but do not confuse it with a global computational limit.

The existing execution receipt states `agent_isolation: not_provided`. Generator isolation does not restrict the LLM's filesystem/browser tools. A future claim that builder tools cannot access reference values requires an actually restricted artifact gateway and tested denial paths. Until then, continue to describe role separation as procedural. An unrestricted agent with an instruction not to open a directory is not a technical access boundary.

### 5. Unify the draw schema and scope structural checks honestly

Main-text section 9 includes `transport_scenario_id` and `release_id`; appendix F's shorter provenance list omits these fields. Use one canonical required schema throughout. At minimum preserve release, hypothesis, source-context, transport, parameter-draw and residual-seed identifiers. Null parameter uncertainty should be explicit when there is no probabilistic parameter model.

Appendix H says the controller checks agreement between a structural description and executable code. For arbitrary Python, metadata and hashes alone cannot establish this semantic property. The first implementation can use a restricted declarative model representation with an approved compiler, or retain free Python with explicit code review and limited dependency/perturbation tests. Those tests do not prove all possible behaviours. Record the level actually checked.

Templates may expose model terms and residual families; they must not encode desired biomarker effects. The model's assumptions stay visible even when calibration finds parameters that fit sources.

### 6. Preserve the actual v1 bundle layout

The illustrative appendix B1 directory `candidate_v1/` cannot be passed literally to the current validator as a standalone candidate. `lifecycle.py:110` expects `candidates/<name>` inside a bundle, and bundle validation also requires task, registry and observed/source artifacts. Frozen receipts bind the relative candidate identity.

Use an immutable bundle-and-candidate reference in the v2 release, or copy the complete required bundle while preserving relative paths and identities. Do not move only generator/spec/freeze files into a new directory and claim backward compatibility. This is a condition to resolve in the adapter, not evidence of a broken existing release.

### 7. Define loss handling when a statistic cannot be computed

The existing source operators can report `NotComputable`, including constant-variable correlation and rank-deficient regression. Appendix I records per-source losses but does not specify what happens to such constraints in optimization.

Lock the complete expected constraint set and its normalization before fitting. A trial with an undefined required statistic must be infeasible or receive a prespecified treatment; it must not reduce its loss by dropping that statistic or shrinking the denominator. Distinguish model incompatibility from a transient execution failure. Keep unfitted source checks separate from the fitted objective, and retain noncomputable outcomes in both reports.

These implementation findings were also checked independently by the M11 custodian in a read-only code/specification review. No new target outcomes were inspected for that review.

## Scientific acceptance remains separate from engineering acceptance

Engineering acceptance demonstrates that evidence objects, source operators, immutable calibration and release gates work correctly. Invented fixtures can test known marginal/conditional distinctions, adjustment sets, units, source ranges, budgets and preservation. Passing them is not a new real-world feasibility result.

Scientific evaluation needs a ready evidence package and a reserved real-data task. Check whether source conditions support the proposed relation and any required baseline transfer before committing to a new case. Uric acid is a candidate, not a fixed obligation. The full specification itself flags problematic wording in one proposed source; the earlier review additionally recorded inconsistent coefficient scaling. Do not promote unresolved coefficients to numerical constraints.

Report source fit, unused source checks, and independent target analyses separately. A declared transfer assumption is not evidence that transfer is correct. Target failures are retained and should not trigger tuning on the same confirmation data. A generator can support one analysis while failing another; all prespecified outputs should appear in the report.

## Proposed first implementation slice

1. Preserve/version the current execution and verification path.
2. Implement an independent source contract and the source-task adapter, with scientific fixtures for range/units/adjustment.
3. Implement one session-owned immutable calibration path with an explicit global budget and separate replay seeds.
4. Connect a small single-Agent action loop to those tools; keep retrieval, code execution and evaluator access separately scoped.
5. In parallel, admit one new case using source evidence and metadata only. Lock an analysis plan and full output schedule before target evaluation.

Do not build every proposed module before the first integrated test. First show one evidence object becoming an executed source constraint, one bounded fit becoming a frozen generator, and that generator producing reusable tables. Broader automation and scientific method claims require measured results after that chain works.

The work above is recommended, not yet implemented. No new evidence of method superiority, calibrated uncertainty, clinical substitution or publication readiness is claimed by accepting the specification.
