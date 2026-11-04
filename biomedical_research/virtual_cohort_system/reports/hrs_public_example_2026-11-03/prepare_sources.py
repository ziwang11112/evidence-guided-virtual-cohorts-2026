"""Register pinned aggregate sources after exact local hash verification."""
from pathlib import Path
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
BUNDLE = HERE / 'bundle'
manifest = json.loads((HERE / 'sources/SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
artifacts = []
checks = []
for item in manifest['files']:
    original = HERE / item['path']
    data = original.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert len(data) == item['bytes'] and sha == item['sha256']
    assert blob == item['git_blob_sha1'] and item['git_blob_verified']
    destination = BUNDLE / item['path']
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(original, destination)
    artifacts.append({'source_id': 'FILSHSTEIN_HRS_PUBLIC', 'path': item['path'],
                      'sha256': sha, 'origin': 'curator', 'screening': 'approved'})
    checks.append({'path': item['path'], 'sha256': sha, 'git_blob_sha1': blob,
                   'bytes': len(data), 'verified': True})
(BUNDLE / 'registry.json').write_text(json.dumps({'artifacts': artifacts}, indent=2) + '\n', encoding='utf-8')
(BUNDLE / 'SOURCE_METADATA.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
(HERE / 'SOURCE_REGISTRATION_REVIEW.json').write_text(json.dumps({
    'scope': 'Identity and admissibility of public aggregate/model artifacts; no scientific truth certification',
    'coordinator': 'root', 'checks': checks,
    'total_source_bytes': sum(c['bytes'] for c in checks),
    'participant_source_records': 0,
    'approved_source_id': 'FILSHSTEIN_HRS_PUBLIC'
}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'registered_files': len(checks), 'source_bytes': sum(c['bytes'] for c in checks)}))
