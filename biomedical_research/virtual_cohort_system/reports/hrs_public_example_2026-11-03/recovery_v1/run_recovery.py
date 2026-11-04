"""Exactly three additional source-parser-repair deliveries; no Agent rerun."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
import time

R = Path(__file__).resolve().parent
U = R.parent
P = U.parents[1]
sys.path.insert(0,str(P))
from cohort_harness.lifecycle import verify_candidate
from cohort_harness.execution import run_candidate,verify_execution,DEFAULT_RUNTIME

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def put(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:
        json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def wsl(p):
    s=str(Path(p).resolve()).replace('\\','/')
    return '/mnt/'+s[0].lower()+s[2:]
def verify():
    v=read(R/'RELEASE.json')
    assert v['execution_released'] is True
    assert v['additional_attempts_allowed']==3 and v['seeds']==[6101,6102,6103]
    assert v['original_release_sha256']==sha(U/'RELEASE.json')
    for path,digest in v['files'].items(): assert sha(R/path)==digest,path
    verify_candidate(R/'bundle','candidates/native_corrected')
    for arm in ['agent','native']: verify_candidate(U/'bundle','candidates/'+arm)
    return v
def main():
    verify()
    slots=[]
    for seed in [6101,6102,6103]:
        name=f'native_corrected_{seed}'; reserve=R/'attempts'/(name+'.reserved.json'); final=R/'attempts'/(name+'.json')
        if final.exists(): slots.append(read(final));continue
        if reserve.exists(): raise RuntimeError('Interrupted reservation: inspect, never repeat '+name)
        verify();put(reserve,{'run_id':name,'seed':seed,'created_utc':now(),'release_sha256':sha(R/'RELEASE.json')})
        result={'run_id':name,'seed':seed,'arm':'native','created_utc':now()}
        try:
            receipt=run_candidate(R/'bundle','candidates/native_corrected',name,seed,
                runtime=DEFAULT_RUNTIME,timeout_seconds=120,memory_mb=1024,output_bytes=30000000,log_bytes=100000)
            verify_execution(R/'bundle',name)
            result.update(status=receipt['status'],error=receipt['error'],elapsed_seconds=receipt['elapsed_seconds'],
                execution_sha256=sha(R/'bundle/executions'/name/'execution.json'))
        except Exception as error:
            result.update(status='controller_error',error=str(error))
        put(final,result);slots.append(result)
        print(json.dumps({'generation':name,'status':result['status']}),flush=True)
    if not (R/'GENERATION_CLOSED.json').exists():
        put(R/'GENERATION_CLOSED.json',{'created_utc':now(),'slots':slots,'attempts_spent':3,
            'initial_attempts_spent':6,'total_physical_attempts':9,
            'release_sha256':sha(R/'RELEASE.json'),
            'attempt_bindings':{x['run_id']:sha(R/'attempts'/(x['run_id']+'.json')) for x in slots}})
    closure=read(R/'GENERATION_CLOSED.json')
    assert [x['run_id'] for x in closure['slots']]==[f'native_corrected_{s}' for s in [6101,6102,6103]]
    assert [x['seed'] for x in closure['slots']]==[6101,6102,6103]
    assert set(closure['attempt_bindings'])=={f'native_corrected_{s}' for s in [6101,6102,6103]}
    assert closure['release_sha256']==sha(R/'RELEASE.json') and closure['attempts_spent']==3
    for slot in closure['slots']:
        name=slot['run_id'];verify()
        assert sha(R/'attempts'/(name+'.json'))==closure['attempt_bindings'][name]
        attempt=read(R/'attempts'/(name+'.json'))
        reservation=read(R/'attempts'/(name+'.reserved.json'))
        assert attempt==slot and slot['arm']=='native'
        assert reservation['run_id']==name and reservation['seed']==slot['seed']
        assert reservation['release_sha256']==sha(R/'RELEASE.json')
        reserve=R/'results'/(name+'.reserved.json');final=R/'results'/(name+'.evaluation.json')
        if final.exists():continue
        if reserve.exists():raise RuntimeError('Interrupted evaluation: do not repeat '+name)
        native=R/'results'/(name+'.native.json'); gls=R/'results'/(name+'.gls.json')
        assert not native.exists() and not gls.exists()
        put(reserve,{'run_id':name,'created_utc':now(),'closure_sha256':sha(R/'GENERATION_CLOSED.json')})
        result={'run_id':name,'arm':'native','seed':slot['seed'],'fit_attempts':0,'started_utc':now()}
        try:
            if slot['status']!='success':result['status']='not_evaluable'
            else:
                receipt=verify_execution(R/'bundle',name)
                assert receipt['status']=='success' and receipt['candidate']=='candidates/native_corrected'
                assert receipt['limits']['seed']==slot['seed']
                assert sha(R/'bundle/executions'/name/'execution.json')==slot['execution_sha256']
                table=R/'bundle/executions'/name/'output/generated.csv'
                result.update(fit_attempts=1,input_sha256=sha(table));started=time.monotonic()
                done=subprocess.run(['wsl.exe','-d','Ubuntu-24.04','--','python3',wsl(U/'evaluation/run_r.py'),
                    wsl(U/'evaluation/native_evaluate.R'),wsl(table),wsl(native)],capture_output=True,timeout=325)
                (R/'results'/(name+'.stdout.log')).write_bytes(done.stdout)
                (R/'results'/(name+'.stderr.log')).write_bytes(done.stderr)
                result.update(returncode=done.returncode,elapsed_seconds=time.monotonic()-started)
                value=read(native) if native.exists() else None
                if value: assert value['input_sha256']==sha(table)
                result['status']=value['status'] if value else 'no_output'
                if done.returncode!=0 and result['status']=='computed':result['status']='process_failed_partial'
                if native.exists():result['native_json_sha256']=sha(native)
                if result['status']=='computed':
                    try:
                        check=subprocess.run([sys.executable,str(U/'evaluation/independent_gls.py'),
                            '--input-csv',str(table),'--native-json',str(native),'--output-json',str(gls)],capture_output=True,timeout=120)
                        result['gls_returncode']=check.returncode
                        result['gls_status']=read(gls)['status'] if gls.exists() else 'no_output'
                        if check.returncode!=0 and result['gls_status']=='pass':result['gls_status']='process_failed_partial'
                        if gls.exists():result['gls_json_sha256']=sha(gls)
                    except Exception as error:result.update(gls_status='failed_no_retry',gls_error=str(error))
        except Exception as error:result.update(status='failed_no_retry',error={'type':type(error).__name__,'message':str(error)})
        finally:
            result['finished_utc']=now();put(final,result)
        print(json.dumps({'evaluation':name,'status':result['status'],'gls':result.get('gls_status')}),flush=True)
    put(R/'CLOSED.json',{'created_utc':now(),'additional_attempts_spent':3,'no_further_recovery':True})

if __name__=='__main__':main()
