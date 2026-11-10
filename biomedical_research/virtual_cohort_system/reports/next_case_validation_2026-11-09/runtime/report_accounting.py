"""Read-only post-seal accounting; no patient or generated row values read."""
import json
from collections import Counter
from pathlib import Path
from controller import verify_batch_seal

R=Path(__file__).resolve().parent
U=R.parent
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def main():
    batch=verify_batch_seal()
    records=[]
    for author in ['A01','A02','A03','A04','A05']:
        b=R/'sessions'/author
        seal=read(b/'AUTHOR_SEAL.json')
        strict=Counter()
        descriptive=Counter()
        for p in (b/'semantic_feedback_v1').glob('*/feedback.json'):
            strict.update(x['status'] for x in read(p)['checks'])
        for p in (b/'descriptive_feedback_v1').glob('*/feedback.json'):
            descriptive.update(x['calculation_status'] for x in read(p)['checks'])
        decision=read(b/'final_decision.json')
        gateway=read(b/'gateway/session/state.json')['usage']
        web=read(b/'web_evidence_v1/state.json')['usage']
        records.append({'author':author,'status':seal['status'],
            'selected_candidate':seal['final_candidate'],
            'attempted_outputs':len(seal['all_outputs']),
            'selected_outputs':len(seal['selected_outputs']),
            'submitted_candidate_count':len(list((b/'candidates').glob('*/freeze.json'))),
            'strict_status_counts':dict(strict),'descriptive_status_counts':dict(descriptive),
            'gateway_usage':gateway,'web_usage':web,
            'optional_source_replay_disposition':decision['optional_source_replay_disposition'],
            'feedback_reports_acknowledged':len(decision['source_feedback_used']),
            'generated_analysis_reports_acknowledged':len(decision['generated_analysis_used'])})
    result={'scope':'All five sealed authors; seed-level checks are repeated calculations, not independent evidence.',
        'batch_seal_sha256':batch['batch_seal_sha256'],'authors':records,
        'new_patient_download_bytes':0,'exact_service_model_snapshot':None,'tokens_or_API_cost':None,
        'interpretation':'Curated original evidence was supplied. Retrieval capability is distinct from actual usage. Unknown service metadata and browser traffic are not invented.'}
    (U/'RUN_ACCOUNTING.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'authors':len(records),'selected_outputs':sum(x['selected_outputs'] for x in records),
        'strict':dict(sum((Counter(x['strict_status_counts']) for x in records),Counter())),
        'descriptive':dict(sum((Counter(x['descriptive_status_counts']) for x in records),Counter()))}))
if __name__=='__main__':main()
