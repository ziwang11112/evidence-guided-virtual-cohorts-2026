"""Six-session adapter over the existing durable GPT tool loop; no new transport."""
from pathlib import Path
import argparse, importlib.util, math
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
BASE_PATH=PROJECT/'work/request_only_repeatability_2026-11-11/api_loop.py'
s=importlib.util.spec_from_file_location('p1_durable_api',BASE_PATH);base=importlib.util.module_from_spec(s);s.loader.exec_module(base)
MODEL,KEY_HELPER=base.MODEL,base.KEY_HELPER
read,sha,write_new,contained=base.read,base.sha,base.write_new,base.contained

def config(root,episode_id):
    root=Path(root);plan=read(root/'PLAN.json');model=plan['model'];limits=plan['limits']
    if (model['id'],model['reasoning_effort'],model['service_tier'])!=(MODEL,'high','default'):raise base.IntegrityError('Model config changed')
    maxima={'max_calls':40,'max_output_tokens':16384,'max_input_bytes':500000,'episode_usd_cap':4,'total_usd_cap':24,'max_actions':60}
    for k,m in maxima.items():
        v=limits.get(k)
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<v<=m:raise base.IntegrityError('Invalid budget '+k)
    ids={f'P1_{c}_A{i}' for c in ['PNS','IRON'] for i in range(1,4)}
    if len(plan['episodes'])!=6 or {e['episode_id'] for e in plan['episodes']}!=ids or episode_id not in ids:raise base.IntegrityError('Unexpected session inventory')
    ep=next(e for e in plan['episodes'] if e['episode_id']==episode_id)
    paths={k:contained(root,ep[k]) for k in ['task_path','request_path','policy_path']}
    task_text=paths['task_path'].read_text(encoding='utf-8');task=base.decode(task_text)
    instructions=contained(root,plan['common_instructions_path']).read_text(encoding='utf-8')+'\n'+paths['policy_path'].read_text(encoding='utf-8')
    content=[{'type':'input_text','text':paths['request_path'].read_text(encoding='utf-8')},
             {'type':'input_text','text':'Task/output contract:\n'+task_text}]
    rates={k:model[k] for k in base.DEFAULT_RATES}
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in rates.values()):raise base.IntegrityError('Invalid tariff')
    return plan,ep,task,instructions,[{'role':'user','content':content}],rates

def external_files():
    prior=PROJECT/'work'
    files=[BASE_PATH,prior/'request_only_repeatability_2026-11-11/tools_runtime.py',
      prior/'lifestyle_application_2026-11-11/tools_runtime.py',prior/'iron_evidence_content_control_2026-11-16/analysis_adapter.py',
      prior/'iron_breadth_2026-11-05/evaluation/analyze.py',prior/'iron_breadth_2026-11-05/evaluation/independent.py',
      prior/'cross_model_api_pilot_2026-11-10/execute_pilot.py',prior/'cross_model_api_pilot_2026-11-10/analyze_pilot.py',
      prior/'next_case_validation_2026-11-09/runtime/analysis_tools.py',
      prior/'request_only_repeatability_2026-11-11/review/recompute_saved_tables.py']
    return files+list((PROJECT/'cohort_harness').rglob('*.py'))

def local_files(plan):
    names={'PLAN.json','api_loop.py','tools_runtime.py','prepare.py','PROTOCOL.md','SOURCE_BINDINGS.json','SOURCE_TRANSFORMATION.json',
      'TARIFF_VERIFICATION.json','MODEL_AVAILABILITY.json','PREFLIGHT_REVIEW.json','pipeline.py','test_adapter.py','TEST_RECEIPT.json',plan['common_instructions_path']}
    names.update(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'private_sources').glob('*') if p.is_file())
    for ep in plan['episodes']:
        names.update(ep[k] for k in ['task_path','request_path','policy_path'])
        names.add(f'requests/{ep["case_id"]}_analyses.json')
    return names

def verify_live_gate(root,plan):
    root=Path(root);f=read(root/'LAUNCH_FREEZE.json');r=read(root/'PREFLIGHT_REVIEW.json');a=read(root/'ROOT_EXECUTION_APPROVAL.json')
    if r['status']!='pass' or not local_files(plan)<=set(f['files']):raise base.IntegrityError('Incomplete freeze/review')
    for n,h in f['files'].items():
        if sha(contained(root,n))!=h:raise base.IntegrityError('Frozen local changed: '+n)
    if r['reviewed_files']!={n:h for n,h in f['files'].items() if n!='PREFLIGHT_REVIEW.json'}:raise base.IntegrityError('Review bytes differ')
    required={p.resolve().as_posix() for p in external_files()}
    if not required<=set(f['external_files']) or r['reviewed_external_files']!=f['external_files']:raise base.IntegrityError('External review incomplete')
    for n,h in f['external_files'].items():
        if sha(Path(n))!=h:raise base.IntegrityError('Frozen external changed')
    if f['credential_helper_sha256']!=sha(KEY_HELPER) or r['credential_helper_sha256']!=f['credential_helper_sha256']:raise base.IntegrityError('Credential helper changed')
    if a.get('status')!='approved' or a['launch_freeze_sha256']!=sha(root/'LAUNCH_FREEZE.json') or a['plan_sha256']!=sha(root/'PLAN.json') or a['files']!=f['files'] or set(a['episodes'])!={e['episode_id'] for e in plan['episodes']}:raise base.IntegrityError('Launch approval incomplete')

def verify_dispatch_gate(root,plan,episode):
    for ep in plan['episodes']:
        p=Path(root)/'episodes'/ep['episode_id']/'OUTCOME.json'
        if p.exists() and read(p)['status'] not in base.ORDINARY_TERMINAL:raise base.IntegrityError('Prior nonroutine outcome needs explicit engineering decision')

base.config=config;base.verify_live_gate=verify_live_gate;base.verify_dispatch_gate=verify_dispatch_gate
def main():
    p=argparse.ArgumentParser();p.add_argument('--episode',required=True);a=p.parse_args()
    result=base.run_episode(a.episode,root=ROOT)
    print(base.json.dumps({k:result.get(k) for k in ['episode_id','status','selected_candidate','calls_receipted','known_tariff_cost_usd','accounted_usd','unknown_usage_calls']}),flush=True)
    if result['status'] not in base.ORDINARY_TERMINAL:raise SystemExit(2)
if __name__=='__main__':main()
