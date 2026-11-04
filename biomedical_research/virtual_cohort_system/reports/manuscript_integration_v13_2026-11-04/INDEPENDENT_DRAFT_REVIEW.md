# Independent v0.13 numerical, source and claim review

4 November 2026. Reviewer: `/root/v13_draft_audit`. **PASS; no unresolved blocker in this audit's scope.** Bound draft SHA-256: `0544e1d3b9ca19ae7f622ad6faff22f652a93a4291e8f8686f5617135b914eb4`.

I independently compared `manuscript/DRAFT_v0_13.md` with v0.12, the frozen corrected new-batch aggregate results, its independent numerical audit, protocol, all four source/proposal reviews and E02 addendum, original trial-feedback aggregates, the integration audit, and the bibliographic metadata. I inspected admitted original XML metadata directly. I did not read participant or generated-table rows, execute a generator, fit a clinical model, or retrieve new literature. The ARISE evidence-to-manuscript skill's source/claim and preservation checks informed the review.

The accompanying [JSON review](INDEPENDENT_DRAFT_REVIEW.json) records **34 passing checks**, exact input/output SHA bindings, the twelve Table S1 comparisons, source identities and resolved findings. [The aggregate-only check script](independent_draft_checks.py) can repeat these checks without model execution.

## Counts and numerical consistency

| Item | Independently checked result |
|---|---|
| Scientific authors and requests | Four authors, two per existing CHNS/ENSANUT request |
| Final outputs | Twelve distinct final table hashes; three final seeds per author; 3,000 rows each, totaling 36,000 virtual rows |
| Physical executions | Sixteen, comprising four trials and twelve final executions |
| Source acquisition | Twenty-four query credits, sixteen author-specific paper uses, twelve distinct originals; query credits include the charged metadata operations and are not represented as twenty-four distinct searches |
| Final estimates | Thirty-six primary coefficient estimates and 330 diagnostic values, totaling 366 |
| Independent numerical audit | 366 computed comparisons, zero mismatches, zero unavailable endpoints in corrected evaluation; the original scalar-interface failure remains preserved |
| Decisions and feedback | All four retained one initial law; zero revisions. Trial feedback contains 7/9/6/7 approximate comparisons and 13/4/14/8 unavailable checks, totaling 29 and 39, respectively |
| Table S1 | All twelve author/endpoint rows and all 48 displayed numeric entries match the frozen values at six decimal places |
| Q4 text | All twelve five-decimal coefficient means and six three-decimal diagnostic means agree with frozen aggregates |
| Complete diagnostic supplement | All 110 author/diagnostic summary rows reproduce, including their references, means and seed ranges |

All 36 primary seed coefficients have the same positive directions as their corresponding existing references. All six ENSANUT outputs have a lower BMI coefficient after glucose adjustment. The manuscript explicitly treats these as repeated measurements of six analysis definitions across four laws, **not 36 independent confirmations**, and describes attenuation as associational rather than mediation. Table S1 ranges and Figure 5 segments are correctly described as seed ranges, not confidence intervals.

## Scientific claims and information boundaries

The abstract, contributions, Q4 and Discussion consistently support repeated evidence-to-cohort construction and analysis-specific usefulness. The manuscript makes no new-estimator claim, universal Agent-superiority claim, causal retrieval-benefit claim, or demonstrated feedback/revision-gain claim. Both clinical reference families remain explicitly historically exposed developmental samples. Fresh author contexts and references withheld during construction are not portrayed as previously unexposed external validation.

The intended analyses were visible to authors, while target coefficients, desired signs, individual records and previous constructions were excluded from the author task. This distinction agrees with the protocol and task instructions. The manuscript also correctly describes the bounded gateway, host dispatch, coordinator review, overlapping sources and lack of arbitrary-request autonomy. This review checks the recorded boundary and its reporting; it does not independently certify host-level author isolation.

The source/model summaries agree with the reviewed proposals: C01's age-conditioned multivariate-lognormal mixture; C02's copula predictors and affine HbA1c conditional mean; E01's bounded beta predictors and conditional gamma response; and E02's lognormal BMI, conditional truncated-normal glucose and positive conditional-mean lognormal response. Source transport, missing dependence and residual assumptions remain identified as assumptions. Approximate source comparisons are not called source-population replays or passed constraints.

The text does not add a new clinical cohort. The completed batch reused frozen aggregate references, and manuscript integration/this review consumed existing aggregates only. The sixteen already-completed construction executions are reported separately from the zero executions performed during this writing review.

## Preservation of unfavorable findings

| Earlier or new adverse finding | Preservation evidence |
|---|---|
| Q1 CHNS BMI worsening; negative conditional-age outcomes; ENSANUT magnitude mismatch; two comparisons favoring statistical constructions | Table 2 and Section 4.2 are identical to v0.12, apart from figure-directory paths |
| Q2 retention and zero revision gain; supplied-summary reconstruction boundary | Table 3 and Section 4.3 are identical to v0.12, apart from figure-directory paths |
| HRS upper-branch instability, inadequate upper-group spread, and three invalid comparator attempts | Section 4.4 and Figure 4 caption are identical to v0.12, apart from figure-directory paths |
| Earlier open-search primary BMI/glucose attenuation, female-direction discrepancy and distributional defects | Section 4.6 retains the adverse interpretation; all seven effects and uncertainty labels survive in the byte-identical prior Figure 5, now Figure S1; its caption is identical after renumbering, and the complete open-search report remains linked |
| Real-real context showing larger primary glucose/female and joint/tail discrepancies | Section 4.6 preserves this interpretation and links the complete 36-metric report; v0.9 retains the earlier full numerical narrative |
| Earlier pre-freeze divergent-moment repair | Explicitly restored in Discussion, distinguished from demonstrated feedback-driven gain |
| Enrichment/direct-row failures, transport failures, infinite-moment history and revision trade-offs | Existing historical supplement and complete v0.9 record remain linked and unchanged by this integration |
| New age displacement, rank mismatch, compressed residual/total variability, and other diagnostic defects | Q4 and Discussion report the principal limitations; all 110 diagnostic summary rows remain linked and match the aggregates |
| New evaluator v1 scalar-type failure | Q4 explicitly retains the additive correction, failed output and audit provenance; no model adjustment after target comparison is claimed |

The condensation shortens some earlier examples in the main narrative, but does not delete an endpoint, adverse comparison or frozen supporting record. In particular, success is not redefined around only the favorable coefficients.

## Citations, source identity and figure organization

All 24 numbered bibliography entries are present, every numeric callout resolves internally, and all 24 entries now have at least one body/supplement callout. Original entries 1–15 are unchanged. All local manuscript links resolve.

For each of the twelve distinct new-batch originals, I parsed the admitted XML and checked title, first-author surname, journal, publication year and DOI against `SOURCE_BIBLIOGRAPHIC_METADATA.json`. All matched. I checked all sixteen author-specific admitted XML copies against their recorded SHA-256 values and checked Table S2's source/author/reference mapping. All matched. Ghazanfari's empty DOI in the metadata is retained as missing rather than invented. This is source identity and bibliographic consistency, not a second full clinical-extraction audit or a live test of external URL availability.

The main manuscript contains five numbered figures. New Figure 5 covers all six primary analyses, all four authors and all 36 final seed values from the current batch. Its numeric binding file matches the frozen results and its output hashes. Old Figure 5 is now Figure S1; its SVG, PDF and PNG bytes are identical to the prior assets, and its full seven-effect/sensitivity caption is preserved. Final PDF readability is assigned to the separate production review and is not claimed here.

## Findings resolved during review

The initial v0.13 draft lacked numeric callouts for existing references 8, 12 and 13. The final draft adds accurate principal-packet and preceding five-source acquisition citations. The initial draft also removed the earlier live author's pre-freeze divergent-moment repair qualifier from Discussion; the final text restores it explicitly. Both issues are resolved in the bound draft; no draft file was edited by this reviewer.

Principal frozen evidence bindings: corrected results `61994088354f290a3e7f6f6b85aac71498e6892093c71167cc021ea2722658ca`; independent numerical results `3c6262e1e5dff180d950aa2e884a98b195308159fcff848e46331796bd95042a`. The JSON retains the complete binding manifest. This review establishes consistency of the current manuscript and retained evidence, not biological validity or submission readiness.
