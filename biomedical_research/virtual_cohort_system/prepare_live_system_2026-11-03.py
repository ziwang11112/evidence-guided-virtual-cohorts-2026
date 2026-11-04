from pathlib import Path
import json,hashlib
from cohort_harness.request_intake import prepare_request
from cohort_harness.execution import DEFAULT_RUNTIME,_runtime_manifest
P=Path.cwd(); W=P.parents[1]; run=P/'work/agent_system_live_2026-11-03'; run.mkdir(exist_ok=False)
base=W/'evcLive01';base.mkdir(exist_ok=False)
def write(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def col(name,kind,unit,**kw):return dict(name=name,kind=kind,unit=unit,role='generated',nullable=False,**kw)
columns=[dict(name='person_id',kind='string',unit='identifier',role='identifier',nullable=False),
col('age','integer','years',minimum=35,maximum=74),col('female','integer','indicator',minimum=0,maximum=1),
col('bmi','number','kg/m^2',minimum=0),col('hba1c','number','percent',minimum=0)]
protocol={'schema_version':1,'kind':'developmental_agent_system_integration',
'case':'Existing CHNS 2009 selected analytic population; already exposed reference',
'population':'Age 35-74, both sexes, common complete-case measurement availability; no diabetes/treatment exclusions; not national representation.',
'fresh_authors':2,'information':'External published evidence and target population/measurement description; no target outcome summaries or participant inputs supplied to authors.',
'requests':{
 'A':{'columns':['person_id','age','female','bmi','hba1c'],'analyses':['hba1c ~ 1 + bmi + age + female'],'primary_terms':['bmi'],'secondary_terms':['age','female']},
 'B':{'columns':['person_id','age','female','bmi','hba1c','glucose'],'analyses':['hba1c ~ 1 + bmi + glucose + age + female'],'primary_terms':['bmi'],'secondary_terms':['glucose','age','female']}},
'diagnostics':'For each non-ID variable mean, sample SD, q10/q50/q90; Pearson/Spearman BMI-HbA1c; B also glucose-HbA1c. Complete coefficient reporting.',
'generated_intervals':'OLS HC3 intervals conditional on this model and synthetic draw; not epistemic or transport uncertainty.',
'reference_intervals':'Original selected CHNS sample; community-cluster CR1-t uncertainty. Comparison developmental, not new confirmation.',
'comparison':'Direction, effect scale, uncertainty, complete seed range and distributions; no post-hoc equivalence threshold or pooled success score.',
'budgets_per_request':{'source_queries':8,'source_downloads':3,'scientific_revisions':1,'initial_trial_attempts':1,'revision_trial_attempts':1,'delivery_seeds':[7301,7302,7303],'rows':3000,'max_physical_tables':8,'contract_repair_rounds':2},
'max_physical_tables':16,'source_seed_identifiers':['doi:10.1111/joim.12010','doi:10.1136/bmj.c2249','doi:10.1371/journal.pone.0296694'],
'source_policy':'Search these previously used original studies; inspect originals. No CHNS-derived generation evidence. No new dataset family; no paid APIs/HPC/training.',
'no_source_replay_substitution':'Generated target diagnostics cannot masquerade as original-source population checks. Declare unavailable when source context cannot be represented.',
'freeze':'Initial artifacts freeze before trial; delivered initial and final versions freeze before evaluator reference comparison. Retention preserves same scientific model; failures consume slots.',
'author_isolation':'Fresh model context with explicit permitted paths; procedural restriction, not OS isolation of all model tools.',
'evaluation_root':str(run/'evaluation'),'bundles':{k:str(base/k) for k in ['A','B']}}
write(run/'PROTOCOL.json',protocol)
for key in ['A','B']:
 task={'schema_version':1,'task_id':'live-system-'+key,'mode':'whole_cohort','population':protocol['population'],
 'row_id':'person_id','n_rows':3000,'columns':columns+([col('glucose','number','mmol/L',minimum=0)] if key=='B' else []),
 'information_policy':{'mode':'published_evidence','excluded_cohorts':['CHNS','China Health and Nutrition Survey'],
 'allowed_tools':['literature.search','literature.fetch','literature.list-supplements','literature.fetch-supplement']},
 'budget':{'source_queries':8,'source_downloads':3,'revisions':1}}
 req={'schema_version':1,'purpose':'Create a complete virtual adult cohort suitable for the requested biomedical analysis. This is a developmental system demonstration using external published evidence.',
 'analyses':protocol['requests'][key]['analyses'],'task':task}
 write(run/f'request_{key}.json',req)
 prepare_request(req,base/key)
 write(base/key/'RUN_RULES.json',{'protocol_sha256':hashlib.sha256((run/'PROTOCOL.json').read_bytes()).hexdigest(),
 'budget':protocol['budgets_per_request'],'source_seed_identifiers':protocol['source_seed_identifiers'],
 'measurement':'HbA1c percentage, BMI kg/m^2, age years, female 0/1; B glucose mmol/L centrally measured serum; fasting adherence in target not individually verified.',
 'scientific_autonomy':'Choose equations, parameters, dependencies, distribution families and source use; no desired signs/coefficient values supplied.',
 'references':'Target values/results and other candidates not provided. Do not read old studies/results outside your bundle.',
 'submission':'Use evidence-cohort-generation skill interface, evidence.json, model_spec.json, generator.py or generated.csv, decision.md, checks.json. Whole-cohort source feedback sidecars required; unavailable source checks may be explicitly recorded.',
 'runtime':'Isolated executor provided by coordinator. Do not run generated-code sampling outside executor. Analytic calculations allowed.',
 'workflow':'Retrieve evidence; author initial candidate; notify coordinator for preflight/trial; receive generated-only diagnostics and declared source feedback; initial delivery; one revision/retain decision; final delivery. Reference comparison only after final freeze.'})
write(run/'RUNTIME_PREFLIGHT.json',_runtime_manifest(DEFAULT_RUNTIME))
write(run/'STATE.json',{'status':'prepared_for_independent_review','scientific_generations':0,'queries':0,'authors':{},'protocol_sha256':hashlib.sha256((run/'PROTOCOL.json').read_bytes()).hexdigest()})
print(json.dumps({'run':str(run),'bundles':protocol['bundles'],'protocol_sha256':hashlib.sha256((run/'PROTOCOL.json').read_bytes()).hexdigest()}))
