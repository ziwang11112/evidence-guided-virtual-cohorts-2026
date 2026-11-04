# Independent review of the v0.9 consolidation

2026-11-04. **PASS for scientific-draft integration. No unresolved numerical, denominator, figure-binding or method-identity blocker was found in the reviewed final snapshot.** This is not a submission-readiness certification or a new biomedical validation.

Reviewed manuscript: [DRAFT_v0_9.md](../../manuscript/DRAFT_v0_9.md), SHA-256 `0de628da4d71bc8ef1fa28c8ec703bccf991bcc27839b37af66aca5a6b00a05e`. Exact reviewed input hashes, individual checks and limits are retained in [REVIEW_v09.json](REVIEW_v09.json). The reviewer did not edit the manuscript.

## Scope and evidence

The review read the consolidation decision, current and preceding manuscripts, frozen protocols/claim locks, original result reports, aggregate JSON, analytical sensitivity review, new figure source/bindings/captions, and the historical-results supplement. It did not read participant records, observed covariate tables or generated rows; run a generator, clinical fit, old test suite or old scientific entrypoint; or perform network retrieval.

The new figure PNG and the copied supplementary PNG were actually viewed. No truncation, overlap or missing effect/scenario was found at the supplied image size. Final journal-layout size and the eventual typeset manuscript were not inspected.

## Numerical and artifact checks

| Check | Result |
|---|---|
| Table 5: seven rows, reference estimate/limits and full three-seed range | **35/35 numeric values** exactly match the frozen construction `evaluation/REPORT.json` at displayed precision |
| Table 6: nine rows, real-real median and range of generated symmetric medians | **27/27 numeric values** exactly match the frozen real-real `REPORT.json` at displayed precision |
| Tables 1–4 | Data rows are byte-for-byte equal to v0.8; no new scientific value was introduced into these preserved tables |
| New sensitivity endpoints | +0.03422 and −0.01095 match the two retained analytical scenarios; delivered assumption remains 0.25 |
| Initial aggregate/manuscript checks | 23/23 passed |
| Figure 5 coefficients, interval limits and SE bindings | **112/112 exact numerical bindings** agree with the frozen report |
| Figure 5 extended integrity checks | **179/179 passed**, including units, seed/table identities, all seven terms, sensitivity bindings, six source input hashes, three output hashes, script hash and unchanged supplement copies |
| Final manuscript snapshot | **30/30 passed**, including unchanged six tables, accepted wording fixes, final Figure 5/S2 asset links and all appended reference entries |
| Local manuscript links | **43 occurrences checked, 0 missing targets** |

These are verification counts, not numbers of clinical studies, constructions or statistical tests. The new table count is 62 numerical values, not 62 separate table cells. The figure includes seven reference effects and 21 generated effects, not 28 independent clinical estimates.

The Table 6 discrepancy definition is correctly preserved as a median over 100 splits of `(abs(G−R1)+abs(G−R2))/2`, followed by a range across the three fixed generated tables. It is not a matched-R2-only discrepancy, the discrepancy of an averaged coefficient, or a confidence interval. The wording and supplement explicitly distinguish these nonexchangeable sampling constructions.

## Experimental denominators

| Unit | Checked interpretation |
|---|---|
| CHNS/ENSANUT main study | 20 Agent + 4 statistical constructions; 72 distinct final tables; 7 exploratory tables; 79 successful physical executions; 2,196 independently checked statistics |
| CHNS information/revision | 6 authors; **42 physical executions** = 6 trials + 36 initial/final deliveries; 24 unique byte tables; 18 distinct delivery tables. Final tables were physically produced but duplicate initial bytes; this differs from an alias-only final stage |
| HRS | 2 constructions; 9 physical generations; 3 invalid initial comparator tables remain retained; 6 valid comparison tables. Each has 11,509 subjects × 4 visits = 46,036 rows |
| Live A/B | 2 constructions and 2 requests; 2 trials + 6 deliveries = 8 physical executions; retention aliases six deliveries rather than adding six executions |
| Open search and latest construction | Acquisition is a distinct no-generation unit; latest construction is 1 model, 1 trial + 3 distinct deliveries = 4 physical executions; retained final aliases add no tables |
| Real-real context | 100 prescribed community-disjoint resplits of one exposed CHNS reference; 3,000 people per side; 3 frozen generated tables reused; all 36 metrics retained. This is no new cohort and no generator improvement |
| Historical evidence | M10 and Wave A keep their own modes/releases and remain outside main-study denominators. The project-wide 13-family inventory is not certified here as a common-version benchmark |

The statement that six actual reference families are discussed is an inventory distinction, with HRS treated as a source-model example. This review did not individually re-certify all 13 historical families or every historical data acquisition.

## Method identity and claims

The [consolidation decision](CONSOLIDATION_DECISION.md) and final Methods now agree: the studies share a scientific procedure but use separately frozen implementations, information packets, feedback opportunities and evaluators. The completed CHNS/ENSANUT main study does not need regeneration simply because later retrieval/analysis-aware review was demonstrated.

The current deliverable is aggregation, plotting and writing. A new unified experiment appears only as a conditional gap if a stronger claim about the latest open-search workflow across cases is chosen. It is not a prerequisite added to the present task.

The draft distinguishes curated main-study evidence, permitted target summaries in R, source-rich HRS reconstruction, bibliographically seeded live retrieval and the later open-search unit. Host dispatch and coordinator-managed execution remain explicit; arbitrary natural-language intake, standalone model launch, broad adaptability and measured effort savings are not claimed.

The later model's changed author, evidence packet, demographic description, law and seeds are disclosed. The text does not attribute its historical differences to a causal search benefit. Seven main-study authors reviewed exploratory output and retained; thirteen finalized without exploration; six L/R authors retained after their additional stage. Live and latest retention are correctly described as operational decisions without demonstrated revision gains. The coordinator-detected pre-freeze moment repair is not relabelled as autonomous source-feedback improvement.

## Adverse and uncertain results retained

- Main-study CHNS BMI deterioration, conditional-age reversal, ENSANUT magnitude discrepancies and statistical-reference advantages remain visible.
- L/R unchanged additional-stage results remain explicit; the historical reference-assisted revision trade-off remains linked.
- HRS parser failure, separate repair, unstable above-threshold interaction and inadequate high-HbA1c spread remain reported.
- Live B's conditioned BMI mismatch and unavailable source checks remain visible.
- Latest primary BMI/glucose attenuation, female direction mismatch, composition/tail discrepancies and all seven nonintercept effects remain shown.
- Table 6 retains primary glucose/female and Pearson dependence discrepancies beside favorable contexts; the full 36-metric report is linked.
- Wave A's negative frozen gate and non-discriminating HAALSI zero anchors, earlier qualitative uptake and infinite-moment defects remain in the unchanged historical supplement. They are not pooled into the new main-study score or deleted from the evidence record.

No equivalence threshold, pooled quality score, restored untouched-reference claim, source-replay mandate or successful-seed selection was introduced.

## Resolved review findings and remaining limits

Four wording issues were identified and resolved before the final snapshot: main-study `retain` versus `initial_final` decisions; shared procedure versus separate releases; L/R physical duplicate outputs versus live/latest aliases; and calling the 36 quantities metrics rather than only diagnostics. The final Figure 5 and S2 captions replace the initial assembly placeholders and use the correct uncertainty labels.

The three appended bibliography entries are now integrated. Their original JATS metadata was checked by the manuscript author; this reviewer confirmed their integration but did not repeat those extraction checks. The first eleven reference entries remain preserved. This review does not repeat all original source interpretation or old participant-level arithmetic.

Author/affiliation/funding/ethics/access declarations, venue selection and final publication layout remain open and are stated in the draft. Those limits do not require new scientific generation for this manuscript-consolidation deliverable.

A final-snapshot bookkeeping command initially failed before writing because its path lookup assumed `/` while metadata used Windows separators. The lookup was normalized and the aggregate-only checks completed successfully. No source result, figure, manuscript or scientific calculation was changed by that reviewer-tool correction.

## Addendum: public aggregate rendering entry point

The figure author subsequently repaired the public reproduction route. The final script hash is `d167a6dc156a054895cfe9552b4460afcc4ed7fba9a878b0d603ea3f0e0c8094`; the manuscript and all three main figure output hashes are unchanged. The reviewer independently examined the routing and supplement-copy code, refreshed the source/binding hashes, and checked the author-run clean public-project verification receipt.

All **27 additional checks passed**: six local and five public input hashes, current and matching public/local output identities, current script identities, exact public/local coefficient and analytical-scenario bindings, explicit public SVG-only supplement handling, and unchanged manuscript hash. The real-real aggregate JSON was independently checked both for parsed equality and equality after removing only whitespace outside strings. Its separate public byte hash is justified; the code does not accept arbitrary variants or fall back after a local hash failure.

The public package supplies the resplit SVG but no source PNG. The final script explicitly records that a public run does not create or validate a supplementary PNG. Figure 5 SVG/PNG/PDF remain identical between the author-tested public and local routes. The reviewer did not repeat that rendering execution or any statistical analysis; this addendum reviews its code, exact source/output identities and retained execution evidence.

[ROOT_README.md](../../../../README.md) and [PUBLIC_SCOPE.md](PUBLIC_SCOPE.md) were also checked. They retain developmental/reconstruction labels, separate frozen versions, adverse findings, host dispatch and the absence of submission. They do not turn the 100 resplits or six reference-family inventory into independent validations. The coordinator applied the review's wording refinement: the main contrast is now explicitly “constructor-averaged mean absolute discrepancies.”
