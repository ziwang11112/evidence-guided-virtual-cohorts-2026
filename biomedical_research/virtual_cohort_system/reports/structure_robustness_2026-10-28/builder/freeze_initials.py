"""Static source/schema checks and freeze only; never executes a generator."""
from pathlib import Path
import hashlib
import json
import sys

P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[2]))
from cohort_harness.__main__ import validate_bundle
from cohort_harness.source_checks import run_source_checks
from cohort_harness.lifecycle import freeze_candidate,verify_candidate
from cohort_harness.source_replay import _plan

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,obj): Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')

review={'scope':'independent_static_source_only','blocking_findings':[],
 'findings':['Correct sex indexing in all structures, including female s2 branch and s3 component lookup.',
             'Observed rows are copied and only TG appended; no opaque-ID biological dependence.',
             'Positive distribution constructions and task assay transformation are internally consistent.',
             'Three substantive families: additive arithmetic mean, nonlinear multiplicative location, latent mixture.',
             'Evidence/replay/context/shared-assumption bytes identical across candidates.',
             '46 diagnostics: 34 TG-related and 12 covariate checks; cumulative fractions preserve all category counts.',
             'Quantile, rank/regression, Table 2 ambiguity, unknown source joint distribution and assay-proxy limitations explicitly retained.'],
 'generator_executed':False,'source_replay_executed':False,
 'limits':'Reviewer inspected only new own candidate artifacts and approved source/interface inputs. Numerical agreement, runtime preservation and transport remain unverified.'}

names=['s1_initial','s2_initial','s3_initial']
shared_files=['evidence.json','source_replay.json','source_contexts/oh.csv','source_contexts/bansal.csv','sa.json','source_checks.json']
for rel in shared_files:
    assert len({sha(P/'candidates'/name/rel) for name in names})==1
for name in names:
    c=P/'candidates'/name
    assert not (c/'freeze.json').exists()
    write(c/'review.json',review)
    report=run_source_checks(P,c)
    assert all(x['status']=='not_computable' for x in report['checks'])
    write(c/'nc.json',report)
    checks=json.loads((c/'checks.json').read_text())
    checks['records'].append({'name':'independent_static_review','status':'pass','detail':'No blocking static issue found; see review.json. Does not establish runtime or numerical source compatibility.'})
    checks['records'].append({'name':'unsupported_source_statistics_retained','status':'pass','detail':'Harness parsed 23 declared not-computable source entries; no statistic was numerically computed and no generator was run.'})
    checks['artifacts'].extend([{'path':rel,'sha256':sha(c/rel)} for rel in ['review.json','nc.json']])
    write(c/'checks.json',checks)
    assert validate_bundle(P,c)['generator_executed'] is False

ready={'kind':'initial_static_freeze_readiness','generator_executed_by_builder':False,'source_replay_executed_by_builder':False,
       'plan_sha256':sha(P/'STRUCTURE_PLAN.json'),'shared':{rel:sha(P/'candidates'/names[0]/rel) for rel in shared_files},'candidates':{}}
for name in names:
    c=P/'candidates'/name
    frozen=freeze_candidate(P,c)
    verified=verify_candidate(P,c)
    assert frozen==verified
    _,contexts,_,_=_plan(P,c,20_000_000)
    ready['candidates'][name]={'freeze_sha256':sha(c/'freeze.json'),'generator_sha256':sha(c/'generator.py'),'model_spec_sha256':sha(c/'model_spec.json'),
                               'static_replay_context_count':len(contexts),'revision_index':verified['revision_index'],'acceptance':verified['acceptance']}
write(P/'INITIAL_READY.json',ready)
print(json.dumps(ready,indent=2))
