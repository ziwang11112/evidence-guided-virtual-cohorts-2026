"""Run exactly the frozen empirical resampling map, without touching generators."""
import csv
import time
from common import *

def main():
    freeze=verify_frozen()
    assert not (HERE/'RUN_STARTED.json').exists(), 'Run already started; inspect existing ledger, do not repeat'
    started=time.monotonic()
    write_new(HERE/'RUN_STARTED.json',dict(created_utc=now(),freeze_sha256=sha(HERE/'FREEZE.json'),max_seconds=MAX_SECONDS))
    records=get_inputs(); frames,_=load_frames(records); pools=make_pools(frames)
    pref=read(HERE/'PREFLIGHT.json'); plan=read(HERE/'STREAM_MAP.json')['streams']
    original=[]; max_delta=0.
    saved={r['dataset_id']:r for r in read(OLD/'ANALYSIS_RESULTS.json')['results']}
    for name,d in frames.items():
        for trait in TRAITS:
            result=analyze_trait(d,trait)
            old=saved[name]['analysis']
            old_trait=next(t for t in old['trait_status'] if t['trait']==trait)
            old_sd=old_trait['sample_sd']
            assert result['n']==old_trait['n'] and abs(result['sample_sd']-old_sd)<1e-9
            max_delta=max(max_delta,abs(result['sample_sd']-old_sd))
            for c in old['contrasts']:
                if c['trait']==trait and c['stratum']=='pooled':
                    delta=abs(result[c['contrast']]-c['raw_estimate'])
                    assert delta<1e-9, (name,trait,c['contrast'],'wrapper disagreement')
                    max_delta=max(max_delta,delta)
            original.append(dict(dataset_id=name,trait=trait,**result))
    with (HERE/'ORIGINAL_ESTIMATES.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(original[0]));w.writeheader();w.writerows(original)
    write_new(HERE/'ORIGINAL_EQUIVALENCE.json',dict(trait_fits=21,contrasts=63,max_abs_difference=max_delta,
        scope='Thin wrapper versus stored closed estimates; original records unchanged'))
    failures=[];done=0;status='complete'
    fields=['trait','replicate','stream','stream_index','dataset_id','status','error','n','sample_sd']+CONTRASTS
    with (HERE/'ESTIMATES.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for slot in plan:
            if time.monotonic()-started>=MAX_SECONDS:
                status='partial_wall_cap';break
            rec={k:slot[k] for k in fields[:5]}
            try:
                sample=sample_pool(pools[slot['trait']][slot['dataset_id']],pref['reference_counts'][slot['trait']],slot['spawn_key'])
                result=analyze_trait(sample,slot['trait'])
                assert result['n']==EXPECTED_N[slot['trait']]
                assert all(np.isfinite(v) for v in result.values())
                rec.update(status='computed',error='',**result)
            except Exception as exc:
                rec.update(status='unavailable',error=type(exc).__name__+': '+str(exc))
                failures.append(rec.copy())
            w.writerow(rec);done+=1
            if done%400==0:
                f.flush()
                progress=dict(completed=done,planned=len(plan),failed=len(failures),elapsed_seconds=round(time.monotonic()-started,2),status='running')
                (HERE/'PROGRESS.json').write_text(json.dumps(progress,indent=2)+'\n',encoding='utf-8')
                print(json.dumps(progress),flush=True)
    verify_frozen()
    result=dict(status=status,created_utc=now(),planned_trait_samples=len(plan),completed_trait_samples=done,
        unavailable=len(failures),computed=done-len(failures),elapsed_seconds=time.monotonic()-started,
        original_verification_trait_fits=21,new_agent_calls=0,new_generated_tables=0,
        individual_resamples_saved=False,estimate_sha256=sha(HERE/'ESTIMATES.csv'),all_bound_inputs_unchanged=True)
    write_new(HERE/'FAILURES.json',failures);write_new(HERE/'RUN_RESULT.json',result)
    print(json.dumps(result),flush=True)

if __name__=='__main__':main()
