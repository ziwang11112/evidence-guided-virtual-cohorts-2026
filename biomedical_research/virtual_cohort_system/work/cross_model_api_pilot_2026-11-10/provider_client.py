"""Bounded provider requests with secret-free payloads and durable cost records.

This module does not execute generated code and never retries a request.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import threading
import time
import requests
from provider_preflight import credentials, headers, redact

HERE=Path(__file__).resolve().parent
MAX_OUTPUT=32768
SYSTEM='You are a scientific model author. Follow the supplied biomedical task and evidence boundary. Return the requested executable artifacts and concise scientific decision record, not a private reasoning transcript.'
CONFIGS={
 'OA_ASTRA':{'provider':'openai','model':'gpt-6-astra','input_rate':10.,'output_rate':50.,'cached_rate':1.,'cache_write_rate':12.5,'effort':'high'},
 'OA_SOL':{'provider':'openai','model':'gpt-6.1-sol','input_rate':2.,'output_rate':10.,'cached_rate':.1,'cache_write_rate':2.5,'effort':'high'},
 'DS_PRO':{'provider':'deepseek','model':'deepseek-v4-pro','input_rate':1.32,'output_rate':3.96,'cached_rate':.044,'effort':'high'},
 'CL_FABLE':{'provider':'anthropic','model':'claude-fable-5-2','input_rate':8.,'output_rate':40.,'cached_rate':.2,'cache_write_rate':10.,'effort':'high'},
 'GE_CARBON':{'provider':'gemini','model':'gemini-4-carbon','input_rate':2.,'output_rate':10.,'cached_rate':.1,'effort':'HIGH'},
}
CAPS={'openai':20.,'anthropic':15.,'gemini':10.,'deepseek':5.}
LOCK=threading.Lock()

def utc():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump_new(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)

def make_request(config,prompt):
    c=CONFIGS[config]; p=c['provider']; model=c['model']
    if p=='openai':
        return 'https://api.openai.com/v1/responses',{'model':model,'instructions':SYSTEM,'input':prompt,'store':False,'reasoning':{'effort':c['effort']},'max_output_tokens':MAX_OUTPUT,'service_tier':'default'}
    if p=='deepseek':
        return 'https://api.deepseek.com/chat/completions',{'model':model,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}],'thinking':{'type':'enabled'},'reasoning_effort':c['effort'],'max_tokens':MAX_OUTPUT,'stream':False}
    if p=='anthropic':
        return 'https://api.anthropic.com/v1/messages',{'model':model,'system':SYSTEM,'messages':[{'role':'user','content':prompt}],'thinking':{'type':'adaptive'},'output_config':{'effort':c['effort']},'max_tokens':MAX_OUTPUT,'stream':False}
    if p=='gemini':
        return 'https://generativelanguage.googleapis.com/v1beta/models/'+model+':generateContent',{'systemInstruction':{'parts':[{'text':SYSTEM}]},'contents':[{'role':'user','parts':[{'text':prompt}]}],'generationConfig':{'maxOutputTokens':MAX_OUTPUT,'thinkingConfig':{'thinkingLevel':c['effort'],'includeThoughts':False}}}
    raise ValueError('Unknown provider')

def extract_response(provider,data):
    if provider=='openai':
        text=''.join(v.get('text','') for item in data.get('output',[]) if item.get('type')=='message' for v in item.get('content',[]) if v.get('type')=='output_text')
        u=data.get('usage') or {}; status=data.get('status'); returned=data.get('model')
        stop=(data.get('incomplete_details') or {}).get('reason')
        norm={'input':u.get('input_tokens'),'output':u.get('output_tokens'),'cached':(u.get('input_tokens_details') or {}).get('cached_tokens',0),'cache_write':(u.get('input_tokens_details') or {}).get('cache_write_tokens',0),'reasoning':(u.get('output_tokens_details') or {}).get('reasoning_tokens')}
    elif provider=='deepseek':
        choice=(data.get('choices') or [{}])[0];text=(choice.get('message') or {}).get('content') or '';u=data.get('usage') or {}; stop=choice.get('finish_reason'); status='completed' if stop=='stop' else 'incomplete';returned=data.get('model')
        norm={'input':u.get('prompt_tokens'),'output':u.get('completion_tokens'),'cached':u.get('prompt_cache_hit_tokens',(u.get('prompt_tokens_details') or {}).get('cached_tokens',0)),'reasoning':(u.get('completion_tokens_details') or {}).get('reasoning_tokens')}
    elif provider=='anthropic':
        text=''.join(v.get('text','') for v in data.get('content',[]) if v.get('type')=='text'); u=data.get('usage') or {};stop=data.get('stop_reason');status='completed' if stop=='end_turn' else 'incomplete';returned=data.get('model')
        norm={'input':u.get('input_tokens'),'output':u.get('output_tokens'),'cached':u.get('cache_read_input_tokens',0),'cache_write':u.get('cache_creation_input_tokens',0),'reasoning':None}
    elif provider=='gemini':
        choice=(data.get('candidates') or [{}])[0];text=''.join(v.get('text','') for v in choice.get('content',{}).get('parts',[]) if not v.get('thought'));u=data.get('usageMetadata') or {};stop=choice.get('finishReason');status='completed' if stop=='STOP' else 'incomplete';returned=data.get('modelVersion')
        thoughts=u.get('thoughtsTokenCount',0);out=u.get('candidatesTokenCount')
        norm={'input':u.get('promptTokenCount'),'output':None if out is None else out+thoughts,'cached':u.get('cachedContentTokenCount',0),'reasoning':thoughts}
    else:raise ValueError(provider)
    return {'text':text,'usage_raw':u,'usage':norm,'completion_status':status,'stop_reason':stop,'returned_model':returned,'response_id':data.get('id',data.get('responseId'))}

def price(config,usage):
    c=CONFIGS[config];p=c['provider'];i=usage.get('input');o=usage.get('output');cached=usage.get('cached',0) or 0
    if i is None or o is None:return None
    if min(i,o,cached)<0:raise ValueError('negative usage')
    if p=='anthropic':
        cost=i*c['input_rate']+cached*c['cached_rate']+(usage.get('cache_write',0) or 0)*c['cache_write_rate']+o*c['output_rate']
    elif p=='openai':
        written=usage.get('cache_write',0) or 0
        if written<0 or cached+written>i:raise ValueError('OpenAI cache token counts exceed total input')
        cost=(i-cached-written)*c['input_rate']+cached*c['cached_rate']+written*c['cache_write_rate']+o*c['output_rate']
    else:
        if cached>i:raise ValueError('cached usage exceeds total input')
        cost=(i-cached)*c['input_rate']+cached*c['cached_rate']+o*c['output_rate']
    return cost/1e6

def parse_artifact(text):
    s=text.strip()
    if s.startswith('```') and s.endswith('```'):
        s=s[s.find('\n')+1:-3].strip()
    def reject_constant(value):raise ValueError('Non-finite JSON value: '+value)
    def unique_pairs(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate JSON key: '+key)
            result[key]=value
        return result
    obj=json.loads(s,parse_constant=reject_constant,object_pairs_hook=unique_pairs)
    if not isinstance(obj,dict) or set(obj)!={'model_spec','generator_py','decision_record'}:
        raise ValueError('Return exactly model_spec, generator_py, decision_record')
    if not isinstance(obj['model_spec'],dict) or not isinstance(obj['decision_record'],dict):
        raise ValueError('model_spec and decision_record must be JSON objects')
    code=obj['generator_py']
    if not isinstance(code,str) or not 1<=len(code.encode('utf-8'))<=200_000:
        raise ValueError('generator_py must be a nonempty string below 200000 bytes')
    tree=ast.parse(code)
    funcs=[f for f in tree.body if isinstance(f,ast.FunctionDef) and f.name=='generate']
    if len(funcs)!=1 or [a.arg for a in funcs[0].args.posonlyargs+funcs[0].args.args]!=['observed','spec','seed'] or funcs[0].args.vararg or funcs[0].args.kwarg or funcs[0].args.kwonlyargs:
        raise ValueError('Define exactly one top-level generate(observed, spec, seed) function')
    if any(isinstance(f,ast.AsyncFunctionDef) and f.name=='generate' for f in tree.body):
        raise ValueError('generate must be synchronous and unique')
    d=obj['decision_record']
    if not {'structure','parameter_provenance','requested_estimands','limitations','checks_actually_performed'}<=set(d):
        raise ValueError('decision_record is missing requested structural fields')
    if not all(isinstance(d[k],list) for k in ['parameter_provenance','requested_estimands','limitations','checks_actually_performed']):
        raise ValueError('decision_record provenance, estimands, limitations and checks must be arrays')
    # Parse only. Do not import or execute untrusted code on the host.
    return obj

def ledger_accounted(root,provider):
    total=0.
    for f in (Path(root)/'calls').glob('*/reservation.json'):
        item=json.loads(f.read_text(encoding='utf-8'))
        if item['provider']!=provider:continue
        receipt=f.with_name('receipt.json')
        if receipt.exists():
            r=json.loads(receipt.read_text(encoding='utf-8'))
            cost=r.get('tariff_cost_usd')
            total+=cost if cost is not None else item['reserved_usd']
        else:total+=item['reserved_usd']
    return total

def call_once(root,call_id,config,prompt):
    root=Path(root); c=CONFIGS[config];provider=c['provider'];keys=credentials(); key=keys[provider]
    if not key:raise ValueError('missing configured credential for '+provider)
    endpoint,body=make_request(config,prompt)
    encoded=json.dumps(body,ensure_ascii=False).encode('utf-8')
    # Byte-based input allowance deliberately overestimates text tokenization;
    # provider-specific hidden processing is not asserted to be exactly matched.
    if len(encoded)>190_000:raise ValueError('Request exceeds frozen short-context input byte ceiling')
    reserved=((len(encoded)+4096)*max(c['input_rate'],c.get('cache_write_rate',0))+MAX_OUTPUT*c['output_rate'])/1e6
    folder=root/'calls'/call_id
    with LOCK:
        used=ledger_accounted(root,provider)
        if used+reserved>CAPS[provider]:raise ValueError('provider project budget exhausted before dispatch')
        folder.mkdir(parents=True,exist_ok=False)
        dump_new(folder/'reservation.json',{'provider':provider,'config':config,'reserved_usd':reserved,'previous_accounted_usd':used,'provider_cap_usd':CAPS[provider],'timestamp_utc':utc(),'cost_status':'conservative_token_allowance_not_invoice'})
        dump_new(folder/'request.json',{'endpoint':endpoint,'body':body})
        (folder/'prompt.txt').write_text(prompt,encoding='utf-8')
    started=utc();t=time.monotonic()
    receipt={'call_id':call_id,'config':config,'provider':provider,'requested_model':c['model'],'started_utc':started,'prompt_sha256':sha(folder/'prompt.txt'),'request_sha256':sha(folder/'request.json'),'tariff_cost_usd':None,'usage':None,'no_automatic_retry':True,'tariff_date':'2026-11-10','tariff':c,'reserved_usd':reserved,'cost_interpretation':'usage-derived published tariff estimate, not provider invoice; DeepSeek uses peak rate as conservative upper tariff'}
    parsed=None
    try:
        with requests.post(endpoint,headers=headers(provider,key),json=body,timeout=(20,1500),allow_redirects=False,stream=True) as r:
            chunks=[];total=0
            for chunk in r.iter_content(65536):
                total+=len(chunk)
                if total>16*1024*1024:raise ValueError('Provider response exceeds capture ceiling')
                chunks.append(chunk)
            raw=b''.join(chunks).decode('utf-8')
            cleaned=redact(raw,keys.values())
            (folder/'response_raw.json').write_text(cleaned,encoding='utf-8')
            receipt.update(http_status=r.status_code,response_bytes=total,secrets_redacted=cleaned!=raw,request_id=r.headers.get('x-request-id',r.headers.get('request-id')))
            data=json.loads(cleaned)
            if not r.ok:
                receipt['status']='api_error'
                err=data.get('error',{})
                receipt['api_error_code']=err.get('code',err.get('type')) if isinstance(err,dict) else None
                receipt['api_error_message']=str(err.get('message',''))[:1500] if isinstance(err,dict) else 'API returned an error'
            else:
                ext=extract_response(provider,data)
                text=ext.pop('text')
                (folder/'response_text.txt').write_text(text,encoding='utf-8')
                receipt.update(ext)
                receipt['tariff_cost_usd']=price(config,ext['usage'])
                receipt['status']='received'
                try:
                    parsed=parse_artifact(text)
                    dump_new(folder/'artifact.json',parsed)
                    receipt['artifact_status']='valid_structure_and_python_ast'
                except (ValueError,SyntaxError,TypeError) as e:
                    receipt['artifact_status']='invalid'
                    receipt['mechanical_error']=str(e)[:1000]
                if ext['completion_status']!='completed':
                    receipt['status']='incomplete_response'
                if receipt['tariff_cost_usd'] is not None and receipt['tariff_cost_usd']>reserved:
                    receipt['reservation_exceeded']=True
    except Exception as e:
        receipt['status']='transport_or_capture_error'
        receipt['error_type']=type(e).__name__
        receipt['error']=redact(str(e)[:1500],keys.values())
    receipt.update(ended_utc=utc(),elapsed_seconds=time.monotonic()-t)
    for name in ['response_raw.json','response_text.txt','artifact.json']:
        if (folder/name).exists():receipt[name+'_sha256']=sha(folder/name)
    with LOCK:
        dump_new(folder/'receipt.json',receipt)
    return receipt,parsed
