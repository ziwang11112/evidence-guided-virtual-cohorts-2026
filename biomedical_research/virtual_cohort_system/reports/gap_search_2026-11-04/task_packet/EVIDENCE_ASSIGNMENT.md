# Active assignment: evidence acquisition only

This file clarifies the live scope in RESEARCH_RULES.json. The intake-generated AUTHOR_TASK.md describes a general future construction workflow; its candidate, generator, execution, source-feedback and data-delivery instructions do not apply in this evidence-only stage. The original intake packet is retained as provenance.

Choose your own literature queries and original studies to address the supplied scientific analysis. There is no fixed DOI bibliography or desired result. Deliver SEARCH_LOG.json, EVIDENCE_CANDIDATES.json and EVIDENCE_REPORT.md under reports/, plus permitted local original-source artifacts. Do not construct a generator, fit a model, read reference participants or sample data in this unit. Source-population replay is not required.

The task-bound gateway maintains one immutable session and enforces its own query/download limits. The combined research budget also counts web queries and any fetch metadata lookup. Five serious original-study reviews is a study count; the gateway's five downloads is a separate operation cap. Record supplements and alternate-route downloads individually. Neither count resets the other.

The gateway transport has a 16 MiB response ceiling; this assignment's saved-file allowance is 10 MiB per file and 50 MiB total. Those narrower combined allowances are procedural, not an extra enforcement mechanism in the existing adapter. Inspect available size metadata before large downloads and track actual saved lengths after retrieval; do not knowingly request an over-limit file or silently discard a breach from the ledger. Web browsing traffic is not byte-metered and must not be reported as zero network bytes. Do not reset the session/configuration to change a limit.

For sources outside the gateway, retain the exact original URL, access result and locator. Do not manufacture a gateway approval. Cohort exclusion still applies. Incidental target-derived snippets are logged and excluded, not silently incorporated into evidence. An access failure does not prove that no lawful original-source route exists.
