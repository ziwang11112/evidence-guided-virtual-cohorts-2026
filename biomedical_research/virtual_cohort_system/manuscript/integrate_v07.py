"""Integrate existing audited studies; no scientific execution or refitting."""
from pathlib import Path

M = Path(__file__).resolve().parent
old = (M / 'DRAFT_v0_6.md').read_text(encoding='utf-8-sig')
methods = old.split('## Methods\n', 1)[1].split('## Results\n', 1)[0]
results = old.split('## Results\n', 1)[1].split('## Discussion\n', 1)[0]
references = old.split('## References and source-access status\n', 1)[1]

intro = '''# Evidence-Guided Agent Generation of Virtual Biomedical Data for Scientific Analysis

Working manuscript v0.7, 3 November 2026 (America/Chicago). This revision integrates the completed longitudinal public example with the two earlier information settings. All studies retain their own protocols, information boundaries and complete outcomes. No new generation, patient-level analysis or parameter adjustment was performed for this writing revision. Author declarations, reproduction packaging and submission formatting remain incomplete.

## Abstract

Individual biomedical measurements may be inaccessible, incomplete or unavailable for a proposed study, although relevant distributions and associations have been published. We present an evidence-guided Agent procedure that converts study-qualified findings, a population description and a research request into an executable joint model and virtual data for ordinary scientific analysis. The Agent selects model structure, numerical constraints and assumptions; statistical software samples and evaluates the resulting records. We report three distinct information settings. In a two-case developmental study using CHNS and ENSANUT references, 20 Agent and four statistical constructions produced 72 final cross-sectional tables without individual-level construction inputs. Added external relational evidence reduced mean absolute discrepancy for five of six designated coefficients, while worsening CHNS BMI. In a separate six-author CHNS experiment, supplied target summaries enabled closer reconstruction: BMI coefficients averaged across each author's seeds ranged from 0.05282 to 0.05579 against the supplied 0.05495 reference. A public HRS example extended construction to complete longitudinal cohorts with 11,509 virtual subjects and four visits. The Agent reproduced a negative below-threshold HbA1c-by-age interaction across three draws, with mean coefficient −0.04464 versus the supplied −0.04684; a weak above-threshold interaction and high-HbA1c dispersion remained less reliable. Complete results and implementation failures were retained and independently checked. These experiments demonstrate analysis-specific uses of evidence-guided virtual data across differing information and modeling requirements. They support constructive use of published knowledge while showing that closer reconstruction of supplied information and transfer of external relationships are distinct achievements.

## Introduction

A biomedical research question can be well defined before the required individual measurements are available. Existing cohorts may omit an indicator, source records may be inaccessible, or no single study may contain the relevant combination of variables. Published findings nevertheless supply partial knowledge: distributions, adjusted associations, subgroup summaries and measurement definitions. Turning that information into a virtual dataset would let researchers execute their intended analyses and inspect the implications of the available evidence.

The scientific challenge is to construct a joint model from these fragments. An age-adjusted coefficient, a marginal correlation and a subgroup mean constrain different aspects of a distribution. Their meanings depend on the population, selection, measurement and adjustment variables of the reporting study. The generator must use compatible evidence and supply the missing structure through stated assumptions. Its useful output is both a table that standard software can analyze and an inspectable account of how that table was constructed.

Prior methods establish important parts of this problem. Filshtein and colleagues generated complete biomedical cohorts from source-specific rules estimated by collaborating analysts. SynthIPD reconstructs survival records and categorical covariates from published trial curves and subgroup summaries. Multilevel network meta-regression connects aggregate findings to individual models under population assumptions. [Filshtein et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8338788/); [SynthIPD v2](https://arxiv.org/html/2509.16466v2); [Phillippo et al.](https://rss.onlinelibrary.wiley.com/doi/full/10.1111/rssa.12579).

LLM-based approaches make model construction itself programmable. G-Sim combines simulator authorship with numerical calibration and structural refinement. LLMSynthor uses aggregate information to synthesize micro-records for downstream queries. SynthCraft assists biomedical synthetic-data workflows using individual-level inputs. Our question is how an Agent can make heterogeneous biomedical evidence operational for a requested dataset when individual construction records, and sometimes complete generating rules, are unavailable. [G-Sim](https://proceedings.mlr.press/v267/holt25b.html); [LLMSynthor](https://arxiv.org/html/2505.14752v4); [SynthCraft](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001290).

We contribute an implemented procedure for study-qualified evidence use and scientific model authorship, an analysis-centered evaluation of the resulting data under different available-information conditions, and a demonstration spanning complete cross-sectional and longitudinal cohorts. The Agent chooses scientific structure and parameters; deterministic software executes its proposal and reports checks. A research request may guide construction, and a new request may lead to a different generator. The reusable object is the procedure and its evidence record, not a single fixed biomedical equation.

The evidence is organized around three questions: what analyses external study fragments support, what accessible target summaries make recoverable, and whether detailed published models can be translated into a more complex longitudinal data product. These are separate experimental questions with separate reference interpretations. Whole-cohort generation without individual construction inputs is the central empirical application here. Indicator enrichment and missing-cell completion remain additional system modes, whose historical evidence is reported separately rather than inferred from whole-cohort performance.

## Methods
'''

start = methods.index('### Evaluation settings and scientific objective')
end = methods.index('### From qualified evidence to an executable joint law')
methods = methods[:start] + '''### Evaluation settings and scientific objective

We integrate three completed experiments without pooling their performance or treating their information conditions as a common factorial design (Table 1). The first compares basic/marginal with additional relational external evidence in two glycemic populations. The second compares external literature with literature plus accessible target summaries in CHNS. The third uses a public HRS generating-model example for longitudinal reconstruction. Individual-level data were not supplied to the constructors in any of these settings. Earlier real data established the CHNS/ENSANUT references; no HRS participant records were accessed for the public example.

**Table 1. Experimental questions, permitted information and units of evidence.** A construction is one authored scientific model; seeds sample that model. Table counts are not counts of independent clinical studies. Protocols and information packets differ across rows.

| Setting and question | Permitted construction information | Authorship and valid delivery | Meaning of the reference comparison |
|---|---|---|---|
| External-evidence developmental study: which requested relationships can be supported? | CHNS/ENSANUT population requests and curated external evidence; target coefficients withheld from fresh author contexts | 20 Agent + 4 prescribed statistical constructions; 72 final tables, 3,000 rows each | Analysis agreement with previously exposed selected-sample references; no restored untouched confirmation |
| CHNS summary-assisted study: can accessible aggregate findings become useful joint data? | External literature in L; the same literature plus 30 target summaries and accompanying reference metadata in R | 6 Agent constructions; 18 distinct final deliveries, 3,000 rows each; 24 distinct tables including trials | Reconstruction of explicitly provided quantities in R; not an independent target prediction |
| HRS public-model example: can the procedure construct longitudinal data for a published analysis? | Published model exports, method code, population specification and requested analysis | 1 Agent + 1 reconstructed published-law specification; 6 valid tables, 11,509 subjects × 4 visits each | Source-rich model reconstruction; 3 initial invalid comparator tables additionally retained in a 9-attempt record |

A subsequent three-table CHNS statistical supplement is a separate calibration reference for the supplied-summary setting. Historical studies with other protocols and method versions remain in the supplement. The detailed methods below retain the two-case main-study definitions before describing each additional setting.

''' + methods[end:]

# Shift the pre-existing numbered tables; the new setting map is Table 1.
methods = methods.replace('**Table 1. Prespecified', '**Table 2. Prespecified')
results = results.replace('Table 2', 'Table 3').replace('Table 1', 'Table 2')
results = results.replace('(Table 3; Figure 3)', '(Table 4; Figure 3)')
results = results.replace('**Table 3. Analysis results in the CHNS', '**Table 4. Analysis results in the CHNS')
methods = methods.replace('R additionally received all 30 existing target summaries: three adjusted regression estimates and 27 marginal/joint diagnostics.', 'R additionally received the existing target-summary package: three adjusted regression estimates and 27 marginal/joint diagnostics, accompanied by the available uncertainty, design and quality metadata.')
methods = methods.replace('its source packet and author allocation are not merged with main-study E0/E1.', 'its source packet and author allocation are not merged with main-study E0/E1. In particular, its historical external packet included Pani evidence, which was absent from the main CHNS conditions.')
methods = methods.replace('Each construction request specified a population, five variables', 'Each main-study construction request specified a population, five variables')
methods = methods.replace('Evaluation retained all six focal coefficients plus 27 CHNS or 28 ENSANUT distribution and joint diagnostics per table.', 'Across the two cases, evaluation retained six focal coefficients; each table was evaluated on its three case-specific regressions and 27 CHNS or 28 ENSANUT distribution and joint diagnostics.')

worked_example = '''### Worked example: translating separate adjusted projections

CHNS2009 E1 A01, selected by its first ordinal identifier rather than its performance, illustrates the actual scientific construction. Jansen's separate age/sex-adjusted HbA1c slopes were `cB = 0.13` for BMI and `cG = 2.29` for glucose in native IFCC response units. The Agent represented age/sex-residual BMI and glucose by `b` and `g`, with residual SDs `sB` and `sG`, and assumed residual correlation `r = 0.25`. A response containing `thetaB*b + thetaG*g` then implies the separate projections

```text
cB = thetaB + thetaG * r * sG/sB
cG = thetaG + thetaB * r * sB/sG.
```

With residual SDs 4.07611 and 0.49694 after the stipulated age/sex contributions, the implemented solution was `thetaB = 0.0642173` and `thetaG = 2.1583154`. Multiplication by the IFCC-to-NGSP slope factor 0.09148 gave 0.00587460 and 0.19744269 in percentage-point response units. Thus the Agent translated separate projections into a joint equation rather than inserting both reported slopes unchanged. Residual correlation, age/sex contributions, factor distributions, target mixture structure and source-to-target transport remained assumptions. The [source-to-generator trace](SUPPLEMENT_SOURCE_AND_ASSUMPTIONS_v05.md) binds these equations to the frozen code and includes the unfitted Bao correlation check and this constructor's target BMI mismatch. The calculation demonstrates a numerical evidence-use operation, not a newly identified joint distribution or uniform source agreement.

'''
methods = methods.replace('### Cases and information conditions\n', worked_example + '### Cases and information conditions\n')

methods += '''### Published-model reconstruction of a complete longitudinal cohort

The third experiment used the public HRS recipient-stage example of Filshtein et al. Published model exports and method definitions were pinned to repository commit `6708e43d5e342fa76d57b31d5a6d0bfcc2979539`. One fresh scientific Agent received those artifacts, the requested variables, visit schedule and analysis. It selected the published recursive conditional family and authored an executable implementation with parameter-level provenance. A separately implemented statistical comparator reconstructed the published generating law. This experiment concerns the HRS recipient-stage generator, not the paper's entire HRS/ARIC pooling and imputation pipeline.

The construction generated demographic strata, age, childhood socioeconomic status, education and HbA1c, then repeated memory scores with correlated individual intercepts and slopes. Each final dataset comprised 11,509 synthetic subjects observed at 0, 2, 4 and 6 years, or 46,036 rows. The requested outcome model used `age60 = (age − 60)/10`, HbA1c terms `min(HbA1c − 6.5, 0)` and `max(HbA1c − 6.5, 0)`, their age interactions, demographic and socioeconomic terms, and subject random intercepts/slopes. Both constructions had three prescribed seeds, 6101–6103. The Agent used the published variance precision; the comparator squared the printed rounded standard deviations, a small disclosed implementation difference.

Evaluation fitted the same 16-fixed-effect R/lme4 mixed model to each completed table, using REML and the fixed optimizer settings. We retained every coefficient, SE, model-conditional Wald interval, variance component and convergence diagnostic, plus all 27 prespecified baseline distribution fields. Python independently recomputed the fixed coefficients and SEs conditional on the fitted variance components; it did not independently optimize REML. Original published coefficients were permitted inputs, so this evaluation measures model reconstruction and analysis preservation. The balanced synthetic visits also differ from the original study's 43,500 observed visits.

An implementation defect invalidated the first three comparator tables: a CRLF-sensitive source parser crossed model boundaries and overwrote seven HbA1c coefficient/SE pairs. A separately reviewed technical recovery restored only those source-bound pairs and their locators, with unchanged generator code and other parameters, then generated three corrected comparator tables. The Agent outputs remained frozen and were not regenerated. Thus nine physical generations produced six valid comparison tables and three retained invalid initial comparator deliveries. All failures and the overturned preparation assessment remain in the [incident record](../work/hrs_public_example_2026-11-03/recovery_v1/INCIDENT_AND_CORRECTION.md). This defect belongs to our implementation, not the published method.

'''

hrs_results = '''### The procedure also constructed a complete longitudinal data product

All three Agent HRS datasets and three corrected published-law datasets supported the specified longitudinal mixed model. Every fit returned the 16 specified effects, converged without a warning or singular fit, and passed the conditional-GLS verification. The below-threshold HbA1c-by-age coefficient averaged −0.044635 in the Agent data, with three-seed range −0.051059 to −0.038247, against the supplied −0.046837. The reconstructed published law averaged −0.040500. Both implementations retained the negative direction in all three draws (Figure 4).

The weak above-threshold interaction was less stable. Agent estimates averaged 0.026485, versus the supplied 0.012867, and one of three model-based intervals excluded zero although the source interval included zero. All three corrected-law point estimates were negative, with mean −0.011691 and intervals including zero. Three draws from nearly the same supplied family, with different random-effect sampling implementations and a minor variance-rounding difference, do not identify a general accuracy ordering. The [complete 16-effect figure](integrated_figures_v07_2026-11-03/figures/figS1_longitudinal_all_effects.svg) and [all-seed coefficient table](../work/hrs_public_example_2026-11-03/summary/fixed_effects_all_seeds.csv) retain every effect.

![Published-example longitudinal relationships](integrated_figures_v07_2026-11-03/figures/fig4_longitudinal.svg)

**Figure 4. Longitudinal analysis of complete virtual HRS cohorts.** Both prespecified HbA1c-by-age interactions are shown for all three Agent and three corrected published-law draws. Each synthetic estimate has its model-conditional 95% Wald interval; the exported source estimate and its reported SE-based interval are distinguished. These intervals are different from the three-seed ranges in Figures 2–3 and Supplementary Figure S1 and do not account for structural or source-to-target uncertainty. The analysis coefficients were supplied during construction. The three invalid initial comparator deliveries are retained in the incident record and excluded from the comparison, not treated as published-method failures.

Overall Agent HbA1c mean/SD averaged 5.8725/0.9676, close to the paper's original 5.9/1.0. However, the subgroup at or above 6.5% had mean/SD 7.1515/0.5630, compared with original 7.7/1.4 and the paper's own synthetic 7.2/0.6. The comparator had the same covariate summaries for these seeds. The procedure therefore reproduced useful aspects of the source law while inheriting its inadequate high-value spread. Complete [baseline diagnostics](../work/hrs_public_example_2026-11-03/summary/distributions_all_seeds.csv) preserve that mismatch. The example broadens the demonstrated data product to repeated measures, piecewise relations, interactions and individual effects; it does not add independent patient observations or a new simulation family.

'''
results += hrs_results

discussion = '''## Discussion

These studies demonstrate a practical evidence-to-data workflow: an Agent can construct complete, analyzable biomedical tables using study-qualified statistical information, a population description and an explicit research request. The scientific work is the selection of a joint model, the interpretation of evidence as numerical constraints and the declaration of missing structure. The resulting data support ordinary analysis software. The experiments characterize that use across externally transferred fragments, accessible target summaries and a detailed published longitudinal model.

The three settings answer complementary questions. With external evidence alone, additional relational information brought five of six designated effects closer to the developmental references but worsened one and left meaningful magnitude discrepancies. With target summaries available, independently authored models reconstructed adjusted regressions and both linear and rank associations more closely. With the HRS source model available, the procedure generated longitudinal cohorts supporting the published mixed-model analysis. The increasingly informative inputs explain different opportunities for construction; these separate studies are not a controlled information ladder or a pooled success rate.

The contribution is an applied biomedical methods procedure with observed analytical uses. Its scientific specificity lies in retaining what a reported number means—population, measurement and adjustment set—while an Agent determines its role in a joint model. Existing methods already generate from summaries and use LLMs to author or revise simulators. Our results add an inspectable implementation and empirical characterization of this evidence-to-model task. The HRS comparison gives a concrete public-method example without requiring a newly customized statistical opponent for every clinical dataset. The already completed statistical references show achievable quality in their stated settings and remain part of the evidence.

Several limitations directly determine how to use the generated data. CHNS and ENSANUT are exposed developmental reference families, and their shared source evidence reduces independence. The HRS example uses a different source family but supplies the model coefficients and has no independent participant-level validation. The external-only data retain effect-size and directional mismatches, including the CHNS conditional-age reversal in one E1 construction. Summary-assisted agreement is demonstrated for provided quantities; additional analyses depend on completion assumptions. The HRS high-HbA1c spread illustrates that a useful fitted relationship and a well-recovered full distribution are distinct properties. Historical negative studies and tail defects remain visible in the supplement.

Reference samples also have uncertainty and are not known population distributions. Conversely, uncertainty in a reference does not make an observed mismatch irrelevant. The final-table seed ranges quantify sampling from a chosen law. HRS Wald intervals are conditional on a fitted synthetic-data model. Neither represents uncertainty across plausible evidence extractions, model structures or population transfers. Larger generated tables can stabilize the numerical implications of a model, but do not add clinical evidence. The supported application is population-level analytical reconstruction and scenario exploration under stated assumptions, not recovery of a person's unmeasured biomarker or confirmation of a new clinical effect.

The present implementation retains researcher curation of evidence and case-specific evaluation definitions. Thus reduced access to individual construction records is demonstrated, whereas fully autonomous paper processing and measured reductions in end-to-end human effort are not. Exact model-snapshot identifiers and token costs were incompletely metered in historical runs. Feedback is available as an operation, but the main and six-author summary experiments retained their models without a measured revision gain. Revision is therefore optional in the method and is not a headline efficacy claim.

A focused next validation would freeze the current procedure for one prospectively selected, previously unexposed reference and a small set of declared analytical uses. It would test whether useful external-evidence generation transfers beyond the development cases. An extraction-to-model audit is a separate requirement only if autonomous article processing becomes a claimed contribution. Neither extension justifies retuning the already disclosed targets. The present manuscript can report the completed construction and reconstruction evidence while keeping these stronger claims explicit as future work.

## Data, code and supporting material

The [public repository](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026) contains reviewed protocols, original code, aggregate results and independent checks. The [main-study report](../work/main_study_freeze_2026-11-03/RESULTS.md), [information-provision report](../work/information_revision_ablation_2026-11-03/RESULTS.md), [statistical supplement](../work/summary_comparator_2026-11-03/RESULTS.md) and [HRS public-example report](../work/hrs_public_example_2026-11-03/RESULTS.md) preserve their own inputs, allocations, failures and complete results. The [integrated figure package](integrated_figures_v07_2026-11-03/FIGURE_PLAN.md) maps each panel to its existing records. Historical drafts and failed experiments remain available. Individual real/generated records, third-party full texts and credentials remain local. This writing revision does not reopen any experimental budget or alter frozen artifacts.

## References and source-access status
'''

draft = intro + methods + '## Results\n' + results + discussion + references
draft = draft.replace('converts study-qualified findings, a population description', 'converts curated, study-qualified findings, a population description')
draft = draft.replace('negative below-threshold HbA1c-by-age interaction across three draws', 'negative below-threshold HbA1c-by-age interaction for memory across three draws')
draft = draft.replace('while showing that closer reconstruction of supplied information and transfer of external relationships are distinct achievements.', 'while showing that reconstruction of supplied information and evaluation of externally transferred relationships answer different questions.')
draft = draft.replace('The increasingly informative inputs explain different opportunities for construction;', 'The inputs in each setting support different construction tasks;')
draft = draft.replace('Thus reduced access to individual construction records is demonstrated,', 'Thus construction without individual-level inputs is demonstrated,')
draft = draft.replace('Their access record distinguishes freshly checked publication records from previously retrieved full text,', 'Their previously completed access record distinguishes publication-record checks from retrieved full text,')
draft = draft.replace('Bibliographic metadata for SynthCraft, Jansen and Wang were checked against publisher pages for this revision;', 'Bibliographic metadata for SynthCraft, Jansen and Wang were checked against publisher pages during v0.6 preparation;')
draft = draft.replace('The predecessor comparisons use the primary-source reading', 'This integration retains the existing bibliography and adds no field-priority claim or new literature search. The predecessor comparisons use the primary-source reading')
draft = draft.replace('Indicator enrichment and missing-cell completion remain additional system modes, whose historical evidence is reported separately rather than inferred from whole-cohort performance.', 'Indicator enrichment has historical supporting experiments; missing-cell completion is an additional system mode not validated by the experiments assembled here. Their evidence is distinguished in the [integrated ledger](INTEGRATED_EVIDENCE_LEDGER_v07_2026-11-03.md), rather than inferred from whole-cohort performance.')
draft = draft.replace('utility_package_2026-11-03/NUMERIC_MANIFEST.json', 'integrated_figures_v07_2026-11-03/NUMERIC_MANIFEST.json')
history = '''### Earlier enrichment and direct-output results provide supporting context

Earlier frozen experiments tested a related data gap: observed covariates were retained while an entirely unmeasured biomarker was generated. The insulin constructions retained selected BMI and curvature directions, while the HbA1c constructions retained age and BMI directions but not all nonlinear or interaction findings. A separate small urate example directly authored the added values as table text and included Agent-directed literature acquisition with controller assistance; it retained selected associations but missed the age relationship and overestimated subgroup variability. These different versions support limited mode-specific feasibility. They do not establish missing-cell completion, a common-protocol comparison of direct versus programmatic output, or automatic retrieval in the present main studies. The [integrated evidence ledger](INTEGRATED_EVIDENCE_LEDGER_v07_2026-11-03.md) links all denominators and failures to their original reports.

'''
draft = draft.replace('## Discussion\n', history + '## Discussion\n', 1)
draft = draft.replace('story_package_2026-11-03/figures/figure1-evidence-to-analysis.drawio.svg', 'integrated_figures_v07_2026-11-03/figures/fig1_method.svg')
draft = draft.replace('utility_package_2026-11-03/figures/figure1_main_scientific_utility.svg', 'integrated_figures_v07_2026-11-03/figures/fig2_external_evidence.svg')
draft = draft.replace('utility_package_2026-11-03/figures/figure2_chns_information_conditions.svg', 'integrated_figures_v07_2026-11-03/figures/fig3_summary_assisted.svg')
assert draft.count('## Abstract\n') == 1
assert draft.count('## Methods\n') == 1
assert draft.count('## Results\n') == 1
assert draft.count('## Discussion\n') == 1
assert 'has not been performed in the studies reported here' not in draft
(M / 'DRAFT_v0_7.md').write_text(draft, encoding='utf-8')
print(f'Wrote DRAFT_v0_7.md: {len(draft.split())} whitespace-delimited words')
