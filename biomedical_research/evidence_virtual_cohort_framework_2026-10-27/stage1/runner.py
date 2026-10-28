"""Stage 1 custodian/controller. Source-only staging extends population_framework.

No model API calls. Nine fresh lineages branch into eighteen source-only revisions.
Outputs and manifests use exclusive creation. Repairs require a new run version.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import math
import platform
import shutil
import time
import traceback
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from source_checks import read,allocation,load_generator,validate_decision,validate_frame,source_diagnostics,call_checked

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]
CASE_IDS=['case_a','case_b','case_c']
PAPER=BASE/'obesity_paper_replay_2026-10-27'
TRAVERS=BASE/'obesity_public_data_replication_2026-10-25'
HE=BASE/'obesity_larger_replication_2026-10-25'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc(): return datetime.now(timezone.utc).isoformat()
def clean(x):
    if isinstance(x,dict): return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [clean(v) for v in x]
    if isinstance(x,np.generic): x=x.item()
    if isinstance(x,float) and not math.isfinite(x): return None
    return x
def write(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f: json.dump(clean(obj),f,indent=2,allow_nan=False); f.write('\n')
def write_text(path,text):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f: f.write(text)
def csv_new(df,path):
    with Path(path).open('x',encoding='utf-8',newline='') as f: df.to_csv(f,index=False)
def files_manifest(root): return {str(p.relative_to(root)).replace('\\','/'):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
def verify_files(root,manifest):
    for p,h in manifest.items():
        if sha(root/p)!=h: raise ValueError('Frozen file changed: '+str(root/p))
def verify_freeze():
    freeze=read(ROOT/'protocol_freeze.json')
    verify_files(ROOT,freeze['files'])
    return freeze

def final_inventory():
    """Commit exactly 18 paired Agent arms plus 3 fixed arms before target reads."""
    expected=[]
    for case in CASE_IDS:
        for build in range(1,4):
            parents=[]
            for branch in ['ordinary','proposed']:
                paths=list((ROOT/'runs'/case/f'build_{build:02d}').glob(branch+'_*/final/manifest.json'))
                if len(paths)!=1: raise ValueError(f'Require exactly one final manifest for {case}/build_{build:02d}/{branch}; found {len(paths)}')
                expected+=paths
                parents.append(read(paths[0].parent.parent/'task.json')['parent'])
            if parents[0]!=parents[1]: raise ValueError('Paired branches did not receive identical initial artifacts and feedback')
        paths=list((ROOT/'statistical'/case/'fixed').glob('statistical_*/final/manifest.json'))
        if len(paths)!=1: raise ValueError('Require exactly one statistical final manifest per case')
        expected+=paths
    discovered=list((ROOT/'runs').rglob('final/manifest.json'))+list((ROOT/'statistical').rglob('final/manifest.json'))
    if set(expected)!=set(discovered) or len(expected)!=21: raise ValueError('Unplanned or duplicated final arms present')
    records=[]
    for p in expected:
        fm=read(p); run=p.parent.parent; task=read(run/'task.json')
        if fm['task']!=task or task['regime']!='whole_cohort': raise ValueError('Task identity/regime differs')
        cm=read(run/'candidate_manifest.json'); verify_files(run,cm['files']); verify_files(p.parent,fm['files'])
        if sha(run/'candidate_manifest.json')!=fm['candidate_manifest_sha256']: raise ValueError('Candidate commitment differs')
        if len(fm['records'])!=20 or fm['cohorts_requested']!=20: raise ValueError('Final cohort count differs')
        if [r['seed'] for r in fm['records']]!=read(ROOT/'protocol.json')['final_seeds'][task['case_id']]: raise ValueError('Final seed inventory differs')
        if task['branch']=='statistical' and fm['scenario_allocation']!={'rho_0':7,'rho_04':7,'rho_08':6}: raise ValueError('Fixed sensitivity allocation differs')
        records.append(dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha(p),run_id=task['run_id'],requested=20,saved=fm['cohorts_saved']))
    path=ROOT/'final_inventory.json'
    inventory=dict(protocol_sha256=sha(ROOT/'protocol_freeze.json'),requested_cohorts=420,final_arms=21,records=records)
    if path.exists():
        if read(path)!=inventory: raise ValueError('Committed final inventory changed')
    else: write(path,inventory)
    return expected

def analysis_registry():
    rows=[]
    def add(case,analysis,term,variables,formula,role,family,transform='none',interpretation='research rehearsal; no clinical validation'):
        rows.append(dict(case_id=case,analysis=analysis,term=term,variables=variables,estimand=term,formula=formula,transformation=transform,missingness='pairwise complete for correlations/paired analyses; available rows per mixed model',multiplicity_family=family,multiplicity='unadjusted descriptive 95% intervals; no familywise confirmatory claims',validation_role=role,evidence_support='unidentified dependence' if role=='reserved' else 'provided marginal summaries; covariance still reserved',interpretation=interpretation,known_paper_statement='prior development exposure; no newly blinded confirmatory claim',reference_reproduced='audited previously; fresh identical implementation evaluation retained'))
    vs=['pfs','gng','dd100','dd1000']
    for x,y in itertools.combinations(vs,2): add('case_a','baseline_pearson',x+'__'+y,[x,y],'Pearson r at month 0; Fisher-z interval','reserved','baseline_correlations')
    for v in ['weight_kg']+vs:
        for a,b in [(3,0),(6,0),(9,0),(12,0),(12,3)]:
            add('case_a','weight_time_reml' if v=='weight_kg' else v+'_time_reml',f'month_{a}_minus_{b}',[v,'month','person_id'],f'{v} ~ C(month) + random participant intercept; REML Powell; normal Wald contrast','given/reconstruction','time_contrasts',interpretation='mean trajectory reconstruction; uncertainty depends on withheld covariance and missingness, not independent reserved mean recovery')
    for v in vs: add('case_a','pooled_standardized_reml',v,['weight_kg',v,'person_id'],'z(weight) ~ z(predictor) + random participant intercept; REML; normal Wald','reserved','proxy_associations','global available-pair sample z scores','exploratory proxy; not exact published coefficient replay')
    for case,first in [('case_b','leptin'),('case_c','leptin_log10')]:
        endpoints=[first,'body_mass','glucose','triglycerides']
        for v in endpoints:
            add(case,'paired_change',v,[v+'_pre',v+'_post'],'mean(post-pre), sample SD(change)/sqrt(n), t interval df=n-1; paired r and change SD retained','given/reconstruction','paired_changes','log10(pg/mL) already supplied' if v=='leptin_log10' else 'none','mean change determined by supplied marginal means; paired covariance, SE and evidence state reserved')
        for x,y in itertools.combinations(endpoints,2): add(case,'change_pearson',x+'__'+y,[x+'_pre',x+'_post',y+'_pre',y+'_post'],'Pearson r of post-pre changes; Fisher-z interval','reserved','cross_endpoint_change_correlations')
    return rows

def prepare():
    if (ROOT/'protocol_freeze.json').exists(): raise FileExistsError('Protocol already frozen')
    for name in ['packets','custodian','runs','statistical']: (ROOT/name).mkdir(exist_ok=True)
    original={}
    ross=read(PAPER/'allowed/evidence.json')
    ross['n_persons']=75
    ross['evidence_items']=[dict(id='E_marginals',operator='per-visit arithmetic mean, sample SD, nonmissing count',population=ross['study_design'],measurement=ross['measurement'],provenance='source_packet_A; supplied target-derived marginals, reconstruction regime A0'),dict(id='E_design',operator='study eligibility and measurement dictionary',population=ross['study_design'],measurement=ross['measurement'],provenance='source_packet_A')]
    schema_a=dict(format='long',n_persons=75,columns=['person_id','month','weight_kg','pfs','gng','dd100','dd1000'],keys=['person_id','month'],baseline_weight_max=180,bounds={'weight_kg':[1e-9,1e308],'pfs':[1,5],'gng':[0,512],'dd100':[0,1],'dd1000':[0,1]},visits=[0,3,6,9,12])
    # Transcription is solely from permitted INPUT.md, never from evaluator values.
    moments_b={k:dict(n=12,unit=u,pre_mean=a,pre_sd=b,post_mean=c,post_sd=d) for k,u,a,b,c,d in [('leptin','ng/mL',9.331,4.463,6.767,4.231),('body_mass','kg',93.083,9.841,91.517,9.662),('glucose','mmol/L',5.125,.578,5.072,.426),('triglycerides','mmol/L',1.364,.668,1.050,.563)]}
    moments_c=read(HE/'generator/shared_moments.json')
    specs=[('case_a',ross,schema_a,PAPER/'evaluation/real.csv',[PAPER/'allowed/evidence.json',PAPER/'allowed/schema.json']),('case_b',moments_b,None,TRAVERS/'evaluation/real_extracted.csv',[TRAVERS/'generator/INPUT.md']),('case_c',moments_c,None,HE/'evaluation/real_extracted.csv',[HE/'generator/INPUT.md',HE/'generator/shared_moments.json'])]
    for case,data,schema,reference,sources in specs:
        if schema is None:
            n=12 if case=='case_b' else 44
            design='12 adult men aged 35-55 with abdominal overweight/obesity; fasting measurements before/after 3 days at approximately 50% usual energy intake; no control arm.' if case=='case_b' else '44 completers aged 7-14 with simple obesity; before/after 3-month home diet/exercise program with professional follow-up; no randomized parallel arm; 43 glucose and triglyceride pairs.'
            evidence=dict(n_persons=n,study_design=design,moments=data,evidence_origin='Rounded target-derived marginal means and sample SDs from public IPD; reconstruction regime A0, not independent joint evidence.',not_provided=['individual records','paired covariance','cross-endpoint covariance','change SDs','test statistics','confidence intervals','paper findings'],evidence_items=[dict(id='E_marginals',operator='arithmetic means and sample SDs on complete endpoint pairs',population=design,measurement='Units specified per endpoint; serum leptin ng/mL' if case=='case_b' else 'Units specified per endpoint; leptin already log10(pg/mL)',provenance='source_packet_'+case[-1].upper()),dict(id='E_design',operator='eligibility, pairing and missing-count description',population=design,measurement='fasting measures at pre/post visits',provenance='source_packet_'+case[-1].upper())])
            schema=dict(format='paired_wide',n_persons=n,columns=['participant_id']+[e+'_'+t for e in data for t in ['pre','post']],keys=['participant_id'],fixed_missing_last=case=='case_c')
        else: evidence=data
        packet=ROOT/'packets'/case
        write(packet/'evidence.json',evidence); write(packet/'schema.json',schema)
        shutil.copyfile(reference,ROOT/'custodian'/f'{case}_reference.csv')
        original[case]=dict(reference_path=str(reference),reference_sha256=sha(reference),allowed_sources={str(p):sha(p) for p in sources},exposure='exposed development; coordinator has seen prior findings; fresh builders restricted to anonymized packet')
    shutil.copyfile(PAPER/'paper_analysis.py',ROOT/'custodian/paper_analysis.py')
    write(ROOT/'custodian/provenance.json',dict(cases=original,implementation_reuse={'source_checks_and_controller':'Concepts and selected idioms adapted from population_framework/runner.py and observers.py; original sources untouched','ross_analysis':dict(source=str(PAPER/'paper_analysis.py'),sha256=sha(PAPER/'paper_analysis.py'))},prohibited_publication='Do not upload reference patient files to GitHub'))
    write(ROOT/'analysis_registry.json',analysis_registry())
    protocol=dict(version='stage1_v3',created_utc=utc(),scope='A0 whole-cohort development synthesis only; no completion; no independent confirmation',cases=CASE_IDS,initial_lineages_per_case=3,branches=['ordinary','proposed'],cohorts_per_branch=20,total_agent_cohorts=360,fixed_statistical_cohorts_per_case=20,total_fixed=60,scheduled_source_only_revision_rounds=1,maximum_revision_rounds=2,additional_round_rule='No second scientific revision scheduled in this bounded run; numerical/interface repairs in new version retained, not target feedback',numerical_calibration_budget='At most three examined structures and at most nine unique structure/seed diagnostic cohorts per branch, including discarded ordinary structures; three fixed seeds per structure; initial allowance three; no target feedback; ordinary chooses one final model; proposed retains one to three',source_check_seeds=[810101,810102,810103],final_seeds={case:[910000+1000*i+j for j in range(20)] for i,case in enumerate(CASE_IDS)},allocation={'1':[20],'2':[10,10],'3':[7,7,6]},selection='Final scheduled source-valid candidate; no selection by target or seed. Failed final draws retained, never replaced.',source_compatibility_rule='Schema/key/support/count/reproducibility/input-preservation mandatory. Marginal diagnostic envelope descriptive only; retained scenarios must explain failures; no target-based exclusion.',whole_cohort_inference='Separate cohorts and scenarios only; no row stacking, Rubin pooling, mixture-probability interpretation, or synthetic-patient sample-size inflation.',baseline='One fixed Gaussian-copula statistical family with three sensitivity contexts rho=0/.4/.8 in fixed order, 7/7/6 draws total; PSD shared-person factor kernel, independent endpoint factors; positive lognormal/bounded beta/gamma margins; never fit or select by target',model_metadata={'model_id':'unavailable through subagent tool','provider_parameters':'unavailable','token_counts':'unavailable','latency':'controller timestamps only; not isolated model inference latency'},isolation='Fresh subagents fork_turns=none; delivered path allowlist; procedural not adversarial filesystem sandbox.',metrics=['execution validity','reserved direction/evidence-state agreement','unsupported confident synthetic result when reference CI overlaps null','estimate absolute error','SE ratio','paired change SD ratio and paired-r error','between-scenario evidence-state disagreement'],claims='Target marginal matching is reconstruction, never method success; no clinical equivalence margins invented; no superiority claim from 3 development cases.')
    write(ROOT/'protocol.json',protocol)
    write_text(ROOT/'PROTOCOL.md','# Frozen Stage 1 feasibility protocol\n\nNine initial lineages, paired ordinary/proposed revisions, 360 final Agent cohorts plus 60 fixed statistical cohorts. All three cases are exposed development. Full synthesis only.\n\nThe exact analysis registry distinguishes supplied mean reconstruction from reserved paired variance, dependence and correlations. Scenario allocation is 20, 10/10, or 7/7/6; it is not an inferential mixture. Cohorts are analyzed separately and never Rubin-pooled or row-stacked. All run failures are retained. Repairs use new version directories.\n\nOne source-only revision per branch is scheduled, under a predeclared maximum of two; no target-result feedback. Model identity/provider settings/token counts are unavailable. Builders receive only packet files, source-only checker and their own common-parent files.\n\nFixed seeds, detailed decision contract and analysis definitions are in protocol.json and analysis_registry.json. Statistical reference family has fixed rho=0/.4/.8 copula contexts, allocated 7/7/6 of twenty total cohorts. Rho=0 is conditional maximum-entropy independence; higher persistence uses a PSD shared-person kernel. Endpoint dependence is unidentified. Sensitivities stay separate and are not selected using target performance.\n')
    frozen=['protocol.json','PROTOCOL.md','analysis_registry.json','source_checks.py','fixed_generator.py','runner.py']
    files={name:sha(ROOT/name) for name in frozen}
    for folder in ['packets','custodian']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file(): files[str(p.relative_to(ROOT)).replace('\\','/')]=sha(p)
    write(ROOT/'protocol_freeze.json',dict(created_utc=utc(),files=files,runtime=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__)))
    return dict(status='protocol_frozen',files=len(files))

def request_text(task,run):
    policy={'initial':'Build one statistically plausible program using this packet. Make no attempt to guess reserved results. Select one model, context target.','ordinary':'Improve the supplied common-parent generator using only source diagnostics and evidence. You may reconsider dependence, mapping, missingness or family, and examine up to three candidate structures. Select one final model (context target). A justified no-op is allowed.','proposed':'Review which joint relationships are constrained or unresolved. Retain one to three scientifically distinct evidence-compatible scenarios when unresolved dependencies materially affect declared analyses. Tie each scenario to an assumption, not merely a different seed. Precommit inclusion rationale and affected analysis classes. A justified single scenario is allowed. Do not claim the examined set covers every possible model.','statistical':'Fixed statistical reference.'}[task['branch']]
    analyses='baseline pairwise correlations among pfs/gng/dd100/dd1000; categorical-visit random-intercept trajectories of all five outcomes; four exploratory standardized weight associations' if task['case_id']=='case_a' else 'four paired endpoint change means with paired t intervals, paired covariance/SD diagnostics; six correlations between endpoint changes'
    return f'''# Fresh builder request: {task['run_id']}

Read ONLY files inside this exact run directory: `{run}`. The allowlist is evidence.json, schema.json, task.json, source_checks.py, REQUEST.md, decision_template.json, and (branches only) parent/generator.py, parent/decision.json, parent/source_feedback.json. Do not inspect ancestors, sibling runs, existing experiments, papers, reference data, evaluations, environment history, or the internet. Do not follow provenance outside the packet. The source labels are anonymous. All target outcomes are reserved to the evaluator.

Write ONLY generator.py and decision.json in this run directory. This is an executable program construction task; source-only Python calculations are allowed. Do not author patient rows directly. Use numpy/pandas/scipy only plus ordinary math/typing/copy/json/itertools; no file/network I/O in generator; use local np.random.default_rng(seed); never mutate evidence. Function: `generate(n, seed, evidence, context="target") -> pandas.DataFrame`. Return columns in schema.json order. n denotes persons. For multiple scenarios, context dispatches the declared scenario ID. Use exact counts/support from packet; new synthetic keys. Code must generalize n by scaling missing counts, although final evaluation fixes n.

Declared analysis classes: {analyses}. No coefficients/directions/p values/intervals are provided. Means supplied in the packet are reconstruction inputs, not validation successes. Missing evidence is unknown, not zero.

Policy: {policy}

One initial submission and one scheduled source-only branch revision; maximum two revisions predeclared but no second scientific round scheduled. Up to three candidate structures within a branch. Numerical source calibration budget: initial construction at most three unique diagnostic cohorts; either revision policy at most nine unique structure/seed cohorts across at most three examined structures, using seeds 810101, 810102, 810103 only. Ordinary may spend its equal budget on rejected alternatives. Log every examined structure, its evaluated seeds, disposition and reason in calibration_log. Controller checks three scheduled seeds per retained structure within this allowance, not additional unique cohorts. No reserved-target feedback or seed selection. Final twenty total cohorts use controller seeds. Allocate one scenario=20, two=10/10, three=7/7/6 in committed order. Ordinary/initial scenario ID must be target. Scenario frequency is resource allocation, not a posterior probability.

Use decision_template.json. Required fields are checked by source_checks.validate_decision. Every evidence item must have use/qualify/defer, reason, operator, population, measurement and provenance. Describe components, unresolved dependencies, parent changes, scientific scenario differences, intended/unvalidated uses and the next discriminating information request. Model ID and provider/token metadata must be explicitly unavailable if not supplied by the tool; do not invent them. Source feedback results may be 'not yet run; controller will attach'.

You may run source_checks via local Python importing only this directory. No need to create sample CSVs; the controller persists diagnostics and final cohorts. Return the two absolute artifact paths, a short source-only explanation, and any limitations. Never read evaluator results. These are synthetic rehearsal datasets; no validated clinical or new empirical findings are claimed.
'''

def decision_template(task,evidence,baseline=False):
    return dict(run_id=task['run_id'],lineage_id=task['lineage_id'],branch=task['branch'],action='fixed_statistical_reference' if baseline else ('build' if task['branch']=='initial' else 'revise'),model_metadata=dict(model_id='unavailable',provider_settings='unavailable',token_counts='unavailable'),model_family='Describe selected family',evidence_use=[dict(x,action='use',reason='Explain use/qualification') for x in evidence['evidence_items']],components=[dict(name='generator',evidence_ids=['E_marginals','E_design'],source_to_target_assumptions='Same-population A0 reconstruction; dependence unspecified')],scenarios=[dict(id='target',n_cohorts=20,assumption='Describe unresolved dependence assumption',inclusion_rationale='Explain scientific rationale',unresolved_dependencies=['within-person and cross-endpoint dependence'],affected_analysis_classes=['reserved dependence and uncertainty'])],changes_from_parent='initial build' if task['branch']=='initial' else 'Describe changes or justified no-op',source_check_results='not yet run; controller will attach',calibration_log=dict(examined_structures=[dict(id='model_1',source_seeds_evaluated=[],disposition='retained',reason='Selected source-compatible model; fill scientific rationale')],final_scenario_to_structure={'target':'model_1'}),intended_uses=['analysis rehearsal'],unvalidated_uses=['clinical decisions','new empirical evidence'],next_information_request='Request a discriminating joint summary, not target findings')

def stage(case,lineage,branch='initial',parent=None,version='v1'):
    verify_freeze()
    run=ROOT/('statistical' if branch=='statistical' else 'runs')/case/(f'build_{lineage:02d}' if branch!='statistical' else 'fixed')/(branch+'_'+version)
    if run.exists(): raise FileExistsError('New run version required')
    run.mkdir(parents=True)
    task=dict(case_id=case,lineage_id=f'{case}_build_{lineage:02d}',run_id=f'{case}_build_{lineage:02d}_{branch}_{version}',branch=branch,version=version,regime='whole_cohort',created_utc=utc(),parent=None)
    if branch in ['ordinary','proposed']:
        parent=Path(parent).resolve(); manifest=read(parent/'candidate_manifest.json')
        verify_files(parent,manifest['files'])
        if manifest['status']!='valid': raise ValueError('Cannot branch invalid parent')
        pt=read(parent/'task.json')
        if pt['case_id']!=case or pt['lineage_id']!=task['lineage_id']: raise ValueError('Parent lineage mismatch')
        task['parent']=dict(manifest_sha256=sha(parent/'candidate_manifest.json'),generator_sha256=sha(parent/'generator.py'),decision_sha256=sha(parent/'decision.json'),source_feedback_sha256=sha(parent/'source_feedback.json'))
        (run/'parent').mkdir()
        for f in ['generator.py','decision.json','source_feedback.json']: shutil.copyfile(parent/f,run/'parent'/f)
    for f in ['evidence.json','schema.json']: shutil.copyfile(ROOT/'packets'/case/f,run/f)
    shutil.copyfile(ROOT/'source_checks.py',run/'source_checks.py')
    write(run/'task.json',task)
    write(run/'decision_template.json',decision_template(task,read(run/'evidence.json'),branch=='statistical'))
    write_text(run/'REQUEST.md',request_text(task,run))
    write(run/'staging_lock.json',dict(files=files_manifest(run),protocol_sha256=sha(ROOT/'protocol_freeze.json')))
    if branch=='statistical':
        shutil.copyfile(ROOT/'fixed_generator.py',run/'generator.py')
        dec=decision_template(task,read(run/'evidence.json'),True)
        dec['model_family']='Gaussian copula sensitivity family; independent endpoints; PSD shared-person dependence; bounded/positive margins'
        base=dec['scenarios'][0]
        dec['scenarios']=[dict(base,id=label,n_cohorts=count,assumption=f'Fixed latent within-person rho={rho}; endpoint independence; count-conditioned independent missingness',inclusion_rationale='Frozen dependence sensitivity; never tuned or selected using target analyses') for label,rho,count in [('rho_0',0,7),('rho_04',.4,7),('rho_08',.8,6)]]
        dec['calibration_log']=dict(examined_structures=[dict(id=s['id'],source_seeds_evaluated=[],disposition='retained',reason='Prespecified statistical dependence sensitivity') for s in dec['scenarios']],final_scenario_to_structure={s['id']:s['id'] for s in dec['scenarios']})
        write(run/'decision.json',dec)
    return str(run)

def check_candidate(run):
    run=Path(run).resolve(); verify_freeze()
    if (run/'candidate_manifest.json').exists(): raise FileExistsError('Candidate already executed; use new version')
    if (run/'RETIRED.json').exists(): raise ValueError('Run retired by documented prelaunch amendment')
    if read(run/'staging_lock.json')['protocol_sha256']!=sha(ROOT/'protocol_freeze.json'): raise ValueError('Run belongs to superseded protocol freeze')
    verify_files(run,read(run/'staging_lock.json')['files'])
    task=read(run/'task.json'); evidence=read(run/'evidence.json'); schema=read(run/'schema.json')
    t0=time.perf_counter(); feedback=dict(kind='source_only',created_utc=utc(),target_results_loaded=False,checks=[],errors=[])
    status='invalid'
    try:
        counts=validate_decision(read(run/'decision.json'),task,evidence)
        module=load_generator(run/'generator.py')
        for context in counts:
            dfs=[]
            for seed in read(ROOT/'protocol.json')['source_check_seeds']:
                df=call_checked(module,schema,copy.deepcopy(evidence),seed,context)
                second=call_checked(module,schema,copy.deepcopy(evidence),seed,context)
                if not df.equals(second): raise ValueError('Reproducibility failed')
                dfs.append(df)
                feedback['checks'].append(dict(context=context,seed=seed,diagnostics=source_diagnostics(df,schema,evidence)))
            if all(dfs[0].equals(x) for x in dfs[1:]): raise ValueError('Seed has no effect')
            # Input-use probe only; not an accuracy score or target feedback.
            changed=copy.deepcopy(evidence)
            if 'moments' in changed:
                e=next(iter(changed['moments'])); changed['moments'][e]['pre_mean']*=1.01
            else: changed['marginal_summaries'][0]['mean']*=1.01
            probe=module.generate(schema['n_persons'],810101,changed,context=context)
            feedback.setdefault('input_use_probes',[]).append(dict(context=context,mean_perturbation_changes_output=not dfs[0].equals(probe)))
        status='valid'
    except Exception as e:
        feedback['errors'].append(dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc()))
    feedback.update(status=status,elapsed_seconds=time.perf_counter()-t0)
    write(run/'source_feedback.json',feedback)
    write(run/'candidate_manifest.json',dict(status=status,created_utc=utc(),files=files_manifest(run),task=task,protocol_sha256=sha(ROOT/'protocol_freeze.json')))
    return dict(run=str(run),status=status,errors=feedback['errors'])

def execute_final(run):
    run=Path(run).resolve(); verify_freeze()
    manifest=read(run/'candidate_manifest.json'); verify_files(run,manifest['files'])
    if manifest['status']!='valid': raise ValueError('Invalid candidate')
    if (run/'final').exists(): raise FileExistsError('Final execution already exists; no overwrite')
    task=read(run/'task.json')
    if task['branch']=='initial': raise ValueError('Initial artifacts are not final arms')
    dec=read(run/'decision.json'); evidence=read(run/'evidence.json'); schema=read(run/'schema.json')
    counts=validate_decision(dec,task,evidence); module=load_generator(run/'generator.py')
    out=run/'final'; out.mkdir(); records=[]; cursor=0
    seeds=read(ROOT/'protocol.json')['final_seeds'][task['case_id']]
    for context,count in counts.items():
        for _ in range(count):
            seed=seeds[cursor]; cursor+=1; t0=time.perf_counter()
            rec=dict(draw=cursor,seed=seed,scenario=context,status='failed')
            try:
                df=call_checked(module,schema,copy.deepcopy(evidence),seed,context)
                path=out/f'cohort_{cursor:02d}_{context}_{seed}.csv'; csv_new(df,path)
                rec.update(status='ok',path=path.name,sha256=sha(path),n_rows=len(df))
            except Exception as e: rec['error']=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc())
            rec['elapsed_seconds']=time.perf_counter()-t0; records.append(rec)
            write(out/f'draw_{cursor:02d}.json',rec)
    write(out/'manifest.json',dict(created_utc=utc(),candidate_manifest_sha256=sha(run/'candidate_manifest.json'),task=task,scenario_allocation=counts,records=records,files=files_manifest(out),cohorts_requested=20,cohorts_saved=sum(x['status']=='ok' for x in records)))
    return dict(run=str(run),requested=20,saved=sum(x['status']=='ok' for x in records))

def paired_analysis(df,case):
    endpoints=['leptin' if case=='case_b' else 'leptin_log10','body_mass','glucose','triglycerides']; out=[]; changes={}
    for e in endpoints:
        d=df[[e+'_pre',e+'_post']].dropna(); change=d.iloc[:,1]-d.iloc[:,0]; changes[e]=df[e+'_post']-df[e+'_pre']; n=len(change)
        est=change.mean(); sd=change.std(ddof=1); se=sd/np.sqrt(n); crit=stats.t.ppf(.975,n-1)
        out.append(dict(analysis='paired_change',term=e,estimate=est,se=se,ci_low=est-crit*se,ci_high=est+crit*se,p=2*stats.t.sf(abs(est/se),n-1) if se>0 else None,status='ok' if se>0 else 'degenerate',n_persons=n,n_rows=n,change_sd=sd,paired_r=d.corr().iloc[0,1],role='given/reconstruction',uncertainty_role='reserved paired covariance'))
    for x,y in itertools.combinations(endpoints,2):
        d=pd.DataFrame({x:changes[x],y:changes[y]}).dropna(); n=len(d)
        if n<4 or d[x].nunique()<2 or d[y].nunique()<2:
            out.append(dict(analysis='change_pearson',term=x+'__'+y,estimate=None,se=None,ci_low=None,ci_high=None,p=None,status='degenerate',n_persons=n,n_rows=n,role='reserved')); continue
        r,p=stats.pearsonr(d[x],d[y]); z=np.arctanh(np.clip(r,-1+1e-14,1-1e-14)); zse=1/np.sqrt(n-3); lo,hi=np.tanh([z-1.95996398454*zse,z+1.95996398454*zse])
        out.append(dict(analysis='change_pearson',term=x+'__'+y,estimate=r,se=(1-r*r)*zse,ci_low=lo,ci_high=hi,p=p,status='ok',n_persons=n,n_rows=n,role='reserved'))
    return clean(out)

def analyze(df,case):
    if case!='case_a': return paired_analysis(df,case)
    spec=importlib.util.spec_from_file_location('stage1_pinned_paper_analysis',ROOT/'custodian/paper_analysis.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return clean(m.analyze(df,include_exploratory=True))
def evidence_state(r):
    if r.get('status')!='ok' or r.get('ci_low') is None or r.get('ci_high') is None: return 'unavailable'
    return 'positive' if r['ci_low']>0 else ('negative' if r['ci_high']<0 else 'overlaps_null')

def evaluate(out_name='evaluation_v1'):
    verify_freeze()
    manifests=final_inventory()  # Gate before loading any reference or analysis result.
    out=ROOT/'custodian'/out_name
    if out.exists(): raise FileExistsError('Evaluation output exists')
    out.mkdir(); registry=read(ROOT/'analysis_registry.json'); references={}; rows=[]; dataset_errors=[]
    for case in CASE_IDS:
        references[case]=analyze(pd.read_csv(ROOT/'custodian'/f'{case}_reference.csv'),case)
        write(out/f'{case}_reference_analyses.json',references[case])
    for mf in manifests:
        fm=read(mf); run=mf.parent.parent; task=fm['task']; case=task['case_id']; verify_files(mf.parent,fm['files']); ref={(r['analysis'],r['term']):r for r in references[case]}
        expected={(r['analysis'],r['term']) for r in registry if r['case_id']==case}
        for rec in fm['records']:
            meta={k:task[k] for k in ['case_id','lineage_id','run_id','branch']}; meta.update(draw=rec['draw'],scenario=rec['scenario'],seed=rec['seed'])
            if rec['status']!='ok':
                dataset_errors.append(dict(meta,status='generation_failed',error=rec.get('error')))
                analyses=[dict(analysis=a,term=t,status='generation_failed',estimate=None,se=None,ci_low=None,ci_high=None) for a,t in sorted(expected)]
            else:
                try:
                    analyses=analyze(pd.read_csv(mf.parent/rec['path']),case)
                    if {(r['analysis'],r['term']) for r in analyses}!=expected: raise ValueError('Unexpected analysis inventory')
                except Exception as e:
                    dataset_errors.append(dict(meta,status='analysis_failed',error=type(e).__name__))
                    analyses=[dict(analysis=a,term=t,status='analysis_failed',estimate=None,se=None,ci_low=None,ci_high=None) for a,t in sorted(expected)]
            for r in analyses:
                key=(r['analysis'],r['term']); rr=ref[key]; policy=next(x for x in registry if x['case_id']==case and (x['analysis'],x['term'])==key)
                state=evidence_state(r); refstate=evidence_state(rr); valid=state!='unavailable' and refstate!='unavailable'
                row=dict(meta,**r,validation_role=policy['validation_role'],multiplicity_family=policy['multiplicity_family'],evidence_state=state,reference_evidence_state=refstate,reference_estimate=rr['estimate'],reference_se=rr['se'],reference_ci_low=rr['ci_low'],reference_ci_high=rr['ci_high'],valid_comparison=valid)
                if valid:
                    row.update(evidence_state_agreement=state==refstate,unsupported_evidence_discrepancy=refstate=='overlaps_null' and state in ['positive','negative'],reference_direction_established=refstate in ['positive','negative'],direction_agreement=(np.sign(r['estimate'])==np.sign(rr['estimate'])) if refstate in ['positive','negative'] else None,absolute_estimate_error=abs(r['estimate']-rr['estimate']),se_ratio=r['se']/rr['se'] if rr['se']>0 else None)
                    if 'change_sd' in r: row.update(change_sd_ratio=r['change_sd']/rr['change_sd'],paired_r_absolute_error=abs(r['paired_r']-rr['paired_r']))
                rows.append(row)
    write(out/'analysis_records.json',rows); write(out/'dataset_failures.json',dataset_errors)
    table=pd.DataFrame(rows); csv_new(table,out/'analysis_records.csv')
    groups=[]
    if len(table):
        grouping=['case_id','lineage_id','branch','scenario','validation_role','multiplicity_family','analysis','term']
        for key,g in table.groupby(grouping,dropna=False):
            valid=g.loc[g.valid_comparison]
            groups.append(dict(zip(grouping,key),analyses_total=len(g),analyses_usable=len(valid),usable_fraction=len(valid)/len(g),evidence_state_agreement=float(valid.evidence_state_agreement.mean()) if len(valid) else None,unsupported_evidence_discrepancies=int(valid.unsupported_evidence_discrepancy.sum()) if len(valid) else 0,median_absolute_estimate_error=float(valid.absolute_estimate_error.median()) if len(valid) else None,median_se_ratio=float(valid.se_ratio.median()) if len(valid) else None))
    write(out/'scenario_summaries.json',groups)
    # Scenario distributions and paired lineage comparisons remain term-specific.
    # These are descriptive finite-scenario sensitivity ranges, never CI/model weights.
    sensitivities=[]; paired=[]
    if len(table):
        for key,g in table.groupby(['case_id','lineage_id','branch','analysis','term']):
            scenario_states={}
            for scenario,sg in g.groupby('scenario'):
                counts=sg.evidence_state.value_counts().to_dict(); denom=len(sg)
                estimates=sg.loc[sg.status.eq('ok'),'estimate'].dropna()
                scenario_states[scenario]=dict(n=denom,median_estimate=float(estimates.median()) if len(estimates) else None,estimate_range=[float(estimates.min()),float(estimates.max())] if len(estimates) else None,states=counts,rates={k:v/denom for k,v in counts.items()},modal_states=sorted([k for k,v in counts.items() if v==max(counts.values())]))
            modes=[v['modal_states'] for v in scenario_states.values()]
            sensitivities.append(dict(zip(['case_id','lineage_id','branch','analysis','term'],key),scenarios=scenario_states,number_of_scenarios=len(scenario_states),between_scenario_modal_evidence_state_disagreement=len({tuple(x) for x in modes})>1,interpretation='Empirical modal-state disagreement across examined scenarios; finite Monte Carlo noise can contribute, so not proof of structural disagreement. Unequal allocations are budget, not posterior probability'))
        for key,g in table.loc[table.branch.isin(['ordinary','proposed'])].groupby(['case_id','lineage_id','analysis','term']):
            rec=dict(zip(['case_id','lineage_id','analysis','term'],key)); arms={}
            for branch,bg in g.groupby('branch'):
                by_scenario=[]
                for scenario,sg in bg.groupby('scenario'):
                    vg=sg.loc[sg.valid_comparison]
                    by_scenario.append(dict(scenario=scenario,draws=len(sg),usable=len(vg),evidence_state_agreement=float(vg.evidence_state_agreement.mean()) if len(vg) else None,unsupported_evidence_discrepancy_rate=float(vg.unsupported_evidence_discrepancy.mean()) if len(vg) else None,median_absolute_estimate_error=float(vg.absolute_estimate_error.median()) if len(vg) else None))
                arms[branch]=by_scenario
            rec.update(arms=arms,interpretation='Paired common initial construction; compare ordinary with each proposed scenario, no pooled proposed effect or inferential mixture')
            paired.append(rec)
    write(out/'scenario_sensitivity.json',sensitivities)
    write(out/'paired_lineage_comparisons.json',paired)
    write(out/'evaluation_manifest.json',dict(created_utc=utc(),protocol_sha256=sha(ROOT/'protocol_freeze.json'),final_manifests={str(p.relative_to(ROOT)):sha(p) for p in manifests},n_final_manifests=len(manifests),requested_cohorts=sum(read(p)['cohorts_requested'] for p in manifests),analysis_records=len(rows),reference_analysis_records=sum(map(len,references.values())),files=files_manifest(out),claim_limits=['Development only','No model mixture or MI pooling','Given mean matching not success','Case-level and lineage/scenario results retained; analyses/seeds are not independent studies']))
    return dict(output=str(out),cohorts=sum(read(p)['cohorts_requested'] for p in manifests),analysis_records=len(rows))

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='action',required=True)
    sub.add_parser('prepare'); sub.add_parser('stageinitial'); sub.add_parser('stagestatistical')
    for action in ['checkcandidate','executefinal']:
        q=sub.add_parser(action); q.add_argument('run')
    q=sub.add_parser('stagebranch'); q.add_argument('parent'); q.add_argument('branch',choices=['ordinary','proposed']); q.add_argument('--version',default='v1')
    q=sub.add_parser('evaluate'); q.add_argument('--out',default='evaluation_v1')
    a=p.parse_args()
    if a.action=='prepare': result=prepare()
    elif a.action=='stageinitial': result=[stage(c,i) for c in CASE_IDS for i in range(1,4)]
    elif a.action=='stagestatistical': result=[stage(c,0,'statistical') for c in CASE_IDS]
    elif a.action=='checkcandidate': result=check_candidate(a.run)
    elif a.action=='executefinal': result=execute_final(a.run)
    elif a.action=='stagebranch':
        task=read(Path(a.parent)/'task.json'); result=stage(task['case_id'],int(task['lineage_id'].split('_')[-1]),a.branch,a.parent,a.version)
    else: result=evaluate(a.out)
    print(json.dumps(clean(result),indent=2,allow_nan=False))
if __name__=='__main__': main()
