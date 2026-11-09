"""Finite aggregate/code payload; never uploads or exports individual tables.

The closure integrity gate hashes local bundle files without parsing their rows.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import importlib.util
import json
import subprocess

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
MIRROR=PROJECT.parent/'github_virtual_cohort_2026-10-27'
BASE_HEAD='000467582effbdd258dc17c6d4c4fa5472ea1d2d'
PREFIX='biomedical_research/virtual_cohort_system/'
REPORT=PREFIX+'reports/'+HERE.name+'/'
OUT=HERE/'publication_transport'
PROJECT_FILES=('cohort_harness/analysis_use_v1.py','docs/ANALYSIS_USE_V1.md','tests/test_analysis_use_v1.py')
UNIT_FILES=('initialize_corrected.py','prepare.py','start_session.py','analysis_use_adapter.py','generated_analysis.py',
    'evaluate.py','close_author.py','independent_recompute.py','test_evaluate.py','test_adapter_integration.py',
    'test_inherited_registry.py','plot_results.py','build_report.py','recompute_coherence.py','prepare_public.py','RULE_BASIS.json','RULE_BASIS.md',
    'SETUP_REVIEW.md','SETUP_REVIEW.json','SETUP_CORRECTION.json','DESIGN_LOCK.json',
    'EVALUATION.json','RECOMPUTATION.json','SCIENTIFIC_REVIEW.md','SCIENTIFIC_REVIEW.json',
    'INDEPENDENT_RESULT_REVIEW.md','INDEPENDENT_RESULT_REVIEW.json','COHERENCE_RECOMPUTATION.json',
    'RESULTS.md','coherence_and_analyses.png','coherence_and_analyses.pdf')

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def encoded(x):return (json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob_sha(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def build():
    if OUT.exists():raise ValueError('Publication already prepared; preserve it')
    head=subprocess.check_output(['git','-C',str(MIRROR),'rev-parse','HEAD']).decode().strip()
    if head!=BASE_HEAD:raise ValueError('Recheck publication base')
    if subprocess.check_output(['git','-C',str(MIRROR),'status','--porcelain']).strip():raise ValueError('Mirror not clean')
    gate=module('publication_closure_gate',HERE/'independent_recompute.py')
    closed,protocol,bundle=gate.closure_gate(HERE)
    for name,digest in read(HERE/'DESIGN_LOCK.json')['files'].items():
        if sha((HERE/name).read_bytes())!=digest:raise ValueError('Design changed')
    audit=read(HERE/'RECOMPUTATION.json');evaluation=read(HERE/'EVALUATION.json')
    expected_checks=26*sum(r['status']=='success' for r in evaluation['runs'])
    if not expected_checks or audit['passed']!=audit['checks'] or audit['checks']!=expected_checks:
        raise ValueError('Arithmetic audit failed or lacks complete positive coverage')
    closure_hash=sha((HERE/'AUTHOR_CLOSED.json').read_bytes())
    protocol_hash=sha((HERE/'PROTOCOL.json').read_bytes())
    if (audit['evaluation_sha256']!=sha((HERE/'EVALUATION.json').read_bytes())
        or audit['closure_sha256']!=closure_hash or audit['protocol_sha256']!=protocol_hash
        or evaluation['closure_sha256']!=closure_hash or evaluation['protocol_sha256']!=protocol_hash):
        raise ValueError('Stale arithmetic audit or evaluation')
    evaluation_hash=sha((HERE/'EVALUATION.json').read_bytes())
    scientific=read(HERE/'SCIENTIFIC_REVIEW.json')['closure_and_result_bindings']
    coherence=read(HERE/'COHERENCE_RECOMPUTATION.json')
    if coherence['status']!='passed':raise ValueError('Coherence audit failed')
    for binding in (scientific,coherence['binding']):
        if (binding['closure_sha256']!=closure_hash or binding['evaluation_sha256']!=evaluation_hash
            or binding['protocol_sha256']!=protocol_hash):raise ValueError('Stale scientific/coherence audit')
    if (scientific['coherence_recomputation_sha256']!=sha((HERE/'COHERENCE_RECOMPUTATION.json').read_bytes())
        or scientific['coherence_script_sha256']!=sha((HERE/'recompute_coherence.py').read_bytes())
        or coherence['binding']['script_sha256']!=sha((HERE/'recompute_coherence.py').read_bytes())):
        raise ValueError('Coherence code/report binding changed')
    review=read(HERE/'INDEPENDENT_RESULT_REVIEW.json')
    if (review['status']!='passed_with_scientific_limitations' or review['blocking_findings']!=[]
        or review['closure_sha256']!=closure_hash or review['evaluation_sha256']!=evaluation_hash
        or review['protocol_sha256']!=protocol_hash):raise ValueError('Independent result review incomplete or stale')
    inspect=module('prior_public_content_screen',PROJECT/'work/adaptive_evidence_loop_2026-11-09/prepare_public.py').inspect_public
    payload=[]
    for name in PROJECT_FILES:payload.append((PREFIX+name,(PROJECT/name).read_bytes()))
    for name in UNIT_FILES:payload.append((REPORT+name,(HERE/name).read_bytes()))
    public_protocol={k:v for k,v in protocol.items() if k!='bundle'}
    payload.append((REPORT+'PROTOCOL_PUBLIC.json',encoded(public_protocol)))
    payload.append((REPORT+'AUTHOR_CLOSED_PUBLIC.json',encoded({k:closed[k] for k in
        ('status','final_candidate','reason','candidates','runs','execution_slots')})))
    failure=read(PROJECT/'work/analysis_use_rubric_2026-11-09/SETUP_FAILURE.json')
    payload.append((REPORT+'SETUP_FAILURE_PUBLIC.json',encoded({k:failure[k] for k in
        ('status','reason','actions','executions','freezes','resolution')})))
    # Update the two existing repository introductions without copying any bundle contents.
    result_link=REPORT+'RESULTS.md'
    for name in ('README.md',PREFIX+'README.md'):
        raw=(MIRROR/name).read_text(encoding='utf8')
        link=result_link if name=='README.md' else 'reports/'+HERE.name+'/RESULTS.md'
        note=('\n**Scientific-use development, 9 November 2026.** An Agent evaluated a baseline and an optional component-coherence repair using execution-bound feedback. '
            'The [complete before/after report]('+link+') retains all scientific analyses, source gaps, setup failures and independent audits. '
            'This is a controlled development check, not new clinical validation or an overall quality claim.\n')
        lines=raw.splitlines(keepends=True);lines.insert(1,note)
        payload.append((name,''.join(lines).encode()))
    for path,raw in payload:inspect(path,raw)
    if len({p for p,_ in payload})!=len(payload):raise ValueError('Duplicate public path')
    OUT.mkdir();entries=[]
    for index,(path,raw) in enumerate(payload):
        local=OUT/f'{index:03d}.payload';local.write_bytes(raw)
        entries.append({'index':index,'path':path,'bytes':len(raw),'sha256':sha(raw),'blob_sha1':blob_sha(raw),
                        'chunks':(len(base64.b64encode(raw))+7999)//8000})
    manifest={'status':'prepared_for_independent_content_review','base_head':BASE_HEAD,'files':entries,
              'total_bytes':sum(x['bytes'] for x in entries),'scope':'Finite original code, original documents and aggregates; no candidates, row tables, source bodies, credentials or raw session logs.'}
    (OUT/'MANIFEST.json').write_bytes(encoded(manifest));print(json.dumps(manifest))

def main():
    p=argparse.ArgumentParser();p.add_argument('--blob',type=int);p.add_argument('--chunk',type=int,default=0);a=p.parse_args()
    if a.blob is None:build();return
    manifest=read(OUT/'MANIFEST.json');item=manifest['files'][a.blob]
    if item['index']!=a.blob or not 0<=a.chunk<item['chunks']:raise ValueError('Invalid payload chunk')
    raw=(OUT/f'{a.blob:03d}.payload').read_bytes()
    if sha(raw)!=item['sha256']:raise ValueError('Payload changed')
    value=base64.b64encode(raw).decode()[a.chunk*8000:(a.chunk+1)*8000]
    print(json.dumps({'index':a.blob,'chunk':a.chunk,'base64':value}))

if __name__=='__main__':main()
