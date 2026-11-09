"""Export a finite public allowlist of original code and aggregate reports only."""
from pathlib import Path
import base64, hashlib, json, shutil

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
PREFIX='biomedical_research/virtual_cohort_system/'

def main():
    review=json.loads((HERE/'FINAL_RESULT_REVIEW.json').read_text(encoding='utf-8-sig'))
    if review['remaining_blockers']:raise ValueError('Reporting review blockers remain')
    destination=HERE/'_local_only/public_export'
    destination.mkdir(parents=True,exist_ok=False)
    entries=[]
    def add(source,relative):
        raw=source.read_bytes()
        if source.suffix.lower()=='.md':
            raw=raw.decode('utf-8-sig').replace('../work/','../reports/').encode('utf-8')
        path=destination/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        entries.append({'path':PREFIX+relative,'local_export':str(path),'bytes':len(raw),
            'sha256':hashlib.sha256(raw).hexdigest(),
            'git_blob_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()})
    for relative in ['cohort_harness/whole_cohort_source_replay_v1.py',
                     'tests/test_whole_cohort_source_replay_v1.py',
                     'docs/WHOLE_COHORT_SOURCE_REPLAY_V1.md',
                     'docs/WHOLE_COHORT_SOURCE_REPLAY_V1_VALIDATION.md',
                     'docs/CURRENT_RESEARCH_FOCUS.md']:
        add(PROJECT/relative,relative)
    unit='reports/'+HERE.name+'/'
    names=['RESULTS.md','RESULTS.json','STATE.json','PROTOCOL.json','MANUSCRIPT_INSERT.md',
           'IMPLEMENTATION_REVIEW.md','IMPLEMENTATION_REVIEW.json','SOURCE_OPERATOR_REVIEW.md',
           'SCIENTIFIC_CANDIDATE_REVIEW.md','SCIENTIFIC_CANDIDATE_REVIEW.json',
           'INITIAL_SOURCE_FEEDBACK.json','INITIAL_SOURCE_INDEPENDENT.json','TARGET_INDEPENDENT.json',
           'AUTHOR_SEALED.json','FINAL_SESSION.json','FINAL_RESULT_REVIEW.md','FINAL_RESULT_REVIEW.json',
           'prepare.py','amend_unfrozen_setup.py','start_session.py','act.py','run_source_stage.py',
           'summarize_source.py','seal_author.py','run_sealed_outputs.py','prepare_target_manifest.py',
           'independent_verify.py','generated_analysis.py','analysis_use_adapter.py','finalize.py',
           'plot_source_results.py','prepare_public.py']
    for name in names:add(HERE/name,unit+name)
    bundle=Path(json.loads((HERE/'PROTOCOL.json').read_text())['bundle'])
    add(bundle/'author_final_decision.json',unit+'author_final_decision.json')
    for name in ['generator.py','model_spec.json','source_to_target_link.json','scientific_design.md',
                 'calculation_budget.json','analytic_sensitivity.json']:
        add(bundle/'candidates/initial'/name,unit+'candidate_initial/'+name)
    for name in ['source_relationships','joint_assumption_sensitivity']:
        for ext in ['png','svg','pdf']:
            add(HERE/'figures'/(name+'.'+ext),unit+'figures/'+name+'.'+ext)
    manifest=HERE/'_local_only/public_manifest.json'
    manifest.write_text(json.dumps(entries,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(entries),'bytes':sum(x['bytes'] for x in entries),
                      'excluded':'Individual real/generated tables, complete original papers, raw session logs and credentials'}))

if __name__=='__main__':main()
