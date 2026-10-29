"""Curator verifies DOCX table extraction against XML and public source metadata."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from datetime import datetime, timezone
import hashlib,json,shutil

E=Path(__file__).resolve().parent
R=E/'research';B=E/'agent_bundle'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))

doc=R/'Mikkelsen2023_Table_1.DOCX'
metadata=read(R/'PMC10308115.1.json')
assert metadata['doi']=='10.3389/fnut.2023.1158383'
assert metadata['version']==1 and not metadata['is_retracted']
uri=next(u for u in metadata['media_urls'] if 'Table_1.DOCX' in u)
assert hashlib.md5(doc.read_bytes()).hexdigest()==uri.split('md5=')[1]
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(doc) as z:
    root=ET.fromstring(z.read('word/document.xml'))
tables=[]
for table in root.findall('.//w:tbl',ns):
    rows=[]
    for row in table.findall('./w:tr',ns):
        cells=[]
        for cell in row.findall('./w:tc',ns):
            paras=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in cell.findall('./w:p',ns)]
            cells.append('\n'.join(paras))
        rows.append(cells)
    tables.append(rows)
assert tables==read(R/'Mikkelsen2023_supplement_tables.json'),'Extraction differs from source XML'
age_rows=[row for row in tables[0] if len(row)==5 and row[2].strip() in ['40-49','50-59','60-69','70-79','80 +']]
assert len(age_rows)==30
assert sum(row[4].strip()=='Reference' for row in age_rows)==2
registry=read(B/'registry.json');count=len(registry['artifacts'])
assert count==6,'Unexpected registry state'
admissions=[]
for name in ['Mikkelsen2023_Table_1.DOCX','Mikkelsen2023_supplement_tables.json','Mikkelsen2023_supplement_text.txt','PMC10308115.1.json']:
    src=R/name;dst=B/'sources'/name
    assert not dst.exists()
    shutil.copyfile(src,dst)
    item={'source_id':'Mikkelsen2023_Tromso7','path':'sources/'+name,'sha256':sha(dst),
          'origin':'curator','screening':'approved'}
    registry['artifacts'].append(item);admissions.append(item)
(B/'registry.json').write_text(json.dumps(registry,indent=2)+'\n',encoding='utf-8')
receipt={'created_utc':datetime.now(timezone.utc).isoformat(),
    'source_doi':metadata['doi'],'source_metadata_sha256':sha(R/'PMC10308115.1.json'),
    'source_service_uri':uri,'docx_sha256':sha(doc),'md5_matches_official_metadata':True,
    'independent_xml_extraction_exact_match':True,'joint_cells':30,'nonreference_estimates_with_CIs':28,
    'previous_registry_entries':count,'admitted':admissions,
    'scientific_scope':'Exact sex-specific age/BMI adjusted back-transformed log-TG coefficients. '
        'Relative effects, not arithmetic means or jointly independent evidence. CI covariance absent. '
        'Norwegian nonfasting study distinct from NHANES. Transport to fasting US and integration over '
        'unobserved adjustment variables remain assumptions. Main-text male count discrepancy is retained.',
    'target_outcomes_accessed':False}
with (E/'supplement_admission.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
print(json.dumps({'status':'admitted','artifacts':len(admissions),'joint_cells':30,'sha256':sha(doc)}))
