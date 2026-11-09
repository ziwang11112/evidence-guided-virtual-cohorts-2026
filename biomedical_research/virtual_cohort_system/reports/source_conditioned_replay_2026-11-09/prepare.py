"""Prepare a fresh source-only task; no previous candidate or outcome copying."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
WORKSPACE=PROJECT.parents[1]
sys.path.insert(0,str(PROJECT))
from cohort_harness.request_intake import prepare_request
from cohort_harness import lifecycle, execution

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f: json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')

def main():
    prior=PROJECT/'work/conditional_evidence_2026-11-09'
    assert sha(prior/'FOLLOW_ON_SPEC.md')=='ba5877270281ee350d55aae367793fcd3d8f8ce48af2b5fe3f132ecc579c1b06'
    old=WORKSPACE/'evcUseR02'; bundle=WORKSPACE/'evcSrcR01'
    task=read(old/'task.json')
    task['task_id']='source-conditioned-whole-cohort-development-2026-11-09'
    task['budget']={'source_queries':5,'source_downloads':5,'revisions':1}
    task['information_policy']['allowed_tools']=[x for x in task['information_policy']['allowed_tools'] if not x.startswith('literature.')]
    task['information_policy']['allowed_tools'].append('whole_cohort_source_replay_v1')
    request={'schema_version':1,
       'purpose':'Source-only developmental experiment: construct analyzable virtual lipid cohorts from published evidence, using explicitly linked source and target population laws. No individual input, no target-reference comparison, and no desired target effect supplied. Author declares measurement/latent interpretation and transport assumptions.',
       'analyses':['Unweighted OLS HDL on intercept, age, sex F/M and raw BMI; report BMI coefficient in mg/dL per5kg/m2.',
                   'Unweighted OLS TC on the same design and units.',
                   'Pearson correlation of paired TC/HDL residuals after those same age/sex/BMI models.'],
       'task':task}
    prepare_request(request,bundle)
    artifacts=[]
    for item in read(old/'registry.json')['artifacts']:
        src=old/item['path']; assert sha(src)==item['sha256']
        rel=item['path'].replace('sources/web_evidence_v1/','sources/curated/inherited_web_v1/')
        dst=bundle/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        artifacts.append({**item,'path':rel,'origin':'curator'})
    originals={
       'Soares2019':['source_bodies_associations/Soares2019.xml','source_bodies_associations/Soares2019_supp.pdf'],
       'Soares2020':['source_bodies_associations/Soares2020.xml','source_bodies_associations/Soares2020_supp.pdf'],
       'Liu2023':['sources_local_joint/lipidomic_aging.xml','sources_local_joint/ACEL-22-e13934-s001.docx']}
    for sid,paths in originals.items():
        for rel in paths:
            src=prior/rel;dst=bundle/'sources/curated'/sid/src.name
            dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
            artifacts.append({'source_id':sid,'path':dst.relative_to(bundle).as_posix(),'sha256':sha(dst),'origin':'curator','screening':'approved'})
    (bundle/'registry.json').write_text(json.dumps({'artifacts':artifacts},indent=2)+'\n',encoding='utf-8')
    (bundle/'input').mkdir()
    for name in ('association_inventory.json','joint_inventory.json','INDEPENDENT_EVIDENCE_REVIEW.json','FOLLOW_ON_SPEC.md'):
        shutil.copyfile(prior/name,bundle/'input'/name)
    shutil.copytree(Path('D:/Codex/home/skills/evidence-cohort-generation'),bundle/'skills/evidence-cohort-generation')
    note='''# New source-conditioned construction

The source registry has been populated by the host with previously audited originals; the intake-time empty-registry note is historical setup provenance. Read the current registry and source-only input files.

No prior scientific candidate, generated table or clinical-reference outcome is supplied. All structures and scientific parameter choices belong to the author. The same code/specification will produce source and target laws through explicit declared shared/population-specific components. A branch on population name alone is not evidence transfer: explain the shared link.

Declare measured versus underlying lipid interpretation and any observation mapping. The same-specimen HDL<=TC concentration relation is a diagnostic whose applicability depends on that declaration; it is not proof about noisy independently measured assays. Preserve all output rows and original requested analyses.

The constructor does not receive requested target-use results until its final retain/revise decision is sealed. Source diagnostics and implementation/coherence checks are allowed. Use the new source replay adapter only after the host provides its reviewed interface; never locally execute the generator as a fallback. The program may read the read-only staged /input/task.json to select context/population, schema and row count while retaining generate(observed,spec,seed). Do not inspect host paths.
'''
    (bundle/'SETUP_NOTES.md').write_text(note,encoding='utf-8')
    contract=read(old/'input/use_contract.json')
    interpretation='Virtual lipid values in mmol/L; author must declare measured-assay versus underlying concentration interpretation and source-to-target measurement mapping.'
    for a in contract['analyses']:a['estimand']['measurement']=interpretation
    contract['coherence_rules'][0]['measurement_interpretation']='Applies to underlying same-specimen concentrations; applicability to independently measured assay outputs is author-declared and reviewed.'
    write(bundle/'input/use_contract.json',contract)
    shutil.copyfile(old/'input/rule_basis.json',bundle/'input/rule_basis.json')
    # No source-law or clinical parameters are supplied by this setup.
    protocol={'unit':HERE.name,'bundle':str(bundle),'status':'setup_not_frozen',
       'scientific_source_spec_sha256':sha(prior/'FOLLOW_ON_SPEC.md'),
       'source_only':True,'target_reference_access':'none','candidate_names':['initial','revised'],
       'target_seeds':[9701,9702,9703],'source_seeds':[19701,19702,19703],
       'target_rows':3000,'target_table_cap_all_alternatives':6,
       'source_evaluation_cap':24,'source_rows_per_evaluation_cap':10000,'objective_evaluation_cap':200,
       'source_context_ids_allowed':['source_main','source_alt1','source_alt2','source_alt3'],
       'discovery_requests_remaining':5,'parent_total_discovery_cap':24,'parent_requests_already_charged':19,
       'parent_source_bytes_cap':104857600,'parent_original_source_bytes_already_charged':5838353,
       'required_analyses':contract['analyses'],'runtime':execution.DEFAULT_RUNTIME,
       'execution_limits':{'timeout_seconds':60,'memory_mb':1536,'output_bytes':20000000,'log_bytes':50000},
       'evaluation_boundary':'All target-like requested-use results withheld until both scientific stages are frozen; source/coherence feedback only before then.',
       'source_to_target_link':'Explicitly author-declared shared versus population-specific components, verified in submitted code/spec; assumptions retained.',
       'scope':'Developmental source-consistency exploration, no new clinical validation or overall quality-gain claim'}
    write(HERE/'PROTOCOL.json',protocol)
    write(HERE/'STATE.json',{'phase':'fresh_task_prepared_engine_and_author_in_progress','bundle':str(bundle),'new_target_reads':False,'source_evaluations':0,'target_executions':0,'new_downloads':0})
    runtime=execution._runtime_manifest(execution.DEFAULT_RUNTIME)
    write(HERE/'RUNTIME_PREFLIGHT.json',runtime)
    lifecycle._registry(bundle)
    print(json.dumps({'bundle':str(bundle),'source_artifacts':len(artifacts),'runtime':'verified_known_files','no_previous_candidates_copied':True}))

if __name__=='__main__':main()
