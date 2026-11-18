"""Durable request-only Responses loop. No scientific policy or candidate editing.

Live CLI: python api_loop.py --episode PNS_BASE (or --all, at most two workers).
Tests must explicitly pass test_mode=True, http_post, runtime_factory and tools.
Request/response files are PRIVATE API captures, including encrypted reasoning.
They are never converted into a reasoning transcript or public report.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent
ENDPOINT = 'https://api.openai.com/v1/responses'
MODEL = 'gpt-6.1-sol'
KEY_HELPER = ROOT.parent / 'economy_feedback_pilot_2026-11-10/budget_keys.py'
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
EPISODE_IDS = {'PNS_BASE', 'PNS_WORKFLOW', 'LIPID_BASE', 'LIPID_WORKFLOW'}
DEFAULT_RATES = {'input_rate': 2., 'output_rate': 10., 'cached_rate': .1, 'cache_write_rate': 2.5}


class IntegrityError(RuntimeError):
    pass


class BusyError(RuntimeError):
    pass


class UnavailableRuntime:
    """An uncertain tool state is never interpreted as a confirmed selection."""
    finalized = False
    selected_candidate = None
    selected_candidate_path = None
    unable_reason = None
    usage = None


def utc():
    return datetime.now(timezone.utc).isoformat()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha(path):
    return sha_bytes(Path(path).read_bytes())


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def decode(raw):
    def reject(_):
        raise ValueError('Non-finite JSON number')
    return json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=reject)


def read(path):
    try:
        return decode(Path(path).read_bytes())
    except (ValueError, OSError) as exc:
        raise IntegrityError('Unreadable durable JSON: ' + Path(path).name) from exc


def write_new(path, value, *, raw=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if raw else encoded(value)
    with path.open('xb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def contained(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise IntegrityError('Expected a unit-relative input path')
    root = Path(root).resolve()
    p = (root / relative).resolve()
    if not p.is_relative_to(root):
        raise IntegrityError('Path leaves pilot unit')
    return p


@contextmanager
def file_lock(path, *, blocking=True):
    """OS locks release on process death; lock-file existence is not a lease."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path.open('a+b')
    if f.seek(0, 2) == 0:
        f.write(b'0')
        f.flush()
    locked = False
    try:
        while True:
            try:
                f.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except (OSError, BlockingIOError):
                if not blocking:
                    raise BusyError('Pilot execution slot is busy')
                time.sleep(.05)
        yield
    finally:
        if locked:
            f.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        f.close()


@contextmanager
def episode_slot(root, episode_id):
    with file_lock(root / '.locks' / (episode_id + '.lock'), blocking=False):
        leases = []
        for n in range(2):
            lease = file_lock(root / '.locks' / ('slot_' + str(n) + '.lock'), blocking=False)
            try:
                lease.__enter__()
            except BusyError:
                continue
            leases.append(lease)
            break
        if not leases:
            raise BusyError('Two episodes already active')
        try:
            yield
        finally:
            leases[0].__exit__(None, None, None)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def config(root, episode_id):
    plan = read(root / 'PLAN.json')
    model = plan['model']
    limits = plan['limits']
    if model['id'] != MODEL or model['reasoning_effort'] != 'high' or model['service_tier'] != 'default':
        raise IntegrityError('Unexpected frozen model configuration')
    maxima = {'max_calls':24, 'max_output_tokens':16384, 'max_input_bytes':250000,
              'episode_usd_cap':4, 'total_usd_cap':16, 'max_actions':60}
    for key, maximum in maxima.items():
        value = limits.get(key)
        if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value) or not 0 < value <= maximum:
            raise IntegrityError('Invalid limit: ' + key)
        if key not in {'episode_usd_cap','total_usd_cap'} and not isinstance(value,int):
            raise IntegrityError('Integer limit required: ' + key)
    rates = {key:model.get(key, value) for key,value in DEFAULT_RATES.items()}
    if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x < 0 for x in rates.values()):
        raise IntegrityError('Invalid tariff')
    ids = [r['episode_id'] for r in plan['episodes']]
    if len(ids) != len(set(ids)) or set(ids) != EPISODE_IDS or episode_id not in EPISODE_IDS:
        raise IntegrityError('Exactly the four registered episodes are required')
    episode = next(r for r in plan['episodes'] if r['episode_id'] == episode_id)
    files = {k: contained(root,episode[k]) for k in ['task_path','request_path','policy_path']}
    common = contained(root,plan['common_instructions_path'])
    task_text = files['task_path'].read_text(encoding='utf-8')
    task = decode(task_text)
    instructions = common.read_text(encoding='utf-8') + '\n\n' + files['policy_path'].read_text(encoding='utf-8')
    initial_input = [{'role':'user','content':[
        {'type':'input_text','text':files['request_path'].read_text(encoding='utf-8')},
        {'type':'input_text','text':'Task contract (JSON):\n' + task_text}]}]
    return plan, episode, task, instructions, initial_input, rates


def verify_live_gate(root, plan):
    freeze = read(root / 'LAUNCH_FREEZE.json')
    review = read(root / 'PREFLIGHT_REVIEW.json')
    if str(review.get('status','')).lower() != 'pass':
        raise IntegrityError('Independent preflight review is not PASS')
    hashes = freeze.get('files')
    if not isinstance(hashes,dict):
        raise IntegrityError('Launch freeze requires files hash map')
    required = {'PLAN.json','api_loop.py','tools_runtime.py','PROTOCOL.md','PREFLIGHT_REVIEW.json',plan['common_instructions_path']}
    for ep in plan['episodes']:
        required.update(ep[k] for k in ['task_path','request_path','policy_path'])
    if not required <= set(hashes):
        raise IntegrityError('Launch freeze omits required code or input')
    for name, expected in hashes.items():
        if sha(contained(root,name)) != expected:
            raise IntegrityError('Launch-frozen file changed: ' + name)
    reviewed = review.get('reviewed_files')
    if not isinstance(reviewed,dict) or not (required-{'PREFLIGHT_REVIEW.json'}) <= set(reviewed):
        raise IntegrityError('Preflight review omits reviewed implementation/input hashes')
    for name, expected in reviewed.items():
        if hashes.get(name) != expected or sha(contained(root,name)) != expected:
            raise IntegrityError('Reviewed bytes differ from launch freeze: ' + name)
    if freeze.get('credential_helper_sha256') != sha(KEY_HELPER):
        raise IntegrityError('Launch freeze must bind local credential-helper bytes')
    if review.get('credential_helper_sha256') != freeze['credential_helper_sha256']:
        raise IntegrityError('Credential helper differs from reviewed version')
    external = freeze.get('external_files',{})
    if external != review.get('reviewed_external_files',{}):
        raise IntegrityError('External runtime dependencies differ from review')
    for name, expected in external.items():
        file=Path(name)
        if not file.is_absolute() or file.suffix != '.py' or sha(file) != expected:
            raise IntegrityError('External Python dependency changed')


def tariff(usage, rates):
    if not isinstance(usage,dict):
        return None
    i, o = usage.get('input_tokens'), usage.get('output_tokens')
    details = usage.get('input_tokens_details') or {}
    cached, written = details.get('cached_tokens',0), details.get('cache_write_tokens',0)
    values = [i,o,cached,written]
    if any(isinstance(x,bool) or not isinstance(x,int) or x < 0 for x in values) or cached + written > i:
        return None
    return ((i-cached-written)*rates['input_rate'] + cached*rates['cached_rate'] +
            written*rates['cache_write_rate'] + o*rates['output_rate']) / 1e6


def accounted(root, episode_id=None):
    total = 0.
    for path in sorted((root/'episodes').glob('*/calls/*/reservation.json')):
        reservation = read(path)
        if episode_id is not None and reservation['episode_id'] != episode_id:
            continue
        amount = reservation['reserved_usd']
        receipt_path = path.with_name('receipt.json')
        if receipt_path.exists():
            receipt = read(receipt_path)
            if receipt.get('reservation_sha256') != sha(path):
                raise IntegrityError('Reservation/receipt binding mismatch')
            cost = receipt.get('tariff_cost_usd')
            if cost is not None:
                amount = cost
        if isinstance(amount,bool) or not isinstance(amount,(int,float)) or not math.isfinite(amount) or amount < 0:
            raise IntegrityError('Invalid ledger amount')
        total += amount
    return total


def clean_text(value, secrets):
    for secret in secrets:
        if secret:
            value = value.replace(secret, '[REDACTED]')
    return value


def request_body(instructions, history, definitions, limits):
    return {'model':MODEL, 'instructions':instructions, 'input':history, 'tools':definitions,
            'tool_choice':'auto', 'parallel_tool_calls':False, 'store':False,
            'include':['reasoning.encrypted_content'], 'reasoning':{'effort':'high'},
            'max_output_tokens':limits['max_output_tokens'], 'service_tier':'default'}


def reserve(root, episode_id, n, body, limits, rates):
    raw = encoded(body)
    if len(raw) > limits['max_input_bytes']:
        return None, 'input_byte_limit'
    # Deliberately generous byte-token allowance, not a claim about invoice tokens.
    allowance = len(raw) + 4096
    reserved = (allowance*max(rates['input_rate'],rates['cache_write_rate']) +
                limits['max_output_tokens']*rates['output_rate']) / 1e6
    folder = root/'episodes'/episode_id/'calls'/f'{n:04d}'
    with file_lock(root/'.locks/ledger.lock'):
        ep_spend, all_spend = accounted(root,episode_id), accounted(root)
        if ep_spend + reserved > limits['episode_usd_cap'] or all_spend + reserved > limits['total_usd_cap']:
            return None, 'budget_limit'
        folder.mkdir(parents=True,exist_ok=False)
        write_new(folder/'request.json',raw,raw=True)
        write_new(folder/'reservation.json',{'episode_id':episode_id,'call_number':n,'reserved_usd':reserved,
          'previous_episode_accounted_usd':ep_spend,'previous_total_accounted_usd':all_spend,
          'created_utc':utc(),'request_sha256':sha_bytes(raw),'input_bytes':len(raw),
          'input_token_allowance':allowance,'max_output_tokens':limits['max_output_tokens'],
          'episode_usd_cap':limits['episode_usd_cap'],'total_usd_cap':limits['total_usd_cap'],
          'rates_per_million_tokens':rates,'reservation_interpretation':'conservative allowance, not provider invoice',
          'endpoint':ENDPOINT,'requested_model':MODEL,'no_automatic_retry':True})
    return folder, None


def send_once(folder, post, auth_headers, secrets, rates):
    reservation = read(folder/'reservation.json')
    request_raw = (folder/'request.json').read_bytes()
    if sha_bytes(request_raw) != reservation['request_sha256']:
        raise IntegrityError('Request/reservation hash mismatch')
    receipt = {'episode_id':reservation['episode_id'],'call_number':reservation['call_number'],
        'started_utc':utc(),'requested_model':MODEL,'endpoint':ENDPOINT,'no_automatic_retry':True,
        'reservation_sha256':sha(folder/'reservation.json'),'request_sha256':sha_bytes(request_raw),
        'reserved_usd':reservation['reserved_usd'],'usage':None,'tariff_cost_usd':None}
    start = time.monotonic()
    response = None
    data = None
    try:
        response = post(ENDPOINT, headers=auth_headers, data=request_raw, timeout=(20,1500),
                        allow_redirects=False, stream=True)
        chunks, size = [], 0
        for chunk in response.iter_content(65536):
            size += len(chunk)
            if size > MAX_RESPONSE_BYTES:
                raise ValueError('Response capture ceiling exceeded')
            chunks.append(chunk)
        raw = b''.join(chunks)
        text = raw.decode('utf-8')
        cleaned = clean_text(text,secrets)
        write_new(folder/'response_raw.json',cleaned.encode('utf-8'),raw=True)
        receipt.update(http_status=response.status_code,response_bytes=size,
          request_id=response.headers.get('x-request-id'), response_original_sha256=sha_bytes(raw),
          response_raw_sha256=sha(folder/'response_raw.json'),secrets_redacted=cleaned!=text)
        data = decode(cleaned)
        if not isinstance(data,dict):
            raise ValueError('Response JSON must be an object')
        receipt.update(usage=data.get('usage'), returned_model=data.get('model'),
          response_id=data.get('id'), completion_status=data.get('status'),
          incomplete_details=data.get('incomplete_details'))
        receipt['tariff_cost_usd'] = tariff(data.get('usage'),rates)
        if cleaned != text:
            receipt['status']='secret_redaction_required'
        elif not 200 <= response.status_code < 300:
            receipt['status']='http_error'
        elif data.get('model') != MODEL:
            receipt['status']='model_mismatch'
        elif data.get('status') != 'completed':
            receipt['status']='incomplete_response'
        elif not isinstance(data.get('output'),list):
            receipt['status']='invalid_output'
        else:
            receipt['status']='received'
        if receipt['tariff_cost_usd'] is not None and receipt['tariff_cost_usd'] > reservation['reserved_usd']:
            receipt['reservation_exceeded']=True
            receipt['status']='reservation_exceeded'
    except Exception as exc:
        receipt.update(status='transport_or_capture_error', error_type=type(exc).__name__,
                       error=clean_text(str(exc),secrets)[:1000])
    finally:
        if response is not None:
            response.close()
    receipt.update(ended_utc=utc(),elapsed_seconds=time.monotonic()-start)
    with file_lock(folder.parents[3]/'.locks/ledger.lock'):
        write_new(folder/'receipt.json',receipt)
    return receipt, data


def tool_error(code):
    return {'ok':False,'error':{'type':'mechanical_error','code':code}}


def advance(folder, history, data, runtime, allowed, action_count, max_actions, seen_ids, secrets):
    """Replay saved results; never redispatch an uncertain tool side effect."""
    output = data['output']
    if any(not isinstance(item,dict) for item in output):
        return None, action_count, 'invalid_output_item'
    calls = [x for x in output if x.get('type')=='function_call']
    ids = [x.get('call_id') for x in calls]
    if any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)) or set(ids)&seen_ids:
        return None, action_count, 'invalid_function_call_correspondence'
    next_input = history + output  # Preserve ALL output items, including encrypted reasoning.
    denied = False
    uncertain = False
    for i, call in enumerate(calls,1):
        intent_path, result_path = folder/f'tool_{i:03d}.intent.json', folder/f'tool_{i:03d}.result.json'
        if result_path.exists() and not intent_path.exists():
            raise IntegrityError('Tool result has no durable intent')
        if intent_path.exists():
            intent = read(intent_path)
            if intent['call'] != call:
                raise IntegrityError('Tool intent does not match API function call')
            if not result_path.exists():
                return None, action_count, 'interrupted_tool_dispatch'
            result = read(result_path)
            if result['intent_sha256'] != sha(intent_path) or result['call_id'] != call['call_id']:
                raise IntegrityError('Tool result correspondence mismatch')
            action_count += 1
            denied |= result.get('budget_denied',False)
            uncertain |= result.get('uncertain_dispatch',False)
        else:
            action_count += 1
            over = action_count > max_actions
            write_new(intent_path,{'call':call,'episode_action_number':action_count,'started_utc':utc(),'budget_denied':over})
            parsed, error = None, None
            if uncertain:
                error='not_dispatched_after_uncertain_tool'
            elif over:
                error='action_budget_exhausted'
                denied=True
            elif call.get('name') not in allowed:
                error='unknown_tool'
            else:
                try:
                    if not isinstance(call.get('arguments'),str):
                        raise ValueError('Arguments must be serialized JSON')
                    parsed=decode(call['arguments'])
                    if not isinstance(parsed,dict):
                        raise ValueError('Arguments must be a JSON object')
                except (ValueError,TypeError):
                    error='malformed_function_arguments'
            if error:
                value=tool_error(error)
            else:
                try:
                    value=runtime.dispatch(call['name'],parsed)
                    encoded(value)  # require JSON-safe output
                except Exception as exc:
                    uncertain=True
                    value={'ok':False,'error':{'type':'mechanical_error','code':'tool_exception',
                           'exception_type':type(exc).__name__,'message':clean_text(str(exc),secrets)[:600]}}
            output_text=clean_text(encoded(value).decode('utf-8'),secrets)
            result={'call_id':call['call_id'],'name':call.get('name'),'output':output_text,
                    'intent_sha256':sha(intent_path),'ended_utc':utc(),'budget_denied':over,
                    'uncertain_dispatch':uncertain}
            write_new(result_path,result)
        next_input.append({'type':'function_call_output','call_id':call['call_id'],'output':result['output']})
    stop = ('uncertain_tool_dispatch' if uncertain else 'finalized' if runtime.finalized else 'action_limit' if denied else
            'model_stopped_without_finalize' if not calls else None)
    continuation={'input':next_input,'action_count':action_count,'stop_reason':stop,
       'response_sha256':sha(folder/'response_raw.json'),
       'tool_results':{p.name:sha(p) for p in sorted(folder.glob('tool_*.result.json'))},
       'created_utc':utc()}
    write_new(folder/'continuation.json',continuation)
    return next_input, action_count, stop


def outcome(root, episode_id, runtime, status, action_count):
    directory=root/'episodes'/episode_id
    receipts=[]
    for p in sorted((directory/'calls').glob('*/receipt.json')):
        receipts.append(read(p))
    known=[r for r in receipts if r.get('tariff_cost_usd') is not None]
    confirmed=bool(runtime.finalized) and status=='finalized'
    selected=runtime.selected_candidate if confirmed else None
    result={'episode_id':episode_id,'closed_utc':utc(),'status':status,'finalized':confirmed,
      'runtime_finalized':bool(runtime.finalized),
      'selected_candidate':selected,'selected_candidate_path':getattr(runtime,'selected_candidate_path',None) if selected else None,
      'unable_reason':getattr(runtime,'unable_reason',None) if confirmed else None,
      'calls_reserved':len(list((directory/'calls').glob('*/reservation.json'))),'calls_receipted':len(receipts),
      'requested_tool_actions':action_count,'tool_usage':getattr(runtime,'usage',None),
      'known_tariff_cost_usd':sum(r['tariff_cost_usd'] for r in known),
      'accounted_usd':accounted(root,episode_id),'unknown_usage_calls':len(list((directory/'calls').glob('*/reservation.json')))-len(known),
      'actual_usage_by_call':[{'call_number':r['call_number'],'usage':r.get('usage'),'tariff_cost_usd':r.get('tariff_cost_usd'),'returned_model':r.get('returned_model')} for r in receipts],
      'history_files':{p.relative_to(directory).as_posix():sha(p) for p in sorted((directory/'calls').rglob('*')) if p.is_file()},
      'private_payload_policy':'Full API output retained privately; no private reasoning extracted into report prose.',
      'no_automatic_retry':True,'host_candidate_selection':False}
    # Runtime paths may be pathlib.Path; serialized relative to episode directory.
    if isinstance(result['selected_candidate_path'],Path):
        selected_path=result['selected_candidate_path'].resolve()
        if not selected_path.is_relative_to(directory.resolve()):
            raise IntegrityError('Selected candidate path leaves episode')
        result['selected_candidate_path']=selected_path.relative_to(directory.resolve()).as_posix()
    write_new(directory/'OUTCOME.json',result)
    return result


def run_episode(episode_id, *, root=ROOT, http_post=None, runtime_factory=None,
                tools=None, test_mode=False):
    root=Path(root).resolve()
    plan, episode, task, instructions, initial_input, rates=config(root,episode_id)
    if test_mode:
        if http_post is None or runtime_factory is None or tools is None:
            raise IntegrityError('Test mode requires all intercepted dependencies; no live fallback')
        auth_headers={'Content-Type':'application/json'}
        secrets=[]
    else:
        if http_post is not None or runtime_factory is not None or tools is not None:
            raise IntegrityError('Injected dependencies require explicit test mode')
        verify_live_gate(root,plan)
        runtime_module=load_module('request_only_tools_runtime',root/'tools_runtime.py')
        runtime_factory=runtime_module.ToolRuntime
        tools=runtime_module.TOOL_DEFINITIONS
        # Read credentials only after launch gate, never in tests or at import.
        helper=load_module('request_only_budget_keys',KEY_HELPER)
        keys=helper.credentials()
        key=keys.get('openai')
        if not key:
            raise IntegrityError('Missing configured OpenAI credential')
        auth_headers=helper.headers('openai',key)
        secrets=[x for x in keys.values() if x]
        import requests
        http_post=requests.post  # requests does not automatically retry this POST.
    if not isinstance(tools,list) or any(t.get('type')!='function' or not isinstance(t.get('name'),str) for t in tools):
        raise IntegrityError('Only dispatched function tools are admitted')
    allowed={t['name'] for t in tools}
    if len(allowed)!=len(tools):
        raise IntegrityError('Duplicate tool definitions')
    directory=root/'episodes'/episode_id
    directory.mkdir(parents=True,exist_ok=True)
    with episode_slot(root,episode_id):
        if (directory/'OUTCOME.json').exists():
            return read(directory/'OUTCOME.json')
        bound={'episode_id':episode_id,'plan_sha256':sha(root/'PLAN.json'),
               'instructions_sha256':sha_bytes(instructions.encode()),'initial_input_sha256':sha_bytes(encoded(initial_input)),
               'tools_sha256':sha_bytes(encoded(tools)),'private_artifacts':True}
        if (directory/'EPISODE_BINDING.json').exists():
            if read(directory/'EPISODE_BINDING.json')!=bound:
                raise IntegrityError('Episode inputs changed across resume')
        else:
            write_new(directory/'EPISODE_BINDING.json',bound)
        # A runtime may rightly reject its own pending journal on construction.
        # Close uncertain operations first, without constructing or replaying it.
        prior=list((directory/'calls').glob('*')) if (directory/'calls').exists() else []
        for folder in prior:
            if not folder.is_dir():
                raise IntegrityError('Unexpected file in call journal')
            if not (folder/'reservation.json').exists() or not (folder/'receipt.json').exists():
                return outcome(root,episode_id,UnavailableRuntime(),'interrupted_http_dispatch',
                               len(list((directory/'calls').glob('*/tool_*.intent.json'))))
            for intent in folder.glob('tool_*.intent.json'):
                if not intent.with_name(intent.name.replace('.intent.','.result.')).exists():
                    return outcome(root,episode_id,UnavailableRuntime(),'interrupted_tool_dispatch',
                                   len(list((directory/'calls').glob('*/tool_*.intent.json'))))
        try:
            runtime=runtime_factory(directory,task,dict(plan['limits']))
        except Exception:
            return outcome(root,episode_id,UnavailableRuntime(),'runtime_initialization_error',
                           len(list((directory/'calls').glob('*/tool_*.intent.json'))))
        history=initial_input
        seen=set()
        actions=0
        limits=plan['limits']
        folders=sorted((directory/'calls').glob('*')) if (directory/'calls').exists() else []
        for n,folder in enumerate(folders,1):
            if not folder.is_dir() or folder.name!=f'{n:04d}':
                raise IntegrityError('Call sequence is not contiguous')
            if not (folder/'reservation.json').exists() or not (folder/'receipt.json').exists():
                return outcome(root,episode_id,runtime,'interrupted_http_dispatch',actions)
            reservation, receipt=read(folder/'reservation.json'),read(folder/'receipt.json')
            expected=request_body(instructions,history,tools,limits)
            if read(folder/'request.json')!=expected or sha(folder/'request.json')!=reservation['request_sha256']:
                raise IntegrityError('Saved request differs from episode-local history')
            if receipt['reservation_sha256']!=sha(folder/'reservation.json'):
                raise IntegrityError('Receipt reservation binding changed')
            if receipt.get('status')!='received':
                return outcome(root,episode_id,runtime,receipt.get('status','invalid_receipt'),actions)
            if sha(folder/'response_raw.json')!=receipt['response_raw_sha256']:
                raise IntegrityError('Response bytes changed')
            data=read(folder/'response_raw.json')
            if (folder/'continuation.json').exists():
                cont=read(folder/'continuation.json')
                if cont['response_sha256']!=sha(folder/'response_raw.json'):
                    raise IntegrityError('Continuation response binding changed')
                for name,h in cont['tool_results'].items():
                    if sha(contained(folder,name))!=h:
                        raise IntegrityError('Saved tool result changed')
                history,actions,stop=cont['input'],cont['action_count'],cont['stop_reason']
                # Reconstruct correspondence rather than trusting a stored input alone.
                expected_history=expected['input']+data['output']
                for p in sorted(folder.glob('tool_*.result.json')):
                    result=read(p)
                    expected_history.append({'type':'function_call_output','call_id':result['call_id'],'output':result['output']})
                if history!=expected_history:
                    raise IntegrityError('Continuation history mismatch')
            else:
                history,actions,stop=advance(folder,history,data,runtime,allowed,actions,limits['max_actions'],seen,secrets)
            seen.update(x['call_id'] for x in data['output'] if isinstance(x,dict) and x.get('type')=='function_call')
            if stop:
                return outcome(root,episode_id,runtime,stop,actions)
        for n in range(len(folders)+1,limits['max_calls']+1):
            if runtime.finalized:
                return outcome(root,episode_id,runtime,'finalized',actions)
            body=request_body(instructions,history,tools,limits)
            folder,stop=reserve(root,episode_id,n,body,limits,rates)
            if stop:
                return outcome(root,episode_id,runtime,stop,actions)
            receipt,data=send_once(folder,http_post,auth_headers,secrets,rates)
            if receipt['status']!='received':
                return outcome(root,episode_id,runtime,receipt['status'],actions)
            history,actions,stop=advance(folder,history,data,runtime,allowed,actions,limits['max_actions'],seen,secrets)
            if stop:
                return outcome(root,episode_id,runtime,stop,actions)
            seen.update(x['call_id'] for x in data['output'] if x.get('type')=='function_call')
        return outcome(root,episode_id,runtime,'call_limit',actions)


def main():
    parser=argparse.ArgumentParser()
    choice=parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--episode',choices=sorted(EPISODE_IDS))
    choice.add_argument('--all',action='store_true')
    args=parser.parse_args()
    ids=[r['episode_id'] for r in read(ROOT/'PLAN.json')['episodes']] if args.all else [args.episode]
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes=list(pool.map(run_episode,ids))
    print(json.dumps([{'episode_id':r['episode_id'],'status':r['status'],
       'selected_candidate':r['selected_candidate'],'accounted_usd':r['accounted_usd']} for r in outcomes]))


if __name__=='__main__':
    main()
