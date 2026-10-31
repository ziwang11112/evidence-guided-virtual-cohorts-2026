# Outcome-blind measurement-consistency adjudication

31 October 2026. Status: root proposal, requiring independent implementation/design review before a second preparation attempt. This is a new version; original protocol, code, release and failed attempt remain unchanged.

## Trigger and inspected information

The sole authorized preparation attempt stopped on one aggregate contradiction: anthropometry.P13, not_weighed_with_numeric_weight, count 1. No participant example or value was released, no final reference was written, and no target association/distribution/effect was computed. The original rule correctly required adjudication instead of silently accepting either conflicting field. This document performs that adjudication at the rule level, without investigating whether the participant's biomarker result would favor a model.

## Uniform selected rule

Restrict the analytical reference to internally consistent measurement documentation. Exclude a record from the reference when an explicit not-weighed flag conflicts with a usable numeric weight, or when a documented alternative/non-standing route conflicts with usable standing-field values. Apply this to both age blocks, both ordinal readings, and every record under the same rule. Preserve a separate consistency-exclusion count/reason; do not relabel the numeric value as proven false, infer which field is correct, replace measurements, or rescue the record through the second pair.

This extends the existing documented-quality restriction. It is an investigator eligibility policy for inconsistent records, not a newly discovered official ENSANUT rule. Missing/other documented quality states retain their original treatment. Undocumented or malformed codes, numerical contract failures, identity/linkage failures and other unadjudicated issues still HOLD. All other diagnosis, recorded fasting duration, pregnancy/lactation, standing-route, same-ordinal-pair, sentinel and positivity rules remain unchanged.

The scientific questions, finite demographic standard, 2,000 generated rows, source packet, source/analytical seeds, stability resampling, readiness floors and construction budget remain unchanged. No reference effect or favorable target statistic has informed this amendment.

## Implementation and retry boundary

Create PROTOCOL_v2.md, prepare_reference_v2.py, corresponding tests and a new independent review. Preserve every version-1 byte and receipt. A separate PREPARATION_RELEASE_v2.json must bind the revised protocol/implementation, this adjudication and unchanged input identities. The second attempt must have a distinct attempt/hold/receipt path and may write the intended private reference only if no earlier successful output exists. No attempt receipt may be deleted or overwritten.

Permit exactly one reviewed second preparation attempt under this amendment. Preserve all consistency exclusions, any new HOLD and readiness failure. Do not launch a third attempt automatically. Source generation remains gated on preparation readiness and the separate scientific execution release; target effects remain gated on all final candidates being frozen.

The public builder task must describe the updated consistently documented measurement subset. It must not reveal the observed contradiction count, eligibility counts, individual values or preparation history to scientific builders. Interpretation remains limited to this selected finite reference, not a national-population claim.
