# Independent review of the additive evaluator scalar correction

2026-11-04. **Decision: APPROVE_V2_EXECUTION.** Static review of the exact v1-to-v2 diff and correction manifest finds a bounded implementation correction. This reviewer has not executed either evaluator, read generated tables or opened reference outcomes for this review.

The old exact-type test rejects NumPy float64 values emitted by the frozen CHNS quantile implementation even when finite. The recorded diagnosis lists all fifteen marginal quantiles in the inspected slot. The whole-payload replacement then makes this interface failure appear as unavailable CHNS analyses as well. It is an evaluator failure, not evidence that those generated tables or scientific models failed.

The new predicate accepts finite real numeric scalars while excluding Boolean values; strings, arrays, complex numbers, missing and nonfinite values remain rejected. Conversion to Python float occurs only after endpoint coverage, unit, status and finiteness validation. No endpoint formula, rank policy, numerical tolerance, model, parameter, selected candidate, seed or reference is changed.

The all-four closure gate still executes before any reference read. The correction manifest is then read and every listed artifact hash checked, including the original and corrected evaluators, original completed results, batch closure, CONTROL, protocol, endpoint contract and diagnosis. The new destination is exclusively created as evaluation_v2, and the results bind the correction-manifest hash with an explicit corrected schema version. Original evaluation files and frozen controls remain preserved. Parent-reported five mock tests cover the scalar boundary and existing gates; these successful tests were not repeated.

The later independent numerical audit must explicitly select evaluation_v2 and verify its completion marker/output hashes. It must retain the v1 correction provenance rather than relabel v1 as a successful run. All author decisions remain closed; this correction authorizes no generation or model revision.

Reviewed identities:

- evaluator.py: af7af1512fb5fb45eb0f1aeb3be9bf4ff6ddc70b34c33157f99cd807ec8e8a9f
- evaluator_v2.py: 9515e5b35a4ba38b6dfbbc2f8f3b9d569dcc0db1240dffc4eb8094294947014b
- EVALUATOR_V2_CORRECTION.json: 4965fbe9bc15c4f18122f5ac393a1d52cb3f892448adb66f5466fa0ef2b24f9d
- EVALUATOR_V1_BUG_DIAGNOSIS.json: 71d98e6e428cbb754d68a4ebb3b9dda76a6d89588c5655baef3aba9a91118075
- CONTROL.json: ae31ee07eddabcd592d8cde0a2bcc5326f108a5d2073de83f96ef2e9d2aa3503

Approval is for the implementation correction and its execution. Numerical agreement with a separate implementation remains pending.
