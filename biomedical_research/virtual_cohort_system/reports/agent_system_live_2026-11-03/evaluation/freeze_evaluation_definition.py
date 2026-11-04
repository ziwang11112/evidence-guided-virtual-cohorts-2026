from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protocol=H.parent/'PROTOCOL.json'
assert sha(protocol)=='4e95e8e32bf4e33b18502ea6051481400cf6ef4886acade990184119284dc7d0'
old=P/'work/chns_admission_2026-11-01/f2'
plan=json.loads((old/'analysis_plan.json').read_text())
definition={
'schema_version':1,'status':'frozen_before_new_reference_read',
'protocol_sha256':sha(protocol),
'request_analyses':{'A':{'predictors':['bmi','age','female'],'primary_term':'bmi'},
'B':{'predictors':['bmi','glucose','age','female'],'primary_term':'bmi'}},
'outcome':'hba1c','intercept':True,'coefficient_report':'all_terms',
'generated_intervals':'HC3-t 95%; conditional on fixed synthetic law and draw',
'reference_intervals':'CR1-t 95%; community clusters and t(groups-1)',
'diagnostics':{'marginal':['mean','sd_ddof1','q10_linear','median_linear','q90_linear'],
'joint':['bmi_hba1c_pearson','bmi_hba1c_spearman','B:glucose_hba1c_pearson','B:glucose_hba1c_spearman']},
'reference_role':'already exposed selected development reference, not known population truth or new confirmation',
'metadata_only_original_plan':{'path':str(old/'analysis_plan.json'),'sha256':sha(old/'analysis_plan.json')},
'original_pure_linkage_engine':{'path':str(old/'evaluation/chns_f2_evaluation.py'),'sha256':sha(old/'evaluation/chns_f2_evaluation.py')},
'reference_files':[{'file':v['file'],'sha256':v['sha256'],'columns':[v['key']]+([v['wave']] if v['wave'] else [])+v['columns']} for v in plan['input_files']],
'generated_diagnostics':{'path':'generated_diagnostics.py','sha256':sha(H/'generated_diagnostics.py')},
'read_gate':'Both author runs closed, selected candidates frozen and all initial/final slots inventoried before any clinical file decode or reference comparison.',
'no_posthoc_equivalence_margin':True}
with (H/'EVALUATION_DEFINITION.json').open('x',encoding='utf-8') as f:json.dump(definition,f,indent=2);f.write('\n')
print(json.dumps({'definition_sha256':sha(H/'EVALUATION_DEFINITION.json'),'raw_reference_reads':0}))
