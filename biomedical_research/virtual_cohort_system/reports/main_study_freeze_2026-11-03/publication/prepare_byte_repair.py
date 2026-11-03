"""Restore exact source bytes in publication; no science/model/result changes."""
from pathlib import Path
import hashlib,json,subprocess,re
from datetime import datetime,timezone
U=Path(__file__).resolve().parents[1]
P=U.parents[1]
E=P.parent/'github_virtual_cohort_2026-10-27'
PREFIX='biomedical_research/virtual_cohort_system/reports/main_study_freeze_2026-11-03/publication/'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes().decode('utf-8-sig'))
def git_blob_sha(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
    assert read(U/'publication/EXPORT_REPAIR_REVIEW.json')['status']=='ready'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=E,text=True).strip()
    assert head=='d485c1d86ea5d6ac544ad43a10c4df25d2590d1f'
    listing=subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=E,text=True)
    blobs={line.split('\t',1)[1]:line.split()[2] for line in listing.splitlines()}
    manifest_path=U/'publication/final_export/MANIFEST.json'
    assert sha(manifest_path.read_bytes())=='3ff534e4814d29fd26ccce005a037b5039ceea01c7f18d12355c271a0db3bc2d'
    old=read(manifest_path)
    mismatches=read(U/'publication/EXPORT_LINE_ENDING_AUDIT.json')['all_mismatches']
    assert len(mismatches)==259 and all(x['blob_matches_normalized_source'] and not x['blob_sha_matches'] for x in mismatches)
    entries=[];inventory=[]
    for item in old['artifacts']:
        path=Path(item['source']);raw=path.read_bytes();dest=item['destination']
        # Only this serialization helper changed; every scientific source remains exact.
        if path!=U/'publication/prepare_export.py':assert sha(raw)==item['sha256'],dest
        digest=git_blob_sha(raw)
        if blobs.get(dest)!=digest:
            content=raw.decode('utf-8')
            assert not re.search(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{30,}',content)
            entries.append({'path':dest,'mode':'100644','type':'blob','content':content})
        inventory.append({'destination':dest,'source':str(path),'sha256':sha(raw),'expected_git_blob_sha':digest})
    for name in ['prepare_byte_repair.py','EXPORT_REPAIR_NOTE.md','EXPORT_REPAIR_REVIEW.md','EXPORT_REPAIR_REVIEW.json','EXPORT_LINE_ENDING_AUDIT.json']:
        p=U/'publication'/name;raw=p.read_bytes();dest=PREFIX+name
        entries.append({'path':dest,'mode':'100644','type':'blob','content':raw.decode('utf-8')})
        inventory.append({'destination':dest,'source':str(p),'sha256':sha(raw),'expected_git_blob_sha':git_blob_sha(raw)})
    out=U/'publication/byte_repair_export';out.mkdir(exist_ok=False)
    batches=[];batch=[];size=0
    for entry in entries:
        n=len(json.dumps(entry,ensure_ascii=False).encode('utf-8'))
        if batch and (size+n>350_000 or len(batch)>=35):batches.append(batch);batch=[];size=0
        batch.append(entry);size+=n
    if batch:batches.append(batch)
    for j,batch in enumerate(batches):(out/f'batch_{j:02d}.json').write_text(json.dumps(batch,ensure_ascii=False),encoding='utf-8')
    manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'parent':head,'files_verified':len(inventory),'changed_files':len(entries),'batches':len(batches),'scope':'Exact text-byte serialization repair plus original audit metadata; no rows, scientific model, result, or protocol changed.','artifacts':inventory}
    (out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='artifacts'}))
if __name__=='__main__':main()
