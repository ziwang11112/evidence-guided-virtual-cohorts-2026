"""Root approval for the new bounded unit, after independent preflight."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import api_loop as launch
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
review=json.loads((R/'PREFLIGHT_REVIEW.json').read_text(encoding='utf-8'))
assert review['status']=='pass'
plan=json.loads((R/'PLAN.json').read_text(encoding='utf-8'))
files={**review['reviewed_files'],'PREFLIGHT_REVIEW.json':sha(R/'PREFLIGHT_REVIEW.json')}
assert all(sha(R/n)==h for n,h in files.items())
freeze=dict(created_utc=datetime.now(timezone.utc).isoformat(),files=files,external_files=review['reviewed_external_files'],credential_helper_sha256=review['credential_helper_sha256'])
write(R/'LAUNCH_FREEZE.json',freeze)
write(R/'ROOT_EXECUTION_APPROVAL.json',dict(status='approved',created_utc=datetime.now(timezone.utc).isoformat(),
    purpose='Execute exactly two independently reviewed fresh scientific Agent constructions and six final draws; no new real lifestyle results until closure.',
    launch_freeze_sha256=sha(R/'LAUNCH_FREEZE.json'),plan_sha256=sha(R/'PLAN.json'),episodes=[r['episode_id'] for r in plan['episodes']],files=files))
launch.verify_live_gate(R,plan)
print('New launch freeze and root approval valid; no API call made')
