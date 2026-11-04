"""Retrieve pinned public source artifacts locally, never participant records.

Optional reproduction helper; does not execute or register a new experiment.
"""
from pathlib import Path
import hashlib
import json
import shutil
import urllib.request

U=Path(__file__).resolve().parent
manifest=json.loads((U/'sources/SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
for item in manifest['files']:
    path=U/item['path']
    if path.exists():
        data=path.read_bytes()
    else:
        name=Path(item['path']).name
        url='https://raw.githubusercontent.com/'+manifest['repository']+'/'+manifest['commit']+'/'+name
        with urllib.request.urlopen(url,timeout=30) as response:
            data=response.read(1_000_001)
        assert len(data)<=1_000_000
        assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as target:target.write(data)
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
    for folder in ['bundle','recovery_v1/bundle']:
        destination=U/folder/item['path']
        if destination.exists():
            assert destination.read_bytes()==data
        else:
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(path,destination)
print('Pinned public aggregate/method source bytes available locally; no experiment executed.')
