"""Verify exported aggregates, rounded PDF tables and allowed package contents."""
from pathlib import Path
import csv,hashlib,json,re,statistics,zipfile
import fitz

I=Path(__file__).resolve().parent;P=I.parents[1];L=P/'work/lifestyle_application_2026-11-11'
O=P/'deliverables/Biomedical_Use_Review_v31_2026-11-11';Z=O.with_suffix('.zip')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,ok):checks.append(name);assert ok,name
def readcsv(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
source=json.loads((L/'ANALYSIS_RESULTS.json').read_text())['results']
truth={(d['dataset_id'],x['trait'],x['contrast']):(x,d) for d in source for x in d['analysis']['contrasts'] if x['stratum']=='pooled'}
records=readcsv(O/'04_PRIMARY_ESTIMATES.csv')
check('63 complete additive comparisons',len(records)==len(truth)==63)
seen=set()
for row in records:
    key=tuple(row[x] for x in ['dataset_id','trait','contrast']); r,d=truth[key];seen.add(key)
    for key2 in ['raw_estimate','raw_lower','raw_upper','n']:
        check(str(key)+key2,float(row[key2])==r[key2])
    for key2 in ['estimate','lower','upper']:
        check(str(key)+'standardized_'+key2,float(row['standardized_'+key2])==r[key2])
    check(str(key)+'unit',row['raw_unit']==r['raw_unit'])
    check(str(key)+'author',row['author']==d.get('episode_id','REFERENCE'))
    check(str(key)+'seed',row['seed']==str(d.get('seed','')))
check('no duplicate or omitted analysis',seen==set(truth))
diag=readcsv(O/'05_SCALE_AND_BRANCHES.csv')
check('21 diagnostics',len(diag)==21)
for row in diag:
    d=next(x for x in source if x['dataset_id']==row['dataset_id'])['analysis']
    t=next(x for x in d['trait_status'] if x['trait']==row['trait'])
    l=next(x for x in d['interactions'] if x['trait']==row['trait'])
    check(str(row)+'sample',int(row['n'])==t['n'])
    check(str(row)+'SD',float(row['sample_sd'])==t['sample_sd'])
    check(str(row)+'LRT',float(row['interaction_p'])==l['p_value'])
    check(str(row)+'branch',row['sex_specific_branch']==str(l['selects_sex_specific']))
check('all sex-specific results preserved',sha(O/'optional/ALL_189_CONTRASTS.csv')==sha(L/'ANALYSIS_CONTRASTS.csv'))
check('189 rows in complete export',len(readcsv(O/'optional/ALL_189_CONTRASTS.csv'))==189)

pdf=fitz.open(O/'01_REVIEW_BRIEF.pdf');check('four pages',len(pdf)==4)
texts=[' '.join(x.get_text().split()) for x in pdf]
for i,p in enumerate(pdf):
    for block in p.get_text('dict')['blocks']:
        if block['type']==0:
            for line in block['lines']:
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    check(f'page{i+1} text inside page',x0>=40 and y0>=25 and x1<=572 and y1<=780)
    check(f'page{i+1} no replacement glyph','\ufffd' not in texts[i])
for t in ['bmi','total_cholesterol','hdl_cholesterol']:
    for c in ['rural_minus_pastoralist','urban_minus_pastoralist','urban_minus_rural']:
        r,_=truth[('real',t,c)]
        expected=f'{r["raw_estimate"]:.3f} [{r["raw_lower"]:.3f}, {r["raw_upper"]:.3f}]'
        check(f'PDF real table {t}/{c}',expected in texts[2])
        for ep in ['LIFESTYLE_A1','LIFESTYLE_A2']:
            v=[r['raw_estimate'] for (did,tt,cc),(r,d) in truth.items() if (tt,cc)==(t,c) and d.get('episode_id')==ep]
            expected=f'{statistics.mean(v):.3f} [{min(v):.3f}, {max(v):.3f}]'
            check(f'PDF generated table {t}/{c}/{ep}',expected in texts[2])
for token in ['1.882','1.700-2.251','0.02457','31.85-34.06','14.40-15.10','42.81','20.23']:
    check('key result '+token,token in texts[2])
for token in ['all nine','original paper was allowed input','no human biomedical verdict','not','confidence intervals','one generated table','not biological equivalence']:
    check('scope '+token,token in ' '.join(texts).lower())
pdf.close()

# Re-read selected scientific commitments rather than trusting the new prose.
a=json.loads((L/'episodes/LIFESTYLE_A1/candidates/v001/model_spec.json').read_text())
b=json.loads((L/'episodes/LIFESTYLE_A2/candidates/v001/model_spec.json').read_text())
check('A1 group HDL SD anchor',a['traits']['hdl']['group_marginal_sds']==[14.72]*3)
check('A2 residual HDL multipliers',b['hdl']['residual_sd_multipliers']==[1,1,1])
check('A2 female HDL origin value',b['hdl']['female_effect']==3.87)
check('BMI shared published anchor',a['traits']['bmi']['group_marginal_means'][0]==b['bmi']['group_means'][0]==19.99)
check('A2 TC assumptions match prose',b['tc']['group_means']==[148.58,150.08,163.58])
for rel,h in json.loads((I/'INPUT_BINDINGS.json').read_text())['hashes'].items():check('preserved '+rel,sha(P/rel)==h)

allowed={'00_START_HERE.txt','01_REVIEW_BRIEF.pdf','02_REVIEW_FORM.md','03_CONTEXT_AND_SOURCES.md','04_PRIMARY_ESTIMATES.csv','05_SCALE_AND_BRANCHES.csv','06_PARAMETER_ORIGINS.md','PACKAGE_MANIFEST.json',
         'optional/ALL_189_CONTRASTS.csv','optional/MANUSCRIPT_v0_31.pdf','optional/EARLIER_GLYCEMIA_LIPID_BRIEF.pdf','optional/EARLIER_CONTEXT_AND_SOURCES.md','optional/EARLIER_ANALYSIS_ESTIMATES.csv'}
actual={x.relative_to(O).as_posix() for x in O.rglob('*') if x.is_file()}
check('allowlist exactly',actual==allowed)
manifest=json.loads((O/'PACKAGE_MANIFEST.json').read_text())
for name,meta in manifest['files'].items():check('manifest '+name,sha(O/name)==meta['sha256'] and (O/name).stat().st_size==meta['bytes'])
with zipfile.ZipFile(Z) as z:
    check('zip exactly matches allowed artifacts',set(z.namelist())=={O.name+'/'+n for n in allowed})
    for n in allowed:check('zip bytes '+n,z.read(O.name+'/'+n)==(O/n).read_bytes())
for f in O.rglob('*'):
    if f.suffix in {'.md','.csv','.txt'}:
        txt=f.read_text(encoding='utf-8')
        check('no credential pattern '+f.name,not re.search(r'sk-[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9_.-]{15,}',txt))
form=(O/'02_REVIEW_FORM.md').read_text(encoding='utf-8')
check('blank human-response fields',form.count('Response: ___')==5 and form.count('| | |')==4)
report={'status':'PASS_ROOT_PACKET_AUDIT','checks':len(checks),'check_names':checks,'new_patient_fits':0,'new_api_calls':0,'raw_or_synthetic_rows_read':False,
        'scientific_review_scope':'Root-led consistency review against frozen sources and prior independent experiment audits; no new external human review',
        'pdf_sha256':sha(O/'01_REVIEW_BRIEF.pdf'),'zip_sha256':sha(Z)}
(I/'PACKET_QA.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','checks','new_api_calls']}))
