"""Bind actual static-only check records; no generator import or execution."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
P=ROOT/'biomedical_research/virtual_cohort_system'
D=P/'work/source_increment_revision_2026-11-05'
C=ROOT/'evcIncE01/candidates/source_increment'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks=read(C/'checks.json')
for name,record_name in [('STATIC_VALIDATION_01.json','static_contract_validation'),('SEMANTIC_PREFLIGHT_01.json','semantic_feedback_v1_preflight')]:
    actual=read(D/name)
    assert actual['exit_code']==0
    shutil.copyfile(D/name,C/'static'/name)
    checks['artifacts'].append({'path':'static/'+name,'sha256':sha(C/'static'/name)})
    checks['records'].append({'name':record_name,'status':'pass','detail':'Actual authorized declaration-only command exited0; complete command/output bound in static/'+name+'. No generator execution and no scientific validity certification.'})
shutil.copyfile(D/'BUILD_ATTEMPT_01.json',C/'static/BUILD_ATTEMPT_01.json')
checks['artifacts'].append({'path':'static/BUILD_ATTEMPT_01.json','sha256':sha(C/'static/BUILD_ATTEMPT_01.json')})
checks['records'].append({'name':'initial_build_directory_guard','status':'fail','detail':'Initial artifact builder rejected controller-created empty candidate directory before writing files; preserved static/BUILD_ATTEMPT_01.json. Guard was corrected to allow only an existing empty directory; completed construction and static validation subsequently passed. No generator/execution repair or scientific change occurred.'})
inputs=[D/'NEW_BUNDLE.json',D/'REVIEW.md',ROOT/'evcIncE01/task.json',ROOT/'evcIncE01/request.json',ROOT/'evcIncE01/registry.json',ROOT/'evcIncE01/SOURCE_INCREMENT_ADMISSION.json',P/'cohort_harness/contracts.py',ROOT/'evcRepE01/candidates/initial/whole_cohort_feedback.json',P/'docs/SEMANTIC_FEEDBACK_V1.md',P/'docs/WHOLE_COHORT_FEEDBACK.md',ROOT/'evcRepE01/sources/gateway/b4f5cd47d62879840dc389a99c671814bf9890f9f8b01260e8c7a910dd92e9a6.xml',ROOT/'evcRepE01/candidates/initial/model_spec.json',ROOT/'evcRepE01/candidates/initial/evidence.json',ROOT/'evcRepE01/candidates/initial/generator.py']
inputs += [D/name for name in ('PROPOSAL.md','PROPOSAL.json','PROPOSAL_CALCULATIONS.json','proposal_constant_calculations.py','PROPOSAL_READ_INTEGRITY.json')]
read_record={'scope':'Stage2 actual scientific/interface inputs read or copied; stage1 list remains in static/PROPOSAL.json. Trusted validators internally read candidate and admitted bundle metadata; no target or prior computed-feedback access.','files':[{'path':str(p),'sha256':sha(p)} for p in inputs],'Kerman_XML_scope':'Only Table T0001 and RESULTS paragraphs displayed to author ordinary source-statistic semantics; no parameter or evidence endpoint added from that read.','network_used':False,'generator_imported_or_executed':False,'freeze_performed':False}
(C/'static/IMPLEMENTATION_INPUT_READS.json').write_text(json.dumps(read_record,indent=2)+'\n',encoding='utf-8')
checks['artifacts'].append({'path':'static/IMPLEMENTATION_INPUT_READS.json','sha256':sha(C/'static/IMPLEMENTATION_INPUT_READS.json')})
(C/'checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
preflight=json.loads(read(D/'SEMANTIC_PREFLIGHT_01.json')['output'])
counts={}
for entry in preflight['checks']:
    key=entry['semantic_status']; counts[key]=counts.get(key,0)+1
print(json.dumps({'status':'static_reports_bound','semantic_status_counts':counts,'generator_sha256':sha(C/'generator.py'),'checks_sha256':sha(C/'checks.json')},indent=2))
