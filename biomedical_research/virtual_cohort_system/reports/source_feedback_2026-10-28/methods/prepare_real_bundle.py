from pathlib import Path
import hashlib
import json
import shutil

root = Path(__file__).resolve().parent
visible = root / 'visible' / 'nhanes_tg_j_v2'
scout = root / 'evidence_scout'
bundle = root / 'tg_agent_bundle'
bundle.mkdir(exist_ok=False)
(bundle / 'sources').mkdir()
(bundle / 'candidates').mkdir()
def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
metadata = json.loads((visible/'task_metadata.json').read_text(encoding='utf-8-sig'))
task = {'schema_version':1, 'task_id':'tg-source-feedback-pilot-2026-10-28',
    'mode':'enrichment', 'population':'US fasting observational sample, adults aged 20-79. Only age, sex and BMI are visible. Generate possible serum triglyceride values for analytical use; not individual recovery.',
    'row_id':'record_id', 'n_rows':metadata['n_rows'],
    'columns':[
        {'name':'record_id','kind':'string','unit':'identifier','role':'identifier','nullable':False},
        {'name':'age','kind':'integer','unit':'years','role':'observed','nullable':False,'minimum':0,'maximum':120},
        {'name':'sex','kind':'category','unit':'1=male;2=female','role':'observed','nullable':False,'categories':[1,2]},
        {'name':'bmi','kind':'number','unit':'kg/m^2','role':'observed','nullable':False,'minimum':0},
        {'name':'tg_mg_dl','kind':'number','unit':'mg/dL','role':'generated','nullable':False,'minimum':0}
    ],
    'information_policy':{'mode':'published_evidence','excluded_cohorts':['NHANES','National Health and Nutrition Examination Survey'],
        'allowed_tools':['approved_local_sources','source_replay']},
    'budget':{'source_queries':0,'source_downloads':0,'revisions':1}}
write(bundle/'task.json',task)
shutil.copyfile(visible/'observed.csv', bundle/'observed.csv')
assert sha(visible/'observed.csv') == sha(bundle/'observed.csv')
manifest = {r['file']:r['sha256'] for r in json.loads((scout/'source_manifest.json').read_text())['files']}
selection = {
    'oh2019':['oh2019_fulltext_readable.txt','oh2019_tables_extracted.json','oh2019_pmc_version_metadata.json','source_report.json'],
    'bansal2007':['bansal2007_article_body_web.txt','source_report.json']}
registry={'artifacts':[]}
for source, files in selection.items():
    for name in files:
        assert sha(scout/name)==manifest[name]
        target=bundle/'sources'/name
        if not target.exists(): shutil.copyfile(scout/name,target)
        registry['artifacts'].append({'source_id':source,'path':'sources/'+name,'sha256':sha(target),'origin':'curator','screening':'approved'})
write(bundle/'registry.json',registry)
protocol={'scope':'exploratory public-data source-feedback feasibility pilot',
    'agent_constructions':1,'feedback_rounds':1,'source_seed':74001,
    'target_seeds':[74101,74102,74103,74104,74105],
    'comparison':'Initial versus final candidate, both retained; not a causal comparison with equal-compute ordinary iteration',
    'feedback':'Only supplied external-source diagnostics; no target analysis values or individual outcomes',
    'selection':'Freeze initial and final, then run all fixed seeds before opening heldout reference analyses',
    'revision':'Builder chooses revise or retain; no controller changes to scientific relationships/parameters',
    'case_protocol_sha256':metadata['protocol_sha256'],
    'builder_boundary':'Fresh-context subagent and instructed path allowlist; not OS-level Agent tool isolation',
    'uncertainty':'Seeds vary residual sampling only unless Agent explicitly models more; rows/seeds do not increase clinical evidence',
    'retrieval_scope':'Curator supplied two primary papers; autonomous gap retrieval is not tested in this pilot'}
write(bundle/'protocol.json',protocol)
(bundle/'TASK_BRIEF.md').write_text('''# Public-data whole-column generation pilot

Construct an initial PROGRAM candidate named initial, with no access to true triglycerides.
Choose scientific relationships, parameters and assumptions from the approved sources yourself.
Preserve the observed table exactly; sex is 1 male and 2 female. Generate strictly positive
tg_mg_dl values in mg/dL. The data will support association analyses, including natural-log TG.
No individual recovery or population causal identification is claimed.

Read the two source articles and the scout's context notes. Extract your own evidence records.
Do not silently interchange arithmetic/geometric means, individual SD/SE, adjusted/unadjusted
slopes, or Spearman/Pearson correlations. Source title and methods have specimen discrepancies.
Interpret source inconsistencies explicitly; unsupported estimators may remain unreplayed.
External cohort-to-US transfer is an assumption. No target regression coefficient is supplied.

Read the current generation skill and docs/SOURCE_REPLAY.md in the project. Submit a frozen
source_replay.json with covariate-only source_contexts/*.csv chosen from reported source
conditions and explicit assumptions, with enough rows for useful Monte Carlo diagnostics.
The same exact generator and specification will run in both source and target contexts.
Do not include generated outcomes as source-input covariates, and do not inspect other tasks.
Use one main construction; do not secretly select a successful seed or favorable model.
The controller will run source replay once and return that report. You may then revise or
retain once, explaining what is supported and what is still unidentified.

Do not run generator code locally; it executes through the isolated adapter. Static checks
are allowed. Do not read custodian files, hidden outcomes, raw public data, past cases/results,
other Agents' messages, or list_agents. Do not attempt record linkage or independent target
downloads. Only this bundle's approved files and explicitly listed interface documentation
are allowed. This procedural restriction is not claimed to be an OS sandbox.
''', encoding='utf-8')
write(root/'real_bundle_preparation.json',{'bundle':str(bundle),'n_rows':task['n_rows'],
    'observed_sha256':sha(bundle/'observed.csv'),'task_sha256':sha(bundle/'task.json'),
    'protocol_sha256':sha(bundle/'protocol.json'),'registry_sha256':sha(bundle/'registry.json'),
    'sources':'curator-reviewed primary external papers; no target clinical outcomes admitted'})
print(bundle)
