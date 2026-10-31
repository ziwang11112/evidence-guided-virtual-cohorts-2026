"""Invented-only tests for the independent audit's M16 adapter; no private data."""
import importlib.util,json,copy,csv,os
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd
import pytest

HERE=Path(__file__).resolve().parent
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
audit=load('m16_audit_adapter',HERE/'recompute.py')
ev=load('m16_ev_for_fixture',HERE.parent/'evaluation_code/evaluator.py')

def fixture(tmp_path):
 records=[]
 for g,(race,sex) in enumerate((('White','male'),('White','female'),('Black','male'),('Black','female'))):
  for j in range(50):
   age=20+(j*7+g*3)%37;bmi=19+((j*11+g*5)%43)/2
   b=(bmi-28)/5;a=(age-40)/10;m=int(sex=='male');r=int(race=='Black')
   records.append(dict(sample_id=f'invented{g}_{j}',race=race,sex=sex,age=age,bmi=bmi,
       urate=4+.4*b-.15*a+.5*m+.2*r+.03*b*b+.06*b*m,
       SDMVSTRA=str(1+j%5),SDMVPSU=str(1+j%2),WTMEC2YR=100+j))
 ref=pd.DataFrame(records);raw=ref.to_csv(index=False).encode()
 release={'reference_weight_column':'WTMEC2YR','builders':[]};tables={}
 for k,bid in enumerate(('b1','b2','b3')):
  b=tmp_path/bid;b.mkdir();builder={'id':bid,'bundle_path':str(b),'status':'complete'};tables[bid]={}
  for stage,delta in [('initial',.2*(k+1)),('final',.05*(k+1))]:
   p=b/'candidates'/stage;p.mkdir(parents=True)
   frame=ref.loc[:,list(ev.load_estimands().BASE_COLUMNS)].copy();frame['urate']+=delta
   dest=p/'generated.csv';frame.to_csv(dest,index=False)
   builder[stage]={'candidate':'candidates/'+stage,'table_sha256':ev.sha(dest)}
   tables[bid][stage]=audit.rows(dest.read_bytes())
  release['builders'].append(builder)
 released=ev.evaluate_verified(release,raw)
 observed=ref.loc[:,['sample_id','race','sex','age','bmi']].to_csv(index=False).encode()
 return audit.rows(raw),audit.rows(observed),tables,released

def test_independent_all_six_tables_and_psu(tmp_path):
 ref,x,tables,released=fixture(tmp_path)
 result=audit.compare_results(audit.load_independent(),ref,x,tables,released)
 assert result['status']=='PASS' and result['comparison_count']>2000
 assert result['maximum_absolute_numeric_difference']<1e-10
 assert len(result['candidate_estimands'])==6
 assert all(v['changed_urate_rows']==200 for v in result['preservation'].values())

def test_detect_changed_scientific_estimate(tmp_path):
 ref,x,tables,released=fixture(tmp_path)
 released['candidate_comparisons'][0]['estimands'][0]['generated']['value']+=1
 with pytest.raises(ValueError,match='Independent disagreement'):
  audit.compare_results(audit.load_independent(),ref,x,tables,released)

def test_detect_changed_covariate(tmp_path):
 ref,x,tables,released=fixture(tmp_path)
 tables['b2']['final'][0]['bmi']='12345'
 with pytest.raises(ValueError,match='covariate changed'):
  audit.compare_results(audit.load_independent(),ref,x,tables,released)

@pytest.mark.parametrize('part',['reference','candidate','changes','psu_summary','psu_deletion','builder'])
def test_detect_missing_or_duplicate_endpoint(tmp_path,part):
 ref,x,tables,released=fixture(tmp_path)
 if part=='reference':released['reference_estimands'].pop()
 if part=='candidate':released['candidate_comparisons'][0]['estimands'][-1]=released['candidate_comparisons'][0]['estimands'][0]
 if part=='changes':released['initial_final_changes'].pop()
 if part=='psu_summary':released['reference_sensitivity']['summaries'].pop()
 if part=='psu_deletion':released['reference_sensitivity']['summaries'][0]['deletions'].pop()
 if part=='builder':released['builder_outcomes'].pop()
 with pytest.raises(ValueError,match='Incomplete or duplicate'):
  audit.compare_results(audit.load_independent(),ref,x,tables,released)

def test_csv_json_integrity_and_corruption(tmp_path):
 ref,x,tables,released=fixture(tmp_path)
 dest=tmp_path/'results';ev.write_results(dest,released)
 out=audit.verify_csv_integrity(audit.read(dest/'evaluation.json'),dest)
 assert out['estimands.csv']['rows']==144 and out['initial_final_changes.csv']['rows']==72
 p=dest/'estimands.csv'
 with p.open(newline='',encoding='utf-8') as f:r=list(csv.DictReader(f));fields=list(r[0])
 r[0]['generated_value']='123456'
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(r)
 with pytest.raises(ValueError,match='CSV/JSON value mismatch'):audit.verify_csv_integrity(released,dest)

def test_csv_json_missing_change_row(tmp_path):
 ref,x,tables,released=fixture(tmp_path)
 dest=tmp_path/'results';ev.write_results(dest,released)
 p=dest/'initial_final_changes.csv';p.write_text('\n'.join(p.read_text().splitlines()[:-1])+'\n')
 with pytest.raises(ValueError,match='CSV/JSON shape mismatch'):audit.verify_csv_integrity(released,dest)

def test_native_weights_are_not_estimators_and_psu_is_joint(tmp_path):
 ref,x,tables,released=fixture(tmp_path)
 for i,row in enumerate(ref):row['WTMEC2YR']=str(1e12 if i%3 else .00001)
 result=audit.compare_results(audit.load_independent(),ref,x,tables,released)
 assert len(result['reference_psu_sensitivity']['deletions'])==10
 assert result['maximum_absolute_numeric_difference']<1e-10

@pytest.mark.parametrize('mode',['retain_and_failed','rank_failure'])
def test_retention_failure_and_null_estimands(tmp_path,mode):
 ref,x,tables,_=fixture(tmp_path)
 release={'reference_weight_column':'WTMEC2YR','builders':[]}
 if mode=='rank_failure':
  for row in ref+x:row['age']='40'
 for bid,stages in tables.items():
  builder={'id':bid,'bundle_path':str(tmp_path/bid),'status':'complete'}
  if mode=='retain_and_failed' and bid=='b1':stages['final']=copy.deepcopy(stages['initial'])
  if mode=='retain_and_failed' and bid=='b3':
   del stages['final'];builder.update(status='failed',failure_record={'fixture':'no final'})
  for stage,table in stages.items():
   if mode=='rank_failure':
    for row in table:row['age']='40'
   p=tmp_path/bid/'candidates'/stage/'generated.csv';pd.DataFrame(table).to_csv(p,index=False)
   builder[stage]={'candidate':'candidates/'+stage,'table_sha256':audit.sha(p)}
  release['builders'].append(builder)
 released=ev.evaluate_verified(release,pd.DataFrame(ref).to_csv(index=False).encode())
 result=audit.compare_results(audit.load_independent(),ref,x,tables,released)
 dest=tmp_path/'results';ev.write_results(dest,released);audit.verify_csv_integrity(audit.read(dest/'evaluation.json'),dest)
 if mode=='retain_and_failed':
  assert len(result['candidate_estimands'])==5
  assert result['preservation']['b1']['changed_urate_rows']==0
  assert len(released['initial_final_changes'])==48
 else:
  assert all(v['failed_deletions']==10 and v['minimum'] is None for v in result['reference_psu_sensitivity']['ranges'].values())

def gate_fixture(tmp_path):
 """Minimal invented bound-file lifecycle; no real reference or generation read."""
 run=tmp_path/'project/work/run';run.mkdir(parents=True)
 def save(p,value):
  p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2),encoding='utf-8')
 def bind(p):return {'path':str(p),'sha256':audit.sha(p)}
 fixed={'protocol':run/'PROTOCOL.md','controller':run/'controller.py',
        'evaluator':run/'evaluation_code/evaluator.py','estimands':run/'evaluation_code/frozen_m15b_estimands.py',
        'self_checker':run.parent.parent/'cohort_harness/self_consistency.py'}
 for p in fixed.values():p.parent.mkdir(parents=True,exist_ok=True);p.write_text('INVENTED BINDING ONLY')
 ref=run/'private/reference.csv';ref.parent.mkdir();ref.write_text('INVENTED REFERENCE NEVER PARSED')
 builders=[];files={'PROTOCOL.md':audit.sha(fixed['protocol']),'controller.py':audit.sha(fixed['controller'])}
 for bid in audit.BUILDERS:
  b=run/'visible'/bid/'bundle';b.mkdir(parents=True)
  save(b/'task.json',{'task_id':bid,'fixture':True});save(b/'registry.json',{'artifacts':[]})
  (b/'observed.csv').write_text('INVENTED X')
  for name in ('task.json','observed.csv'):files[(b/name).relative_to(run).as_posix()]=audit.sha(b/name)
  builders.append({'id':bid,'bundle_path':str(b),'status':'complete','task_sha256':audit.sha(b/'task.json'),'observed_sha256':audit.sha(b/'observed.csv')})
 pre=run/'prelaunch.json'
 save(pre,{'files':files,'engine_files':{str(fixed['self_checker']):audit.sha(fixed['self_checker'])},
           'reference':bind(ref),'reference_weight_column':'WTMEC2YR','registry_prefixes':{b:[] for b in audit.BUILDERS}})
 for builder in builders:
  b=Path(builder['bundle_path']);bid=builder['id']
  for i,stage in enumerate(('initial','final')):
   name='candidates/'+stage;cp=b/name;cp.mkdir(parents=True)
   for science in audit.SCIENCE_FILES:save(cp/science,{'fixture':'not a scientific assertion'})
   pc=run/'commitments'/bid/(stage+'.json')
   save(pc,{'builder':bid,'candidate':name,'generated_exists':False,'created_utc':datetime.now(timezone.utc).isoformat(),
            'prelaunch_sha256':audit.sha(pre),'files':{f:audit.sha(cp/f) for f in audit.SCIENCE_FILES}})
   (cp/'audit/preauthoring_commitment.json').write_bytes(pc.read_bytes());(cp/'generated.csv').write_text('INVENTED TABLE')
   commitments={name+'/'+p.relative_to(cp).as_posix():audit.sha(p) for p in cp.rglob('*') if p.is_file()}
   commitments.update({'task.json':builder['task_sha256'],'observed.csv':builder['observed_sha256']})
   parent=None if i==0 else {'candidate':'candidates/initial','receipt_path':'candidates/initial/freeze.json','sha256':builder['initial']['freeze_sha256']}
   save(cp/'freeze.json',{'candidate':name,'route':'generated.csv','commitments':commitments,'revision_index':i,
                        'parent':parent,'created_utc':datetime.now(timezone.utc).isoformat()})
   builder[stage]={'candidate':name,'table_sha256':audit.sha(cp/'generated.csv'),'freeze_sha256':audit.sha(cp/'freeze.json'),'preauthoring':bind(pc)}
 release={'schema_version':1,'kind':'m16_target_evaluation_release','evaluation_authorized':True,
          'controller_checks':{k:True for k in audit.CHECKS},'prelaunch':bind(pre),'reference':bind(ref),
          'reference_weight_column':'WTMEC2YR','builders':builders,**{k:bind(p) for k,p in fixed.items()}}
 path=run/'release.json';save(path,release)
 result={'release_manifest_sha256':audit.sha(path),'evaluator_sha256':release['evaluator']['sha256'],'frozen_estimands_sha256':release['estimands']['sha256']}
 return run,path,release,result,ref

@pytest.mark.parametrize('defect',[None,'assertion','kind','precommit','code','prelaunch_reference_alias','reference_hardlink'])
def test_public_gate_never_reads_reference(tmp_path,monkeypatch,defect):
 run,path,release,result,ref=gate_fixture(tmp_path)
 if defect=='assertion':release['controller_checks']['all_builders_closed']=False
 if defect=='kind':release['kind']='wrong'
 if defect=='precommit':
  p=Path(release['builders'][2]['final']['preauthoring']['path']);record=audit.read(p);record['generated_exists']=True;p.write_text(json.dumps(record))
 if defect=='code':Path(release['controller']['path']).write_text('changed')
 if defect=='prelaunch_reference_alias':
  p=Path(release['prelaunch']['path']);pre=audit.read(p);pre['files']['private/reference.csv']=release['reference']['sha256'];p.write_text(json.dumps(pre));release['prelaunch']['sha256']=audit.sha(p)
 if defect=='reference_hardlink':
  alias=run/'alias.py';os.link(ref,alias)
  p=Path(release['prelaunch']['path']);pre=audit.read(p);pre['engine_files'][str(alias)]=release['reference']['sha256'];p.write_text(json.dumps(pre));release['prelaunch']['sha256']=audit.sha(p)
 path.write_text(json.dumps(release));result['release_manifest_sha256']=audit.sha(path)
 original=Path.read_bytes;calls=[]
 def protect(p):
  if p.resolve()==ref.resolve():calls.append(str(p));raise AssertionError('Premature reference access')
  return original(p)
 monkeypatch.setattr(Path,'read_bytes',protect)
 if defect is None:assert audit.verify_public_release(path,result,run=run)['evaluation_authorized'] is True
 else:
  with pytest.raises(ValueError):audit.verify_public_release(path,result,run=run)
 assert calls==[]

def test_no_execute_flag_reads_nothing(tmp_path,monkeypatch):
 def forbidden(_):raise AssertionError('No file reads expected')
 monkeypatch.setattr(audit,'read',forbidden)
 with pytest.raises(SystemExit):audit.main(['--release',str(tmp_path/'r'),'--results',str(tmp_path/'v'),'--output',str(tmp_path/'o')])
