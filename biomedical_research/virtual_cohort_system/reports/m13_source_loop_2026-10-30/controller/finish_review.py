"""Record the actual Agent response and promote only a retained source candidate."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from cohort_harness import scientific_loop
from cohort_harness.lifecycle import read_json, sha256

P=Path(__file__).resolve().parents[2]


def finish(name):
    root=P/'work/m13'/name
    exchange=root/'agent_exchange'
    receipt=exchange/'review_receipt.json'
    if receipt.exists():
        raise ValueError('Review already received; do not replay mutations')
    decision=read_json(exchange/'review_decision.json')
    receipt.write_text(json.dumps({'actor':'/root/m13_'+name,'received_utc':datetime.now(timezone.utc).isoformat(),
        'decision_sha256':sha256(exchange/'review_decision.json'),
        'response_sha256':sha256(exchange/'review_response.md'),
        'source_only':True},indent=2)+'\n')
    scientific_loop.record_decision(root,'review01',decision)
    promoted=False
    if decision['choice']=='retain_structure':
        scientific_loop.promote(root,'review01','source_reviewed')
        promoted=True
    else:
        scientific_loop.verify_loop(root)
    result={'choice':decision['choice'],'promoted':promoted,'loop_integrity_verified':True,
            'scope':'source-checked development candidate; no target evaluation',
            'freeze_sha256':sha256(root/'candidates/source_reviewed/freeze.json') if promoted else None}
    (exchange/'loop_completion.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('name',choices=['build01','build02'])
    finish(parser.parse_args().name)
