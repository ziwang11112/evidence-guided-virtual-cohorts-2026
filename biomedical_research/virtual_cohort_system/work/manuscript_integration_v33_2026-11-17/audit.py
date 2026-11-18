"""Editorial data reconciliation and deliverable QA. No frozen experiment is rerun."""
from pathlib import Path
import hashlib,json,math,re,zipfile
import pandas as pd
import fitz
W=Path(__file__).resolve().parent;P=W.parents[1];M=P/'manuscript';B=M/'methods_draft_v33_2026-11-17'
checks=[]
def check(label,ok):
 checks.append({'check':label,'passed':bool(ok)})
 if not ok:raise AssertionError(label)
def eq(label,a,b):check(label,math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-12))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
binding=json.loads((W/'INPUT_BINDINGS.json').read_text())['files']
changed=[r for r,h in binding.items() if sha(P/r)!=h]
check('closed inputs and old manuscript remain unchanged',not changed)
plots=pd.read_csv(W/'PLOTTED_VALUES.csv')
counts=plots.figure.value_counts().to_dict()
check('complete plotted denominators',counts=={'fig2-scientific-use':81,'fig3-evidence-composition':98,'figS1-search-followup':125,'fig4-pressure-content':197,'fig5-iron-content':197})
life=pd.read_csv(P/'work/lifestyle_application_2026-11-11/ANALYSIS_CONTRASTS.csv');life=life[life.stratum=='pooled']
comp=pd.read_csv(P/'work/evidence_composition_pilot_2026-11-16/analysis/analyses.csv')
old=pd.read_json(P/'work/pns_joint_evidence_2026-11-16/analysis/seed_results.json')
cases={case:pd.read_csv(P/f'work/{case}_evidence_content_control_2026-11-16/analysis/seed_results.csv') for case in ['pns','iron']}
for i,r in plots.iterrows():
 if r.figure=='fig2-scientific-use':
  z=life[(life.trait==r.trait)&(life.contrast==r.contrast)]
  if r.kind=='constructor_mean':z=z[z.dataset_id.str.startswith('LIFESTYLE_'+r.dataset+'_')]
  else:z=z[z.dataset_id==r.dataset]
  expected=z.raw_estimate.mean()
  if r.kind=='real_reference':
   eq(f'life lower {i}',r.lower,z.iloc[0].raw_lower);eq(f'life upper {i}',r.upper,z.iloc[0].raw_upper)
 elif r.figure=='fig3-evidence-composition':
  ep='partial_xy_given_z' if r.task=='adjusted' else 'change_correlation'
  z=comp[(comp.family==r.task)&(comp.condition==r.condition)&(comp.estimand==ep)]
  if r.kind=='identified_reference':
   check(f'identified reference {i}',r.condition=='combined' and z.identified.all());expected=.21875 if r.task=='adjusted' else -.6
  else:
   z=z[z.id==r.dataset]
   if r.kind=='draw':z=z[z.seed==int(r.seed)]
   expected=z.value.mean()
 elif r.figure=='figS1-search-followup':
  z=old[old.estimand==r.analysis]
  if r.kind=='real_reference':expected=z.reference.iloc[0]
  else:
   z=z[z.id==r.dataset]
   if r.kind=='draw':z=z[z.seed==int(r.seed)]
   expected=z.value.mean()
 else:
  case='pns' if r.figure=='fig4-pressure-content' else 'iron'
  z=cases[case];z=z[z.estimand==r.analysis]
  if r.kind=='reference':
   expected=z.reference.iloc[0]*r.multiplier
   if case=='iron' and pd.notna(r.lower):
    obj=json.loads((P/'work/iron_evidence_content_control_2026-11-16/analysis/REFERENCE_USED.json').read_text())
    lo,hi=obj['original_aggregate']['estimands'][r.analysis]['ci95']
    eq(f'reference lower {i}',r.lower,lo*r.multiplier);eq(f'reference upper {i}',r.upper,hi*r.multiplier)
  elif r.kind=='arm_discrepancy':
   z=z[z.arm==r.condition]
   expected=z.groupby('id').absolute_reference_difference.mean().mean()
  else:
   z=z[z.id==r.dataset]
   if r.kind=='draw':z=z[z.seed==int(r.seed)]
   expected=z.absolute_reference_difference.mean() if r.kind=='constructor_discrepancy' else z.value.mean()*r.multiplier
 eq(f'plotted value {i}',r.x,expected)

improvements={}
for case,dr in cases.items():
 ar=pd.read_csv(P/f'work/{case}_evidence_content_control_2026-11-16/analysis/arm_results.csv')
 check(f'{case} 9 constructions',dr.id.nunique()==9)
 check(f'{case} 27 draws',len(dr[['id','seed']].drop_duplicates())==27)
 for _,r in ar.iterrows():
  z=dr[(dr.arm==r.arm)&(dr.estimand==r.estimand)]
  check(f'{case} availability {r.arm} {r.estimand}',len(z)==9 and z.id.nunique()==3)
  eq(f'{case} mean {r.arm} {r.estimand}',r.author_mean,z.groupby('id').value.mean().mean())
  errs=(z.value.map(math.log)-z.reference.map(math.log)).abs() if case=='iron' and r.estimand=='odds_ratio' else (z.value-z.reference).abs()
  eq(f'{case} discrepancy {r.arm} {r.estimand}',r.author_mean_absolute_reference_difference,errs.groupby(z.id).mean().mean())
 primary='residual_correlation' if case=='pns' else 'odds_ratio'
 a=ar[ar.estimand==primary].set_index('arm').author_mean_absolute_reference_difference
 improvements[case]=100*(1-a.JOINT/a.SUMMARY)
 # Check the text's complete construction-level ordering, not just arm means.
 e=dr[dr.estimand==primary].groupby(['arm','id']).absolute_reference_difference.mean()
 check(f'{case} each joint author closer than every summary author',e['JOINT'].max()<e['SUMMARY'].min())

text=(M/'DRAFT_v0_33.md').read_text(encoding='utf8');main,supp=text.split('## Supplementary results',1)
for case in ['pns','iron']:check(f'{case} rounded gain in abstract',f'{improvements[case]:.1f}%' in main.split('## 1.')[0])
check('5 main figures',len(re.findall(r'^\*\*Figure \d+\.',main,re.M))==5)
check('1 support figure',len(re.findall(r'^\*\*Figure S\d+\.',supp,re.M))==1)
check('3 main tables',len(re.findall(r'^\*\*Table \d+\.',main,re.M))==3)
check('6 supplement tables',len(re.findall(r'^\*\*Table S\d+\.',supp,re.M))==6)
check('old 92.89 percent gain relegated to history','92.89%' not in main and '92.89%' in supp)
for phrase in ['Previously exposed','ordinary Agent','Gaussian copula','Student-t','no target individual','not a calibrated','worsens','withheld','one call each']:
 check('claim boundary '+phrase,phrase.lower() in text.lower())
check('complete identified composition results',len(comp[comp.identified])==90 and comp[comp.identified].identified_within_0_08.all())
check('24 controlled constructions',comp.id.nunique()==24)
with zipfile.ZipFile(B/'overleaf_v33.zip') as z:
 names=z.namelist()
 check('ZIP only tex readme and 6 figures',len(names)==8 and all(n=='paper.tex' or n=='OVERLEAF_README.md' or (n.startswith('figures/') and n.endswith('.pdf')) for n in names))
 for n in names:check('ZIP exact '+n,z.read(n)==(B/n).read_bytes())
with fitz.open(B/'paper.pdf') as pdf,fitz.open(B/'tmp/pdfs/standalone/paper.pdf') as independent:
 check('standalone same page count',len(pdf)==len(independent))
 for i,(a,b) in enumerate(zip(pdf,independent)):
  check(f'standalone same text page {i+1}',a.get_text()==b.get_text())
  check(f'no blank page {i+1}',len(a.get_text().strip())>200)
  check(f'no replacement glyph {i+1}','\ufffd' not in a.get_text())
 pages=len(pdf)
 check('metadata title',pdf.metadata['title']==text.splitlines()[0][2:])
for folder in [B,B/'tmp/pdfs/standalone']:
 log=(folder/'build-pass-2.txt').read_text(encoding='utf-8',errors='replace')
 check('no TeX overflow or missing glyph '+str(folder),not re.search(r'Overfull|Missing character|LaTeX Warning:|Undefined control sequence|! LaTeX Error',log))
result={'passed':all(x['passed'] for x in checks),'checks':len(checks),'protected_files':len(binding),'protected_changed':changed,
 'plotted_rows':len(plots),'figure_counts':counts,'relative_discrepancy_reductions_pct':improvements,'pages':pages,
 'new_api_calls':0,'new_patient_fits':0,'new_generated_cohorts':0,'standalone_compile':True,'checks_detail':checks}
(W/'CONTENT_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
(B/'BUILD_QA.json').write_text(json.dumps({k:v for k,v in result.items() if k!='checks_detail'},indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks_detail','figure_counts']}))
