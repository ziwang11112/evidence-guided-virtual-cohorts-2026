"""Audit new editorial artifacts against closed aggregates; never read patient rows."""
from pathlib import Path
import csv,hashlib,json,math,re,zipfile
import numpy as np
import pandas as pd
import fitz

W=Path(__file__).resolve().parent
P=W.parents[1]
M=P/'manuscript'
B=M/'methods_draft_v32_2026-11-16'
checks=[]
sources=set()

def check(name,condition):
    checks.append({'check':name,'passed':bool(condition)})
    if not condition: raise AssertionError(name)
def eq(name,a,b):check(name,math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-12))
def read(rel):
    sources.add(rel)
    return json.loads((P/rel).read_text(encoding='utf8'))
def frame(rel):
    sources.add(rel)
    return pd.read_csv(P/rel)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

protected=read('work/manuscript_integration_v32_2026-11-16/INPUT_BINDINGS.json')['files']
for rel,digest in protected.items():check('protected '+rel,sha(P/rel)==digest)
l=frame('work/lifestyle_application_2026-11-11/ANALYSIS_CONTRASTS.csv')
l=l[l.stratum=='pooled']
c=frame('work/evidence_composition_pilot_2026-11-16/analysis/analyses.csv')
ca=frame('work/evidence_composition_pilot_2026-11-16/analysis/cell_summary.csv')
p=pd.DataFrame(read('work/pns_joint_evidence_2026-11-16/analysis/seed_results.json'))
pa=read('work/pns_joint_evidence_2026-11-16/analysis/arm_results.json')
ref=read('work/pns_joint_evidence_2026-11-16/analysis/REFERENCE_USED.json')['PNS']
plotted=pd.read_csv(W/'PLOTTED_VALUES.csv')
check('all 304 plotted rows retained',len(plotted)==304)
counts=plotted.figure.value_counts().to_dict()
check('expected complete figure denominators',counts=={'fig2-scientific-use':81,'fig3-evidence-composition':98,'fig4-joint-evidence':125})

for i,r in plotted.iterrows():
    if r.figure=='fig2-scientific-use':
        z=l[(l.trait==r.trait)&(l.contrast==r.contrast)]
        if r.kind=='constructor_mean':
            z=z[z.dataset_id.str.startswith('LIFESTYLE_'+r.dataset+'_')]
            check(f'lifestyle {i} three draws',len(z)==3)
            expected=sum(z.raw_estimate)/3
        else:
            z=z[z.dataset_id==r.dataset]
            check(f'lifestyle {i} unique source',len(z)==1)
            expected=z.iloc[0].raw_estimate
            if r.kind=='real_reference':
                eq(f'lifestyle CI lower {i}',r.lower,z.iloc[0].raw_lower)
                eq(f'lifestyle CI upper {i}',r.upper,z.iloc[0].raw_upper)
                eq(f'lifestyle sample count {i}',r.n,z.iloc[0]['n'])
    elif r.figure=='fig3-evidence-composition':
        endpoint='partial_xy_given_z' if r.task=='adjusted' else 'change_correlation'
        z=c[(c.family==r.task)&(c.condition==r.condition)&(c.estimand==endpoint)]
        if r.kind=='identified_reference':
            check(f'composition {i} reference only identified',r.condition=='combined' and z.identified.all())
            expected=(.5-.6*.6)/math.sqrt((1-.6**2)*(1-.6**2)) if r.task=='adjusted' else (.52*5-.8*4)
        else:
            z=z[z.id==r.dataset]
            if r.kind=='draw':z=z[z.seed==int(r.seed)]
            check(f'composition {i} expected nested count',len(z)==(1 if r.kind=='draw' else 3))
            expected=sum(z.value)/len(z)
    else:
        z=p[p.estimand==r.analysis]
        if r.kind=='real_reference':
            expected=ref[r.analysis]['value']
        else:
            z=z[z.id==r.dataset]
            if r.kind=='draw':z=z[z.seed==int(r.seed)]
            check(f'PNS {i} expected nested count',len(z)==(1 if r.kind=='draw' else 3))
            expected=sum(z.value)/len(z)
    eq(f'plotted aggregate {i}',r.x,expected)

# The paper's descriptive MAEs average draw discrepancies, not the absolute
# difference of an overall mean. All primary and dispersion outcomes are checked.
for r in pa:
    z=p[(p.arm==r['arm'])&(p.estimand==r['estimand'])]
    constructor_means=[sum(g.value)/len(g) for _,g in z.groupby('id')]
    constructor_errors=[sum(abs(g.value-g.reference))/len(g) for _,g in z.groupby('id')]
    eq('PNS condition mean '+r['arm']+r['estimand'],r['author_mean'],sum(constructor_means)/3)
    eq('PNS condition MAE '+r['arm']+r['estimand'],r['author_mean_absolute_reference_difference'],sum(constructor_errors)/3)

check('24 composition constructors',c.id.nunique()==24)
check('72 composition draws',len(c[['id','seed']].drop_duplicates())==72)
check('216 composition analyses',len(c)==216)
identified=c[c.identified]
check('90 identified estimates',len(identified)==90)
check('90 numerical tolerances',identified.identified_within_0_08.all())
check('738 source checks',ca.source_checks_total.sum()==738 and (ca.source_checks_passed==ca.source_checks_total).all())
check('72 correct functional labels',ca.identification_total.sum()==72 and (ca.identification_correct==ca.identification_total).all())

text=(M/'DRAFT_v0_32.md').read_text(encoding='utf8')
main,supp=text.split('## Supplementary results',1)
check('four figures',len(re.findall(r'^\*\*Figure \d+\.',text,re.M))==4)
check('three main tables',len(re.findall(r'^\*\*Table \d+\.',main,re.M))==3)
check('three supplement tables',len(re.findall(r'^\*\*Table S\d+\.',supp,re.M))==3)
check('all placeholders resolved','@@' not in text)
check('references 1 through 12',re.findall(r'^(\d+)\. ',main.split('## References')[1],re.M)==[str(x) for x in range(1,13)])

def table(number):
    section=text.split('**Table '+number+'.',1)[1]
    block=section[section.index('\n|')+1:].split('\n\n',1)[0]
    return [[x.strip() for x in line.strip('|').split('|')] for line in block.splitlines()[2:]]
t1=table('S1'); t2=table('S2');t3=table('S3')
check('all nine lifestyle rows',len(t1)==9)
for row in t1:
    label,realstr,a1,a2=row
    trait={'BMI':'bmi','Total cholesterol':'total_cholesterol','HDL':'hdl_cholesterol'}[label.split(':')[0]]
    contrast=label.split(': ')[1].replace(' − ','_minus_')
    z=l[(l.trait==trait)&(l.contrast==contrast)]
    rr=z[z.dataset_id=='real'].iloc[0]
    check('lifestyle displayed reference '+label,realstr==f'{rr.raw_estimate:.3f} [{rr.raw_lower:.3f}, {rr.raw_upper:.3f}]')
    for author,value in [('A1',a1),('A2',a2)]:
        check('lifestyle displayed mean '+label+author,value==f"{z[z.dataset_id.str.startswith('LIFESTYLE_'+author+'_')].raw_estimate.mean():.3f}")
check('all eight composition cells',len(t2)==8)
check('all five PNS endpoints',len(t3)==5)
for row,metric in zip(t3,['residual_correlation','bmi_sbp','bmi_dbp','sbp.sd_population','dbp.sd_population']):
    original=next(a for a in pa if a['arm']=='ORIGINAL' and a['estimand']==metric)
    added=next(a for a in pa if a['arm']=='AUGMENTED' and a['estimand']==metric)
    check('PNS formatted row '+metric,row[1:]==[f"{ref[metric]['value']:.4f}",f"{original['author_mean']:.4f}",f"{added['author_mean']:.4f}",f"{original['author_mean_absolute_reference_difference']:.5f} / {added['author_mean_absolute_reference_difference']:.5f}"])

log=(B/'paper.log').read_text(encoding='utf8',errors='replace')
issues=[line for line in log.splitlines() if re.search(r'overfull|missing character|undefined|warning',line,re.I) and not line.startswith('Package:')]
check('no layout/glyph/anchor warnings',not issues)
with fitz.open(B/'paper.pdf') as doc,fitz.open(B/'tmp/pdfs/standalone/paper.pdf') as standalone:
    check('standalone page count',len(doc)==len(standalone))
    for i in range(len(doc)):
        check('standalone identical text page '+str(i+1),doc[i].get_text()==standalone[i].get_text())
        mainlinks=sorted(x.get('uri','') for x in doc[i].get_links())
        zlinks=sorted(x.get('uri','') for x in standalone[i].get_links())
        check('standalone identical links page '+str(i+1),mainlinks==zlinks)
        words=doc[i].get_text('words')
        check('no out-of-page text page '+str(i+1),all(x[0]>=0 and x[1]>=0 and x[2]<=doc[i].rect.width+.1 and x[3]<=doc[i].rect.height+.1 for x in words))
    pages=len(doc)
    supp_start=next(i+1 for i,pag in enumerate(doc) if 'Supplementary results' in pag.get_text())
with zipfile.ZipFile(B/'overleaf_v32.zip') as z:
    names=z.namelist()
    check('archive contains only paper/readme/four figure PDFs',len(names)==6 and all(n in ['paper.tex','OVERLEAF_README.md'] or n.startswith('figures/') and n.endswith('.pdf') for n in names))
    check('archive has no traversal/absolute paths',all('..' not in n.split('/') and not n.startswith(('/','\\')) and ':' not in n for n in names))

result={'status':'passed','root_led_editorial_checks':len(checks),'patient_rows_read':False,'new_model_calls':0,
        'new_cohort_generation':0,'protected_input_files_unchanged':len(protected),'pages':pages,
        'supplement_starts_at_page':supp_start,'new_statistical_figures':3,'copied_overview':1,
        'plotted_values_verified':len(plotted),'main_tables':3,'supplement_tables':3,
        'standalone_zip_compiled':True,'standalone_text_and_links_match':True,'layout_warnings':issues,
        'scope':'Editorial and aggregate reconciliation only; no new scientific evaluation or independent personnel review.',
        'source_hashes':{rel:sha(P/rel) for rel in sorted(sources)},'checks':checks}
(W/'CONTENT_AUDIT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
(B/'BUILD_QA.json').write_text(json.dumps({k:v for k,v in result.items() if k not in ['checks','source_hashes']},indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','source_hashes']}))
