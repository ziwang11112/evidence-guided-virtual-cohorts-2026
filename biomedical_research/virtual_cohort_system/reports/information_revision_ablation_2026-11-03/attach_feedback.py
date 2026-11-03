"""Attach fixed operators without editing the author's scientific construction."""
from pathlib import Path
import argparse,hashlib,json,sys
P=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(P))
from cohort_harness import semantic_feedback_v1
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
    with p.open('x',encoding='utf-8') as f:json.dump(o,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def attach(bundle,candidate):
    b=Path(bundle).resolve();c=(b/'candidates'/candidate.removeprefix('candidates/')).resolve()
    if c.parent!=b/'candidates':raise ValueError('Candidate outside supplied bundle')
    if (c/'freeze.json').exists():raise ValueError('Cannot alter frozen candidate')
    science={f:sha(c/f) for f in ('generator.py','model_spec.json')}
    write(c/'whole_cohort_feedback.json',read(b/'input/whole_cohort_feedback_template.json'))
    write(c/'source_semantics_v1.json',{'schema_version':1,'evidence_sha256':sha(c/'evidence.json'),
        'recipe_sha256':sha(c/'whole_cohort_feedback.json'),
        'bindings':read(b/'input/semantic_bindings_template.json')['bindings']})
    report=semantic_feedback_v1.preflight(b,candidate)
    assert science=={f:sha(c/f) for f in science}
    return {'candidate':candidate,'checks':len(report['checks']),'science_sha256_unchanged':science,
        'scope':'Allowed-input semantics; unavailable external source-population replay remains unavailable.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--candidate',required=True);a=p.parse_args()
    print(json.dumps(attach(a.bundle,a.candidate),indent=2))
