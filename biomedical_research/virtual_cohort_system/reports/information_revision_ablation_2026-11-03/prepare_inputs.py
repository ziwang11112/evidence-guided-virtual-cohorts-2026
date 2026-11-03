"""Prepare six fresh author views from external evidence and declared aggregates."""
from pathlib import Path
import copy,json,hashlib,shutil

U=Path(__file__).resolve().parent;P=U.parents[1];W=P.parents[1];ROOT=W/'evcIA'
PRE=P/'work/adaptive_reference_pilot_2026-11-03'
OLD=P/'work/developmental_continuation_v1_2026-11-03/author_inputs'
RB=W/'evcAR/b'
ORDER=['L01','R01','R02','L02','L03','R03']
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(o,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')

AUTHOR='''# Scientific author task: whole-cohort generation and diagnostic revision

Your assigned root is {root}. Read only this task, b/task.json, b/input/*, b/sources/* and your own new candidates and feedback. Read the evidence-cohort-generation skill and narrow cohort_harness interface code as needed. Do not read sibling roots, earlier project results/generators, evaluation-reference files outside this assignment, or raw participant files. All five variables are generated; observed is None. The scientific analyses are visible in input/analysis_definitions.json. Choose structure, parameters and scientific assumptions yourself; no law/sign/family or forced revision is prescribed.

Use the source evidence in its actual population, measurement, adjustment and uncertainty context. Means/SDs, regression projections, correlation types and weighted results are not interchangeable. The audit restores additional source age evidence with its qualifications. Missing evidence does not establish independence. Extra explicitly supplied reference summaries, if present in this assignment, are allowed development inputs; they remain sample estimates. Do not obtain them from other project files. Original literature retrieval is allowed (two queries and one new original document total); record actual URLs/queries and overlap. Equivalent published findings retrieved in ordinary source research are permitted. Root curator must register newly used artifacts before freezing. No forced search when existing sources suffice.

Submit a complete five-variable adult cohort of 3000 rows with unique synthetic row_id. Create NEW b/candidates/<name>/ containing generator.py, model_spec.json, evidence.json, decision.md and checks.json. Program ABI is generate(observed,spec,seed), observed=None, returning a DataFrame in exact task order. Model specification follows parameters/assumptions/parameter_provenance schema. Use b/input/compiled_evidence.json as the source record, with a curator-registered supplement if needed. Every scientific parameter needs source/derivation or explicit assumption. Keep finite-moment/positive-support reasoning and unassessed uses concise. All new text must use UTF-8 explicitly. Never change a frozen candidate.

Root attaches the fixed diagnostic semantics, freezes and runs your candidate in the existing isolated backend. You may request two numerical trial tables before initial delivery and two in the final revision phase, each3000rows. All row-producing simulation belongs in these supplied executions and consumes the budget; do not locally sample/import/run a generator or hide additional cohorts inside optimization. Deterministic mathematical calculations/integration/optimization without synthetic rows are allowed; retain actual producer scripts and log their limits. Source-context numerical replay is not supplied in this experiment; analytic source reasoning and target-generation diagnostics remain available. Do not compare target-population metrics to a differently selected source as if that were a replay.

Initial delivery uses fixed seeds4101,4102,4103. After full permitted feedback, choose revise/retain and submit a final version, frozen before the same delivery seeds. At most10tableattempts including4trials+6deliveries; failure consumes a slot, no hidden retries. At most one post-initial revision cycle. Trial seeds are4201/4202 initially and4301/4302 after feedback. Do not exhaust a budget merely because it exists, select a favorable seed, tune a p-value or claim exact sample agreement as population recovery.

You receive all generated30 statistics. Whether reference values/comparisons are available is determined by your assigned information package; do not infer their values from unavailable feedback. Source checks without source simulation are explicitly not computable. In checks.json the legacy source_only scope denotes declared input evidence, not an independent scientific validation. Record unperformed checks as not_computable. Bind actual earlier feedback used in revisions; no fabricated passes or private reasoning traces required.

No paid API, training, HPC, new cohort download, accounts, patient-level access or additional scientific subagents. The calling environment dispatches you; the harness does not itself launch an LLM. One author may make several tool/feedback turns within this construction. Report actual sources, trial requests, changes/no-op and limitations. First deliver a candidate for one requested trial or initial delivery; do not stop at a plan. Final decision later uses keys reason,kind(revise/retain),addressed_findings,remaining_limitations in root/FINAL_AUTHOR_DECISION.json.
'''

def main():
    ROOT.mkdir(exist_ok=False)
    audit=(PRE/'inputs/EXTERNAL_EVIDENCE_AUDIT.md').read_text(encoding='utf-8')
    # Reuse source facts without historical input-regime instructions.
    audit=audit[audit.index('## Source identity and status'):audit.index('## Provenance and handoff')]
    audit=audit.replace('Full supplied CHNS summaries may be used as declared developmental information.','A target-specific summary may only be used if explicitly supplied in the assigned task.')
    audit=audit.replace('Full supplied CHNS summaries separately allowed','Target-specific summaries are task-dependent')
    audit=audit.replace('full CHNS reference summaries separately allowed','target-specific summaries are task-dependent')
    audit='# External evidence: separately conditioned source observations\n\nSource facts below are reconciled from existing original-source audits; no new original-paper verification is claimed. No common target-generating equation is identified.\n\n'+audit
    base=load(OLD/'input/compiled_evidence.json');base_registry=load(OLD/'registry.json')
    oldtask=load(P/'work/chns_admission_2026-11-01/f2/task.json')
    defs=load(RB/'input/analysis_definitions.json')
    defs={'analyses':[{k:d[k] for k in ['id','operator','outcome','predictors','term','intercept','weights','unit']} for d in defs['analyses']],
          'diagnostics':{'marginal_variables':['age','female','bmi','glucose','hba1c'],'marginal_statistics':['mean','sample_sd_ddof1','quantile_0.1_linear','quantile_0.5_linear','quantile_0.9_linear'],'joint':['pearson_glucose_hba1c','spearman_glucose_hba1c_average_ties']}}
    diagnostics=[v+'_'+s for v in defs['diagnostics']['marginal_variables'] for s in ['mean','sd','q10','median','q90']]+['glucose_hba1c_pearson','glucose_hba1c_spearman']
    ref_evidence=load(RB/'input/compiled_evidence.json');ref_checks=load(RB/'input/whole_cohort_feedback_template.json')['checks'];ref_bindings=load(RB/'input/semantic_bindings_template.json')['bindings']
    manifest=[]
    for key in ORDER:
        root=ROOT/key;b=root/'b';(b/'input').mkdir(parents=True);(b/'candidates').mkdir();shutil.copytree(OLD/'sources',b/'sources')
        (b/'sources/EXTERNAL_EVIDENCE_AUDIT.md').write_text(audit,encoding='utf-8',newline='\n')
        evidence=copy.deepcopy(base);registry=copy.deepcopy(base_registry)
        art={'path':'sources/EXTERNAL_EVIDENCE_AUDIT.md','sha256':sha(b/'sources/EXTERNAL_EVIDENCE_AUDIT.md')}
        evidence['sources'].append({'id':'S_AUDIT','identifier':'local:qualified_external_source_reconciliation','population':'Distinct populations retained separately: Lifelines, Shanghai SHDS, MIND-China and NHANES. No pooled target cohort.',
            'measurement':'Original source units/adjustment sets retained separately; derivative source reconciliation, not a new original study.','cohort_ids':['Lifelines','SHDS II','MIND-China','NHANES'],'artifacts':[art]})
        evidence['items'].append({'id':'E_SOURCE_RECONCILIATION','source_id':'S_AUDIT','locator':'Source-specific tables and primary source locators in EXTERNAL_EVIDENCE_AUDIT.md','variables':['age','female','bmi','glucose','hba1c'],'kind':'contextual','estimate':None,'unit':'','uncertainty':{'kind':'not_reported'},'adjustment':[],
            'selection':'Source-specific age, disease and measurement selections; no common target selection.','applicability':'Readable source context, not an identified target law or an executed source-population reconstruction.'})
        registry['artifacts'].append({'source_id':'S_AUDIT',**art,'origin':'curator','screening':'approved'})
        task=copy.deepcopy(oldtask);task['task_id']='information-revision-'+key+'-2026-11-03';task['population']=task['population'].replace('Age/sex composition is not supplied. ','')
        task['information_policy']={'mode':'published_evidence','excluded_cohorts':[],'allowed_tools':['admitted_source_read','literature.search','literature.fetch','contract_validation','isolated_numeric_trial','semantic_feedback_v1','allowed_information_diagnostics','candidate_revision']}
        task['budget']={'source_queries':2,'source_downloads':1,'revisions':4}
        check={'id':'external_context_unreplayed','evidence_id':'E_SOURCE_RECONCILIATION','status':'not_computable','operator':None,'assumption_ids':[],
               'reason':'No source-population reconstruction was executed. Task-population statistics are not numerical source-study replay.'}
        binding={'check_id':check['id'],'evidence_id':check['evidence_id'],'source_locator':evidence['items'][-1]['locator'],'definition_status':'unsupported','source_operator':None,'weights':'not_reported','transform':'not_reported','source_variable_units':{},'source_n':{'status':'not_reported'},'uncertainty_role':'not_reported','reason':check['reason']}
        checks=[check];bindings=[binding]
        if key.startswith('R'):
            shutil.copy2(RB/'input/reference_summary.json',b/'input/reference_summary.json');shutil.copy2(RB/'sources/CHNS_DEVELOPMENT_REFERENCE.json',b/'sources/CHNS_DEVELOPMENT_REFERENCE.json')
            source=copy.deepcopy(next(s for s in ref_evidence['sources'] if s['id']=='CHNS_DEV_REF'));source['population']=task['population'];evidence['sources'].append(source)
            evidence['items']+=copy.deepcopy([i for i in ref_evidence['items'] if i['source_id']=='CHNS_DEV_REF'])
            registry['artifacts'].append({'source_id':'CHNS_DEV_REF',**source['artifacts'][0],'origin':'curator','screening':'approved'})
            checks+=copy.deepcopy(ref_checks);bindings+=copy.deepcopy(ref_bindings)
        write(b/'task.json',task);write(b/'registry.json',registry);write(b/'input/compiled_evidence.json',evidence);write(b/'input/analysis_definitions.json',defs)
        write(b/'input/whole_cohort_feedback_template.json',{'schema_version':1,'population':task['population'],'measurement':{'mode':'identity','description':'Actual target-task output units. Declared development references only when explicitly supplied; external source replay is unavailable.'},'assumption_ids':[],'checks':checks})
        write(b/'input/semantic_bindings_template.json',{'bindings':bindings})
        profile={'schema_version':1,'information_condition':key[0],'constructor_id':key,'bundle':str(b),'analysis_definitions':str(b/'input/analysis_definitions.json'),
            'required_analysis_ids':['E1','E2','E3'],'required_diagnostic_ids':diagnostics,'numeric_semantic_evidence_ids':[i['id'] for i in evidence['items'] if i['source_id']=='CHNS_DEV_REF'],
            'budgets':{'fresh_constructors':1,'author_phases':2,'initial_trials':2,'revision_trials':2,'delivery_per_stage':3,'delivery_seeds':[4101,4102,4103],'max_total_tables':10,'rows_per_table':3000,'retrieval_queries':2,'retrieval_documents':1},
            'source_context_execution':'not_supplied','interpretation':'One developmental case. All information provided or independently retrieved is logged. No patient-level recovery or untouched target validation.'}
        if key.startswith('R'):profile['reference_summary']=str(b/'input/reference_summary.json')
        write(root/'profile.json',profile)
        (root/'AUTHOR_TASK.md').write_text(AUTHOR.format(root=str(root)),encoding='utf-8',newline='\n')
        files=[root/'profile.json',root/'AUTHOR_TASK.md',b/'task.json',b/'registry.json',*sorted((b/'input').glob('*')),*sorted((b/'sources').glob('*'))]
        manifest.append({'constructor':key,'information_condition':key[0],'root':str(root),'files':[{'path':str(f),'sha256':sha(f)} for f in files if f.is_file()]})
    write(U/'INPUT_MANIFEST.json',{'launch_blocks':[['L01','R01'],['R02','L02'],['L03','R03']],'constructors':manifest})
    write(U/'STATE.json',{'phase':'prepared_pending_independent_release','execution_enabled':False,'scheduled_runs_verified':0,'fresh_authors':0,'attempts':0,'delivery_attempt_budget':36,'trial_attempt_budget':24,'constructors':{k:{'status':'prepared'} for k in ORDER},'old_pilot_pooled':False,'raw_patient_reads':0})
    print(json.dumps({'constructors':ORDER,'root':str(ROOT),'prepared_only':True}))
if __name__=='__main__':main()
