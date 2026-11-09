"""Lock reviewed infrastructure and start new target-session; no generation."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
sys.path.insert(0,str(PROJECT))
from cohort_harness import adaptive_session_v2 as session

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2);f.write('\n')

def main():
    protocol=read(HERE/'PROTOCOL.json');bundle=Path(protocol['bundle'])
    reviewed=read(HERE/'IMPLEMENTATION_REVIEW.json')
    if reviewed['remaining_blockers']:raise ValueError('Outstanding independent implementation issues')
    for path,expected in reviewed['reviewed_code_hashes'].items():
        if sha(Path(path))!=expected:raise ValueError('Reviewed code changed: '+path)
    generated_deps=[PROJECT/'work/evidence_use_cross_task_2026-11-05/lipid_provider.py',PROJECT/'work/scaleup_2026-11-01/analysis/k02_analysis.py']
    use_deps=[PROJECT/'cohort_harness/analysis_use_v1.py',PROJECT/'cohort_harness/analysis_evidence.py',bundle/'input/use_contract.json']
    config={'schema_version':2,'limits':{'actions':64,'candidates':2,'executions':6,'feedbacks':6,'analyses':12},
        'allowed_seeds':protocol['target_seeds'],'runtime':protocol['runtime'],
        'execution_limits':protocol['execution_limits'],
        'analysis_adapters':{},
        'web_evidence':{'response_bytes':16777216,'extracted_bytes':8388608,'total_bytes':104857600-5838353,
                        'http_requests':5,'timeout_seconds':30,'max_redirects':0,'pdf_pages':300}}
    for name,file,deps in [('generated','generated_analysis.py',generated_deps),('analysis_use','analysis_use_adapter.py',use_deps)]:
        adapter=HERE/file
        config['analysis_adapters'][name]={'path':str(adapter),'function':'analyze','sha256':sha(adapter),'dependencies':{str(p):sha(p) for p in deps}}
    write(HERE/'SESSION_CONFIG.json',config)
    files=[HERE/'PROTOCOL.json',HERE/'start_session.py',HERE/'act.py',HERE/'generated_analysis.py',HERE/'analysis_use_adapter.py',
           PROJECT/'cohort_harness/whole_cohort_source_replay_v1.py',HERE/'IMPLEMENTATION_REVIEW.json']
    write(HERE/'DESIGN_LOCK.json',{'files':{str(p):sha(p) for p in files},'scope':'Source-only generated-data exploration; no clinical-reference evaluation'})
    write(HERE/'SESSION_CREATED.json',session.create_session(bundle,config))
    result=session.verify_session(bundle)
    write(HERE/'SESSION_VERIFIED.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
