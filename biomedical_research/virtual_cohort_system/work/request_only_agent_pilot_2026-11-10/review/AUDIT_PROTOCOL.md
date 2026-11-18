# Post-run audit boundary

Prepared while construction is running; no author feedback is supplied. The frozen runtime, prompts, policies, candidates and receipts remain unchanged.

The audit begins only after all four planned episodes have a durable terminal outcome. `audit_run.py` reads tool journals, search/source metadata, candidate manifests/specifications and API receipts. It does not read credentials, full API response bodies/private reasoning, clinical rows or target reference results, and it does not execute generators.

## Questions

1. Did the model actually search and read evidence? Separate query attempts, accepted search metadata, full-text fetches and pages or tables returned. Preserve exclusions, failed retrievals and incomplete pagination. Returned text is not evidence of comprehension.
2. What numerical statements actually constrain the final generator? Statically trace each main slope, scale and residual-dependence choice to a read source and its measurement, unit, adjustment set and population. Mark direct report, derivation requiring assumptions, free assumption, or unresolved. A source ID alone does not certify a parameter. Use only already acquired article content; do not silently repair evidence gaps with new searches.
3. What changed? Link each candidate to the previous version using code/specification hashes, then inspect scientific changes rather than counting file changes as improvements. Distinguish mechanical repair, numerical-law revision, documentation-only revision and explicit retention.
4. What was actually executed and charged? Match API timestamps/model IDs/token receipts, tool requests/results, fixed diagnostic-seed trials, terminal selection and failed attempts. Keep tariff estimates separate from invoices and conservative reservations.

## Deliverables after closure

- `TOOL_SOURCE_COST_AUDIT.json/.md`: deterministic metadata summary with artifact links; all four episodes retained.
- `SCIENTIFIC_PROVENANCE_AUDIT.md`: concise static source-to-model attribution, with uncertainties and nonidentity transforms identified. This does not substitute for independent source recertification or later numerical evaluation.

The four episodes are two cases with one construction under each policy. They support a feasibility and implementation audit, not a general claim of policy superiority. Repeated candidate versions and generated seeds are not independent agents or clinical studies.
