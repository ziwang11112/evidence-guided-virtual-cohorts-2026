# Reused literature gateway

Source: `biomedical_research/evidence_gap_loop_2026-10-28/tools/literature_gateway.py`.

Original SHA-256: `e209362f704ad667dd558d3e7b624ce877415e628f65d1fd1cff4aa1614853e6`.

Copied 28 October 2026. The original experiment file is unchanged. This is local project reuse, not a new dependency from an external repository.

One behavioral adaptation in the vendored copy: `Screen.__init__` accepts an empty `compact_aliases` list. The generic task contract permits an empty `excluded_cohorts` list. With no exclusions, the screen applies no invented placeholder rule. Nonempty aliases still require a meaningful alphanumeric representation; all parsing, URL restrictions, document checks, budgets and artifact handling retain the original implementation.

The task adapter lives in `cohort_harness/literature.py`. It supplies the task-bound configuration, fixes the session path, checks accepted artifact events and appends verified artifacts to the bundle registry. The vendor module remains an implementation component, not an authorized alternate tool for builders to create fresh sessions or bypass task budgets.

The session state, audit log, binding and registry are trusted procedural records. They are not authenticated against a malicious user who can rewrite the host filesystem. Exclusion aliases cannot prove the absence of all target-derived evidence or pretraining knowledge.
