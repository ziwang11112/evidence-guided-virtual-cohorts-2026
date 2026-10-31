"""B1 source-only review; no observed/generated/reference row access."""
from pathlib import Path
import hashlib,json,math,sys

R=Path(__file__).resolve().parent.parent
P=R.parent.parent
sys.path.insert(0,str(P))
from cohort_harness.contracts import validate_evidence,validate_spec
from cohort_harness.lifecycle import _registry

b=R/'visible/b1/bundle'
c=b/'candidates/initial'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e,s=read(c/'evidence.json'),read(c/'model_spec.json')
validate_spec(s,validate_evidence(e,read(b/'task.json')))
_registry(b)

# Manually transcribed from visually/textually inspected original tables.
groups=['wm','wf','bm','bf']
expected={}
def summaries(prefix,values,sd_items=True):
    for group,rows in zip(groups,values):
        for variable,(mean,sd) in zip(['age','bmi','urate'],rows):
            expected[f'{prefix}_{group}_{variable}_mean']=(mean,sd)
            if sd_items:expected[f'{prefix}_{group}_{variable}_sd']=(sd,None)
summaries('yun',[
    [(36.9,11),(28.6,6),(6.1,1.3)],[(37.1,10.9),(28,7.4),(4.5,1.2)],
    [(34.3,11.5),(28.2,7.3),(6.2,1.5)],[(35.1,11.8),(31.4,8.7),(4.6,1.7)]])
summaries('sun',[
    [(33.2,8.8),(27.6,5.6),(6.1,1.3)],[(32.7,8.9),(26.4,6.8),(4.2,1.1)],
    [(31.3,9.1),(27.2,6.7),(6,1.5)],[(30.4,8.5),(29.1,7.9),(4.2,1.2)]])
for group,value in zip(groups,[1.38,2.59,1.29,2.14]):
    expected[f'sun_{group}_reverse_bmi_slope']=(value,None)
for group,value in zip(['all','white','black','male','female','dbp','hypertension'],[.322,.337,.302,.332,.407,.323,.378]):
    expected[f'yun_{group}_std_bmi_to_urate']=(value,None)
for time,values in [('baseline',[
    [(34.8,4.7),(28,4.9),(6,1.2)],[(34.4,4.9),(27,6.6),(4.2,1.1)],
    [(34.4,4.3),(28.1,6.9),(6.1,1.3)],[(34,5.1),(31.1,8.1),(4.2,1.3)]]),('followup',[
    [(45.6,6.2),(30,5.5),(6.2,1.3)],[(45.1,6.5),(29.4,7.2),(4.6,1.3)],
    [(44.5,5.8),(29.6,8.3),(6.4,1.6)],[(45.3,6.6),(34.4,8.8),(4.9,1.5)]])]:
    for group,rows in zip(groups,values):
        for variable,pair in zip(['age','bmi','urate'],rows):
            expected[f'yun_long_{time}_{group}_{variable}']=pair
for stage,rows,correlation in [('pre',[(35,10),(23,4),(225,76)],-.013),
                              ('post',[(55,4),(25,3),(239,76)],.345)]:
    for variable,(mean,sd) in zip(['age','bmi','urate'],rows):
        expected[f'bon_{stage}_{variable}_mean']=(mean,sd)
        expected[f'bon_{stage}_{variable}_sd']=(sd,None)
    expected[f'bon_{stage}_bmi_urate_r']=(correlation,None)
items={x['id']:x for x in e['items']}
numeric={k:v for k,v in items.items() if v['estimate'] is not None}
assert set(numeric)==set(expected)
for key,(value,sd) in expected.items():
    item=numeric[key]
    assert item['estimate']==value,key
    if sd is not None:assert item['uncertainty']=={'kind':'sd','value':sd},key
    else:assert item['uncertainty']=={'kind':'not_reported'},key
for group in groups:
    it=items[f'sun_{group}_reverse_bmi_slope']
    assert it['adjustment']==['age'] and it['unit']=='kg/m^2 per mg/dL'
for stage in ['pre','post']:
    assert items[f'bon_{stage}_urate_mean']['unit']=='micromol/L'
    assert items[f'bon_{stage}_bmi_urate_r']['kind']=='correlation'

construction=read(c/'audit/construction.json')
assert construction==s['parameters']['construction']
assert construction['interpretation']=='working_guides'
def expr(node,row):
    if 'const' in node:return node['const']
    if 'column' in node:return row[node['column']]
    if 'lookup' in node:
        look=node['lookup'];return next(x['value'] for x in look['values'] if x['key']==row[look['column']])
    a,z=[expr(x,row) for x in node['args']]
    return {'add':lambda:a+z,'sub':lambda:a-z,'mul':lambda:a*z,'min':lambda:min(a,z),'max':lambda:max(a,z)}[node['op']]()
formula_checks=0
for g,(race,sex) in enumerate([('White','male'),('White','female'),('Black','male'),('Black','female')]):
    for age in [20,40,56]:
        for bmi in [18,40,50]:
            row={'race':race,'sex':sex,'age':age,'bmi':bmi}
            mu=[6.1,4.5,6.2,4.6][g]+.07*(min(bmi,40)-[28.6,28,28.2,31.4][g])+.035*max(bmi-40,0)+(.01 if sex=='male' else .025)*(age-[36.9,37.1,34.3,35.1][g])
            assert math.isclose(expr(construction['conditional_mean'],row),mu,abs_tol=1e-12)
            assert math.isclose(expr(construction['conditional_sd'],row),[1.2,1.05,1.4,1.55][g],abs_tol=1e-12)
            formula_checks+=2
plan=s['parameters']['source_check_plan']
assert len(plan)==33 and len({x['id'] for x in plan})==33
assert sum(x['status']=='approximate' for x in plan)==20
assert sum(x['status']=='not_computable' for x in plan)==13
for check in plan:
    item=items[check['evidence_id']]
    if check['status']=='not_computable':assert check['operator'] is None;continue
    op=check['operator']
    assert op['unit']==item['unit'] and op['missing_policy']=='error'
    if op['kind']=='ols_coefficient':
        assert op['outcome']=='bmi' and op['predictors']==['urate','age'] and op['term']=='urate' and op['include_intercept']
    else:assert op['kind']==item['kind'] and op['column']=='urate'
    prefix=check['evidence_id'].split('_')[1]
    idx=groups.index(prefix)
    assert op['selection']==[{'column':'race','op':'eq','value':['White','White','Black','Black'][idx]},
                             {'column':'sex','op':'eq','value':['male','female','male','female'][idx]}]
result={'status':'pass','scope':'source-only numerical extraction and invented-predictor formula verification',
        'evidence_item_count':len(items),'numeric_items_checked':len(expected),'source_plan_checks':len(plan),
        'invented_formula_comparisons':formula_checks,'target_data_read':False,'observed_rows_read':False,
        'generated_rows_read':False,'bindings':{name:sha(c/name) for name in ['evidence.json','model_spec.json','audit/construction.json','audit/revision_plan.json']}}
out=Path(__file__).with_suffix('.json')
with out.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
