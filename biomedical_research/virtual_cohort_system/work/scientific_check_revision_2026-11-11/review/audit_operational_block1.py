"""Read-only operational first-block audit; never reads clinical references.

All four outcomes must exist. Checks API history/cost correspondence, immutable
candidate lineage and source-output exposure. No candidate execution or target
comparison is performed. A separate human inspection adjudicates exposure hits.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import importlib.util
import sys

UNIT = Path(__file__).resolve().parents[1]


def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bsha(b): return hashlib.sha256(b).hexdigest()
def enc(x): return json.dumps(x, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
def normalize(s): return ''.join(c for c in unicodedata.normalize('NFKD', s).lower() if not unicodedata.combining(c))


def current_tariff(usage, model):
    if not isinstance(usage, dict): return None
    i, o = usage.get('input_tokens'), usage.get('output_tokens')
    details = usage.get('input_tokens_details') or {}
    c, w = details.get('cached_tokens', 0), details.get('cache_write_tokens', 0)
    if any(type(x) is not int or x < 0 for x in [i, o, c, w]) or c + w > i: return None
    fi, fo = (2, 1.5) if i > 272000 else (1, 1)
    return (((i-c-w)*model['input_rate']+c*model['cached_rate']+w*model['cache_write_rate'])*fi+
            o*model['output_rate']*fo)/1e6


def main():
    spec=importlib.util.spec_from_file_location('reviewed_revision_api',UNIT/'api_loop.py')
    api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
    plan = read(UNIT/'PLAN.json')
    limits=plan['limits']
    episodes = [e for e in plan['episodes'] if e['block'] == 1]
    assert len(episodes) == 4
    assert all((UNIT/'episodes'/e['episode_id']/'OUTCOME.json').exists() for e in episodes), 'Wait for all4 closed outcomes'
    assert not (UNIT/'EVALUATION.json').exists(), 'Operational gate must precede reference evaluation'
    assert not (UNIT/'CONSTRUCTION_CLOSURE.json').exists(), 'Global closure not yet appropriate'
    checks, failures, flags, summaries = [], [], [], []

    def check(name, condition):
        checks.append(name)
        if not condition: failures.append(name)

    def number(name, a, b): check(name, a is not None and b is not None and abs(a-b) < 1e-10)

    freeze, approval = read(UNIT/'LAUNCH_FREEZE.json'), read(UNIT/'ROOT_EXECUTION_APPROVAL.json')
    for n, h in freeze['files'].items(): check('frozen '+n, sha(UNIT/n) == h)
    for n, h in freeze['external_files'].items(): check('external '+n, sha(n) == h)
    check('root approval freeze', approval['launch_freeze_sha256'] == sha(UNIT/'LAUNCH_FREEZE.json'))
    check('root approval files', approval['files'] == freeze['files'])
    check('root approval all24', set(approval['episodes']) == {e['episode_id'] for e in plan['episodes']})

    for ep in episodes:
        eid = ep['episode_id']; folder = UNIT/'episodes'/eid
        outcome, state, binding = [read(folder/n) for n in ['OUTCOME.json','TOOLS_STATE.json','EPISODE_BINDING.json']]
        check(eid+' routine terminal', outcome['status'] in {'finalized','call_limit','input_byte_limit','budget_limit','action_limit','output_token_limit','model_stopped_without_finalize'})
        check(eid+' no pending tool', state['pending'] is None)
        check(eid+' plan binding', binding['plan_sha256'] == sha(UNIT/'PLAN.json'))
        _,_,task,instructions,history,_=api.config(UNIT,eid)
        check(eid+' fresh approved instructions', binding['instructions_sha256'] == bsha(instructions.encode()))
        check(eid+' fresh approved request', binding['initial_input_sha256'] == bsha(enc(history)))
        calls = sorted((folder/'calls').glob('*/reservation.json'))
        known, accounted, unknown, actions = 0., 0., 0, 0
        times, returned_models, request_sizes, output_statuses = [], set(), [], Counter()
        submitted = []
        for k, reservation_path in enumerate(calls, 1):
            cf = reservation_path.parent; reservation = read(reservation_path)
            receipt = read(cf/'receipt.json') if (cf/'receipt.json').exists() else None
            check(eid+f' call{k} contiguous', cf.name == f'{k:04d}')
            request = read(cf/'request.json')
            check(eid+f' call{k} request hash', sha(cf/'request.json') == reservation['request_sha256'])
            check(eid+f' call{k} approved instructions', request['instructions'] == instructions)
            check(eid+f' call{k} exact carried history', request['input'] == history)
            check(eid+f' call{k} exact tools', bsha(enc(request['tools'])) == binding['tools_sha256'])
            check(eid+f' call{k} model', request['model'] == plan['model']['id'])
            check(eid+f' call{k} settings', request['reasoning'] == {'effort':'high'} and request['service_tier'] == 'default' and request['store'] is False and request['parallel_tool_calls'] is False)
            check(eid+f' call{k} output limit', request['max_output_tokens'] == plan['limits']['max_output_tokens'])
            raw_size = (cf/'request.json').stat().st_size; request_sizes.append(raw_size)
            check(eid+f' call{k} byte cap', raw_size == reservation['input_bytes'] and raw_size <= plan['limits']['max_input_bytes'])
            allowance = raw_size + 4096
            fi, fo = (2, 1.5) if allowance > 272000 else (1, 1)
            expected_reserve = (allowance * max(plan['model']['input_rate'],plan['model']['cache_write_rate'])*fi+
                                plan['limits']['max_output_tokens']*plan['model']['output_rate']*fo)/1e6
            number(eid+f' call{k} reservation', reservation['reserved_usd'], expected_reserve)
            check(eid+f' call{k} episode cap', reservation['previous_episode_accounted_usd']+expected_reserve <= limits['episode_usd_cap']+1e-12)
            check(eid+f' call{k} total cap', reservation['previous_total_accounted_usd']+expected_reserve <= limits['total_usd_cap']+1e-12)
            check(eid+f' call{k} no retry', reservation['no_automatic_retry'] is True)
            if receipt is None:
                unknown += 1; accounted += reservation['reserved_usd']; continue
            check(eid+f' call{k} receipt binding', receipt['reservation_sha256'] == sha(reservation_path))
            check(eid+f' call{k} request binding', receipt['request_sha256'] == reservation['request_sha256'])
            cost = current_tariff(receipt.get('usage'), plan['model'])
            if cost is None:
                unknown += 1; accounted += reservation['reserved_usd']
                check(eid+f' call{k} unknown cost null', receipt.get('tariff_cost_usd') is None)
            else:
                known += cost; accounted += cost
                number(eid+f' call{k} actual tariff', receipt['tariff_cost_usd'], cost)
                check(eid+f' call{k} reserve sufficient', cost <= reservation['reserved_usd']+1e-12)
            times.append(receipt.get('elapsed_seconds',0)); returned_models.add(receipt.get('returned_model'))
            output_statuses[receipt.get('status')] += 1
            if (cf/'response_raw.json').exists():
                check(eid+f' call{k} response binding', sha(cf/'response_raw.json') == receipt['response_raw_sha256'])
                response_body = read(cf/'response_raw.json')
                check(eid+f' call{k} receipt extraction', receipt['usage'] == response_body.get('usage') and receipt['returned_model'] == response_body.get('model'))
            if k < len(calls): check(eid+f' call{k} no continuation after API failure', receipt.get('status') == 'received')
            if receipt.get('status') != 'received': continue
            response = read(cf/'response_raw.json')
            # Carry opaque output objects without interpreting encrypted reasoning.
            history += response['output']
            for p in sorted(cf.glob('tool_*.result.json')):
                result = read(p); intentp = p.with_name(p.name.replace('.result.','.intent.')); intent = read(intentp)
                actions += 1
                check(eid+f' call{k} tool binding '+p.name, result['intent_sha256'] == sha(intentp))
                check(eid+f' call{k} tool correspondence '+p.name,
                      result['call_id'] == intent['call']['call_id'] and intent['call'] in response['output'])
                check(eid+f' call{k} tool uncertainty '+p.name, not result.get('uncertain_dispatch',False))
                history.append({'type':'function_call_output','call_id':result['call_id'],'output':result['output']})
                value = json.loads(result['output'])
                if intent['call']['name'] == 'submit_candidate' and value.get('status') == 'stored':
                    submitted.append((value['candidate_id'],json.loads(intent['call']['arguments'])))
                if intent['call']['name'] in {'literature_search','read_source'}:
                    parts = [value['content']] if isinstance(value.get('content'),str) else []
                    parts += [m['context'] for m in value.get('matches',[]) if isinstance(m.get('context'),str)]
                    if value.get('hits'): parts.append(json.dumps(value['hits'],ensure_ascii=False))
                    text = '\n'.join(parts); norm = normalize(text)
                    patterns = ['pesquisa nacional','national health survey','turkana','evidence-guided-virtual-cohorts','from published evidence to analyzable',r'\bpns\b']
                    for pattern in patterns:
                        for match in re.finditer(pattern,norm):
                            flags.append({'episode_id':eid,'tool_result':str(p.relative_to(UNIT)),
                                          'pattern':pattern,'context':text[max(0,match.start()-180):match.end()+220]})
            if (cf/'continuation.json').exists():
                cont = read(cf/'continuation.json')
                check(eid+f' call{k} continuation', cont['input'] == history and cont['action_count'] == actions)
        check(eid+' calls total', len(calls) == outcome['calls_reserved'] and len(calls) <= limits['max_calls'])
        check(eid+' requested action total', actions == outcome['requested_tool_actions'])
        check(eid+' dispatched action cap', state['actions'] <= limits['max_actions'])
        number(eid+' known cost',outcome['known_tariff_cost_usd'],known)
        number(eid+' accounted cost',outcome['accounted_usd'],accounted)
        check(eid+' unknown count',outcome['unknown_usage_calls']==unknown)
        check(eid+' returned identity',returned_models == {plan['model']['id']})
        check(eid+' source quotas',state['gateway_usage'].get('queries',0) <= limits['max_queries'] and state['gateway_usage'].get('downloads',0) <= limits['max_downloads'])
        check(eid+' construction quotas',len(state['candidates']) <= 1+limits['max_candidates'] and state['runs'] <= limits['max_runs'])
        for cid,args in submitted:
            cp=folder/'candidates'/cid;manifest=read(cp/'manifest.json')
            check(eid+'/'+cid+' manifest',sha(cp/'manifest.json')==state['candidates'][cid]['manifest_sha256'])
            for n,h in manifest['files'].items():check(eid+'/'+cid+' immutable '+n,sha(cp/n)==h)
            check(eid+'/'+cid+' Agent code exact',(cp/'generator.py').read_bytes()==args['generator_py'].encode('utf-8'))
            check(eid+'/'+cid+' Agent parameters exact',read(cp/'model_spec.json')==args['model_spec'])
            check(eid+'/'+cid+' Agent notes exact',read(cp/'notes.json')=={'notes':args.get('notes',''),'provenance':args.get('provenance')})
        check(eid+' all candidates from API submissions',({'v000'}|{cid for cid,_ in submitted})==set(state['candidates']))
        selected=outcome.get('selected_candidate')
        if selected:
            decision=read(folder/'FINAL_SELECTION.json')
            check(eid+' exact Agent selection',state['finalized'] and state['selected_candidate']==selected==decision['candidate_id'])
        for rel,h in outcome['history_files'].items():check(eid+' closed API history '+rel,sha(folder/rel)==h)
        extended=audit_revision_details(ep,folder,state,outcome,task,check,api)
        summaries.append({'revision_audit':extended,'episode_id':eid,'case_id':ep['case_id'],'arm':ep['arm'],'status':outcome['status'],
            'selected_candidate':selected,'calls':len(calls),'tool_actions':actions,'queries':state['gateway_usage'].get('queries',0),
            'downloads':state['gateway_usage'].get('downloads',0),'candidate_count':len(state['candidates']),'trial_attempts':state['runs'],
            'known_tariff_usd':known,'accounted_usd':accounted,'unknown_usage_calls':unknown,'request_max_bytes':max(request_sizes,default=0),
            'api_elapsed_seconds_sum':sum(times),'returned_models':sorted(x for x in returned_models if x),'receipt_status_counts':dict(output_statuses)})
    for pair in sorted({e['pair_id'] for e in episodes}):
        rows=[e for e in episodes if e['pair_id']==pair]
        inputs=[api.config(UNIT,e['episode_id'])[4] for e in rows]
        bindings=[read(UNIT/'episodes'/e['episode_id']/'EPISODE_BINDING.json') for e in rows]
        check(pair+' exact input parity',inputs[0]==inputs[1])
        check(pair+' exact tool parity',bindings[0]['tools_sha256']==bindings[1]['tools_sha256'])
    report={'status':'pass' if not failures else 'blocked','created_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'All four first-block operations; no generated-to-clinical comparison',
        'plan_sha256':sha(UNIT/'PLAN.json'),'launch_freeze_sha256':sha(UNIT/'LAUNCH_FREEZE.json'),
        'outcome_sha256':{e['episode_id']:sha(UNIT/'episodes'/e['episode_id']/'OUTCOME.json') for e in episodes},
        'target_comparisons_inspected':False,'checks':len(checks),'failures':failures,
        'source_exposure_flag_status':'manual adjudication required' if flags else 'No literal flags in returned source text under these patterns; not proof of independence',
        'source_exposure_flags':flags,'episodes':summaries,'reviewer_provider_calls':0,'patient_records_read':False,'generated_row_values_read':False,'generated_files_hashed_only':True,
        'credential_values_read':False,'candidate_code_executed':False,'opaque_reasoning_not_interpreted':True}
    destination=UNIT/'review'/'OPERATIONAL_BLOCK1_TECHNICAL.json'
    with destination.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'status':report['status'],'checks':len(checks),'failures':failures,
                      'source_flags':len(flags),'episodes':summaries},ensure_ascii=False))





def audit_revision_details(ep, folder, state, outcome, task, check, api):
    """New revision-specific lineage and controlled-feedback audit; no references."""
    eid=ep['episode_id']; prefix=eid+' revision '
    def safe(base,relative):
        p=(base/relative).resolve()
        check(prefix+'contained '+str(relative),p.is_relative_to(base.resolve()))
        if not p.is_relative_to(base.resolve()): raise ValueError('Path escapes audit boundary')
        return p
    package_path=safe(UNIT,ep['imported_package_path']); package=read(package_path)
    check(prefix+'import metadata',state['import_binding']=={
        'package_sha256':sha(package_path),'review_policy':ep['arm'],
        'requested_analysis_ids':ep['requested_analysis_ids'],'analysis_requirements':ep['analysis_requirements']})
    for name,h in package['files'].items():check(prefix+'import immutable '+name,sha(safe(package_path.parent,name))==h)
    initial=safe(folder,state['candidates']['v000']['path']); manifest=read(initial/'manifest.json')
    check(prefix+'v000 original manifest',manifest['imported_original_manifest_sha256']==package['candidate_manifest_sha256_original'])
    check(prefix+'v000 local manifest',sha(initial/'manifest.json')==state['candidates']['v000']['manifest_sha256'])
    for name in ['generator.py','model_spec.json','notes.json']:
        check(prefix+'v000 original bytes '+name,sha(initial/name)==package['files'][name]==manifest['files'][name])
    for cid,item in state['candidates'].items():
        cp=safe(folder,item['path']); m=read(cp/'manifest.json')
        check(prefix+'candidate identity '+cid,cp.name==cid and m['candidate_id']==cid)
        check(prefix+'candidate manifest '+cid,sha(cp/'manifest.json')==item['manifest_sha256'])
        for name,h in m['files'].items():check(prefix+'candidate file '+cid+'/'+name,sha(safe(cp,name))==h)
    for sid,item in state.get('searches',{}).items():check(prefix+'search record '+sid,sha(safe(folder,item['path']))==item['sha256'])
    for sid,item in state.get('sources',{}).items():
        for key in ['path','xml_path']:
            if key in item:
                expected=item.get('xml_sha256',item.get('sha256'))
                check(prefix+'source XML '+sid,expected is not None and sha(safe(folder,item[key]))==expected)
    # Match each host-side tool journal to exactly one model-originated intent.
    outer=[]; inspection_returns=[]; selections=[]
    for result_path in sorted((folder/'calls').glob('*/tool_*.result.json')):
        result=read(result_path); intent=read(result_path.with_name(result_path.name.replace('.result.','.intent.')))
        call=intent['call']; value=json.loads(result['output'])
        try: args=json.loads(call['arguments'])
        except (ValueError,TypeError): args=None
        outer.append((call['name'],args,value,result_path))
        if call['name']=='inspect_law' and value.get('review_receipt_sha256'):
            inspection_returns.append((args,value,result_path))
        if call['name']=='finalize' and value.get('status')=='finalized':selections.append((args,value))
    actions=sorted((folder/'tool_actions').glob('action_*'))
    check(prefix+'durable dispatched action count',len(actions)==state['actions'])
    cursor=0
    for i,action in enumerate(actions,1):
        check(prefix+f'action {i} sequence',action.name==f'action_{i:04d}')
        req,res=read(action/'request.json'),read(action/'result.json')
        found=None
        while cursor<len(outer):
            name,args,value,p=outer[cursor];cursor+=1
            if name==req['name'] and args==req['arguments'] and value==res:
                found=p;break
        check(prefix+f'action {i} exact API dispatch/result',found is not None)
    check(prefix+'finalize from API',bool(selections)==state['finalized'])
    if state['finalized']:
        check(prefix+'single terminal Agent finalize',len(selections)==1)
        args,value=selections[-1];decision=read(folder/'FINAL_SELECTION.json')
        check(prefix+'terminal reason unmodified',decision['reason']==args.get('reason','') and decision['unable_reason']==args.get('unable_reason'))
        check(prefix+'terminal selection unmodified',decision['candidate_id']==args.get('candidate_id')==value['selected_candidate'])
    # Inspect trial identities and hashes only, never load generated rows.
    trials=state.get('trial_history',[])
    check(prefix+'trial count',len(trials)==state['runs'])
    successful=[]
    for i,trial in enumerate(trials,1):
        run=safe(folder,trial['run_path']); cp=safe(folder,state['candidates'][trial['candidate_id']]['path'])
        check(prefix+f'trial {i} sequential',run.name==f'trial_{i:03d}')
        if trial['execution_receipt_sha256'] is not None:
            check(prefix+f'trial {i} receipt',sha(run/'execution.json')==trial['execution_receipt_sha256'])
            rec=read(run/'execution.json')
            check(prefix+f'trial {i} identity',rec['candidate_id']==trial['candidate_id'] and rec['seed']==53001)
            check(prefix+f'trial {i} no sandbox fallback',rec.get('isolation')=='WSL/bubblewrap only; no fallback')
        if trial['input_bindings_sha256'] is not None:
            check(prefix+f'trial {i} input binding hash',sha(run/'input_bindings.json')==trial['input_bindings_sha256'])
            staged=read(run/'input_bindings.json')
            check(prefix+f'trial {i} staged inputs',staged=={p.name:sha(p) for p in (run/'input').iterdir() if p.is_file()})
            for name in ['generator.py','model_spec.json']:
                check(prefix+f'trial {i} selected artifact '+name,staged.get(name)==sha(cp/name))
            check(prefix+f'trial {i} exact task',read(run/'input/task.json')==task)
            check(prefix+f'trial {i} diagnostic seed',read(run/'input/request.json')['seed']==53001)
        if trial['status']=='success':
            check(prefix+f'trial {i} success receipt',rec['status']=='success')
            check(prefix+f'trial {i} generated hash',sha(run/'output/generated.csv')==rec['generated_sha256'])
            successful.append(trial)
    # Independently revalidate declarations without running code or reading tables.
    spec=importlib.util.spec_from_file_location('operational_declaration_checker',UNIT/'law_checks.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    check_task=dict(task,requested_analysis_ids=ep['requested_analysis_ids'],analysis_requirements=ep['analysis_requirements'])
    unknowns=[]; unavailable_sources=[]; used_source_ids=set(); completeness=[]
    for ordinal,meta in state.get('review_receipts',{}).items():
        path=safe(folder,meta['path']);receipt=read(path);result=receipt['result'];contract=receipt['review_contract']
        check(prefix+'review hash '+ordinal,sha(path)==meta['sha256'])
        cid=meta['candidate_id'];cp=safe(folder,state['candidates'][cid]['path'])
        check(prefix+'review candidate '+ordinal,receipt['candidate_id']==cid==result['candidate_id'] and result['candidate_manifest_sha256']==sha(cp/'manifest.json')==meta['candidate_manifest_sha256'])
        matching=[(a,v) for a,v,p in inspection_returns if v['review_receipt_sha256']==meta['sha256']]
        check(prefix+'review returned to Agent '+ordinal,len(matching)==1)
        if matching:
            a,v=matching[0];returned={k:x for k,x in v.items() if k not in {'usage','review_receipt_sha256'}}
            check(prefix+'review model-declared contract '+ordinal,a['candidate_id']==cid and a['review_contract']==contract)
            check(prefix+'review exact feedback '+ordinal,returned==result)
        val=module.validate_contract(contract,check_task)
        check(prefix+'review semantic validation '+ordinal,val==result['contract_validation'] and val['valid']==meta['valid_contract'])
        coverage=val.get('coverage',{})
        complete=(not coverage.get('mathematical_variables_not_declared') and not coverage.get('analyses_without_dependencies') and coverage.get('analysis_coverage')=='complete_declarations_only')
        check(prefix+'review completeness '+ordinal,complete==meta['complete_declarations'])
        completeness.append({'ordinal':ordinal,'candidate_id':cid,'complete':complete})
        check(prefix+'review not certification '+ordinal,result['target_reference_read'] is False and result['science_certified'] is False)
        ids=set()
        for item in contract.get('mathematical_review',[])+contract.get('physiological_rules',[]):ids.update(item.get('source_ids',[]))
        for analysis in contract.get('joint_analyses',[]):
            for dep in analysis.get('dependencies',[]):ids.update(dep.get('source_ids',[]))
        check(prefix+'all cited IDs bound '+ordinal,ids==set(result['source_bindings']))
        used_source_ids.update(ids)
        for sid,bound in result['source_bindings'].items():
            versions=[]
            for origin,registry in [('imported',package['sources']),('newly_retrieved',state['sources'])]:
                if sid in registry:
                    x=registry[sid];versions.append({'origin':origin,'version':x.get('version'),'xml_sha256':x.get('xml_sha256',x.get('sha256'))})
            if versions:
                check(prefix+'availability-only source '+ordinal+'/'+sid,bound['status']=='registered_availability_only_not_evidence_validation' and bound['registered_versions']==versions and bound['selected_evidence_version'] is None and bound['version_ambiguous']==(len({(v['version'],v['xml_sha256']) for v in versions})>1))
            else:
                check(prefix+'unknown source honest '+ordinal+'/'+sid,bound['status']=='unavailable_unregistered_source');unavailable_sources.append(sid)
        if result.get('execution_receipt_sha256'):
            matches=[t for t in successful if t['candidate_id']==cid and t['execution_receipt_sha256']==result['execution_receipt_sha256'] and t['input_bindings_sha256']==result['input_bindings_sha256']]
            check(prefix+'review trial bindings '+ordinal,len(matches)==1)
        # This reports unresolved declarations, not their clinical accuracy.
        unknowns.extend({'ordinal':ordinal,'variable':m.get('variable')} for m in contract.get('mathematical_review',[]) if m.get('moment_assessment')=='unresolved')
    if ep['arm']=='structured' and outcome.get('selected_candidate'):
        check(prefix+'structured selected candidate inspected',any(x['candidate_id']==outcome['selected_candidate'] and x['complete'] for x in completeness))
    return {'review_receipts':len(completeness),'review_coverage':completeness,'unresolved_mathematical_declarations':unknowns,
            'unregistered_source_ids':sorted(set(unavailable_sources)),'declared_source_ids':sorted(used_source_ids),
            'inspected_rows':False,'reference_files_read':False,'trial_byte_bindings_verified':True,
            'source_availability_does_not_certify_extraction_or_transfer':True}


if __name__ == '__main__':main()
