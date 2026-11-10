"""Reorganize audited findings; never read individual data or run a generator."""
from pathlib import Path
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
source=P/'manuscript/DRAFT_v0_25.md'
text=source.read_text(encoding='utf-8')

def section_replace(start,end,replacement):
    global text
    assert text.count(start)==1 and text.count(end)==1,(start,end)
    a=text.index(start); b=text.index(end,a)
    text=text[:a]+replacement.strip()+'\n\n'+text[b:]

# Promote the core-replication display; all supplementary numerical rows remain.
pattern=r'!\[Repeated open-retrieval scientific analyses\]\([^\n]+\)\n\n\*\*Figure S2\.[^\n]+\n\n'
text,n=re.subn(pattern,'',text); assert n==1
def numbers(match):
    old=match.group(1)
    return 'Figure '+({'3':'5','5':'6','S2':'3','S3':'S2','S4':'S3','S5':'S4','S6':'S5'}.get(old,old))
text=re.sub(r'\bFigure (S?\d+)\b',numbers,text)
text=text.replace('Methods working draft v0.25, 8 November 2026.','Methods working draft v0.26, 9 November 2026.')
text=text.replace('Section 5.1 shows their consequences','Section 5.3 shows their consequences')

section_replace('## Abstract','## 1. Introduction', '''## Abstract

Biomedical studies often make aggregate findings available while the individual measurements needed for a new analysis remain inaccessible. We study whether a scientific agent can turn such evidence and a research request into analyzable virtual cohorts. The agent interprets study conditions, chooses a joint stochastic model, and supplies numerical relationships and explicit assumptions; statistical tools execute the model and inspect its outputs. In an open-retrieval evaluation, four constructions produced twelve complete cohorts. All six requested glycemia analyses retained their sample-reference point directions across draws, with differing magnitude agreement; both constructions for one population preserved attenuation of the BMI coefficient after glucose adjustment. In a separate two-case experiment with twenty agent constructions, additional published relationship evidence reduced mean absolute discrepancy for five of six regression coefficients. Comparisons with a fixed statistical completion favored the agent arm in four of six relationship-evidence analyses. Iron-status and lipid results demonstrate useful analyses alongside substantial joint-dependence and dispersion mismatches, and an earlier prospective evaluation failed both overall criteria. These findings support analysis-specific use of evidence-guided virtual data and identify the scientific modeling work needed to construct them without target individual-level training records.''')

section_replace('## 1. Introduction','## 2. Related work and problem definition', '''## 1. Introduction

A researcher wants to analyze how BMI, age and glucose relate to HbA1c in a population for which individual measurements are unavailable. Published studies provide pieces of the required information: biomarker summaries, age profiles and regressions adjusted for different covariates. These findings do not arrive as a joint dataset or a complete simulation model. To run a multivariable analysis, someone must decide how the pieces can be combined and which additional relationships must be assumed.

We study an evidence-to-data workflow in which a scientific agent undertakes that modeling work. The researcher specifies the population, measurements and intended analyses. The agent works from reviewed evidence or retrieves studies under the task's access rules, chooses how to connect the variables, and authors a stochastic generator. Its output is a virtual cohort accompanied by the executable model and a record of source-supported and assumed choices. Researchers can then apply ordinary regression, stratified or other specified analyses to its records. Complete generation requires no target individual-level training records; optional observed variables can instead support enrichment or partial completion.

The research question is whether the resulting data preserve the information needed for the requested analyses. A single coefficient is not enough to describe this property. The same cohort may need to support both a BMI regression adjusted for age and sex and a second regression additionally adjusted for glucose. Agreement requires a useful joint construction, while the source studies may report only separate projections. An agent can choose such a construction, but the assumptions it adds can also produce biased effects, weak interactions or insufficient individual variation.

Our contribution is a concrete scientific-agent procedure for converting heterogeneous biomedical evidence into analyzable records, together with an analysis-level evaluation of the resulting data. We first show repeated construction for two glycemia requests, including the behavior of BMI coefficients before and after glucose adjustment. We then test the value of relationship evidence and compare with a specified statistical completion. Iron-status and lipid analyses expose how useful and unsupported properties can coexist in one table. Published-model reconstruction, historical input modes and earlier prospective failures retain their distinct roles. The study documents both practical uses and the conditions under which they remain unvalidated.''')

architecture_note='''The experiments implement this common procedure through versioned controllers rather than one unchanged runtime. The main evidence contrast uses curated packets; the open-retrieval replication lets authors select studies; later prototypes connect a broader action loop and source-context execution. Optional capabilities are attributed only to runs that exercised them. Different study protocols and references are not pooled as tests of the latest release.

'''
text=text.replace('## 3. How a scientific agent constructs an analyzable cohort',architecture_note+'## 3. How a scientific agent constructs an analyzable cohort',1)

text=text.replace('Each experiment specifies what the constructor can see and which analyses the delivered table should support (Table 3). We summarize the iron case first because it asks three questions of one dataset. The glycemia evidence contrast then varies one input to construction.',
'Each experiment specifies what the constructor can see and which analyses the delivered table should support (Table 3). We first evaluate complete cohorts built for two glycemia requests, then examine the information contrast and additional biomedical uses.')
old='''| Iron status | External evidence; target eligibility; no target biomarkers | 2 agent; 6 tables of 5,000 | Threshold association, joint burden and continuous ranks |
| Q1: CHNS and ENSANUT | Basic evidence (E0); E0 plus external relations (E1) | 20 agent + 4 prescribed; 72 tables of 3,000 | Six adjusted glycemia coefficients |'''
new='''| Q4: open-retrieval replication | Population/measurement definitions and analyses; no bibliographic seeds or target records/results | 4 agent; 12 tables of 3,000 | Six glycemia analyses; adjustment patterns |
| Q1: CHNS and ENSANUT | Basic evidence (E0); E0 plus external relations (E1) | 20 agent + 4 prescribed; 72 tables of 3,000 | Six adjusted glycemia coefficients |
| Iron status | External evidence; target eligibility; no target biomarkers | 2 agent; 6 tables of 5,000 | Threshold association, joint burden and continuous ranks |'''
assert old in text; text=text.replace(old,new,1)
text=text.replace('| Q2 / Q4: supporting conditions | Q2: with or without 30 target summaries; Q4: open paper retrieval without bibliographic seeds | Q2: 6 agent laws / 18 distinct tables; Q4: 4 / 12 | Reconstruction of supplied summaries; repeated open retrieval |',
'| Q2: supplied-summary reconstruction | With or without 30 target summaries | 6 agent laws; 18 distinct tables | Reconstruction of supplied summaries |')

start=text.index('## 5. Results'); end=text.index('## 6. Discussion')
old_results=text[start:end]
parts=re.split(r'(?=### 5\.\d+\.)',old_results)[1:]
assert len(parts)==4
iron,evidence,cross,reconstruction=parts
iron=iron.replace('### 5.1.','### 5.3.',1)
cross=cross.replace('### 5.3.','### 5.4.',1)
reconstruction=reconstruction.replace('### 5.4.','### 5.5.',1)
evidence=evidence.replace('The iron case illustrates what a fixed source packet leaves open. The next comparison asks whether adding published associations to basic evidence helps constrain a model.',
'The next comparison asks whether published associations help constrain the scientific information in a generated cohort beyond basic summaries.')
evidence=evidence.replace('Table S1 reports both statistical arms and both agent arms for all six analyses.',
'''Table S1 reports both statistical arms and both agent arms for all six analyses.

Agent arm averages were closer than the delivered statistical specification in six of six E0 comparisons and four of six E1 comparisons. The comparator completes unprovided within-source dependence by independence under its entropy criterion; mixing sources can still induce dependence. Agents can instead choose dependent structures and document their assumptions. In ENSANUT E1, they used the published age slope numerically, whereas the fixed specification left it contextual because source covariates, dispersion and weighting were unbound. These are relevant differences in evidence use under incomplete specification. Five Agent constructions versus one fixed construction per arm do not establish superiority over statistical model search, and every E1 Agent lost to the statistical reference on CHNS glucose and ENSANUT glucose-adjusted BMI.''')

cap_file=HERE/'FIGURE_CAPTION.md'
if cap_file.exists():
    caption=next(line for line in cap_file.read_text(encoding='utf-8').splitlines() if line.startswith('**Figure 3'))
    caption=caption.replace('**Figure 3 |','**Figure 3.',1)
    assert caption.startswith('**Figure 3.')
else:
    caption='''**Figure 3. Scientific analyses of complete Agent-generated cohorts.** All six prespecified analyses, four constructions and 36 estimates from twelve final tables are retained. Individual marks show three draws per law, with a distinct mean marker and a seed range. References use CHNS community-cluster CR1-t 95% intervals and ENSANUT cluster-resampling stability bands. Seed ranges are not confidence intervals; neither reference band is an equivalence criterion. Native units and zero are retained. These are developmental replications on existing references.'''

core='''### 5.1. Can generated cohorts support the requested scientific analyses?

Four fresh authors constructed complete cohorts for the CHNS and ENSANUT requests through open paper retrieval. They received the analyses and population definitions, but no target measurements, coefficients, desired signs or prior models. Their twelve final 3,000-row tables supported all six requested analysis definitions. All 36 seed estimates retained the reference point direction; the effective replication units are four authored laws and two requests, not 36 independent discoveries. A separate implementation reproduced all 366 reported coefficients and diagnostics on the frozen outputs (Supplement S3).

For CHNS, the two construction means for age/sex-adjusted BMI were 0.03992 and 0.05338 against a reference of 0.05495 HbA1c percentage points per kg/m². The corresponding glucose coefficients were 0.37754 and 0.49241 against 0.40209 percentage points per mmol/L. The conditional age coefficients were smaller than the reference: 0.00311 and 0.00563 versus 0.00811 per year. Both authors therefore produced useful associations, with different magnitude trade-offs (Figure 3).

For ENSANUT, the BMI coefficient before and after adding glucose adjustment changed from 0.09165 to 0.07509 in E01 and from 0.07140 to 0.04733 in E02, compared with 0.08364 to 0.05664 in the sample reference. Every draw preserved attenuation using the same generated records. This is a multivariable association pattern, not causal mediation or a wholly evidence-independent discovery. Both age coefficients were too large, and residual HbA1c RMS was only approximately 0.295/0.324 against 0.488. Direction and adjustment behavior did not ensure adequate individual variability.

![All six scientific analyses under four complete-cohort constructions](paper_figures_v26_2026-11-09/fig3-analysis-utility.svg)

'''+caption+'''

A separate real-real context analysis evaluated three earlier tables from one evidence-to-generation law, not these four authors. Across 100 community-disjoint CHNS resplits, the median absolute reduced-model BMI difference was 0.007239; symmetric generated-real discrepancy medians were 0.004383–0.012727. Age discrepancies were also on a similar numerical scale, while the full-model glucose discrepancy remained appreciably larger than real-real variation. This supplies descriptive context rather than an equivalence threshold, and does not make 100 resplits independent cohorts (Supplement S6).

'''
text=text[:start]+'## 5. Results\n\n'+core+evidence+iron+cross+reconstruction+text[end:]

section_replace('## 6. Discussion','## Limitations and Ethical Considerations', '''## 6. Discussion

The strongest use demonstrated here is converting incomplete scientific information into a table that supports a specified analysis. In the open-retrieval cases, different authored models preserved several effect magnitudes and the reduction in the BMI coefficient after glucose adjustment. In the separate information experiment, relationship evidence improved five of six analysis discrepancies. These findings locate practical value in the evidence-to-model construction: the user can state the research problem without first writing a complete joint generator.

The favorable fixed-comparator results occur under incomplete joint specification. They motivate examining how an Agent uses evidence and supplies dependence assumptions, not assuming that language-model generation replaces statistical modeling. The Agent-generated cohorts themselves are statistical models sampled by numerical tools. The implementation contribution is assigning the scientific construction to an author that can interpret different studies and requests, while preserving an executable result. Fully supplied summaries and fitted models are useful reconstruction controls; conventional calibration also performs well in those settings.

Whole-cohort generation and variable extension share this evidence-to-model problem. A richer historical pilot also showed that literal synthetic training rows can retain predictive information on later real participants, but its outcome-conditioned training summaries differ from our literature-driven inputs (Supplement S14). These modes show a practical range of uses without establishing that one unchanged controller or one model law works everywhere. Recent adaptive and source-context prototypes demonstrate additional executed capabilities separately (Supplement S15).

Some scientific properties remain poorly determined. The iron model closer on joint prevalence was not the model closer on continuous ranks; both missed the primary target odds ratio. Lipid residual dependence and glycemia dispersion also remained inaccurate. The diagnoses point to evidence adequacy and joint/transfer assumptions as leading explanations, without uniquely identifying their contributions. A controlled diagnostic with exact compatible summaries found that ordinary constructors already reconciled separate projections into the same joint law; adding a consistency instruction gave no improvement (Supplement S13). These results support a simple workflow with explicit assumptions and use-specific evaluation. They do not show that a source-consistency label can predict reliability before a target comparison.''')

text=text.replace('The protocols differ across studies. No held-out trial shows that review improves outcomes or that the workflow saves a measured amount of human time.',
'The protocols and controllers differ across studies; the main evidence and open-retrieval results are developmental evaluations on previously exposed project references. Their shared procedure should not be mistaken for a multi-case confirmation of the newest adaptive controller. Some historical dispatches record an inherited host model without the exact backend identity, limiting model-specific reproduction and attribution. No held-out trial shows that review improves outcomes or that the workflow saves a measured amount of human time.')
text=text.replace('No new clinical cohort was generated for this revision. Supplement S13 reports a separate artificial mechanism diagnostic.',
'This manuscript revision reorganizes existing frozen results and promotes the complete open-retrieval analysis display. No new clinical cohort was generated or target refitted. Supplement S13 reports a separate artificial mechanism diagnostic; Supplements S14–S15 distinguish the historical predictive-use study and later implementation development.')

# Explicitly distinguish the supporting law's evaluation from the core replication.
text=text.replace('A separate analysis contextualized the same three tables with 100 community-disjoint resplits of the existing CHNS sample, drawing 3,000 people per side and retaining all 36 metrics. Secondary BMI and age discrepancies were on scales comparable with within-sample variation, while primary glucose/female and several joint/tail discrepancies were larger. The complete table preserves the nonexchangeable real-real and generated comparisons. These are descriptive interpretation aids, not a new population or retrospectively selected equivalence cutoff.\n\n','')
anchor='### S7. Prospective evaluation under the earlier method'
context='''The [real-real context analysis](../work/real_real_calibration_2026-11-04/RESULTS.md) reuses this evidence-to-generation law (`evcBuild01`, seeds 7401–7403). It does not evaluate the four Q4 authors. One hundred fixed community-disjoint partitions of the selected CHNS sample each provided two 3,000-person subsamples. Across the nine coefficients, 21 marginal summaries and six correlations, all 36 metrics were retained. Reduced-model BMI had median real-real difference 0.007239 versus generated-real symmetric discrepancy medians 0.004383–0.012727; reduced-model age had 0.001705 versus 0.001055–0.002387. Full-model glucose was 0.023839 versus 0.079642–0.109154. These selected examples illustrate agreement and disagreement relative to ordinary resampling variation; the complete report contains every metric. The resplits do not define population truth, independent cohorts or prespecified acceptable margins.

'''
assert anchor in text;text=text.replace(anchor,context+anchor,1)

text+='''

### S14. Historical synthetic training on a later real sample

The [October 25 temporal pilot](../../obesity_temporal_prediction_2026-10-25/RESULTS.md) tested a different input setting and direct-row output route. Two fresh authors literally supplied 128-row cohorts from rich outcome-by-sex-conditioned summaries of 128 real NHANES2015–16 training participants. Inputs included counts, means, SDs, quantiles and regularized Gaussian-rank correlations. An ordinary Gaussian-copula generator supplied 100 comparison cohorts. The predictor set was age, sex, BMI, waist and systolic blood pressure; HbA1c and design variables were not predictors. The outcome was current HbA1c at least 5.7% among adults with BMI at least 30, not future diabetes or obesity classification.

All preprocessing and classifier artifacts were locked before the NHANES2017–18 test download. Evaluation used 1,811 eligible test participants. Table S8 retains the primary logistic and secondary histogram-gradient-boosting results. Both Agent cohorts carried predictive information, but neither exceeded the real-training AUC. One was below and one above the ordinary-generation median in each classifier, both within the ordinary draw distributions. The ordinary median summarizes 100 draws, not 100 independent studies. Neither a confidence interval nor a noninferiority test was calculated for the AUC differences. The complete report also retains log loss, balanced accuracy and weighted sensitivity analyses. This is evidence of historical downstream utility under rich real-training summaries, not a literature-only or current-controller confirmation.

**Table S8. Historical synthetic-training utility on later real participants.** Higher AUC and lower Brier score indicate better performance on this selected sample. Agent rows come from two literal 128-row datasets. The ordinary entry is the median across 100 generated training cohorts. Both classifiers used the same 1,811-person test; no rows were regenerated after test disclosure.

| Classifier | Training cohort | AUC | Brier score |
|---|---|---:|---:|
| Logistic (primary) | Real 128 | 0.734936 | 0.210303 |
| Logistic (primary) | Agent A1 | 0.712130 | 0.216229 |
| Logistic (primary) | Agent A2 | 0.726871 | 0.213445 |
| Logistic (primary) | Ordinary, median | 0.717394 | 0.215560 |
| Histogram boosting (secondary) | Real 128 | 0.660930 | 0.240598 |
| Histogram boosting (secondary) | Agent A1 | 0.634484 | 0.247879 |
| Histogram boosting (secondary) | Agent A2 | 0.646883 | 0.242525 |
| Histogram boosting (secondary) | Ordinary, median | 0.638858 | 0.261487 |

### S15. Later adaptive and source-context implementation

The [bounded adaptive case](../work/adaptive_case_loop_2026-11-09/RESULTS.md) executed 28 dispatched actions, including retrieval, construction, inspection and a final choice. The author produced two scientific models and six tables, then retained the initial model. Its sensitivity altered two analyses in different directions of reference agreement. This is executed scientific decision-making, with zero initial-to-selected-final improvement. It is not a new clinical population or a controlled estimate of a feedback benefit.

The [source-conditioned replay](../work/source_conditioned_replay_2026-11-09/RESULTS.md) next linked one Agent-authored shared source/target law to eight sex/site-stratified BMI–lipid coefficients from the [admitted source study](https://doi.org/10.1136/bmjgh-2019-001542). Four source contexts and three seeds yielded twelve 8,000-row source tables and 24 numerical projections. All reported directions were retained, with independent QR/FWL arithmetic agreement within 5.9e-15. The source weighting and BMI-standardization convention remained unresolved: every strict semantic check stayed unavailable, and the numerical projections were explicitly assumption-dependent. The Agent retained the initial law. Three subsequent 3,000-row target-scenario tables supported nine requested estimates and 69 descriptive calculations without a new clinical-reference comparison. Residual component coupling could change substantially while the mean slopes remained fixed. These results demonstrate source-conditioned execution and attributable assumptions, not independently established target accuracy.

The [method-coverage audit](../work/manuscript_focus_v26_2026-11-09/METHOD_COVERAGE.md) separates these implementations from the curated Q1 comparison, open-retrieval Q4 workflow, Q5 evidence-use interface, iron source pilot, HRS reconstruction and earlier prospective controller. They share the scientific procedure described in Sections 2–3. Optional later components were not exercised in every historical case and are not credited retroactively. No participant or generated row table was opened for this manuscript integration.
'''

out=P/'manuscript/DRAFT_v0_26.md'
text=text.replace('In an open-retrieval evaluation, four constructions produced twelve complete cohorts.',
                  'In a developmental open-retrieval evaluation on previously exposed project references, four constructions produced twelve complete cohorts.',1)
text=text.replace('In a separate two-case experiment with twenty agent constructions, additional published relationship evidence reduced mean absolute discrepancy for five of six regression coefficients.',
                  'In a separate developmental two-case experiment with twenty agent constructions, additional published relationship evidence reduced mean absolute discrepancy for five of six regression coefficients.',1)
text=text.replace('Both Agent cohorts carried predictive information, but neither exceeded the real-training AUC.',
                  'A prevalence-only predictor using the training prevalence 68/128 had AUC 0.5 and Brier score 0.248578. Both Agent cohorts carried predictive information, but neither exceeded the real-training AUC.',1)
text=text.replace('Deterministic tools sampled the records and computed the reported analyses; separate implementations checked the numerical results where specified.',
                  'For program-based studies, deterministic tools sampled the records; the historical direct-row study used literal Agent-authored values. Deterministic tools computed the reported analyses, and separate implementations checked the numerical results where specified.',1)
out.write_text(text,encoding='utf-8')
report={'input':str(source.relative_to(P)), 'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'output':str(out.relative_to(P)), 'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
        'new_generation':False,'new_target_evaluation':False,
        'changes':['Application-led abstract and introduction','Complete core-replication result promoted to main Figure3',
                   'All six main evidence contrasts and comparator asymmetry retained','Iron and cross-task full findings retained',
                   'Explicit method-version scope','Real-real single-law provenance','Historical temporal utility separated in S14','Adaptive/source-context capability separated in S15'],
        'main_figures':6,'supplement_figures':5,'main_tables':3,'supplement_tables':8}
(HERE/'REVISION_FACTS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(out),'words':len(text.split()),'source_hash':report['input_sha256']}))
