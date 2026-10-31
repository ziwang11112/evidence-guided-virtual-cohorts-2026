"""Register only controller-reviewed requested originals/supplements; append-only registry."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def main():
 for bid,sid,files,reason in [
  ('b1','PMC8516664',[], 'No content admitted: browser recaptcha and EuropePMC HTTP500; prior gateway alias rejection retained.'),
  ('b2','PMC4750804',['PMC4750804.xml','PMC4750804.txt'],
   'Original recruits Korea Association of Health Promotion2005-2009, linked HIRA history, analyzed45098 adults; excludes relevant medications. NHANES appears in cited background, not original recruitment. Entire source exposed, incidental NHANES numeric findings cannot constrain generation. No adjustment/transport equivalence inferred.'),
  ('b3','PMC7803020',['PMC7803020_mmc2.docx','PMC7803020_mmc2.txt'],
   'Exact mmc2.docx supplement link listed in the builder gateway manifest for independent Gunma health-check original. DOCX parsed and full table/paragraph content inspected, no embedded media. Age/sex summary table supplies marginal statistics, not an adjusted urate-age coefficient; source labels and units preserved.')]:
  b=R/'visible'/bid/'bundle';regpath=b/'registry.json';reg=read(regpath);prior=sha(regpath)
  admitted=[]
  if bid=='b3':
   state_text=(b/'gateway/session/state.json').read_text()
   assert '5e64ee2798fcbc01d444c875' in state_text and 'mmc2.docx?md5=44b15014a7915dc677f9322bc5edabf1' in state_text
  for name in files:
   src=R/'source_admission'/bid/name;relative='sources/controller/'+name;dest=b/relative
   dest.parent.mkdir(parents=True,exist_ok=True)
   if dest.exists():raise ValueError('Already admitted')
   shutil.copyfile(src,dest)
   a={'source_id':sid,'path':relative,'sha256':sha(dest),'origin':'curator','screening':'approved'}
   assert a not in reg['artifacts'];reg['artifacts'].append(a);admitted.append(a)
  if files:
   regpath.write_text(json.dumps(reg,indent=2)+'\n',encoding='utf-8')
  result=read(R/'source_admission'/bid/((sid if bid!='b3' else 'PMC7803020_mmc2')+'_result.json'))
  receipt={'builder':bid,'source':sid,'created_utc':datetime.now(timezone.utc).isoformat(),
           'review_reason':reason,'admitted_artifacts':admitted,'prior_registry_sha256':prior,
           'new_registry_sha256':sha(regpath),'acquisition_record':result,
           'controller_acquisition_charges':2 if bid!='b3' else 1,
           'gateway_acquisitions_at_request':1,'cumulative_acquisitions_at_review':3 if bid!='b3' else 2,
           'total_acquisition_cap':4,'remaining_acquisitions':1 if bid!='b3' else 2,
           'budget_rule':'Controller charges share the original cap; gateway configuration is immutable and does not auto-deduct these manual charges. Builder/controller must enforce cumulative ledger.',
           'target_outcomes_read':False}
  new(R/'visible'/bid/'research/controller_source_admission.json',receipt)
  new(R/'source_admission'/bid/'ADMISSION_REVIEW.json',receipt)
  print(json.dumps({'builder':bid,'admitted_artifacts':len(admitted),'remaining_acquisitions':receipt['remaining_acquisitions']}))
if __name__=='__main__':main()
