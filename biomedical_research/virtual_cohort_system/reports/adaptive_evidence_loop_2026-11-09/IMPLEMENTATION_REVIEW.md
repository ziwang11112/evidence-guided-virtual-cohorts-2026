# Focused implementation review

9 November 2026. The reviewed fixes pass. This review occurred after the v2 design/engine lock and did not change the author bundle, engines, task, protocol, configuration or locks. It inspected code and immutable commitments, with invented in-memory checks only; it did not inspect target values, generated tables or author scientific choices.

- Internal web/provenance failures now halt. Direct checks covered provenance violations, interruption and local/parser failures. Ordinary encrypted/unsupported PDF, page-limit, parse-timeout, HTTP403 and network-timeout failures remain recoverable.
- A web action calls `web.verify(root)` before recording new acquisition-state bindings. Verification failure follows the halted integrity path.
- Closure derives final selection and executions from verified session actions, rejects extra execution receipts, and checks the exact candidate/seed schedule plus cardinality. The evaluator repeats candidate, selection, slot and disk-inventory checks before accessing the reference. Invented checks rejected extra runs, duplicate slots, altered candidates, altered selection and altered run inventory.
- Independent recomputation now checks both schedule cardinality and set equality. Both strict and descriptive feedback remain mandatory and artifact-bound.
- All 14 design-lock files, 12 legacy engine hashes and 14 new engine hashes match. No historical engine changed.

The locked implementation report records 21 passing controller/evaluator tests; this reviewer inspected their cases and did not repeat the full suite. The JSON companion distinguishes directly observed checks from that reported result.

No unresolved actionable finding was identified in this focused scope. Author quality, source validity, live retrieval success, clinical analysis usefulness and publication approval remain unassessed. This is an implementation review, not a scientific validation result.
