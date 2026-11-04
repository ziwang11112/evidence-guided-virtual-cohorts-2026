"""Prepare new metadata-only tasks. Never reads target values or scientific parameters."""
from pathlib import Path
import hashlib, json, sys
R=Path(__file__).resolve().parent
P=R.parents[1]
W=P.parents[1]
sys.path.insert(0,str(P))
from cohort_harness.contracts import validate_task
from cohort_harness.literature import run_literature
def write_new(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
base=P/'work/main_study_freeze_2026-11-03'
analyses={
 'CHNS2009':[
  {'id':'E1','formula':'hba1c ~ 1 + bmi + age + female','term':'bmi','unit':'percentage points per kg/m^2'},
  {'id':'E2','formula':'hba1c ~ 1 + glucose + age + female','term':'glucose','unit':'percentage points per mmol/L'},
  {'id':'E3','formula':'hba1c ~ 1 + age + female + bmi + glucose','term':'age','unit':'percentage points per year'}],
 'ENSANUT2018':[
  {'id':'Q1_age10','formula':'hba1c ~ 1 + age10 + female + bmi5 + glucose10','term':'age10','unit':'percentage points per 10 years'},
  {'id':'Q2_bmi5','formula':'hba1c ~ 1 + age10 + female + bmi5','term':'bmi5','unit':'percentage points per 5 kg/m^2'},
  {'id':'Q3_bmi5','formula':'hba1c ~ 1 + age10 + female + bmi5 + glucose10','term':'bmi5','unit':'percentage points per 5 kg/m^2'}]}
excluded=['CHNS','China Health and Nutrition Survey','ENSANUT','Encuesta Nacional de Salud y Nutricion']
authors={}
for case,ids in [('CHNS2009',['C01','C02']),('ENSANUT2018',['E01','E02'])]:
    original=base/'cases'/case/'task.json'
    profile=R/'cases'/case/'profile.json'
    provider=base/'cases'/case/('generated_provider.py' if case=='CHNS2009' else 'generated_feedback.py')
    write_new(profile,{'case_id':case,'information_condition':'open_evidence','constructor_kind':'agent','analysis_ids':[a['id'] for a in analyses[case]],'source_numeric_mode':'qualified_semantic_v1','provider':str(provider),'provider_sha256':sha(provider)})
    for aid in ids:
        bundle=W/('evcRep'+aid)
        if bundle.exists():raise FileExistsError(bundle)
        bundle.mkdir()
        task=json.loads(original.read_text(encoding='utf-8'))
        task['task_id']='core-workflow-replication-2026-11-04-'+aid
        task['information_policy']={'mode':'published_evidence','excluded_cohorts':excluded,'allowed_tools':['literature.search','literature.fetch','admitted_source_read','contract_validation','controller_source_feedback','retained_analytic_calculation']}
        task['budget']={'source_queries':8,'source_downloads':4,'revisions':1}
        validate_task(task)
        write_new(bundle/'task.json',task)
        write_new(bundle/'registry.json',{'artifacts':[]})
        request={'mode':'whole_cohort','population':task['population'],'n_rows':3000,'individual_input':False,'intended_analyses':analyses[case],
          'estimator':'OLS with intercept' if case=='CHNS2009' else 'Equal-age-sex-cell WLS, 1/8 mass per cell, exactly 375 rows/cell; not national-survey estimation',
          'transformations':{} if case=='CHNS2009' else {'age10':'(age-50)/10','bmi5':'(bmi-25)/5','glucose10':'(glucose-100)/10'},
          'prespecified_secondary_diagnostics':'All provider-defined marginals, quantiles, available joint/conditional diagnostics, invalid or duplicate rows and uncomputable results; no new target clinical analysis.',
          'desired_signs_or_values':None}
        write_new(bundle/'request.json',request)
        write_new(bundle/'SEARCH_LEDGER.json',{'author':aid,'actions':[],'original_studies_seriously_read':[],'scope':'Only task-bound Europe PMC/PMC gateway; no supplied DOI seeds or target values','status':'not_started'})
        instructions=f'''# Independent scientific author {aid}

Use only this bundle, its registered sources and the procedural interface files in {P}/cohort_harness, docs/EXECUTION_ADAPTER.md, docs/SEMANTIC_FEEDBACK_V1.md, and the evidence-cohort-generation skill. Do not read any other experiment, manuscript, old candidate, target result, hidden individual record or other author's material. This is a procedural information boundary, not OS isolation.

Read task.json and request.json. You choose all scientific structure, distributions, parameters, transformations, evidence weights and unsupported assumptions. No required sign, effect size, probability family or named paper is supplied. All variables are generated; no participant input exists. Intended analysis questions are visible.

## First phase: actual evidence acquisition and proposal

Select your own queries. Use the sole task-bound gateway already initialized by the controller: Python -m cohort_harness.literature --bundle "{bundle}" search --query QUERY; fetch --pmcid ID [--version N]. Run from {P} using C:/Users/ziwan/AppData/Local/Programs/Python/Python312/python.exe. Queries and fetch metadata share an eight-query budget; four original-study downloads/serious reads maximum across the entire author task. Failed and rejected actions consume their actual gateway budgets. Do not reset sessions, use another search tool, retry indefinitely, or fetch beyond the budget. This evaluates bounded accessible-primary-literature retrieval, not arbitrary web access. Do not use CHNS- or ENSANUT-participant studies as generating evidence. A conservative gateway rejection may exclude an otherwise applicable paper; record it rather than bypass it.

Record all actions, source selections/rejections and limitations in SEARCH_LEDGER.json, alongside the authoritative gateway action/audit logs. Read the actual admitted original material, including its measurement, population, selection, adjustment, units, uncertainty and study-overlap details. Do not replace an adjusted coefficient with a correlation or a standard error with individual SD. Do not invent missing values or source confidence intervals.

Prepare SOURCE_REVIEW_REQUEST.md describing exactly what source quantities you would use, their locators and applicability, and PROPOSED_CONSTRUCTION.md describing the intended joint law, how it would support the requested analyses, what is numerically constrained and what is assumed. Identify finite-moment requirements. You may use, qualify or decline evidence. A lack of evidence is reportable; stop rather than inspect targets. Do not yet generate a candidate or any rows. Return to the controller for source/implementation review.

## Later phase after source review

The same author will write candidates/initial with evidence.json, model_spec.json, decision.md, checks.json, generator.py OR generated.csv, source_semantics_v1.json and whole_cohort_feedback.json. Read actual schema documentation. Registry approvals are created by the screened adapter/controller, never by the author. Scientific model settings belong in the specification with reported/derived/assumption provenance.

Source acquisition is closed at the first candidate freeze. One initial trial (8100), at most one scientific revision and its trial (8110), then one final model choice followed by three fixed deliveries (8101,8102,8103). Do not execute your generator locally; the controller uses the existing isolated execution adapter. Up to two mechanical/source review rounds before each freeze, no target-driven advice. Conditional source comparisons on the target population must be explicitly approximate with transfer assumptions; they are not source-population replay. Unsupported checks remain unavailable. Preserve earlier candidates and bind actual feedback before retain/revise. A no-op is valid. After the revision trial, no second scientific revision or new search is allowed. Final rows cannot be used to choose the final candidate. All four author slots close before evaluator reference comparisons.

This is one fresh scientific author slot, not multi-Agent scientific voting. Do not train models, call paid APIs, start HPC, download individual data or publish third-party materials. Log actual actions, failures and interventions; do not provide private reasoning traces.
'''
        (bundle/'AUTHOR_TASK.md').write_text(instructions,encoding='utf-8')
        init=run_literature(bundle,'init')
        if init.get('status')!='ok':raise RuntimeError(init)
        authors[aid]={'bundle':str(bundle),'case_id':case,'provider':str(provider),'profile':str(profile),'task_sha256':sha(bundle/'task.json'),'request_sha256':sha(bundle/'request.json')}
protocol={'kind':'core_workflow_replication_v1','date':'2026-11-04','purpose':'Developmental repeated application of one Agent evidence-acquisition/construction/review policy to two existing whole-cohort requests; not a causal retrieval contrast or fresh clinical validation.',
 'authors':authors,'trial_seeds':{'initial':8100,'revision':8110},'final_seeds':[8101,8102,8103],
 'limits':{'timeout_seconds':30,'memory_mb':1536,'output_bytes':20000000,'log_bytes':100000},'max_physical_executions':20,'max_feedback_revisions':1,'n_rows':3000,
 'acquisition':{'adapter':'cohort_harness.literature','scope':'Accessible primary literature via fixed Europe PMC/PMC gateway, self-selected queries, no DOI seeds','per_author_queries_including_fetch_metadata':8,'per_author_originals_and_downloads':4,'closed_at':'first_candidate_freeze','excluded_cohort_aliases':excluded,'failed_actions_count':True,'new_patient_data':False,'response_limit_bytes':16777216,'network_metering':'Retain gateway actual response/artifact bytes; browser traffic not used. No patient-data acquisition.'},
 'feedback':{'adapter':'semantic_feedback_v1','qualified_approximate_target_population_comparisons':True,'source_population_replay_claim':False,'unsupported_operators':'unavailable','reference_values_to_authors':False,'generated_only_provider_per_case':True},
 'reference':{'path':str(base/'final_evaluation/RESULTS.json'),'sha256':sha(base/'final_evaluation/RESULTS.json'),'read_after':'all four slots closed and scheduled final attempts resolved','exposed_development':True,'new_reference_fits':False},
 'analyses':analyses,'diagnostics':'Reuse each immutable main-study generated_statistics provider and all its declared diagnostic outputs. No pooled cross-unit quality score or post-hoc equivalence threshold.',
 'finalization':'Select initial or one directly revised frozen candidate only after permitted trial feedback and before all three final draws. Failed attempts remain charged; no replacement authors/seeds. Terminal failures are retained and can close without deliverable rows.',
 'review':'Independent source meaning, transformations, mathematical finite moments, generator/spec consistency, task validity and semantic-feedback checks. No required biological agreement or reference-derived parameters.',
 'interpretation':'Four scientific authors, two existing exposed reference families, at most12 final draw tables. Historical main study remains closed and separately named; no search/revision efficacy, universal superiority, independent clinical confirmation or total cost-saving claim.',
 'stop':'Close once all four slots and full scheduled analysis/accounting have independent review, regardless of outcomes. No automatic extension.',
 'controls':'No paid API, training, HPC, new patient download or alteration of prior frozen artifacts. Patient-like generated rows and third-party originals remain local.'}
write_new(R/'PROTOCOL.json',protocol)
write_new(R/'STATE.json',{'status':'source_acquisition_ready_generation_not_released','protocol_sha256':sha(R/'PROTOCOL.json'),'author_slots':list(authors),'actual_dispatches':{},'physical_generation_attempts':0,'new_patient_reads':0,'clinical_reference_read':False,'next':'Independent protocol review; bounded fresh-author acquisition; audited runner and source/model reviews before execution.'})
print(json.dumps({'prepared':list(authors),'protocol_sha256':sha(R/'PROTOCOL.json'),'generation_started':False},indent=2))

if __name__=='__main__':pass
