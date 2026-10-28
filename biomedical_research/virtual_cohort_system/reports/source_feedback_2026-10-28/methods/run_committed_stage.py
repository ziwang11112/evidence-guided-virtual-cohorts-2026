"""Controller only: run fixed protocol seeds, never alter scientific settings."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

project = Path(__file__).resolve().parents[2]
bundle, name, phase = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
assert name in {'initial', 'final'} and phase in {'source', 'target'}
protocol = json.loads((bundle/'protocol.json').read_text(encoding='utf-8'))
logs = bundle/'controller_runs'
logs.mkdir(exist_ok=True)
runtime = project/'work/m2-runtime-config.json'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def command(label, args):
    record = logs/(label+'.json')
    if record.exists(): raise RuntimeError('Controller log already exists: '+label)
    result = subprocess.run([sys.executable,'-m','cohort_harness',*args], cwd=project,
                            capture_output=True,text=True,encoding='utf-8',errors='replace')
    payload = {'args':args,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    record.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    if result.returncode: raise RuntimeError('Failed '+label+'; inspect retained log')
    return json.loads(result.stdout)
base=['--bundle',str(bundle)]
command(name+'_'+phase+'_verify_candidate',['verify',*base,'--candidate',name])
if phase=='source':
    replay_id=name+'_feedback'
    result=command(name+'_source_replay',['source-replay',*base,'--candidate',name,
        '--replay-id',replay_id,'--seed',str(protocol['source_seed']),'--runtime',str(runtime)])
    command(name+'_source_verify',['verify-source-replay',*base,'--replay-id',replay_id,'--candidate',name])
    rows=[{'context':c['id'],'id':v['id'],'status':v['status'],'reported':v.get('reported_value'),
           'value':v.get('value'),'difference':v.get('difference'),'n_used':v.get('n_used'),
           'generation_link_verified':v['generation_link_verified']}
          for c in result['contexts'] for v in c['checks']]
    summary={'candidate':name,'phase':'source','status':result['status'],
        'report_path':str(bundle/'source_replays'/replay_id/'replay.json'),
        'report_sha256':sha(bundle/'source_replays'/replay_id/'replay.json'),'checks':rows}
else:
    rows=[]
    for seed in protocol['target_seeds']:
        run_id=name+'_seed_'+str(seed)
        result=command(run_id,['execute',*base,'--candidate',name,'--run-id',run_id,
                              '--seed',str(seed),'--runtime',str(runtime)])
        command(run_id+'_verify',['verify-execution',*base,'--run-id',run_id])
        output=bundle/'executions'/run_id/'output/generated.csv'
        rows.append({'label':run_id,'stage':name,'seed':seed,'path':str(output),
                     'sha256':sha(output),'status':result['status'],
                     'execution_sha256':sha(bundle/'executions'/run_id/'execution.json')})
    summary={'candidate':name,'phase':'target_outputs_only','outputs':rows,
             'reference_results_read':False,'candidate_freeze_sha256':sha(bundle/'candidates'/name/'freeze.json')}
destination=logs/(name+'_'+phase+'_summary.json')
with destination.open('x',encoding='utf-8') as stream: json.dump(summary,stream,indent=2,allow_nan=False)
print(json.dumps(summary,indent=2,allow_nan=False))
