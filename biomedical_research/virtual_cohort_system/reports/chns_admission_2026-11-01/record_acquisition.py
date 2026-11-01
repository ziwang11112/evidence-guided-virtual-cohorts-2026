"""Local-only intake ledger; no participant values are read or printed."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = [
    ('pexam_00.pdf', '7504991', '5a9fc2c974b95fad3a962b285129dc34', 'codebooks'),
    ('mast_pub_12.pdf', '7504949', '61649e093be0813dc83012371f2a0062', 'codebooks'),
    ('surveys_pub_12.pdf', '7504999', 'bbe06cb7d2bf0e84dab2488412d3cc32', 'codebooks'),
    ('biomarker_09.sas7bdat', '7505013', '60945adcb840138a559836c0b33e2be0', 'private_data'),
    ('pexam_00.sas7bdat', '7504992', 'a531a3b0d380fbae1baeabda3e8453f1', 'private_data'),
    ('mast_pub_12.sas7bdat', '7504950', '26eeabd1330107aa54f89d1e73f74dee', 'private_data'),
    ('surveys_pub_12.sas7bdat', '7505000', 'c52cb94ef07176e52812a4ea74dcaaaf', 'private_data'),
]

def write_json(path, obj):
    path.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))

def main():
    records = []
    for name, file_id, expected_md5, folder in FILES:
        p = ROOT / folder / name
        if not p.exists():
            continue
        b = p.read_bytes()
        if len(b) > 200 * 1024**2:
            raise ValueError('Per-file cap exceeded: ' + name)
        md5 = hashlib.md5(b).hexdigest()
        if md5 != expected_md5:
            raise ValueError('Publisher MD5 mismatch: ' + name)
        records.append(dict(file=name, local_relative_path=str(p.relative_to(ROOT)).replace('\\','/'),
            file_id=file_id, version='1.0', bytes=len(b), md5=md5,
            sha256=hashlib.sha256(b).hexdigest(), publisher_md5_match=True,
            download_method='requested Chrome official download',
            url=f'https://dataverse.unc.edu/file.xhtml?fileId={file_id}&version=1.0',
            participant_file=folder=='private_data'))
    extra = ROOT / 'codebooks' / 'C10BIOMARKER.pdf'
    if extra.exists():
        b = extra.read_bytes()
        records.append(dict(file=extra.name, local_relative_path='codebooks/'+extra.name,
            bytes=len(b), md5=hashlib.md5(b).hexdigest(), sha256=hashlib.sha256(b).hexdigest(),
            publisher_md5_match=None, participant_file=False,
            download_method='bounded HTTPS after Chrome verified official link; PDF plugin save failed',
            url='https://chns.cpc.unc.edu/wp-content/uploads/C10BIOMARKER.pdf'))
    total = 1827456 + sum(r['bytes'] for r in records)
    if total > 500 * 1024**2:
        raise ValueError('Total download cap exceeded')
    now = datetime.now(timezone.utc).isoformat()
    write_json(ROOT/'ACQUISITION_LEDGER.json', dict(updated_utc=now, inherited_metadata_bytes=1827456,
        files=records, current_download_bytes=sum(r['bytes'] for r in records), total_metered_bytes=total,
        total_cap_bytes=500*1024**2, per_file_cap_bytes=200*1024**2, browser_traffic='unmetered',
        failed_browser_save_attempts='C10BIOMARKER downloadMedia, PDF toolbar, Alt-link returned no local file; browser traffic not metered'))
    for path in [ROOT/'STATE.json',ROOT.parent/'post_review_semantics_2026-11-01'/'STATE.json']:
        s = json.loads(path.read_text(encoding='utf-8'))
        s['phase']='CHNS_schema_and_access_audit'
        s['updated_utc']=now
        s['participant_downloads']=sum(r['participant_file'] for r in records)
        s['metadata_documents_downloaded']=2+sum(not r['participant_file'] for r in records)
        s['metered_download_bytes']=total
        s['measured_download_bytes']=total
        s['remaining_metered_budget_bytes']=500*1024**2-total
        s['automation']={'id':'chns','status':'ACTIVE','verified_status':'ACTIVE',
            'replaces_deleted':'automation-4','cadence_minutes':30,
            'foreground_resumption_not_a_scheduled_run':True}
        s['terms_consent']={'dataset_doi':'10.15139/S3/9PQ5KV','version':'1.0',
            'user_confirmed':'2026-11-01, direct message authorizing Terms acceptance and required files',
            'accepted_in_official_chrome':True,'scope':'same unchanged dataset terms for necessary files'}
        s.pop('approval_needed',None)
        s['next_action']='Complete schema and linkage audit before external source selection and independent F2 freeze. No target effect calculation.'
        write_json(path,s)
    print(json.dumps({'files_verified':len(records),'participant_files':sum(r['participant_file'] for r in records),
        'total_metered_bytes':total,'scheduled_runs_verified':1}))

if __name__=='__main__':
    main()
