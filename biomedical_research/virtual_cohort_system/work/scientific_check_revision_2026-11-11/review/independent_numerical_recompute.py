"""Independent saved-table arithmetic; explicit post-code-audit authorization required.
Never executes candidate code, calls a model, fits a clinical reference or reads patients.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,math,re,unicodedata
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]
P=R.parents[1]
OLD=R.parent/'request_only_repeatability_2026-11-11'
SNAP=P/'work/cross_model_api_pilot_2026-11-10/_host_only/REFERENCE_SNAPSHOT.json'
EPS=np.finfo(float).eps
KEYS={'PNS':['bmi_sbp','bmi_dbp','residual_correlation','sbp.sd_population','dbp.sd_population','sbp_below_dbp_fraction'],
 'lipids':['K02-HDL-BMI','K02-TC-BMI','K02-LIPID-RESIDUAL','total_cholesterol.sd_sample','hdl_cholesterol.sd_sample','hdl_above_total_fraction']}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s).lower() if not unicodedata.combining(c))
def arithmetic(frame,case):
 """Independent unweighted OLS; unscaled covariates then slope times five."""
 assert case in KEYS and len(frame)>4 and frame.columns.is_unique
 ident=frame.columns[0];assert not frame[ident].isna().any() and not frame[ident].duplicated().any()
 if case=='PNS':
  cols=['age','female','bmi','sbp','dbp'];z=frame[cols].to_numpy(float)
  assert np.isfinite(z).all() and np.isin(z[:,1],[0,1]).all() and np.all((z[:,0]>=20)&(z[:,0]<=79))
  age,sex,bmi,y0,y1=z.T
 else:
  cols=['age','bmi','total_cholesterol','hdl_cholesterol'];z=frame[cols].to_numpy(float)
  assert np.isfinite(z).all() and frame['sex'].isin(['F','M']).all() and np.all(z[:,0]>=18) and np.all(z[:,1:]>0)
  age,bmi,tc,hdl=z.T;sex=(frame['sex']=='F').to_numpy(float);y0=tc*38.67;y1=hdl*38.67
 X=np.column_stack([np.ones(len(frame)),age,sex,bmi]);Y=np.column_stack([y0,y1])
 scaled=np.column_stack([np.ones(len(frame)),(age-50)/10,sex,(bmi-25)/5])
 rank=int(np.linalg.matrix_rank(scaled));values=dict.fromkeys(KEYS[case])
 if case=='PNS':
  values.update({'sbp.sd_population':float(np.std(y0,ddof=0)),'dbp.sd_population':float(np.std(y1,ddof=0)),
    'sbp_below_dbp_fraction':float(np.mean(y0<y1))})
 else:
  values.update({'total_cholesterol.sd_sample':float(np.std(y0,ddof=1)),'hdl_cholesterol.sd_sample':float(np.std(y1,ddof=1)),
    'hdl_above_total_fraction':float(np.mean(y1>y0))})
 if rank==4:
  # Different coordinates and joint solve from the production estimators.
  coef=np.linalg.lstsq(X,Y,rcond=None)[0];res=Y-X@coef;res-=np.mean(res,axis=0)
  for j,key in enumerate(['bmi_sbp','bmi_dbp'] if case=='PNS' else ['K02-TC-BMI','K02-HDL-BMI']):
   if case=='PNS' or np.ptp(Y[:,j])!=0:values[key]=float(5*coef[3,j])
  if case=='PNS':
   usable=min(np.mean(res**2,axis=0))>EPS*max(float(np.var(y0)),float(np.var(y1)),1.)*100
  else:
   usable=all(np.linalg.norm(res[:,j])>16*EPS*max(scaled.shape)*max(float(np.linalg.norm(Y[:,j])),np.finfo(float).tiny) for j in [0,1])
  if usable:
   corr=float((res[:,0]/np.linalg.norm(res[:,0]))@(res[:,1]/np.linalg.norm(res[:,1])))
   values['residual_correlation' if case=='PNS' else 'K02-LIPID-RESIDUAL']=float(np.clip(corr,-1,1))
 margins={}
 for c in frame.select_dtypes(include='number').columns:
  if c==ident:continue
  a=frame[c].to_numpy(float);margins[c]={'mean':float(np.mean(a)),'sd_sample':float(np.std(a,ddof=1)),
   'min':float(np.min(a)),'max':float(np.max(a)),'quantiles':{str(q):float(np.quantile(a,q)) for q in [.01,.25,.5,.75,.99]}}
 quality={'design_rank':rank,'n':len(frame),'row_filtering':False,'component_violation_count':int(np.sum(y0<y1)),
          'duplicate_measurement_rows':int(frame.drop(columns=[ident]).duplicated().sum())}
 return {'values':values,'margins':margins,'quality':quality}
def tariff(usage,model):
 if not isinstance(usage,dict):return None
 i,o=usage.get('input_tokens'),usage.get('output_tokens');d=usage.get('input_tokens_details') or {};c,w=d.get('cached_tokens',0),d.get('cache_write_tokens',0)
 if any(type(v) is not int or v<0 for v in [i,o,c,w]) or c+w>i:return None
 fi,fo=(2,1.5) if i>272000 else (1,1)
 return (((i-c-w)*model['input_rate']+c*model['cached_rate']+w*model['cache_write_rate'])*fi+o*model['output_rate']*fo)/1e6

def main():
 authorization=read(R/'review/NUMERICAL_REVIEW_AUTHORIZATION.json')
 assert authorization['status']=='approved'
 assert authorization['code_source_audit_sha256']==sha(R/'review/CODE_SOURCE_CHANGE_AUDIT.json')
 assert authorization['construction_closure_sha256']==sha(R/'CONSTRUCTION_CLOSURE.json')
 source_audit=read(R/'review/CODE_SOURCE_CHANGE_AUDIT.json');assert source_audit['target_comparisons_inspected'] is False
 c,plan=read(R/'CONSTRUCTION_CLOSURE.json'),read(R/'PLAN.json')
 assert c['all_episodes_closed'] and len(c['episodes'])==24 and c['plan_sha256']==sha(R/'PLAN.json')
 final=read(R/'FINAL_TABLES.json');assert final['construction_closure_sha256']==sha(R/'CONSTRUCTION_CLOSURE.json')
 evaluation=read(R/'EVALUATION.json');assert evaluation['final_tables_sha256']==sha(R/'FINAL_TABLES.json')
 assert evaluation['reference_snapshot_sha256']==sha(SNAP)
 references=read(SNAP)['references']
 mapping={x['pair_id']:x for x in read(R/'_host_only/IMPORT_MAPPING.json')['pairs']}
 for name,h in read(R/'BASELINE_BINDINGS.json')['files'].items():assert sha(OLD/name)==h
 old=read(OLD/'FINAL_TABLES.json');old_eval=read(OLD/'EVALUATION.json')
 checks=[];failures=[];max_error=0.;computed={};oldcomputed={};retention=[];costs=[];exposure=[];exposure_records=[]
 def check(label,ok):
  checks.append(label)
  if not ok:failures.append(label)
 def equal(label,a,b):
  nonlocal max_error
  if a is None or b is None:check(label,a is None and b is None);return
  if isinstance(a,(int,float)) and isinstance(b,(int,float)):
   delta=abs(a-b);max_error=max(max_error,delta);check(label,math.isfinite(a) and math.isfinite(b) and delta<=1e-8+1e-9*max(abs(a),abs(b)))
  else:check(label,a==b)
 def safe(base,relative):
  path=(base/relative).resolve();assert path.is_relative_to(base.resolve());return path
 def analyze_slots(base,records,destination,label):
  for s in records:
   key=(s['episode_id'],s['seed']);check(label+' unique '+str(key),key not in destination)
   result=None
   if s['status']=='success':
    path=safe(base,s['generated_path']);check(label+' row hash '+str(key),sha(path)==s['generated_sha256'])
    receipt=read(safe(base,s['receipt_path']));check(label+' receipt hash '+str(key),sha(safe(base,s['receipt_path']))==s['receipt_sha256'])
    check(label+' bound stats '+str(key),receipt.get('statistics')==s['statistics'])
    check(label+' candidate seed '+str(key),receipt['candidate_id']==s['candidate_id'] and receipt['seed']==s['seed'])
    result=arithmetic(pd.read_csv(path),s['case_id']);check(label+' row count '+str(key),result['quality']['n']==3000)
    supplied={x['id']:x['value'] for cat in ['analyses','diagnostics'] for x in s['statistics'][cat]}
    check(label+' six metrics '+str(key),set(supplied)==set(KEYS[s['case_id']]))
    for metric,value in result['values'].items():equal(label+' '+str(key)+' '+metric,value,supplied[metric])
    for metric,value in result['quality'].items():equal(label+' quality '+str(key)+' '+metric,value,s['statistics']['quality'][metric])
    for col,summary in result['margins'].items():
     existing=s['statistics'].get('marginals_delivered_units',{}).get(col)
     if existing:
      for metric,value in summary.items():
       if isinstance(value,dict):
        for q,v in value.items():equal(label+' marginal '+str(key)+col+metric+q,v,existing[metric][q])
       else:equal(label+' marginal '+str(key)+col+metric,value,existing[metric])
   else:
    check(label+' missing not imputed '+str(key),s.get('statistics') is None)
   destination[key]={'status':s['status'],'statistics':result,'generated_sha256':s.get('generated_sha256')}
 expected={(ep['episode_id'],seed) for ep in plan['episodes'] for seed in plan['evaluation_seeds']}
 check('all72 slots',len(final['slots'])==72 and {(s['episode_id'],s['seed']) for s in final['slots']}==expected)
 analyze_slots(R,final['slots'],computed,'current')
 analyze_slots(OLD,old['slots'],oldcomputed,'initial')
 def summaries(records,eps):
  result={}
  for ep in eps:
   for metric in KEYS[ep['case_id']]:
    vals=[];byseed=[]
    for seed in plan['evaluation_seeds']:
     row=records[(ep['episode_id'],seed)];v=row['statistics']['values'][metric] if row['statistics'] else None
     byseed.append({'seed':seed,'status':row['status'],'value':v})
     if v is not None:vals.append(v)
    ref=references[ep['case_id']][metric]['value']
    result[(ep['episode_id'],metric)]={'values':byseed,'available_seeds':len(vals),'mean':sum(vals)/len(vals) if vals else None,
      'minimum':min(vals) if vals else None,'maximum':max(vals) if vals else None,
      'mean_absolute_reference_difference':sum(abs(v-ref) for v in vals)/len(vals) if vals and ref is not None else None}
  return result
 current_summaries=summaries(computed,plan['episodes'])
 old_eps=[{'episode_id':m['old_episode_id'],'case_id':m['case_id']} for m in mapping.values()]
 initial_summaries=summaries(oldcomputed,old_eps)
 for label,supplied,ours in [('current',evaluation['summaries'],current_summaries),('initial',old_eval['summaries'],initial_summaries)]:
  for row in supplied:
   key=row['episode_id'],row['analysis_id'];computed_row=ours[key]
   check(label+' reference retained '+str(key),row['reference']==references[row['case_id']][row['analysis_id']])
   for f,v in computed_row.items():
    if f=='values':
     for a,b in zip(v,row[f]):equal(label+' seed estimate '+str(key)+str(a['seed']),a['value'],b['value']);check(label+' seed status '+str(key)+str(a['seed']),a['seed']==b['seed'] and a['status']==b['status'])
    else:equal(label+' summary '+str(key)+f,v,row[f])
 pair_rows=[];initial_rows=[]
 for ep in plan['episodes']:
  eid=ep['episode_id'];folder=R/'episodes'/eid;outcome=read(folder/'OUTCOME.json');cid=outcome.get('selected_candidate')
  oldid=mapping[ep['pair_id']]['old_episode_id'];package=R/ep['imported_package_path']
  changes={n:(sha(folder/'candidates'/cid/n)!=sha(package.parent/n)) if cid else None for n in ['generator.py','model_spec.json','notes.json']}
  declared=evaluation['paired_initial_comparison']['artifact_changes'][eid]
  check(eid+' changes exact',declared['changed_artifact_bytes']==changes and declared['explicitly_retained_import']==(cid=='v000'))
  law_same=cid is not None and not changes['generator.py'] and not changes['model_spec.json']
  hashes=[]
  if law_same:
   for seed in plan['evaluation_seeds']:
    now,before=computed[(eid,seed)],oldcomputed[(oldid,seed)]
    same=now['status']==before['status'] and now['generated_sha256']==before['generated_sha256']
    check(eid+' unchanged-law row equality '+str(seed),same);hashes.append({'seed':seed,'equal':same})
  retention.append({'episode_id':eid,'law_byte_identical':law_same,'changes':changes,'seed_hashes':hashes})
  for metric in KEYS[ep['case_id']]:
   a=initial_summaries[(oldid,metric)]['mean'];b=current_summaries[(eid,metric)]['mean'];ref=references[ep['case_id']][metric]['value']
   delta=b-a if a is not None and b is not None else None;ed=abs(b-ref)-abs(a-ref) if delta is not None and ref is not None else None
   supplied=next(r for r in evaluation['paired_initial_comparison']['rows'] if r['episode_id']==eid and r['analysis_id']==metric)
   equal(eid+metric+' paired initial',a,supplied['initial_mean']);equal(eid+metric+' paired final',b,supplied['final_mean'])
   equal(eid+metric+' paired delta',delta,supplied['change_in_mean']);equal(eid+metric+' paired error delta',ed,supplied['change_in_absolute_reference_difference'])
   initial_rows.append({'episode_id':eid,'pair_id':ep['pair_id'],'case_id':ep['case_id'],'arm':ep['arm'],'analysis_id':metric,'initial_mean':a,'final_mean':b,'reference':ref,'change':delta,'absolute_distance_change':ed,'law_byte_identical':law_same})
  known=accounted=0.;unknown=0;call_count=0
  for reserve_path in sorted((folder/'calls').glob('*/reservation.json')):
   reservation=read(reserve_path);cf=reserve_path.parent;call_count+=1
   check(eid+' request hash '+cf.name,sha(cf/'request.json')==reservation['request_sha256'])
   if not (cf/'receipt.json').exists():unknown+=1;accounted+=reservation['reserved_usd'];continue
   receipt=read(cf/'receipt.json');check(eid+' cost receipt '+cf.name,receipt['reservation_sha256']==sha(reserve_path))
   actual=tariff(receipt.get('usage'),plan['model'])
   if actual is None:unknown+=1;accounted+=reservation['reserved_usd']
   else:known+=actual;accounted+=actual;equal(eid+' tariff '+cf.name,actual,receipt['tariff_cost_usd'])
   check(eid+' model identity '+cf.name,receipt['returned_model']==plan['model']['id'])
  equal(eid+' total known',known,outcome['known_tariff_cost_usd']);equal(eid+' total accounted',accounted,outcome['accounted_usd'])
  check(eid+' usage count',unknown==outcome['unknown_usage_calls'] and call_count==outcome['calls_reserved'])
  for rel,h in outcome['history_files'].items():check(eid+' closed call hash '+rel,sha(safe(folder,rel))==h)
  costs.append({'episode_id':eid,'calls':call_count,'known_tariff_usd':known,'accounted_usd':accounted,'unknown_usage_calls':unknown})
  for path in sorted((folder/'calls').glob('*/tool_*.result.json')):
   value=json.loads(read(path)['output']);intent=read(path.with_name(path.name.replace('.result.','.intent.')))['call']
   if intent['name'] not in {'literature_search','read_source'}:continue
   exposure_records.append({'episode_id':eid,'tool':intent['name'],'arguments':json.loads(intent['arguments']),'status':value.get('status'),'reason':value.get('reason'),'source_id':value.get('source_id'),'source_version':value.get('source_version'),'source_xml_sha256':value.get('xml_sha256'),'tool_result':str(path.relative_to(R)),'tool_result_sha256':sha(path)})
   parts=[value['content']] if isinstance(value.get('content'),str) else []
   parts += [m['context'] for m in value.get('matches',[]) if isinstance(m.get('context'),str)]
   if value.get('hits'):parts.append(json.dumps(value['hits'],ensure_ascii=False))
   text='\n'.join(parts);normalized=norm(text)
   for pattern in ['pesquisa nacional','national health survey','turkana','evidence-guided-virtual-cohorts','from published evidence to analyzable',r'\bpns\b']:
    for hit in re.finditer(pattern,normalized):exposure.append({'episode_id':eid,'tool_result':str(path.relative_to(R)),'pattern':pattern,'context':text[max(0,hit.start()-120):hit.end()+160]})
 for pair,m in mapping.items():
  for metric in KEYS[m['case_id']]:
   g=current_summaries[(pair+'_GENERIC',metric)]['mean'];s=current_summaries[(pair+'_STRUCTURED',metric)]['mean'];ref=references[m['case_id']][metric]['value']
   pair_rows.append({'pair_id':pair,'case_id':m['case_id'],'analysis_id':metric,'generic_mean':g,'structured_mean':s,'reference':ref,
    'structured_minus_generic':s-g if s is not None and g is not None else None,
    'structured_minus_generic_absolute_distance':abs(s-ref)-abs(g-ref) if s is not None and g is not None and ref is not None else None})
 equal('overall known cost',sum(x['known_tariff_usd'] for x in costs),evaluation['costs']['known_tariff_usd'])
 equal('overall accounted cost',sum(x['accounted_usd'] for x in costs),evaluation['costs']['accounted_usd'])
 check('total cap',sum(x['accounted_usd'] for x in costs)<=48)
 report={'status':'pass' if not failures else 'blocked','created_utc':datetime.now(timezone.utc).isoformat(),
  'authorization_sha256':sha(R/'review/NUMERICAL_REVIEW_AUTHORIZATION.json'),'code_source_audit_sha256':sha(R/'review/CODE_SOURCE_CHANGE_AUDIT.json'),
  'construction_closure_sha256':sha(R/'CONSTRUCTION_CLOSURE.json'),'evaluation_sha256':sha(R/'EVALUATION.json'),
  'runner_sha256':sha(Path(__file__)),'checks':len(checks),'failures':failures,'largest_absolute_arithmetic_difference':max_error,
  'current_slot_status_counts':dict(Counter(x['status'] for x in computed.values())),'initial_slot_status_counts':dict(Counter(x['status'] for x in oldcomputed.values())),
  'retention_hash_checks':retention,'initial_comparisons':initial_rows,'generic_structured_comparisons':pair_rows,'costs':costs,'source_exposure_flags':exposure,'source_exposure_records':exposure_records,
  'source_exposure_boundary':'Literal matches require adjudication; no matches do not certify independence. Historical source exposure remains developmental.',
  'interpretation':'No pooled cross-unit score or new acceptance threshold. Equal-law outputs must be equal at the same saved seeds; different-law seeds are not independent constructors. Difference to a sample reference is not population accuracy.',
  'clinical_patient_rows_read':False,'saved_generated_tables_read':True,'new_generator_runs':0,'new_provider_calls':0,'new_reference_fits':0}
 write(R/'review/INDEPENDENT_NUMERICAL_REVIEW.json',report)
 print(json.dumps({'status':report['status'],'checks':len(checks),'failures':failures,'current':report['current_slot_status_counts'],'initial':report['initial_slot_status_counts'],'max_difference':max_error,'exposure_flags':len(exposure)},ensure_ascii=False))
if __name__=='__main__':main()
