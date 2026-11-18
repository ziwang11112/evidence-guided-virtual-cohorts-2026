"""Bounded second-case evidence-content experiment; Agent laws are never authored here."""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, random, sys
import numpy as np
import pandas as pd
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
OLD=PROJECT/'work/iron_breadth_2026-11-05'
PRIOR=PROJECT/'work/pns_evidence_content_control_2026-11-16'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
    s.loader.exec_module(m);return m
engine=load('iron_content_shared_engine',PROJECT/'work/pns_joint_evidence_2026-11-16/experiment.py')
adapter=load('iron_content_adapter',ROOT/'analysis_adapter.py')
engine.ROOT=ROOT
engine.REFERENCE=OLD/'evaluation/TARGET.json'
engine.PRIMARY=adapter.PRIMARY
engine.ENDPOINTS=adapter.ENDPOINTS
engine.SEEDS=[16311,16313,16317]
engine.client.CAPS={'openai':3.0}
engine.runtime._generated_statistics=adapter.statistics
read=engine.read;write=engine.write;sha=engine.sha;check=engine.check
ARMS=['BASE','SUMMARY','JOINT']
SOURCE=ROOT/'sources/zhu2010_original.pdf'
SOURCE_ROWS=[
 [0,0,0,732,45,687],[0,1,0,183,17,166],
 [0,0,1,283,96,187],[0,1,1,74,26,48],
 [1,0,0,188,22,166],[1,1,0,64,1,63],
 [1,0,1,111,43,68],[1,1,1,36,8,28]
]
def prepare():
    check(not (ROOT/'inputs/schedule.json').exists(),'Already prepared')
    task={'schema_version':1,'task_id':'iron_evidence_content_control_v1','mode':'whole_cohort',
          'population':'The phlebotomy-weighted complete-measurement domain of nonpregnant women aged 20–44 in NHANES August 2021–August 2023; RIDEXPRG=2, both measured hemoglobin and raw ferritin, positive phlebotomy weight. Pregnancy unknown/incomplete excluded; no CRP restriction. Equal-weight virtual rows represent this domain only under explicit transport assumptions. No individual measurements or target outcome summaries are supplied.',
          'row_id':'row_id','n_rows':5000,
          'columns':[{'name':'row_id','kind':'integer','unit':'','role':'identifier','nullable':False},
                     {'name':'hb_g_dl','kind':'number','unit':'g/dL','role':'generated','nullable':False,'minimum':0},
                     {'name':'ferritin_ug_l','kind':'number','unit':'ug/L raw ferritin','role':'generated','nullable':False,'minimum':0}],
          'information_policy':{'mode':'published_evidence','excluded_cohorts':['NHANES','National Health and Nutrition Examination Survey','evidence-guided-virtual-cohorts'],'allowed_tools':[]},
          'budget':{'source_queries':0,'source_downloads':0,'revisions':0}}
    engine.contracts.validate_task(task)
    analyses=[
      {'id':'odds_ratio','question':'Crude odds ratio for Hb <12 g/dL among raw ferritin <15 ug/L versus ferritin >=15 ug/L; do not adjust for other variables.',
       'operator':'For cells a=both low,b=Hb low only,c=ferritin low only,d=neither: (a*d)/(b*c). If any cell is zero, report not estimable with no continuity correction.'},
      {'id':'joint_prevalence','question':'What fraction has both Hb <12 g/dL and raw ferritin <15 ug/L?','operator':'a/n on exactly the same rows.'},
      {'id':'spearman','question':'How strongly do the continuous Hb and raw ferritin measurements rank together?',
       'operator':'Spearman correlation with average ranks for ties on the same rows; constant ranks are not estimable.'}
    ]
    context={'source_id':'ZHU2010','doi':'10.1024/0300-9831/a000014',
      'title':'Iron, Folate, and B12 Deficiencies and their Associations with Anemia among Women of Childbearing Age in a Rural Area in Northern China',
      'population':'Xianghe County, China, June 2004; 1671 nonpregnant/nonlactating parous women 2–4 years postpartum using IUD contraception. Chronic disease, prescription medications and recent multivitamin use excluded as specified in Methods.',
      'n':1671,'overlap':'Tables I and IV describe the same women, not independent samples. Source study is not the NHANES target.',
      'measurement':'Duplicate fasting venous HemoCue Hb; raw EDTA plasma ferritin by Randox immunoturbidimetry. Hb g/L divided by 10 gives g/dL. Ferritin ug/L is the admitted interpretation from the explicit Table I cutoff and Tables III/IV.',
      'thresholds':{'hb_low':'Hb <120 g/L (equivalently <12 g/dL)','ferritin_low':'raw ferritin <15 ug/L'},
      'caveats':['Source/target population, assay, parity, postpartum and contraceptive selection differ; no transfer function is identified.',
                 'Table I Hb location is inconsistently labelled mean/geometric mean; its numerical value is omitted. Ferritin header and one Methods cutoff contain unit-printing inconsistencies; admitted units follow explicit threshold/table labels.',
                 'Broad printed concentration intervals have unclear construction and are omitted; do not treat them as SD or SE.',
                 'Source sampling/weighting details do not identify target weights or target conditional relationships. Model and transport uncertainty are not sampling variation.',
                 'Only selected source fields are provided in this controlled experiment. Omitted relationships are unknown, not zero or independent. No continuous rank coefficient is supplied.']}
    marginal=[
      {'id':'FERRITIN_GM','variable':'ferritin_ug_l','statistic':'geometric mean','value':17.4,'unit':'ug/L','n':1671,'locator':'Table I, PDF page 4','status':'REPORTED','uncertainty':'not supplied in this payload; no SD inferred'},
      {'id':'HB_LOW','variable':'hb_g_dl','statistic':'count below strict cutoff','count':258,'denominator':1671,'threshold':12,'unit':'g/dL','locator':'Table I, PDF page 4','status':'REPORTED'},
      {'id':'FERRITIN_LOW','variable':'ferritin_ug_l','statistic':'count below strict cutoff','count':504,'denominator':1671,'threshold':15,'unit':'ug/L','locator':'Table I, PDF page 4','status':'REPORTED'}]
    cells={'both_low':sum(r[4] for r in SOURCE_ROWS if r[2]),
           'only_hb_low':sum(r[4] for r in SOURCE_ROWS if not r[2]),
           'only_ferritin_low':sum(r[5] for r in SOURCE_ROWS if r[2]),
           'neither_low':sum(r[5] for r in SOURCE_ROWS if not r[2])}
    joint=[{'id':'PAIRED_THRESHOLD_COUNTS','statistic':'two-way contingency counts; no covariate adjustment',
            'cells':cells,'n':1671,'cutoffs':{'hb_g_dl':12,'ferritin_ug_l':15},'inequality':'strict less-than; equality belongs to upper group',
            'status':'DERIVED_FROM_REPORTED_COUNTS','derivation':'Sum the eight mutually exclusive Table IV rows over folate and B12 categories, retaining ferritin category and Hb anemia columns.',
            'locator':'Table IV, PDF page 7','uncertainty':'Exact displayed sample counts; no target or transport interval supplied.'}]
    inp=ROOT/'inputs'
    write(inp/'generation_task.json',task);write(inp/'requested_analyses.json',analyses)
    for arm in ARMS:
        evidence={'context':copy.deepcopy(context),'marginal_statistics':[] if arm=='BASE' else copy.deepcopy(marginal),
                  'joint_statistics':copy.deepcopy(joint) if arm=='JOINT' else []}
        payload={'task':task,'requested_analyses':analyses,'approved_source_evidence':evidence}
        write(inp/(arm+'.json'),payload)
        (inp/(arm+'.prompt.txt')).write_text(engine.make_prompt(payload),encoding='utf8')
    slots=[{'id':f'{a}_{i}','arm':a,'author_repetition':i} for a in ARMS for i in range(1,4)]
    random.Random(16310).shuffle(slots);write(inp/'schedule.json',slots)
    write(ROOT/'SOURCE_EXTRACTION.json',{'source_sha256':sha(SOURCE),'columns':['folate_low','b12_low','ferritin_low','n','hb_low','hb_not_low'],'table_iv_rows':SOURCE_ROWS,
      'collapsed_counts':cells,'table_i_low_hb':258,'table_i_low_ferritin':504,'table_i_ferritin_geometric_mean':17.4,
      'review':'Root original-page visual check; values reconcile with the preserved prior independent source audit. No OR supplied to author.'})
    (ROOT/'TARIFF.json').write_bytes((PRIOR/'TARIFF.json').read_bytes())
    old_paths=[p for folder in [OLD,PRIOR] for p in folder.rglob('*') if p.is_file()]
    write(ROOT/'OLD_IMMUTABILITY.json',{p.relative_to(PROJECT).as_posix():sha(p) for p in old_paths})
    print(json.dumps({'prepared':True,'authors':9,'planned_tables':27,'source_count_total':sum(cells.values()),'target_reference_parsed':False}))

def preflight():
    check(not (ROOT/'PREFLIGHT.json').exists(),'Preflight already closed')
    checks=[];payload={a:read(ROOT/'inputs'/(a+'.json')) for a in ARMS}
    check(all(o['task']==engine.task() and o['requested_analyses']==payload['BASE']['requested_analyses'] for o in payload.values()),'Task/operator mismatch')
    m=copy.deepcopy(payload['SUMMARY']);j=copy.deepcopy(payload['JOINT'])
    joint=j['approved_source_evidence'].pop('joint_statistics');check(m['approved_source_evidence'].pop('joint_statistics')==[] and m==j,'Increment is not joint-only')
    b=copy.deepcopy(payload['BASE']);s=copy.deepcopy(payload['SUMMARY'])
    b['approved_source_evidence'].pop('marginal_statistics');s['approved_source_evidence'].pop('marginal_statistics')
    check(b==s,'Base/summary context differs');checks.append('three conditions share task/context; increments are exact')
    source=read(ROOT/'SOURCE_EXTRACTION.json')
    check(all(r[3]==r[4]+r[5] for r in SOURCE_ROWS),'Source row total mismatch')
    cells=source['collapsed_counts'];check(cells=={'both_low':173,'only_hb_low':85,'only_ferritin_low':331,'neither_low':1082},'Independent prior extraction mismatch')
    check(sum(cells.values())==1671 and cells['both_low']+cells['only_hb_low']==258 and cells['both_low']+cells['only_ferritin_low']==504,'Source margins mismatch')
    check(sha(SOURCE)==source['source_sha256'],'Source bytes changed');checks.append('original count collapse and direct marginal counts reconcile')
    for arm in ARMS:
        prompt=(ROOT/'inputs'/(arm+'.prompt.txt')).read_text(encoding='utf8')
        check(prompt==engine.make_prompt(payload[arm]),'Prompt differs from packet')
        check('REFERENCE_SNAPSHOT' not in prompt and 'evaluation/TARGET' not in prompt and '6.653' not in prompt and '17.79' not in prompt,'Answer/path in prompt')
        if arm!='JOINT':check('both_low' not in json.dumps(payload[arm]['approved_source_evidence']),'Joint cells leaked')
    checks.append('no target aggregate, derived source OR, conditional Table III or full text in prompts')
    task=engine.task()
    def frame(h,f):return pd.DataFrame({'row_id':range(len(h)),'hb_g_dl':h,'ferritin_ug_l':f})
    def get(f):
        t=copy.deepcopy(task);t['n_rows']=len(f);normal=adapter.statistics(f,t);ind,counts=adapter.independent_values(f)
        vals=engine.endpoints(normal)
        for k in adapter.ENDPOINTS:
            v,w=vals[k],ind[k]
            check((v is None and w is None) or (v is not None and w is not None and np.isclose(v,w,atol=1e-12,rtol=1e-12)),'Independent fixture mismatch: '+k)
        return vals,normal
    v,_=get(frame([11,11,12,12],[14,15,14,15]))
    check(v['odds_ratio']==1 and v['joint_prevalence']==.25 and abs(v['spearman'])<1e-12,'Boundary/tie fixture differs')
    checks.append('strict cutoffs, threshold equality and tied-rank fixture')
    v,n=get(frame([11,11,13,13],[10,10,20,20]))
    check(v['odds_ratio'] is None and v['spearman']==1 and 'zero_cell_odds_ratio_not_estimable_no_continuity_correction' in n['flags'],'Zero cell smoothing/error')
    v,_=get(frame([12,12,12,12],[10,15,20,25]));check(v['spearman'] is None,'Constant-rank missingness')
    checks.append('zero cells and constant ranks stay nonestimable')
    h=[11]*4+[13]*4
    v1,_=get(frame(h,[14,14,14,16,14,16,16,16]))
    v2,_=get(frame(h,[14,16,16,16,14,14,14,16]))
    check(np.isclose(v1['odds_ratio'],9) and np.isclose(v2['odds_ratio'],1/9),'Pairing perturbation failed')
    check(v1['low_hb_fraction']==v2['low_hb_fraction'] and v1['low_ferritin_fraction']==v2['low_ferritin_fraction'],'Marginals changed')
    checks.append('same margins with changed pairing changes estimated association')
    for bad in [frame([-1,12],[10,20]),frame([float('nan'),12],[10,20])]:
        try:get(bad)
        except ValueError:pass
        else:raise ValueError('Invalid measurement accepted')
    checks.append('invalid measurement rejection')
    q=ROOT/'integration';candidate=q/'candidate';candidate.mkdir(parents=True)
    fixture="import numpy as np\nimport pandas as pd\ndef generate(observed,spec,seed):\n r=np.random.default_rng(seed);n=spec['task']['n_rows'];k=r.integers(0,4,n);return pd.DataFrame({'row_id':np.arange(n),'hb_g_dl':np.where(k<2,11.,13.),'ferritin_ug_l':np.where(k%2==0,10.,20.)})\n"
    (candidate/'generator.py').write_text(fixture,encoding='utf8')
    fixture_task=copy.deepcopy(task);fixture_task['n_rows']=128
    write(candidate/'model_spec.json',{'task':fixture_task,'model':{}})
    r=engine.runtime.isolated_run(candidate,fixture_task,16303,q/'smoke',engine.LIMITS)
    check(r['status']=='success','Isolated fixture failed: '+str(r.get('error')))
    receipt=read(q/'smoke/execution.json');probe=receipt['worker_report']['pre_import_probe']
    check(not probe['mnt_visible'] and not probe['home_visible'] and not probe['route_table'],'Isolation leak')
    f=pd.read_csv(q/'smoke/output/generated.csv',float_precision='round_trip');get(f)
    check(receipt['statistics']['analyses'][0]['id']=='odds_ratio','Wrong analyzer routing')
    checks.append('new iron adapter connected to unchanged isolated worker; independent recomputation')
    check(bool(engine.client.credentials()['openai']),'Previously authorized credential unavailable')
    checks.append('existing authorized credential present; no new key or secret output')
    write(ROOT/'PREFLIGHT.json',{'passed':True,'checks':checks,'new_api_calls':0,'artificial_fixture_tables':1,'experimental_tables':0,
         'target_reference_parsed':False,'reviewer':'root','independent_recomputation':'preserved separately implemented weighted-midrank estimator'})
    print(json.dumps({'preflight_passed':True,'checks':len(checks)}))

def dependencies():
    paths=[Path(__file__),ROOT/'analysis_adapter.py',ROOT/'ADMISSION_PLAN.md',ROOT/'PROTOCOL.md',ROOT/'SOURCE_AUDIT.md',
           ROOT/'SOURCE_EXTRACTION.json',ROOT/'PREFLIGHT.json',ROOT/'OLD_IMMUTABILITY.json',ROOT/'TARIFF.json',ROOT/'RUNTIME.json',SOURCE,
           PROJECT/'work/pns_joint_evidence_2026-11-16/experiment.py',
           PROJECT/'work/cross_model_api_pilot_2026-11-10/provider_client.py',
           PROJECT/'work/cross_model_api_pilot_2026-11-10/provider_preflight.py',
           PROJECT/'work/request_only_repeatability_2026-11-11/tools_runtime.py',
           OLD/'evaluation/analyze.py',OLD/'evaluation/independent.py',
           OLD/'admission/source_review.md',OLD/'admission/SOURCE_CLARIFICATION.md']
    paths+=list((ROOT/'inputs').glob('*'))
    paths+=list((PROJECT/'cohort_harness').rglob('*.py'))
    return {p.relative_to(PROJECT).as_posix():sha(p) for p in paths}

def freeze():
    check(read(ROOT/'PREFLIGHT.json')['passed'],'Preflight required')
    schedule=read(ROOT/'inputs/schedule.json');reserves=[]
    for r in schedule:
        prompt=(ROOT/'inputs'/(r['arm']+'.prompt.txt')).read_text(encoding='utf8')
        body=engine.client.make_request(engine.CONFIG,prompt)[1]
        size=len(json.dumps(body,ensure_ascii=False).encode())
        check(size<190000,'Request too large')
        reserves.append(((size+4096)*2.5+engine.client.MAX_OUTPUT*10)/1e6)
    check(sum(reserves)<3.0,'Reservations exceed budget')
    write(ROOT/'RUNTIME.json',engine.execution._runtime_manifest(engine.execution._runtime(None)))
    write(ROOT/'GENERATION_FREEZE.json',{'frozen_utc':engine.client.utc(),'files':dependencies(),
      'reference_sha256':sha(engine.REFERENCE),'model_config':engine.client.CONFIGS[engine.CONFIG],
      'system':engine.client.SYSTEM,'max_output_tokens':engine.client.MAX_OUTPUT,'cap_usd':3.0,
      'schedule':schedule,'seeds':engine.SEEDS,'limits':engine.LIMITS,'max_calls':9,'max_tables':27,
      'conservative_schedule_reservation_usd':sum(reserves),'primary_comparison':'JOINT versus SUMMARY average absolute log-OR difference',
      'primary':engine.PRIMARY,'diagnostics':engine.ENDPOINTS[3:],
      'reference_scope':'already exposed iron case; fresh constructions do not reset exposure',
      'source_scope':'same previously admitted source; explicit within-source masks, not historical full-packet baseline'})
    print(json.dumps({'frozen':True,'sha256':sha(ROOT/'GENERATION_FREEZE.json'),'reserved_usd':sum(reserves)}))

def verify():
    f=read(ROOT/'GENERATION_FREEZE.json')
    for p,h in f['files'].items():check(sha(PROJECT/p)==h,'Frozen dependency changed: '+p)
    check(sha(engine.REFERENCE)==f['reference_sha256'],'Reference changed')
    check(f['model_config']==engine.client.CONFIGS[engine.CONFIG] and f['system']==engine.client.SYSTEM,'Model settings changed')
    check(f['max_output_tokens']==engine.client.MAX_OUTPUT and f['cap_usd']==engine.client.CAPS['openai'],'Budget changed')
    check(f['seeds']==engine.SEEDS and f['limits']==engine.LIMITS and len(f['schedule'])==9,'Execution/schedule changed')
    check(engine.runtime._generated_statistics is adapter.statistics,'Iron analyzer not connected')
    return f
engine.verify=verify

def analyze():
    verify()
    cc=read(ROOT/'CONSTRUCTION_CLOSURE.json');ec=read(ROOT/'EXECUTION_CLOSURE.json')
    check(cc['freeze_sha256']==sha(ROOT/'GENERATION_FREEZE.json') and ec['construction_sha256']==sha(ROOT/'CONSTRUCTION_CLOSURE.json'),'Closure changed')
    scheduled={r['id'] for r in read(ROOT/'inputs/schedule.json')}
    check(len(cc['rows'])==9 and {r['id'] for r in cc['rows']}==scheduled,'Missing author outcomes')
    expected={(r['id'],seed) for r in cc['rows'] if r['status']=='sealed' for seed in engine.SEEDS}
    actual={(r['id'],r['seed']) for r in ec['rows']}
    check(len(actual)==len(ec['rows']) and actual==expected,'Execution inventory mismatch')
    authors={r['id']:r for r in cc['rows']}
    records=[];details=[];failures=[];maxdiff=0.;comparisons=0
    for a in cc['rows']:
        if a['status']!='sealed':failures.append({'id':a['id'],'stage':'construction','error':a.get('error')})
    for out in ec['rows']:
        folder=ROOT/'executions'/out['id']/str(out['seed'])
        check(sha(folder/'execution.json')==out['receipt_sha256'],'Execution receipt changed')
        r=read(folder/'execution.json')
        if r['status']!='success':
            failures.append({**out,'stage':'execution','error':r.get('error')});continue
        for name,h in read(folder/'input_bindings.json').items():check(sha(folder/'input'/name)==h,'Staged input changed')
        table=folder/'output/generated.csv';check(sha(table)==r['generated_sha256'],'Rows changed')
        frame=pd.read_csv(table,float_precision='round_trip')
        other,counts=adapter.independent_values(frame);vals=engine.endpoints(r['statistics'])
        check(set(vals)==set(engine.ENDPOINTS),'Wrong endpoint inventory')
        check(counts==[r['statistics']['cells'][k]['n'] for k in adapter.production.CELL_NAMES],'Independent cell counts differ')
        for k,v in vals.items():
            z=other[k]
            if v is None or z is None:check(v is None and z is None,'Nonestimability mismatch')
            else:
                delta=abs(v-z);maxdiff=max(maxdiff,delta);check(np.isclose(v,z,atol=1e-9,rtol=1e-10),'Independent result mismatch: '+k)
            comparisons+=1;records.append({'id':out['id'],'arm':authors[out['id']]['arm'],'seed':out['seed'],'estimand':k,'value':v})
        details.append({**out,'statistics':r['statistics'],'generated_sha256':sha(table)})
    # Only after all constructors and all draws are closed, parse the existing exposed reference.
    ref=read(engine.REFERENCE)
    refs={k:ref['estimands'][k]['estimate'] for k in engine.PRIMARY}
    c=ref['cells']
    refs['low_hb_fraction']=c['both_low']['weighted_fraction']+c['only_hb_low']['weighted_fraction']
    refs['low_ferritin_fraction']=c['both_low']['weighted_fraction']+c['only_ferritin_low']['weighted_fraction']
    for r in records:
        r['reference']=refs[r['estimand']]
        r['absolute_reference_difference']=adapter.discrepancy(r['estimand'],r['value'],r['reference'])
        r['difference_scale']='natural log OR' if r['estimand']=='odds_ratio' else 'native unit'
    summary=[];arms=[]
    for a in cc['rows']:
        for k in engine.ENDPOINTS:
            rr=[r for r in records if r['id']==a['id'] and r['estimand']==k and r['value'] is not None]
            vv=[r['value'] for r in rr]
            summary.append({'id':a['id'],'arm':a['arm'],'estimand':k,'planned_seeds':3,'available_seeds':len(vv),
              'seed_mean':float(np.mean(vv)) if vv else None,'seed_min':min(vv) if vv else None,'seed_max':max(vv) if vv else None,
              'mean_absolute_reference_difference':float(np.mean([r['absolute_reference_difference'] for r in rr])) if rr else None,
              'difference_scale':'natural log OR' if k=='odds_ratio' else 'native unit'})
    for arm in ARMS:
        for k in engine.ENDPOINTS:
            ss=[r for r in summary if r['arm']==arm and r['estimand']==k and r['available_seeds']>0]
            arms.append({'arm':arm,'estimand':k,'planned_authors':3,'available_authors':len(ss),
              'complete_authors':sum(r['available_seeds']==3 for r in ss),
              'author_mean':float(np.mean([r['seed_mean'] for r in ss])) if ss else None,
              'author_mean_absolute_reference_difference':float(np.mean([r['mean_absolute_reference_difference'] for r in ss])) if ss else None,
              'difference_scale':'natural log OR' if k=='odds_ratio' else 'native unit'})
    dest=ROOT/'analysis';dest.mkdir(exist_ok=False)
    for name,obj in [('seed_results',records),('author_results',summary),('arm_results',arms),('details',details),('failures',failures)]:
        write(dest/(name+'.json'),obj)
        if obj and name not in ['details','failures']:pd.DataFrame(obj).to_csv(dest/(name+'.csv'),index=False)
    write(dest/'REFERENCE_USED.json',{'reference_sha256':sha(engine.REFERENCE),'values':refs,'original_aggregate':ref,
          'scope':'previously exposed measured-sample estimates, not known population truths'})
    write(dest/'INDEPENDENT_RECOMPUTATION.json',{'passed':True,'endpoint_comparisons':comparisons,
         'maximum_absolute_difference':maxdiff,'method':'preserved independent weighted-midranks implementation vs production; equal weights on virtual tables',
         'extra_generator_runs':0,'patient_data_read':False})
    receipts=[read(p) for p in (ROOT/'calls').glob('*/receipt.json')]
    costs={'author_calls':len(receipts),'estimated_usd':sum(r.get('tariff_cost_usd') or 0 for r in receipts),
      'unknown_cost_reserved_usd':sum(r['reserved_usd'] for r in receipts if r.get('tariff_cost_usd') is None),
      'requested_models':sorted({r['requested_model'] for r in receipts}),'returned_models':sorted({str(r.get('returned_model')) for r in receipts}),
      'usage':{k:sum((r.get('usage') or {}).get(k) or 0 for r in receipts) for k in ['input','output','cached','reasoning']},
      'invoice':False,'new_search_calls':0,'source_retrieval':'one publisher PDF downloaded, no paid retrieval Agent'}
    write(dest/'COSTS.json',costs)
    write(dest/'SLOT_ACCOUNTING.json',{'planned_constructors':9,'closed_constructors':len(cc['rows']),
      'sealed_constructors':sum(r['status']=='sealed' for r in cc['rows']),'planned_tables':27,
      'attempted_execution_slots':len(ec['rows']),'successful_tables':len(details),
      'failed_execution_slots':sum(r['status']!='success' for r in ec['rows']),
      'unexecuted_due_to_failed_construction':27-len(expected),
      'nonestimable_endpoint_slots':sum(r['value'] is None for r in records),'statistical_unit':'construction; seeds nested'})
    old=read(ROOT/'OLD_IMMUTABILITY.json');check(all(sha(PROJECT/p)==h for p,h in old.items()),'Closed historical artifact changed')
    write(dest/'OLD_INPUT_CHECK.json',{'passed':True,'unchanged_files':len(old)})
    print(json.dumps({'analysis_complete':True,'successful_tables':len(details),'failures':len(failures),
          'independent_max_difference':maxdiff,'estimated_usd':costs['estimated_usd'],'arms':arms}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','preflight','freeze','run','analyze','verify'])
    action=parser.parse_args().action
    if action=='run':engine.run()
    else:globals()[action]()

