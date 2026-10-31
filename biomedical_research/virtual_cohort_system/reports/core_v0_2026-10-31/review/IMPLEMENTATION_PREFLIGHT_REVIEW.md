# Independent implementation preflight review

Date: 2026-10-31. Scope: read-only review of the compact method, integration plan, task, registry, admitted artificial source, and initial/revision launch prompts. No candidate program was inspected in this review; no generator, test, retrieval or earlier experiment was run. No patient reference or historical candidate/output was read.

Disposition: the bounded design is suitable for candidate assembly. It is not yet an F1 implementation freeze or a claim that the replay succeeded.

The task and prompts agree on whole-cohort generation without observed rows, 768 synthetic rows, exactly 256 rows at each x=0,1,2, group=0, and nonnegative y. Source A is explicitly artificial and contains only six stratum aggregate constraints; its copied SHA-256 matches the admitted value a9a1831c74ef04d7ce97cd012c4c208a9815551cdd248d0762e244e75a5d66d2. No observed.csv is present. Quotas are correctly identified as task design. Source distribution, tails and interpolation remain Agent assumptions rather than supplied laws.

The schedule fixes at most two executions, initial_run and final_run, both seed 26301. It excludes sampling previews, empirical moment forcing, seed selection, replacement after execution failure, local fallback and new retrieval. One retain/revise opportunity is explicit. Same-seed retention is one unique draw, not independent replication or improvement. Source checks are diagnostic; no fit threshold or superiority claim is introduced.

Required wording correction before the method manifest: CORE_METHOD_V0.md says that source_replay "reconstructs supported covariate contexts". The adapter instead executes the same frozen enrichment generator under builder-declared, frozen covariate-only source contexts. It does not scientifically reconstruct those populations. Replace that phrase to retain the documented capability boundary.

Freeze prerequisites still pending at this review:

- Inspect the authored candidate's source extraction, parameter provenance, stochastic construction and six exact selection/operator definitions. Verify that initial checks describe only work actually performed.
- Run native structural validation and existing whole_cohort_feedback._read_plan preflight without importing or executing the generator; independently review numeric operator fields and selection semantics because _read_plan does not fully validate them.
- Bind the actual scientific and controller prompts, task, registry/source, method, plan, relevant implementation/worker bytes and dependency/runtime records before initial execution. The method/protocol are not automatically bound merely by being outside the candidate; the assembly manifest must identify them.
- After actual successful execution, require both verified receipt integrity and status=success. Independently verify quota counts: the native task contract checks x range/type but does not enforce equal stratum counts.
- Verify initial_feedback with expected candidate and run, compare its final-candidate copy byte-for-byte, bind that copy in checks.json, and freeze the true parent-linked retain/revise record. Native lifecycle alone does not authenticate the meaning of an auxiliary report.
- Preserve generator.py and model_spec.json byte-for-byte for retain, and preserve evidence.json and whole_cohort_feedback.json for either decision in this fixture. Never edit the frozen initial directory.
- Complete the prescribed final artifact lineage and independent six-statistic recomputation before deciding F1 ready. Failure or an Agent stop must remain an explicit closeout outcome; do not represent missing stages as completed or launch a replacement run.

No framework code or new tests are needed for these prerequisites. The controller must account for the two-run cap because the native task schema budgets only queries, downloads and revisions. Agent access restrictions and source admission remain procedural, while the existing backend isolates only the generator process. The documents state these limits appropriately.
