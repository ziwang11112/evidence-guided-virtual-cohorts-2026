"""Summarize only M11 source executions, never target tables or evaluator files."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from cohort_harness.source_replay import verify_source_replay
from cohort_harness.lifecycle import verify_candidate
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=read(HERE/'source_plan.json');summ={'scope':'source_only','source_plan_sha256':sha(HERE/'source_plan.json'),'target_data_or_results_read':False,'all_versions_retained':True,'candidates':[],'pairs':[],'verified_generator_executions':0,'verified_replay_reports':0,'source_run_failures':[],'limitations':['Pooled summaries are derived from verified per-seed outputs, not a native harness pooled estimator.','Calibrated median fit uses the same source seeds and is mechanical.','IQR and age diagnostics were not refitted; no target validity inferred.','Scenarios are sensitivity alternatives, not calibrated parameter or transport uncertainty.']}
refs={'male':{'q25':5.0,'median':5.3,'q75':5.8,'age':.0153},'female':{'q25':4.8,'median':5.2,'q75':5.6,'age':.0191}}
for family in ['ha','hb']:
 b=ROOT/'work/m11'/family;names=['initial']+['calibrated_'+s['id'] for s in plan['scenarios']]
 reports={}
 for name in names:
  c=b/'candidates'/name;receipt=verify_candidate(b,c)
  assert sha(c/'source_plan.json')==summ['source_plan_sha256']
  summ['candidates'].append({'family':family,'name':name,'path':str(c),'freeze_sha256':sha(c/'freeze.json'),'generator_sha256':sha(c/'generator.py'),'model_spec_sha256':sha(c/'model_spec.json'),'evidence_sha256':sha(c/'evidence.json'),'parent':receipt['parent']})
  for seed in plan['source_seeds']:
   r=verify_source_replay(b,f'{name}_{seed}',candidate=f'candidates/{name}');reports[name,seed]=r
   summ['verified_replay_reports']+=1;summ['verified_generator_executions']+=len(r['contexts'])
   if r['status']!='success':summ['source_run_failures'].append({'family':family,'candidate':name,'seed':seed})
 assert not summ['source_run_failures']
 for s in plan['scenarios']:
  sid=s['id'];new='calibrated_'+sid;cal=read(b/f'candidates/{new}/calibration.json')
  pooled={name:[] for name in ['initial',new]}
  for name in pooled:
   for seed in plan['source_seeds']:
    p=b/f'source_replays/{name}_{seed}/contexts/{sid}/bundle/executions/replay/output/generated.csv'
    pooled[name].append(pd.read_csv(p,usecols=['sex','hba1c_pct'],float_precision='round_trip'))
   pooled[name]=pd.concat(pooled[name],ignore_index=True)
  for sex,label in [('male','men'),('female','women')]:
   pair={'family':family,'scenario':sid,'sex':sex,'offset':cal['sex'][sex]['offset'],'location':cal['sex'][sex]['calibrated_location'],'source_reference':refs[sex],'pooled':{},'per_seed':[]}
   for name in pooled:
    y=pooled[name].loc[pooled[name].sex.eq(sex),'hba1c_pct'].to_numpy();q=np.quantile(y,[.25,.5,.75],method='linear')
    pair['pooled'][name]={'n':len(y),'q25':float(q[0]),'median':float(q[1]),'q75':float(q[2]),'iqr':float(q[2]-q[0]),'median_difference_from_source':float(q[1]-refs[sex]['median']),'q25_difference_from_source':float(q[0]-refs[sex]['q25']),'q75_difference_from_source':float(q[2]-refs[sex]['q75']),'lower_bound_count':int((y==3).sum()),'upper_bound_count':int((y==20).sum())}
   pair['pooled_iqr_change']=pair['pooled'][new]['iqr']-pair['pooled']['initial']['iqr']
   for seed in plan['source_seeds']:
    row={'seed':seed}
    for name in ['initial',new]:
     ctx=next(x for x in reports[name,seed]['contexts'] if x['id']==sid)
     checks={x['evidence_id']:x for x in ctx['checks']}
     assert all(x['generation_link_verified'] for x in checks.values())
     keys={'median':f'ship_SHIP_Trend_{label}_median_None','q25':f'ship_SHIP_Trend_{label}_quantile_0.25','q75':f'ship_SHIP_Trend_{label}_quantile_0.75','age':f'ship_SHIP_Trend_{label}_age_beta_per_year'}
     row[name]={k:{'value':checks[e]['value'],'difference':checks[e]['difference']} for k,e in keys.items()}
     row[name]['iqr']=row[name]['q75']['value']-row[name]['q25']['value']
    row['age_change']=row[new]['age']['value']-row['initial']['age']['value'];pair['per_seed'].append(row)
   summ['pairs'].append(pair)
families={f:[x for x in summ['candidates'] if x['family']==f] for f in ['ha','hb']}
assert len({x['evidence_sha256'] for x in summ['candidates']})==1
for f,cs in families.items():assert len({x['generator_sha256'] for x in cs})==1
summ['paired_evidence_identical_across_all_candidates']=True;summ['generator_identical_within_each_family']=True
summ['max_abs_calibrated_pooled_median_difference']=max(abs(x['pooled']['calibrated_'+x['scenario']]['median_difference_from_source']) for x in summ['pairs'])
summ['max_abs_pooled_iqr_change']=max(abs(x['pooled_iqr_change']) for x in summ['pairs'])
summ['max_abs_per_seed_age_slope_change']=max(abs(r['age_change']) for x in summ['pairs'] for r in x['per_seed'])
(HERE/'source_screen_summary.json').write_text(json.dumps(summ,indent=2,allow_nan=False)+'\n',encoding='utf-8')
lines=['# M11 source-only screen completion','',f"Verified {summ['verified_generator_executions']} isolated source generator executions in {summ['verified_replay_reports']} replay reports; no source execution failures. All eight candidates are frozen/verified. Evidence bytes match across every candidate; generator bytes match within each family. No target tables or evaluator results were read.",'','| Family | Scenario | Sex | Location offset | Initial median | Calibrated median | IQR | Mean replay age slope |','|---|---|---|---:|---:|---:|---:|---:|']
for p in summ['pairs']:
 name='calibrated_'+p['scenario'];a=p['pooled']['initial'];z=p['pooled'][name];slope=np.mean([r[name]['age']['value'] for r in p['per_seed']])
 lines.append(f"| {p['family']} | {p['scenario']} | {p['sex']} | {p['offset']:.6f} | {a['median']:.6f} | {z['median']:.6f} | {z['iqr']:.6f} | {slope:.6f} |")
lines+=['',f"Maximum absolute calibrated pooled-median discrepancy is {summ['max_abs_calibrated_pooled_median_difference']:.3g} percentage points. Maximum pooled IQR change is {summ['max_abs_pooled_iqr_change']:.3g}; maximum per-seed age-slope change is {summ['max_abs_per_seed_age_slope_change']:.3g} percentage points/year.",'','The source-reference IQR is 0.8 for each sex. Reference age slopes are 0.0153 (men) and 0.0191 (women) percentage points/year. Individual quartile/age discrepancies and every seed remain in source_screen_summary.json. Locations were calibrated to medians; neither IQRs nor slopes were refitted. Exact median agreement is expected from the fixed additive correction and reused source seeds. It provides no independent target validation.','',f"Source plan SHA256: `{summ['source_plan_sha256']}`",'','Source support and selection remain approximate: raw baseline n=4420 age bins are used for the n=4402 HbA1c analysis sample; open >=70 compressed to 70-79; pooled BMI used within each sex; dependence and tails assumed. Grossmann moments are unfitted context diagnostics. The initial pooled-age quartiles 40/52/65 differ from Masuch 40/53/64 and were retained.','','Controller review: fixed-plan hash guards were added; all candidate plan copies and audit plan hash matched before target phase. New replay reports are verified inside run_source_replay (its return calls verify_source_replay); calibration also verifies initial reports explicitly. An extra source-rank assertion initially treated clipped ties as strict ordering; corrected before any freeze to allow tied values, then all source-X invariants passed. No scientific candidate parameter changed because of that preparation check.']
(HERE/'source_screen_completion.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'source_executions':summ['verified_generator_executions'],'replay_reports':summ['verified_replay_reports'],'candidates':len(summ['candidates']),'max_median_error':summ['max_abs_calibrated_pooled_median_difference'],'max_iqr_change':summ['max_abs_pooled_iqr_change'],'max_age_change':summ['max_abs_per_seed_age_slope_change'],'summary':str(HERE/'source_screen_summary.json')}))
