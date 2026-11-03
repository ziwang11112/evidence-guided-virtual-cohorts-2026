"""Assemble final reporting from audited aggregates; no scientific computation or rows."""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib

U = Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
    assert not p.exists(), p
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
now = datetime.now(timezone.utc).isoformat()
r = read(U/'final_evaluation/RESULTS.json')
a = read(U/'independent_audit/RESULTS.json')
i = read(U/'publication/RESULT_INTERPRETATION.json')
assert a['status']=='matched' and a['result_sha256']==sha(U/'final_evaluation/RESULTS.json')
assert r['successful_executions']==r['complete_analysis_slots']==72
assert i['provisional'] is False
labels = {
 ('CHNS2009','E1'): 'CHNS: BMI adjusted for age/sex',
 ('CHNS2009','E2'): 'CHNS: glucose adjusted for age/sex',
 ('CHNS2009','E3'): 'CHNS: age adjusted for sex/BMI/glucose',
 ('ENSANUT2018','Q1_age10'): 'ENSANUT: age adjusted for sex/BMI/glucose',
 ('ENSANUT2018','Q2_bmi5'): 'ENSANUT: BMI adjusted for age/sex',
 ('ENSANUT2018','Q3_bmi5'): 'ENSANUT: BMI adjusted for age/sex/glucose',
}
table = ['| Analysis | Unit | Sample reference | E0 discrepancy | E1 discrepancy | E1 minus E0 |',
         '|---|---|---:|---:|---:|---:|']
for c in r['agent_information_contrasts']:
    case,ep = c['case_id'],c['endpoint']
    vals=[r['references'][case][ep]['value'],c['arms']['E0']['mean_constructor_mean_absolute_discrepancy'],c['arms']['E1']['mean_constructor_mean_absolute_discrepancy'],c['E1_minus_E0_mean_absolute_discrepancy']]
    table.append('| '+labels[(case,ep)]+' | '+c['unit']+' | '+' | '.join(f'{v:.6f}' for v in vals)+' |')
report = '''# Completed main study: evidence-guided virtual biomedical data

**Decision: close this frozen experiment and proceed to manuscript writing with analysis-specific claims. No additional construction, reference tuning or case acquisition is part of this unit.**

## What was done

The experiment generated complete age/sex/BMI/glucose/HbA1c cohorts without individual inputs. Two existing development cases (CHNS 2009 and ENSANUT 2018) each had E0 marginal/basic evidence and E1 additional qualified relational evidence. Five fresh scientific Agent contexts per case/condition selected probability laws and parameters. One fixed statistical specification per case/condition provided a descriptive comparator. The research questions were visible; target values were withheld from the authors. Both real reference samples had already been exposed to the research team, so this is not untouched confirmation.

All 24 constructions closed before common evaluation. The campaign completed 72 distinct final tables of 3,000 synthetic rows each (60 Agent and 12 statistical), plus seven exploratory tables: 79 successful physical executions and no failed generator executions. Generated rows and seeds do not increase the number of independent clinical samples. The two selected real references contain 6,631 CHNS and 6,931 ENSANUT participants under their different original selection/weighting definitions; these samples are not pooled.

Each table was evaluated on three prespecified regressions plus 27 CHNS or 28 ENSANUT diagnostics. Independent arithmetic agreed for all 2,196 statistics, with 22,713 total checks and a maximum numerical difference of 4.26e-14. All scheduled analyses were available. The audit checked existing generated outputs and frozen aggregate reference mappings; it did not repeat the patient-level reference analyses or certify biological validity.

## All six prespecified scientific analyses

The discrepancy below is the arm mean of each constructor's mean absolute difference from the sample-reference coefficient across three final seeds. These coefficients use different units and are not combined into an accuracy score. HbA1c `%` in the stored unit means percentage-point change per listed predictor unit.

__TABLE__

Additional relational evidence was associated with smaller discrepancies in five of six prespecified analyses. CHNS BMI worsened. This is a descriptive result, not a success rate, significance test or evidence that every generated relationship is valid.

Direction agreement and magnitude agreement differ. All ENSANUT E1 focal coefficients were positive, but the five age means were 0.09777–0.10245 per decade versus 0.07513 in the reference. BMI means were 0.05646–0.06252 before glucose adjustment and 0.02500–0.04209 after adjustment, versus 0.08364 and 0.05664. CHNS E1 BMI means were 0.01240–0.04576 versus 0.05495; E1 A03 retained a negative conditional-age mean despite the positive reference. No author was selected after seeing these comparisons.

All four statistical constructions remain in the full report and figure. Under E1, statistical CHNS glucose discrepancy was 0.01202 versus the Agent arm's 0.02408; statistical ENSANUT conditional-BMI discrepancy was 0.00794 versus 0.02565. The statistical specification was closer on those two analyses, while other comparisons favored the Agent arm. One fixed specification versus five Agent-authored models does not establish general superiority of either approach. Information availability was equal within an arm, but numerical-use decisions differed.

## What the implementation demonstrated

All ten E1 Agent constructions used at least one quantitative relation as a numerical model constraint. Their reviewed records distinguish constraints, analytic checks and contextual evidence. That fixes the earlier citation-only implementation problem; it does not imply all reported relations were matched or transported. Source-population replay was unavailable in this allocation, so generated target statistics were never relabeled as original-source replay.

Seven Agent authors used one exploratory feedback cycle and retained their model. Thirteen finalized their initial model without exploratory feedback; the four statistical constructions also finalized without revision. There were zero feedback-driven scientific revisions. Consequently this study provides no evidence of revision gains, even though the review/retention interface operated.

The observed results do not isolate why a source-supported relationship transports or fails. Differences in population, measurement, selection and unreported joint structure are plausible explanations, not established causal mechanisms. The CHNS conditional-age and ENSANUT conditional-BMI requests illustrate analysis beyond a directly supplied conditional target coefficient, but their validity still depends on model completion and transport assumptions.

## Figure and interpretation limits

![All constructors and all final seeds](publication/figures/main_scientific_uses.svg)

Every panel shows all five E0 and E1 Agent constructions and both statistical references. Dots are individual final seeds; mean markers and vertical ranges describe the three seeds, not confidence intervals. Diamonds mark statistical constructions. The line is the previously exposed sample estimate. Shading is a CHNS community-cluster CR1-t 95% interval or an ENSANUT empirical cluster-resampling stability band; neither is an equivalence margin or an interval for every marginal mean. ENSANUT uses its equal eight-cell analytical standard, not national survey weights.

The figures show genuine analysis-specific discrepancies; reference uncertainty is retained without treating it as permission to ignore mismatch. Seeds measure conditional simulation variation, not source-estimation, structural or transport uncertainty. No post-hoc acceptance threshold or pooled performance test was introduced. The public records contain all diagnostics, not only the six displayed endpoints.

## Reproducibility, cost and next work

The release, generators, evidence-use records, decisions, all final analyses and independent audit remain retained. Before common evaluation the audit implementation was repaired for compensated weighted quantile boundaries and CSV floating-point parsing; original blocked versions and their reviews are preserved. The repaired audit was separately committed/reviewed before evaluation and did not change any generator or reference.

The 79 execution receipts sum to 53.565 seconds of isolated generator runtime. This excludes source preparation, Agent authoring, review, orchestration and user time. Token costs, exact model-snapshot identifiers and end-to-end research costs were unavailable; no recruitment-cost savings are inferred.

Proceed with manuscript v0.4 and a contribution-to-evidence audit. The contribution is an executable study-qualified evidence-to-data procedure, with numerical-use records and empirical analysis-specific benefits and limits. Complete bibliographic predecessors, source/data declarations, observable runtime details and submission formatting. Current evidence does not establish universal data quality, clinical interchangeability, causal validity, individual-measurement recovery, general statistical superiority or guaranteed publication. No further fitting to these revealed references is authorized by this close-out.

See [full interpretation and constructor ledger](publication/RESULT_INTERPRETATION.md), [primary aggregate results](final_evaluation/RESULTS.json), [independent audit](independent_audit/RESULTS.json), and [claim lock](CLAIM_LOCK.json).
'''.replace('__TABLE__','\n'.join(table))
assert not (U/'RESULTS.md').exists()
(U/'RESULTS.md').write_text(report,encoding='utf-8')
lock={
 'schema_version':'main_study_claim_lock_v1','created_utc':now,
 'decision':'close_frozen_main_study_and_write_analysis_specific_manuscript',
 'bindings':{name:sha(U/name) for name in ['RELEASE.json','final_evaluation/RESULTS.json','independent_audit/RESULTS.json','publication/RESULT_INTERPRETATION.json','publication/UPTAKE_INVENTORY.json','RESULTS.md']},
 'completed':{'constructions':24,'agent_constructions':20,'statistical_constructions':4,'final_tables':72,'unique_final_tables':72,'rows_per_final_table':3000,'exploratory_tables':7,'total_attempts':79,'failed_generator_attempts':0,'numeric_statistics_audited':2196},
 'supported_claims':['Whole-cohort evidence-guided construction without individual input executed under the fixed procedure.','All ten E1 Agent models numerically used at least one qualified relation.','E1 had smaller constructor-first mean absolute discrepancy for five of six prespecified analyses; CHNS BMI worsened.','Scientific analysis performance depends on endpoint, author and information condition.','Statistical comparator orderings are mixed and descriptive.'],
 'unsupported_claims':['All relations or distributions recovered','Known population truth reconstructed','Clinical or individual-measurement substitution','General superiority over statistical synthesis or other Agents','Feedback-driven revision benefit','Untouched clinical confirmation','Causal explanation of observed discrepancies','Calibrated structural or transport uncertainty','Measured recruitment-cost savings'],
 'retain_counterexamples':['CHNS E1 BMI discrepancy increased.','CHNS E1 A03 conditional-age mean was negative.','ENSANUT E1 age was high and BMI effects low relative to the sample reference.','Statistical CHNS glucose and ENSANUT conditional BMI had smaller discrepancies than corresponding Agent constructions.'],
 'reference_status':'Previously exposed development samples; uncertain case-specific sample estimates, no equivalence threshold.',
 'revision_decisions':{'agent_retain':7,'agent_initial_final':13,'statistical_initial_final':4,'revised':0},
 'no_new_generation':True,'no_target_retuning':True,'no_new_acquisition':True,
 'next':'Manuscript and public reviewed artifact synchronization; finish citations/declarations before submission.'
}
write(U/'CLAIM_LOCK.json',lock)
write(U/'publication/FIGURE_VISUAL_QA.json',{'created_utc':now,'figure_sha256':sha(U/'publication/figures/main_scientific_uses.png'),'inspected_by':'root_visual_inspection','status':'readable_no_clipping_or_overlap_observed','scope':'All six panels, all constructor labels, legend and plotted reference bands inspected. Caption explicitly distinguishes seed ranges from uncertainty and shading from acceptance margins.'})
state=read(U/'STATE.json')
write(U/'publication/STATE_BEFORE_CLOSEOUT.json',state)
state.update({'phase':'main_study_evaluated_independently_matched_writing','execution_enabled':False,'actual_constructions':24,'actual_tables':79,'actual_table_attempts':79,'actual_final_tables':72,'closed_constructions':24,'target_reference_evaluation_performed':True,'independent_audit_version':'v3','independent_audit_status':'matched','numeric_statistics_audited':2196,'manuscript':'manuscript/DRAFT_v0_4.md','next':'Complete manuscript review and publish reviewed aggregate/code artifacts; no additional generation or tuning.','updated_utc':now,'claim_lock':'CLAIM_LOCK.json','results':'RESULTS.md'})
assert state['scheduled_runs_verified']==0
(U/'STATE.json').write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
old=read(U/'CONTINUATION.json');write(U/'publication/CONTINUATION_BEFORE_CLOSEOUT.json',old)
cont={'created_utc':now,'active_release':old['active_release'],'pending':[],'scientific_generation_complete':True,'closed_constructions':24,'final_tables':72,'target_reference_evaluation_performed':True,'independent_audit_status':'matched','author_decisions':lock['revision_decisions'],'last_public_commit':old['last_public_commit'],'no_new_schedule':True,'no_new_acquisition':True,'do_not_rerun_generators_evaluators_or_passing_tests':True,'next':['Review DRAFT_v0_4.md, RESULTS.md and CLAIM_LOCK.json against matched aggregate results.','Prepare allowlisted metadata/code/aggregate/figure export and sync via existing GitHub connector with a branch lease.','Record publication receipt and final user report; later work is manuscript completion, not this campaign regeneration.']}
(U/'CONTINUATION.json').write_text(json.dumps(cont,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'results_sha256':sha(U/'RESULTS.md'),'claim_lock_sha256':sha(U/'CLAIM_LOCK.json'),'phase':state['phase']}))
