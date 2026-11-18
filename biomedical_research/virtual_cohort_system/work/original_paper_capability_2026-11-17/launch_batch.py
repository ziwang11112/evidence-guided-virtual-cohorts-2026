"""Launch at most two independent frozen sessions; never replace a failed author."""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parent

def run(identifier):
    process=subprocess.run([sys.executable,'-B','-X','utf8',str(ROOT/'api_loop.py'),'--episode',identifier],
                           cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    log=ROOT/'launch_logs';log.mkdir(exist_ok=True)
    with (log/(identifier+'.stdout.txt')).open('x',encoding='utf-8') as f:f.write(process.stdout)
    with (log/(identifier+'.stderr.txt')).open('x',encoding='utf-8') as f:f.write(process.stderr)
    return {'episode_id':identifier,'returncode':process.returncode,'summary':process.stdout.strip()[-1800:]}

def main():
    plan=json.loads((ROOT/'PLAN.json').read_text(encoding='utf-8'))
    assert not (ROOT/'BATCH_LAUNCH.json').exists(),'Do not launch the same batch twice'
    with (ROOT/'BATCH_LAUNCH.json').open('x',encoding='utf-8') as f:
        json.dump({'episodes':[e['episode_id'] for e in plan['episodes']],'max_concurrent_sessions':2,'replacement_authors':False},f,indent=2)
    queue=iter(e['episode_id'] for e in plan['episodes']);results=[];stopped=False
    with ThreadPoolExecutor(max_workers=2) as pool:
        active={}
        for _ in range(2):
            identifier=next(queue);print(json.dumps({'started':identifier}),flush=True);active[pool.submit(run,identifier)]=identifier
        while active:
            completed,_=wait(active,return_when=FIRST_COMPLETED)
            for future in completed:
                identifier=active.pop(future)
                try:result=future.result()
                except Exception as error:result={'episode_id':identifier,'returncode':99,'error_type':type(error).__name__}
                results.append(result);print(json.dumps(result),flush=True)
                if result['returncode']!=0:stopped=True
            if not stopped:
                for _ in range(2-len(active)):
                    identifier=next(queue,None)
                    if identifier is None:break
                    print(json.dumps({'started':identifier}),flush=True);active[pool.submit(run,identifier)]=identifier
    with (ROOT/'BATCH_RESULT.json').open('x',encoding='utf-8') as f:
        json.dump({'status':'stopped_nonroutine' if stopped else 'complete','scheduled':6,'closed_processes':len(results),'results':results},f,indent=2)
    if stopped:raise SystemExit(2)

if __name__=='__main__':main()
