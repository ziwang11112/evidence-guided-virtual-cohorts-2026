# CHNS R30 input-comparability audit

3 November 2026. **Input audit only; not approval to fit or execute.** No participant or generated rows, historical generators or historical model specifications were read. No scientific generator, fitter or evaluator was imported or executed. This work writes only this file and `INPUT_COMPARABILITY_AUDIT.json`.

## Conclusion

The retained R01, R02 and R03 empirical input packets are byte-identical across authors; all **39** files listed for them in the historical input manifest still match their declared SHA-256 values. `AUTHOR_TASK.md`, `profile.json` and `b/task.json` differ only in constructor/root identity. The new conventional comparator can receive the same available empirical information without new patient analysis or source retrieval.

No author-added literature is recorded: all registries retain exactly six curator-approved source IDs, source directories contain the original four files, all nine candidate `evidence.json` files are semantically identical to the supplied compiled evidence, no retrieval events occur in the session logs, and each author's decision records explicitly report zero new queries/documents. This conclusion relies on the retained records and declarations. Author general tools were procedurally scoped, not host-isolated; it is not a complete external attestation of every tool call.

**Two input details matter:** (1) the historical external audit supplies Pani age evidence and additional Jansen rows, so the later main-study CHNS E1 packet is not a substitute; (2) the R30 reference JSON includes intervals and quality/design metadata beyond thirty point statistics. Supply the complete historical allowed files rather than silently reducing the input to thirty numbers.

## Exact shared input bindings

Paths below are relative to each `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcIA/R0{1,2,3}/` root. All listed bytes match across the three roots.

| File | SHA-256 |
|---|---|
| `b/input/reference_summary.json` | `7cda7cb9a3a1b337b92bc6f6664366fede1cd50dd1da9d255d20c346d5d25b02` |
| `b/input/analysis_definitions.json` | `785ba2b5da2ce992840df8c6fc7b7ce62acc80bc3c09b2b5cd7094e11b38703c` |
| `b/input/compiled_evidence.json` | `ea2e821a7022459e0da5c1e4f9d27bd2f4cbf6784a51d30401f19d2a1ce86067` |
| `b/sources/evidence_packet.json` | `254a9bca0c612e4e03a22c9e4457b4b34eb4d5cd4672df8c2a4cd15131f7ab84` |
| `b/sources/EXTERNAL_EVIDENCE_AUDIT.md` | `95a567ff5fa8901888f17f960893d37d942a950181429388ba8ee73baa857caa` |
| `b/sources/NGSP_UNITS.md` | `724a8b7965ab7bcb1d27a089204473b505d9e83b3042dea05c52cca3d8cf89d4` |
| `b/registry.json` | `5dfac2dbe227a9ba07f6e9de0fce926c57b554c89d6a67acd704edb8ad12616f` |
| `b/input/semantic_bindings_template.json` | `3f561b4ea4029aae5bda1500ddfe478a7d722ef3ddb73016f7d48fe8b8001bae` |
| `b/input/whole_cohort_feedback_template.json` | `f357c94742f914e61895b17a8d7d67b9ebc9fb4810afd50fee2844f4a36642a4` |

The duplicate `b/sources/CHNS_DEVELOPMENT_REFERENCE.json` has the same hash as `b/input/reference_summary.json`. The complete 39 expected/observed hash comparisons, each constructor's identity-specific file hashes, session contracts and feedback hashes are in the companion JSON. The candidate `evidence.json` SHA-256 is `ef135314edaa2e3433c5b573982b41a8e9bb3453a019501e4003ec958873b912` for all nine candidate copies; different serialization from the input compiled-evidence hash does not change JSON content.

## Allowed scientific information

The registered source IDs are `S_JANSEN_2013`, `S_BAO_2010`, `S_MIND_2024`, `S_NGSP_UNITS`, `S_AUDIT`, and `CHNS_DEV_REF`. The compiled evidence contains 67 items: 37 external/context items and 30 reference items. This count is not an information-sufficiency claim.

`EXTERNAL_EVIDENCE_AUDIT.md` was expressly allowed to every author. It contains Bao sex-specific summaries, additional Jansen age/model rows and Pani's adjusted age slope plus eight age-band means/SEs, with source/operator qualifications. Pani enters through `S_AUDIT`; absence of a separate Pani source ID from the six-entry registry does not mean its text was unavailable. The audit's references to older project paths are provenance locators, not blanket authorization to inspect those old project files. No newly retrieved source supplement needs to be supplied to the new builder.

The exact reference summary contains the 6,631-person selected CHNS sample's three coefficients and 27 diagnostics, plus their available coefficient uncertainty, cluster/df metadata, ranks/condition numbers, eligibility/linkage/missingness and quality counts. These remain disclosed developmental inputs, not patient records or independent validation data. The new comparator should inherit the whole supplied JSON; using extra empirical quantities outside it would require an explicit information amendment.

## Analysis and task contract

All five scientific variables are generated; input observations are absent. Required output is 3,000 rows with unique synthetic `row_id`, age as integers 35–74, binary `female`, positive BMI, glucose in mmol/L and HbA1c in percent. Task numeric bounds allow glucose/HbA1c zero, but scientific feedback treats nonpositive glycemia as invalid; valid analysis must not silently drop those rows.

The three analyses are intercept-including unweighted OLS: (E1) BMI coefficient in HbA1c ~ age + female + BMI; (E2) glucose coefficient in HbA1c ~ age + female + glucose; (E3) age coefficient in HbA1c ~ female + BMI + glucose + age. Diagnostics are five statistics for each of age/female/BMI/glucose/HbA1c (mean, sample SD with ddof=1, linear q10/q50/q90), plus glucose–HbA1c Pearson and average-tie Spearman. This is selected-sample analysis, not national survey weighting.

Source-population numerical replay was not supplied. Target diagnostics were not source replay. Author contracts permitted deterministic analytic calculations/integration/optimization if producers and limits were retained; row-producing simulations required the isolated controller and consumed table slots. The exact historical numerical optimization budgets are not standardized across authors and should not be reconstructed as equal search effort.

## Historical feedback and actual budget

| Item | Per-author permission | R01 | R02 | R03 |
|---|---|---:|---:|---:|
| New literature | At most 2 queries / 1 original document | 0 / 0 recorded | 0 / 0 recorded | 0 / 0 recorded |
| Initial trials | At most 2; seeds 4201/4202 | 1, seed 4201 | 1, seed 4201 | 1, seed 4201 |
| Initial delivery | 3 seeds, 4101–4103 | 3 | 3 | 3 |
| Revision trials | At most 2; seeds 4301/4302 | 0 | 0 | 0 |
| Final delivery | 3 seeds, 4101–4103 | 3 | 3 | 3 |
| Scientific revision cycle | At most 1 after initial feedback | retain | retain | retain |
| Total physical attempts | At most 10 | 7 | 7 | 7 |

The historical `b/task.json` generic lifecycle field says `budget.revisions=4`; it is not four scientific revision cycles. The profile, author instructions and session contract explicitly constrain this experiment to one post-initial cycle, two phases and ten total table attempts. Preserve that distinction when reusing metadata.

All 21 recorded executions succeeded. Each author received a trial-feedback file, three-seed initial aggregate feedback and final aggregate feedback. All feedback-event file hashes match their referenced event hashes. Across all 21 feedback run records, the exact three analysis IDs and 27 diagnostic IDs, their reference values, coefficient intervals and reference-summary hash match the supplied input. Each semantic report has 30 computable target-summary checks and one unavailable external-source replay check. No new empirical target statistic was identified in feedback; feedback also contains generated-table quality and implementation status.

All nine matched initial/final seed pairs have identical recorded generated-table hashes. Thus these three authors contributed nine distinct delivered tables plus three distinct trial tables, twelve distinct table hashes in total. Final repeats do not increase independent model or table replication. These checks use metadata and stored feedback only, not table rows.

## Consequences for the new comparison

- Supply the complete shared empirical input set above, including the external audit and full reference JSON. Differences in numerical uptake are allowed but must be recorded.
- Keep historical candidate decisions, fit reports, model hints, generators and generated feedback values on the auditor/evaluator side. They are not the common empirical packet and should not guide the new statistical builder.
- Describe the comparison as a new prescribed statistical construction against retained historical Agent outputs under matched available empirical inputs. Three statistical final seeds can be compared descriptively with each author's three distinct delivery seeds.
- Report historical feedback/search opportunities and the new comparator's actual budget. Matching data access does not erase the historical three-author versus one-prescribed-law asymmetry, temporal knowledge, optimizer effort or feedback differences. One new three-draw comparator is not an equal-budget prospective contest.
- Supplied-summary consistency is a legitimate outcome. General method-family superiority, independent population validation, causal recovery, complete joint identification and measured automation/time savings do not follow from this comparison.
- This audit establishes input comparability only. The new protocol, specification, numerical feasibility and execution release still need their own review; no clinical fitting or generation was performed here.

## Provenance and limits

Primary local records: `work/information_revision_ablation_2026-11-03/INPUT_MANIFEST.json`, `PROTOCOL.md`, `AUTHOR_DISPATCH_PROVENANCE.json`; each R root's allowed input/source files, session contract/events/feedback, candidate evidence/decision/check declarations and final author decision. SHA-256 bindings and structured audit findings are in `INPUT_COMPARABILITY_AUDIT.json`. Exact provider model snapshot/token usage are absent from dispatch provenance. This audit neither rereads original publications nor independently authenticates their extraction.
