"""Bounded independent preflight. No API, generator execution or patient rows."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / 'request_only_repeatability_2026-11-11'
sys.path.insert(0, str(ROOT))
import api_loop
import tools_runtime


def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')


def main():
    checks=[]
    def ok(name, condition):
        checks.append({'name':name,'passed':bool(condition)})
        if not condition: raise AssertionError(name)
    def rejects(name, fn):
        try: fn()
        except (ValueError, api_loop.IntegrityError, OSError): ok(name, True)
        else: ok(name, False)
    plan=read(ROOT/'PLAN.json')
    mapping=read(ROOT/'_host_only/IMPORT_MAPPING.json')
    oldplan=read(OLD/'PLAN.json')
    ok('24 episodes, 12 pairs, 6 blocks',len(plan['episodes'])==24 and len(mapping['pairs'])==12 and {r['block'] for r in plan['episodes']}==set(range(1,7)))
    ok('all twelve original laws included', {r['old_episode_id'] for r in mapping['pairs']}=={e['episode_id'] for e in oldplan['episodes']})
    ok('original plan and closure bound', mapping['old_plan_sha256']==sha(OLD/'PLAN.json') and mapping['old_construction_closure_sha256']==sha(OLD/'CONSTRUCTION_CLOSURE.json'))
    ok('same seeds as original',plan['evaluation_seeds']==oldplan['evaluation_seeds'])
    req=read(ROOT/'analysis_requirements.json')
    all_inputs=[]
    for pair in mapping['pairs']:
        ep=[e for e in plan['episodes'] if e['pair_id']==pair['pair_id']]
        ok(pair['pair_id']+' exact paired policies',{e['arm'] for e in ep}=={'generic','structured'} and len(ep)==2)
        a=api_loop.config(ROOT, ep[0]['episode_id']); b=api_loop.config(ROOT,ep[1]['episode_id'])
        ok(pair['pair_id']+' identical initial messages', a[4]==b[4])
        ok(pair['pair_id']+' only policy instructions differ',a[2]==b[2] and a[5]==b[5] and a[3]!=b[3])
        ok(pair['pair_id']+' analysis semantics bound', all(e['analysis_requirements']==req[e['case_id']] for e in ep))
        for e in ep:
            ok(e['episode_id']+' analysis IDs exact',e['requested_analysis_ids']==[x['analysis_id'] for x in req[e['case_id']]])
            ok(e['episode_id']+' same imported package',e['imported_package_path']==pair['package_path'])
        package_path=ROOT/pair['package_path'];package=read(package_path)
        ok(pair['pair_id']+' package manifest hash',sha(package_path)==pair['package_sha256'])
        original=OLD/pair['old_candidate_relative_path']
        ok(pair['pair_id']+' original manifest bound',sha(original/'manifest.json')==package['candidate_manifest_sha256_original']==pair['old_manifest_sha256'])
        for name in ['generator.py','model_spec.json','notes.json']:
            ok(pair['pair_id']+' original byte parity '+name,(package_path.parent/name).read_bytes()==(original/name).read_bytes())
        expected={'generator.py','model_spec.json','notes.json'}|{m['path'] for m in package['sources'].values()}
        ok(pair['pair_id']+' import exact whitelist',set(package['files'])==expected)
        for name,h in package['files'].items():
            p=api_loop.contained(package_path.parent,name)
            ok(pair['pair_id']+' imported hash '+name,sha(p)==h)
        for sid,m in package['sources'].items():
            ok(pair['pair_id']+' source version/hash '+sid,m['sha256']==m['xml_sha256']==package['files'][m['path']] and type(m['version']) is int)
        text=json.dumps(a[4],ensure_ascii=False)
        for forbidden in ['EVALUATION.json','REFERENCE_SNAPSHOT.json','SCIENTIFIC_PROVENANCE_AUDIT','INITIAL_STATIC_SCREEN','FINAL_TABLES.json','PRIMARY_ANALYSES']:
            ok(pair['pair_id']+' no host report filename '+forbidden,forbidden not in text)
        all_inputs.append(a[4])
    for case in ['PNS','LIPID']:
        new_task=read(ROOT/'tasks'/f'{case}.json');old_task=read(OLD/'tasks'/f'{case}.json')
        ok(case+' scientific task fields preserved',{k:v for k,v in new_task.items() if k!='budget'}=={k:v for k,v in old_task.items() if k!='budget'})
        ok(case+' only revision budget metadata changed',new_task['budget']=={'source_queries':8,'source_downloads':6,'revisions':3})
        ok(case+' request bytes preserved',(ROOT/'requests'/f'{case}.txt').read_bytes()==(OLD/'requests'/f'{case}.txt').read_bytes())
    lim=plan['limits']
    for name,value in {'max_calls':24,'max_actions':24,'max_queries':8,'max_downloads':6,'max_candidates':3,'max_runs':3,'episode_usd_cap':2,'total_usd_cap':48}.items():
        ok('bounded budget '+name,lim[name]==value)
    ok('no paid calls before preflight', not (ROOT/'episodes').exists() or not list((ROOT/'episodes').glob('*/calls/*/reservation.json')))
    ok('no evaluator read in tool runtime source', 'REFERENCE_SNAPSHOT' not in (ROOT/'tools_runtime.py').read_text() and 'EVALUATION.json' not in (ROOT/'tools_runtime.py').read_text())
    oldfreeze=read(OLD/'LAUNCH_FREEZE.json')
    external=dict(oldfreeze['external_files'])
    external[(OLD/'tools_runtime.py').as_posix()]=sha(OLD/'tools_runtime.py')
    for path,h in external.items():ok('pinned external '+str(Path(path).relative_to(ROOT.parents[1])),sha(path)==h)
    ok('old v0.29 remains unchanged',sha(ROOT.parents[1]/'manuscript/DRAFT_v0_29.md')=='ba5e5704a5537c5c9483fd3b6b85266f849cf7f41781d21255b3716626963506')
    ok('old repeatability plan unchanged',sha(OLD/'PLAN.json')=='ec1115c2df2ee6a4be3c320bf690893325870561474418661f4c813faec20152')
    for name,h in read(ROOT/'BASELINE_BINDINGS.json')['files'].items():ok('evaluator-only baseline hash '+name,sha(OLD/name)==h)
    # Verify per-request reservation feasibility without dispatching or loading credentials.
    maximum_initial_reserve=0
    for ep in plan['episodes']:
        _,_,_,instructions,initial,rates=api_loop.config(ROOT,ep['episode_id'])
        body=api_loop.request_body(instructions,initial,tools_runtime.TOOL_DEFINITIONS,lim)
        n=len(api_loop.encoded(body));allowance=n+4096
        inf,outf=(2.,1.5) if allowance>api_loop.LONG_CONTEXT_THRESHOLD else (1.,1.)
        reserve=(allowance*max(rates['input_rate'],rates['cache_write_rate'],rates['cached_rate'])*inf+lim['max_output_tokens']*rates['output_rate']*outf)/1e6
        maximum_initial_reserve=max(maximum_initial_reserve,reserve)
        ok(ep['episode_id']+' initial request within bytes and cost',n<=lim['max_input_bytes'] and reserve<=lim['episode_usd_cap'])
        ok(ep['episode_id']+' shared tool set',body['tools']==tools_runtime.TOOL_DEFINITIONS and body['parallel_tool_calls'] is False)
    # Isolated counterexample checks on actual mathematical scanner, not actual generators.
    fixtures={
      'positive_nested': 'import numpy as np\ndef generate(observed,spec,seed):\n r=np.random.default_rng(seed)\n b=12+np.exp(r.normal(size=3))\n return np.exp(.02*b)\n',
      'negative_nested': 'import numpy as np\ndef generate(observed,spec,seed):\n r=np.random.default_rng(seed)\n b=r.lognormal(size=3)\n return np.exp(-.02*b)\n',
      'clipped_input': 'import numpy as np\ndef generate(observed,spec,seed):\n r=np.random.default_rng(seed)\n b=np.clip(r.lognormal(size=3),1,10)\n return np.exp(.02*b)\n'}
    results={k:tools_runtime.checks.inspect_program(v) for k,v in fixtures.items()}
    ok('generic nested positive pattern signalled',any(f['code']=='EXP_OF_HEAVY_TAINT' for f in results['positive_nested']['findings']))
    ok('negative pattern never labelled theorem',all(f['proof'] is False for f in results['negative_nested']['findings']))
    ok('literal cap remains noncertifying',results['clipped_input']['mathematical_validity']=='not_certified' and any(f['code']=='FINITE_LITERAL_CLIP' for f in results['clipped_input']['findings']))
    # Artificial unavailable-output evaluator fixture: no model, sampler or target.
    fixture=ROOT/'review'/'offline_evaluator_fixture'
    fixture.mkdir(exist_ok=False)
    unit=fixture/'new_unit';unit.mkdir()
    write(unit/'PLAN.json',plan)
    spec=importlib.util.spec_from_file_location('independent_revision_evaluator',ROOT/'evaluate_pilot.py')
    evaluator=importlib.util.module_from_spec(spec);sys.modules[spec.name]=evaluator;spec.loader.exec_module(evaluator)
    evaluator.ROOT=unit
    for ep in plan['episodes'][:-1]:
        write(unit/'episodes'/ep['episode_id']/'OUTCOME.json',dict(episode_id=ep['episode_id'],status='budget_limit',selected_candidate=None,calls_reserved=0,known_tariff_cost_usd=0,accounted_usd=0))
    rejects('23 closed branches cannot close24',evaluator.close)
    ok('failed partial closure writes no seal',not (unit/'CONSTRUCTION_CLOSURE.json').exists())
    ep=plan['episodes'][-1]
    write(unit/'episodes'/ep['episode_id']/'OUTCOME.json',dict(episode_id=ep['episode_id'],status='budget_limit',selected_candidate=None,calls_reserved=0,known_tariff_cost_usd=0,accounted_usd=0))
    evaluator.close();slots=evaluator.draw()
    ok('24 closed branches retain72 planned missing slots',len(slots)==72 and all(s['status']=='unavailable' and s['candidate_id'] is None for s in slots))
    fake_ref={'value':1.0,'unit':'artificial_fixture_only'}
    fake_snapshot=fixture/'FAKE_REFERENCE.json';write(fake_snapshot,{'references':{'PNS':{'probe':fake_ref},'lipids':{'probe':fake_ref}}})
    evaluator.SNAPSHOT=fake_snapshot;evaluator.SNAPSHOT_SHA=sha(fake_snapshot)
    fake_old=fixture/'request_only_repeatability_2026-11-11';fake_old.mkdir()
    fake_summary=[{'episode_id':m['old_episode_id'],'analysis_id':'probe','reference':fake_ref,'unit':fake_ref['unit'],'mean':2.0,'available_seeds':3} for m in mapping['pairs']]
    write(fake_old/'EVALUATION.json',{'summaries':fake_summary})
    write(unit/'BASELINE_BINDINGS.json',{'files':{'EVALUATION.json':sha(fake_old/'EVALUATION.json')}})
    write(unit/'_host_only/IMPORT_MAPPING.json',mapping)
    result=evaluator.evaluate();out=read(unit/'EVALUATION.json')
    ok('missing outputs not imputed from initial laws',result['counts']['unavailable_tables']==72 and all(r['final_mean'] is None and r['change_in_mean'] is None for r in out['paired_initial_comparison']['rows']))
    ok('all24 branches retained in paired comparison',len(out['paired_initial_comparison']['rows'])==24 and len(out['paired_initial_comparison']['artifact_changes'])==24)
    # Existing owner tests exercise mocked runtime and tampered staged artifacts;
    # no duplication of those suite runs is needed here.
    out={'status':'pass','created_utc':datetime.now(timezone.utc).isoformat(),
       'checks':checks,'checks_passed':len(checks),'maximum_initial_reserved_usd':maximum_initial_reserve,
       'api_calls':0,'generator_executions':0,'patient_rows_read':0,
       'old_full_suites_rerun':False,'external_files':external,
       'fixture_note':'Artificial evaluator fixture contains no patient or generated model rows; sentinel references are not study evidence.'}
    write(ROOT/'review/INDEPENDENT_OFFLINE_CHECKS.json',out)
    print(json.dumps({'status':'pass','checks':len(checks),'maximum_initial_reserved_usd':maximum_initial_reserve}))


if __name__=='__main__':main()
