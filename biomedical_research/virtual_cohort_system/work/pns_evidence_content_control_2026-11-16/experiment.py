"""Three-arm evidence-content diagnostic, reusing the frozen isolated runner.

The host edits source cards, never Agent scientific parameters. No target result
is parsed before construction and execution closure.
"""
from pathlib import Path
from collections import defaultdict
import argparse, copy, hashlib, importlib.util, json, random, re, sys
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
OLD=PROJECT/'work/pns_joint_evidence_2026-11-16'
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('content_control_frozen_engine',OLD/'experiment.py')
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
# Runtime-only rebinding leaves the closed experiment's files byte-unchanged.
engine.ROOT=ROOT
engine.SEEDS=[16211,16213,16217]
engine.client.CAPS={'openai':3.0}
ARMS=['BASE','SUMMARY','JOINT']
SOURCE=OLD/'episodes/PNS_SEARCH/gateway/session/approved/caa0c790c33497f11467f2d3a861a87ff8f27df710ade6a3bd6cc45ca0dac1c5.xml'
read,sha,write,check=engine.read,engine.sha,engine.write,engine.check

def extract_source():
    tree=ET.fromstring(SOURCE.read_bytes())
    check(tree.find('.//article-id[@pub-id-type="doi"]').text=='10.1136/bmjopen-2024-089374','Wrong source')
    tables={}
    for table_id in ['T1','T2','T3']:
        node=tree.find(f'.//table-wrap[@id="{table_id}"]')
        tables[table_id]=[[''.join(c.itertext()).strip() for c in r if c.tag in ('td','th')] for r in node.findall('.//tr')]
    numeric=lambda s:float(re.search(r'-?\d+(?:\.\d+)?',s.replace('−','-')).group())
    t1,t2,t3=tables['T1'],tables['T2'],tables['T3']
    counts=next(r for r in t1 if r and r[0].startswith('N='))
    age=next(r for r in t1 if r and r[0]=='Age mean (years)')
    moments=[]
    for variable,label,unit in [('sbp','SBP*','mmHg'),('dbp','DBP','mmHg'),('bmi','BMI†','kg/m^2')]:
        row=next(r for r in t2 if r and r[0]==label)
        moments.append({'variable':variable,'mean':numeric(row[1]),'sample_sd':numeric(row[2]),'unit':unit,'locator':f'T2, {label}, Total columns'})
    idx={r[0]:r for r in t3[1:] if r}
    corr=[]
    for x,y,row,col in [('sbp','dbp','DBP',2),('sbp','age','Age',2),('dbp','age','Age',3),
                        ('sbp','bmi','BMI',2),('dbp','bmi','BMI',3),('age','bmi','BMI',4)]:
        corr.append({'x':x,'y':y,'statistic':'unadjusted Pearson correlation','value':numeric(idx[row][col]),'unit':'dimensionless','locator':f'T3, {row} row, {t3[0][col]} column'})
    card={
      'id':'BF2018','doi':'10.1136/bmjopen-2024-089374','pmcid':'PMC12185928',
      'title':'Association of relationship satisfaction with blood pressure: a cross-sectional study of older adults in rural Burkina Faso.',
      'population':{'study':'2018 CRSN Heidelberg Aging Study, Nouna surveillance area, rural Burkina Faso',
        'eligibility':'Partnered adults aged at least 40; pregnancy and BP medication in previous two weeks excluded. Availability, missingness and outlier exclusions in the source also apply.',
        'n':int(numeric(counts[0])),'women_n':int(numeric(counts[1])),'men_n':int(numeric(counts[2])),
        'mean_age_years':numeric(age[1]),'age_sd':None,'locator':'T1, Total column'},
      'measurement':'BP in mmHg: seated left arm, Omron Series 7, at least 15 minutes rest, three readings; mean of last two. BMI kg/m^2. Source methods do not specify survey weights for these summaries.',
      'marginal_statistics':moments,'relationships':[],
      'uncertainty':'Published rounded estimates. No sampling CI/SE for these supplied moments or correlations. Rounding does not quantify sampling or population-transfer uncertainty.',
      'applicability':['These are source-population quantities, not parameters known for the requested population.',
         'Source age, geography, partnership, treatment exclusion and BP measurement differ from the requested analytical distribution.',
         'Unadjusted correlations, if supplied, are not covariate-adjusted residual correlations. Any linear projection or transport must be justified separately.',
         'Sex-specific joint moments, nonlinear conditional variation, target treatment mixture and matched measurement error are not identified by this card.',
         'The tables describe one common analytical sample; multiple numbers are not independent studies. No overlap with PNS is indicated; participant linkage has not been verified.']}
    joint=copy.deepcopy(card);joint['relationships']=corr
    return card,joint,{'source_path':SOURCE.relative_to(PROJECT).as_posix(),'source_sha256':sha(SOURCE),'original_table_cells':tables,
        'extraction':'explicit total-column and pair-cell allowlist; contains no target values'}

def prepare():
    check(not (ROOT/'inputs/schedule.json').exists(),'Already prepared')
    marginal,joint,audit=extract_source()
    t=read(OLD/'inputs/generation_task.json');t['task_id']='pns_evidence_content_control_v1'
    engine.contracts.validate_task(t)
    inp=ROOT/'inputs';write(inp/'generation_task.json',t)
    write(ROOT/'SOURCE_EXTRACTION.json',audit)
    (inp/'base_evidence.json').write_bytes((OLD/'inputs/base_evidence.json').read_bytes())
    (inp/'requested_analyses.json').write_bytes((OLD/'inputs/requested_analyses.json').read_bytes())
    for arm in ARMS:
        payload={'task':t,'requested_analyses':read(inp/'requested_analyses.json'),
                 'existing_evidence':read(inp/'base_evidence.json'),
                 'additional_study_evidence':None if arm=='BASE' else (marginal if arm=='SUMMARY' else joint)}
        write(inp/(arm+'.json'),payload)
        (inp/(arm+'.prompt.txt')).write_text(engine.make_prompt(payload),encoding='utf8')
    slots=[{'id':f'{a}_{i}','arm':a,'author_repetition':i} for a in ARMS for i in range(1,4)]
    random.Random(16210).shuffle(slots);write(inp/'schedule.json',slots)
    (ROOT/'TARIFF.json').write_bytes((OLD/'TARIFF.json').read_bytes())
    write(ROOT/'OLD_IMMUTABILITY.json',engine.inventory(OLD))
    print(json.dumps({'prepared':True,'authors':9,'new_search_calls':0,'target_parsed':False}))

def preflight():
    engine.contracts.validate_task(engine.task());checks=[]
    payload={a:read(ROOT/'inputs'/(a+'.json')) for a in ARMS}
    stripped={a:{k:v for k,v in obj.items() if k!='additional_study_evidence'} for a,obj in payload.items()}
    check(all(v==stripped['BASE'] for v in stripped.values()),'Common task/base changed')
    checks.append('identical task, analyses and historical base in all conditions')
    m=copy.deepcopy(payload['SUMMARY']['additional_study_evidence']);j=copy.deepcopy(payload['JOINT']['additional_study_evidence'])
    relationships=j.pop('relationships');check(m.pop('relationships')==[] and m==j,'Nonrelationship information differs')
    checks.append('SUMMARY and JOINT differ only in six reported pairwise correlations')
    check(len(relationships)==6,'Wrong pair count')
    source_report=read(OLD/'inputs/additional_evidence.json')['records'][0]['numerical_statistics']
    aliases={'sbp':'SBP','dbp':'DBP','age':'age','bmi':'BMI'}
    order=['sbp','dbp','age','bmi'];matrix=np.eye(4)
    for r in relationships:
        old_key=aliases[r['x']]+'_'+aliases[r['y']]
        check(r['value']==source_report['reported_pearson_correlations'][old_key],'Extraction differs from independently audited prior source')
        a,b=order.index(r['x']),order.index(r['y']);matrix[a,b]=matrix[b,a]=r['value']
    check(np.linalg.eigvalsh(matrix).min()>0,'Source correlation block not positive definite')
    check(m['population']['women_n']+m['population']['men_n']==m['population']['n'],'Source n mismatch')
    for r in m['marginal_statistics']:
        sk={'sbp':'SBP_mmHg','dbp':'DBP_mmHg','bmi':'BMI_kg_m2'}[r['variable']]
        check(r['sample_sd']==source_report['reported_SD'][sk],'Source SD mismatch')
    checks.append('original XML values reconcile with prior source audit; matrix valid')
    for a in ARMS:
        prompt=(ROOT/'inputs'/(a+'.prompt.txt')).read_text(encoding='utf8')
        check(prompt==engine.make_prompt(payload[a]),'Prompt not constructed from approved payload')
        check(all(x not in prompt for x in ['REFERENCE_SNAPSHOT','0.717184','0.787977','derived_partial_correlation']),'Forbidden target or supplied source answer')
    check(sha(ROOT/'inputs/base_evidence.json')==sha(OLD/'inputs/base_evidence.json'),'Base differs')
    checks.append('source derivation and target result excluded; base is byte-identical')
    check(engine.execution._runtime_manifest(engine.execution._runtime(None))==read(OLD/'RUNTIME.json'),'Existing runtime changed')
    checks.append('same runtime manifest as the completed isolated and independently recomputed experiment')
    key_present=bool(engine.client.credentials()['openai']);check(key_present,'Existing authorized OpenAI credential unavailable')
    checks.append('previously authorized credential present; no secret output or write')
    write(ROOT/'PREFLIGHT.json',{'passed':True,'checks':checks,'source_matrix_min_eigenvalue':float(np.linalg.eigvalsh(matrix).min()),
        'target_parsed':False,'new_api_calls':0,'new_patient_data_read':False,'reviewer':'root',
        'reused_execution_evidence':str(OLD/'PREFLIGHT.json'),
        'controls_not_claimed':['equal prompt length','automatic source admission','new target family','unseen target outcomes for root']})
    print(json.dumps({'preflight_passed':True,'checks':len(checks)}))

def dependencies():
    # Bind the proven client/runtime/analysis chain and archived source trajectory.
    f=dict(read(OLD/'GENERATION_FREEZE.json')['files'])
    paths=[Path(__file__),ROOT/'PROTOCOL.md',ROOT/'SOURCE_AUDIT.md',ROOT/'SOURCE_EXTRACTION.json',
           ROOT/'PREFLIGHT.json',ROOT/'OLD_IMMUTABILITY.json',ROOT/'TARIFF.json',ROOT/'RUNTIME.json']
    paths+=list((ROOT/'inputs').glob('*'))
    f.update({x.relative_to(PROJECT).as_posix():sha(x) for x in paths})
    return f

def freeze():
    check(read(ROOT/'PREFLIGHT.json')['passed'],'Preflight required')
    schedule=read(ROOT/'inputs/schedule.json');reserves=[]
    for row in schedule:
        prompt=(ROOT/'inputs'/(row['arm']+'.prompt.txt')).read_text(encoding='utf8')
        body=engine.client.make_request(engine.CONFIG,prompt)[1];size=len(json.dumps(body,ensure_ascii=False).encode())
        check(size<190000,'Request too large')
        reserves.append(((size+4096)*2.5+engine.client.MAX_OUTPUT*10)/1e6)
    check(sum(reserves)<3.0,'Reservations exceed fixed budget')
    write(ROOT/'RUNTIME.json',engine.execution._runtime_manifest(engine.execution._runtime(None)))
    write(ROOT/'GENERATION_FREEZE.json',{'frozen_utc':engine.client.utc(),'files':dependencies(),
        'reference_sha256':sha(engine.REFERENCE),'model_config':engine.client.CONFIGS[engine.CONFIG],
        'system':engine.client.SYSTEM,'max_output_tokens':engine.client.MAX_OUTPUT,'cap_usd':3.0,
        'schedule':schedule,'seeds':engine.SEEDS,'limits':engine.LIMITS,'max_calls':9,'max_tables':27,
        'conservative_schedule_reservation_usd':sum(reserves),'primary_comparison':'JOINT minus SUMMARY mean absolute residual-correlation reference difference',
        'primary':engine.PRIMARY,'diagnostics':engine.ENDPOINTS[3:],
        'reference_scope':'previously exposed case selected for developmental mechanism check; not independent replication',
        'source_admission':'prior Agent-found source; root-led extraction and information masking'})
    print(json.dumps({'frozen':True,'sha256':sha(ROOT/'GENERATION_FREEZE.json'),'reserved_usd':sum(reserves)}))

def verify():
    f=read(ROOT/'GENERATION_FREEZE.json')
    for path,h in f['files'].items():check(sha(PROJECT/path)==h,'Bound input changed: '+path)
    check(sha(engine.REFERENCE)==f['reference_sha256'],'Reference changed')
    check(f['model_config']==engine.client.CONFIGS[engine.CONFIG] and f['system']==engine.client.SYSTEM,'Model configuration changed')
    check(f['max_output_tokens']==engine.client.MAX_OUTPUT and f['cap_usd']==engine.client.CAPS['openai'],'Budget changed')
    check(f['seeds']==engine.SEEDS and f['limits']==engine.LIMITS,'Execution settings changed')
    check(len(f['schedule'])==9,'Wrong schedule')
    return f

engine.verify=verify

def analyze():
    verify();cc=read(ROOT/'CONSTRUCTION_CLOSURE.json');ec=read(ROOT/'EXECUTION_CLOSURE.json')
    check(cc['freeze_sha256']==sha(ROOT/'GENERATION_FREEZE.json') and ec['construction_sha256']==sha(ROOT/'CONSTRUCTION_CLOSURE.json'),'Closure changed')
    scheduled={r['id'] for r in read(ROOT/'inputs/schedule.json')}
    check(len(cc['rows'])==9 and {r['id'] for r in cc['rows']}==scheduled,'Construction inventory incomplete')
    expected={(r['id'],seed) for r in cc['rows'] if r['status']=='sealed' for seed in engine.SEEDS}
    actual={(r['id'],r['seed']) for r in ec['rows']}
    check(len(ec['rows'])==len(actual) and actual==expected,'Execution slots missing or duplicated')
    authors={r['id']:r for r in cc['rows']};ind=engine.load_review()
    records=[];details=[];failures=[];maxdiff=0.;count=0
    for a in cc['rows']:
        if a['status']!='sealed':failures.append({'id':a['id'],'stage':'construction','error':a.get('error')})
    for out in ec['rows']:
        folder=ROOT/'executions'/out['id']/str(out['seed'])
        check(sha(folder/'execution.json')==out['receipt_sha256'],'Execution receipt changed');r=read(folder/'execution.json')
        if r['status']!='success':failures.append({**out,'stage':'execution','error':r.get('error')});continue
        for name,h in read(folder/'input_bindings.json').items():check(sha(folder/'input'/name)==h,'Staged input changed')
        csv=folder/'output/generated.csv';check(sha(csv)==r['generated_sha256'],'Rows changed')
        data,_=ind.load_table(csv,engine.task());recalc=ind.independent_statistics(data,'PNS')
        vals=engine.endpoints(r['statistics']);check(set(vals)==set(engine.ENDPOINTS),'Endpoint inventory mismatch')
        for k,v in vals.items():
            other=recalc['values'][k]
            if v is None or other is None:check(v is None and other is None,'Missing-value mismatch')
            else:
                delta=abs(v-other);maxdiff=max(maxdiff,delta)
                check(np.isclose(v,other,atol=1e-9,rtol=1e-10),'Independent recomputation differs: '+k)
            count+=1;records.append({'id':out['id'],'arm':authors[out['id']]['arm'],'seed':out['seed'],'estimand':k,'value':v})
        details.append({**out,'statistics':r['statistics'],
            'nonpositive_counts':{k:int((data[k]<=0).sum()) for k in ['bmi','sbp','dbp']},'generated_sha256':sha(csv)})
    # Exposed aggregate is first parsed only after every construction/output closed.
    refs=read(engine.REFERENCE)['references']['PNS']
    for r in records:
        ref=refs[r['estimand']]['value'];r['reference']=ref
        r['absolute_reference_difference']=abs(r['value']-ref) if r['value'] is not None and ref is not None else None
    summary=[];arms=[]
    for a in cc['rows']:
        for k in engine.ENDPOINTS:
            rows=[r for r in records if r['id']==a['id'] and r['estimand']==k and r['value'] is not None]
            vv=[r['value'] for r in rows]
            summary.append({'id':a['id'],'arm':a['arm'],'estimand':k,'available_seeds':len(vv),
                'seed_mean':float(np.mean(vv)) if vv else None,'seed_min':min(vv) if vv else None,'seed_max':max(vv) if vv else None,
                'mean_absolute_reference_difference':float(np.mean([r['absolute_reference_difference'] for r in rows])) if vv else None})
    for a in ARMS:
        for k in engine.ENDPOINTS:
            rr=[r for r in summary if r['arm']==a and r['estimand']==k and r['available_seeds']]
            arms.append({'arm':a,'estimand':k,'planned_authors':3,'available_authors':len(rr),
                'author_mean':float(np.mean([r['seed_mean'] for r in rr])) if rr else None,
                'author_mean_absolute_reference_difference':float(np.mean([r['mean_absolute_reference_difference'] for r in rr])) if rr else None})
    dest=ROOT/'analysis';dest.mkdir(exist_ok=False)
    for name,obj in [('seed_results',records),('author_results',summary),('arm_results',arms),('details',details),('failures',failures)]:
        write(dest/(name+'.json'),obj)
        if obj and name not in ['details','failures']:pd.DataFrame(obj).to_csv(dest/(name+'.csv'),index=False)
    write(dest/'REFERENCE_USED.json',{'reference_sha256':sha(engine.REFERENCE),'PNS':refs,'scope':'exposed sample estimates; not known population truth'})
    write(dest/'INDEPENDENT_RECOMPUTATION.json',{'passed':True,'endpoint_comparisons':count,'maximum_absolute_difference':maxdiff,
        'method':'existing independent QR implementation versus production estimator; root-led new execution','extra_generator_runs':0})
    receipts=[read(p) for p in (ROOT/'calls').glob('*/receipt.json')]
    costs={'author_calls':len(receipts),'author_tariff_usd':sum(r.get('tariff_cost_usd') or 0 for r in receipts),
        'new_search_calls':0,'unknown_author_reservations_usd':sum(r['reserved_usd'] for r in receipts if r.get('tariff_cost_usd') is None),
        'requested_models':sorted({r['requested_model'] for r in receipts}),'returned_models':sorted({str(r.get('returned_model')) for r in receipts}),
        'author_usage':{k:sum((r.get('usage') or {}).get(k) or 0 for r in receipts) for k in ['input','output','cached','reasoning']},
        'invoice':False,'tariff':'TARIFF.json; stored tariff, not a newly verified invoice'}
    write(dest/'COSTS.json',costs)
    write(dest/'SLOT_ACCOUNTING.json',{'planned_constructors':9,'planned_tables':27,
        'closed_constructors':len(cc['rows']),'attempted_execution_slots':len(ec['rows']),
        'successful_tables':len(details),'unexecuted_due_to_failed_construction':27-len(expected),
        'failed_execution_slots':sum(r['status']!='success' for r in ec['rows']),
        'statistical_unit':'construction within one case; seeds nested, not independent clinical samples'})
    old=read(ROOT/'OLD_IMMUTABILITY.json');check(all(sha(OLD/r)==h for r,h in old.items()),'Closed old artifacts changed')
    write(dest/'OLD_INPUT_CHECK.json',{'passed':True,'old_files_unchanged':len(old)})
    print(json.dumps({'analysis_complete':True,'tables':len(details),'failures':len(failures),'max_recomputation_difference':maxdiff,'cost':costs,'arms':arms}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','preflight','freeze','run','analyze','verify'])
    action=parser.parse_args().action
    if action=='run':engine.run()
    else:globals()[action]()
