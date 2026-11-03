# Group 3 independent review

CHNS2009_E0_A03, selected `candidates/initial`, retain decision: **ready** for the requested implementation and scientific-artifact review. Reviewer: `/root/main_review_g3`. No closure or delivery action was taken.

The generator implements its declared shared-Gamma law. Independent closed-form arithmetic confirms valid positive Gamma residuals, finite moments of every polynomial order, positive-definite population covariance, and the stated model-implied E1/E2/E3 coefficients. Units and task support agree. All 31 marginal source records and the chosen MIND-China anchors trace to registered evidence. E0 has no non-marginal operations, so empty numerical uptake is appropriate.

`lifecycle.verify_candidate(bundle, 'candidates/initial')` passed. Freeze, source, own-trial receipt and decision-linked hashes were checked. Own-trial feedback leaves all 31 source comparisons unavailable with null calculations; it does not use the generated target scenario as a source population. The retained script uses deterministic arithmetic and static parsing only: no generator import/execution, row parsing, random sampling, clinical target results, sibling models or original evaluator outcomes.

Scientific limitations remain: assumed dependence and demographic independence, unvalidated marginal transport and positive unbounded tails, and unquantified source-estimate/structural/transport uncertainty. Readiness does not certify favorable science or target validity.

- Bound review: `evcMS/CHNS2009_E0_A03/independent_review.json`.
- Retained calculation and output: `evcMS/CHNS2009_E0_A03/independent_review_support/review_candidate.py` and `deterministic_audit.json`.
- Candidate freeze SHA-256: `9acce3bcfd615dc71cac090d42261d61d7b6a7c0d782c6b5cf76837dbbeab85b`.
- Decision SHA-256: `c41e2f5314093729680b77f148bbecdac468ad61f2be19df1f5a379d31eb32cd`.

## Additional assigned reviews

The earlier CHNS2009_E0_A03 review remains unchanged. Both newly assigned candidates are **ready**, with no blocking findings. Their independent scripts and deterministic outputs are retained under each candidate root's `independent_review_support/`; reviews are at each root's `independent_review.json`.

| Candidate | Selected action | Independent checks |
|---|---|---|
| ENSANUT2018_E0_A02 | `initial_final` | Verified fixed 375-person demographic cells, lognormal/beta law, finite moments, support, all 17 registered evidence items, empty E0 uptake and 17 unavailable source comparisons. No trial was requested or required. |
| CHNS2009_E1_A02 | `retain` | Verified affine Gamma/uniform/excess law, moments/support in target and separately declared source scenarios, 31 marginal and four relationship records, separate Jansen projections, Bao Pearson arithmetic and contextual-only MIND Spearman. Own-trial bindings passed; all four target-table source comparisons remain unavailable. |

Both `lifecycle.verify_candidate(bundle, 'candidates/initial')` calls and semantic preflights passed. ENSANUT's zero population slopes follow its declared independence assumption. CHNS's E3 age coefficient follows its assumed conditional excess structure; neither is a target result. Source agreement is not transport validation. Distribution, composition, measurement and selection assumptions remain unvalidated, with external-estimate/structural/transport uncertainty unquantified. No generator import/execution, sampling, generated-row parsing, clinical reference access, frozen-file or decision edits, closure, or delivery occurred in these reviews.

ENSANUT2018_E0_A02 bindings:

- Freeze: `3dcec8f8488fd44fa6a91507dd3b933e562eb82f710e05ea9e9ea24164246d4f`.
- Decision: `b3fe7a9408fb2bac64eda4e5a89a796f4dd4b8d7f7efe4f524389008f3a7bb99`.
- Review: `0bfc4121a4cc359b79b0fa14c1fe41acc8d2e06315f0695002101c3e4e5c9b7d`.

CHNS2009_E1_A02 bindings:

- Freeze: `99340f044a9ca9c1b1aecab6ce99ec57b6ff58879b20bb2042512f78998f3abe`.
- Decision: `beeecdca9d63e712645e5c276705df53ab5a49db8fd8c6193d7dfe71212ee1b8`.
- Review: `0316c697516e05692dbc287cdd5f01455370c221a67d5a3a08adb2c8b71487f5`.
