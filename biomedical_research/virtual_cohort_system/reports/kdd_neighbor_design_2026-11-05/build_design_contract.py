"""Bind a proposed comparison to existing metadata/code; do not run science."""
from pathlib import Path
import hashlib,json

R=Path(__file__).resolve().parent;P=R.parents[1];W=P.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=P/'work/evidence_use_cross_task_2026-11-05'
anchors={
 'current_draft':P/'manuscript/DRAFT_v0_15.md',
 'source_protocol':prior/'PROTOCOL.json',
 'source_control':prior/'CONTROL.json',
 'source_interface_manifest':prior/'INTERFACE_MANIFEST.json',
 'endpoint_contract':prior/'ENDPOINT_CONTRACT.json',
 'old_runner_read_only':prior/'runner.py',
 'old_controller_read_only':prior/'controller_evidence_use.py',
 'old_evaluator_read_only':prior/'evaluator.py',
 'lipid_statistic_provider':prior/'lipid_provider.py',
 'evidence_use_interface':P/'cohort_harness/evidence_use_v1.py',
 'glycemia_request':W/'evcUseH01/request.json',
 'glycemia_curated_manifest':W/'evcUseH01/CURATED_INPUTS.json',
 'lipid_request':W/'evcUseL01/request.json',
 'lipid_curated_manifest':W/'evcUseL01/CURATED_INPUTS.json',
 'evaluation_only_ensanut_aggregate':P/'work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json',
 'evaluation_only_turkana_aggregate':P/'work/scaleup_2026-11-01/production_release/evaluation/PUBLISHABLE_AGGREGATES.json',
 'exposure_registry':P/'docs/DATASET_EXPOSURE_REGISTRY.md',
}
bindings={name:{'path':str(p.relative_to(W)).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size,
 'constructor_visible':name in ('glycemia_request','glycemia_curated_manifest','lipid_request','lipid_curated_manifest')}
 for name,p in anchors.items()}
endpoints=json.loads((prior/'ENDPOINT_CONTRACT.json').read_text(encoding='utf-8'))
cases=[]
for name,prefix in [('ENSANUT2018','H'),('Turkana','L')]:
 ep=endpoints['cases'][name]
 cases.append({'case_id':name,'prefix':prefix,'rows_per_final':3000,'individual_construction_input':False,
   'primary':ep['analyses'],'diagnostics':ep['diagnostics'],
   'matching_reference_outputs_per_episode':31 if prefix=='H' else 5,
   'generated_only_outputs_per_episode':0 if prefix=='H' else 21,
   'reference_status':'previously_exposed_development_reference',
   'source_ids':(['PMC2551641','PMC3075530','PMC6458679','PMC8038122'] if prefix=='H' else
     ['agongo_2018_navrongo','greiner_2021','obirikorang_2015_ashanti'])})
schedule=[]
for r in range(1,6):
 for ci,case in enumerate(cases):
  methods=['EVC','LLMSynthor-E'] if r%2 else ['LLMSynthor-E','EVC']
  for method in methods:
   mi=0 if method=='EVC' else 1
   seed=133000+ci*1000+mi*100+r
   schedule.append({'order':len(schedule)+1,'episode_id':f'KNC_{"EVC" if mi==0 else "LS"}_{case["prefix"]}{r:02d}',
    'case_id':case['case_id'],'method':method,'replicate':r,'rng_seed':seed,'rows':3000,
    'primary_delivery':'one final draw after fixed law' if mi==0 else 'native cumulative adaptive output',
    'expected_primary_estimates':3,'status':'not_dispatched'})
assert len(schedule)==20 and len({r['episode_id'] for r in schedule})==20
assert len({r['rng_seed'] for r in schedule})==20
assert sum(r['expected_primary_estimates'] for r in schedule)==60
quota_rounds=[{'round':i+1,'cell_counts':{str(i%8):30}} for i in range(96)]
quota_rounds += [{'round':97+i,'cell_counts':{str(2*i):15,str(2*i+1):15}} for i in range(4)]
quota_totals={str(i):sum(r['cell_counts'].get(str(i),0) for r in quota_rounds) for i in range(8)}
assert len(quota_rounds)==100 and set(quota_totals.values())=={375}
assert all(sum(r['cell_counts'].values())==30 and len(r['cell_counts'])<=2 for r in quota_rounds)
assert sum(quota_totals.values())==3000
contract={
 'schema_version':'kdd_neighbor_design_v1','date':'2026-11-05',
 'status':'DESIGN_ONLY_NOT_EXECUTION_RELEASED','generation_released':False,
 'protocol_sha256':sha(R/'PROTOCOL.md'),'manuscript_base':'v0.15','bindings':bindings,'cases':cases,
 'methods':{
  'EVC':{'identity':'evidence-qualified Agent law construction cross-task v1; curated-only evidence',
   'new_independent_episodes':10,'max_scientific_revisions_per_episode':1,
   'final_tables_per_episode':1,'old_generators_reused':False},
  'LLMSynthor-E':{'identity':'independent paper-based reimplementation plus biomedical evidence-to-macro intake',
   'official_code_available_at_audit':False,'paper_version':'2505.14752v4',
   'audited_repo_head':'92e443f93c6edecc0fa9ca3045d4204da7d42aa5',
   'new_independent_episodes':10,'proposal_rounds':100,'group_inference_schedule':'each round, Appendix-A interpretation',
   'proposal_max_per_round':5,'group_max_per_round':3,'new_rows_per_round':30,
   'append_only':True,'primary_frozen_mixture_replay':False,'official_numerical_reproduction_claim':False}},
 'schedule':schedule,
 'llmsynthor_ensanut_demographic_schedule':{'role':'declared outcome-free biomedical task adaptation',
  'cell_index_rule':'ordered eight sex-by-age cells from the pinned original request; binding required at release',
  'rounds':quota_rounds,'final_cell_totals':quota_totals,
  'agent_controls':'biomarker intervals and within-cell proposal count splits',
  'numeric_biological_relations_prescribed':False},
 'macro_admission':{'reported_derived_assumed_numeric_targets_immutable':True,
  'new_target_inference_inputs':['admitted source evidence','schema','admitted targets'],
  'new_target_inference_excludes':['current generated frequencies','evaluation results'],
  'unresolved_group_after_inference_budget':'exclude with recorded reason; never infer from generated rows'},
 'counts':{'reference_cases':2,'methods':2,'episodes_per_method_case':5,'scheduled_final_tables':20,
  'fictional_rows_if_complete':60000,'primary_estimates_if_complete':60,
  'all_analysis_diagnostic_values_if_complete':570,'matched_reference_comparisons_if_complete':360,
  'generated_only_diagnostics_if_complete':210},
 'budgets':{'new_source_queries':0,'new_source_downloads':0,'new_patient_reads_or_refits':0,
  'new_paid_endpoints':0,'training':False,'hpc':False,
  'short_live_fixture_episodes_max':2,'live_fixture_proposal_rounds_each':3,'live_fixture_model_requests_total_max':24,
   'logical_model_requests_per_main_episode_max':234,
  'llmsynthor_call_components':{'proposals':100,'groups':100,'intake':2,'optional_missing_joint_inference':20,'repairs':10,'scientific_review':2},
  'visible_output_tokens_per_main_episode_ceiling':1000000,
  'actual_model_service_and_version':'REQUIRED_BEFORE_RELEASE',
  'per_call_output_limits':'REQUIRED_BEFORE_RELEASE; proposal/group and code roles distinguished',
  'active_time_limit':'REQUIRED_BEFORE_RELEASE after technical latency measurement; not outcome-dependent',
  'same_backbone_required':True,'equal_consumed_compute_claim':False},
 'gates_pending':[
  'v4 prompt parity and declared ambiguous reproduction choices',
  'independent native operator/proposal/cumulative-controller fidelity checks on invented fixtures',
  'generic evidence-to-macro scientific adapter review without our fitted law or target results',
  'actual model dispatcher, fresh-context boundaries, call and available token metering',
  'new controller and cumulative-output receipts; no mutation of old frozen controllers',
  'clean equal curated packets and reviewed information boundary',
  'episode evaluator and independent arithmetic checks; frozen estimator conventions retained',
  'complete code/prompt/input/runtime/reference hash binding and reviewed execution release'],
 'not_scheduled':['G-Sim runs','CHNS R30 rerun','common-macro ablation','new clinical cohort','extra seed resampling'],
 'interpretation':{'primary_level':'matched-evidence developmental workflow comparison',
  'component_causal_attribution':False,'fresh_clinical_confirmation':False,
  'target_reference_is_population_truth':False,'universal_superiority':False,
  'success_rule':'report all predefined scientific analyses, completion and measured costs; no post-hoc winner threshold'},
}
(R/'DESIGN_CONTRACT.json').write_text(json.dumps(contract,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(R/'STATE.json').write_text(json.dumps({'status':'DESIGN_READY_FOR_INDEPENDENT_REVIEW','date':'2026-11-05',
 'generation_released':False,'protocol_sha256':contract['protocol_sha256'],'contract_sha256':sha(R/'DESIGN_CONTRACT.json'),
 'new_scientific_runs':0,'patient_rows_read':False,'next':'Implement and independently audit LLMSynthor core on invented native fixtures; resolve execution gates before biomedical runs.'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':contract['status'],'input_metadata_files_hashed':len(bindings),'scheduled_tables':len(schedule),
 'primary_estimates':60,'all_analysis_diagnostic_values':570,'new_scientific_runs':0}))
