# Prospective continuation design review

Reviewer: continuation_release_review. Date: 2026-11-03.

**Disposition: design is feasible with the conditions below; no execution release is approved by this review.** The narrow solution is a new, separately reviewed release using the two existing scientific constructions, an explicit historical lineage record, one bounded mechanical metadata repair, and the unchanged execution/evaluation interfaces. No new scientific author, dataset, optimizer, endpoint or general interface compiler is needed.

## Scope and evidence inspected

I read the prior pilot's PROTOCOL.md, NEXT_EXECUTION_REQUIREMENTS.md, ADMISSION_CLOSURE.json and INDEPENDENT_CLOSURE_REVIEW.md; its RELEASE.json and INITIAL_PACKET.json metadata; the released controller and controller schema; the evaluator's pre-reference gate; and the qualified-relationship validator. I also read the evidence-cohort-generation skill and harness interface. I did not execute/import a generator, sample a cohort, open reference-report contents, read participant tables, reopen the old ledger, or modify an old file. This is a design review, not an independent rerun of the prior closure audit or a final review of as-yet-unbound continuation artifacts.

The prior closure records establish 54 source and 18 target allocations aborted unrun, zero draws and zero generated rows, no branch packets/decisions, and no evaluation authorization. They preserve both initial failures and the A02 qualified-review supersession. They also state that the two schema returns and common initial correction allowance were consumed. A future release must not describe those old allocations as pending, transferable, successfully completed or failed generator draws.

## Required resolutions before release approval

### 1. Preserve the distinction between historical authoring and current automatic repair

The unchanged controller's register_version schema accepts only fixed provenance fields. It requires model_calls/output_tokens to remain null; scientific_opportunities to equal 2 for a corrected initial; author_turns to be at least 2; packet_sha256 to name the new release's initial packet; and distinct context_id values across registered versions. Therefore those fields alone cannot describe a zero-fresh-author continuation without ambiguity.

Use the hash-bound author_trace and continuation protocol to define those mandatory numeric fields explicitly as **historical, carried-forward construction counts**, not new calls or renewed allowances. Preserve the historical author actor/context, observed turns, old packet binding and original/corrected submission bindings. Add explicit trace entries for fresh_initial_model_calls=0, fresh_initial_author_turns=0, fresh_initial_scientific_opportunities=0, and the current automatic repair's actual producer, time, script hash and transformation scope. State that the new packet hash is the current approved registration/branch-input contract; it is not evidence that the historical author received that new packet. Historical model-call/token counts remain unknown. Do not fill those controller fields with zero or invent historical counts to pass validation.

The root's deterministic metadata repair is a technical preparation action, not another independent constructor or a third scientific decision. If the intended historical values cannot be corroborated from the existing trace, resolve that discrepancy explicitly before registration; the controller's lower bound is not evidence of actual author turns. Fresh branch contexts must be separate from the historical author contexts, from each other and from the coordinator context that has seen both branches' source information. Branch model-call/token availability must likewise be reported honestly.

### 2. Record the full cross-release lineage; local revision indices are not historical resets

The proposed new reused_parent at local index 0 is a byte copy of the old initial_interface candidate, which itself is an old index-1 correction. The new corrected initial at index 1 must parent that copy; both future branches at index 2 must independently parent the same new accepted initial. That local shape satisfies the existing controller, but the copy is not a fresh index-0 scientific construction.

A release-bound lineage manifest should bind both old original and old corrected freeze receipts, the old release and closure/supersession records, every copied candidate file, the new index-0 receipt and new index-1 receipt. Record old-original -> old-interface-correction -> new reused copy -> new metadata correction, with branch ancestry added when available. The old files and receipts remain in place. Re-freezing produces a new lifecycle commitment, not a replacement historical receipt. A02's revoked approval must not become valid because the candidate was copied.

Provide a per-file old-to-new equality/difference record. Require generator.py, model_spec.json, evidence.json, scientific-validity/final-law declarations, support_selection_v1.json, and other scientific baseline declarations to be byte-identical. Review every allowed difference in qualified_plan_v1.json and check/static-report metadata. Do not copy an old check result and present it as a newly executed check. Fresh checks must state their actual inputs, scope and outcome; retained checks must identify their historical provenance.

### 3. Make the newly authorized budget explicit and finite

The new ledger at evcDC/ledger is a separate allocation of at most 54 source and 18 target tables, 3,000 rows each, with the same three source contexts, target context and seeds. The old evcDP ledger stays closed and all its 72 dispositions stay in the process denominator. This is neither a resume nor a transfer of unused quota. Do not aggregate the two releases as 144 generator attempts: the prior 72 were unrun allocations.

The continuation protocol must explicitly allow the one automatic alias correction before admission, with zero fresh initial scientific construction. The fixed author_allowance.schema_returns=2 field must not be interpreted as replenishing the exhausted old initial return allowance. State separately the actual inherited usage, the single present technical transformation, and each new branch's prospective one scientific opportunity and schema-only return limit. No repeated repair/rehash/review cycle may silently create an unlimited initial correction budget. Failure of the narrow repair or any required admission gate produces a retained, explicit failure disposition unless a separately authorized new release changes the scope.

Retained branch laws still receive separate immutable candidates, run IDs and slot dispositions. They are paired repeats, not independent constructions. Failed, stopped, ineligible and interrupted phases consume/close their scheduled slots under the existing no-retry rules; no alternate seeds, local generator execution or replacement versions are permitted.

### 4. Keep the alias correction scientifically neutral and actually validate it

The demonstrated failure is the mismatch between the mapping input hba1c and the unit-evidence representation HbA1c_percent, plus its missing native alias. The intended repair is to connect the existing generated column to that already declared representation and use the correct native input name. It must preserve the conversion constants, source evidence identity, source population, response/predictor roles, adjustment sets, selection, weighting assumptions and numerical functional. The alias may cite an existing relevant measurement assumption; it may not silently invent specimen/assay equivalence or require a new scientific assumption hidden inside metadata.

Keep original qualified bindings as {}. The new metadata checker should report all J/B/M contexts together, be read-only, and neither run the generator nor manufacture approval. Its success is insufficient for admission. After preparing and sealing the actual context children, obtain genuine independent candidate-specific reviews and run qualified_relationships_v1._prepare on each actual sealed J/B/M child with those exact bound declarations/reviews. Preserve all results. Check the final parent/child freeze identities, native aliases, mapping inputs and evidence names, strict-unavailable semantics, operator contracts, support/moment gates and zero-attempt status. Never substitute a synthetic passing declaration or reuse A02's revoked review.

If any scientific file must change to make this pass, stop calling the action metadata-only and record a new scientific decision under a prospectively allowed scope. A successful interface repair is not measured scientific improvement.

### 5. Bind the complete current packet without rewriting historical exposure

Task, evidence and registry bytes must equal the old approved packet. The current author packet should include the complete qualified interface, read-only preflight, current protocol and applicable scientific/support requirements. If historical instructions are copied too, identify them explicitly as historical and make the current continuation instructions authoritative; an old instruction to start two fresh authors must not conflict with the zero-new-initial-author design.

The controller copies all initial-packet files into both branch packets. Audit this allowlist before freezing it: no prior target results, reference contents, generated rows, numerical source feedback or source-result summaries may enter the common/self-review packet through an apparently harmless review or provenance document. Put historical administrative lineage in release metadata when it is unnecessary for authoring. Both branches receive the same accepted initial scientific artifacts; only source_feedback receives authenticated initial numerical feedback. Final branch feedback stays hidden until both decisions are irrevocable.

### 6. Retain the existing release and reveal barriers

Use the unchanged released controller, evaluator, analytical plan, runtime and environment checks. Bind the new preparation/preflight/lineage/protocol artifacts in the new release; freeze their bytes before final review. The controller's schema names and evaluator's developmental labels do not make this a new independent confirmation.

Require all constructor/version source dispositions and branch choices to close before the immutable scientific inventory and first target generation. Close all target slots before authorizing the frozen evaluator. Reference bindings remain metadata only until that authorization. A changed runtime, engine, candidate, support review, target output or reference commitment is an integrity stop, not a reason to silently update the release. Keep the same three F2 analyses, existing reference uncertainty policy, all unavailable/failure statuses, and developmental/assumption-dependent interpretation. No outcome widens the dataset, evidence, endpoint or draw budget.

## Minimal evidence needed for the later hash-bound release review

The final review should inspect the new protocol and release digest; unchanged engine/evaluator and old packet bindings; complete lineage and per-file delta records; corroborated historical counters and explicit zero-fresh-author trace; sealed new parents/children; new genuine scientific/support/qualified reviews; actual J/B/M _prepare pass records; zero-attempt state; and the complete common packet allowlist. It should verify that no approval, source opening or dispatch relies on this design review alone. No additional scientific draw or broad test-suite rerun is requested here.

Written only to the new continuation review directory. Final release approval is intentionally withheld pending the concrete, hash-bound draft.
