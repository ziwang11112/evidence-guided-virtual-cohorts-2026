"""One-time reviewed pre-session tool-boundary amendment; no candidate changes."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
BUNDLE=HERE.parents[3]/'evcSrcR01'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (BUNDLE/'adaptive_session_v2').exists()
    assert not list((BUNDLE/'candidates').glob('*/freeze.json'))
    task_path=BUNDLE/'task.json';request_path=BUNDLE/'request.json'
    before={p.name:sha(p) for p in (task_path,request_path)}
    task=json.loads(task_path.read_text())
    task['information_policy']['allowed_tools']=[x for x in task['information_policy']['allowed_tools'] if not x.startswith('literature.')]
    request=json.loads(request_path.read_text());request['task']=task
    for p,v in [(task_path,task),(request_path,request)]:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
    note=BUNDLE/'input/ACQUISITION_BOUNDARY.md'
    note.write_text('# Single acquisition allowance\n\nThe current task enables web.fetch only for body acquisition, through the one adaptive-session web_evidence ledger with five total HTTP requests. There is no parallel literature query/download allowance. Native definition discovery is available through root dispatch only, shares the remaining five-request envelope, and must be recorded before use with actual gateway requests; no discovery has been used in this unit. The task budget fields are ceilings, not independently spendable allowances. Existing originals were copied from audited local files and consume no new download allowance.\n',encoding='utf-8')
    receipt={'scope':'pre-session setup amendment; current task/request authoritative over intake-time generated prose',
             'reason':'Prevent separate literature and web ledgers from multiplying remaining acquisition allowance',
             'before':before,'after':{p.name:sha(p) for p in (task_path,request_path)},'new_acquisition':0}
    with (HERE/'SETUP_AMENDMENT.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
    print(json.dumps(receipt))

if __name__=='__main__':main()
