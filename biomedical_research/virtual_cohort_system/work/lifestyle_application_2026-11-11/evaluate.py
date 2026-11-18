"""One analysis entry point for reference and every predeclared final table."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
import pandas as pd
import analysis_operator as op
import reference_adapter as ra
import sample_final as sf
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False)
def main():
    sf.launch.verify_live_gate(R,read(R/'PLAN.json'));sf.verify()
    inventory=read(R/'FINAL_TABLES.json')
    assert inventory['construction_closure_sha256']==sha(R/'CONSTRUCTION_CLOSURE.json')
    assert len(inventory['slots'])==6
    reference=R.parent/'scaleup_2026-11-01/private_data/22Jul20_for_Dryad_noIDs.txt'
    targets=[dict(dataset_id='real',kind='real_reference',path=reference,sha256=ra.EXPECTED_SHA)]
    for s in inventory['slots']:
        targets.append(dict(dataset_id=s['episode_id']+'_s'+str(s['seed']),kind='virtual',episode_id=s['episode_id'],seed=s['seed'],status=s['status'],
            path=R/s['generated_path'] if s['status']=='success' else None,sha256=s.get('generated_sha256'),error=s.get('error')))
    bindings={n:sha(R/n) for n in ['analysis_operator.py','reference_adapter.py','evaluate.py','FINAL_TABLES.json','CONSTRUCTION_CLOSURE.json']}
    for t in targets:
        if t['path']:assert sha(t['path'])==t['sha256']
    write(R/'EVALUATION_INPUTS.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),files=bindings,inputs=[{**t,'path':str(t['path']) if t['path'] else None} for t in targets]))
    results=[]
    for t in targets:
        rec={k:v for k,v in t.items() if k!='path'}
        if not t['path']:results.append(rec);continue
        try:
            if t['kind']=='real_reference':frame,exclusions=ra.load_reference(t['path']);rec['reference_exclusions']=exclusions
            else:frame=pd.read_csv(t['path'],dtype={'id':str})
            stats=op.analyze_frame(frame)
            # Pure operator reads neither files nor target; the runner records reference access.
            rec['analysis']=stats;rec['status']='computed'
            scale={q['trait']:q['sample_sd'] for q in stats['trait_status']}
            for c in stats['contrasts']:
                if c['status']=='computed':
                    for key in ['estimate','se','lower','upper']:c['raw_'+key]=c[key]*scale[c['trait']]
                    c['raw_unit']='kg/m2' if c['trait']=='bmi' else 'mg/dL'
        except Exception as e:rec.update(status='failed',error=dict(type=type(e).__name__,message=str(e)))
        results.append(rec)
    write(R/'ANALYSIS_RESULTS.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),target_reference_read=True,results=results))
    rows=[]
    for r in results:
        contrasts=r.get('analysis',{}).get('contrasts',[])
        if not contrasts:
            contrasts=[dict(trait=t,stratum=s,contrast=c,status='unavailable',reason=r.get('error',r.get('status')))
                       for t in op.TRAITS for s in ['pooled','F','M'] for c,_ in op.CONTRASTS]
        for c in contrasts:rows.append(dict(dataset_id=r['dataset_id'],kind=r['kind'],**c))
    pd.DataFrame(rows).to_csv(R/'ANALYSIS_CONTRASTS.csv',index=False)
    assert all(sha(R/n)==h for n,h in bindings.items())
    assert all(not t['path'] or sha(t['path'])==t['sha256'] for t in targets),'Analysis input changed'
    print(json.dumps(dict(datasets=len(results),computed=sum(r['status']=='computed' for r in results),contrast_rows=len(rows),reference_read=True)))
if __name__=='__main__':main()
