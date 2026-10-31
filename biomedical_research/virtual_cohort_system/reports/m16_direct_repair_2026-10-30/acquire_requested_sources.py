"""One-shot controller retrieval requested by builders; no target access or source admission."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,urllib.request,xml.etree.ElementTree as ET,zipfile,io

R=Path(__file__).resolve().parent
REQUESTS=[
 ('b1','PMC8516664','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8516664/fullTextXML','xml',1),
 ('b2','PMC4750804','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4750804/fullTextXML','xml',1),
 ('b3','PMC7803020_mmc2','https://pmc-oa-opendata.s3.amazonaws.com/PMC7803020.1/mmc2.docx?md5=44b15014a7915dc677f9322bc5edabf1','docx',0),
]
def write_new(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 for bid,sid,url,extension,webattempt in REQUESTS:
  d=R/'source_admission'/bid;d.mkdir(parents=True,exist_ok=True)
  rec={'builder':bid,'source':sid,'url':url,'created_utc':datetime.now(timezone.utc).isoformat(),
       'controller_xml_or_docx_attempts':1,'prior_controller_web_attempts':webattempt,
       'prior_controller_web_result':'recaptcha_no_article_content' if webattempt else 'not_attempted',
       'purpose':'Agent-requested independent source access; pending scientific admission',
       'target_outcomes_read':False}
  write_new(d/(sid+'_attempt.json'),rec)
  try:
   request=urllib.request.Request(url,headers={'User-Agent':'Academic-evidence-review/1.0'})
   with urllib.request.urlopen(request,timeout=30) as response:
    raw=response.read(16*1024*1024+1);finalurl=response.url;status=response.status
   if len(raw)>16*1024*1024:raise ValueError('Response byte cap exceeded')
   if finalurl!=url:raise ValueError('Unexpected redirect; retained as failed attempt')
   p=d/(sid+'.'+extension)
   with p.open('xb') as f:f.write(raw)
   if extension=='xml':
    root=ET.fromstring(raw)
    content='\n'.join(' '.join(e.itertext()) for e in root.iter() if e.tag in {'article-title','abstract','sec'})
   else:
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
     root=ET.fromstring(z.read('word/document.xml'))
     ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
     content='\n'.join(' | '.join(' '.join(c.itertext()) for c in row.findall('w:tc',ns)) for row in root.findall('.//w:tr',ns))
     content+='\nPARAGRAPHS\n'+'\n'.join(' '.join(p.itertext()) for p in root.findall('.//w:p',ns))
     images=[n for n in z.namelist() if n.startswith('word/media/')]
     if images:rec['embedded_images']=images
   with (d/(sid+'.txt')).open('x',encoding='utf-8') as f:f.write(content)
   rec.update(status='downloaded_pending_review',http_status=status,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  except Exception as error:rec.update(status='failed',error=type(error).__name__+': '+str(error))
  write_new(d/(sid+'_result.json'),rec)
  print(json.dumps(rec))
if __name__=='__main__':main()
