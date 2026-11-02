import sys,json,hashlib,copy
from pathlib import Path
import numpy as np
import pandas as pd
base=Path('work/scaleup_2026-11-01/case_k01')
sys.path[:0]=[str(base/'implementation'),str(base/'analysis')]
import statistical_reference as ref
from test_statistical_reference import invented_records
from generated_validity import CONTEXTS,validate_generated_context
from source_descriptives import compute_source_descriptives
from k01_analysis import analyze_frame,IDS
assert hashlib.sha256((base/'implementation/statistical_reference.py').read_bytes()).hexdigest()=='c9c903b6a12b2c669eb25f7c2e3f69318368a17e64b415569e91d4636c80b9f7'
plan=json.loads((base/'request/descriptive_diagnostic_plan.json').read_text(encoding='utf-8'))
planned={r['evidence_id']:r for r in plan['items']}
base_task=json.loads((base/'request/task_template.json').read_text(encoding='utf-8'))
fixture=invented_records()
model=ref.fit_reference(fixture)
assert model['provenance']['sampled_rows']==0 and model['provenance']['optimizer_calls']==0
n,seed=24,20261102
frames={};guard_receipts={};diagnostic_errors=[];checked_ids=[]
for context in (*ref.SOURCE_CONTEXTS,ref.TARGET_CONTEXT):
    f=ref.sample(model['parameters'],context,n,seed)
    frames[context]=f
    task=copy.deepcopy(base_task);task['task_id']='INVENTED-K01-independent-composed';task['n_rows']=n;task['population']=CONTEXTS[context]['population']
    guard_receipts[context]=validate_generated_context(f,task,context_id=context)
    if context==ref.TARGET_CONTEXT: continue
    result=compute_source_descriptives(f,task,context_id=context)
    assert not result['semantic_feedback_v1_invoked'] and not result['execution_authenticated']
    for got in result['checks']:
        spec=planned[got['id']];op=spec['operator'];actual=got['diagnostic']
        assert spec['context_id']==context and actual['unit']==spec['comparison_unit']
        assert actual['n_input']==actual['n_selected']==actual['n_used']==n and actual['n_missing_dropped']==0
        if op['kind']=='proportion':
            predicates=op['boolean_event']['all']
            assert predicates==got['derived_event']['predicates']
            hit=0
            for _,row in f.iterrows():
                truth=[]
                for p in predicates:
                    x,v=row[p['column']],p['value']
                    truth.append({'eq':lambda:x==v,'ge':lambda:x>=v,'le':lambda:x<=v,'lt':lambda:x<v}[p['op']]())
                hit+=all(truth)
            expected=hit/n
        else:
            vals=f[op['column']].to_numpy()
            mean=sum(float(x) for x in vals)/n
            expected=mean if op['kind']=='mean' else (sum((float(x)-mean)**2 for x in vals)/(n-1))**0.5
            assert got['operator']['kind']==('mean' if op['kind']=='mean' else 'sd')
        diagnostic_errors.append(abs(actual['value']-expected));checked_ids.append(got['id'])
assert set(checked_ids)==set(planned) and len(checked_ids)==18
f=frames[ref.TARGET_CONTEXT];generated=analyze_frame(f,role='generated');toy_reference=analyze_frame(f,role='reference')
assert generated['status']==toy_reference['status']=='complete'
assert generated['metric_denominators']=={} and all(v['interval']['status']=='unavailable' for v in generated['estimands'].values())
y=f.glucose.to_numpy();s=(f.sex=='F').to_numpy(dtype=float)
x=np.column_stack([np.ones(n),f.age.to_numpy(),s,f.bmi.to_numpy()]);xi=np.column_stack([x,s*f.bmi.to_numpy()])
point_errors=[];se_errors=[];estimates=[]
for key,design,term,scale in [(IDS[0],x,3,5),(IDS[1],x,1,10),(IDS[2],xi,4,5)]:
    q,r=np.linalg.qr(design,mode='reduced');coef=np.linalg.solve(r,q.T@y)
    residual=y-design@coef;lever=np.sum(q*q,axis=1);pinv=np.linalg.solve(r,q.T)
    oracle=float(coef[term]*scale);se=float(np.sqrt(np.sum((pinv[term]*residual/(1-lever))**2))*scale)
    endpoint=toy_reference['estimands'][key];assert endpoint['interval']['status']=='available'
    point_errors.append(abs(endpoint['estimate']-oracle));se_errors.append(abs(endpoint['interval']['standard_error']-se));estimates.append(endpoint['estimate'])
assert max(point_errors+se_errors)<1e-10 and max(diagnostic_errors)<1e-10
assert abs(toy_reference['metric_denominators']['glucose']['sample_sd']-np.std(y,ddof=1))<1e-12
print(json.dumps({'scope':'invented_fixture_only_not_clinical','rows_per_context':n,'contexts':list(frames),'seed':seed,'sample_calls':3,'total_invented_rows':72,'source_checks_verified':len(checked_ids),'max_source_arithmetic_error':max(diagnostic_errors),'invented_target_contrasts':dict(zip(IDS,estimates)),'max_raw_QR_point_error':max(point_errors),'max_raw_QR_HC3_SE_error':max(se_errors),'all_guards_valid':all(v['status']=='valid' for v in guard_receipts.values()),'retained_csv_or_candidate_or_isolated_execution':False},ensure_ascii=False))
