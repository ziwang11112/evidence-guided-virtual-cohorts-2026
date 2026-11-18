from pathlib import Path
import json,csv,hashlib
from collections import Counter
from datetime import datetime,timezone
U=Path(__file__).resolve().parent;P=U.parents[1]
ROUNDS={'R1':P/'work/cross_model_api_pilot_2026-11-10','R2':P/'work/economy_feedback_pilot_2026-11-10'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(name,obj):
 (U/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def csvout(name,rows,fields=None):
 fields=fields or list(rows[0])
 with (U/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='raise');w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})
def native_records(rnd,u):
 if rnd=='R1':
  for r in read(u/'CONSTRUCTION_OUTCOMES.json')['records']:
   yield dict(r,version_id=r['construction_id'],kind='initial',parent_version_id=None,review_disposition=None,call_directory=u/'calls'/(r['construction_id']+'_initial'))
 else:
  parents=read(u/'INITIAL_OUTCOMES.json')['records'];lookup={r['parent_id']:r for r in parents}
  for r in parents:yield dict(r,version_id=r['parent_id'],kind='initial',parent_version_id=None,review_disposition=None,call_directory=u/'calls/initial'/r['parent_id'])
  for b in read(u/'REVIEW_OUTCOMES.json')['records']:
   r=lookup[b['parent_id']];yield dict(r,version_id=b['branch_id'],candidate_path=b['candidate_path'],kind='review',parent_version_id=b['parent_id'],review_disposition=b['disposition'],call_directory=u/'calls/review'/b['branch_id'])
def main():
 inputs={};maps={};sources={}
 for case in ['PNS','LIPID']:
  path=U/(case+'_PARAMETER_MAP.json');v=read(path);inputs[str(path.relative_to(P))]=sha(path);sources[case]=v.get('sources',{})
  for r in v['records']:
   k=(r['round'],r['version_id']);assert k not in maps,k;maps[k]=r
 attempts=[];summaries=[];seedrows=[];parameters=[];derivations=[]
 for rnd,u in ROUNDS.items():
  e=read(u/'EVALUATION.json');inputs[str((u/'EVALUATION.json').relative_to(P))]=sha(u/'EVALUATION.json')
  native=e.get('construction_summaries',e.get('version_summaries'));slots=e['all_slots']
  for r in native_records(rnd,u):
   ident=r['version_id'];key=(rnd,ident);m=maps.pop(key);receipt=read(r['call_directory']/'receipt.json');vidfield='construction_id' if rnd=='R1' else 'version_id'
   sub=[s for s in slots if s[vidfield]==ident];assert len(sub)==3
   ss=[s for s in native if s[vidfield]==ident];assert len(ss)==6
   assert m['case_id']==r['case_id'] and m['kind']==r['kind'];assert m.get('parent_version_id')==r['parent_version_id']
   artifact=r['call_directory']/'artifact.json'
   success=sum(s['execution_status']=='success' for s in sub);complete=sum(s['analysis_status']=='complete' for s in sub)
   a={'round':rnd,'version_id':ident,'case_id':r['case_id'],'model_config':r['model_config'],'requested_model':receipt['requested_model'],'returned_model':receipt.get('returned_model'),'kind':r['kind'],'parent_version_id':r['parent_version_id'],'review_disposition':r['review_disposition'],'api_status':receipt['status'],'api_artifact_status':receipt.get('artifact_status'),'execution_status_counts':dict(Counter(s['execution_status'] for s in sub)),'successful_tables':success,'complete_analysis_tables':complete,'scheduled_tables':3,'tariff_cost_usd':receipt.get('tariff_cost_usd'),'unknown_reserve_usd':receipt['reserved_usd'] if receipt.get('tariff_cost_usd') is None else 0,'candidate_path':str((u/r['candidate_path']).relative_to(P)) if r['candidate_path'] else None,'call_receipt':str((r['call_directory']/'receipt.json').relative_to(P)),'artifact_sha256':sha(artifact) if artifact.exists() else None,'law_delivery':'delivered' if complete else 'execution_failed' if r['candidate_path'] else 'not_delivered','provenance_record':m}
   attempts.append(a)
   for p in m.get('parameters',[]):parameters.append({'round':rnd,'version_id':ident,'case_id':r['case_id'],'model_config':r['model_config'],'kind':r['kind'],'parent_version_id':r['parent_version_id'],'law_delivery':a['law_delivery'],**p})
   for s in ss:
    claim=m.get('endpoint_claims',{}).get(s['id'],{});law=claim.get('validated_population_value');mean=s['seed_mean'];ref=s['reference'];rv=ref.get('value')
    supports=[p for p in m.get('parameters',[]) if s['id'] in p.get('analysis_ids',[])]
    q={'round':rnd,'version_id':ident,'case_id':r['case_id'],'model_config':r['model_config'],'kind':r['kind'],'parent_version_id':r['parent_version_id'],'review_disposition':r['review_disposition'],'law_delivery':a['law_delivery'],'category':s['category'],'analysis_id':s['id'],'unit':s['unit'],'available_seeds':s['available_seeds'],'scheduled_seeds':3,'seed_mean':mean,'seed_min':s['seed_range'][0] if s['seed_range'] else None,'seed_max':s['seed_range'][1] if s['seed_range'] else None,'reference_value':rv,'reference_uncertainty':ref.get('uncertainty'),'mean_signed_difference':s.get('mean_signed_difference'),'mean_absolute_difference':s.get('mean_absolute_difference'),'declared_population_value':claim.get('declared_population_value'),'validated_population_value':law,'claim_validation_status':claim.get('validation_status','unassessed'),'claim_note':claim.get('note'),'parameter_ids':[p['parameter_id'] for p in supports],'source_ids':sorted({str(x) for p in supports for x in p.get('source_ids',[])}),'provenance_components':sorted({x for p in supports for x in p.get('provenance_components',[])}),'support_note':('Source anchors and assumptions are layered; categories are not exclusive and do not constitute confidence scores.' if supports else 'No core parameter mapping is supplied for this diagnostic or unavailable attempt; source support remains unassessed.')}
    if isinstance(law,(int,float)) and isinstance(mean,(int,float)) and isinstance(rv,(int,float)):
     q['generated_minus_validated_law']=mean-law;q['validated_law_minus_reference']=law-rv
     assert abs((mean-law)+(law-rv)-(mean-rv))<1e-10
     derivations.append({k:q[k] for k in ['round','version_id','case_id','model_config','kind','analysis_id','unit','seed_mean','validated_population_value','reference_value','generated_minus_validated_law','validated_law_minus_reference','claim_validation_status']}|{'interpretation':'Algebraic decomposition, not causal error attribution. Generated-minus-law includes sampling; law-minus-sample-reference includes scenario and transport/reference differences.'})
    else:q['generated_minus_validated_law']=None;q['validated_law_minus_reference']=None
    summaries.append(q)
   for s in sub:
    for category in ['analyses','diagnostics']:
     for x in s[category]:
      seedrows.append({'round':rnd,'version_id':ident,'case_id':r['case_id'],'model_config':r['model_config'],'kind':r['kind'],'seed':s['seed'],'execution_status':s['execution_status'],'analysis_status':s['analysis_status'],'category':category,'analysis_id':x['id'],'unit':x['unit'],'value':x['value'],'statistic_status':x['status'],'reason':x.get('reason'),'reference_value':x.get('reference',{}).get('value'),'generated_sha256':s['generated_sha256']})
 assert not maps;assert len(attempts)==32 and len(summaries)==192 and len(seedrows)==576
 initial=[a for a in attempts if a['kind']=='initial'];working=[a for a in initial if a['complete_analysis_tables']==3];assert len(initial)==28 and len(working)==20
 residual={}
 for case,aid in [('PNS','residual_correlation'),('lipids','K02-LIPID-RESIDUAL')]:
  chosen=[s for s in summaries if s['kind']=='initial' and s['case_id']==case and s['analysis_id']==aid and s['available_seeds']==3]
  residual[case]={'initial_laws':len(chosen),'below_sample_reference':sum(s['seed_mean']<s['reference_value'] for s in chosen),'min_seed_mean':min(s['seed_mean'] for s in chosen),'max_seed_mean':max(s['seed_mean'] for s in chosen),'reference':chosen[0]['reference_value'],'scope':'Two fixed tasks overall; repeated constructions share source packets and model families.'}
 counts={'api_calls':len(attempts),'initial_attempts':len(initial),'complete_initial_artifacts':sum(a['api_status']=='received' and a['api_artifact_status']=='valid_structure_and_python_ast' for a in initial),'working_initial_laws':len(working),'review_calls':4,'review_retained_noop':sum(a['review_disposition']=='retained_noop' for a in attempts),'review_revised':sum(a['review_disposition']=='revised' for a in attempts),'scheduled_evaluation_tables':96,'successful_evaluation_tables':sum(a['successful_tables'] for a in attempts),'complete_evaluation_tables':sum(a['complete_analysis_tables'] for a in attempts),'additional_diagnostic_tables':6,'primary_analysis_summary_rows':sum(s['category']=='analyses' for s in summaries),'all_analysis_summary_rows':len(summaries),'parameter_records':len(parameters),'validated_law_decomposition_rows':len(derivations),'known_tariff_usd':sum(a['tariff_cost_usd'] or 0 for a in attempts),'unknown_reserve_usd':sum(a['unknown_reserve_usd'] for a in attempts)}
 output={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Retrospective synthesis of two completed whole-cohort pilots; no new API/generator/patient analysis or source-paper authentication','inputs_sha256':inputs,'counts':counts,'sources':sources,'attempts':attempts,'analysis_summaries':summaries,'parameters':parameters,'seed_results':seedrows,'law_reference_decomposition':derivations,'residual_dependence_pattern':residual}
 dump('SYNTHESIS.json',output)
 csvout('ATTEMPTS.csv',[{k:v for k,v in a.items() if k!='provenance_record'} for a in attempts]);csvout('ANALYSIS_RESULTS.csv',summaries);csvout('SEED_RESULTS.csv',seedrows)
 fields=['round','version_id','case_id','model_config','kind','parent_version_id','law_delivery','parameter_id','name','value','unit','source_ids','source_reported_value','source_operator','provenance_components','transformation','transport_assumptions','actual_code_use','locators','analysis_ids','mathematical_note']
 csvout('PARAMETER_SOURCES.csv',[{k:r.get(k) for k in fields} for r in parameters]);csvout('LAW_REFERENCE_DECOMPOSITION.csv',derivations)
 print(json.dumps({'counts':counts,'residual_dependence_pattern':residual},indent=2))
if __name__=='__main__':main()
