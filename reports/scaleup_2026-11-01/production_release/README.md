# Wave A: released whole-cohort construction and source feedback

The scientific question is whether an Agent can turn published study-level evidence, population/measurement descriptions and explicit assumptions into virtual biomedical cohorts that support useful analyses. This wave supplies **no participant records** to the constructors. The Agent authors the joint generator and its parameters; deterministic tools check and execute that submitted program. Each independent construction uses one scientific Agent. Repetition across five constructors tests stability and is not a claim that multi-Agent collaboration is necessary.

## Fixed experiment

K01 uses the admitted HAALSI glucose task; K02 uses the qualified, investigator-context-exposed Turkana lipid task. Each has five independent fresh-context Agent constructions and one prescribed statistical reference. Each stage includes all scheduled source contexts and three 5,000-row target tables with seeds 2101–2103. There is at most one source-feedback decision and one changed final per Agent. Retention aliases the initial output; it does not create another sample. All initial/final target report slots, including failed or unrun slots, will be reported. There are 72 reserved initial/final target slots and 36 final entries across the two cases.

All twelve constructor inventories must close before the designated evaluator can load measured target outcomes. The same three precommitted analyses per case and full resolution grid apply to every output. Available outputs from a failed stage remain reportable diagnostics but do not earn a successful constructor classification. K02 alone cannot enable an expansion. Generated rows do not increase the number of independent patients or cohorts, and generated-sample intervals are not treated as measurement uncertainty.

## Actual interfaces

- `submission/submission.py` delivers an explicit allowlist to a fresh constructor and packages its five authored files. The coordinator supplies no desired scientific relationship. Independent reviews precede freezing and derived context binding.
- `render_feedback_packet` first exposes only authenticated source feedback and asks the original constructor to choose retain/revise/stop. The controller does not presume revision. A separately authorized final packet exists only after a revise decision.
- `run_stage.py` verifies the released dependency inventory, records the nonretryable allocation, invokes the existing isolated guarded runner, computes K01's separately approved source descriptives, and records status without target effects.
- `evaluation/evaluate_campaign.py` is the one release-bound evaluator. Its reference mappings, original analyses, unit mapping, complete inventory accounting and disclosure gates are fixed in advance.

`GLOBAL_RELEASE.json` is bound by the independent `RELEASE_APPROVAL.json`. The release hash is `9d7576d1e5bda2c88f7a58ad590d962184f9236aea66185b40d11942e700e8f7`. It pins 130 code/design artifacts. The local execution ledger is `evcA/ledger` under the workspace. Release approval permits this bounded experiment; it is not a judgment that the generated data are scientifically valid.

## Checks and retained failures

The new submission/evaluation suites comprise 40 distinct invented tests. These supplement, rather than rerun or replace, the earlier component tests. The first actual isolated software smoke failed all five attempts because SciPy was absent; no table was generated. The dedicated runtime received the pinned SciPy 1.16.3 binary without changing NumPy or pandas, and one separate pure bubblewrap special-function check passed. All five failures remain retained. See `runtime/README.md` and `INDEPENDENT_REVIEW.md`.

The first K01/A01 static packaging attempt also rejected a source descriptor shape before candidate creation. The scientific Agent corrected the metadata shape without changing its scientific law. The exact mechanical clarification is retained for all subsequent constructors; original drafts remain local. No failed generation was retried.

## Interpretation and custody

Unknown source weighting and unresolved analysis conventions are not silently repaired. Strict source checks can remain unavailable while clearly labelled equal-weight descriptive comparisons are computed. Such comparisons do not identify missing joint relationships or certify population/assay transport. Source confidence intervals are not individual standard deviations or acceptance bands. All target relationships are still evaluated independently after closure, including unfavourable findings.

Execution status and feedback decisions are in `execution_status/` and `candidate_reviews/`; the current campaign state remains the parent `STATE.json`. Patient-level real and generated tables, complete third-party documents and credentials stay local. Public materials contain code, original documentation, provenance, review records and permitted summaries. No scientific success is inferred from the runtime checks or number of generated rows.
