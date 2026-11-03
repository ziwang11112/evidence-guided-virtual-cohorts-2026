# Independent design and evidence-packet review

2 November 2026. Reviewer: `/root/highlight_existing_mechanism`. Amendment producer: `/root`; packet producer: `/root/highlight_evidence_admission`.

**The reuse amendment is methodologically suitable for the stated descriptive CHNS benchmark comparison. The actual E0/E1 packets pass their independent content and derivation review. No material blocking error was found.** This is a design and evidence-input review only. No target/harness contract, generator, execution, collector, scientific result or release is approved. `evidence/PACKET_REVIEW.json` binds the exact files inspected.

## Benchmark interpretation and analysis

Previously exposed CHNS data can support this new, fixed information intervention without becoming unseen validation. The amendment explicitly records researcher exposure, preserves the old experiments, withholds target empirical values from the new constructors, and limits the claim to reduced discrepancy on the reused benchmark. These are the appropriate distinctions. Another data acquisition is not required for this question.

The three proposed mathematical projections agree with the old CHNS plan and the existing evaluator: HbA1c on age/female/BMI with focal BMI; HbA1c on age/female/glucose with focal glucose; and HbA1c on female/BMI/glucose/age with focal age. Intercepts, native target units, the original common-complete-case population and reference uncertainty remain unchanged. Jansen's separate age/gender-adjusted source projections are not concatenated, and source plasma versus target serum remains an explicit applicability assumption. The third use is additional joint reuse rather than another independent cohort or a recovered biological discovery.

Five constructors per arm and three draws per constructor give 30 reserved target attempts and ten independent construction contexts, not 30 independent clinical or Agent replications. The existing 3,000-row task size is adequate as a fixed computational choice; it does not create more measurement evidence. A one-pass profile legitimately tests the supplied-information contrast without a source-feedback revision or a conventional reference arm. Its results must not be presented as evidence that a feedback or source-replay component improves performance.

The stated endpoint summary is coherent: for constructor i and endpoint k, calculate `L_ik = mean_s(abs(generated_isk - reference_k))`; then report each constructor, both arm means and `mean_E1(L_ik) - mean_E0(L_ik)`. This is not `abs(mean_s(generated_isk) - reference_k)`. Improvement on both designated projections requires both complete-arm contrasts to be negative. The amendment appropriately denies the complete-arm positive claim when required results are missing, rather than allowing a successful subset to replace failed slots. No clinical adequacy, equivalence, formal superiority test or broad population-generalization claim follows from the sign of this descriptive contrast.

The existing reference-interval endpoints can supply the proposed descriptive sensitivity without new participant access. Endpoint sensitivity is not a proof of robustness at every point inside an interval: differences of absolute-discrepancy summaries can change within it. The amendment does not make that stronger claim. The intervals are not equivalence margins or a joint confidence region, as the amendment already states.

## Implementation reuse and pending release fields

The reviewed existing `chns_f2_evaluation.py` separates pure `analyze()` and `compare_estimates()` from reference decoding. They can analyze new generated tables against the exact old reference object. The pure helper validates the old analysis plan's metadata but does not open its participant files. Reuse the unchanged scientific formulas and plan; retain the full historical target report and independent recomputation by hash.

Do not reuse `summarize_slots()` or `evaluate_released()` for the new arm inventory. They retain the old C1/C2, initial/revised, seed and one-time-reveal assumptions. A small new 30-slot inventory/comparison wrapper is the necessary addition already identified in the amendment. Keep evidence-arm labels separate from the historical estimand IDs E1/E2/E3. No new phase-aware source/target bridge or approximate OLS collector is needed for this one-pass profile.

Before execution, the separate contract still must name the exact three seed values, common constructor prompt and task bytes, allowed runtime/limits, finite technical-repair rule, ten constructor identities and 30 slot identities. These are acknowledged pending release fields, not grounds to restart data acquisition or enlarge the experiment. Candidate scientific content remains Agent-authored; no target values or prior fitted models belong in review advice or constructor inputs.

## Actual packet verification

| Item | Independent finding |
|---|---|
| Common base | Canonical JSON content is exactly equal between E0 and E1; shared-base SHA-256 is `70904b1a3a92fe05dd38c3e69ab4e8b277292aa010ccca802cc552acbc6b89c8`. |
| Common sources and margins | Both contain the three approved source metadata records and 15 grouped marginal records, exactly copied from the approved candidate specification with only `provenance_ids` removed. |
| Information count | E0 has 15 grouped marginal records and zero relationships. E1 has those same 15 plus exactly four relationships, for 19 grouped information records. The three metadata records are additional context, not empirical constraints counted again. |
| Relationship definitions | E1 preserves all four approved numerical values, units, conditioning, mathematical definitions, assumptions and strict-unavailability statuses. Only the qualified-comparison status changes from pending to the independently approved disposition. |
| Added interpretation | Common text preserves source/target distinctions, uncertainty and access boundaries without adding empirical facts. E1's binary-nuisance recoding record exactly matches the approved record. Its separate-Jansen-model explanation preserves the source meanings. |
| E0 leakage | No added relationship value, interval, direction claim, relationship ID or reconstructible relationship summary was found. Named studies/DOIs remain common attribution and cannot establish absence of prior model knowledge. |
| Wider-workspace leakage | Neither arm includes coordinator audit paths, hashes, broad source documents, article bodies, historical target names/results, target empirical values or fitted generators. |
| Derivation manifest | Both arm sizes/hashes, approval hash, candidate hash and common-base digest match the actual files. `packet_manifest.json` remains coordinator-only. |

Static inspection used strict JSON parsing, exact record comparison and hashing, not a software test suite or generator. One initial substring screen flagged `0.13` within the shared MIND DOI `10.1371`; semantic inspection and exact numeric-field inspection confirmed that this was an identifier false positive, not the Jansen coefficient. No packet was changed to hide that finding.

Reviewed packet hashes:

- `evidence/E0.json`: `ef5d6515a995e43c59d5ac4309e890d4bfc27dd1ec2e67e1796fc8829cb6cdd2`.
- `evidence/E1.json`: `254a9bca0c612e4e03a22c9e4457b4b34eb4d5cd4672df8c2a4cd15131f7ab84`.
- `evidence/packet_manifest.json`: `95a6318fc3dccec0884f935a64e8794ac69f69f431ea831f05b099d37edb4e18`.
- `REUSE_AMENDMENT.md`: `2797c1006479636199bce69caba29a75d00fe0a75a6f0f5a2e0c6e13f18acef0`.

Mount only the exact assigned arm file, together with a separately reviewed common task/prompt. Do not mount this review, the manifest, the other arm file or the evidence directory wholesale. These arm files are explicitly a sanitized evidence format, not current harness `evidence.json`; this approval does not assert that a harness compiler or candidate binding already exists. Any common unit guidance introduced at task compilation must be identical between arms and must preserve the distinction between scale conversion and assay/serum-plasma transport.

## Review scope

This review inspected the new amendment/packets/manifest, the bound source approval and candidate specification, and existing analysis-code/protocol metadata already reviewed in this task. It read no patient or generated rows, performed no web requests, downloaded nothing and executed no tests, generators or scientific analysis. Only this review and its machine packet-review record were created. Historical files, source approvals, amendment and packets remain unchanged.
