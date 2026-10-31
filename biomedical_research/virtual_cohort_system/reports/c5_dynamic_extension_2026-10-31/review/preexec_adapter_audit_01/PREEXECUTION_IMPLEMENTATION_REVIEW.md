# C5 pre-execution implementation review

Status: PASS for the bound adapter/controller implementation and protocol. No remaining implementation blocker was found after the narrow source-commitment and controller-abort guards were added. This is not authorization to bypass candidate scientific review, execution commitments, or final-output custody.

## Scope and exclusions

Read the protocol draft, public analysis/output contracts, adapter, adapter tests/README, task setup, fixed controller, exposure clarification, and the native contract/lifecycle/execution APIs used by them. Did not read actual source packets, author scientific parameters, custody contents, analytic answers or evaluator code. No scientific generator, patient-data analysis or real C5 execution was launched. All audit writes are confined to this new review directory.

## Actual checks

| Area | Finding |
|---|---|
| Parent trust | Native execution verification plus explicit successful status and controller-pinned execution-file digest are required. An intact failed receipt cannot become an extension parent. |
| Source bindings | Adapter pins the registry and verifies approved artifact hashes. The amended task setup also verifies the externally delivered custodian-commitment pin and visible artifact hashes; final intake checks the initial author bindings. The controller invokes source verification before sealing/verification. |
| Typed extension | Existing column definitions, units and order must match except the explicit generated-to-observed role transition. New fields must be generated; native task validation applies. Population/row identity changes cannot silently extend the old table. |
| Preservation | Parent CSV bytes are copied exactly. Native output validation checks exact parsed old values, identifiers/order, schema and count. Preservation reports bind verified output and independently recompute native preservation checks. |
| Provenance | Synthetic inputs are not relabelled as measured patients. Completion provenance distinguishes filled and previously observed cells. Hashes establish procedural integrity, not source truth or cryptographic authority. |
| Route-only actions | Reuse/new-population/revise/clarify create records, not child generation. Execution refuses a route-only transition. Agent makes the structured decision; no keyword parser or implicit LLM is implemented. |
| Execution and paths | Agent programs are not imported on the host; only the native isolated generator route is accepted. Runtime substitution is refused. Native workspace path guards reject traversal, unsafe paths, links and parent/source overlap. |
| Budgets | This unit has zero source-query/download/revision budgets. The actual public contract contains nine fixed slots. The root controller enforces that schedule and exclusive start marker; the adapter is not an independent global execution-budget service. |
| Failure closure | A failed attempted slot records all remaining blocked slots, preserves prior results, stops without fill-in runs, and never produces an analytic reveal. Preflight/integrity exceptions have a distinct CONTROLLER_ABORT record and require explicit manual closeout; they do not claim nine-slot completion. |
| Scientific scope | Controller and adapter contain no source regression coefficients, residual scales, covariance formulas or hardcoded desired relationships. Fixed task names, units, seeds and file hashes are procedural. |

## Tests actually run

- 37 adapter tests passed in a new explicit temporary directory. Parent fixture operations exercise native validation of three invented literal rows. Child process backends are mocked; these tests are not new evidence of real sandbox operation.
- Four independent controller failure tests passed before the outer abort-record amendment. Their receipt is preserved as historical verification.
- Eight current independent controller/source-guard tests passed after amendment: early/middle/late failures, execution exceptions, restart refusal, preflight/integrity abort logging, source-content changes, custodian-pin replacement, and changed initial-author commitments.
- No full suite was run. Current test counts are 37 adapter plus 8 guard cases, not 49 distinct tests; the four earlier controller cases overlap the current coverage.

Exact code/document and receipt hashes are recorded in REVIEW_BINDINGS.json. Test fixture/output directories stay local and are not evidence of scientific performance.

## Protocol and exposure qualifications

The final-information comparison is between a full-joint route and a conditional extension under one sequentially informed author. Parent/extension records are paired; the separate joint draws are not paired observations merely because replicate indices match. Adding a covariate can change an adjusted coefficient while exact old-cell preservation remains valid.

The source-access deviation is explicitly disclosed: root inspected the final visible packet during intake before the scientific author's initial freeze. The author was procedurally restricted to the initial packet and reportedly froze before its final-source access. Coordinator blindness and OS-level Agent knowledge isolation must not be claimed. The implementation Agent's earlier exposure to historical project summaries is also disclosed; it authored plumbing, not the scientific candidate. No hidden-answer access is asserted or checked by this code review.

Complete Gaussian evidence already implies the analytic answers. This remains an invented implementation/consistency check, not biomedical validation, algorithm superiority, newly identified biology, or completion of draft-readiness gate F2.

## Remaining prerequisites outside this review

Before actual execution, root must bind the final protocol and reviewed versions, validate the actual candidates and extension-template scientific bytes, obtain the planned independent conditional-mean/variance structural review, and seal the schedule. Nonzero residual spread alone is insufficient. Root owns the nine actual runs; final scientific conclusions require their committed outputs and the independent postrun audit.
