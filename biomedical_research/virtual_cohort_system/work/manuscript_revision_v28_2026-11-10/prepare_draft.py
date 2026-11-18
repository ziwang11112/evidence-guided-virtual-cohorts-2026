"""Integrate reviewed retrospective attribution and the completed PNS task.

No scientific generator or evaluator is imported or run.
"""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
source = P / 'manuscript/DRAFT_v0_27.md'
old = source.read_text(encoding='utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source) == 'b2f013950d026b360de1e6001925913f2e2f96363b2b1bf5b30ac5106b87acdd'
text = old.replace('Methods working draft v0.27, 9 November 2026.', 'Methods working draft v0.28, 10 November 2026.', 1)
inserts = (HERE / 'STORY_INSERTS.md').read_text(encoding='utf-8')
changes = []

def block(name):
    marker = '## ' + name + '\n'
    assert inserts.count(marker) == 1, name
    result = inserts.split(marker, 1)[1].split('\n## ', 1)[0].strip()
    result = re.sub(r'^Placement:[^\n]*\n\n', '', result)
    result = re.sub(r'^### [^\n]*\n\n', '', result)
    return result.strip()

def replace(before, after, reason):
    global text
    assert text.count(before) == 1, before[:100]
    text = text.replace(before, after, 1)
    changes.append(reason)

def paragraph(prefix, after, reason):
    matches = [p for p in text.split('\n\n') if p.startswith(prefix)]
    assert len(matches) == 1, prefix
    replace(matches[0], after, reason)

paragraph('Biomedical studies often make aggregate findings', block('Abstract'), 'Reframe abstract around generation utility and analysis-specific attribution')
paragraph('Our contribution is an implemented scientific-agent procedure', block('Introduction contributions'), 'Describe demonstrated contributions without claiming predictive reliability labels')
paragraph('**Figure 1. The scientific agent', '**Figure 1. From a research request to a recorded model and an analyzable cohort.** The author selects a joint law and records evidence and assumptions; an isolated worker executes its program. The illustrated review loop is an implementation option under versioned study budgets. Q4, Q5 and PNS retained their first frozen, reviewed laws; the figure does not establish a quality benefit from feedback. Measured target results enter the comparison after closure where the protocol seals them. Table 1 identifies the actual actors and Supplement S12 the implementation paths.', 'Keep the accepted overview while clarifying that the loop is not the demonstrated scientific contribution')

attribution_methods = block('Attribution methods')
table = re.search(r'\| Quantity \| Meaning and role \|\n(?:\|[^\n]*\n?)+', attribution_methods)
assert table
attribution_methods = attribution_methods.replace(table[0], 'The source statistic retains its original population, measurement, adjustment, weighting and uncertainty. The adopted parameter records what the author placed in the generator and why. The full-model implication applies the requested analysis to the complete probability law, including its joint dependence, nonlinearities and selection; it need not equal a coefficient in the code. The generated estimate applies that analysis to a finite draw. The measured reference applies it to the eligible real sample, retaining its own selection, weighting and uncertainty.\n')
replace('## 5. Results', '### 4.1. Retrospective model-to-analysis attribution\n\n' + attribution_methods + '\n\n## 5. Results', 'Add retrospective audit methods with clear information exposure')

pns_row = '| Paired blood pressure | Identical external evidence and visible analyses; target BP results sealed until all authors closed | 5 agent; 15 tables of 3,000 | Age/sex-adjusted BMI effects on SBP and DBP; adjusted residual correlation |'
replace('| Earlier prospective wave | External summaries and population description; exact target results withheld | 5 agent + 1 prescribed per case; 36 tables of 5,000 | HAALSI glucose and Turkana lipid analyses |', pns_row + '\n| Earlier prospective wave | External summaries and population description; exact target results withheld | 5 agent + 1 prescribed per case; 36 tables of 5,000 | HAALSI glucose and Turkana lipid analyses |', 'Add PNS to evaluation inventory without treating the exposed family as a new cohort')

new_sections = '### 5.6. From evidence to a joint law and its scientific analyses\n\n' + block('Attribution results')
new_sections += '''

![Model implications, sampled estimates and measured references remain distinct](paper_figures_v28_2026-11-10/fig7-attribution.svg)

**Figure 7. Tracing model commitments into different scientific analyses.** Panel a separates the source-table/B-law crude odds ratio (6.653) from A's target-law implication after its assumed independent-Hb redraw (4.646), and shows all final generated estimates and the measured NHANES reference with its design-based 95% interval. Panel b shows continuous Hb-ferritin Spearman correlations from the same six tables; no population rank coefficient is implied by the published threshold table alone. Panel c shows L03's model-implied age/sex/BMI-adjusted residual TC-HDL Pearson correlation, its three generated estimates and the Turkana reference, for which no interval is available. Model implications are retrospective calculations under the frozen laws, not target fits or additional observations. The source's pooled Spearman correlation is a different statistic and is not plotted on the adjusted-Pearson axis. These panels illustrate inspectable model consequences, not uniquely identified causes of population discrepancies.

### 5.7. Does a further whole-cohort request retain the same analytical distinctions?

Five fresh author contexts constructed complete age, recorded-sex, BMI, SBP and DBP cohorts from identical external evidence. All fifteen outputs were sealed before the reference analyses were revealed. The PNS family had already been used for other outcomes, so this is a qualified new-task validation within an exposed release, not a new independent cohort. The reference consisted of 8,352 eligible laboratory-substudy records with supplied laboratory weights [41]. Both BMI regressions adjust for age and sex; the residual Pearson analysis additionally removes BMI from both blood pressures. Supplement S18 gives eligibility, measurement, uncertainty and all author summaries.

All fifteen tables supported the three analyses (Figure 8). Across all draws, BMI-SBP coefficients ranged from 3.081 to 4.276 mmHg per 5 kg/m², compared with the weighted reference 3.524. BMI-DBP coefficients were larger, 2.886-3.691 versus 2.260, while residual correlations were smaller, 0.466-0.646 versus 0.717. Unweighted reference estimates of 3.435, 2.114 and 0.741 retained this discrepancy pattern. Marginal SD ratios relative to the weighted reference ranged from 0.931 to 1.129 for SBP and 0.896 to 1.076 for DBP. Generated means were lower across all draws. The results therefore do not support a universal contraction of all variances, or adequacy of the full joint distribution from one favorable regression.

All five authors adopted INTERSALT's BMI coefficients, 0.7754 and 0.5967 mmHg per BMI unit, as conditional location parameters under explicit transfer assumptions [39]. The source coefficients pool within-centre regressions with additional sodium, potassium and alcohol adjustment. Nonlinear age terms, heteroscedasticity and selection mean that the requested age/sex-only projections need not equal those parameters. The five assumed pre-selection residual correlations were 0.50, 0.65, 0.50, 0.55 and 0.55; these are neither the older Beijing population's raw correlation [40] nor the requested post-selection residual estimand. Exact population projections were not computed in this audit.

To describe agreement among authors, we took each author's median over its three seeds and calculated the sample SD across the five medians. The absolute discrepancy between the mean of those medians and the measured reference was 1.02, 5.11 and 2.95 times that SD for SBP, DBP and residual correlation. These are descriptive ratios, not calibrated uncertainty intervals or z statistics. The constructions shared a host service, evidence and workflow. Their consistency does not establish cross-provider convergence or provide independent clinical corroboration.

![All five authors and all fixed blood-pressure draws](paper_figures_v28_2026-11-10/fig8-pns-utility.svg)

**Figure 8. Complete blood-pressure results across five authored laws.** Each panel shows all three fixed draws for each author and the weighted PNS reference. BMI effects are mmHg per 5 kg/m², adjusted for age and sex; residual correlation removes age, sex and BMI. The reference band is the 2.5th-97.5th percentile of 500 conditional IID row resamples retaining supplied weights. It is not a complex-survey confidence interval or an equivalence margin. Draws are nested within laws and all authors share one reference. Source conditional coefficients and assumed innovation correlations are not substituted for the requested population estimands. All five authors retained their initial reviewed law; no generation occurred after target disclosure.
'''
replace('## 6. Discussion', new_sections.strip() + '\n\n## 6. Discussion', 'Integrate attribution and complete PNS results with two new aggregate-only figures')

old_discussion = text.split('## 6. Discussion\n\n', 1)[1].split('\n## Limitations and Ethical Considerations', 1)[0]
retained_discussion = [p for p in old_discussion.split('\n\n') if p.startswith(('The favorable fixed-comparator', 'Whole-cohort generation and variable extension'))]
assert len(retained_discussion) == 2
new_discussion = block('Discussion') + '\n\n' + '\n\n'.join(retained_discussion) + '\n\nA controlled diagnostic with exact compatible summaries found that ordinary constructors already reconciled separate projections into the same joint law; adding a consistency instruction gave no improvement (Supplement S13). This result favors keeping the demonstrated procedure simple. Additional architecture is not a substitute for evidence that identifies the relationships required by a scientific use.\n'
replace(old_discussion, new_discussion, 'Align interpretation while retaining comparator, broader-use and negative controlled-experiment findings')
new_use = '| PNS: BMI associations with both blood pressures and their adjusted dependence | All five laws produced analyzable records; BMI-SBP magnitudes overlapped the conditional reference resampling interval, while BMI-DBP effects were consistently larger and residual correlations smaller. | Adequate joint-distribution recovery, calibrated author-ensemble uncertainty, cross-provider agreement or revision benefit. The release family was already exposed and the intervals omit complex-survey design. |'
replace('| HRS/Q3 and Q2: analyses whose model information or summaries were supplied', new_use + '\n| HRS/Q3 and Q2: analyses whose model information or summaries were supplied', 'Keep PNS successes and mismatches in the same use table')

paragraph('The [public research repository]', 'The [public research repository](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026) retains versioned protocols, executable programs and aggregate audits. The iron [protocol seal](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/commit/bedd845768c1c938768f58fce685f53cbf97f3df) and [delivery seal](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/commit/c88192edeb0bc63b60d0bfe6e3a7282ced9d2975) precede its target evaluation. This revision integrates the previously completed PNS task and a retrospective attribution audit; it conducts no new clinical experiment or target refit. The [attribution table](../work/parameter_attribution_2026-11-10/ATTRIBUTION_MASTER.md) binds all 90 requested-analysis records and six dispersion records to their frozen aggregates and model specifications. Supplement S18 documents PNS, S19 the attribution scope, and S13-S15 retain the distinct artificial, historical and implementation-development studies. Independent numerical checking verifies the integration, not clinical validity or prospective calibration.', 'Document actual new retrospective material and preserved study boundaries')

refs = '''39. Intersalt Cooperative Research Group. Intersalt: an international study of electrolyte excretion and blood pressure. Results for 24 hour urinary sodium and potassium excretion. *BMJ*. 1988;297:319-328. [Article](https://doi.org/10.1136/bmj.297.6644.319).
40. Zhang Z, Gu X, Tang Z, et al. Associations of blood pressure components with risks of cardiovascular events and all-cause death in a Chinese population: A Prospective Study. *Journal of Clinical Hypertension*. 2022;24:825-837. [Article](https://doi.org/10.1111/jch.14529); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC9278591/).
41. Pesquisa Nacional de Saúde, Fiocruz. PNS 2013 laboratory-substudy release and field documentation. [Official data access](https://www.pns.icict.fiocruz.br/bases-de-dados/); [laboratory documentation](https://www.pns.icict.fiocruz.br/exames-laboratoriais/). The retained release, field dictionary and acquisition provenance are bound in the study archive; no claim of national inference is made from the selected laboratory-weighted sample.
'''
replace('## Supplementary results', refs + '\n## Supplementary results', 'Add the two verified original blood-pressure sources and official PNS provenance')

text += '''

### S18. Blood-pressure protocol, complete author results and source feedback

The PNS request was fixed before its reference effects were inspected. Authors received a target description, identical reviewed external evidence, the three analyses and optional bounded retrieval. They received no target records, means, slopes or prior generators. Each could retain its reviewed initial construction or make one source-feedback revision, with three prespecified seeds (271, 409, 557) at 3,000 rows. All five retained the initial law, undertook no additional retrieval and performed no exact source-population replay. There were fifteen final tables and no post-reveal regeneration. The author programs use different nonlinear surfaces, dependence and feasibility assumptions; an author identifier denotes a new context under the shared service, not a separately identified model backend.

Eligibility used baseline ages 20-79, recorded sex codes 1/2, weight 30-200 kg, height 120-210 cm, SBP 60-290 mmHg, DBP 30-200 mmHg and positive finite laboratory weight, with complete required measurements. Reported pregnancy was excluded; unknown or inapplicable pregnancy was retained. BMI was weight divided by squared height in metres. No HbA1c, treatment or hypertension restriction, and no SBP-greater-than-DBP reference filter, was applied. Selection retained 8,352 of 8,952 released records. The BP fields represent baseline measurements; the laboratory-substudy weight defines the selected analytical reference, not proven national representativeness. The field inventory provides no supported survey strata or PSU identifiers. All analyses use the same rows and a design with intercept, age, female indicator and BMI. Weighted point estimates have an unweighted sensitivity analysis. The displayed intervals use 500 IID row resamples retaining row weights; they do not account for complex survey design, nonresponse, transport or evidence uncertainty.

**Table S11. All PNS author summaries and measured references.** Each author entry is its median over three draws. BMI effects are mmHg per 5 kg/m², adjusted for age and sex. Residual Pearson correlation adjusts both blood pressures for age, sex and BMI. The weighted reference is a sample estimate; its interval is conditional IID row-resampling stability, not an acceptance margin. Every draw appears in Figure 8 and the frozen results.

| Construction/reference | BMI-SBP | BMI-DBP | Residual correlation |
|---|---:|---:|---:|
| A01 | 3.391 | 2.997 | 0.508 |
| A02 | 3.815 | 3.350 | 0.644 |
| A03 | 3.980 | 2.933 | 0.506 |
| A04 | 3.880 | 3.053 | 0.557 |
| A05 | 3.709 | 3.058 | 0.526 |
| Weighted sample reference | 3.524 | 2.260 | 0.717 |
| Conditional reference interval | 2.961-4.119 | 1.931-2.585 | 0.700-0.734 |
| Unweighted reference sensitivity | 3.435 | 2.114 | 0.741 |

Source feedback produced 108 non-computable strict check evaluations, 75 computed assumption-labelled descriptive contrasts and 27 unavailable descriptive contrasts. These are repeated evaluations, not independent evidence items. The strict checks did not replace INTERSALT's pooled, more-adjusted coefficients with target age/sex-only regressions. Restricting generated target-context ages to 65-79 was a descriptive contrast with Beijing, not a replay of that source population. Authors documented discrepancies and retained their laws; unchanged retention neither demonstrates feedback gain nor certifies source fit or transport. Independent recomputation verified selection and 306 numerical comparisons across the reference and fifteen outputs, with maximum absolute difference 1.82e-12. Frozen bootstrap quantiles were not independently refitted on patient data in that audit. Residual-SD ratios across draws were 0.833-1.058 for SBP and 0.880-1.034 for DBP. Generated means were 117.90-124.81/74.65-77.05 mmHg, versus reference 125.83/78.87.

### S19. Attribution scope, operator distinctions and prospective limits

The retrospective audit covers thirty Agent constructions: twenty in the main CHNS/ENSANUT contrast, five PNS authors, three Q5 lipid authors and both iron authors. It includes ninety requested-analysis records and six lipid marginal-SD diagnostics. It does not cover every historical construction, statistical comparator, HRS reconstruction or prospective wave. Audit counts are not replication counts. Eighty main-study specification, generator, uptake and evidence files matched their original freeze hashes; the audit also checked the later case specifications and original aggregate anchors. No individual row table was read and no scientific generator or evaluator was rerun for this attribution.

For each requested analysis the record separates the original source statistic and operator, adopted parameters and native provenance, additional bridge assumptions, model-implied estimand where already derived, finite generated estimates and measured-reference estimate with its available uncertainty. REPORTED, DERIVED and ASSUMED are parameter-origin descriptors. A single endpoint can depend on all three, and a derivation may itself require an assumed joint distribution. Target transport and source applicability are recorded separately. Seven requested-analysis entries and six dispersion entries have existing numerical model implications in this scope; the other eighty-three remain uncomputed, not replaced by declared coefficients or generated values. Null theory fields do not mean the empirical analysis failed to run.

L03's existing lognormal-mixture algebra implies TC and HDL BMI slopes of 10.872168 and -2.105832 mg/dL per 5 kg/m², and residual Pearson correlation 0.132232. Its generated means are 10.015112, -1.986781 and 0.141343, with seed ranges 8.617345-11.698752, -2.122835 to -1.913541, and 0.121087-0.155368. These quantities are neither literal source coefficients nor means across different authors. Published pooled rank correlations constrain a different operator and enter through disclosed copula, conditioning and population assumptions. Agreement between a fixed law and its finite draws is an implementation property, not independent clinical evidence.

The PNS descriptive author-spread ratios use each author's median across its three seeds, the arithmetic mean of those five medians, and their sample SD with denominator four. Signed mean-reference differences divided by this SD are +1.02238, +5.11135 and -2.94896 for SBP, DBP and residual correlation. Using the median of the five medians instead gives +1.28799, +4.95360 and -3.33221. These describe the five constructed laws; they are not calibrated z statistics and do not identify a universal Agent prior. No historical missing backend identity is imputed.

An analysis-support card is proposed as future work, not validated in this paper. Such a card would expose evidence, operator mismatch, completion assumptions and sensitivity of a requested analysis. The current categories and judgments were assessed with outcomes known, even when the underlying author declarations preceded evaluation. All predicted-error and validated-reliability fields in the retrospective table remain null. A separate frozen assessment is required to test prediction of fragility or error. A planned cross-provider pilot is likewise not reported as an experiment here.
'''
target = P / 'manuscript/DRAFT_v0_28.md'
target.write_text(text, encoding='utf-8')
assert sha(source) == 'b2f013950d026b360de1e6001925913f2e2f96363b2b1bf5b30ac5106b87acdd'
facts = {'input':str(source),'input_sha256':sha(source),'output':str(target),'output_sha256':sha(target),
         'changes':changes,'new_clinical_experiments':0,'new_generator_executions':0,
         'preserved_original_figure_paths':re.findall(r'^!\[[^\]]*\]\(([^)]+)\)',old,re.M),
         'attribution_master_sha256':sha(P/'work/parameter_attribution_2026-11-10/ATTRIBUTION_MASTER.json')}
(HERE/'REVISION_FACTS.json').write_text(json.dumps(facts,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'draft':str(target),'changes':len(changes),'sha256':sha(target)}))
