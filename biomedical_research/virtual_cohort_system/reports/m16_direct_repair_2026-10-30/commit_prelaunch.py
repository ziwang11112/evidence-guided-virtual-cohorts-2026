"""Bind approved M16 inputs before launching scientific builders; no private outcome read."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json

R=Path(__file__).resolve().parent
P=R.parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    if (R/'prelaunch.json').exists():raise ValueError('Prelaunch already committed')
    files=['PROTOCOL.md','controller.py','BUILDER_TASK.md','SEED_PROVENANCE.md','setup_bundles.py',
           'commit_prelaunch.py','admission/safe_admission_receipt.json','admission/prep_report.json',
           'admission/SOURCE_POLICY_CLARIFICATION.md','admission/target_metadata.md','admission/target_access.json',
           'admission/bundle_preparation.json','visible/observed.csv',
           'review/SELF_CHECK_INDEPENDENT_REVIEW.md','review/PRELAUNCH_REVIEW.md']
    prefixes={}
    for bid in ('b1','b2','b3'):
        base=R/'visible'/bid
        reg=read(base/'bundle/registry.json');prefixes[bid]=reg['artifacts']
        files.extend('visible/'+bid+'/'+rel for rel in ('TASK.md','SEED_PROVENANCE.md','bundle/task.json',
            'bundle/observed.csv','bundle/gateway/config.json','bundle/gateway/binding.json'))
        files.extend('visible/'+bid+'/bundle/'+a['path'] for a in reg['artifacts'])
        if any((base/'bundle/candidates').iterdir()):raise ValueError('Builder output exists before prelaunch')
    code=[P/'cohort_harness'/name for name in ('self_consistency.py','contracts.py','lifecycle.py',
          '__main__.py','source_checks.py','execution.py','literature.py')]
    code.extend(R/'evaluation_code'/name for name in ('evaluator.py','frozen_m15b_estimands.py'))
    safe=read(R/'admission/safe_admission_receipt.json')
    record={'schema_version':1,'kind':'M16_prelaunch','created_utc':datetime.now(timezone.utc).isoformat(),
            'files':{name:sha(R/name) for name in files},'engine_files':{str(p.resolve()):sha(p) for p in code},
            'registry_prefixes':prefixes,'reference':{'path':str(R/'private/custodian/reference.csv'),
            'sha256':safe['reference_sha256']},'reference_weight_column':'WTMEC2YR',
            'reference_content_read':False,'builder_constructions_started':False,
            'independent_reviews':'See bound review documents; technical readiness is not scientific validity'}
    with (R/'prelaunch.json').open('x',encoding='utf-8',newline='\n') as f:
        json.dump(record,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'prelaunch_sha256':sha(R/'prelaunch.json'),'files':len(files),'engines':len(code),
                      'reference_content_read':False}))
if __name__=='__main__':main()
