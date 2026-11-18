"""Create the new root-owned paired protocol inputs; no API or generator execution."""
from pathlib import Path
import json
import shutil
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'request_only_repeatability_2026-11-11'

def put(path,obj):
    with path.open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,ensure_ascii=False)

def main():
    old=json.loads((OLD/'PLAN.json').read_text(encoding='utf-8'))
    requirements=json.loads((ROOT/'analysis_requirements.json').read_text(encoding='utf-8'))
    for folder in ['tasks','requests']:
        (ROOT/folder).mkdir(exist_ok=True)
        for name in ['PNS','LIPID']:
            source=OLD/folder/(name+('.json' if folder=='tasks' else '.txt'))
            dest=ROOT/folder/source.name
            if folder=='tasks':
                task=json.loads(source.read_text(encoding='utf-8'))
                task['budget']={'source_queries':8,'source_downloads':6,'revisions':3}
                if dest.exists():assert json.loads(dest.read_text(encoding='utf-8'))==task
                else:put(dest,task)
            elif dest.exists():assert dest.read_bytes()==source.read_bytes()
            else:shutil.copyfile(source,dest)
    for name in ['TARIFF_VERIFICATION.json','MODEL_AVAILABILITY.json']:
        dest=ROOT/name
        if not dest.exists():shutil.copyfile(OLD/name,dest)
    limits=dict(old['limits'])
    limits.update(max_calls=24,episode_usd_cap=2.0,total_usd_cap=48.0,max_actions=24,
                  source_queries=8,source_downloads=6,max_queries=8,max_downloads=6,
                  max_executions=3,max_runs=3,max_candidates=3)
    groups={case:sorted([e for e in old['episodes'] if e['case_id']==case],key=lambda e:e['episode_id']) for case in ['PNS','lipids']}
    initial=[e for pair in zip(groups['PNS'],groups['lipids']) for e in pair]
    episodes=[]
    for i,origin in enumerate(initial,1):
        pair_id=f'R{i:02d}'
        ids=['bmi_sbp','bmi_dbp','residual_correlation'] if origin['case_id']=='PNS' else ['K02-TC-BMI','K02-HDL-BMI','K02-LIPID-RESIDUAL']
        for arm in ['generic','structured']:
            episodes.append(dict(episode_id=pair_id+'_'+arm.upper(),pair_id=pair_id,
                case_id=origin['case_id'],arm=arm,block=(i+1)//2,
                task_path=origin['task_path'],request_path=origin['request_path'],
                policy_path=f'policies/{arm}.txt',imported_package_path=f'imports/{pair_id}/package.json',
                requested_analysis_ids=ids,analysis_requirements=requirements[origin['case_id']]))
    now=datetime.now(timezone.utc).isoformat()
    plan=dict(schema_version=1,version='scientific_check_revision_v1',status='prepared_pending_independent_review',
        created_utc=now,model=old['model'],limits=limits,episodes=episodes,
        common_instructions_path='policies/common.txt',evaluation_seeds=old['evaluation_seeds'],
        design='All12 frozen starting laws, paired generic versus structured review; developmental correction pilot',
        max_concurrent_episodes=2,max_final_tables=72,final_rows_per_table=3000,automatic_http_retries=0,
        source_scope=old['source_scope'],reference_role='Previously exposed references; no target feedback to review Agents',
        no_new_patient_access=True,no_new_target_fits=True,no_initial_evidence=False,
        n_blocks=6,block_size=4,starting_laws=12,review_arms=['generic','structured'],
        source_unit=OLD.name,initial_final_tables='Evaluator-only pinned original36tables; not imported to Agent',
        construction_gate='All24 terminal before final sampling/clinical comparison; operational gate afterblock1',
        experiment_scope='Revision mechanism, not a replacement of the request-only end-to-end experiment',
        tariff_basis='Same-day official verification inherited without rate or model substitution',
        scientific_parameters_authored_by='API review Agent only; root supplies no numeric target relationships')
    plan['analysis_requirements_path']='analysis_requirements.json'
    plan['task_metadata_change']='Only budget fields:8queries6downloads3revisions;scientifictaskfieldsunchanged'
    put(ROOT/'PLAN.json',plan)
    put(ROOT/'STATE.json',dict(status='implementation_and_independent_preflight',created_utc=now,updated_utc=now,
        planned_sessions=24,starting_laws=12,paid_sessions_started=0,known_tariff_usd=0,
        maximum_new_unit_usd=48,target_comparisons_opened=False,no_paid_launch_before_root_freeze=True))
    print(json.dumps({'episodes':len(episodes),'pairs':12,'old_to_new_order':[e['episode_id'] for e in initial]}))

if __name__=='__main__':main()
