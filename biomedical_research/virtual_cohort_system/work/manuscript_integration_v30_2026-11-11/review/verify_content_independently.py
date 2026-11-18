"""Independent aggregate-to-manuscript and SVG binding checks; no row data or execution."""
from pathlib import Path
import csv, hashlib, json, math, re, statistics, xml.etree.ElementTree as ET
from datetime import datetime, timezone
import fitz

P = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
F = P/'manuscript/paper_figures_v30_2026-11-11'
R = P/'work/request_only_repeatability_2026-11-11'
S = P/'work/scientific_check_revision_2026-11-11'
C = P/'work/request_only_agent_capacity_2026-11-10'
checks = []
def check(label, truth, details=None):
    checks.append({'check': label, 'pass': bool(truth), 'details':details})
def eq(label, a, b, tol=1e-11):
    check(label, a == b if a is None or b is None else math.isclose(float(a),float(b),abs_tol=tol,rel_tol=0), {'actual':a,'expected':b})
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p): return list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))

e,s,c = read(R/'EVALUATION.json'), read(S/'EVALUATION.json'), read(C/'EVALUATION.json')
plan,b = read(R/'PLAN.json'), read(F/'FIG5_BINDINGS.json')
draft = (P/'manuscript/DRAFT_v0_30.md').read_text(encoding='utf-8')
ref = read(P/'work/cross_model_api_pilot_2026-11-10/_host_only/REFERENCE_SNAPSHOT.json')['references']
summ = {(r['episode_id'],r['analysis_id']):r for r in e['summaries']}
ssum = {(r['episode_id'],r['analysis_id']):r for r in s['summaries']}
primary = ['bmi_sbp','bmi_dbp','residual_correlation','K02-TC-BMI','K02-HDL-BMI','K02-LIPID-RESIDUAL']
bycsv,seedcsv=rows(F/'fig5-constructor-estimates.csv'),rows(F/'fig5-seed-estimates.csv')
check('36 means; 108 seed estimates',len(bycsv)==36 and len(seedcsv)==108)
check('all twelve assigned laws', {r['episode_id'] for r in bycsv}=={r['episode_id'] for r in plan['episodes']})
check('all six primary endpoints',set(r['analysis_id'] for r in bycsv)==set(primary))
for rel,h in {**b['sources']}.items(): check('figure source hash '+rel,sha(P/rel)==h)
for name,h in b['outputs'].items(): check('figure output hash '+name,sha(F/name)==h)
for r in bycsv:
    ident=(r['episode_id'],r['analysis_id']); expected=summ[ident]
    values=[v['value'] for v in expected['values']]
    for key,want in [('mean',statistics.mean(values)),('minimum',min(values)),('maximum',max(values)),('available_seeds',3)]:
        eq(str(ident)+' '+key,float(r[key]),want)
    rr=expected['reference']; eq(str(ident)+' reference',float(r['reference_value']),rr['value'])
    check(str(ident)+' pinned reference record',rr==ref[expected['case_id']][r['analysis_id']])
    for field in ['lower','upper']:
        got=float(r['reference_'+field]) if r['reference_'+field] else None
        eq(str(ident)+' reference '+field,got,rr['uncertainty'].get(field))
    check(str(ident)+' metadata',r['case_id']==expected['case_id'] and r['arm']==expected['arm'] and r['unit']==expected['unit'])
for r in seedcsv:
    expected=summ[(r['episode_id'],r['analysis_id'])]
    v=next(x for x in expected['values'] if x['seed']==int(r['seed']))
    eq(str((r['episode_id'],r['analysis_id'],r['seed']))+' seedvalue',float(r['value']),v['value'])

# Read plot coordinates back from the saved SVG using visible tick positions,
# independent of renderer values/xlim declarations. A one-micro-point rounding
# tolerance is propagated through the tick-derived affine transform.
ns={'s':'http://www.w3.org/2000/svg'}
xml=ET.parse(F/'fig5-autonomous-analysis-utility.svg').getroot()
for panel,aid in enumerate(primary,1):
    ax=xml.find(".//s:g[@id='axes_%d']"%panel,ns)
    xticks=[g for g in ax.findall('.//s:g',ns) if g.attrib.get('id','').startswith('xtick_')]
    ticks=[]
    for g in xticks:
        t=g.find('.//s:text',ns)
        if t is not None: ticks.append((float(t.attrib['x']),float(''.join(t.itertext()).replace('−','-'))))
    (x1,v1),(x2,v2)=ticks[:2]; slope=(v2-v1)/(x2-x1)
    inv=lambda x:v1+(x-x1)*slope
    tol=abs(slope)*3e-6
    case='PNS' if panel<=3 else 'lipids'
    expected=sorted([r for r in e['summaries'] if r['case_id']==case and r['analysis_id']==aid],key=lambda r:(r['arm']!='ordinary',int(r['episode_id'].rsplit('_R',1)[1])))
    colls=[g for g in ax.findall('s:g',ns) if g.attrib.get('id','').startswith('PathCollection_')]
    check('panel %d marker sets'%panel,len(colls)==12)
    for n,r in enumerate(expected):
        for offset,vals in [(0,[v['value'] for v in r['values']]),(1,[r['mean']])]:
            # SVG painter order groups all z=4 seed sets before all z=5 means.
            marks=[x for x in colls[n+6*offset].findall('.//s:use',ns) if 'x' in x.attrib]
            check('panel%d %s marker count'%(panel,r['episode_id']),len(marks)==len(vals))
            for k,(mark,value) in enumerate(zip(marks,vals)):
                eq('panel%d %s mark%d.%d'%(panel,r['episode_id'],offset,k),inv(float(mark.attrib['x'])),value,tol)
    colored=[];orange=[]
    for path in ax.findall('s:g/s:path',ns):
        style=path.attrib.get('style',''); nums=[float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:e[-+]?\d+)?',path.attrib.get('d',''))]
        if 'stroke: #c27732' in style: orange.append(nums)
        if 'stroke: #2e69a1' in style or 'stroke: #8062a8' in style: colored.append(nums)
    check('panel%d all six ranges'%panel,len(colored)==6)
    for seg,r in zip(colored,expected):
        eq('panel%d %s range min'%(panel,r['episode_id']),inv(seg[0]),r['minimum'],tol)
        eq('panel%d %s range max'%(panel,r['episode_id']),inv(seg[2]),r['maximum'],tol)
    eq('panel%d reference line'%panel,inv(orange[0][0]),ref[case][aid]['value'],tol)
    shades=[path for path in ax.findall('s:g/s:path',ns) if 'fill: #c27732' in path.attrib.get('style','')]
    unc=ref[case][aid]['uncertainty']
    check('panel%d band availability'%panel,len(shades)==int(unc['status']=='available'))
    if shades:
        nums=[float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:e[-+]?\d+)?',shades[0].attrib['d'])]
        eq('panel%d band lower'%panel,inv(nums[0]),unc['lower'],tol)
        eq('panel%d band upper'%panel,inv(nums[2]),unc['upper'],tol)

def table(n):
    tail=draft.split('**Table '+n+'.',1)[1]
    out=[];started=False
    for line in tail.splitlines():
        if line.startswith('|'): started=True;out.append([x.strip() for x in line.strip('|').split('|')])
        elif started:break
    return {row[0]:row[1:] for row in out[2:]}

# Exact rounding against all new diagnostic table entries, not selected examples.
for tid,case,ids in [('S18','PNS',['bmi_sbp','bmi_dbp','residual_correlation','sbp.sd_population','dbp.sd_population','sbp_below_dbp_fraction']),('S19','lipids',['K02-TC-BMI','K02-HDL-BMI','K02-LIPID-RESIDUAL','total_cholesterol.sd_sample','hdl_cholesterol.sd_sample','hdl_above_total_fraction'])]:
    t=table(tid)
    for name,cells in t.items():
        for aid,cell in zip(ids,cells):
            value=ref[case][aid]['value'] if name=='Existing sample reference' else summ[(name,aid)]['mean']
            check(tid+' '+name+' '+aid,cell==('unavailable' if value is None else f'{value:.4f}'),{'printed':cell,'expected':value})

labels=['BMI-SBP slope','BMI-DBP slope','SBP-DBP residual correlation','BMI-TC slope','BMI-HDL slope','TC-HDL residual correlation']
for label,aid in zip(labels,primary):
    cells=table('5')[label]
    for j,arm in enumerate(['ordinary','workflow']):
        vals=[r['mean'] for r in e['summaries'] if r['analysis_id']==aid and r['arm']==arm]
        sep=' to ' if min(vals)<0 else '-'
        check('Table5 '+label+' '+arm,cells[j]==f'{min(vals):.3f}{sep}{max(vals):.3f}')
    rr=next(r['reference']['value'] for r in e['summaries'] if r['analysis_id']==aid)
    check('Table5 '+label+' reference',cells[2]==f'{rr:.3f}')

cap={r['analysis_id']:{x['arm']:x for x in c['summaries'] if x['analysis_id']==r['analysis_id']} for r in c['summaries']}
for label,aid in zip(labels,primary):
    vals=[cap[aid][a]['mean'] for a in ['ordinary','workflow']]+[cap[aid]['ordinary']['reference']['value']]
    for j,v in enumerate(vals):check('TableS17 '+label+' col'+str(j),table('S17')[label][j]==f'{v:.3f}')
check('DBP SD correction S16',table('S16')['DBP population SD, mmHg'][2]=='11.094')
check('no stale 10.757', '10.757' not in draft)

r04names=['BMI-TC, mg/dL per 5 kg/m²','BMI-HDL, mg/dL per 5 kg/m²','TC-HDL residual correlation','TC sample SD, mg/dL','HDL sample SD, mg/dL']
r04ids=['K02-TC-BMI','K02-HDL-BMI','K02-LIPID-RESIDUAL','total_cholesterol.sd_sample','hdl_cholesterol.sd_sample']
for label,aid in zip(r04names,r04ids):
    vals=[summ[('LIPID_BASE_R2',aid)]['mean'],ssum[('R04_GENERIC',aid)]['mean'],ssum[('R04_STRUCTURED',aid)]['mean'],ref['lipids'][aid]['value']]
    digits=5 if aid=='K02-LIPID-RESIDUAL' else 3
    for j,v in enumerate(vals):check('TableS20 '+label+' col'+str(j),table('S20')[label][j]==f'{v:.{digits}f}')

lineage={'R01':'PNS_BASE_R1','R02':'LIPID_BASE_R1','R03':'PNS_BASE_R2','R04':'LIPID_BASE_R2','R05':'PNS_BASE_R3','R06':'LIPID_BASE_R3','R07':'PNS_WORKFLOW_R1','R08':'LIPID_WORKFLOW_R1','R09':'PNS_WORKFLOW_R2','R10':'LIPID_WORKFLOW_R2','R11':'PNS_WORKFLOW_R3','R12':'LIPID_WORKFLOW_R3'}
initial_slots={(r['episode_id'],r['seed']):r for r in e['slots']}
equal=[]
for row in s['slots']:
    same=row['generated_sha256']==initial_slots[(lineage[row['episode_id'].split('_')[0]],row['seed'])]['generated_sha256']
    equal.append(same)
    check('saved hash equality '+row['episode_id']+' '+str(row['seed']),same == (not row['episode_id'].startswith('R04_')))
check('66/72 unchanged',sum(equal)==66 and len(equal)==72)
check('20 retained; four revisions',sum(x['selected_candidate']=='v000' for x in s['episodes'])==20 and {x['episode_id'] for x in s['episodes'] if x['selected_candidate']=='v001'}=={'R04_GENERIC','R04_STRUCTURED','R07_GENERIC','R07_STRUCTURED'})
for label,d,wantn,wantt,wantcalls,wantcost in [('repeatability',e,12,36,331,3.9851613),('review',s,24,72,343,4.8731316)]:
    check(label+' counts',d['counts']['episodes']==wantn and d['counts']['successful_tables']==wantt and d['counts']['model_calls']==wantcalls)
    eq(label+' accounted cost',d['costs']['accounted_usd'],wantcost)
    check(label+' unknown usage',sum(x['unknown_usage_calls'] for x in d['episodes'])==0)

for case in ['PNS','lipids']:
    for aid in sorted({r['analysis_id'] for r in e['summaries'] if r['case_id']==case and r['reference']['value'] is not None}):
        errors={a:statistics.mean(r['mean_absolute_reference_difference'] for r in e['summaries'] if r['case_id']==case and r['analysis_id']==aid and r['arm']==a) for a in ['ordinary','workflow']}
        check('descriptive arm comparison '+case+' '+aid,True,errors)

for phrase in ['24 dependent review sessions','not confidence intervals','PNS_BASE_R3 also samples shared parameters','previously exposed','not a cross-unit score','Neither policy consistently dominated','without attributing the earlier delivery improvement to a single component','Tanzania/Uganda','lacks a deterministic runtime bound','not an observed violation-rate reduction']:
    check('interpretation '+phrase,phrase in draft)

with fitz.open(F/'fig5-autonomous-analysis-utility.pdf') as pdf:
    check('figure PDF one page',len(pdf)==1)
    pdf[0].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(HERE/'FIG5_REVIEW_ACTUAL_PDF.png')
    text=pdf[0].get_text()
    for phrase in ['Blood pressure','Blood lipids','Ordinary Agent','Workflow','not confidence intervals','not equivalence margins']:
        check('PDF text '+phrase,phrase in text)

paths=[P/'manuscript/DRAFT_v0_30.md',F/'fig5-autonomous-analysis-utility.pdf',F/'fig5-autonomous-analysis-utility.svg',F/'fig5-caption.md',F/'fig5-constructor-estimates.csv',F/'fig5-seed-estimates.csv',F/'FIG5_BINDINGS.json',R/'EVALUATION.json',R/'PLAN.json',S/'EVALUATION.json',C/'EVALUATION.json',S/'review/CODE_SOURCE_CHANGE_AUDIT.json',S/'review/INDEPENDENT_NUMERICAL_REVIEW.json']
result={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'pass' if all(x['pass'] for x in checks) else 'fail','check_count':len(checks),'checks':checks,'issues':[x for x in checks if not x['pass']],'reviewed_files':{str(x.relative_to(P)):sha(x) for x in paths},'scope':'Independent manuscript/figure binding to saved aggregate evidence and prior frozen source/numerical audit. No generated/patient rows, API calls, generator reruns or clinical refits. SVG coordinates recovered from visible ticks. Visual assessment recorded separately.'}
(HERE/'FIGURE_AND_CONTENT_NUMERIC_REVIEW.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'checks':len(checks),'issues':result['issues']},ensure_ascii=False))
