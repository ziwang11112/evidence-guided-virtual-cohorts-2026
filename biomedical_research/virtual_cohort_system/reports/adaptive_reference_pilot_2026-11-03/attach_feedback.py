"""Attach fixed reference operators, never alter a scientific construction."""
from pathlib import Path
import argparse, hashlib, json, sys

P=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(P))
from cohort_harness import semantic_feedback_v1

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
    with p.open('x',encoding='utf-8') as f:json.dump(o,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def attach(bundle,candidate):
    b=Path(bundle).resolve();c=(b/'candidates'/candidate).resolve()
    if c.parent!=b/'candidates':raise ValueError('Candidate outside supplied bundle')
    if (c/'freeze.json').exists():raise ValueError('Cannot alter frozen candidate')
    science={f:sha(c/f) for f in ('generator.py','model_spec.json') if (c/f).exists()}
    plan=read(b/'input/whole_cohort_feedback_template.json')
    write(c/'whole_cohort_feedback.json',plan)
    sidecar={'schema_version':1,'evidence_sha256':sha(c/'evidence.json'),'recipe_sha256':sha(c/'whole_cohort_feedback.json'),
             'bindings':read(b/'input/semantic_bindings_template.json')['bindings']}
    write(c/'source_semantics_v1.json',sidecar)
    report=semantic_feedback_v1.preflight(b,candidate)
    assert science=={f:sha(c/f) for f in science}
    return {'candidate':candidate,'reference_checks':len(report['checks']),'science_sha256_unchanged':science,
            'scope':'Declared exposed-reference semantics only; not external study population replay.'}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--bundle',required=True);a.add_argument('--candidate',required=True);args=a.parse_args()
    print(json.dumps(attach(args.bundle,args.candidate),indent=2))
