"""Bind M6 final inspection artifacts without changing earlier milestones."""
from pathlib import Path
import hashlib
import json

E=Path(__file__).resolve().parent
P=E.parents[1]
C=P/'reports/source_identifiability_2026-10-29'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))

def main():
    old=read(P/'m5_validation.json')
    code=dict(old['code_sha256'])
    for name,value in code.items(): assert sha(P/name)==value,name
    for path in sorted(C.rglob('*.py')): code[path.relative_to(P).as_posix()]=sha(path)
    manifest=read(C/'file_manifest.json')
    assert manifest=={p.relative_to(C).as_posix():sha(p) for p in C.rglob('*') if p.is_file() and p.name!='file_manifest.json'}
    source=read(E/'source_analysis/gate_summary.json')
    tests=read(E/'review/FROZEN_ANALYSIS_TESTS.json')
    complete=(E/'results/aggregate_report.json').exists()
    record={'schema_version':1,'milestone':'M6','date':'2026-10-29',
        'scope':'constructive_source_identifiability_and_synthetic_probe_no_new_real_outcomes',
        'code_sha256':code,'report_sha256':sha(P/'MILESTONE_6_RESULTS.md'),
        'curated_file_manifest_sha256':sha(C/'file_manifest.json'),
        'postrun_audit_sha256':sha(C/'POSTRUN_AUDIT.md'),
        'tests':{'frozen_analysis_invented_tests':tests['tests_run'],'exit_code':tests['exit_code'],
                 'current_core_engine_and_prior_bound_files_unchanged':True,
                 'historical_core_suite':{'milestone':'M4','passed':258,'skipped':1,'rerun_M6':False},
                 'independent_pre_execution_review':'passed','independent_postrun_review':'see_bound_audit'},
        'execution':{'candidate_versions':3,'source_replays':9,'source_context_executions':18,
                     'synthetic_probe_executions':9 if complete else 0,'scientific_revisions':0,
                     'source_seeds':[78101,78102,78103],'probe_seeds':[78201,78202,78203],
                     'source_check_records':source['n_all_records'],
                     'paired_source_comparisons':source['n_paired_comparisons'],
                     'paired_source_gate_failures':source['n_gate_failures'],
                     'source_gate_all_passed':source['all_passed'],
                     'complete_probe_phase':complete,'protocol_commitment_sha256':sha(E/'protocol_commitment.json'),
                     'source_commitment_sha256':sha(E/'source_commitment.json')},
        'interpretation':{'conditional_on_product_source_covariates':True,'imperfect_anchor_retained':True,
                          'source_admissibility_certified':False,'new_biological_discovery':False,
                          'new_real_target_evaluation':False,'clinical_importance_threshold':False,
                          'descriptive_MC_scale_gate_only':True,'all_four_analytic_cells_reported':True},
        'boundary':{'builder_historical_target_results_available':False,
                    'reviewer_and_analyst_incidental_historical_summary_exposure':True,
                    'exposure_note':'Agent inventory displayed unrelated completed-agent aggregate summaries; disclosed, not used for this constructive source-only experiment. No related files or patient rows opened.',
                    'outer_Agent_OS_isolated':False,'generator_backend':'wsl_bubblewrap',
                    'patient_rows_used_or_exported':False,
                    'curated_archive':'Inspection only; row-level synthetic execution inputs/outputs and runtime/full sources omitted.'}}
    if complete:
        record['execution']['evaluation_commitment_sha256']=sha(E/'evaluation_commitment.json')
        record['execution']['aggregate_result_sha256']=sha(E/'results/aggregate_report.json')
    destination=P/'m6_validation.json'
    assert not destination.exists()
    destination.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'passed','code_files':len(code),'curated_files':len(manifest)+1,
                      'report_sha256':record['report_sha256'],'validation_sha256':sha(destination)}))

if __name__=='__main__': main()
