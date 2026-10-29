"""Create an inspection-only package with explicit aggregate and code allowlists."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json

E=Path(__file__).resolve().parent;P=E.parents[1];W=P.parents[1]
C=P/'reports/joint_evidence_pilot_2026-10-29'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    C.mkdir(parents=True,exist_ok=False)
    execution_bundle=Path(read(E/'execution_location.json')['bundle'])
    selected=[]
    def add(relative):
        path=E/relative
        if not path.is_file():raise ValueError('Missing intended artifact: '+relative)
        selected.append((path,relative))
    for name in ['prepare_pilot.py','admit_supplement.py','controller.py','release_guard.py',
                 'summarize_pilot.py','curate_pilot.py','pilot_intent.json','baseline_import.json',
                 'supplement_admission.json','protocol_commitment.json','evaluation_design.json',
                 'evaluation_commitment.json','release_verification.json','pre_execution_review.json',
                 'freeze_pilot.py','prepare_short_execution.py','execution_location.json',
                 'execution_path_amendment.json','attempt1/protocol_commitment.json',
                 'attempt1/controller.py','attempt1/release_guard.py',
                 'controller_logs/baseline_80201.json','check_paired_source.py',
                 'source_feedback/AGENT_REVIEW.md','source_feedback/AGENT_REVIEW.json']:
        add(name)
    for name in ['Mikkelsen2023_recovery_report.md','retrieval_log.md','source_artifact_manifest.json',
                 'Mikkelsen2023_joint_evidence.json','Mikkelsen2023_joint_age_BMI_sex_TG.csv']:
        add('research/'+name)
    for name in ['build_candidate.py']:
        add('builder/'+name)
    for name in ['generator.py','model_spec.json','decision.md']:
        add('builder/drafts/overlay_reviewdraft/'+name)
    for name in ['CANDIDATE_AUDIT.md','CANDIDATE_AUDIT.json','SOURCE_TABLE_STATIC_CHECK.json',
                 'PAIRED_SOURCE_NUMERICAL_CHECK.json','POSTRUN_CONCLUSION_AUDIT.md',
                 'POSTRUN_CONCLUSION_AUDIT.json','POSTRUN_CONCLUSION_AUDIT_INITIAL_DRAFT.json']:
        add('review/'+name)
    for variant in ['baseline','joint_evidence']:
        for name in ['generator.py','model_spec.json','evidence.json','decision.md','checks.json',
                     'analysis_evidence.json','source_replay.json','freeze.json']:
            add('agent_bundle/candidates/'+variant+'/'+name)
    for name in ['revision.json','source_checks.json','static_validation.json','unsupported_source_check_result.json']:
        add('agent_bundle/candidates/joint_evidence/'+name)
    add('agent_bundle/task.json');add('agent_bundle/registry.json')
    for name in ['survey_analysis.py','evaluate_committed.py','analysis_protocol.json','test_evaluator.py',
                 'protocol_amendment.json','invented_validation.json','review_receipt.json','README.md']:
        add('evaluation/'+name)
    for name in ['release_receipt.json','reference_analyses.json','endpoint_comparison.csv',
                 'nonestimable.json','interpretation.json','result_hashes.json',
                 'pilot_summary.json','primary_conclusions.png','primary_conclusions.svg']:
        add('evaluation/results/'+name)
    for variant in ['baseline','joint_evidence']:
        add('source_feedback/'+variant+'_portfolio.json')
        for seed in [80201,80202,80203]:
            rel=f'source_replays/{variant}_{seed}/replay.json'
            selected.append((execution_bundle/rel,'execution_bundle/'+rel))
        for seed in [80101,80102,80103]:
            rel=f'executions/{variant}_{seed}/execution.json'
            selected.append((execution_bundle/rel,'execution_bundle/'+rel))
    pairs=[]
    # Preserve scientific/frozen originals locally. Only copied machine paths are normalized.
    replacements=[(str(P),'${PROJECT_ROOT}'),(str(W),'${WORKSPACE_ROOT}'),
        (str(execution_bundle),'${EXECUTION_BUNDLE}'),
        ('${PYTHON312}','${PYTHON312}'),
        ('${CODEX_HOME}','${CODEX_HOME}')]
    for src,rel in selected:
        raw=src.read_bytes();data=raw;changed=False
        if src.suffix.lower() in ['.json','.md','.py','.csv','.svg']:
            text=raw.decode('utf-8-sig')
            for old,new in replacements:
                for sep in ['/', '\\']:
                    base=old.replace('\\','/').replace('/',sep)
                    for _ in range(4):
                        if base in text:text=text.replace(base,new);changed=True
                        base=base.replace('\\','\\\\')
            data=text.encode('utf-8') if changed else raw
        dst=C/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
        if dst.suffix=='.json':read(dst)
        source_relative=src.relative_to(P).as_posix() if src.is_relative_to(P) else '${EXECUTION_BUNDLE}/'+src.relative_to(execution_bundle).as_posix()
        pairs.append({'source_relative':source_relative,'curated_relative':rel,
            'original_sha256':sha(src),'copied_sha256':sha(dst),'machine_paths_normalized':changed})
    readme='''# M8 inspection package

This package contains frozen scientific choices, exact public study-level extraction, aggregate source/target results, reviewer findings, evaluator code and provenance. It excludes all participant-level tables (observed, hidden, generated and source-context rows), full-text articles/supplements, runtime settings and caches. The study-level joint-effect CSV is published aggregate evidence, not patient data.

The earlier overlay draft was never frozen or executed. The final candidate replaces the inherited log interaction; see its decision and review. Candidate freeze hashes refer to full local originals. Machine paths in some inspection copies are normalized with explicit original/copied hashes. Missing source-context, source artifact and auxiliary historical files mean this is not a one-command replay archive.

Read the repository MILESTONE_8_RESULTS.md for conclusions and limitations. All target endpoints and seeds are retained. Repeated seeds measure simulation randomness, not clinical replication or model uncertainty.
'''
    (C/'README.md').write_text(readme,encoding='utf-8')
    provenance={'created_utc':datetime.now(timezone.utc).isoformat(),'inspection_only':True,
        'pairs':pairs,'excluded':['participant rows','source-context rows','full-text source artifacts','runtime settings','caches']}
    (C/'curation_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    manifest={p.relative_to(C).as_posix():sha(p) for p in sorted(C.rglob('*')) if p.is_file()}
    (C/'file_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    code={p.relative_to(P).as_posix():sha(p) for p in sorted((P/'cohort_harness').glob('*.py'))}
    report=P/'MILESTONE_8_RESULTS.md'
    validation={'milestone':'M8','created_utc':datetime.now(timezone.utc).isoformat(),
        'scientific_status':'completed exploratory source-informed structure comparison; see report for mixed findings',
        'report_sha256':sha(report),'readme_sha256':sha(P/'README.md'),
        'curated_manifest_sha256':sha(C/'file_manifest.json'),'curated_files':len(manifest)+1,
        'harness_code_bindings':code,'target_rows':1575,'source_replays':6,'source_generator_executions':12,
        'target_generator_executions':6,'target_endpoint_comparisons':402,
        'new_evaluator_tests':9,'new_harness_core_changes':False,
        'candidate_hashes':{v:sha(E/'agent_bundle/candidates'/v/'freeze.json') for v in ['baseline','joint_evidence']},
        'execution_boundary':'WSL/bubblewrap generator-only; outer Agent tools procedurally restricted',
        'target_feedback_used_for_revision':False,'post_target_candidate_change':False,
        'nonestimable_records':len(read(E/'evaluation/results/nonestimable.json')),
        'historical_evaluator_agent_exposure_disclosed':True,
        'not_established':['ordinary-Agent superiority','independent-cohort validation','calibrated model/transport uncertainty','publication readiness']}
    (P/'m8_validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'curated_files':len(manifest)+1,'manifest_sha256':sha(C/'file_manifest.json'),
                      'validation_sha256':sha(P/'m8_validation.json'),'report_sha256':sha(report)}))

if __name__=='__main__':main()
