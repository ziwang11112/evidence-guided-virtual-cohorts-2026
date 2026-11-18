"""Copy approved unchanged inputs and derive one local budget-limited API client."""
from pathlib import Path
import json
import hashlib

U=Path(__file__).resolve().parent
OLD=U.parent/'cross_model_api_pilot_2026-11-10'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,b):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(b)

def main():
    copied={}
    for rel in ['packets/common_prompt.txt','packets/ASSEMBLY_MANIFEST.json',
        'packets/PNS/task.json','packets/PNS/requested_analyses.json','packets/PNS/evidence.json','packets/PNS/prompt.txt',
        'packets/LIPID/task.json','packets/LIPID/requested_analyses.json','packets/LIPID/evidence.json','packets/LIPID/prompt.txt',
        '_host_only/REFERENCE_SNAPSHOT.json']:
        src=OLD/rel;put(U/rel,src.read_bytes());copied[rel]={'from':str(src),'sha256':sha(src)}
    code=(OLD/'provider_client.py').read_text(encoding='utf-8')
    code=code.replace('from provider_preflight import credentials, headers, redact','from budget_keys import credentials, headers, redact')
    code='\n'.join(line for line in code.split('\n') if not line.startswith(" 'CL_FABLE':") and not line.startswith(" 'GE_CARBON':"))
    code=code.replace("CAPS={'openai':20.,'anthropic':15.,'gemini':10.,'deepseek':5.}","CAPS={'openai':8.,'deepseek':2.}")
    code=code.replace(".glob('*/reservation.json')",".rglob('reservation.json')")
    code=code.replace("write_text(prompt,encoding='utf-8')","write_text(prompt,encoding='utf-8',newline='\\n')")
    code=code.replace("write_text(cleaned,encoding='utf-8')","write_text(cleaned,encoding='utf-8',newline='\\n')")
    code=code.replace("write_text(text,encoding='utf-8')","write_text(text,encoding='utf-8',newline='\\n')")
    put(U/'provider_client.py',code.encode())
    manifest={'copied_files':copied,'client_parent':str(OLD/'provider_client.py'),
        'client_parent_sha256':sha(OLD/'provider_client.py'),'new_client_sha256':sha(U/'provider_client.py'),
        'modifications':['two-provider credential reader','three model configurations only','provider caps8+2USD',
            'combined initial/review ledger','explicit LF text capture'],
        'old_frozen_files_modified':False,'provider_calls':0}
    put(U/'INPUT_ASSEMBLY.json',json.dumps(manifest,indent=2).encode())
    print(json.dumps({'input_files':len(copied),'api_calls':0,'client_sha256':sha(U/'provider_client.py')}))

if __name__=='__main__':main()
