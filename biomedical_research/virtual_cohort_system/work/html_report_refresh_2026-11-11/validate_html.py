"""File-only checks. No browser, rendering, network or scientific execution."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse,unquote
from collections import Counter
import base64,hashlib,json,subprocess,xml.etree.ElementTree as ET
W=Path(__file__).resolve().parent;P=W.parents[1];page=P/'docs/research-report.html'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser');checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail})
check('no unresolved placeholders','@@' not in str(s))
ids=[x['id'] for x in s.select('[id]')];check('unique DOM ids',len(ids)==len(set(ids)))
check('current old entry matches',sha(page)==sha(P/'docs/research-explainer-2026-11-04.html'))
for a in s.select('a[href]'):
 href=a['href'];u=urlparse(href)
 if not u.scheme:
  if not u.path:check('anchor '+href,u.fragment in ids)
  else:check('local path '+href,(page.parent/unquote(u.path)).is_file())
for i,img in enumerate(s.select('img')):
 check('image alt '+str(i),bool(img.get('alt')))
 uri=img['src'];check('image embedded '+str(i),uri.startswith('data:image/svg+xml;base64,'))
 svg=base64.b64decode(uri.split(',',1)[1]);root=ET.fromstring(svg)
 check('valid SVG '+str(i),root.tag.endswith('svg'))
 check('no SVG script '+str(i),not any(e.tag.endswith('script') for e in root.iter()))
tabs=s.select('[role=tab]');panels=s.select('[role=tabpanel]')
check('four result panels',len(tabs)==len(panels)==4)
for t in tabs:
 p=s.find(id=t['aria-controls']);check('matching panel '+t['id'],p and p.get('aria-labelledby')==t['id'])
check('one active initial tab',sum(t.get('aria-selected')=='true' for t in tabs)==1)
check('one visible initial panel',sum(not p.has_attr('hidden') for p in panels)==1)
payload=json.loads(s.find(id='report-data').get_text())
audit=json.loads((P/'work/scientific_use_review_v30_2026-11-11/NUMERICAL_USE_AUDIT.json').read_text())
bp=json.loads((W/'BP_PLOT_DATA.json').read_text())
main=json.loads((P/'work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json').read_text())
check('all audited glycemia/lipid records exact',payload['glycemia_and_lipid']==audit['summary_records'])
check('all BP records exact',payload['blood_pressure']==bp['summary_records'])
check('six evidence contrasts exact',payload['information_contrasts']==main['agent_information_contrasts'])
for rel,h in audit['input_hashes'].items():check('frozen input '+rel,sha(P/rel)==h)
check('no third-party script',[x.get('src') for x in s.select('script[src]')]==[])
js='\n'.join(x.get_text() for x in s.select('script') if x.get('type')!='application/json')
(W/'report_interaction.js').write_text(js,encoding='utf-8')
r=subprocess.run(['node','--check',str(W/'report_interaction.js')],capture_output=True,text=True)
check('JavaScript syntax',r.returncode==0,r.stderr or None)
fixtures={'tabs':[dict(x.attrs) for x in tabs],'panels':[dict(x.attrs) for x in panels]}
(W/'dom_fixtures.json').write_text(json.dumps(fixtures),encoding='utf-8')
out={'status':'pass' if all(c['pass'] for c in checks) else 'fail','html_sha256':sha(page),'checks':checks,'check_count':len(checks),'browser_preview':'Not performed: Chrome plugin rejects file:// URLs. No alternate browser, localhost or raw-CDP workaround used.','scope':'Static HTML/data/link/image-XML/JavaScript-syntax checks; not rendered-page or clinical validation.'}
(W/'STATIC_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':out['status'],'checks':len(checks),'failures':[c for c in checks if not c['pass']]},ensure_ascii=False,indent=2))
assert out['status']=='pass'
