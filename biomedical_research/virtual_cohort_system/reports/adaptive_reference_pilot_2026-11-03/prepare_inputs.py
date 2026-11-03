"""Prepare explicitly exposed aggregate inputs; never reads patient records."""
from pathlib import Path
import copy, hashlib, json, shutil

P = Path(__file__).resolve().parents[2]
U = Path(__file__).resolve().parent
B = P.parents[1] / 'evcAR/b'
OLD = P / 'work/developmental_continuation_v1_2026-11-03/author_inputs'
F2 = P / 'work/chns_admission_2026-11-01/f2'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:
        json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False); f.write('\n')

def main():
    if (B/'task.json').exists(): raise RuntimeError('Prepared inputs already exist; no overwrite')
    (B/'input').mkdir(parents=True,exist_ok=True)
    (B/'candidates').mkdir(exist_ok=True)
    shutil.copytree(OLD/'sources',B/'sources')
    for path in (F2/'sources').glob('*.md'):
        if not (B/'sources'/path.name).exists(): shutil.copy2(path,B/'sources'/path.name)
    original_report=F2/'evaluation_results/REPORT.json'
    ref=read(original_report)['reference']
    write(B/'input/reference_summary.json',ref)
    shutil.copy2(B/'input/reference_summary.json',B/'sources/CHNS_DEVELOPMENT_REFERENCE.json')
    plan=read(F2/'analysis_plan.json')
    analyses=copy.deepcopy(plan['estimands'])
    for item in analyses:
        item['feedback']=True
        item['source_class']='explicitly_provided_development_reference'
    write(B/'input/analysis_definitions.json',{'analyses':analyses,'diagnostics':plan['diagnostics'],
        'interpretation':'Reference-assisted development; no independent target validation. All 30 statistics available to author.'})
    task=read(F2/'task.json')
    task['task_id']='chns-reference-assisted-adaptive-pilot-2026-11-03'
    task['population']=task['population'].replace('Age/sex composition is not supplied. ', '') + ' All existing aggregate reference distributions and three regression estimates are explicitly supplied as developmental inputs.'
    task['information_policy']={'mode':'published_evidence','excluded_cohorts':[],
        'allowed_tools':['admitted_source_read','literature.search','literature.fetch','contract_validation','isolated_numeric_trial','semantic_feedback_v1','development_reference_feedback','candidate_revision']}
    task['budget']={'source_queries':4,'source_downloads':2,'revisions':4}
    write(B/'task.json',task)
    evidence=read(OLD/'input/compiled_evidence.json')
    registry=read(OLD/'registry.json')
    artifact={'path':'sources/CHNS_DEVELOPMENT_REFERENCE.json','sha256':sha(B/'sources/CHNS_DEVELOPMENT_REFERENCE.json')}
    evidence['sources'].append({'id':'CHNS_DEV_REF','identifier':'local:CHNS_2009_previously_revealed_reference_summary',
        'population':task['population'],'measurement':'Age years, female 0/1, BMI kg/m^2, central serum glucose mmol/L, whole-blood HbA1c percent. Unweighted selected complete-case sample. Not a new published external study.',
        'cohort_ids':['CHNS'],'artifacts':[artifact]})
    registry['artifacts'].append({'source_id':'CHNS_DEV_REF',**artifact,'origin':'curator','screening':'approved'})
    units={c['name']:c['unit'] for c in task['columns']}
    checks=[]; bindings=[]; diagnostic_ids=[]
    def add(name,value,op,locator,uncertainty=None):
        kind=op['kind']; eid='REF_'+name
        variables=[op['outcome'],op['term']] if kind=='ols_coefficient' else ([op['x'],op['y']] if 'correlation' in kind else [op['column']])
        adjustment=[v for v in op.get('predictors',[]) if v!=op.get('term')]
        item={'id':eid,'source_id':'CHNS_DEV_REF','locator':locator,'variables':variables,'kind':kind,'estimate':value,'unit':op['unit'],
            'uncertainty':uncertainty or {'kind':'not_reported'},'adjustment':adjustment,'selection':'Previously fixed CHNS 2009 complete-case analytical sample ages 35-74, n='+str(ref['n']),
            'applicability':'Supplied reference fit only; not population truth or independent validation. Estimator uncertainty unavailable unless stated.'}
        if kind in ('median','quantile'): item['method']='linear'
        if kind=='quantile': item['q']=op['q']
        evidence['items'].append(item)
        op={**op,'selection':[],'missing_policy':'error'}
        checks.append({'id':name,'evidence_id':eid,'status':'computed','operator':op,'assumption_ids':[],
            'reason':'Same explicitly supplied developmental-reference analysis definition; agreement evaluates reference consistency only.'})
        operands=set(variables+adjustment)
        bindings.append({'check_id':name,'evidence_id':eid,'source_locator':locator,'definition_status':'specified','source_operator':op,
            'weights':'none','transform':'identity','source_variable_units':{v:units[v] for v in sorted(operands)},
            'source_n':{'status':'reported','value':ref['n'],'scope':'CHNS selected complete-case analysis'},
            'uncertainty_role':'estimate' if uncertainty else 'not_reported','reason':'Declared statistics exactly as calculated in retained reference report; no external source-population claim.'})
    for variable,values in ref['diagnostics']['marginal'].items():
        for stat,value in values.items():
            name=variable+'_'+stat; diagnostic_ids.append(name)
            kind={'q10':'quantile','q90':'quantile'}.get(stat,stat)
            op={'kind':kind,'column':variable,'unit':units[variable]}
            if stat in ('q10','median','q90'):op['method']='linear'
            if stat in ('q10','q90'):op['q']=.1 if stat=='q10' else .9
            add(name,value,op,'reference.diagnostics.marginal.'+variable+'.'+stat)
    for kind,value in ref['diagnostics']['joint'].items():
        name='glucose_hba1c_'+kind; diagnostic_ids.append(name)
        add(name,value,{'kind':'correlation' if kind=='pearson' else 'spearman_correlation','x':'glucose','y':'hba1c','unit':'1'},'reference.diagnostics.joint.'+kind)
    for item in analyses:
        rid=item['id']; value=ref['estimands'][rid]; ci=value['interval']
        add(rid,value['coefficient'],{'kind':'ols_coefficient','outcome':item['outcome'],'predictors':item['predictors'],'term':item['term'],'include_intercept':True,'unit':units[item['outcome']]+'/'+units[item['term']]},
            'reference.estimands.'+rid,{'kind':'ci','low':ci['lower'],'high':ci['upper'],'level':.95} if ci['status']=='available' else None)
    audit=U/'inputs/EXTERNAL_EVIDENCE_AUDIT.md'
    if audit.exists():
        destination=B/'sources/EXTERNAL_EVIDENCE_AUDIT.md'
        shutil.copy2(audit,destination)
        audit_artifact={'path':'sources/EXTERNAL_EVIDENCE_AUDIT.md','sha256':sha(destination)}
        evidence['sources'].append({'id':'S_AUDIT','identifier':'local:qualified_external_evidence_reconciliation_2026-11-03',
            'population':'Several distinct external populations described individually in the source audit; no pooled cohort.',
            'measurement':'Original source units and adjustment sets retained separately; audit is derivative authored context, not a new original study.',
            'cohort_ids':['Lifelines','SHDS II','MIND-China','NHANES'],'artifacts':[audit_artifact]})
        evidence['items'].append({'id':'E_SOURCE_RECONCILIATION','source_id':'S_AUDIT',
            'locator':'Numerical evidence and its meaning; individual study tables and primary source locators',
            'variables':['age','female','bmi','glucose','hba1c'],'kind':'contextual','estimate':None,'unit':'',
            'uncertainty':{'kind':'not_reported'},'adjustment':[],
            'selection':'See each source separately; includes excluded diabetes, weighted survey and older rural selections.',
            'applicability':'Readable evidence context, including previously omitted age projections; not a common numerical source operator or identified target law.'})
        registry['artifacts'].append({'source_id':'S_AUDIT',**audit_artifact,'origin':'curator','screening':'approved'})
    write(B/'registry.json',registry)
    write(B/'input/compiled_evidence.json',evidence)
    feedback={'schema_version':1,'population':task['population'],'measurement':{'mode':'identity','description':'Development-reference estimates in task units; no external population replay.'},'assumption_ids':[],'checks':checks}
    write(B/'input/whole_cohort_feedback_template.json',feedback)
    write(B/'input/semantic_bindings_template.json',{'bindings':bindings})
    profile={'schema_version':1,'kind':'reference_assisted_adaptive_development','bundle':str(B),
        'information_regime':'external_evidence_plus_all_existing_reference_statistics','raw_individual_inputs':False,'independent_validation':False,
        'required_analysis_ids':[x['id'] for x in analyses],'required_diagnostic_ids':diagnostic_ids,
        'reference_summary':str(B/'input/reference_summary.json'),'analysis_definitions':str(B/'input/analysis_definitions.json'),
        'budgets':{'fresh_constructors':1,'author_phases':2,'initial_trials':2,'revision_trials':2,'delivery_per_stage':3,'delivery_seeds':[3101,3102,3103],'max_total_tables':10,'rows_per_table':3000,'retrieval_queries':4,'retrieval_documents':2},
        'reference_provenance':{'report_path':str(original_report),'report_sha256':sha(original_report),'extract':'reference only; no old candidate outputs'},
        'interpretation':'Existing revealed CHNS reused explicitly for reference-assisted development. No exposed reference promoted to an independent test. No source uncertainty or unidentified dependence resolved by more synthetic rows.'}
    write(U/'profile.json',profile)
    write(U/'STATE.json',{'phase':'inputs_prepared','scientific_constructions':0,'new_patient_reads':0,'executions':0,'status':'awaiting_fresh_author_and_session','old_experiment_mutations':0})
    print(json.dumps({'bundle':str(B),'evidence_items':len(evidence['items']),'reference_checks':len(checks),'diagnostics':len(diagnostic_ids),'profile':str(U/'profile.json')},indent=2))

if __name__=='__main__':main()
