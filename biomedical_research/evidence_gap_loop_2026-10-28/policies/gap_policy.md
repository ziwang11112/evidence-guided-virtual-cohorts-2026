# Consequential evidence-gap/action workflow

Follow the common construction contract, using the same tools, model freedom, total budget and initial/revision schedule as the ordinary workflow. Make the following decision process explicit and operational.

1. Map the evidence needed for intended analyses: conditional location/dependence, relationship shape, relevant modifiers, conditional variability, tails, source selection, measurement and target applicability. Mark irrelevant dimensions as such. Do not require a particular interaction, nonlinear term, sign or distribution merely because it is available.
2. Identify consequential gaps. Separate a usable reported constraint, an assumption-dependent bridge, contextual evidence and missing information. “Not reported” does not by itself establish zero, independence or a constant effect.
3. Rank follow-up actions by the analysis they could change and a concrete obtainable lead. Search for distinguishing evidence or supplements rather than merely adding articles. Where enough source context exists, check the candidate against the statistic under that source's population/measurement/adjustment conditions. If the operator cannot be computed, record that instead of fitting invented data as known.
4. Consider a focused scientific challenge: could another plausible model satisfy the current evidence while changing an intended interpretation? State what information would discriminate it. Do not adopt a more complex alternative merely because it exists; a finite sensitivity set is not a calibrated uncertainty interval.
5. Let evidence and review trigger a concrete action: retrieve, re-extract, check, revise, assess sensitivity, retain or stop with reasons. Distinguish individual residual variability from source population/measurement differences. Reassess previously supported components after a revision.

Required in both `initial/` and `final/`:

`gaps.json`: a nonempty list; each record has `id`, `component`, `affected_analysis`, `evidence_status`, `consequence`, `next_action`, `status`, `resolution`.

Allowed status values: `open`, `acted`, `resolved`, `unresolved`, `not_applicable`. Initial records may be open. Final records must have a non-open status and an explicit nonempty resolution. A resolution can state that evidence remains insufficient; it must not invent certainty.

`actions.json`: a nonempty list; each record has `gap_id`, `action`, `evidence_artifacts`, `model_change`, `reason`.

Allowed actions: `retrieve`, `reextract`, `source_check`, `revise`, `sensitivity`, `retain`, `stop`. `evidence_artifacts` uses run-relative path/hash objects from the actual gateway; a retrieval claim requires at least one real registered artifact. Link actions to gaps. State whether an action changed a parameter, structure, measurement assumption, analysis qualification, or nothing.

Use the review turn for the most consequential attainable correction within remaining budget. Limit countermodel exploration to a focused challenge and explain search saturation. Do not fill the records with decorative steps while leaving their implications unconsidered.

Primary performance concerns the generated data on every reserved analysis, regardless of your support labels. Better qualifications are a separate result; declining every analysis is not success. No source or target relationship is prescribed by this policy.
