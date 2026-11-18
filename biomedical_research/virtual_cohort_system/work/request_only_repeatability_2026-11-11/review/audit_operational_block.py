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
    plan = read(UNIT/'PLAN.json')
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
    check('root approval all12', set(approval['episodes']) == {e['episode_id'] for e in plan['episodes']})

    for ep in episodes:
        eid = ep['episode_id']; folder = UNIT/'episodes'/eid
        outcome, state, binding = [read(folder/n) for n in ['OUTCOME.json','TOOLS_STATE.json','EPISODE_BINDING.json']]
        check(eid+' routine terminal', outcome['status'] in {'finalized','call_limit','input_byte_limit','budget_limit','action_limit','output_token_limit','model_stopped_without_finalize'})
        check(eid+' no pending tool', state['pending'] is None)
        check(eid+' plan binding', binding['plan_sha256'] == sha(UNIT/'PLAN.json'))
        instructions = (UNIT/plan['common_instructions_path']).read_text(encoding='utf-8')+'\n\n'+(UNIT/ep['policy_path']).read_text(encoding='utf-8')
        history = [{'role':'user','content':[
            {'type':'input_text','text':(UNIT/ep['request_path']).read_text(encoding='utf-8')},
            {'type':'input_text','text':'Task contract (JSON):\n'+(UNIT/ep['task_path']).read_text(encoding='utf-8')}]}]
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
            check(eid+f' call{k} episode cap', reservation['previous_episode_accounted_usd']+expected_reserve <= 4+1e-12)
            check(eid+f' call{k} total cap', reservation['previous_total_accounted_usd']+expected_reserve <= 48+1e-12)
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
        check(eid+' calls total', len(calls) == outcome['calls_reserved'] and len(calls) <= 48)
        check(eid+' requested action total', actions == outcome['requested_tool_actions'])
        check(eid+' dispatched action cap', state['actions'] <= 60)
        number(eid+' known cost',outcome['known_tariff_cost_usd'],known)
        number(eid+' accounted cost',outcome['accounted_usd'],accounted)
        check(eid+' unknown count',outcome['unknown_usage_calls']==unknown)
        check(eid+' returned identity',returned_models == {plan['model']['id']})
        check(eid+' source quotas',state['gateway_usage'].get('queries',0) <= 20 and state['gateway_usage'].get('downloads',0) <= 16)
        check(eid+' construction quotas',len(state['candidates']) <= 6 and state['runs'] <= 6)
        for cid,args in submitted:
            cp=folder/'candidates'/cid;manifest=read(cp/'manifest.json')
            check(eid+'/'+cid+' manifest',sha(cp/'manifest.json')==state['candidates'][cid]['manifest_sha256'])
            for n,h in manifest['files'].items():check(eid+'/'+cid+' immutable '+n,sha(cp/n)==h)
            check(eid+'/'+cid+' Agent code exact',(cp/'generator.py').read_bytes()==args['generator_py'].encode('utf-8'))
            check(eid+'/'+cid+' Agent parameters exact',read(cp/'model_spec.json')==args['model_spec'])
            check(eid+'/'+cid+' Agent notes exact',read(cp/'notes.json')=={'notes':args.get('notes',''),'provenance':args.get('provenance')})
        check(eid+' all candidates from API submissions',{cid for cid,_ in submitted}==set(state['candidates']))
        selected=outcome.get('selected_candidate')
        if selected:
            decision=read(folder/'FINAL_SELECTION.json')
            check(eid+' exact Agent selection',state['finalized'] and state['selected_candidate']==selected==decision['candidate_id'])
        for rel,h in outcome['history_files'].items():check(eid+' closed API history '+rel,sha(folder/rel)==h)
        summaries.append({'episode_id':eid,'case_id':ep['case_id'],'arm':ep['arm'],'status':outcome['status'],
            'selected_candidate':selected,'calls':len(calls),'tool_actions':actions,'queries':state['gateway_usage'].get('queries',0),
            'downloads':state['gateway_usage'].get('downloads',0),'candidate_count':len(state['candidates']),'trial_attempts':state['runs'],
            'known_tariff_usd':known,'accounted_usd':accounted,'unknown_usage_calls':unknown,'request_max_bytes':max(request_sizes,default=0),
            'api_elapsed_seconds_sum':sum(times),'returned_models':sorted(x for x in returned_models if x),'receipt_status_counts':dict(output_statuses)})
    report={'status':'pass' if not failures else 'blocked','created_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'All four first-block operations; no generated-to-clinical comparison',
        'plan_sha256':sha(UNIT/'PLAN.json'),'launch_freeze_sha256':sha(UNIT/'LAUNCH_FREEZE.json'),
        'outcome_sha256':{e['episode_id']:sha(UNIT/'episodes'/e['episode_id']/'OUTCOME.json') for e in episodes},
        'target_comparisons_inspected':False,'checks':len(checks),'failures':failures,
        'source_exposure_flag_status':'manual adjudication required' if flags else 'No literal flags in returned source text under these patterns; not proof of independence',
        'source_exposure_flags':flags,'episodes':summaries,'reviewer_provider_calls':0,'patient_records_read':False,
        'credential_values_read':False,'candidate_code_executed':False,'opaque_reasoning_not_interpreted':True}
    destination=UNIT/'review'/'OPERATIONAL_BLOCK1_AUDIT.json'
    with destination.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'status':report['status'],'checks':len(checks),'failures':failures,
                      'source_flags':len(flags),'episodes':summaries},ensure_ascii=False))


if __name__ == '__main__':main()
