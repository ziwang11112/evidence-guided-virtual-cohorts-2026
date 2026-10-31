"""B3 source-only review; no observed/generated/reference row access."""
from pathlib import Path
import hashlib,json,math,sys,zipfile,xml.etree.ElementTree as ET,re

R=Path(__file__).resolve().parent.parent
P=R.parent.parent
sys.path.insert(0,str(P))
from cohort_harness.contracts import validate_evidence,validate_spec
from cohort_harness.lifecycle import _registry

b=R/'visible/b3/bundle';c=b/'candidates/initial'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e,s=read(c/'evidence.json'),read(c/'model_spec.json')
validate_spec(s,validate_evidence(e,read(b/'task.json')))
_registry(b)
for source in e['sources']:
    for artifact in source['artifacts']:assert sha(b/artifact['path'])==artifact['sha256']

# Transcribed from the independently inspected original main tables.
groups=['WM','WF','BM','BF'];expected={}
def summaries(prefix,values):
    for group,rows in zip(groups,values):
        for variable,(mean,sd) in zip(['age','bmi','urate'],rows):
            expected[f'{prefix}_{group}_{variable}_mean']=(mean,sd)
            expected[f'{prefix}_{group}_{variable}_sd']=(sd,None)
summaries('yun',[
    [(36.9,11),(28.6,6),(6.1,1.3)],[(37.1,10.9),(28,7.4),(4.5,1.2)],
    [(34.3,11.5),(28.2,7.3),(6.2,1.5)],[(35.1,11.8),(31.4,8.7),(4.6,1.7)]])
summaries('sun',[
    [(33.2,8.8),(27.6,5.6),(6.1,1.3)],[(32.7,8.9),(26.4,6.8),(4.2,1.1)],
    [(31.3,9.1),(27.2,6.7),(6,1.5)],[(30.4,8.5),(29.1,7.9),(4.2,1.2)]])
summaries('yun_I_follow',[
    [(25.4,4.2),(28.3,6.2),(6.2,1.2)],[(24.4,3.6),(27.9,8),(4.3,1.1)],
    [(24.1,4.3),(27.9,6.8),(5.8,1.3)],[(24.5,4),(31.2,8.7),(4.3,2.4)]])
summaries('yun_II_base',[
    [(34.8,4.7),(28,4.9),(6,1.2)],[(34.4,4.9),(27,6.6),(4.2,1.1)],
    [(34.4,4.3),(28.1,6.9),(6.1,1.3)],[(34,5.1),(31.1,8.1),(4.2,1.3)]])
summaries('yun_II_follow',[
    [(45.6,6.2),(30,5.5),(6.2,1.3)],[(45.1,6.5),(29.4,7.2),(4.6,1.3)],
    [(44.5,5.8),(29.6,8.3),(6.4,1.6)],[(45.3,6.6),(34.4,8.8),(4.9,1.5)]])
expected['yun_bmi_standardized']=(.322,None)
for group,value in zip(['White','Black','male','female'],[.337,.302,.332,.407]):
    expected[f'yun_s3_{group}']=(value,None)
for group,value,std in zip(groups,[1.38,2.59,1.29,2.14],[.33,.44,.28,.33]):
    expected[f'sun_{group}_reverse_slope']=(value,None)
    expected[f'sun_{group}_reverse_standardized']=(std,None)
for stage,rows,correlation in [('pre',[(35,10),(23,4),(225,76)],-.013),
                              ('post',[(55,4),(25,3),(239,76)],.345)]:
    for variable,(mean,sd) in zip(['age','bmi','urate'],rows):
        expected[f'bon_{stage}_{variable}_mean']=(mean,sd)
        expected[f'bon_{stage}_{variable}_sd']=(sd,None)
    expected[f'bon_{stage}_urate_mean_mgdl']=(rows[2][0]/59.48,76/59.48)
    expected[f'bon_{stage}_urate_sd_mgdl']=(76/59.48,None)
    expected[f'bon_{stage}_bmi_pearson']=(correlation,None)
for sex,mean,sd in [('male',5.9,1.2),('female',4.3,.9)]:
    expected[f'ohyama_{sex}_urate_mean']=(mean,sd)
    expected[f'ohyama_{sex}_urate_sd']=(sd,None)
# Directly parse the original admitted DOCX, rather than the builder extract.
w={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(b/'sources/controller/PMC7803020_mmc2.docx') as z:
    doc=ET.fromstring(z.read('word/document.xml'))
sex=None;original_supplement_numeric_items=0
for tr in doc.findall('.//w:tbl/w:tr',w):
    vals=[''.join(tc.itertext()).strip() for tc in tr.findall('w:tc',w)]
    if vals[0].startswith('Men ('):sex='male'
    if vals[0].startswith('Women ('):sex='female'
    var=next((v for prefix,v in [('Age,','age'),('BMI,','bmi'),('Uric acid,','urate')] if vals[0].startswith(prefix)),None)
    if sex and var:
        for i,cell in enumerate(vals[1:5]):
            match=re.fullmatch(r'([\d.]+) \(([\d.]+)\)',cell)
            assert match,cell
            mean,sd=map(float,match.groups())
            expected[f'ohyama_{sex}_age{i}_{var}_mean']=(mean,sd)
            expected[f'ohyama_{sex}_age{i}_{var}_sd']=(sd,None)
            original_supplement_numeric_items+=2
items={x['id']:x for x in e['items']}
numeric={k:v for k,v in items.items() if v['estimate'] is not None}
assert set(numeric)==set(expected),(set(numeric)-set(expected),set(expected)-set(numeric))
for key,(value,sd) in expected.items():
    item=numeric[key]
    assert math.isclose(item['estimate'],value,abs_tol=1e-12),key
    if sd is not None:
        assert item['uncertainty']['kind']=='sd' and math.isclose(item['uncertainty']['value'],sd,abs_tol=1e-12),key
    else:assert item['uncertainty']=={'kind':'not_reported'},key
for group in groups:
    assert items[f'sun_{group}_reverse_slope']['adjustment']==['age']
for key,item in items.items():
    if key.startswith('ohyama_'):assert not item['adjustment']

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
    for age in [20,40,45,56]:
        for bmi in [18,40,50]:
            row={'race':race,'sex':sex,'age':age,'bmi':bmi}
            knot=40 if sex=='male' else 45
            low=0 if sex=='male' else -.003
            high=-.01 if sex=='male' else .03
            mu=[6.1,4.5,6.2,4.6][g]+.07*(min(bmi,40)-[28.6,28,28.2,31.4][g])+.03*max(bmi-40,0)
            mu+=low*(min(age,knot)-[36.9,37.1,34.3,35.1][g])+high*max(age-knot,0)
            assert math.isclose(expr(construction['conditional_mean'],row),mu,abs_tol=1e-12)
            assert math.isclose(expr(construction['conditional_sd'],row),[1.2,1.1,1.4,1.5][g],abs_tol=1e-12)
            formula_checks+=2
n=[1012,1209,509,672]
def pool(means,sds):
    avg=sum(a*v for a,v in zip(n,means))/sum(n)
    return math.sqrt(sum((a-1)*sd**2+a*(v-avg)**2 for a,v,sd in zip(n,means,sds))/(sum(n)-1))
sy=pool([6.1,4.5,6.2,4.6],[1.3,1.2,1.5,1.7]);sx=pool([28.6,28,28.2,31.4],[6,7.4,7.3,8.7])
deriv=s['parameters']['scientific_derivation']
for name,value in [('source_pooled_urate_sd',sy),('source_pooled_bmi_sd',sx),('approx_raw_bmi_coefficient',.322*sy/sx)]:
    assert math.isclose(deriv[name],value,abs_tol=1e-12)
plan=s['parameters']['source_check_plan']
assert len(plan)==27 and len({x['id'] for x in plan})==27
assert sum(x['status']=='approximate' for x in plan)==24
assert sum(x['status']=='not_computable' for x in plan)==3
for check in plan:
    item=items[check['evidence_id']]
    if check['status']=='not_computable':assert check['operator'] is None;continue
    op=check['operator']
    assert op['unit']==item['unit'] and op['missing_policy']=='error'
    if op['kind']=='ols_coefficient':
        assert op['outcome']=='bmi' and op['predictors']==['urate','age'] and op['term']=='urate' and op['include_intercept']
    else:assert op['kind']==item['kind'] and op['column']=='urate'
    prefix=check['evidence_id'].split('_')[1]
    if check['evidence_id'].startswith('ohyama'):
        assert op['selection']==[{'column':'sex','op':'eq','value':prefix}]
    else:
        idx=groups.index(prefix)
        assert op['selection']==[{'column':'race','op':'eq','value':['White','White','Black','Black'][idx]},
                                 {'column':'sex','op':'eq','value':['male','female','male','female'][idx]}]
result={'status':'pass','scope':'source-only numerical extraction and invented-predictor formula verification',
        'evidence_item_count':len(items),'numeric_items_checked':len(expected),
        'supplement_numeric_items_parsed_directly_from_original_docx':original_supplement_numeric_items,
        'source_plan_checks':len(plan),'invented_formula_comparisons':formula_checks,
        'target_data_read':False,'observed_rows_read':False,'generated_rows_read':False,
        'bindings':{name:sha(c/name) for name in ['evidence.json','model_spec.json','audit/construction.json','audit/revision_plan.json']}}
with Path(__file__).with_suffix('.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
