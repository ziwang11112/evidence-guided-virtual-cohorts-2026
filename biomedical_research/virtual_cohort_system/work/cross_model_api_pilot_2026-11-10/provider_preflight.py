"""Read credential presence and authenticated model catalogs without generation.

Never print or persist secrets, request headers or environment contents.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import requests
from dotenv import dotenv_values

HERE = Path(__file__).resolve().parent
KEYS = {'openai':'OPENAI_API_KEY', 'deepseek':'DEEPSEEK_API_KEY',
        'anthropic':'ANTHROPIC_API_KEY', 'gemini':'GEMINI_API_KEY'}
ENDPOINTS = {'openai':'https://api.openai.com/v1/models',
             'deepseek':'https://api.deepseek.com/models',
             'anthropic':'https://api.anthropic.com/v1/models',
             'gemini':'https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000'}

def credentials(path=Path('D:/.env')):
    values = dotenv_values(path, interpolate=False)
    return {provider:(values.get(name) or '').strip() for provider,name in KEYS.items()}

def headers(provider, key):
    if provider=='anthropic':
        return {'x-api-key':key,'anthropic-version':'2023-06-01','Content-Type':'application/json'}
    if provider=='gemini':
        return {'x-goog-api-key':key,'Content-Type':'application/json'}
    return {'Authorization':'Bearer '+key,'Content-Type':'application/json'}

def redact(value, keys):
    for key in keys:
        if key:
            value=value.replace(key, '[REDACTED]')
    return value

def main():
    keys=credentials()
    results={'timestamp_utc':datetime.now(timezone.utc).isoformat(),
             'operation':'authenticated_read_only_model_catalogs', 'generation_calls':0,'providers':{}}
    for provider,key in keys.items():
        item={'key_present':bool(key), 'endpoint':ENDPOINTS[provider]}
        if key:
            try:
                r=requests.get(ENDPOINTS[provider],headers=headers(provider,key),timeout=(15,60),allow_redirects=False)
                item['http_status']=r.status_code
                data=r.json()
                if r.ok:
                    raw=data.get('data',data.get('models',[]))
                    item['models']=[{k:m[k] for k in ['id','name','display_name','displayName','version','inputTokenLimit','outputTokenLimit','supportedGenerationMethods'] if k in m} for m in raw]
                    item['has_more']=data.get('has_more',bool(data.get('nextPageToken')))
                else:
                    error=data.get('error',{})
                    item['error_code']=error.get('code',error.get('type')) if isinstance(error,dict) else 'api_error'
                    item['error_message']=redact(str(error.get('message',''))[:600],keys.values()) if isinstance(error,dict) else 'API error'
            except Exception as e:
                item['failure_type']=type(e).__name__
                item['error_message']=redact(str(e)[:600],keys.values())
        results['providers'][provider]=item
        print(json.dumps({'provider':provider,'key_present':item['key_present'], 'http_status':item.get('http_status'),
                          'failure':item.get('error_code',item.get('failure_type')),
                          'models':[m.get('id',m.get('name')) for m in item.get('models',[]) if any(x in m.get('id',m.get('name','')).lower() for x in ['gpt-6','gpt-5','deepseek','claude','gemini-4','gemini-3'])]},ensure_ascii=False),flush=True)
    dest=HERE/'PROVIDER_CATALOGS.json'
    with dest.open('x',encoding='utf-8') as f:json.dump(results,f,indent=2,ensure_ascii=False)

if __name__=='__main__':main()
