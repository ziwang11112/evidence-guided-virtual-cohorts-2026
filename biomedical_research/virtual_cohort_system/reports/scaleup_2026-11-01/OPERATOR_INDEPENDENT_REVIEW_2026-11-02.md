# Independent review of the contextual statistics utility

2 November 2026. Read-only review of the new utility, tests and README. No target data, primary-source files, generator or old module was modified. The existing `condition`/`apply_operator` functions were read only to verify the delegated selection semantics. No previously passing suite was rerun. Four focused, invented in-memory cases were executed because static inspection identified two concrete edge cases and the root requested a missing-selection check.

**Decision: request two narrow repairs before approving the utility's source-check eligibility guarantee.** The arithmetic and the stated separation from scientific validation are otherwise appropriately bounded. These findings concern the new utility only; they do not require a broader framework or changes to frozen operators.

## Finding 1 — bind or eliminate categorical ordering effects [P2]

**Locations:** `operators/contextual_statistics.py`, lines 118–128 (`context_contract`) and 138–149 (selection evaluation).

The commitment records scalar cell values but not pandas categorical ordering. The utility allows ordered comparisons against string-valued selection columns. Pandas uses lexical order for an object-string column and the declared category order for an ordered categorical column. The same cells can therefore produce different selected participants without changing the contract or invalidating its approval.

Reproduced with `x=[1,4,16]`, `group=['A','B','C']`, selection `group < 'B'`, identical operator/context/source declarations and the original approval:

| Input representation | Selected x | Geometric mean | Same contract hash | Exact-source flag |
|---|---:|---:|---|---|
| Object strings | 1 | 1 | Reference | true |
| Ordered categorical with categories C, B, A | 16 | approximately 16 | yes | true |

This is an ordinary dtype change, not merely a host user rewriting all approvals. It breaks the README's claim that the approval commits to the relevant inputs determining the statistic.

**Narrow repair:** either reject ordered comparisons for categorical selection values and retain only `eq`/`ne`/`in`, normalize permitted string comparisons to an explicit dtype-independent meaning, or bind and validate the categorical ordering metadata used by evaluation. Add a focused regression test showing that changing category order cannot change the selected result while retaining the same valid approval. Apply the same rule to geometric and delegated prevalence paths.

## Finding 2 — unresolved selection scales can receive exact eligibility [P2]

**Locations:** `operators/contextual_statistics.py`, lines 191–208. The original-scale check at lines 192–193 applies only to the statistic operand; the later source/table equality comparison accepts two identical `not_reported` scale declarations for selection variables.

Reproduced with `x=[1,4,16]`, numeric `group=[20,40,60]`, selection `group > 30`, and `variable_scales['group']='not_reported'` in both descriptors. A matching approval yields a geometric mean near 8 and `exact_source_check_allowed=true` with no eligibility reason. The arithmetic has a defined result, but an unknown scale does not establish that the declared cutoff selects the source population intended by the statistic.

**Narrow repair:** retain the descriptive calculation if useful, but make any unresolved scale needed by a selection predicate ineligible for an exact source check. If explicit transformed selection variables are supported, document and test their semantics separately from unknown scales; agreement between two unknown declarations must not count as semantic resolution. Add a focused test for unknown numeric selection scale, and preferably the equivalent prevalence case.

## Missing-selection concern resolved

The preliminary concern about `selection_missing_policy='exclude'` and a `ne` predicate did not reproduce. The imported `condition()` explicitly combines its predicate mask with `series.notna()`, so both paths exclude missing selection values.

An invented frame with `x=[1,4,100]`, group `['F','F',None]` and selection `group != 'M'` produced:

- geometric mean 2, with two selected/used rows;
- prevalence `x < 5` of 100%, with denominator two;
- one missing-selection exclusion in both outputs.

The wrapper's use of the original frame for delegated prevalence therefore preserves the intended missing-selection behavior for this concern. No redundant change to the old arithmetic is needed.

## Checks and claim boundaries otherwise supported

- Geometric mean uses the stable log definition, rejects selected zero/negative/nonfinite values and requires original-scale numeric operands. Complete-case removal is explicit, rather than an implicit repair.
- Threshold boundaries and denominators reuse the existing arithmetic. The new tests exercise strict/inclusive thresholds and fraction/percentage units.
- Unknown or weighted source estimates cannot acquire exact-source eligibility; an unweighted descriptive result remains separately labeled. No confidence interval is converted to individual spread or precision weight.
- Source/table context mismatches, target/fixture kind, missing approval and changed scalar inputs prevent exact eligibility. Approval strings remain procedural declarations, not authentication or proof of valid transport; the README states this limitation correctly.
- The utility accepts no reported source estimate and computes no fit, loss or validity score. It does not certify original extraction, source membership, generator provenance or source-population reconstruction. `collector_integrated=false` and `scientific_validity='not_assessed'` are consistent with the implementation.
- Existing tests do not cover the two findings above. Their passing status does not resolve these newly reproduced cases. Only targeted repair verification is needed before reconsidering approval; no target experiment or old full-suite rerun is justified by this review.

## Reviewed version hashes

| File | SHA256 |
|---|---|
| `operators/contextual_statistics.py` | `2A7AC21F2E291423854AE0E32CFC24D27EE0F5D5E5814B83B16959066164B366` |
| `operators/test_contextual_statistics.py` | `94A95274672B020989DA805A717F64BCF600A2D6990B0A6EBE24AEBFFA7134E7` |
| `operators/README.md` | `3E569E49C85BEFF4ECEF1D917EA9803D7EFD820070C99212122C6CCBA4BA7357` |

This review applies to those exact bytes. It is not approval of a subsequent repair until that repair is inspected.
