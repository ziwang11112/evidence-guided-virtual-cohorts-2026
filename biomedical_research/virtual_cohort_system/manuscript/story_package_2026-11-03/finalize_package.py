"""Finalize display provenance and portable links, without scientific execution."""
from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
PUBLIC='https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/blob/26ccdfb5a77c665ddce1d1c0c73ce991b7107fb3/biomedical_research/virtual_cohort_system/reports/'
new_docs=[P/'manuscript/CONTRIBUTION_EVIDENCE_MAP_2026-11-03.md',HERE/'README.md',P/'manuscript/CORE_CONTRIBUTION_POSITIONING_2026-11-03.md',P/'manuscript/JOURNAL_FIT_2026-11-03.md',P/'manuscript/STORY_AND_FIGURE_AUDIT_2026-11-03.md']
for p in new_docs:
 s=p.read_bytes().decode('utf-8')
 s=re.sub(r'\((?:\.\./)+work/([^)]*)\)',lambda m:'('+PUBLIC+m[1]+')',s)
 p.write_bytes(s.encode('utf-8'))

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((HERE/'DISPLAY_PROVENANCE.json').read_text(encoding='utf-8'))
receipt['code_sha256']=sha(HERE/'build_displays.py')
receipt['outputs']={str(f.relative_to(HERE)).replace('\\','/'):sha(f) for f in sorted([*(HERE/'figures').glob('*'),*(HERE/'tables').glob('*')]) if f.is_file()}
receipt['new_scientific_executions']=0
receipt['source_repair']='Native draw.io XML repair pass applied; parsed geometry and unique cell identifiers checked.'
receipt['visual_review']='Root inspected final Figure 1 PNG and final Figure 2 PNG at full resolution; readable labels, all panels, no clipping or legend overlap. Independent package review is separate.'
receipt['post_render_code_change']='Only public reports-directory fallback added after final redraw; plotting calculations and native diagram are unchanged.'
root=ET.parse(HERE/'figures/figure1-evidence-to-analysis.drawio').getroot()
cells=root.findall('.//mxCell');ids=[c.get('id') for c in cells]
assert len(ids)==len(set(ids))
assert all(c.find('mxGeometry') is not None for c in cells if c.get('edge')=='1')
assert len(receipt['outputs'])==9
(HERE/'DISPLAY_PROVENANCE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'outputs':len(receipt['outputs']),'scientific_executions':0,'code_sha256':receipt['code_sha256']}))
