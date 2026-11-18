"""Local credential loader; only the two authorized providers are exposed."""
from pathlib import Path
from dotenv import dotenv_values

def credentials(path=Path('D:/.env')):
    values=dotenv_values(path,interpolate=False)
    return {p:(values.get(k) or '').strip() for p,k in
            [('openai','OPENAI_API_KEY'),('deepseek','DEEPSEEK_API_KEY')]}

def headers(provider,key):
    if provider not in {'openai','deepseek'}:raise ValueError('Provider excluded by economy policy')
    return {'Authorization':'Bearer '+key,'Content-Type':'application/json'}

def redact(value,keys):
    for key in keys:
        if key:value=value.replace(key,'[REDACTED]')
    return value
