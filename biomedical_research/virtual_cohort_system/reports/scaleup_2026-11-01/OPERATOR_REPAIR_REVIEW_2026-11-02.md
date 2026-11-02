# Independent repair review of the contextual statistics utility

2 November 2026. Additive review following [the original findings](OPERATOR_INDEPENDENT_REVIEW_2026-11-02.md), which remains unchanged. The repaired utility, added tests and README were inspected read-only. No target/source dataset, generator or frozen module was accessed or changed.

**Decision: both reported blockers are resolved in the reviewed bytes. Bounded approval is appropriate for this standalone in-memory arithmetic and declared-context utility.** This is not approval of a campaign adapter, source-population reconstruction, biomedical transfer assumptions or active calibration.

## Repair verification

1. **Categorical ordering cannot change an eligible result under the same scalar commitment.** The shared `_compute` path now rejects `lt`/`le`/`gt`/`ge` unless the selection column is numeric, non-categorical and declared original-scale (lines 145–147). Object-string and ordered-categorical comparisons from the original reproduction are both unavailable. The contract still deliberately omits category order, but only order-independent categorical `eq`/`ne`/`in` remain supported. Both geometric and delegated prevalence calculations pass through this gate.
2. **Unresolved selection scales no longer receive exact eligibility.** Selection scales outside `original` and `categorical` now make the calculation unavailable before selection arithmetic (lines 142–144). The original `not_reported` numeric-selection case, along with natural-log and log10 variants, returns neither a diagnostic nor exact-source eligibility. This is a conservative, documented unsupported-operation boundary; no conversion is guessed.

The README now describes these restrictions and explains why category order need not be committed for the remaining supported predicates. The new tests exercise the unchanged scalar contract with reordered categories, both statistic paths, invalid scales and positive controls. The repair changes no old operator or source-check schema.

## Independent focused checks

Small invented frames re-exercised the original failures and positive controls through `diagnostic`, with matching procedural fixture approvals. Twenty-four diagnostic results were checked across geometric mean and prevalence; this is an inline reproduction count, not 24 new pytest tests or scientific replications.

- Both object-string and reversed ordered-categorical forms of the original inequality now return unavailable with exact eligibility false, despite their identical scalar contract hash.
- Unknown, natural-log and log10 selection scales are rejected on both paths.
- Original-scale numeric selection remains available: selecting two values `[4,16]` gives geometric mean approximately 8, and the strict threshold `x < 5` has prevalence 50% with denominator two.
- Categorical equality, inequality (`ne`) and membership produce identical valid results before and after changing category order.

The author's reported run of the 21 added targeted tests (31 deselected) is consistent with the inspected cases; that pytest command was not repeated. Neither the unchanged 31 tests nor an old full suite was rerun. The original missing-selection `ne` concern had already been resolved by the first review and required no repair.

## Remaining boundary is intentional

The utility still reports unweighted descriptive arithmetic separately from eligibility under an independently approved declared source context. Unknown or weighted source estimators remain ineligible. For example, this repair does not convert a source packet's `not_reported` weighting into `none`, nor does it turn target-population diagnostics into exact source replay. It compares no published estimate, computes no acceptance threshold and estimates no uncertainty. The README continues to distinguish the procedural commitment from authentication, scientific validity and transport verification. These limits match the implementation.

## Approved version hashes

| File | SHA256 |
|---|---|
| `operators/contextual_statistics.py` | `B2E899622802395124D22F6C74975BB3B286F49FE0633D46F1A61290C46D4B3F` |
| `operators/test_contextual_statistics.py` | `421350FE69C847BB336891B9B49BE5A0724576576BA0257743DCB8301142EB4E` |
| `operators/README.md` | `DC80403902EB7BA7CE8331C0C75E47C7578F821B91C831B5FFAFBC1E337C70CA` |

No further implementation or experiment is requested by this bounded repair review.
