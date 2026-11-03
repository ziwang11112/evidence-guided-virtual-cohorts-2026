"""Common evaluation only after all six author sessions are closed."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
U=Path(__file__).resolve().parent
sys.path.insert(0,str(U/'implementation'))
from information_session_v1 import Session
from analysis_feedback import generated_statistics,with_reference,load,sha
from cohort_harness.lifecycle import read_table
ROOT=U.parents[3]/'evcIA'
KEYS=('L01','R01','R02','L02','L03','R03')
def save(p,o):
    with p.open('x',encoding='utf-8') as f:json.dump(o,f,indent=2,allow_nan=False);f.write('\n')
def main():
    sessions={k:Session(ROOT/k) for k in KEYS}
    # Verify closure BEFORE opening the common reference or any final measurements.
    for k,s in sessions.items():
        assert len([e for e in s.selected('feedback') if e['stage']=='final'])==1,k
        assert len([e for e in s.selected('decision')])==1,k
        assert len([e for e in s.selected('handback') if e['stage']=='final'])==1,k
    verification={k:s.verify() for k,s in sessions.items()}
    refpath=ROOT/'R01/b/input/reference_summary.json';ref=load(refpath)
    rows=[];constructors=[]
    for k,s in sessions.items():
        defs=load(ROOT/k/'b/input/analysis_definitions.json')
        for a in s.selected('attempt'):
            result=next((e for e in s.selected('result') if e['attempt_index']==a['index']),
                {'status':'interrupted_or_unresolved','error':'Attempt reserved without a completion record'})
            row={key:a[key] for key in ('run_id','candidate','purpose','stage','phase','seed')}
            row.update(constructor=k,condition=k[0],status=result['status'],error=result.get('error'),elapsed_seconds=result.get('elapsed_seconds'))
            if result['status']=='success':
                output=s.bundle/'executions'/a['run_id']/'output/generated.csv'
                frame=read_table(output,load(s.bundle/'task.json'),output=True)
                row.update(statistics=with_reference(generated_statistics(frame,defs),ref),output_sha256=sha(output),rows=len(frame))
            else:row['statistics']={group:[{'id':i,'value':None,'status':'unavailable'} for i in s.contract[key]] for group,key in [('analyses','analysis_ids'),('diagnostics','diagnostic_ids')]}
            rows.append(row)
        for stage in ('initial','final'):
            part=[r for r in rows if r['constructor']==k and r['stage']==stage and r['purpose']=='delivery']
            assert len(part)==3
            for group in ('analyses','diagnostics'):
                for ident in [r['id'] for r in part[0]['statistics'][group]]:
                    vals=[next(x for x in r['statistics'][group] if x['id']==ident) for r in part]
                    good=[v for v in vals if v['value'] is not None]
                    constructors.append({'constructor':k,'condition':k[0],'stage':stage,'group':group,'id':ident,'n_successful_seeds':len(good),
                        'seed_values':{str(r['seed']):v['value'] for r,v in zip(part,vals)},
                        'values':[v['value'] for v in vals],'mean':float(np.mean([v['value'] for v in good])) if good else None,
                        'range':[min(v['value'] for v in good),max(v['value'] for v in good)] if good else None,
                        'reference':good[0]['reference'] if good else None,
                        'mean_absolute_difference':float(np.mean([abs(v['difference']) for v in good])) if good else None})
    comparisons=[]
    for final in [c for c in constructors if c['stage']=='final']:
        initial=next(c for c in constructors if c['constructor']==final['constructor'] and c['id']==final['id'] and c['stage']=='initial')
        x,y=initial['mean_absolute_difference'],final['mean_absolute_difference']
        matched=[seed for seed,v in initial['seed_values'].items() if v is not None and final['seed_values'].get(seed) is not None]
        reference=final['reference'] if final['reference'] is not None else initial['reference']
        comparisons.append({'constructor':final['constructor'],'id':final['id'],'initial_mean_absolute_difference':x,'final_mean_absolute_difference':y,
            'change':y-x if x is not None and y is not None else None,
            'change_interpretation':'Difference of available-seed means; use matched_seed_changes for matched comparisons',
            'matched_seed_count':len(matched),'matched_seed_ids':matched,
            'matched_seed_changes':{seed:abs(final['seed_values'][seed]-reference)-abs(initial['seed_values'][seed]-reference) for seed in matched}})
    success=[r for r in rows if r['status']=='success']
    report={'unit':'information_revision_ablation_2026-11-03','reference_sha256':sha(refpath),'reference_role':'Exposed CHNS development sample; not new confirmation or population truth',
        'independent_constructors':6,'constructors_per_condition':3,'clinical_cases':1,'raw_patient_reads':0,
        'attempts':len(rows),'delivery_attempts':sum(r['purpose']=='delivery' for r in rows),'trial_attempts':sum(r['purpose']=='trial' for r in rows),
        'successful_tables':len(success),'distinct_table_hashes':len({r['output_sha256'] for r in success}),'failed_attempts':len(rows)-len(success),
        'runs':rows,'constructor_stage_statistics':constructors,'paired_revision_changes':comparisons,'verification':verification}
    save(U/'COMPLETE_RESULTS.json',report)
    print(json.dumps({k:report[k] for k in ('attempts','delivery_attempts','trial_attempts','successful_tables','distinct_table_hashes','failed_attempts')}))
if __name__=='__main__':main()
