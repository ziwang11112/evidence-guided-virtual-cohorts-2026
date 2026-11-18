# Agent-led scientific checking and revision: complete results

11 November 2026. All 24 review sessions and 72 final tables are complete. Independent source/code review preceded clinical comparison; independent saved-row recomputation passed.

**The checks supported genuine model repair, but did not establish a general improvement in the final data's scientific analyses.** Both ordinary and structured review repaired the same two starting laws. A blood-lipid revision removed a divergent ideal tail; a blood-pressure revision addressed a possible failure after rounding. Most scientific estimates stayed exactly unchanged. The changed lipid analyses show modest movement toward the sample reference on one slope, essentially unchanged residual dependence, and slightly worse dispersion agreement. This supports retaining scientific checks as quality assurance, while keeping analyzable virtual data and inspectable modeling decisions as the central contribution.

## 1. What ran

| Item | Executed scope |
|---|---|
| Starting generators | All 12 frozen laws from the preceding request-only study; six blood-pressure and six lipid laws |
| Review design | Each law reviewed once by a fresh ordinary Agent and once by a fresh structured-review Agent |
| Model | gpt-6.1-sol, high reasoning, default tier, identical tool and budget opportunities |
| Scientific inputs | Same original request, imported code/specification/notes, captured-source catalog and full-text read access within each pair; articles were not all preloaded and supplementary retrieval was allowed |
| Target information | No clinical reference estimates, old evaluation results or host-selected numerical repairs supplied to the new review contexts |
| Agent decisions | 20 explicit retentions of v000; four selections of revised v001, both arms for R04 and R07 |
| Final generation | 72/72 successful tables; three fixed seeds and 3,000 synthetic rows per branch, 216,000 final fictional rows |
| Comparison data | 36 already-saved initial synthetic tables; previously exposed clinical sample references, not new patient validation |
| Resources | 343 API calls; USD4.8731316 known/accounted token-tariff estimate; zero unknown-usage receipts |

Seeds and synthetic rows are not independent clinical replications. There are twelve starting laws in two contexts and one reviewer per branch/law. This is a paired developmental revision experiment, separate from the earlier end-to-end construction comparison. Providing the initial sources here deliberately isolates review of an existing artifact; it does not redefine the request-only baseline.

## 2. What was integrated

The versioned API entry point exposes the following tools to **both** review policies. Ordinary review may use every capability; structured review additionally asks for explicit coverage and requires an inspection receipt for the selected law. Honest unresolved and no-change decisions satisfy the gate when documented. The host did not insert case-specific slopes, covariances, dispersion values or repair instructions.

| Layer | Agent responsibility | Deterministic implementation | What it cannot certify |
|---|---|---|---|
| Mathematical law | State support, transformations, moment claims and justification; choose any repair | A bounded AST screen points to potentially problematic transformations; isolated execution checks delivered values | A static warning is not a theorem, and no warning or finite sample does not prove integrability |
| Physiological consistency | Select and justify applicable rules, measurement interpretation and tolerances | Declarative linear equalities/inequalities are evaluated on generated rows with counts and denominators | A declared rule is not automatically a universal biological fact; separate assays and ideal component concentrations differ |
| Joint scientific analyses | Specify relevant operators, adjustment sets, parameter origins, uncertainty and unidentified dependencies | Validate the declared schema/source registrations and analysis coverage; return generated-only regression/dependence diagnostics | Coverage and plausible output do not establish correct extraction, an identified covariance or transportability |

`api_loop.py` dispatches the calls; `tools_runtime.py` binds inspections to the exact candidate and isolated trial; `law_checks.py` implements generic checks. Candidate changes are new immutable versions. The Agent decides whether to read more evidence, inspect, revise, retain or stop. No target-fitting optimizer or host-authored scientific correction is hidden in these checks.

All 24 Agents invoked the inspection tool. Ordinary review's 18 inspection calls yielded 13 completed review receipts, two static-only responses and three invalid-contract responses; structured review's 25 calls yielded 12 completed receipts, one static-only response and twelve invalid-contract responses. Invalid contracts were recorded and recovered, not counted as completed scientific reviews. Ordinary/structured literature-search calls numbered 22/36: 16/25 passed the local protection gate, including two/four gateway errors; six/eleven were rejected locally. New successful full-source downloads numbered one/two. These are operational counts, not scores of evidence quality. Both policies submitted two new candidates. The contrast concerns organization plus a completion gate under shared tools; it does not isolate the causal effect of making the checker available. Estimated API costs were USD2.0268326 for ordinary and USD2.8462990 for structured review; these are observed costs under common ceilings, not a general efficiency estimate.

## 3. What the Agents actually repaired

### R04: finite moments, with different physiological choices

The initial law, previously LIPID_BASE_R2, placed a positive exponential link on shifted-lognormal BMI. Under the ideal real-valued sampling law, total cholesterol contained `exp(c * BMI)` with positive c. The corresponding positive moments diverge despite ordinary finite samples looking plausible.

- **Ordinary review** replaced the TC BMI contribution with a positive affine term. Given the fixed support and coefficients, this yields finite positive polynomial measurement moments. It retained the separate TC/HDL measurement model.
- **Structured review** used a log-BMI predictor, giving polynomial rather than exponential growth in BMI. It additionally generated positive HDL and non-HDL components and set TC to their sum. Fixed-specification positivity and reference covariance algebra were independently checked. The component covariance was derived from an already assumed reference covariance, not newly identified target dependence.

Both remove the particular divergent-tail defect. Structured review enforces TC > HDL by construction under an **ideal concentration-component interpretation**. That is an additional measurement/modeling assumption, not proof that every noisy observed assay pair must obey strict ordering. Its reference covariance conversion does not guarantee the requested cross-sectional OLS residual correlation.

The independent audit retained one small provenance wording error: the structured HDL contract says Tanzania/Uganda, while the cited HDL contrast is Tanzanian and the newly fetched Ugandan paper measured TC only. The numerical HDL source is Tanzanian; the record does not establish use of a Ugandan HDL coefficient. Frozen artifacts were not silently edited.

### R07: acceptance after rounding

The initial blood-pressure generator accepted continuous SBP/DBP pairs and then rounded them. A pair satisfying the continuous condition could become invalid at half-mmHg resolution and trigger an exception.

Both Agents moved rounding before pair acceptance. Ordinary review kept its 100-attempt failure cap; structured review removed that cap and used rejection until acceptance. The latter has almost-sure termination under the fixed law, but no deterministic execution-time bound. The external isolated worker still imposes its execution limit.

**All six final R07 tables are byte-identical to their corresponding initial tables.** No rounding boundary event affected these prescribed draws. The change repairs a possible delivery edge case; it produced no observed scientific-analysis gain in this experiment.

### The other ten laws

Both branches explicitly retained their initial laws. Their sixty final tables are byte-identical to the saved initial tables. The audit distinguishes implemented numerical caps from genuinely unbounded ideal laws; for example, R02 is finite under its actual caps and must not be mislabeled as the uncapped R04 defect. Finite moments do not resolve unsupported transport or dependence assumptions.

## 4. Did final scientific analysis improve?

The table below shows the one starting law whose saved numerical analyses changed. These are means across the three prescribed seeds, not confidence intervals. All twelve starting-law profiles and all requested analyses are retained in the accompanying figures and tables; the other eleven laws' analysis estimates did not change in either arm.

| R04 analysis | Initial | Ordinary review | Structured review | Existing sample reference |
|---|---:|---:|---:|---:|
| BMI-TC slope, mg/dL per 5 kg/m2 | 14.615 | 14.106 | 13.364 | 5.683 |
| BMI-HDL slope, mg/dL per 5 kg/m2 | -1.490 | -1.490 | -1.511 | -4.623 |
| TC-HDL residual correlation | 0.35900 | 0.35938 | 0.35838 | 0.51207 |
| TC sample SD, mg/dL | 36.687 | 36.503 | 36.418 | 42.847 |
| HDL sample SD, mg/dL | 13.133 | 13.133 | 13.125 | 20.176 |

Both repairs modestly reduce the BMI-TC distance to this sample reference. The HDL effect remains much weaker in magnitude; residual dependence is essentially unchanged. TC dispersion moves slightly farther from the sample reference in both branches, and HDL dispersion also moves slightly farther in the structured branch. The very small correlation changes are not evidence of a resolved dependency problem. No post hoc equivalence threshold, significance test or pooled cross-unit quality score is introduced.

Across all 72 final tables, **66 are byte-identical to their corresponding initial tables**: sixty explicit retentions and the six R07 outputs. Only the six R04 tables differ. Thus four changed code files must not be reported as four empirical quality improvements.

Common physiological diagnostics also remain visible. No final BP table has SBP below DBP. The retained R08 lipid law still has one HDL > TC row in seed 54003 in each review branch, the same original record reproduced twice. That is one row per 54,000 lipid rows in each arm; the copies are not independent new failures. No row was removed. A component-model change in R04 did not eliminate this separate retained-law diagnostic.

The clinical estimates are uncertain samples, not known population truth. Figure shading uses only the pinned uncertainty already available; there is no invented correlation confidence band. The PNS reference uncertainty is not a new complex-survey inference. Reused references make these developmental comparisons. Equal random seeds after changed programs need not represent matched random events; encoded cohort-level parameter variation also remains distinct from ordinary row-sampling variation.

## 5. Evidence, implementation and interpretation

The preclinical audit examined all twelve initial laws, all four selected revisions and all 24 selected review declarations, including thirteen primary source-passage checks. It found **no newly established residual-dependence constraint for the revised laws**. R04's covariance conversion and R07's source moment decomposition still depend on reference-population and joint-model assumptions. The checks made those assumptions inspectable; they did not supply the missing information.

This experiment supports the following narrower statements:

1. An Agent using general inspection tools can notice and repair a mathematical law defect and a delivery edge case without receiving desired clinical values.
2. Mathematical validity, physiological construction and analytical transfer are separate properties. A repair can be correct yet leave scientific analyses unchanged or mixed.
3. Ordinary review can perform the same principal repairs. This pilot does not show a general scientific-quality advantage for the explicit structured-review policy.
4. The inspectable records help locate source assumptions and a provenance-label defect. They are not a calibrated confidence label or a measured improvement in human review efficiency.

The study does not establish that checks solve joint-evidence scarcity, that additional review usually improves data, or that this model generalizes to unseen cohorts. No further case, provider, paid batch or target-guided revision follows automatically.

## 6. Verification and artifacts

- Independent preflight: 478 checks; owner offline suites: 34 law-check and 32 runtime tests. First-block operational audit: 2,293 checks. These are implementation checks, not independent scientific experiments.
- Source/code audit frozen before evaluation: [audit table](review/CODE_SOURCE_CHANGE_AUDIT.md), [bound findings](review/CODE_SOURCE_CHANGE_AUDIT.json).
- Independent numerical review: **13,419 checks, zero failures**; all 72 final and 36 saved initial tables; largest arithmetic discrepancy **9.33e-14**. No generator, patient reference fit or API call rerun: [review](review/INDEPENDENT_NUMERICAL_REVIEW.json).
- Reporting verification: **9,245 aggregate checks passed**, including 216 summary rows, 648 scalar seed estimates, 144 paired changes and 24 resource records. Both final PDFs were rendered through Poppler and visually inspected. Figure ranges are seed variation, not clinical confidence intervals: [reporting QA](reporting/qa/REPORTING_QA.md).
- No new literal target-family matches in returned-source screening. This is not a certificate of source independence; earlier source-preview exposure and current applicability limitations remain in lineage.
- [Complete evaluation](EVALUATION.json), [analysis table](ANALYSIS_RESULTS.csv), [construction closure](CONSTRUCTION_CLOSURE.json), [final table ledger](FINAL_TABLES.json).
- [All analysis profiles](reporting/paired_analysis_profiles.pdf), [paired reference-distance changes](reporting/paired_reference_distance_changes.pdf), [complete aggregate/resource tables](reporting/AGGREGATE_TABLES.md).

The reporting export initially stopped before drawing because its baseline allowlist omitted the already-bound aggregate `ANALYSIS_RESULTS.csv`. The reporting-only allowlist was corrected; frozen experimental inputs and estimates were not changed. The failure and visual checks are recorded with the reporting artifacts.

Patient-level records, synthetic row tables, captured full papers, raw API logs and credentials remain local. This unit has not been uploaded to GitHub. The frozen manuscript v0.29 is unchanged; [manuscript-ready text](MANUSCRIPT_INSERT.md) is supplied separately and is not yet in its PDF/Overleaf archive.

## 7. Decision for the paper and method

Retain the three checks as reusable quality-assurance tools available to a scientific Agent. Do not make the structured gate, extra review calls or revision frequency the main novelty. Use this bounded study to explain a concrete distinction: **a mathematically better generator can still lack the joint evidence needed for a better scientific analysis**.

The main story remains a research request leading to Agent-selected evidence, an executable joint model, analyzable virtual data and an inspectable record of sources and assumptions. Add this experiment as the quality-assurance and limitations section beside the earlier request-only comparison. Preserve the mixed comparisons and unmodified data alongside the repaired examples. Continue with manuscript integration and external biomedical interpretation review; no new mechanism or data collection is required by this result alone.
