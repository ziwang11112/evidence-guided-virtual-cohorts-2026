"""Independent, read-only postrun audit of frozen source execution.

Never imports a generator, generates a production cohort, or opens reference rows.
Run directories are inspected only after candidate_manifest.json exists.
"""
from pathlib import Path
import ast
import collections
import datetime as dt
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] / 'stage1'

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run_audit():
    checks, runs, deferred = [], [], []
    def check(name, ok, detail=None):
        checks.append({'check': name, 'passed': bool(ok), 'detail': detail})
    freeze = read(ROOT/'protocol_freeze.json')
    protocol = read(ROOT/'protocol.json')
    freeze_sha = sha(ROOT/'protocol_freeze.json')
    for rel, digest in freeze['files'].items():
        if rel.startswith('custodian/'):
            deferred.append(rel)
            continue
        check('protocol_hash:'+rel, sha(ROOT/rel)==digest)
    manifests = sorted(list((ROOT/'runs').rglob('candidate_manifest.json')) + list((ROOT/'statistical').rglob('candidate_manifest.json')))
    for mp in manifests:
        run = mp.parent
        cm = read(mp)
        task = read(run/'task.json')
        rid = task['run_id']
        check(rid+':candidate_protocol', cm['protocol_sha256']==freeze_sha)
        check(rid+':candidate_task', cm['task']==task)
        check(rid+':candidate_valid', cm['status']=='valid')
        for rel, digest in cm['files'].items():
            check(rid+':candidate_hash:'+rel, sha(run/rel)==digest)
        lock = read(run/'staging_lock.json')
        check(rid+':staging_protocol', lock['protocol_sha256']==freeze_sha)
        for rel, digest in lock['files'].items():
            check(rid+':staging_hash:'+rel, sha(run/rel)==digest)
        case = task['case_id']
        for rel in ['evidence.json','schema.json']:
            check(rid+':packet_equality:'+rel, sha(run/rel)==sha(ROOT/'packets'/case/rel))
        check(rid+':checker_equality', sha(run/'source_checks.py')==sha(ROOT/'source_checks.py'))
        dec=read(run/'decision.json')
        fb=read(run/'source_feedback.json')
        ids=[s['id'] for s in dec['scenarios']]
        allocation=dict(zip(ids, {1:[20],2:[10,10],3:[7,7,6]}[len(ids)]))
        check(rid+':declared_allocation', all(s['n_cohorts']==allocation[s['id']] for s in dec['scenarios']))
        check(rid+':source_feedback_valid', fb['status']=='valid' and not fb['errors'] and fb['target_results_loaded'] is False)
        observed={(x['context'],x['seed']) for x in fb['checks']}
        expected={(context,seed) for context in ids for seed in protocol['source_check_seeds']}
        check(rid+':controller_checks_complete', observed==expected and len(fb['checks'])==len(expected))
        check(rid+':input_use_probes', len(fb.get('input_use_probes',[]))==len(ids) and all(x['mean_perturbation_changes_output'] for x in fb.get('input_use_probes',[])))
        log=dec['calibration_log']
        structures=log['examined_structures']; retained=set(log['final_scenario_to_structure'].values())
        allowance=3 if task['branch']=='initial' else 9
        actual=maximal=0
        for st in structures:
            seeds=st['source_seeds_evaluated']
            actual+=len(seeds)
            maximal+=len(set(seeds)|set(protocol['source_check_seeds'])) if st['id'] in retained else len(set(seeds))
            check(rid+':logged_seed_set:'+st['id'], len(set(seeds))==len(seeds) and set(seeds)<=set(protocol['source_check_seeds']))
        check(rid+':candidate_budget', len(structures)<=(1 if task['branch']=='initial' else 3) and maximal<=allowance)
        check(rid+':final_map', set(log['final_scenario_to_structure'])==set(ids) and retained<={s['id'] for s in structures})
        source=(run/'generator.py').read_text(encoding='utf-8-sig'); tree=ast.parse(source)
        imports=[]; calls=[]
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): imports.extend(a.name for a in node.names)
            if isinstance(node, ast.ImportFrom): imports.append(node.module)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name): calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute): calls.append(ast.unparse(node.func))
        prohibited={'open','eval','exec','compile','__import__','input','breakpoint'}
        suspicious=[x for x in calls if x in prohibited or any(k in x.lower() for k in ['read_csv','read_json','read_pickle','read_excel','read_parquet','fromfile','to_csv','tofile','urlopen','request','socket','subprocess','system','getattr','globals','locals'])]
        check(rid+':static_no_obvious_hidden_io', not suspicious, suspicious)
        if task.get('parent'):
            parent=run.parent/'initial_v3'
            check(rid+':parent_manifest', sha(parent/'candidate_manifest.json')==task['parent']['manifest_sha256'])
            for rel,key in [('generator.py','generator_sha256'),('decision.json','decision_sha256'),('source_feedback.json','source_feedback_sha256')]:
                check(rid+':parent_copy:'+rel, sha(run/'parent'/rel)==sha(parent/rel)==task['parent'][key])
        row={'run_id':rid,'path':str(run.relative_to(ROOT)).replace('\\','/'),'branch':task['branch'],'case':case,'lineage':task['lineage_id'],
             'candidate_sha256':sha(mp),'generator_sha256':sha(run/'generator.py'),'candidate_time':cm['created_utc'],
             'action':dec['action'],'scenarios':dec['scenarios'],'changes_from_parent':dec['changes_from_parent'],
             'calibration_log':log,'builder_logged_unique_checks':actual,'controller_union_unique_checks':maximal,
             'source_diagnostic_cells':sum(len(x['diagnostics']) for x in fb['checks']),
             'outside_descriptive_envelope':sum(not x['within_source_diagnostic_envelope'] for d in fb['checks'] for x in d['diagnostics']),
             'imports':sorted(set(imports)),'calls':sorted(set(calls)), 'source_lines':len(source.splitlines()),
             'final_exists':(run/'final/manifest.json').exists()}
        if row['final_exists']:
            fm=read(run/'final/manifest.json')
            check(rid+':final_candidate_hash', fm['candidate_manifest_sha256']==sha(mp))
            check(rid+':final_task', fm['task']==task)
            check(rid+':final_allocation', fm['scenario_allocation']==allocation)
            check(rid+':final_seed_order', [x['seed'] for x in fm['records']]==protocol['final_seeds'][case])
            check(rid+':final_requested', fm['cohorts_requested']==len(fm['records'])==20)
            check(rid+':final_draw_order', [x['draw'] for x in fm['records']]==list(range(1,21)))
            check(rid+':final_scenario_counts', dict(collections.Counter(x['scenario'] for x in fm['records']))==allocation)
            check(rid+':final_saved_count', fm['cohorts_saved']==sum(x['status']=='ok' for x in fm['records']))
            check(rid+':chronology', task['created_utc']<=fb['created_utc']<=cm['created_utc']<=fm['created_utc'])
            for rel,digest in fm['files'].items(): check(rid+':final_hash:'+rel, sha(run/'final'/rel)==digest)
            for rec in fm['records']:
                check(rid+':draw_log:'+str(rec['draw']), read(run/'final'/f"draw_{rec['draw']:02d}.json")==rec)
                if rec['status']=='ok': check(rid+':draw_artifact:'+str(rec['draw']), fm['files'].get(rec['path'])==rec['sha256']==sha(run/'final'/rec['path']))
            row['requested']=fm['cohorts_requested'];row['saved']=fm['cohorts_saved'];row['final_time']=fm['created_utc']
        runs.append(row)
    for case in protocol['cases']:
        for build in range(1,4):
            a=ROOT/'runs'/case/f'build_{build:02d}'/'ordinary_v1'; b=a.with_name('proposed_v1')
            if (a/'candidate_manifest.json').exists() and (b/'candidate_manifest.json').exists():
                check(f'{case}_build_{build:02d}:sibling_parent_identity', read(a/'task.json')['parent']==read(b/'task.json')['parent'])
    result={'audit_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'stage':'source only, references unopened','protocol_sha256':freeze_sha,
            'checks_total':len(checks),'checks_passed':sum(x['passed'] for x in checks),'failed_checks':[x for x in checks if not x['passed']],
            'frozen_candidates':len(runs),'final_arms':sum(x['final_exists'] for x in runs),'requested_cohorts':sum(x.get('requested',0) for x in runs),
            'saved_cohorts':sum(x.get('saved',0) for x in runs),'deferred_custodian_hashes':deferred,'runs':runs,'checks':checks,
            'limits':['Manifest integrity verifies retained artifacts, not absence of undeclared builder calculations.', 'AST/manual source review is procedural, not an adversarial security proof.', 'No production generation or target evaluation executed by this audit.']}
    path=HERE/'source_execution_audit.json'
    path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['checks_total','checks_passed','failed_checks','frozen_candidates','final_arms','requested_cohorts','saved_cohorts']}))
    print(json.dumps([{k:x[k] for k in ['run_id','action','builder_logged_unique_checks','controller_union_unique_checks','outside_descriptive_envelope','source_lines']} for x in runs]))

if __name__=='__main__': run_audit()
