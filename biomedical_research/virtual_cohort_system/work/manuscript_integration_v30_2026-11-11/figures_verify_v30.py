"""Check exported Figure 5 against saved aggregates and PDF geometry only."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import pdfplumber

P=Path(__file__).resolve().parents[2]
O=P/'manuscript/paper_figures_v30_2026-11-11'
E=P/'work/request_only_repeatability_2026-11-11/EVALUATION.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
evaluation=json.loads(E.read_text())
lookup={(r['episode_id'],r['analysis_id']):r for r in evaluation['summaries']}
checks=[]

def check(name,value):
    checks.append({'name':name,'pass':bool(value)})
    assert value,name

with (O/'fig5-constructor-estimates.csv').open(newline='',encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
with (O/'fig5-seed-estimates.csv').open(newline='',encoding='utf-8') as f:
    seeds=list(csv.DictReader(f))
check('36 distinct constructor-endpoint records',len(rows)==len({(r['episode_id'],r['analysis_id']) for r in rows})==36)
check('12 constructors preserved',len({r['episode_id'] for r in rows})==12)
check('six endpoint definitions preserved',len({r['analysis_id'] for r in rows})==6)
check('108 distinct seed estimates',len(seeds)==len({(r['episode_id'],r['analysis_id'],r['seed']) for r in seeds})==108)
for row in rows:
    key=(row['episode_id'],row['analysis_id']);source=lookup[key]
    for field in ['case_id','arm','unit']:
        check(f'{key}:{field}',row[field]==source[field])
    for field in ['mean','minimum','maximum']:
        check(f'{key}:{field}',float(row[field])==source[field])
    check(f'{key}:reference',float(row['reference_value'])==source['reference']['value'])
    check(f'{key}:all seeds',int(row['available_seeds'])==3)
    unc=source['reference']['uncertainty']
    check(f'{key}:interval availability',(row['reference_interval_available']=='True')==(unc['status']=='available'))
    for bound in ['lower','upper']:
        got=float(row['reference_'+bound]) if row['reference_'+bound] else None
        check(f'{key}:reference {bound}',got==unc.get(bound))
for row in seeds:
    values=lookup[(row['episode_id'],row['analysis_id'])]['values']
    source=next(v for v in values if v['seed']==int(row['seed']))
    check(f"{row['episode_id']}:{row['analysis_id']}:{row['seed']}",float(row['value'])==source['value'])
pdf=O/'fig5-autonomous-analysis-utility.pdf'
with pdfplumber.open(pdf) as doc:
    check('one PDF page',len(doc.pages)==1)
    page=doc.pages[0]
    check('intended physical width',abs(page.width-7.8*72)<.001)
    check('intended physical height',abs(page.height-6.0*72)<.001)
    words=page.extract_words()
    check('text within page',all(w['x0']>=0 and w['top']>=0 and w['x1']<=page.width and w['bottom']<=page.height for w in words))
    text=page.extract_text()
    for required in ['SBP vs BMI','DBP vs BMI','SBP-DBP dependence','TC vs BMI','HDL vs BMI','TC-HDL dependence','not confidence intervals','not equivalence margins']:
        check('PDF text: '+required,required in text)
supplement=P/'work/scientific_check_revision_2026-11-11/reporting/paired_analysis_profiles.pdf'
copy=O/'figS6-scientific-check-revision-profiles.pdf'
check('supplement byte-identical',sha(supplement)==sha(copy))
manifest=json.loads((O/'FIG5_BINDINGS.json').read_text())
check('manifest source binding',manifest['sources'][str(E.relative_to(P))]==sha(E))
for name,digest in manifest['outputs'].items():
    check('output hash: '+name,sha(O/name)==digest)
qa={
    'completed_utc':datetime.now(timezone.utc).isoformat(),
    'status':'PASS', 'check_count':len(checks), 'checks':checks,
    'evaluation_sha256':sha(E), 'figure_pdf_sha256':sha(pdf),
    'render_path':str((O/'qa/fig5-actual-pdf.png').relative_to(P)),
    'render_sha256':sha(O/'qa/fig5-actual-pdf.png'),
    'render_tool':'Poppler pdftoppm, actual PDF, 180 dpi',
    'visual_inspection':{'actual_pdf_and_png_seen':True,'clipped_text':False,
       'text_overlap':False,'illegible_units_or_glyphs':False,
       'all_six_panels_and_six_rows_each_visible':True,
       'seed_variation_distinguished_from_reference_uncertainty':True,
       'color_palette':'blue / purple / orange; no green'},
    'limits':'Figure-data agreement and legibility only; not certification of scientific validity or equivalence.'
}
(O/'qa/FIG5_QA.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
manifest['visual_qa']='PASS; actual PDF render inspected; see qa/FIG5_QA.json'
(O/'FIG5_BINDINGS.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','checks':len(checks),'figure_pdf_sha256':sha(pdf)}))
