# C4 independent preexecution review

**Decision: PASS for the frozen design, controller, and two initial candidates.** The root may issue the separate feedback-phase release for the six scheduled initial-feedback runs. This review is not an election or test release, and does not approve the scientific utility of any generated table. No unresolved preexecution blocker was found.

Reviewed on 31 October 2026 before scientific generation. The reviewer read only public source contracts, admission and commitment metadata, the frozen protocol and plan, controller and relevant harness implementation, recorded controller tests, and initial candidate code and metadata. Candidate code was inspected as text, never imported or executed. Custody contents, hidden analytical operators, hidden truth values, and evaluator results were not opened.

## Frozen bindings

The independent stdlib-only metadata audit completed with PASS and recorded 32 public artifact hashes in `PREEXECUTION_METADATA_AUDIT.json`. It independently compared public files against source admission, task commitment, initial freeze receipts, the execution plan, and root preexecution bindings. All initial frozen files, copied source contracts, task specifications, source registrations, and engine hashes match. Both scientific execution directories and the scientific diagnostics directory contained zero runs or outputs at audit time.

| Artifact | SHA-256 |
| --- | --- |
| `PROTOCOL.md` | `6ab7a04c376fae705bc076caa376a4126f9c1528bb9a3c92e9ebc4358329ac00` |
| `TASK_COMMITMENT.json` | `d9be7d67bb8ffb605928249fd5ab60be56f92a003f6144dae5bbcdd10bd4903a` |
| `method/plan.json` | `4467df703e3222baeeccfe42de5f2871f8288a6ad03fad1e09a8274fa7369e02` |
| `method/controller.py` | `a2d786f3f6842920e65e1ffc3eb186879697394ad00c959fc514c4c5eecfe416` |
| `method/test_controller.py` | `2dcd5b1e0394473ef6eea919072ecc0d3c221f270b03e471ecd5b30b9fb4ed98` |
| `method/test_results.xml` | `51aa0cb97eed265e9268338c21cd6ecfc4ad39e878b2809dd953097c032fb653` |
| Task A initial `freeze.json` | `72a8327cabdf2d73edcad5ef95627cfbefb8e2fbaf51c595409eeffab8b3a9e7` |
| Task B initial `freeze.json` | `c5bfd8fe22dadd598021c48ee6d0c43144d15b6ac07e47ce07c3cc72808086f9` |

## Findings

The final 54-run schedule supersedes the preliminary 72-run design suggestion: six initial-feedback tables, 24 election tables, and 24 untouched final tables. There is no numerical calibration of revisions. Each task supplies one identical four-label pool to all selectors, including duplicates or retained proposals when scientifically justified. Three disjoint seed sets, complete pool freezing before election, selection sealing before test, fixed run identifiers, and separately hash-bound root releases preserve the intended phase separation.

The two public source contracts are explicitly artificial. Task A has nine admitted checks; Task B has eight and leaves one dependence unidentified. The implementation uses every check, sample SD with `ddof=1`, Pearson correlation, and the exact normalized squared-loss formula. The preserved ambiguity in the earlier admission prose is resolved explicitly in the final protocol and agrees with both visible JSON contracts and the implementation.

The protected policy requires every admitted-correlation check to pass on every election draw, together with strict aggregate-loss improvement over the initial candidate. Minimum loss uses the same loss and candidate order. Ties favor the initial version. A failed or nonfinite draw invalidates the entire candidate; missing draws cannot reduce the denominator. All-invalid outcomes retain the initial label with a failure manifest and an unqualified flag. The separate numeric and protected qualification arrays permit truthful qualification of every policy's choice.

Diagnostics are recomputed from verified generated-table and execution-receipt bytes. Source, task, generator, specification, freeze, feedback, pool, method, and sealed selection bindings are checked through the staged workflow. Test release recomputes and verifies the sealed election decision before any test execution. Existing slots cannot be rerun automatically. This is a procedural, hash-checked controller, not a security boundary isolating the Agent author.

Both initial candidates use the same ordinary i.i.d. Gaussian Cholesky program with a single seeded random-number generator. Static inspection found no moment matching, favorable-draw search, seed-specific branches, file or network access, or hidden-evaluator call. Task A copies the admitted full covariance. Task B expressly labels its conditional-independence completion and derived unreported correlation as an assumption; it does not claim that source feedback identifies that choice. No weak initial model or successful revision is imposed.

The recorded final controller suite passes all 38 tests. The reviewer inspected the tests and final results; the suite was run by the execution engineer, not rerun here. Tests cover selector differences and ties, retention, failed and nonfinite draws, full mock staging, absent or stale releases, phase/seed/case errors, diagnostic or table tampering, and rejection of a changed sealed selection. The earlier single failure concerned exact floating-point equality in an aggregation assertion; its log/XML are preserved, and the revised test uses a tight numerical comparison. All backend operations in this suite are labeled mocks. These tests establish controller behavior, not actual generator execution or sandbox effectiveness.

## Limits and next boundary

Task A's unreported projection is mathematically derivable from its admitted Gaussian moments. It tests preservation of an analytical consequence, not recovery of independent scientific information. A source-qualified Task B result may fail under a compatible hidden law; that failure must remain visible. Gate pass alone is not a positive utility result. Identical selections, unchanged proposals, or a policy that always retains are prespecified nondiscriminating outcomes and do not justify replacement tasks or extra proposals.

This PASS binds the listed bytes and the fuller audit manifest. The next authorized control action is the root's feedback release only. After the permitted feedback, revision authorship must stop at the fixed pool; election and untouched testing require their own releases. Runtime output validity and the independent audit of hidden analytical calculations remain future work after their respective boundaries open. This review makes no clinical-validation, general-superiority, or novelty claim.
