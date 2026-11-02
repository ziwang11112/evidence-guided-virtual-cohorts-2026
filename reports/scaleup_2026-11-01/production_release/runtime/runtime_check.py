"""Prospective supplemental runtime identity. No generator or participant input."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
VENV = '/home/zwang/.cache/evidence-cohort-runtime/m2/venv'
SCRIPT = r'''
import hashlib,importlib.metadata as md,json,pathlib,platform,sys
import numpy,pandas,scipy,scipy.special._ufuncs
distributions={}
for name in ('numpy','pandas','scipy'):
    dist=md.distribution(name)
    files={str(f):hashlib.sha256(pathlib.Path(dist.locate_file(f)).read_bytes()).hexdigest()
           for f in dist.files if pathlib.Path(dist.locate_file(f)).is_file()}
    raw=json.dumps(files,sort_keys=True,separators=(',',':')).encode()
    distributions[name]={'version':dist.version,'file_count':len(files),'file_inventory_sha256':hashlib.sha256(raw).hexdigest()}
paths=[pathlib.Path(sys.executable).resolve(),pathlib.Path(sys.prefix)/'pyvenv.cfg',pathlib.Path(scipy.special._ufuncs.__file__),pathlib.Path('/home/zwang/.cache/evidence-cohort-runtime/m2/bubblewrap/usr/bin/bwrap')]
print(json.dumps({'python':platform.python_version(),'distributions':distributions,'critical_files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}},sort_keys=True))
'''

def capture():
    result = subprocess.run(['wsl.exe','--distribution','Ubuntu-24.04','--exec',
        VENV+'/bin/python','-I','-B','-c',SCRIPT],capture_output=True,check=True,timeout=60)
    manifest=json.loads(result.stdout)
    expected={'numpy':'2.4.5','pandas':'3.0.3','scipy':'1.16.3'}
    if {k:v['version'] for k,v in manifest['distributions'].items()} != expected:
        raise ValueError('Runtime dependency versions differ from prospective release')
    return manifest

def verify(path=HERE/'RUNTIME_IDENTITY.json'):
    expected=json.loads(Path(path).read_text(encoding='utf-8'))
    actual=capture()
    if actual != expected:
        raise ValueError('Released runtime identity changed')
    return {'status':'verified','runtime_identity_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}

if __name__=='__main__':
    if sys.argv[1:] == ['capture']:
        with (HERE/'RUNTIME_IDENTITY.json').open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(capture(),stream,indent=2);stream.write('\n')
        print('Prospective runtime identity captured; no cohort executed.')
    else:
        print(json.dumps(verify()))
